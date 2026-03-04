import os
import sys
import json
import re
import datetime
import shutil
import tempfile
import ctypes
import threading
from pathlib import Path
from collections import Counter
from tkinter import (Tk, Toplevel, Frame, Label, Entry, Button, 
    ttk, messagebox, Scrollbar, Listbox, Checkbutton, Radiobutton, Scale)

# --- CONFIGURARE PENTRU PYINSTALLER ---
def resource_path(relative_path):
    """
    Obtine calea absoluta catre resurse, functioneaza atat in mediul de dezvoltare,
    cat si cand aplicatia este "inghetata" cu PyInstaller.
    """
    try:
        # PyInstaller creeaza un folder temporar si stocheaza acolo path-ul in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # In mediul de dezvoltare, calea este folderul curent
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# --- CONFIGURARE LINGVISTICĂ ---
LANG = {
    "ro": {
        "app_title": "YO Log PRO v12.0 - Multi-Contest",
        "call": "Indicativ", "band": "Bandă", "mode": "Mod", "rst_s": "RST S", "rst_r": "RST R", "note": "Notă/Locator",
        "log": "LOG", "update": "ACTUALIZEAZĂ", "search": "🔍 Caută",
        "settings": "Setări", "stats": "Statistici", "validate": "Validează", "export": "Export",
        "delete": "Șterge", "backup": "Backup", "online": "Online",
        "theme": "Temă", "font_size": "Mărime Font", "contest": "Concurs", "category": "Categorie",
        "county": "Județ", "operator": "Tip Operator",
        "required_stations": "Stații Obligatorii", "special_calls": "Indicative Speciale",
        "points_per_qso": "Puncte/QSO", "edit_contests": "Editează Reguli Concurs",
        "add_rule": "Adaugă Regulă", "save_changes": "Salvează Modificări",
        "cancel": "Anulează", "stations_worked": "Stații Lucrate",
        "total_score": "Scor Total", "diploma_eligible": "Eligibil Diplomă",
        "validation_result": "Rezultat Validare",
        "maraton_category_a": "A. Seniori YO (>18 ani)",
        "maraton_category_b": "B. YL",
        "maraton_category_c": "C. Juniori YO (<=18 ani)",
        "maraton_category_d": "D. Club",
        "maraton_category_e": "E. DX",
        "maraton_category_f": "F. Receptori",
        "score_20_pts": "20 pct (YP8IC, YR8TGN)",
        "score_10_pts": "10 pct (Cluburi Neamț/Iași cu /IC)",
        "score_5_pts": "5 pct (YO/YL Neamț/Iași cu /IC)",
        "score_1_pt": "1 pct (Standard)",
        "enter_county": "Județ (NT/IS pt. punctaj IC):",
        "county_nt": "Neamț (NT)", "county_is": "Iași (IS)",
        "stafeta_category_a": "A. Echipe Seniori",
        "stafeta_category_b": "B. Echipe Juniori",
        "stafeta_category_c": "C. Echipe Mixte",
        "yo_dx_category_a": "A. Single-Op High",
        "yo_dx_category_b": "B. Single-Op Low",
        "yo_dx_category_c": "C. Multi-Op",
        "log_simplu_name": "Log Simplu (Cursă de Zi)",
    },
    "en": {
        "app_title": "YO Log PRO v12.0 - Multi-Contest",
        "call": "Call", "band": "Band", "mode": "Mode", "rst_s": "RST S", "rst_r": "RST R", "note": "Note/Locator",
        "log": "LOG", "update": "UPDATE", "search": "🔍 Search",
        "settings": "Settings", "stats": "Stats", "validate": "Validate", "export": "Export",
        "delete": "Delete", "backup": "Backup", "online": "Online",
        "theme": "Theme", "font_size": "Font Size", "contest": "Contest", "category": "Category",
        "county": "County", "operator": "Operator Type",
        "required_stations": "Required Stations", "special_calls": "Special Callsigns",
        "points_per_qso": "Points/QSO", "edit_contests": "Edit Contest Rules",
        "add_rule": "Add Rule", "save_changes": "Save Changes",
        "cancel": "Cancel", "stations_worked": "Stations Worked",
        "total_score": "Total Score", "diploma_eligible": "Diploma Eligible",
        "validation_result": "Validation Result",
        "maraton_category_a": "A. Senior YO (>18)",
        "maraton_category_b": "B. YL",
        "maraton_category_c": "C. Junior YO (<=18)",
        "maraton_category_d": "D. Club",
        "maraton_category_e": "E. DX",
        "maraton_category_f": "F. SWL",
        "score_20_pts": "20 pts (YP8IC, YR8TGN)",
        "score_10_pts": "10 pts (Neamț/Iași Clubs with /IC)",
        "score_5_pts": "5 pts (Neamț/Iași Hams with /IC)",
        "score_1_pt": "1 pt (Standard)",
        "enter_county": "Enter County (NT/IS for IC score):",
        "county_nt": "Neamț (NT)", "county_is": "Iași (IS)",
        "stafeta_category_a": "A. Senior Teams",
        "stafeta_category_b": "B. Junior Teams",
        "stafeta_category_c": "C. Mixed Teams",
        "yo_dx_category_a": "A. Single-Op High",
        "yo_dx_category_b": "B. Single-Op Low",
        "yo_dx_category_c": "C. Multi-Op",
        "log_simplu_name": "Simple Log (Day Traffic)",
    }
}

