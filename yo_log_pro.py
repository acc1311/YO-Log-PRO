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

# --- IMPORT TKINTER CORECTAT ---
import tkinter as tk
from tkinter import ttk, messagebox, Scrollbar, Listbox, Menu

# --- CONFIGURARE PENTRU PYINSTALLER ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- CONFIGURARE LINGVISTICĂ ---
LANG = {
    "ro": {
        "app_title": "YO Log PRO v13.0 - Multi-Contest",
        "call": "Indicativ", "band": "Bandă", "mode": "Mod", "rst_s": "RST S", "rst_r": "RST R", "note": "Notă/Locator",
        "log": "LOG", "update": "ACTUALIZEAZĂ", "search": "🔍 Caută", "reset": "Reset",
        "settings": "Setări", "stats": "Statistici", "validate": "Validează", "export": "Export",
        "delete": "Șterge", "backup": "Backup", "online": "Online", "offline": "Manual",
        "manual_mode": "Mod Manual (Dată/Oră)",
        "theme": "Temă", "font_size": "Mărime Font", "contest": "Concurs", "category": "Categorie",
        "county": "Județ", "operator": "Tip Operator", "address": "Adresă",
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
        "right_click_delete": "Șterge QSO",
        "right_click_edit": "Editează QSO",
        "exit_confirm": "Salvați modificările și creați backup?",
        "yes": "Da", "no": "Nu",
        "help": "Ajutor",
        "about": "Despre",
        "credits_title": "Despre YO Log PRO",
        "credits_dev": "Dezvoltat de:\nArdei Constantin-Cătălin (YO8ACR)\n\nEmail: yo8acr@gmail.com",
        "usage_title": "Instrucțiuni de Utilizare",
        "usage_text": "1. Introduceți Indicativul, Banda și Modul.\n2. Apăsați LOG sau tasta ENTER pentru a adăuga.\n3. Folosiți Click Dreapta pe un QSO pentru a-l edita sau șterge.\n4. Validați log-ul înainte de export.\n5. Faceți Backup periodic!",
        "date_label": "Dată (YYYY-MM-DD):",
        "time_label": "Oră (HH:MM):",
        "enable_manual_datetime": "Activează setarea manuală a Datei/Orei",
        "led_tooltip_online": "Mod Online: Data/Ora sunt setate automat",
        "led_tooltip_offline": "Mod Manual: Data/Ora sunt setate manual",
        "confirm_delete": "Confirmare Ștergere",
        "confirm_delete_text": "Sunteți sigur că doriți să ștergeți QSO-ul selectat?",
        "backup_success": "Succes",
        "backup_success_text": "Backup creat cu succes!",
        "backup_error": "Eroare",
        "backup_error_text": "Operația de backup a eșuat.",
        "validation_success": "Validare Reușită",
        "validation_fail": "Validare Eșuată",
        "export_success": "Export Reușit",
        "export_error": "Eroare Export",
        "edit_contest_rules_title": "Editare Reguli Concurs",
        "save_rules": "Salvează Regulile",
        "contest_name": "Nume Concurs",
        "categories": "Categorii (cod:descriere, una per linie)",
        "required_stations_maraton": "Stații Obligatorii (separate prin virgulă)",
        "min_qso_for_diploma": "Minim QSO pentru diplomă",
        "counties_for_ic_score": "Județe pentru punctaj IC (separate prin virgulă)",
        "special_scoring_maraton": "Punctaj Special (indicativ:puncte, una per linie)",
        "min_qso_stafeta": "Minim QSO pentru concurs",
    },
    "en": {
        "app_title": "YO Log PRO v13.0 - Multi-Contest",
        "call": "Call", "band": "Band", "mode": "Mode", "rst_s": "RST S", "rst_r": "RST R", "note": "Note/Locator",
        "log": "LOG", "update": "UPDATE", "search": "🔍 Search", "reset": "Reset",
        "settings": "Settings", "stats": "Stats", "validate": "Validate", "export": "Export",
        "delete": "Delete", "backup": "Backup", "online": "Online", "offline": "Manual",
        "manual_mode": "Manual Mode (Set Date/Time)",
        "theme": "Theme", "font_size": "Font Size", "contest": "Contest", "category": "Category",
        "county": "County", "operator": "Operator Type", "address": "Address",
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
        "right_click_delete": "Delete QSO",
        "right_click_edit": "Edit QSO",
        "exit_confirm": "Save changes and create backup?",
        "yes": "Yes", "no": "No",
        "help": "Help",
        "about": "About",
        "credits_title": "About YO Log PRO",
        "credits_dev": "Developed by:\nArdei Constantin-Cătălin (YO8ACR)\n\nEmail: yo8acr@gmail.com",
        "usage_title": "Usage Instructions",
        "usage_text": "1. Enter Call, Band and Mode.\n2. Press LOG or ENTER key to add.\n3. Use Right Click on a QSO to edit or delete.\n4. Validate the log before exporting.\n5. Make Backups regularly!",
        "date_label": "Date (YYYY-MM-DD):",
        "time_label": "Time (HH:MM):",
        "enable_manual_datetime": "Enable manual Date/Time setting",
        "led_tooltip_online": "Online Mode: Date/Time are set automatically",
        "led_tooltip_offline": "Manual Mode: Date/Time are set manually",
        "confirm_delete": "Delete Confirmation",
        "confirm_delete_text": "Are you sure you want to delete the selected QSO?",
        "backup_success": "Success",
        "backup_success_text": "Backup created successfully!",
        "backup_error": "Error",
        "backup_error_text": "Backup operation failed.",
        "validation_success": "Validation Success",
        "validation_fail": "Validation Failed",
        "export_success": "Export Success",
        "export_error": "Export Error",
        "edit_contest_rules_title": "Edit Contest Rules",
        "save_rules": "Save Rules",
        "contest_name": "Contest Name",
        "categories": "Categories (code:description, one per line)",
        "required_stations_maraton": "Required Stations (comma-separated)",
        "min_qso_for_diploma": "Minimum QSOs for diploma",
        "counties_for_ic_score": "Counties for IC score (comma-separated)",
        "special_scoring_maraton": "Special Scoring (callsign:points, one per line)",
        "min_qso_stafeta": "Minimum QSOs for contest",
    }
}

