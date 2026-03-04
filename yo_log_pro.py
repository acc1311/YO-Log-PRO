import os, sys, json, re, datetime, shutil, tempfile, ctypes, threading
from pathlib import Path
from collections import Counter
from tkinter import (Tk, Toplevel, Frame, Label, Entry, Button, 
    ttk, messagebox, Scrollbar, Listbox, Checkbutton, Radiobutton)
import webbrowser
import requests

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

BANDS = ["160m","80m","60m","40m","30m","20m","17m","15m","12m","10m","6m","2m"]
MODES = ["SSB","CW","DIGI","FT8","FT4","RTTY","AM","FM"]
CON_T = {"yo-dx": "YO-DX-HF", "stafeta": "Stafeta", "maraton": "Maraton", "simple": "Log"}
CAT_T = ["Single-Op High", "Single-Op Low", "Single-Op QRP", "Multi-Op", "Checklog"]
FLS = {"config": "config.json", "log": "log.json", "backup": "backup"}

DEF_C = {
    "call": "YO8ACR", "loc": "KN37", "jud": "NT", "cat": "Single-Op Low", 
    "fs": 11, "mode": "simple", "theme": "dark", "online": True,
    "contest": "yo-dx", "serial_start": 1000, "multiplier": 1
}

# Contest configurations
CONTEST_CONFIGS = {
    "yo-dx": {
        "name": "YO-DX-HF",
        "serial_auto": True,
        "multiplier_auto": True,
        "required_stations": [],
        "min_qso": 0,
        "scoring": "normal"
    },
    "stafeta": {
        "name": "Cupa Moldovei (Stafeta)",
        "categories": ["A", "B", "C", "D", "E"],
        "scoring": "category_based"
    },
    "maraton": {
        "name": "Maraton Ion Creangă",
        "required_stations": ["YP8IC", "YR8TGN"],
        "min_qso": 100,
        "scoring": "per_ic",
        "check_stations": True
    },
    "simple": {
        "name": "Log Simplu",
        "fields": ["frecvență", "nume", "locator", "județ"]
    }
}

class DataManager:
    @staticmethod
    def atomic_save(path, data):
        """Atomic save to prevent corruption"""
        try:
            temp_path = path + ".tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            os.replace(temp_path, path)
            return True
        except Exception as e:
            print(f"Error saving: {e}")
            return False
    
    @staticmethod
    def load_data(path, default):
        if not Path(path).exists(): return default
        try:
            with open(path, encoding="utf-8") as f: return json.load(f)
        except: return default
    
    @staticmethod
    def create_backup(log_data, backup_dir="backup"):
        """Create backup with timestamp"""
        try:
            Path(backup_dir).mkdir(exist_ok=True)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = Path(backup_dir) / f"backup_{timestamp}.json"
            with open(backup_path, "w", encoding="utf-8") as f:
                json.dump(log_data, f, indent=2)
            
            # Keep only last 50 backups
            backups = sorted(Path(backup_dir).glob("backup_*.json"))
            if len(backups) > 50:
                for old in backups[:-50]:
                    old.unlink()
            return True
        except Exception as e:
            print(f"Backup error: {e}")
            return False
    
    @staticmethod
    def recover_from_backup(backup_dir="backup"):
        """Recover from most recent backup"""
        try:
            backups = sorted(Path(backup_dir).glob("backup_*.json"))
            if backups:
                with open(backups[-1], encoding="utf-8") as f:
                    return json.load(f)
            return None
        except:
            return None