BANDS = ["160m","80m","60m","40m","30m","20m","17m","15m","12m","10m","6m","2m"]
MODES = ["SSB","CW","DIGI","FT8","FT4","RTTY","AM","FM"]

# --- STRUCTURA DE REGULI A CONCURSURILOR (MODULARĂ) ---
DEFAULT_CONTEST_RULES = {
    "maraton": {
        "name": "Maraton Ion Creangă",
        "categories": {
            "A": "A. Seniori YO (>18 ani)",
            "B": "B. YL",
            "C": "C. Juniori YO (<=18 ani)",
            "D": "D. Club",
            "E": "E. DX",
            "F": "F. Receptori"
        },
        "required_stations": ["YP8IC", "YR8TGN"],
        "special_scoring": {
            "YP8IC": 20, "YR8TGN": 20,
            "IC_CLUB": 10, "IC_INDIVIDUAL": 5
        },
        "counties_for_ic_score": ["NT", "IS"],
        "min_qso_for_diploma": 100,
        "scoring_mode": "maraton_special"
    },
    "stafeta": {
        "name": "Cupa Moldovei (Stafeta)",
        "categories": {
            "A": "A. Echipe Seniori",
            "B": "B. Echipe Juniori",
            "C": "C. Echipe Mixte"
        },
        "scoring_mode": "category_based",
        "min_qso": 50
    },
    "yo-dx": {
        "name": "YO-DX-HF",
        "categories": {
            "A": "A. Single-Op High",
            "B": "B. Single-Op Low",
            "C": "C. Multi-Op"
        },
        "scoring_mode": "standard",
        "exchange_serial": True
    },
    "log_simplu": {
        "name": "Log Simplu (Cursă de Zi)",
        "categories": {
            "A": "A. Individual"
        },
        "scoring_mode": "none"
    }
}

class LanguageManager:
    def __init__(self):
        self.current = "ro"
    
    def t(self, key):
        return LANG.get(self.current, {}).get(key, key)
    
    def set_lang(self, lang):
        if lang in LANG:
            self.current = lang

lang_manager = LanguageManager()

class DataManager:
    @staticmethod
    def atomic_save(path, data):
        try:
            temp_path = path + ".tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            os.replace(temp_path, path)
            return True
        except Exception as e:
            print(f"Error saving {path}: {e}")
            return False
    
    @staticmethod
    def load_data(path, default):
        full_path = resource_path(path)
        if not Path(full_path).exists():
            # Dacă fișierul nu există, salvăm valorile implicite
            if isinstance(default, dict):
                DataManager.atomic_save(full_path, default)
            return default
        try:
            with open(full_path, encoding="utf-8") as f: return json.load(f)
        except:
            return default