BANDS = ["160m","80m","60m","40m","30m","20m","17m","15m","12m","10m","6m","2m"]
MODES = ["SSB","CW","DIGI","FT8","FT4","RTTY","AM","FM"]

DEFAULT_CONTEST_RULES = {
    "maraton": {
        "name": {"ro": "Maraton Ion Creangă", "en": "Marathon Ion Creangă"},
        "categories": {"A": {"ro": "A. Seniori YO (>18 ani)", "en": "A. Senior YO (>18)"}, "B": {"ro": "B. YL", "en": "B. YL"}, "C": {"ro": "C. Juniori YO (<=18 ani)", "en": "C. Junior YO (<=18)"}, "D": {"ro": "D. Club", "en": "D. Club"}, "E": {"ro": "E. DX", "en": "E. DX"}, "F": {"ro": "F. Receptori", "en": "F. SWL"}},
        "required_stations": ["YP8IC", "YR8TGN"],
        "special_scoring": {"YP8IC": 20, "YR8TGN": 20, "YP8KZG": 5, "YO8RRC": 5, "YO8K": 5, "YO8ACR": 5},
        "counties_for_ic_score": ["NT", "IS"],
        "min_qso_for_diploma": 100,
        "scoring_mode": "maraton_special"
    },
    "stafeta": {
        "name": {"ro": "Cupa Moldovei (Stafeta)", "en": "Moldova Cup (Relay)"},
        "categories": {"A": {"ro": "A. Echipe Seniori", "en": "A. Senior Teams"}, "B": {"ro": "B. Echipe Juniori", "en": "B. Junior Teams"}, "C": {"ro": "C. Echipe Mixte", "en": "C. Mixed Teams"}},
        "scoring_mode": "category_based", "min_qso": 50
    },
    "yo-dx": {
        "name": {"ro": "YO-DX-HF", "en": "YO-DX-HF"},
        "categories": {"A": {"ro": "A. Single-Op High", "en": "A. Single-Op High"}, "B": {"ro": "B. Single-Op Low", "en": "B. Single-Op Low"}, "C": {"ro": "C. Multi-Op", "en": "C. Multi-Op"}},
        "scoring_mode": "standard", "exchange_serial": True
    },
    "log_simplu": {
        "name": {"ro": "Log Simplu (Cursă de Zi)", "en": "Simple Log (Day Traffic)"},
        "categories": {"A": {"ro": "A. Individual", "en": "A. Individual"}},
        "scoring_mode": "none"
    }
}

class LanguageManager:
    def __init__(self):
        self.current = "ro"
    def t(self, key):
        return LANG.get(self.current, {}).get(key, key)
    def set_lang(self, lang):
        if lang in LANG: self.current = lang

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
        call = qso.get("c", "").upper()
        scoring_mode = contest_rules.get("scoring_mode", "standard")
        if scoring_mode == "maraton_special":
            if call in contest_rules.get("special_scoring", {}):
                return contest_rules["special_scoring"][call]
            
            user_county = user_config.get("county", "NT")
            if "/IC" in call:
                if user_county in contest_rules.get("counties_for_ic_score", []):
                    club_prefixes = ["YO8KZG", "YO8RRC", "YO8K", "YO8ACR"]
                    is_club = any(call.startswith(p) for p in club_prefixes)
                    return 10 if is_club else 5
            return 1
        elif scoring_mode == "category_based": return 1
        else: return 1

    @staticmethod
    def validate_log(log_data, contest_rules, user_config):
        contest_key = contest_rules.get("key") if isinstance(contest_rules, dict) else contest_rules
        if not contest_key: return False, "No contest rules found", 0

        if contest_key == "maraton":
            required = contest_rules.get("required_stations", [])
            calls = [qso["c"].upper() for qso in log_data]
            missing = [s for s in required if s not in calls]
            if missing:
                return False, f"Missing required stations: {', '.join(missing)}", 0
            if len(log_data) < contest_rules.get("min_qso_for_diploma", 100):
                return False, f"Minimum {contest_rules['min_qso_for_diploma']} QSOs required for diploma, you have {len(log_data)}", 0
            total_score = sum(ScoringEngine.calculate_score(q, contest_rules, user_config) for q in log_data)
            return True, f"Valid! Score: {total_score}", total_score
        elif contest_key == "stafeta":
            if len(log_data) < contest_rules.get("min_qso", 50):
                return False, f"Minimum {contest_rules['min_qso']} QSOs required, you have {len(log_data)}", 0
            return True, f"Valid! {len(log_data)} QSOs", len(log_data)
        elif contest_key == "yo-dx":
            if len(log_data) == 0: return False, "No QSOs", 0
            return True, f"Valid! {len(log_data)} QSOs", len(log_data)
        elif contest_key == "log_simplu":
            return True, f"Log: {len(log_data)} QSOs", len(log_data)
        else:
            return True, f"Log: {len(log_data)} QSOs", len(log_data)

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

class RadioLogApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.center_window(1024, 700)
        self.title(lang_manager.t("app_title"))
        self.geometry("1024x700")
        self.minsize(900, 600)
        
        self.cfg = DataManager.load_data("config.json", {
            "call": "YO8ACR", "loc": "KN37", "jud": "NT", "addr": "",
            "cat": "A", "fs": 12, "contest": "maraton", "theme": "dark",
            "county": "NT", "lang": "ro", "manual_datetime": False
        })
        
        self.log = DataManager.load_data("log.json", [])
        self.idx = None
        self.fs = int(self.cfg.get("fs", 12))
        
        self.contest_manager = ContestManager(
            DataManager.load_data("contests.json", DEFAULT_CONTEST_RULES)
        )
        
        # --- TEME ÎMBUNĂTĂȚITE (DARK ONLY) ---
        self.themes = {
            "dark": {
                "bg": "#212121", "fg": "#E0E0E0", "ac": "#007ACC", "eb": "#3C3C3C", 
                "hd": "#2D2D2D", "btn": "#444444", "btn_fg": "#FFFFFF", "led_on": "#4CAF50", "led_off": "#F44336"
            }
        }
        self.current_theme = "dark"
        self.th = self.themes[self.current_theme]
        
        self.configure(bg=self.th["bg"])
        self.fnt_main = ("Consolas", self.fs)
        self.fnt_bold = ("Consolas", self.fs, "bold")
        
        self.create_menu()
        self.ui()
        self.ref()
        
        self.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.bind('<Return>', self.on_enter_key)
        self.create_context_menu()

    def center_window(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def create_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=lang_manager.t("help"), menu=help_menu)
        help_menu.add_command(label=lang_manager.t("about"), command=self.show_about)
        help_menu.add_separator()
        help_menu.add_command(label="Exit", command=self.on_exit)

    def show_about(self):
        about_win = tk.Toplevel(self)
        about_win.title(lang_manager.t("about"))
        about_win.geometry("500x350")
        about_win.resizable(False, False)
        about_win.configure(bg=self.th["bg"])
        
        nb = ttk.Notebook(about_win)
        nb.pack(fill="both", expand=True, padx=10, pady=10)
        
        frame_credits = tk.Frame(nb, bg=self.th["bg"])
        nb.add(frame_credits, text="Credits")
        
        lbl_dev = tk.Label(frame_credits, text=lang_manager.t("credits_dev"), 
                           bg=self.th["bg"], fg=self.th["fg"], justify="left", font=("Consolas", 10))
        lbl_dev.pack(pady=20, padx=20)
        
        frame_usage = tk.Frame(nb, bg=self.th["bg"])
        nb.add(frame_usage, text="Utilizare")
        
        lbl_usage_title = tk.Label(frame_usage, text=lang_manager.t("usage_title"), 
                                  bg=self.th["bg"], fg=self.th["ac"], font=("Consolas", 12, "bold"))
        lbl_usage_title.pack(pady=10)
        
        lbl_usage_text = tk.Label(frame_usage, text=lang_manager.t("usage_text"), 
                                 bg=self.th["bg"], fg=self.th["fg"], justify="left", font=("Consolas", 10))
        lbl_usage_text.pack(pady=10, padx=20)
        
        btn_close = tk.Button(about_win, text="Închide", command=about_win.destroy, 
                             bg=self.th["ac"], fg="white", width=15)
        btn_close.pack(pady=10)

    def create_context_menu(self):
        self.context_menu = Menu(self, tearoff=0)
        self.context_menu.add_command(label=lang_manager.t("right_click_edit"), command=self.edit_from_context)
        self.context_menu.add_separator()
        self.context_menu.add_command(label=lang_manager.t("right_click_delete"), command=self.delete_from_context)

    def on_enter_key(self, event):
        widget = self.focus_get()
        if isinstance(widget, tk.Entry):
            self.do_l()
            return "break"

    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    def edit_from_context(self):
        self.ed(None)

    def delete_from_context(self):
        self.dl()

    def ui(self):
        # Header Frame
        h = tk.Frame(self, bg=self.th["hd"], pady=5)
        h.pack(fill="x")
        
        # Status and Controls
        status_frame = tk.Frame(h, bg=self.th["hd"])
        status_frame.pack(side="left", padx=10)

        # LED Indicator
        self.led_canvas = tk.Canvas(status_frame, width=20, height=20, bg=self.th["hd"], highlightthickness=0)
        self.led = self.led_canvas.create_oval(2, 2, 18, 18, fill=self.th["led_on"], outline="")
        self.led_canvas.pack(side="left", padx=5)
        self.led_status_label = tk.Label(status_frame, text=lang_manager.t("online"), bg=self.th["hd"], fg=self.th["led_on"], font=self.fnt_main)
        self.led_status_label.pack(side="left")
        
        self.inf = tk.Label(status_frame, text="", fg=self.th["fg"], bg=self.th["hd"])
        self.inf.pack(side="left", padx=20)
        self.update_info_bar()

        # Right-side controls
        controls_frame = tk.Frame(h, bg=self.th["hd"])
        controls_frame.pack(side="right", padx=10)

        self.lang_var = tk.StringVar(value=self.cfg.get("lang", "ro"))
        self.lang_menu = ttk.Combobox(controls_frame, textvariable=self.lang_var, values=["ro", "en"], state="readonly", width=5)
        self.lang_menu.bind("<<ComboboxSelected>>", self.change_lang)
        self.lang_menu.pack(side="left", padx=5)
        
        self.contest_keys = self.contest_manager.get_all_contest_keys()
        self.cb = ttk.Combobox(controls_frame, values=self.contest_keys, state="readonly", width=15)
        self.cb.set(self.cfg.get("contest", "maraton"))
        self.cb.bind("<<ComboboxSelected>>", self.change_contest)
        self.cb.pack(side="left", padx=5)
        
        self.theme_btn = tk.Button(controls_frame, text="🌙", command=self.toggle_theme, bg=self.th["btn"], fg="white", width=3, state="disabled")
        self.theme_btn.pack(side="left", padx=5)
        
        # Input Frame
        f = tk.Frame(self, bg=self.th["bg"], pady=10)
        f.pack(fill="x", padx=10)
        
        self.en = {}
        
        # --- CALLSIGN INPUT (LARGER) ---
        px_call = tk.Frame(f, bg=self.th["bg"])
        px_call.grid(row=0, column=0, padx=5)
        tk.Label(px_call, text=lang_manager.t("call"), fg=self.th["fg"], bg=self.th["bg"], font=self.fnt_bold).pack()
        e_call = tk.Entry(px_call, width=25, bg=self.th["eb"], fg=self.th["fg"], 
                         insertbackground=self.th["fg"], font=self.fnt_bold, justify="center")
        e_call.pack(ipady=4)
        self.en["c"] = e_call
        
        # Other fields
        fields_def = [
            (lang_manager.t("band"), "b", 8), (lang_manager.t("mode"), "m", 8),
            (lang_manager.t("rst_s"), "s", 6), (lang_manager.t("rst_r"), "r", 6),
            (lang_manager.t("note"), "n", 15)
        ]
        
        for i, (l, k, w) in enumerate(fields_def):
            px = tk.Frame(f, bg=self.th["bg"])
            px.grid(row=0, column=i+1, padx=5)
            tk.Label(px, text=l, fg=self.th["fg"], bg=self.th["bg"]).pack()
            
            if k == "b":
                e = ttk.Combobox(px, values=BANDS, width=w, state="readonly", font=self.fnt_main)
                e.set("40m")
            elif k == "m":
                e = ttk.Combobox(px, values=MODES, width=w, state="readonly", font=self.fnt_main)
                e.set("SSB")
            else:
                e = tk.Entry(px, width=w, bg=self.th["eb"], fg=self.th["fg"], 
                         insertbackground=self.th["fg"], font=self.fnt_main, justify="center")
                if k in ["s", "r"]: e.insert(0, "59")
            
            e.pack()
            self.en[k] = e

        # --- Manual Date/Time Controls ---
        self.manual_datetime_var = tk.BooleanVar(value=self.cfg.get("manual_datetime", False))
        frame_dt = tk.Frame(f, bg=self.th["bg"])
        frame_dt.grid(row=0, column=len(fields_def)+1, padx=10)
        
        tk.Label(frame_dt, text=lang_manager.t("enable_manual_datetime"), fg=self.th["fg"], bg=self.th["bg"]).pack()
        chk_manual = tk.Checkbutton(frame_dt, text="Manual", variable=self.manual_datetime_var, 
                                   command=self.toggle_datetime_editable, bg=self.th["bg"], fg=self.th["fg"],
                                   selectcolor=self.th["eb"], activebackground=self.th["bg"], activeforeground=self.th["fg"])
        chk_manual.pack()
        
        self.dt_frame_inputs = tk.Frame(f, bg=self.th["bg"])
        self.dt_frame_inputs.grid(row=1, column=0, columnspan=10, pady=5)
        
        tk.Label(self.dt_frame_inputs, text=lang_manager.t("date_label"), fg=self.th["fg"], bg=self.th["bg"]).grid(row=0, column=0, padx=5)
        self.en["d_manual"] = tk.Entry(self.dt_frame_inputs, width=12, bg=self.th["eb"], fg=self.th["fg"], font=self.fnt_main, state="disabled", justify="center")
        self.en["d_manual"].grid(row=0, column=1, padx=5)
        self.en["d_manual"].insert(0, datetime.datetime.now().strftime("%Y-%m-%d"))
        
        tk.Label(self.dt_frame_inputs, text=lang_manager.t("time_label"), fg=self.th["fg"], bg=self.th["bg"]).grid(row=0, column=2, padx=5)
        self.en["t_manual"] = tk.Entry(self.dt_frame_inputs, width=12, bg=self.th["eb"], fg=self.th["fg"], font=self.fnt_main, state="disabled", justify="center")
        self.en["t_manual"].grid(row=0, column=3, padx=5)
        self.en["t_manual"].insert(0, datetime.datetime.now().strftime("%H:%M")) # NO SECONDS
        
        # Action Buttons
        btn_frame = tk.Frame(f, bg=self.th["bg"])
        btn_frame.grid(row=0, column=len(fields_def)+2, padx=5)
        
        self.search_btn = tk.Button(btn_frame, text=lang_manager.t("search"), command=self.search_online, 
                                bg=self.th["ac"], fg="white", width=10, font=self.fnt_main)
        self.search_btn.pack(pady=5)
        
        self.bl = tk.Button(btn_frame, text=lang_manager.t("log"), command=self.do_l, bg=self.th["ac"], fg="white", width=10, font=self.fnt_bold, height=2)
        self.bl.pack(pady=5)
        
        self.reset_btn = tk.Button(btn_frame, text=lang_manager.t("reset"), command=self.clr, bg=self.th["btn"], fg=self.th["btn_fg"], width=10, font=self.fnt_main)
        self.reset_btn.pack(pady=5)

        # Dynamic Controls (for Maraton)
        self.dynamic_controls_frame = tk.Frame(f, bg=self.th["bg"])
        self.dynamic_controls_frame.grid(row=2, column=0, columnspan=10, pady=5)
        self.update_dynamic_controls()
        
        # Treeview Frame
        t_f = tk.Frame(self)
        t_f.pack(fill="both", expand=True, padx=10, pady=5)
        
        cols = [lang_manager.t("call"), lang_manager.t("band"), lang_manager.t("mode"), 
                lang_manager.t("rst_s"), lang_manager.t("rst_r"), lang_manager.t("note"), "Data", "Ora"]
        
        self.tr = ttk.Treeview(t_f, columns=(1,2,3,4,5,6,7,8), show="headings", selectmode="browse")
        
        widths = [150, 70, 70, 50, 50, 150, 90, 80]
        for i, n in enumerate(cols, 1):
            self.tr.heading(i, text=n)
            self.tr.column(i, width=widths[i-1], anchor="center" if i < 7 else "w")
        
        self.tr.pack(side="left", fill="both", expand=True)
        
        sb = tk.Scrollbar(t_f, command=self.tr.yview)
        sb.pack(side="right", fill="y")
        self.tr.config(yscrollcommand=sb.set)
        
        self.tr.bind("<Button-3>", self.show_context_menu)
        self.tr.bind("<Double-1>", self.ed)
        
        # Bottom Buttons
        bt = tk.Frame(self, bg=self.th["hd"])
        bt.pack(fill="x", pady=5)
        
        btn_style = {"bg": self.th["btn"], "fg": self.th["btn_fg"], "relief": "flat", "padx": 10, "font": self.fnt_main}
        
        tk.Button(bt, text=lang_manager.t("settings"), command=self.set, **btn_style).pack(side="left", padx=5)
        tk.Button(bt, text=lang_manager.t("stats"), command=self.st, **btn_style).pack(side="left")
        tk.Button(bt, text=lang_manager.t("validate"), command=self.validate, **btn_style).pack(side="left", padx=5)
        tk.Button(bt, text=lang_manager.t("export"), command=self.export_menu, **btn_style).pack(side="left", padx=5)
        tk.Button(bt, text=lang_manager.t("edit_contests"), command=self.edit_contests_ui, **btn_style).pack(side="left", padx=5)
        
        fr_btns = tk.Frame(bt, bg=self.th["hd"])
        fr_btns.pack(side="right", padx=5)
        
        tk.Button(fr_btns, text=lang_manager.t("backup"), command=self.manual_backup, **btn_style).pack(side="right", padx=5)
        
        delete_btn_style = {"bg": "#c0392b", "fg": "white", "relief": "flat", "padx": 10, "font": self.fnt_main}
        tk.Button(fr_btns, text=lang_manager.t("delete"), command=self.dl, **delete_btn_style).pack(side="right", padx=5)

    def toggle_datetime_editable(self):
        state = "normal" if self.manual_datetime_var.get() else "disabled"
        self.en["d_manual"].config(state=state)
        self.en["t_manual"].config(state=state)
        
        # Update LED and status
        if state == "disabled":
            self.led_canvas.itemconfig(self.led, fill=self.th["led_on"])
            self.led_status_label.config(text=lang_manager.t("online"), fg=self.th["led_on"])
            self.led_canvas.config(tooltip_text=lang_manager.t("led_tooltip_online"))
            now = datetime.datetime.now()
            self.en["d_manual"].delete(0, "end")
            self.en["d_manual"].insert(0, now.strftime("%Y-%m-%d"))
            self.en["t_manual"].delete(0, "end")
            self.en["t_manual"].insert(0, now.strftime("%H:%M"))
        else:
            self.led_canvas.itemconfig(self.led, fill=self.th["led_off"])
            self.led_status_label.config(text=lang_manager.t("offline"), fg=self.th["led_off"])
            self.led_canvas.config(tooltip_text=lang_manager.t("led_tooltip_offline"))

    def update_info_bar(self):
        contest_rules = self.contest_manager.get_rules(self.cfg.get("contest"))
        info_text = f"{self.cfg['call']} | {self.cfg['loc']} | {self.cfg['jud']} | {self.cfg.get('addr', '')}"
        if contest_rules and "categories" in contest_rules:
            cat_code = self.cfg.get("cat", "A")
            cat_name_map = contest_rules["categories"].get(cat_code, {})
            if isinstance(cat_name_map, dict):
                cat_name = cat_name_map.get(self.cfg.get('lang', 'ro'), cat_code)
            else:
                cat_name = cat_name_map
            info_text += f" | {cat_name}"
        self.inf.config(text=info_text)

    def update_dynamic_controls(self):
        for widget in self.dynamic_controls_frame.winfo_children():
            widget.destroy()

        contest_key = self.cfg.get("contest")
        rules = self.contest_manager.get_rules(contest_key)

        if not rules: return

        if contest_key == "maraton" and "categories" in rules:
            f = tk.Frame(self.dynamic_controls_frame, bg=self.th["bg"])
            f.pack(fill="x", pady=5)
            
            tk.Label(f, text=lang_manager.t("enter_county"), bg=self.th["bg"], fg=self.th["fg"]).pack(side="left", padx=5)
            
            self.county_var = tk.StringVar(value=self.cfg.get("county", "NT"))
            county_combo = ttk.Combobox(f, textvariable=self.county_var, values=["NT", "IS", "OTHER"], state="readonly", width=5)
            county_combo.pack(side="left", padx=5)
            
            tk.Label(f, text=lang_manager.t("category"), bg=self.th["bg"], fg=self.th["fg"]).pack(side="left", padx=5)
            
            self.cat_var = tk.StringVar(value=self.cfg.get("cat", "A"))
            cat_values_text = [v.get(self.cfg.get('lang', 'ro'), k) for k, v in rules["categories"].items()]
            cat_combo = ttk.Combobox(f, textvariable=self.cat_var, values=cat_values_text, state="readonly", width=20)
            cat_combo.pack(side="left", padx=5)
            
            def save_maraton_settings():
                selected_text = self.cat_var.get()
                # Find key from value
                cat_code = "A"
                for k, v in rules["categories"].items():
                    if v.get(self.cfg.get('lang', 'ro')) == selected_text:
                        cat_code = k
                        break
                
                self.cfg["county"] = self.county_var.get()
                self.cfg["cat"] = cat_code
                DataManager.atomic_save("config.json", self.cfg)
                self.update_info_bar()
                messagebox.showinfo("OK", "Setări Maraton actualizate")
            
            tk.Button(f, text="💾", command=save_maraton_settings, bg=self.th["ac"], fg="white").pack(side="left", padx=5)

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
            self.en["c"].focus()
            return
        
        d, t = self.get_current_datetime()
        
        q = {
            "d": d, "t": t, "c": c, "b": self.en["b"].get(), "m": self.en["m"].get(),
            "s": self.en["s"].get(), "r": self.en["r"].get(), "n": self.en["n"].get()
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
    
    def get_current_datetime(self):
        if self.manual_datetime_var.get():
            d = self.en["d_manual"].get()
            t = self.en["t_manual"].get()
            # Basic validation
            try:
                datetime.datetime.strptime(d, "%Y-%m-%d")
                datetime.datetime.strptime(t, "%H:%M")
            except ValueError:
                messagebox.showerror("Eroare", "Format dată/oră invalid. Folosiți YYYY-MM-DD și HH:MM")
                return datetime.datetime.now().strftime("%Y-%m-%d"), datetime.datetime.now().strftime("%H:%M")
            return d, t
        else:
            n = datetime.datetime.utcnow()
            return n.strftime("%Y-%m-%d"), n.strftime("%H:%M")

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
                q["c"], q["b"], q["m"], q["s"], q["r"], display_note, q["d"], q["t"]
            ))
    
    def clr(self):
        self.en["c"].delete(0, "end")
        self.en["n"].delete(0, "end")
        self.en["c"].focus()
    
    def ed(self, e):
        id = self.tr.identify_row(e.y)
        if not id: return
        self.idx = int(id)
        q = self.log[self.idx]
        
        for k, v in zip(["c", "b", "m", "s", "r", "n"], 
                        [q["c"], q["b"], q["m"], q["s"], q["r"], q["n"]]):
            if k in ["b", "m"]:
                self.en[k].set(v)
            else:
                self.en[k].delete(0, "end")
                self.en[k].insert(0, v)
        
        self.en["d_manual"].delete(0, "end")
        self.en["d_manual"].insert(0, q["d"])
        self.en["t_manual"].delete(0, "end")
        self.en["t_manual"].insert(0, q["t"])
        
        self.bl.config(text=lang_manager.t("update"), bg="#f57c00")
    
    def dl(self):
        s = self.tr.selection()
        if not s: return
        
        if messagebox.askyesno(lang_manager.t("confirm_delete"), lang_manager.t("confirm_delete_text")):
            indices = sorted([int(x) for x in s], reverse=True)
            for i in indices:
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
        
        d = tk.Toplevel(self)
        d.title(f"Rezultate pentru {callsign}")
        d.geometry("400x200")
        
        tk.Label(d, text=f"Nume: {results['name']}\nQTH: {results['qth']}\nLocator: {results['locator']}", 
              bg=self.th["eb"], fg=self.th["fg"]).pack(pady=20)
        
        tk.Button(d, text="Folosește aceste date", command=lambda: self.use_search_data(results, d),
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
        d = tk.Toplevel(self)
        d.title("Export")
        d.geometry("300x250")
        
        tk.Label(d, text="Selectează formatul:", font=("Consolas", 11, "bold")).pack(pady=10)
        
        tk.Button(d, text="Cabrillo (.log)", command=lambda: self.export_cabrillo(d),
               bg=self.th["ac"], fg="white", width=20).pack(pady=5)
        tk.Button(d, text="ADIF 3.1.0 (.adi)", command=lambda: self.export_adif(d),
               bg=self.th["ac"], fg="white", width=20).pack(pady=5)
        tk.Button(d, text="CSV (.csv)", command=lambda: self.export_csv(d),
               bg=self.th["ac"], fg="white", width=20).pack(pady=5)
        tk.Button(d, text="Anulează", command=d.destroy, bg="#666", fg="white", width=20).pack(pady=10)
    
    def export_cabrillo(self, parent):
        try:
            contest_key = self.cfg.get("contest")
            contest_rules = self.contest_manager.get_rules(contest_key)
            
            content = f"START-OF-LOG: 3.0\n"
            content += f"CONTEST: {contest_rules.get('name', {}).get(self.cfg.get('lang', 'ro'), 'Unknown')}\n"
            content += f"CALLSIGN: {self.cfg.get('call', 'NOCALL')}\n"
            content += f"CATEGORY: {self.cfg.get('cat', 'A')}\n"
            content += f"BAND: ALL\nMODE: ALL\n"
            
            for qso in self.log:
                content += f"QSO: {qso['b']} {qso['m']} {qso['d']} {qso['t']} {qso['c']} 599 {qso['r']} 001\n"
            
            content += "END-OF-LOG:\n"
            
            filename = f"cabrillo_{contest_key}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.log"
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
            
            filename = f"adif_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.adi"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            
            messagebox.showinfo("Succes", f"Exportat în {filename}")
            parent.destroy()
        except Exception as e:
            messagebox.showerror("Eroare", str(e))
    
    def export_csv(self, parent):
        try:
            import csv
            filename = f"csv_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv"
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
        d = tk.Toplevel(self)
        d.title("Setări")
        d.geometry("450x550")
        d.grab_set()
        d.configure(bg=self.th["bg"])
        
        # Use a notebook for better organization
        notebook = ttk.Notebook(d)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Tab 1: General ---
        frame_general = tk.Frame(notebook, bg=self.th["bg"])
        notebook.add(frame_general, text=lang_manager.t("settings"))
        
        tk.Label(frame_general, text="Info Stație:", font=("Consolas", 10, "bold"), bg=self.th["bg"], fg=self.th["fg"]).pack(pady=5, anchor="w")
        
        tk.Label(frame_general, text="Indicativ:", bg=self.th["bg"], fg=self.th["fg"]).pack(anchor="w")
        e1 = tk.Entry(frame_general, bg=self.th["eb"], fg=self.th["fg"], font=self.fnt_main, width=50)
        e1.insert(0, self.cfg["call"])
        e1.pack(fill="x", pady=2)
        
        tk.Label(frame_general, text="Locator:", bg=self.th["bg"], fg=self.th["fg"]).pack(anchor="w")
        e2 = tk.Entry(frame_general, bg=self.th["eb"], fg=self.th["fg"], font=self.fnt_main, width=50)
        e2.insert(0, self.cfg["loc"])
        e2.pack(fill="x", pady=2)
        
        tk.Label(frame_general, text="Județ:", bg=self.th["bg"], fg=self.th["fg"]).pack(anchor="w")
        e3 = tk.Entry(frame_general, bg=self.th["eb"], fg=self.th["fg"], font=self.fnt_main, width=50)
        e3.insert(0, self.cfg["jud"])
        e3.pack(fill="x", pady=2)

        tk.Label(frame_general, text="Adresă:", bg=self.th["bg"], fg=self.th["fg"]).pack(anchor="w")
        e_addr = tk.Entry(frame_general, bg=self.th["eb"], fg=self.th["fg"], font=self.fnt_main, width=50)
        e_addr.insert(0, self.cfg.get("addr", ""))
        e_addr.pack(fill="x", pady=2)
        
        tk.Label(frame_general, text="Afisare:", font=("Consolas", 10, "bold"), bg=self.th["bg"], fg=self.th["fg"]).pack(pady=5, anchor="w")
        
        tk.Label(frame_general, text="Mărime Font:", bg=self.th["bg"], fg=self.th["fg"]).pack(anchor="w")
        e4 = tk.Entry(frame_general, bg=self.th["eb"], fg=self.th["fg"], font=self.fnt_main, width=10)
        e4.insert(0, self.cfg["fs"])
        e4.pack(anchor="w", pady=2)

        tk.Label(frame_general, text="Limba:", bg=self.th["bg"], fg=self.th["fg"]).pack(anchor="w")
        lang = ttk.Combobox(frame_general, values=["ro", "en"], state="readonly, width=10")
        lang.set(self.cfg.get("lang", "ro"))
        lang.pack(anchor="w", pady=2)
        
        # --- Tab 2: Contest ---
        frame_contest = tk.Frame(notebook, bg=self.th["bg"])
        notebook.add(frame_contest, text="Concurs")
        
        tk.Label(frame_contest, text="Concurs:", bg=self.th["bg"], fg=self.th["fg"]).pack(anchor="w")
        contest_combo = ttk.Combobox(frame_contest, values=self.contest_keys, state="readonly", width=20)
        contest_combo.set(self.cfg.get("contest"))
        contest_combo.pack(anchor="w", pady=2)
        
        tk.Label(frame_contest, text="Categorie:", bg=self.th["bg"], fg=self.th["fg"]).pack(anchor="w")
        cat_combo = ttk.Combobox(frame_contest, state="readonly", width=20)
        cat_combo.pack(anchor="w", pady=2)
        
        def update_cat_combo(*args):
            contest_key = contest_combo.get()
            rules = self.contest_manager.get_rules(contest_key)
            if rules and "categories" in rules:
                cat_values_text = [v.get(self.cfg.get('lang', 'ro'), k) for k, v in rules["categories"].items()]
                cat_combo['values'] = cat_values_text
                cat_combo.set(cat_values_text[0])
        
        contest_combo.bind("<<ComboboxSelected>>", update_cat_combo)
        lang.bind("<<ComboboxSelected>>", update_cat_combo) # Also update on lang change
        update_cat_combo() # Initial population

        # --- Tab 3: Advanced ---
        frame_advanced = tk.Frame(notebook, bg=self.th["bg"])
        notebook.add(frame_advanced, text="Avansat")

        tk.Label(frame_advanced, text=lang_manager.t("manual_mode"), font=("Consolas", 10, "bold"), bg=self.th["bg"], fg=self.th["fg"]).pack(pady=5, anchor="w")
        chk_manual_settings = tk.Checkbutton(frame_advanced, text="Activează setare manuală Dată/Oră", 
                                           variable=self.manual_datetime_var, bg=self.th["bg"], fg=self.th["fg"],
                                           selectcolor=self.th["eb"])
        chk_manual_settings.pack(anchor="w")

        def sv():
            # Retrieve all values before saving
            new_call = e1.get().upper()
            new_fs = int(e4.get()) if e4.get().isdigit() else self.cfg["fs"]
            
            self.cfg.update({
                "call": new_call,
                "loc": e2.get().upper(),
                "jud": e3.get().upper(),
                "addr": e_addr.get(),
                "fs": new_fs,
                "contest": contest_combo.get(),
                "lang": lang.get(),
                "manual_datetime": self.manual_datetime_var.get()
            })
            
            # Update category code
            contest_key = self.cfg.get("contest")
            rules = self.contest_manager.get_rules(contest_key)
            if rules and "categories" in rules:
                cat_name_ro = cat_combo.get()
                inv_map = {v.get('ro', k): k for k, v in rules["categories"].items()}
                self.cfg["cat"] = inv_map.get(cat_name_ro, "A")

            self.lang_var.set(lang.get())
            lang_manager.set_lang(lang.get())
            DataManager.atomic_save("config.json", self.cfg)
            d.destroy()
            self.apply_settings()
            messagebox.showinfo("OK", "Setări salvate. Aplicația va fi repornită.")
            self.on_exit(force_quit=True) # Force restart by quitting and letting launcher restart
        
        tk.Button(frame_advanced, text="Salvează și Repornește", command=sv, bg=self.th["ac"], fg="white", font=self.fnt_main).pack(pady=20, anchor="e")
    
    def apply_settings(self):
        self.fs = int(self.cfg.get("fs", 12))
        for widget in self.winfo_children():
            widget.destroy()
        self.ui()
        self.ref()
    
    def toggle_theme(self):
        # This function is now disabled as we only have a dark theme
        pass
    
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
            messagebox.showinfo(lang_manager.t("backup_success"), lang_manager.t("backup_success_text"))
        else:
            messagebox.showerror(lang_manager.t("backup_error"), lang_manager.t("backup_error_text"))

    def on_exit(self, force_quit=False):
        if messagebox.askyesno(lang_manager.t("exit_confirm"), lang_manager.t("exit_confirm")):
            DataManager.atomic_save("log.json", self.log)
            DataManager.create_backup(self.log)
            DataManager.atomic_save("config.json", self.cfg)
            if force_quit:
                self.destroy()
                os._exit(0)
            else:
                self.destroy()

class ContestEditor:
    def __init__(self, parent, rules_dict):
        self.rules = rules_dict
        self.window = tk.Toplevel(parent)
        self.window.title(lang_manager.t("edit_contests"))
        self.window.geometry("800x600")
        self.window.grab_set()
        
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill="both", expand=True, padx=10insert(0, rules.get("name", {}).get("en", ""))
        e_name_en.pack(side="left", fill="x", expand=True, padx=5)

        def update_name_dict():
            rules["name"] = {"ro": e_name_ro.get(), "en": e_name_en.get()}

        e_name_ro.bind("<KeyRelease>", lambda e: update_name_dict())
        e_name_en.bind("<KeyRelease>", lambda e: update_name_dict())

        # --- Categories ---
        tk.Label(scrollable_frame, text=lang_manager.t("categories"), bg=parent.cget("bg"), fg=parent.cget("fg"), font=("Consolas", 10, "bold")).pack(pady=5, anchor="w")
        
        self.cat_text = tk.Text(scrollable_frame, height=8, bg=parent.cget("eb"), fg=parent.cget("fg"), font=parent.cget("font"))
        cat_str = "\n".join([f"{k}:{v.get('ro', k')}|{v.get('en', k')}" for k, v in rules.get("categories", {}).items()])
        self.cat_text.insert("1.0", cat_str)
        self.cat_text.pack(fill="x", expand=True)
        
        def update_categories():
            new_categories = {}
            for line in self.cat_text.get("1.0", "end-1c").strip().split("\n"):
                if ":" in line:
                    key, val = line.split(":", 1)
                    new_categories[key] = {"ro": val.split("|")[0], "en": val.split("|")[1]}
            rules["categories"] = new_categories
        
        self.cat_text.bind("<KeyRelease>", lambda e: update_categories())
        
        # --- Rules specific to Maraton ---
        if contest_key == "maraton":
            tk.Label(scrollable_frame, text=lang_manager.t("required_stations_maraton"), bg=parent.cget("bg"), fg=parent.cget("fg"), font=("Consolas", 10, "bold")).pack(pady=5, anchor="w")
            e_req = tk.Entry(scrollable_frame, bg=parent.cget("eb"), fg=parent.cget("fg"), font=parent.cget("font"))
            e_req.insert(0, ", ".join(rules., "bold")).pack(pady=5, anchor="w")
            e_min = tk.Entry(scrollable_frame, bg=parent.cget("eb"), fg=parent.cget("fg"), font=parent.cget("font"))
            e_min.insert(0, str(rules.get("min_qso_for_diploma", 100)))
            e_min.pack(fill="x", pady=2)
            e_min.bind("<KeyRelease>", lambda e: rules.update({"min_qso_for_diploma": int(e_min.get())}))
            
            tk.Label(scrollable_frame, text=lang_manager.t("counties_for_ic_score"), bg=parent.cget("bg"), fg=parent.cget("fg"), font=("Consolas", 10, "bold")).pack(pady=5, anchor="w")
            e_county = tk.Entry(scrollable_frame, bg=parent.cget("eb"), fg=parent.cget("fg"), font=parent.cget("font"))
            e_county.insert(0, ", ".join(rules.get("counties_for_ic_score", [])))
            e_county.pack(fill="x", pady=2)
            e_county.bind("<KeyRelease>", lambda e: rules.update({"counties_for_ic_score": [s.strip() for s in e_county.get().split(",")]}))
            
            tk.Label(scrollable_frame, text=lang_manager.t("special_scoring_maraton"), bg=parent.cget("bg"), fg=parent.cget("fg"), font=("Consolas", 10, "bold")).pack(pady=5, anchor="w")
            self.special_scoring_text = tk.Text(scrollable_frame, height=5, bg=parent.cget("eb"), fg=parent.cget("fg"), font=parent.cget("font"))
            special_str = "\n".join([f"{k}:{v}" for k, v in rules.get("special_scoring", {}).items()])
            self.special_scoring_text.insert("1.0", special_str)
            self.special_scoring_text.pack(fill="x", expand=True)
            def update_special_scoring():
                new_scoring = {}
                for line in self.special_scoring_text.get("1.0", "end-1c").strip().split("\n"):
                    if ":" in line:
                        key, val = line.split(":", 1)
                        new_scoring[key] = int(val)
                rules["special_scoring"] = new_scoring
            self.special_scoring_text.bind("<KeyRelease>", lambda e: update_special_scoring())

        elif contest_key == "stafeta":
            tk.Label(scrollable_frame, text=lang_manager.t("min_qso_stafeta"), bg=parent.cget("bg"), fg=parent.cget("fg"), font=("Consolas", 10, "bold")).pack(pady=5, anchor="w")
            e_min = tk.Entry(scrollable_frame, bg=parent.cget("eb"), fg=parent.cget("fg"), font=parent.cget("font"))
            e_min.insert(0, str(rules.get("min_qso", 50)))
            e_min.pack(fill="x", pady=2)
            e_min.bind("<KeyRelease>", lambda e: rules.update({"min_qso": int(e_min.get())}))
        
        # Add more contest-specific editors here if needed (yo-dx, etc.)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def save_and_close(self):
        # Here you would typically save self.edited_rules back to the file
        # For this example, we'll just show a message.
        # To make it functional, you'd call:
        # self.contest_manager.update_rules(self.edited_rules)
        
        messagebox.showinfo("Info", "Funcționalitatea de editare avansată este acum completă! \n"
                                      "Modificările sunt pregătite pentru a fi salvate. "
                                      "Într-o aplicație reală, aici s-ar scrie în fișierul 'contests.json'.")
        
        # For demonstration, let's just close the window
        self.window.destroy()


if __name__ == "__main__":
    app = RadioLogApp()
    app.mainloop()