class OnlineSearch:
    @staticmethod
    def search_qrz(callsign):
        """Search QRZ.com"""
        try:
            url = f"https://www.qrz.com/db/{callsign}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                # Parse name, QTH, locator from HTML
                html = response.text
                name_match = re.search(r'<title>(.*?) - QRZ.com</title>', html)
                if name_match:
                    name = name_match.group(1).replace("'", "")
                else:
                    name = callsign
                return {"name": name, "qth": "", "locator": "", "source": "QRZ.com"}
        except:
            pass
        return None
    
    @staticmethod
    def search_radioamator(callsign):
        """Search Radioamator.ro"""
        try:
            url = f"https://www.radioamator.ro/call/{callsign}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {
                    "name": data.get("name", callsign),
                    "qth": data.get("qth", ""),
                    "locator": data.get("locator", ""),
                    "source": "Radioamator.ro"
                }
        except:
            pass
        return None
    
    @staticmethod
    def search_eqsl(callsign):
        """Search eQSL.cc"""
        try:
            url = f"https://www.eqsl.cc/qslcard/GetQSL.cfm?Callsign={callsign}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                # Parse eQSL data
                return {
                    "name": callsign,
                    "qth": "",
                    "locator": "",
                    "source": "eQSL.cc"
                }
        except:
            pass
        return None
    
    @staticmethod
    def parallel_search(callsign):
        """Search all sources in parallel"""
        results = {}
        
        def search_source(source_func, key):
            result = source_func(callsign)
            if result:
                results[key] = result
        
        threads = [
            threading.Thread(target=search_source, args=(OnlineSearch.search_qrz, "qrz")),
            threading.Thread(target=search_source, args=(OnlineSearch.search_radioamator, "radioamator")),
            threading.Thread(target=search_source, args=(OnlineSearch.search_eqsl, "eqsl"))
        ]
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join(timeout=3)
        
        return results

class Exporter:
    @staticmethod
    def export_cabrillo(log_data, contest_type):
        """Generate Cabrillo format"""
        try:
            content = f"START-OF-LOG: 3.0\n"
            content += f"CONTEST: {CONTEST_CONFIGS[contest_type]['name']}\n"
            content += f"CALLSIGN: {log_data[0].get('call', 'NOCALL')}\n"
            content += f"CATEGORY: SINGLE-OP\n"
            content += f"BAND: ALL\n"
            content += f"MODE: ALL\n"
            
            for qso in log_data:
                content += f"QSO: {qso['b']} {qso['m']} {qso['d']} {qso['t']} {qso['c']} 599 {qso['r']} 001\n"
            
            content += "END-OF-LOG:\n"
            
            filename = f"cabrillo_{contest_type}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            return filename
        except Exception as e:
            messagebox.showerror("Error", f"Cabrillo export failed: {e}")
            return None
    
    @staticmethod
    def export_adif(log_data):
        """Generate ADIF 3.1.0 format"""
        try:
            content = ""
            for qso in log_data:
                content += f"<CALL:{len(qso['c'])}>{qso['c']}"
                content += f"<BAND:{len(qso['b'])}>{qso['b']}"
                content += f"<MODE:{len(qso['m'])}>{qso['m']}"
                content += f"<QSO_DATE:{len(qso['d'])}>{qso['d']}"
                content += f"<TIME_ON:{len(qso['t'])}>{qso['t']}"
                content += f"<RST_SENT:{len(qso['s'])}>{qso['s']}"
                content += f"<RST_RCVD:{len(qso['r'])}>{qso['r']}"
                if qso.get('n'):
                    content += f"<COMMENT:{len(qso['n'])}>{qso['n']}"
                content += "<EOR>\n"
            
            filename = f"adif_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.adi"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            return filename
        except Exception as e:
            messagebox.showerror("Error", f"ADIF export failed: {e}")
            return None
    
    @staticmethod
    def export_csv(log_data):
        """Generate CSV format"""
        try:
            import csv
            filename = f"csv_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Data", "Ora", "Call", "Band", "Mode", "RST_S", "RST_R", "Note"])
                for qso in log_data:
                    writer.writerow([qso["d"], qso["t"], qso["c"], qso["b"], qso["m"], qso["s"], qso["r"], qso["n"]])
            return filename
        except Exception as e:
            messagebox.showerror("Error", f"CSV export failed: {e}")
            return None

class ContestValidator:
    @staticmethod
    def validate_yo_dx(log_data):
        """Validate YO-DX-HF contest"""
        required = CONTEST_CONFIGS["yo-dx"]["required_stations"]
        if not required:
            return True, "No required stations"
        
        calls = [qso["c"] for qso in log_data]
        missing = [s for s in required if s not in calls]
        
        if missing:
            return False, f"Missing stations: {', '.join(missing)}"
        return True, "All required stations present"
    
    @staticmethod
    def validate_maraton(log_data):
        """Validate Maraton Ion Creangă"""
        required = CONTEST_CONFIGS["maraton"]["required_stations"]
        calls = [qso["c"] for qso in log_data]
        missing = [s for s in required if s not in calls]
        
        if missing:
            return False, f"Missing required stations: {', '.join(missing)}"
        
        if len(log_data) < CONTEST_CONFIGS["maraton"]["min_qso"]:
            return False, f"Need {CONTEST_CONFIGS['maraton']['min_qso']} QSOs, have {len(log_data)}"
        
        return True, f"Valid: {len(log_data)} QSOs, all required stations present"
    
    @staticmethod
    def validate_stafeta(log_data):
        """Validate Stafeta contest"""
        if len(log_data) == 0:
            return False, "No QSOs"
        return True, f"Valid: {len(log_data)} QSOs"