class ScoringEngine:
    @staticmethod
    def calculate_score(qso, contest_rules, user_config):
        """Calculează scorul pentru un singur QSO în funcție de regulile concursului."""
        call = qso.get("c", "").upper()
        scoring_mode = contest_rules.get("scoring_mode", "standard")
        
        if scoring_mode == "maraton_special":
            if call in ["YP8IC", "YR8TGN"]:
                return 20
            
            user_county = user_config.get("county", "NT")
            
            if "/IC" in call:
                if user_county in contest_rules.get("counties_for_ic_score", []):
                    club_prefixes = ["YO8KZG", "YO8RRC", "YO8K", "YO8ACR"]
                    is_club = any(call.startswith(p) for p in club_prefixes)
                    return 10 if is_club else 5
            return 1
            
        elif scoring_mode == "category_based":
            return 1
        else:
            return 1

    @staticmethod
    def validate_log(log_data, contest_rules, user_config):
        """Validează întregul log pentru un concurs."""
        contest_key = contest_rules.get("key")
        
        if contest_key == "maraton":
            required = contest_rules.get("required_stations", [])
            calls = [qso["c"].upper() for qso in log_data]
            missing = [s for s in required if s not in calls]
            
            if missing:
                return False, f"Lipsesc stațiile obligatorii: {', '.join(missing)}", 0
            
            if len(log_data) < contest_rules.get("min_qso_for_diploma", 100):
                return False, f"Necesar minim {contest_rules['min_qso_for_diploma']} QSO pentru diplomă, ai {len(log_data)}", 0
            
            total_score = sum(ScoringEngine.calculate_score(q, contest_rules, user_config) for q in log_data)
            return True, f"Valid! Scor: {total_score}", total_score

        elif contest_key == "stafeta":
            if len(log_data) < contest_rules.get("min_qso", 50):
                return False, f"Necesar minim {contest_rules['min_qso']} QSO, ai {len(log_data)}", 0
            return True, f"Valid! {len(log_data)} QSO-uri", len(log_data)
        
        elif contest_key == "yo-dx":
            if len(log_data) == 0:
                return False, "Niciun QSO", 0
            return True, f"Valid! {len(log_data)} QSO-uri", len(log_data)
        
        elif contest_key == "log_simplu":
            return True, f"Log: {len(log_data)} QSO-uri", len(log_data)
        
        else:
            return True, f"Log: {len(log_data)} QSO-uri", len(log_data)


class ContestManager:
    def __init__(self, rules_dict):
        self.rules = rules_dict

    def get_rules(self, contest_key):
        return self.rules.get(contest_key)

    def get_all_contest_keys(self):
        return list(self.rules.keys())

    def update_rules(self, new_rules):
        self.rules = new_rules
        DataManager.atomic_save(resource_path("contests.json"), self.rules)

class RadioLogApp(Tk):
    def __init__(self):
        super().__init__()
        self.title(lang_manager.t("app_title"))
        self.geometry("1400x900")
        
        self.cfg = DataManager.load_data("config.json", {
            "call": "YO8ACR", "loc": "KN37", "jud": "NT", 
            "cat": "A", "fs": 11, "contest": "maraton", "theme": "dark",
            "county": "NT", "lang": "ro"
        })
        
        self.log = DataManager.load_data("log.json", [])
        self.idx = None
        self.fs = int(self.cfg.get("fs", 11))
        
        self.contest_manager = ContestManager(
            DataManager.load_data("contests.json", DEFAULT_CONTEST_RULES)
        )
        
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
        self.protocol("WM_DELETE_WINDOW", self.on_exit)
    
    def ui(self):
        h = Frame(self, bg=self.th["hd"], pady=5)
        h.pack(fill="x")
        
        self.lang_var = tk.StringVar(value=self.cfg.get("lang", "ro"))
        self.lang_menu = ttk.Combobox(h, textvariable=self.lang_var, values=["ro", "en"], state="readonly", width=5)
        self.lang_menu.bind("<<ComboboxSelected>>", self.change_lang)
        self.lang_menu.pack(side="left", padx=5)
        
        Label(h, text="YO Log PRO", font=("Consolas", self.fs+4, "bold"), fg="#4fc3f7", bg=self.th["hd"]).pack(side="left", padx=10)
        
        self.contest_keys = self.contest_manager.get_all_contest_keys()
        self.cb = ttk.Combobox(h, values=self.contest_keys, state="readonly", width=15)
        self.cb.set(self.cfg.get("contest", "maraton"))
        self.cb.bind("<<ComboboxSelected>>", self.change_contest)
        self.cb.pack(side="left", padx=5)
        
        self.inf = Label(h, text="", fg="#81c784", bg=self.th["hd"])
        self.inf.pack(side="left", padx=20)
        self.update_info_bar()
        
        self.theme_btn = Button(h, text="☀/🌙", command=self.toggle_theme, bg=self.th["ac"], fg="white")
        self.theme_btn.pack(side="right", padx=5)
        
        f = Frame(self, bg=self.th["bg"], pady=10)
        f.pack(fill="x")
        
        self.en = {}
        fields = [
            (lang_manager.t("call"), "c", 12), 
            (lang_manager.t("band"), "b", 8), 
            (lang_manager.t("mode"), "m", 8),
            (lang_manager.t("rst_s"), "s", 5), 
            (lang_manager.t("rst_r"), "r", 5), 
            (lang_manager.t("note"), "n", 20)
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
        
        self.search_btn = Button(f, text=lang_manager.t("search"), command=self.search_online, 
                                bg=self.th["ac"], fg="white")
        self.search_btn.grid(row=0, column=len(fields), padx=5)
        
        self.bl = Button(f, text=lang_manager.t("log"), command=self.do_l, bg=self.th["ac"], fg="white")
        self.bl.grid(row=0, column=len(fields)+1, padx=10)
        
        self.dynamic_controls_frame = Frame(f, bg=self.th["bg"])
        self.dynamic_controls_frame.grid(row=1, column=0, columnspan=8, pady=10)
        self.update_dynamic_controls()
        
        t_f = Frame(self)
        t_f.pack(fill="both", expand=True, padx=10, pady=5)
        
        cols = [lang_manager.t("call"), lang_manager.t("band"), lang_manager.t("mode"), 
                lang_manager.t("rst_s"), lang_manager.t("rst_r"), lang_manager.t("note")]
        
        self.tr = ttk.Treeview(t_f, columns=(1,2,3,4,5,6), show="headings")
        for i, n in enumerate(cols, 1):
            self.tr.heading(i, text=n)
            self.tr.column(i, width=100)
        
        self.tr.pack(side="left", fill="both", expand=True)
        
        sb = Scrollbar(t_f, command=self.tr.yview)
        sb.pack(side="right", fill="y")
        self.tr.config(yscrollcommand=sb.set)
        
        self.tr.bind("<Double-1>", self.ed)
        
        bt = Frame(self, bg=self.th["hd"])
        bt.pack(fill="x")
        
        Button(bt, text=lang_manager.t("settings"), command=self.set).pack(side="left", padx=10)
        Button(bt, text=lang_manager.t("stats"), command=self.st).pack(side="left")
        Button(bt, text=lang_manager.t("validate"), command=self.validate).pack(side="left", padx=10)
        Button(bt, text=lang_manager.t("export"), command=self.export_menu).pack(side="left", padx=10)
        Button(bt, text=lang_manager.t("edit_contests"), command=self.edit_contests_ui).pack(side="left", padx=10)
        Button(bt, text=lang_manager.t("delete"), command=self.dl).pack(side="right", padx=10)
        Button(bt, text=lang_manager.t("backup"), command=self.manual_backup).pack(side="right", padx=5)
    
    def update_info_bar(self):
        contest_rules = self.contest_manager.get_rules(self.cfg.get("contest"))
        info_text = f"{self.cfg['call']} | {self.cfg['loc']} | {self.cfg['jud']}"
        if contest_rules and "categories" in contest_rules:
            cat_code = self.cfg.get("cat", "A")
            cat_name = contest_rules["categories"].get(cat_code, cat_code)
            info_text += f" | {cat_name}"
        self.inf.config(text=info_text)

    def update_dynamic_controls(self):
        for widget in self.dynamic_controls_frame.winfo_children():
            widget.destroy()

        contest_key = self.cfg.get("contest")
        rules = self.contest_manager.get_rules(contest_key)

        if not rules:
            return

        if contest_key == "maraton" and "categories" in rules:
            f = Frame(self.dynamic_controls_frame, bg=self.th["bg"])
            f.pack(fill="x", pady=5)
            
            Label(f, text=lang_manager.t("enter_county"), bg=self.th["bg"], fg=self.th["fg"]).pack(side="left", padx=5)
            
            self.county_var = tk.StringVar(value=self.cfg.get("county", "NT"))
            county_combo = ttk.Combobox(f, textvariable=self.county_var, values=["NT", "IS", "OTHER"], state="readonly", width=5)
            county_combo.pack(side="left", padx=5)
            
            Label(f, text=lang_manager.t("category"), bg=self.th["bg"], fg=self.th["fg"]).pack(side="left", padx=5)
            
            self.cat_var = tk.StringVar(value=self.cfg.get("cat", "A"))
            cat_combo = ttk.Combobox(f, textvariable=self.cat_var, values=list(rules["categories"].keys()), state="readonly", width=3)
            cat_combo.pack(side="left", padx=5)
            
            def save_maraton_settings():
                self.cfg["county"] = self.county_var.get()
                self.cfg["cat"] = self.cat_var.get()
                DataManager.atomic_save("config.json", self.cfg)
                self.update_info_bar()
                messagebox.showinfo("OK", "Setări Maraton actualizate")
            
            Button(f, text="💾", command=save_maraton_settings, bg=self.th["ac"], fg="white").pack(side="left", padx=5)

    def change_lang(self, event):
        lang = self.lang_var.get()
        lang_manager.set_lang(lang)
        self.cfg['lang'] = lang
        DataManager.atomic_save("config.json", self.cfg)
        for widget in self.winfo_children():
            widget.destroy()
        self.ui()
        self.ref()

    def change_contest(self, event):
        contest_key = self.cb.get()
        self.cfg["contest"] = contest_key
        DataManager.atomic_save("config.json", self.cfg)
        for widget in self.winfo_children():
            widget.destroy()
        self.ui()
        self.ref()

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
            self.bl.config(text=lang_manager.t("log"), bg=self.th["ac"])
        else:
            self.log.insert(0, q)
        
        self.ref()
        self.clr()
        DataManager.atomic_save("log.json", self.log)
        DataManager.create_backup(self.log)
    
    def ref(self):
        for i in self.tr.get_children():
            self.tr.delete(i)
        
        contest_key = self.cfg.get("contest")
        contest_rules = self.contest_manager.get_rules(contest_key)
        
        for i, q in enumerate(self.log):
            display_note = q["n"]
            if contest_key == "maraton" and contest_rules:
                score = ScoringEngine.calculate_score(q, contest_rules, self.cfg)
                display_note = f"{q['n']} ({score}p)"
            
            self.tr.insert("", "end", iid=i, values=(
                q["c"], q["b"], q["m"], q["s"], q["r"], display_note
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
        
        self.bl.config(text=lang_manager.t("update"), bg="#f57c00")
    
    def dl(self):
        s = self.tr.selection()
        if not s:
            return
        
        if messagebox.askyesno("?", "Ștergeți selecția?"):
            for i in sorted([int(x) for x in s], reverse=True):
                self.log.pop(i)
            self.ref()
            DataManager.atomic_save("log.json", self.log)
            DataManager.create_backup(self.log)
    
    def search_online(self):
        callsign = self.en["c"].get().strip()
        if not callsign:
            messagebox.showwarning("Warning", "Introduceți un indicativ")
            return
        
        self.search_btn.config(text="Caută...", state="disabled")
        self.update()
        
        def search():
            results = {
                "name": callsign,
                "qth": "Iasi" if "YO" in callsign else "Unknown",
                "locator": "KN37" if "YO8" in callsign else "Unknown"
            }
            self.after(0, lambda: self.show_search_results(results, callsign))
        
        threading.Thread(target=search, daemon=True).start()
    
    def show_search_results(self, results, callsign):
        self.search_btn.config(text=lang_manager.t("search"), state="normal")
        
        d = Toplevel(self)
        d.title(f"Rezultate pentru {callsign}")
        d.geometry("400x200")
        
        Label(d, text=f"Nume: {results['name']}\nQTH: {results['qth']}\nLocator: {results['locator']}", 
              bg=self.th["eb"], fg=self.th["fg"]).pack(pady=20)
        
        Button(d, text="Folosește aceste date", command=lambda: self.use_search_data(results, d),
               bg=self.th["ac"], fg="white").pack(pady=10)
    
    def use_search_data(self, data, window):
        if data.get('name'):
            self.en['c'].delete(0, "end")
            self.en['c'].insert(0, data['name'])
        if data.get('qth'):
            self.en['n'].delete(0, "end")
            self.en['n'].insert(0, data['qth'])
        window.destroy()
    
    def validate(self):
        contest_key = self.cfg.get("contest")
        contest_rules = self.contest_manager.get_rules(contest_key)
        
        if not contest_rules:
            messagebox.showerror("Eroare", "Reguli de concurs negăsite.")
            return

        contest_rules['key'] = contest_key
        
        valid, msg, score = ScoringEngine.validate_log(self.log, contest_rules, self.cfg)
        
        if valid:
            diploma = "DA" if len(self.log) >= contest_rules.get("min_qso_for_diploma", 100) else "NU"
            messagebox.showinfo(lang_manager.t("validation_result"), 
                f"✓ {msg}\n\nScor Total: {score}\nEligibil Diplomă ({contest_rules.get('min_qso_for_diploma', 100)} QSO): {diploma}")
        else:
            messagebox.showwarning(lang_manager.t("validation_result"), f"✗ {msg}")
    
    def export_menu(self):
        d = Toplevel(self)
        d.title("Export")
        d.geometry("300x250")
        
        Label(d, text="Selectează formatul:", font=("Consolas", 11, "bold")).pack(pady=10)
        
        Button(d, text="Cabrillo (.log)", command=lambda: self.export_cabrillo(d),
               bg=self.th["ac"], fg="white", width=20).pack(pady=5)
        Button(d, text="ADIF 3.1.0 (.adi)", command=lambda: self.export_adif(d),
               bg=self.th["ac"], fg="white", width=20).pack(pady=5)
        Button(d, text="CSV (.csv)", command=lambda: self.export_csv(d),
               bg=self.th["ac"], fg="white", width=20).pack(pady=5)
        Button(d, text="Anulează", command=d.destroy, bg="#666", fg="white", width=20).pack(pady=10)
    
    def export_cabrillo(self, parent):
        try:
            contest_key = self.cfg.get("contest")
            contest_rules = self.contest_manager.get_rules(contest_key)
            
            content = f"START-OF-LOG: 3.0\n"
            content += f"CONTEST: {contest_rules.get('name', 'Unknown')}\n"
            content += f"CALLSIGN: {self.cfg.get('call', 'NOCALL')}\n"
            content += f"CATEGORY: {self.cfg.get('cat', 'A')}\n"
            content += f"BAND: ALL\nMODE: ALL\n"
            
            for qso in self.log:
                content += f"QSO: {qso['b']} {qso['m']} {qso['d']} {qso['t']} {qso['c']} 599 {qso['r']} 001\n"
            
            content += "END-OF-LOG:\n"
            
            filename = f"cabrillo_{contest_key}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            
            messagebox.showinfo("Succes", f"Exportat în {filename}")
            parent.destroy()
        except Exception as e:
            messagebox.showerror("Eroare", str(e))
    
    def export_adif(self, parent):
        try:
            content = ""
            for qso in self.log:
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
            
            messagebox.showinfo("Succes", f"Exportat în {filename}")
            parent.destroy()
        except Exception as e:
            messagebox.showerror("Eroare", str(e))
    
    def export_csv(self, parent):
        try:
            import csv
            filename = f"csv_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Data", "Ora", "Call", "Band", "Mode", "RST_S", "RST_R", "Nota"])
                for qso in self.log:
                    writer.writerow([qso["d"], qso["t"], qso["c"], qso["b"], qso["m"], qso["s"], qso["r"], qso["n"]])
            
            messagebox.showinfo("Succes", f"Exportat în {filename}")
            parent.destroy()
        except Exception as e:
            messagebox.showerror("Eroare", str(e))
    
    def edit_contests_ui(self):
        ContestEditor(self, self.contest_manager.rules)
    
    def set(self):
        d = Toplevel(self)
        d.title("Setări")
        d.geometry("400x500")
        d.grab_set()
        
        Label(d, text="Info Stație:", font=("Consolas", 10, "bold")).pack(pady=5)
        
        Label(d, text="Indicativ:").pack()
        e1 = Entry(d)
        e1.insert(0, self.cfg["call"])
        e1.pack()
        
        Label(d, text="Locator:").pack()
        e2 = Entry(d)
        e2.insert(0, self.cfg["loc"])
        e2.pack()
        
        Label(d, text="Județ:").pack()
        e3 = Entry(d)
        e3.insert(0, self.cfg["jud"])
        e3.pack()
        
        Label(d, text="Concurs:").pack()
        contest_combo = ttk.Combobox(d, values=self.contest_keys, state="readonly")
        contest_combo.set(self.cfg.get("contest"))
        contest_combo.pack()
        
        Label(d, text="Afisare:", font=("Consolas", 10, "bold")).pack(pady=5)
        
        Label(d, text="Mărime Font:").pack()
        e4 = Entry(d)
        e4.insert(0, self.cfg["fs"])
        e4.pack()
        
        Label(d, text="Temă:").pack()
        theme = ttk.Combobox(d, values=["dark", "light"], state="readonly")
        theme.set(self.cfg["theme"])
        theme.pack()
        
        Label(d, text="Limba:").pack()
        lang = ttk.Combobox(d, values=["ro", "en"], state="readonly")
        lang.set(self.cfg.get("lang", "ro"))
        lang.pack()
        
        def sv():
            self.cfg.update({
                "call": e1.get().upper(),
                "loc": e2.get().upper(),
                "jud": e3.get().upper(),
                "fs": int(e4.get()),
                "theme": theme.get(),
                "contest": contest_combo.get(),
                "lang": lang.get()
            })
            self.lang_var.set(lang.get())
            lang_manager.set_lang(lang.get())
            DataManager.atomic_save("config.json", self.cfg)
            d.destroy()
            self.apply_settings()
            messagebox.showinfo("OK", "Setări salvate. Reporniți aplicația pentru efect complet.")
        
        Button(d, text="Salvează", command=sv, bg=self.th["ac"], fg="white").pack(pady=20)
    
    def apply_settings(self):
        self.fs = int(self.cfg.get("fs", 11))
        self.current_theme = self.cfg.get("theme", "dark")
        self.th = self.themes[self.current_theme]
        
        for widget in self.winfo_children():
            widget.destroy()
        
        self.ui()
        self.ref()
    
    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.cfg["theme"] = self.current_theme
        self.th = self.themes[self.current_theme]
        self.apply_settings()
    
    def st(self):
        b = Counter(q["b"] for q in self.log)
        m = f"Total: {len(self.log)} QSOs\n\n"
        for k in sorted(b.keys()):
            m += f"{k}: {b[k]}\n"
        
        contest_key = self.cfg.get("contest")
        if contest_key == "maraton":
            contest_rules = self.contest_manager.get_rules(contest_key)
            required = contest_rules.get("required_stations", [])
            calls = [qso["c"] for qso in self.log]
            found = [s for s in required if s in calls]
            m += f"\n{lang_manager.t('stations_worked')}: {len(set(calls))}"
            if found:
                m += f"\n{lang_manager.t('required_stations')}: {', '.join(found)}"
            
            user_county = self.cfg.get("county", "NT")
            total_score = sum(ScoringEngine.calculate_score(q, contest_rules, self.cfg) for q in self.log)
            m += f"\n\n{lang_manager.t('total_score')}: {total_score}"

        messagebox.showinfo("Stats", m)
    
    def manual_backup(self):
        if DataManager.create_backup(self.log):
            messagebox.showinfo("Backup", "Backup creat cu succes")
        else:
            messagebox.showerror("Eroare", "Backup eșuat")
    
    def on_exit(self):
        if messagebox.askyesno("Exit", "Salvați modificările și creați backup?"):
            DataManager.atomic_save("log.json", self.log)
            DataManager.create_backup(self.log)
            DataManager.atomic_save("config.json", self.cfg)
            self.destroy()

class ContestEditor:
    def __init__(self, parent, rules_dict):
        self.rules = rules_dict
        self.window = Toplevel(parent)
        self.window.title(lang_manager.t("edit_contests"))
        self.window.geometry("800x600")
        self.window.grab_set()
        
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        for contest_key in self.rules.keys():
            frame = Frame(self.notebook, bg=parent.th["bg"])
            self.notebook.add(frame, text=contest_key.upper())
            self.create_contest_editor(frame, contest_key)
        
        Button(self.window, text=lang_manager.t("save_changes"), 
               command=self.save_and_close, bg=parent.th["ac"], fg="white").pack(pady=10)
    
    def create_contest_editor(self, parent, contest_key):
        rules = self.rules[contest_key]
        
        Label(parent, text="Nume Concurs:", bg=parent.th["bg"], fg=parent.th["fg"]).pack(pady=5)
        e_name = Entry(parent, bg=parent.th["eb"], fg=parent.th["fg"])
        e_name.insert(0, rules.get("name", ""))
        e_name.pack()
        
        if "categories" in rules:
            Label(parent, text="Categorii (unul per linie, cod:descriere):", bg=parent.th["bg"], fg=parent.th["fg"]).pack(pady=5)
            self.cat_text = Text(parent, height=5, bg=parent.th["eb"], fg=parent.th["fg"])
            cat_str = "\n".join([f"{k}:{v}" for k, v in rules["categories"].items()])
            self.cat_text.insert("1.0", cat_str)
            self.cat_text.pack(fill="x", expand=True)

        if contest_key == "maraton":
            Label(parent, text="Stații Obligatorii (virgulă):", bg=parent.th["bg"], fg=parent.th["fg"]).pack(pady=5)
            e_req = Entry(parent, bg=parent.th["eb"], fg=parent.th["fg"])
            e_req.insert(0, ", ".join(rules.get("required_stations", [])))
            e_req.pack()
            
            Label(parent, text="Minim QSO pentru diplomă:", bg=parent.th["bg"], fg=parent.th["fg"]).pack(pady=5)
            e_min = Entry(parent, bg=parent.th["eb"], fg=parent.th["fg"])
            e_min.insert(0, str(rules.get("min_qso_for_diploma", 100)))
            e_min.pack()
            
            Label(parent, text="Județe pentru punctaj IC (virgulă):", bg=parent.th["bg"], fg=parent.th["fg"]).pack(pady=5)
            e_county = Entry(parent, bg=parent.th["eb"], fg=parent.th["fg"])
            e_county.insert(0, ", ".join(rules.get("counties_for_ic_score", [])))
            e_county.pack()

            self.e_req = e_req
            self.e_min = e_min
            self.e_county = e_county
    
    def save_and_close(self):
        # Aici ar trebui implementată logica de salvare a modificărilor din UI în dicționarul de reguli.
        # Pentru simplitate, afișăm un mesaj.
        self.window.destroy()
        messagebox.showinfo("Info", "Funcționalitatea de editare avansată este în dezvoltare. "
                                      "Pentru a modifica regulile, editați direct fișierul 'contests.json' "
                                      "sau folosiți o aplicație de editare JSON.")


if __name__ == "__main__":
    app = RadioLogApp()
    app.mainloop()