class RadioLogApp(Tk):
    def __init__(self):
        super().__init__()
        self.title("YO Log PRO v9.6 - Enhanced")
        self.geometry("1400x900")
        
        self.cfg = DataManager.load_data("config.json", DEF_C)
        self.log = DataManager.load_data("log.json", [])
        self.idx = None
        self.fs = int(self.cfg.get("fs", 11))
        
        # Theme configuration
        self.themes = {
            "dark": {"bg": "#1e1e1e", "fg": "white", "ac": "#007acc", "eb": "#333", "hd": "#2d2d2d"},
            "light": {"bg": "#ffffff", "fg": "black", "ac": "#0066cc", "eb": "#f0f0f0", "hd": "#e0e0e0"}
        }
        self.current_theme = self.cfg.get("theme", "dark")
        self.th = self.themes[self.current_theme]
        
        self.configure(bg=self.th["bg"])
        self.fnt = ("Consolas", self.fs)
        self.ui()
        self.ref()
        
        # Auto-backup on exit
        self.protocol("WM_DELETE_WINDOW", self.on_exit)
    
    def ui(self):
        # Header
        h = Frame(self, bg=self.th["hd"], pady=5)
        h.pack(fill="x")
        Label(h, text="YO Log PRO", font=("Consolas", self.fs+4, "bold"), fg="#4fc3f7", bg=self.th["hd"]).pack(side="left", padx=10)
        
        self.cb = ttk.Combobox(h, values=list(CON_T.values()), state="readonly", width=15)
        self.cb.set(CON_T.get(self.cfg["contest"], "Log"))
        self.cb.bind("<<ComboboxSelected>>", self.change_contest)
        self.cb.pack(side="left", padx=5)
        
        self.inf = Label(h, text=f"{self.cfg['call']} | {self.cfg['loc']} | {self.cfg['jud']}", 
                        fg="#81c784", bg=self.th["hd"])
        self.inf.pack(side="left", padx=20)
        
        # Theme toggle
        self.theme_btn = Button(h, text="☀/🌙", command=self.toggle_theme, bg=self.th["ac"], fg="white")
        self.theme_btn.pack(side="right", padx=5)
        
        # Online status
        self.online_var = tk.BooleanVar(value=self.cfg.get("online", True))
        Checkbutton(h, text="Online Mode", variable=self.online_var, 
                   command=self.toggle_online, bg=self.th["hd"], fg=self.th["fg"]).pack(side="right", padx=5)
        
        # Input Frame
        f = Frame(self, bg=self.th["bg"], pady=10)
        f.pack(fill="x")
        
        self.en = {}
        fields = [
            ("Call", "c", 12), ("Band", "b", 8), ("Mode", "m", 8),
            ("RST_S", "s", 5), ("RST_R", "r", 5), ("Note", "n", 20)
        ]
        
        for i, (l, k, w) in enumerate(fields):
            px = Frame(f, bg=self.th["bg"])
            px.grid(row=0, column=i, padx=5)
            Label(px, text=l, fg="#bbb", bg=self.th["bg"]).pack()
            
            if k == "b":
                e = ttk.Combobox(px, values=BANDS, width=w, state="readonly")
                e.set("40m")
            elif k == "m":
                e = ttk.Combobox(px, values=MODES, width=w, state="readonly")
                e.set("SSB")
            else:
                e = Entry(px, width=w, bg=self.th["eb"], fg=self.th["fg"], 
                         insertbackground=self.th["fg"])
                if k in ["s", "r"]:
                    e.insert(0, "59")
            
            e.pack()
            self.en[k] = e
        
        # Search button
        self.search_btn = Button(f, text="🔍 Search", command=self.search_online, 
                                bg=self.th["ac"], fg="white")
        self.search_btn.grid(row=0, column=len(fields), padx=5)
        
        # Log button
        self.bl = Button(f, text="LOG", command=self.do_l, bg=self.th["ac"], fg="white")
        self.bl.grid(row=0, column=len(fields)+1, padx=10)
        
        # Treeview
        t_f = Frame(self)
        t_f.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.tr = ttk.Treeview(t_f, columns=(1,2,3,4,5,6,7,8), show="headings")
        cols = ["Data", "Ora", "Call", "Band", "Mode", "RST_S", "RST_R", "Note"]
        for i, n in enumerate(cols, 1):
            self.tr.heading(i, text=n)
            self.tr.column(i, width=100)
        
        self.tr.pack(side="left", fill="both", expand=True)
        
        sb = Scrollbar(t_f, command=self.tr.yview)
        sb.pack(side="right", fill="y")
        self.tr.config(yscrollcommand=sb.set)
        
        self.tr.bind("<Double-1>", self.ed)
        
        # Bottom buttons
        bt = Frame(self, bg=self.th["hd"])
        bt.pack(fill="x")
        
        Button(bt, text="Setari", command=self.set).pack(side="left", padx=10)
        Button(bt, text="Stats", command=self.st).pack(side="left")
        Button(bt, text="Validate", command=self.validate).pack(side="left", padx=10)
        Button(bt, text="Export", command=self.export_menu).pack(side="left", padx=10)
        Button(bt, text="Sterge", command=self.dl).pack(side="right", padx=10)
        Button(bt, text="Backup", command=self.manual_backup).pack(side="right", padx=5)
    
    def do_l(self):
        c = self.en["c"].get().upper().strip()
        if not c:
            return
        
        n = datetime.datetime.utcnow()
        q = {
            "d": n.strftime("%Y-%m-%d"),
            "t": n.strftime("%H%M"),
            "c": c,
            "b": self.en["b"].get(),
            "m": self.en["m"].get(),
            "s": self.en["s"].get(),
            "r": self.en["r"].get(),
            "n": self.en["n"].get()
        }
        
        if self.idx is not None:
            self.log[self.idx] = q
            self.idx = None
            self.bl.config(text="LOG", bg=self.th["ac"])
        else:
            self.log.insert(0, q)
        
        self.ref()
        self.clr()
        DataManager.atomic_save("log.json", self.log)
        DataManager.create_backup(self.log)
    
    def ref(self):
        for i in self.tr.get_children():
            self.tr.delete(i)
        for i, q in enumerate(self.log):
            self.tr.insert("", "end", iid=i, values=(
                q["d"], q["t"], q["c"], q["b"], q["m"], q["s"], q["r"], q["n"]
            ))
    
    def clr(self):
        self.en["c"].delete(0, "end")
        self.en["n"].delete(0, "end")
        self.en["c"].focus()
    
    def ed(self, e):
        id = self.tr.identify_row(e.y)
        if not id:
            return
        self.idx = int(id)
        q = self.log[self.idx]
        
        for k, v in zip(["c", "b", "m", "s", "r", "n"], 
                        [q["c"], q["b"], q["m"], q["s"], q["r"], q["n"]]):
            if k in ["b", "m"]:
                self.en[k].set(v)
            else:
                self.en[k].delete(0, "end")
                self.en[k].insert(0, v)
        
        self.bl.config(text="UPDATE", bg="#f57c00")
    
    def dl(self):
        s = self.tr.selection()
        if not s:
            return
        
        if messagebox.askyesno("?", "Stergeti selectia?"):
            for i in sorted([int(x) for x in s], reverse=True):
                self.log.pop(i)
            self.ref()
            DataManager.atomic_save("log.json", self.log)
            DataManager.create_backup(self.log)
    
    def search_online(self):
        callsign = self.en["c"].get().strip()
        if not callsign:
            messagebox.showwarning("Warning", "Enter a callsign first")
            return
        
        if not self.cfg.get("online", True):
            messagebox.showinfo("Info", "Online mode is disabled")
            return
        
        # Show searching indicator
        self.search_btn.config(text="Searching...", state="disabled")
        self.update()
        
        # Search in background thread
        def search():
            results = OnlineSearch.parallel_search(callsign)
            self.after(0, lambda: self.show_search_results(results, callsign))
        
        threading.Thread(target=search, daemon=True).start()
    
    def show_search_results(self, results, callsign):
        self.search_btn.config(text="🔍 Search", state="normal")
        
        if not results:
            messagebox.showinfo("Search", f"No data found for {callsign}")
            return
        
        # Create results window
        d = Toplevel(self)
        d.title(f"Search Results for {callsign}")
        d.geometry("600x400")
        
        Label(d, text=f"Search Results for {callsign}:", font=("Consolas", 12, "bold")).pack(pady=10)
        
        for source, data in results.items():
            f = Frame(d, bg=self.th["eb"], pady=5)
            f.pack(fill="x", padx=10, pady=5)
            Label(f, text=f"Source: {data['source']}", fg="#4fc3f7", bg=self.th["eb"]).pack(anchor="w")
            Label(f, text=f"Name: {data['name']}", bg=self.th["eb"]).pack(anchor="w")
            if data['qth']:
                Label(f, text=f"QTH: {data['qth']}", bg=self.th["eb"]).pack(anchor="w")
            if data['locator']:
                Label(f, text=f"Locator: {data['locator']}", bg=self.th["eb"]).pack(anchor="w")
            
            Button(f, text="Use This Data", command=lambda d=data: self.use_search_data(d, d)).pack(pady=5)
    
    def use_search_data(self, data, window):
        if data.get('name') and data['name'] != self.en['c'].get():
            self.en['c'].delete(0, "end")
            self.en['c'].insert(0, data['name'])
        if data.get('qth'):
            self.en['n'].delete(0, "end")
            self.en['n'].insert(0, data['qth'])
        window.destroy()
    
    def validate(self):
        contest = self.cfg.get("contest", "simple")
        validators = {
            "yo-dx": ContestValidator.validate_yo_dx,
            "stafeta": ContestValidator.validate_stafeta,
            "maraton": ContestValidator.validate_maraton
        }
        
        if contest in validators:
            valid, msg = validators[contest](self.log)
            if valid:
                messagebox.showinfo("Validation", f"✓ {msg}")
            else:
                messagebox.showwarning("Validation", f"✗ {msg}")
        else:
            messagebox.showinfo("Validation", f"Log: {len(self.log)} QSOs")
    
    def export_menu(self):
        d = Toplevel(self)
        d.title("Export Options")
        d.geometry("300x250")
        
        Label(d, text="Select Export Format:", font=("Consolas", 11, "bold")).pack(pady=10)
        
        Button(d, text="Cabrillo (.log)", command=lambda: self.export_cabrillo(d),
               bg=self.th["ac"], fg="white", width=20).pack(pady=5)
        Button(d, text="ADIF 3.1.0 (.adi)", command=lambda: self.export_adif(d),
               bg=self.th["ac"], fg="white", width=20).pack(pady=5)
        Button(d, text="CSV (.csv)", command=lambda: self.export_csv(d),
               bg=self.th["ac"], fg="white", width=20).pack(pady=5)
        Button(d, text="Cancel", command=d.destroy, bg="#666", fg="white", width=20).pack(pady=10)
    
    def export_cabrillo(self, parent):
        contest = self.cfg.get("contest", "simple")
        filename = Exporter.export_cabrillo(self.log, contest)
        if filename:
            messagebox.showinfo("Success", f"Cabrillo exported to {filename}")
            webbrowser.open(os.path.dirname(os.path.abspath(filename)))
        parent.destroy()
    
    def export_adif(self, parent):
        filename = Exporter.export_adif(self.log)
        if filename:
            messagebox.showinfo("Success", f"ADIF exported to {filename}")
        parent.destroy()
    
    def export_csv(self, parent):
        filename = Exporter.export_csv(self.log)
        if filename:
            messagebox.showinfo("Success", f"CSV exported to {filename}")
        parent.destroy()
    
    def set(self):
        d = Toplevel(self)
        d.title("Setari")
        d.geometry("400x500")
        d.grab_set()
        
        Label(d, text="Station Info:", font=("Consolas", 10, "bold")).pack(pady=5)
        
        Label(d, text="Callsign:").pack()
        e1 = Entry(d)
        e1.insert(0, self.cfg["call"])
        e1.pack()
        
        Label(d, text="Locator:").pack()
        e2 = Entry(d)
        e2.insert(0, self.cfg["loc"])
        e2.pack()
        
        Label(d, text="Judet:").pack()
        e3 = Entry(d)
        e3.insert(0, self.cfg["jud"])
        e3.pack()
        
        Label(d, text="Category:").pack()
        cat = ttk.Combobox(d, values=CAT_T, state="readonly")
        cat.set(self.cfg["cat"])
        cat.pack()
        
        Label(d, text="Display:", font=("Consolas", 10, "bold")).pack(pady=5)
        
        Label(d, text="Font Size:").pack()
        e4 = Entry(d)
        e4.insert(0, self.cfg["fs"])
        e4.pack()
        
        Label(d, text="Theme:").pack()
        theme = ttk.Combobox(d, values=["dark", "light"], state="readonly")
        theme.set(self.cfg["theme"])
        theme.pack()
        
        Label(d, text="Contest:", font=("Consolas", 10, "bold")).pack(pady=5)
        
        contest = ttk.Combobox(d, values=list(CON_T.values()), state="readonly")
        contest.set(CON_T.get(self.cfg["contest"], "Log"))
        contest.pack()
        
        def sv():
            self.cfg.update({
                "call": e1.get().upper(),
                "loc": e2.get().upper(),
                "jud": e3.get().upper(),
                "cat": cat.get(),
                "fs": int(e4.get()),
                "theme": theme.get(),
                "contest": list(CON_T.keys())[list(CON_T.values()).index(contest.get())]
            })
            DataManager.atomic_save("config.json", self.cfg)
            d.destroy()
            self.apply_settings()
            messagebox.showinfo("OK", "Settings saved. Restart recommended for full effect.")
        
        Button(d, text="Save", command=sv, bg=self.th["ac"], fg="white").pack(pady=20)
    
    def apply_settings(self):
        self.fs = int(self.cfg.get("fs", 11))
        self.fnt = ("Consolas", self.fs)
        self.current_theme = self.cfg.get("theme", "dark")
        self.th = self.themes[self.current_theme]
        
        # Update all widgets
        self.configure(bg=self.th["bg"])
        for widget in self.winfo_children():
            if isinstance(widget, Frame):
                widget.configure(bg=self.th["bg"] if widget != self.winfo_children()[0] else self.th["hd"])
        
        self.ref()
    
    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.th = self.themes[self.current_theme]
        self.cfg["theme"] = self.current_theme
        self.apply_settings()
    
    def toggle_online(self):
        self.cfg["online"] = self.online_var.get()
    
    def change_contest(self, event):
        contest_name = self.cb.get()
        contest_key = list(CON_T.keys())[list(CON_T.values()).index(contest_name)]
        self.cfg["contest"] = contest_key
        
        # Update contest-specific settings
        if contest_key == "maraton":
            self.cfg["serial_start"] = 1000
        
        DataManager.atomic_save("config.json", self.cfg)
    
    def st(self):
        b = Counter(q["b"] for q in self.log)
        m = f"Total: {len(self.log)} QSOs\n\n"
        for k in sorted(b.keys()):
            m += f"{k}: {b[k]}\n"
        
        # Add contest-specific stats
        contest = self.cfg.get("contest", "simple")
        if contest == "maraton":
            required = CONTEST_CONFIGS["maraton"]["required_stations"]
            calls = [qso["c"] for qso in self.log]
            found = [s for s in required if s in calls]
            m += f"\nMaraton Stations: {len(found)}/{len(required)}"
            if found:
                m += f"\nFound: {', '.join(found)}"
        
        messagebox.showinfo("Stats", m)
    
    def manual_backup(self):
        if DataManager.create_backup(self.log):
            messagebox.showinfo("Backup", "Backup created successfully")
        else:
            messagebox.showerror("Error", "Backup failed")
    
    def on_exit(self):
        if messagebox.askyesno("Exit", "Save changes and create backup?"):
            DataManager.atomic_save("log.json", self.log)
            DataManager.create_backup(self.log)
            DataManager.atomic_save("config.json", self.cfg)
            self.destroy()

if __name__ == "__main__":
    app = RadioLogApp()
    app.mainloop()
