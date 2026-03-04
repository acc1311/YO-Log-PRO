#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YO Log PRO v13.0 - Multi-Contest Amateur Radio Logger
Developed by: Ardei Constantin-Cătălin (YO8ACR)
Email: yo8acr@gmail.com
"""

import os
import sys
import json
import datetime
from pathlib import Path
from collections import Counter
import tkinter as tk
from tkinter import ttk, messagebox, Menu


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def get_data_dir():
    """Get writable data directory"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.abspath(".")


# =============================================================================
# CONSTANTS
# =============================================================================

BANDS = ["160m", "80m", "60m", "40m", "30m", "20m", "17m", "15m", "12m", "10m", "6m", "2m"]
MODES = ["SSB", "CW", "DIGI", "FT8", "FT4", "RTTY", "AM", "FM"]

TRANSLATIONS = {
    "ro": {
        "app_title": "YO Log PRO v13.0 - Multi-Contest",
        "call": "Indicativ",
        "band": "Bandă",
        "mode": "Mod",
        "rst_s": "RST S",
        "rst_r": "RST R",
        "note": "Notă/Locator",
        "log": "LOG",
        "update": "ACTUALIZEAZĂ",
        "search": "🔍 Caută",
        "reset": "Reset",
        "settings": "Setări",
        "stats": "Statistici",
        "validate": "Validează",
        "export": "Export",
        "delete": "Șterge",
        "backup": "Backup",
        "online": "Online",
        "offline": "Manual",
        "category": "Categorie",
        "county": "Județ",
        "required_stations": "Stații Obligatorii",
        "stations_worked": "Stații Lucrate",
        "total_score": "Scor Total",
        "validation_result": "Rezultat Validare",
        "date_label": "Dată:",
        "time_label": "Oră:",
        "enable_manual": "Manual",
        "confirm_delete": "Confirmare Ștergere",
        "confirm_delete_text": "Sigur ștergeți QSO-ul selectat?",
        "backup_success": "Backup creat cu succes!",
        "backup_error": "Eroare la backup!",
        "exit_confirm": "Salvați modificările?",
        "help": "Ajutor",
        "about": "Despre",
        "save": "Salvează",
        "close": "Închide",
        "credits": "Dezvoltat de:\nArdei Constantin-Cătălin (YO8ACR)\n\nEmail: yo8acr@gmail.com",
        "usage": "1. Introduceți Indicativul, Banda și Modul.\n2. Apăsați LOG sau ENTER.\n3. Click Dreapta pentru editare/ștergere.\n4. Validați log-ul înainte de export.\n5. Faceți Backup periodic!",
        "edit_qso": "Editează QSO",
        "delete_qso": "Șterge QSO",
        "data": "Data",
        "ora": "Ora",
        "select_format": "Selectează formatul:",
        "cancel": "Anulează",
        "export_success": "Export reușit!",
        "error": "Eroare",
        "settings_saved": "Setări salvate!",
        "locator": "Locator:",
        "address": "Adresă:",
        "font_size": "Mărime Font:",
        "station_info": "Info Stație:"
    },
    "en": {
        "app_title": "YO Log PRO v13.0 - Multi-Contest",
        "call": "Callsign",
        "band": "Band",
        "mode": "Mode",
        "rst_s": "RST S",
        "rst_r": "RST R",
        "note": "Note/Locator",
        "log": "LOG",
        "update": "UPDATE",
        "search": "🔍 Search",
        "reset": "Reset",
        "settings": "Settings",
        "stats": "Statistics",
        "validate": "Validate",
        "export": "Export",
        "delete": "Delete",
        "backup": "Backup",
        "online": "Online",
        "offline": "Manual",
        "category": "Category",
        "county": "County",
        "required_stations": "Required Stations",
        "stations_worked": "Stations Worked",
        "total_score": "Total Score",
        "validation_result": "Validation Result",
        "date_label": "Date:",
        "time_label": "Time:",
        "enable_manual": "Manual",
        "confirm_delete": "Confirm Delete",
        "confirm_delete_text": "Delete selected QSO?",
        "backup_success": "Backup created!",
        "backup_error": "Backup error!",
        "exit_confirm": "Save changes?",
        "help": "Help",
        "about": "About",
        "save": "Save",
        "close": "Close",
        "credits": "Developed by:\nArdei Constantin-Cătălin (YO8ACR)\n\nEmail: yo8acr@gmail.com",
        "usage": "1. Enter Callsign, Band and Mode.\n2. Press LOG or ENTER.\n3. Right Click to edit/delete.\n4. Validate before export.\n5. Backup regularly!",
        "edit_qso": "Edit QSO",
        "delete_qso": "Delete QSO",
        "data": "Date",
        "ora": "Time",
        "select_format": "Select format:",
        "cancel": "Cancel",
        "export_success": "Export successful!",
        "error": "Error",
        "settings_saved": "Settings saved!",
        "locator": "Locator:",
        "address": "Address:",
        "font_size": "Font Size:",
        "station_info": "Station Info:"
    }
}

DEFAULT_CONTESTS = {
    "maraton": {
        "name_ro": "Maraton Ion Creangă",
        "name_en": "Marathon Ion Creangă",
        "categories": ["A. Seniori YO", "B. YL", "C. Juniori YO", "D. Club", "E. DX", "F. Receptori"],
        "required_stations": ["YP8IC", "YR8TGN"],
        "special_scoring": {"YP8IC": 20, "YR8TGN": 20, "YP8KZG": 5, "YO8RRC": 5, "YO8K": 5, "YO8ACR": 5},
        "counties_for_ic": ["NT", "IS"],
        "min_qso_diploma": 100,
        "scoring_mode": "maraton"
    },
    "stafeta": {
        "name_ro": "Cupa Moldovei (Stafeta)",
        "name_en": "Moldova Cup (Relay)",
        "categories": ["A. Echipe Seniori", "B. Echipe Juniori", "C. Echipe Mixte"],
        "min_qso": 50,
        "scoring_mode": "standard"
    },
    "yo-dx": {
        "name_ro": "YO-DX-HF",
        "name_en": "YO-DX-HF",
        "categories": ["A. Single-Op High", "B. Single-Op Low", "C. Multi-Op"],
        "scoring_mode": "standard"
    },
    "log_simplu": {
        "name_ro": "Log Simplu",
        "name_en": "Simple Log",
        "categories": ["A. Individual"],
        "scoring_mode": "none"
    }
}

DEFAULT_CONFIG = {
    "call": "YO8ACR",
    "loc": "KN37",
    "jud": "NT",
    "addr": "",
    "cat": 0,
    "fs": 12,
    "contest": "maraton",
    "county": "NT",
    "lang": "ro",
    "manual_datetime": False
}

THEME = {
    "bg": "#1E1E1E",
    "fg": "#E0E0E0",
    "accent": "#007ACC",
    "entry_bg": "#2D2D2D",
    "header_bg": "#252526",
    "btn_bg": "#3C3C3C",
    "btn_fg": "#FFFFFF",
    "led_on": "#4CAF50",
    "led_off": "#F44336",
    "warning": "#FF9800",
    "success": "#4CAF50",
    "error": "#F44336"
}


# =============================================================================
# DATA MANAGER
# =============================================================================

class DataManager:
    """Handles all data persistence operations"""
    
    @staticmethod
    def get_file_path(filename):
        """Get full path to data file"""
        return os.path.join(get_data_dir(), filename)
    
    @staticmethod
    def save_json(filename, data):
        """Save data to JSON file with atomic write"""
        filepath = DataManager.get_file_path(filename)
        temp_path = filepath + ".tmp"
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            if os.path.exists(filepath):
                os.remove(filepath)
            os.rename(temp_path, filepath)
            return True
        except Exception as e:
            print(f"Save error: {e}")
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
            return False
    
    @staticmethod
    def load_json(filename, default=None):
        """Load data from JSON file"""
        filepath = DataManager.get_file_path(filename)
        
        if not os.path.exists(filepath):
            if default is not None:
                DataManager.save_json(filename, default)
            return default if default is not None else {}
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Load error: {e}")
            return default if default is not None else {}
    
    @staticmethod
    def create_backup(log_data):
        """Create timestamped backup of log"""
        try:
            backup_dir = os.path.join(get_data_dir(), "backups")
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_dir, f"log_backup_{timestamp}.json")
            
            with open(backup_file, "w", encoding="utf-8") as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
            
            # Keep only last 50 backups
            backups = sorted(Path(backup_dir).glob("log_backup_*.json"))
            while len(backups) > 50:
                backups[0].unlink()
                backups.pop(0)
            
            return True
        except Exception as e:
            print(f"Backup error: {e}")
            return False


# =============================================================================
# LANGUAGE MANAGER
# =============================================================================

class Lang:
    """Simple language manager"""
    
    _current = "ro"
    
    @classmethod
    def set(cls, lang):
        if lang in TRANSLATIONS:
            cls._current = lang
    
    @classmethod
    def get(cls):
        return cls._current
    
    @classmethod
    def t(cls, key):
        """Get translation for key"""
        return TRANSLATIONS.get(cls._current, {}).get(key, key)


# =============================================================================
# SCORING ENGINE
# =============================================================================

class ScoringEngine:
    """Calculates scores based on contest rules"""
    
    @staticmethod
    def calculate_qso_score(call, contest_key, contests, user_county="NT"):
        """Calculate score for a single QSO"""
        if contest_key not in contests:
            return 1
        
        rules = contests[contest_key]
        scoring_mode = rules.get("scoring_mode", "standard")
        
        if scoring_mode == "maraton":
            call_upper = call.upper()
            
            # Check special scoring first
            special = rules.get("special_scoring", {})
            if call_upper in special:
                return special[call_upper]
            
            # Check /IC suffix for county-based scoring
            if "/IC" in call_upper:
                if user_county in rules.get("counties_for_ic", []):
                    # Check if it's a club station
                    club_prefixes = ["YO8KZG", "YO8RRC", "YO8K", "YO8ACR"]
                    for prefix in club_prefixes:
                        if call_upper.startswith(prefix):
                            return 10
                    return 5
            
            return 1
        
        return 1
    
    @staticmethod
    def validate_log(log_data, contest_key, contests, user_config):
        """Validate log against contest rules"""
        if not log_data:
            return False, "Log-ul este gol", 0
        
        if contest_key not in contests:
            return True, f"Log valid: {len(log_data)} QSO-uri", len(log_data)
        
        rules = contests[contest_key]
        
        # Check required stations for Maraton
        if contest_key == "maraton":
            required = rules.get("required_stations", [])
            calls_in_log = {qso.get("c", "").upper() for qso in log_data}
            
            missing = [s for s in required if s not in calls_in_log]
            if missing:
                return False, f"Lipsesc stațiile obligatorii: {', '.join(missing)}", 0
            
            min_qso = rules.get("min_qso_diploma", 100)
            if len(log_data) < min_qso:
                return False, f"Minim {min_qso} QSO-uri necesare, aveți {len(log_data)}", 0
        
        # Check minimum QSOs for Stafeta
        if contest_key == "stafeta":
            min_qso = rules.get("min_qso", 50)
            if len(log_data) < min_qso:
                return False, f"Minim {min_qso} QSO-uri necesare, aveți {len(log_data)}", 0
        
        # Calculate total score
        user_county = user_config.get("county", "NT")
        total_score = sum(
            ScoringEngine.calculate_qso_score(qso.get("c", ""), contest_key, contests, user_county)
            for qso in log_data
        )
        
        return True, f"Log valid! Scor: {total_score}", total_score


# =============================================================================
# MAIN APPLICATION
# =============================================================================

class RadioLogApp(tk.Tk):
    """Main application class"""
    
    def __init__(self):
        super().__init__()
        
        # Load data
        self.config_data = DataManager.load_json("config.json", DEFAULT_CONFIG.copy())
        self.log_data = DataManager.load_json("log.json", [])
        self.contests = DataManager.load_json("contests.json", DEFAULT_CONTESTS.copy())
        
        # Set language
        Lang.set(self.config_data.get("lang", "ro"))
        
        # App state
        self.edit_index = None
        self.entries = {}
        
        # Setup window
        self.setup_window()
        self.setup_styles()
        self.create_menu()
        self.create_ui()
        self.create_context_menu()
        self.refresh_log()
        
        # Bindings
        self.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.bind('<Return>', self.on_enter_pressed)
    
    def setup_window(self):
        """Configure main window"""
        self.title(Lang.t("app_title"))
        self.configure(bg=THEME["bg"])
        
        # Window size and position
        width, height = 1100, 720
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.minsize(900, 600)
    
    def setup_styles(self):
        """Configure ttk styles"""
        self.font_size = int(self.config_data.get("fs", 12))
        self.font_main = ("Consolas", self.font_size)
        self.font_bold = ("Consolas", self.font_size, "bold")
        
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("Treeview",
                       background=THEME["entry_bg"],
                       foreground=THEME["fg"],
                       fieldbackground=THEME["entry_bg"],
                       font=self.font_main)
        
        style.configure("Treeview.Heading",
                       background=THEME["header_bg"],
                       foreground=THEME["fg"],
                       font=self.font_bold)
        
        style.map("Treeview", background=[("selected", THEME["accent"])])
    
    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=Lang.t("help"), menu=help_menu)
        help_menu.add_command(label=Lang.t("about"), command=self.show_about)
        help_menu.add_separator()
        help_menu.add_command(label="Exit", command=self.on_exit)
    
    def create_context_menu(self):
        """Create right-click context menu"""
        self.ctx_menu = Menu(self, tearoff=0)
        self.ctx_menu.add_command(label=Lang.t("edit_qso"), command=self.edit_selected)
        self.ctx_menu.add_separator()
        self.ctx_menu.add_command(label=Lang.t("delete_qso"), command=self.delete_selected)
    
    def create_ui(self):
        """Create all UI elements"""
        self.create_header()
        self.create_input_area()
        self.create_log_view()
        self.create_button_bar()
    
    def create_header(self):
        """Create header with status and controls"""
        header = tk.Frame(self, bg=THEME["header_bg"], pady=8)
        header.pack(fill="x")
        
        # Left side - Status
        left_frame = tk.Frame(header, bg=THEME["header_bg"])
        left_frame.pack(side="left", padx=15)
        
        # LED indicator
        self.led_canvas = tk.Canvas(left_frame, width=18, height=18, 
                                    bg=THEME["header_bg"], highlightthickness=0)
        self.led = self.led_canvas.create_oval(2, 2, 16, 16, 
                                               fill=THEME["led_on"], outline="")
        self.led_canvas.pack(side="left", padx=(0, 8))
        
        self.status_label = tk.Label(left_frame, text=Lang.t("online"),
                                     bg=THEME["header_bg"], fg=THEME["led_on"],
                                     font=self.font_main)
        self.status_label.pack(side="left")
        
        # Info bar
        self.info_label = tk.Label(left_frame, text="", bg=THEME["header_bg"],
                                   fg=THEME["fg"], font=self.font_main)
        self.info_label.pack(side="left", padx=20)
        self.update_info_bar()
        
        # Right side - Controls
        right_frame = tk.Frame(header, bg=THEME["header_bg"])
        right_frame.pack(side="right", padx=15)
        
        # Language selector
        self.lang_var = tk.StringVar(value=self.config_data.get("lang", "ro"))
        lang_combo = ttk.Combobox(right_frame, textvariable=self.lang_var,
                                  values=["ro", "en"], state="readonly", width=5)
        lang_combo.pack(side="left", padx=5)
        lang_combo.bind("<<ComboboxSelected>>", self.on_language_change)
        
        # Contest selector
        contest_names = list(self.contests.keys())
        self.contest_var = tk.StringVar(value=self.config_data.get("contest", "maraton"))
        contest_combo = ttk.Combobox(right_frame, textvariable=self.contest_var,
                                     values=contest_names, state="readonly", width=15)
        contest_combo.pack(side="left", padx=5)
        contest_combo.bind("<<ComboboxSelected>>", self.on_contest_change)
    
    def create_input_area(self):
        """Create input fields area"""
        input_frame = tk.Frame(self, bg=THEME["bg"], pady=15)
        input_frame.pack(fill="x", padx=15)
        
        # Row 1: Main input fields
        row1 = tk.Frame(input_frame, bg=THEME["bg"])
        row1.pack(fill="x")
        
        # Callsign (larger)
        call_frame = tk.Frame(row1, bg=THEME["bg"])
        call_frame.pack(side="left", padx=5)
        tk.Label(call_frame, text=Lang.t("call"), bg=THEME["bg"], 
                fg=THEME["fg"], font=self.font_bold).pack()
        self.entries["call"] = tk.Entry(call_frame, width=20, bg=THEME["entry_bg"],
                                        fg=THEME["fg"], font=self.font_bold,
                                        insertbackground=THEME["fg"], justify="center")
        self.entries["call"].pack(ipady=5)
        
        # Other fields
        fields = [
            ("band", Lang.t("band"), 8, BANDS, "40m"),
            ("mode", Lang.t("mode"), 8, MODES, "SSB"),
            ("rst_s", Lang.t("rst_s"), 6, None, "59"),
            ("rst_r", Lang.t("rst_r"), 6, None, "59"),
            ("note", Lang.t("note"), 15, None, ""),
        ]
        
        for key, label, width, values, default in fields:
            frame = tk.Frame(row1, bg=THEME["bg"])
            frame.pack(side="left", padx=5)
            tk.Label(frame, text=label, bg=THEME["bg"], 
                    fg=THEME["fg"], font=self.font_main).pack()
            
            if values:
                entry = ttk.Combobox(frame, values=values, width=width,
                                    state="readonly", font=self.font_main)
                entry.set(default)
            else:
                entry = tk.Entry(frame, width=width, bg=THEME["entry_bg"],
                               fg=THEME["fg"], font=self.font_main,
                               insertbackground=THEME["fg"], justify="center")
                if default:
                    entry.insert(0, default)
            
            entry.pack()
            self.entries[key] = entry
        
        # Manual datetime checkbox
        dt_frame = tk.Frame(row1, bg=THEME["bg"])
        dt_frame.pack(side="left", padx=15)
        
        self.manual_dt_var = tk.BooleanVar(value=self.config_data.get("manual_datetime", False))
        chk = tk.Checkbutton(dt_frame, text=Lang.t("enable_manual"),
                            variable=self.manual_dt_var, bg=THEME["bg"],
                            fg=THEME["fg"], selectcolor=THEME["entry_bg"],
                            activebackground=THEME["bg"], command=self.toggle_manual_datetime)
        chk.pack()
        
        # Action buttons
        btn_frame = tk.Frame(row1, bg=THEME["bg"])
        btn_frame.pack(side="left", padx=10)
        
        self.log_btn = tk.Button(btn_frame, text=Lang.t("log"), command=self.add_qso,
                                bg=THEME["accent"], fg="white", font=self.font_bold,
                                width=12, height=2, cursor="hand2")
        self.log_btn.pack(pady=2)
        
        tk.Button(btn_frame, text=Lang.t("reset"), command=self.clear_inputs,
                 bg=THEME["btn_bg"], fg=THEME["btn_fg"], font=self.font_main,
                 width=12, cursor="hand2").pack(pady=2)
        
        # Row 2: Manual date/time inputs
        row2 = tk.Frame(input_frame, bg=THEME["bg"])
        row2.pack(fill="x", pady=(10, 0))
        
        tk.Label(row2, text=Lang.t("date_label"), bg=THEME["bg"],
                fg=THEME["fg"], font=self.font_main).pack(side="left", padx=5)
        
        self.entries["date"] = tk.Entry(row2, width=12, bg=THEME["entry_bg"],
                                       fg=THEME["fg"], font=self.font_main,
                                       justify="center", state="disabled")
        self.entries["date"].pack(side="left", padx=5)
        
        tk.Label(row2, text=Lang.t("time_label"), bg=THEME["bg"],
                fg=THEME["fg"], font=self.font_main).pack(side="left", padx=5)
        
        self.entries["time"] = tk.Entry(row2, width=10, bg=THEME["entry_bg"],
                                       fg=THEME["fg"], font=self.font_main,
                                       justify="center", state="disabled")
        self.entries["time"].pack(side="left", padx=5)
        
        # Initialize date/time
        now = datetime.datetime.now()
        self.entries["date"].config(state="normal")
        self.entries["date"].insert(0, now.strftime("%Y-%m-%d"))
        self.entries["date"].config(state="disabled")
        
        self.entries["time"].config(state="normal")
        self.entries["time"].insert(0, now.strftime("%H:%M"))
        self.entries["time"].config(state="disabled")
        
        # Row 3: Contest-specific controls
        self.contest_controls = tk.Frame(input_frame, bg=THEME["bg"])
        self.contest_controls.pack(fill="x", pady=(10, 0))
        self.update_contest_controls()
    
    def create_log_view(self):
        """Create log treeview"""
        tree_frame = tk.Frame(self, bg=THEME["bg"])
        tree_frame.pack(fill="both", expand=True, padx=15, pady=5)
        
        # Columns
        columns = ("call", "band", "mode", "rst_s", "rst_r", "note", "date", "time")
        headers = [Lang.t("call"), Lang.t("band"), Lang.t("mode"),
                  Lang.t("rst_s"), Lang.t("rst_r"), Lang.t("note"),
                  Lang.t("data"), Lang.t("ora")]
        widths = [150, 70, 70, 60, 60, 180, 100, 80]
        
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                                selectmode="browse")
        
        for col, header, width in zip(columns, headers, widths):
            self.tree.heading(col, text=header)
            self.tree.column(col, width=width, anchor="center")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bindings
        self.tree.bind("<Double-1>", self.on_tree_double_click)
        self.tree.bind("<Button-3>", self.on_tree_right_click)
    
    def create_button_bar(self):
        """Create bottom button bar"""
        btn_bar = tk.Frame(self, bg=THEME["bg"], pady=10)
        btn_bar.pack(fill="x", padx=15)
        
        buttons = [
            (Lang.t("settings"), self.show_settings, THEME["warning"]),
            (Lang.t("stats"), self.show_stats, "#2196F3"),
            (Lang.t("validate"), self.validate_log, THEME["success"]),
            (Lang.t("export"), self.show_export, "#9C27B0"),
            (Lang.t("delete"), self.delete_selected, THEME["error"]),
            (Lang.t("backup"), self.create_backup, "#607D8B"),
        ]
        
        for text, command, color in buttons:
            tk.Button(btn_bar, text=text, command=command, bg=color, fg="white",
                     font=self.font_main, width=14, cursor="hand2").pack(side="left", padx=5)
    
    # =========================================================================
    # UI UPDATE METHODS
    # =========================================================================
    
    def update_info_bar(self):
        """Update the info bar text"""
        call = self.config_data.get("call", "NOCALL")
        contest_key = self.config_data.get("contest", "maraton")
        
        # Get contest name safely
        contest = self.contests.get(contest_key, {})
        lang_key = "name_" + Lang.get()
        contest_name = contest.get(lang_key, contest.get("name_ro", contest_key))
        
        # Get category safely
        cat_idx = self.config_data.get("cat", 0)
        categories = contest.get("categories", ["A"])
        if isinstance(cat_idx, int) and 0 <= cat_idx < len(categories):
            category = categories[cat_idx]
        else:
            category = categories[0] if categories else "A"
        
        qso_count = len(self.log_data)
        
        info_text = f"{call} | {contest_name} | {category} | QSO: {qso_count}"
        self.info_label.config(text=info_text)
    
    def update_contest_controls(self):
        """Update contest-specific controls"""
        for widget in self.contest_controls.winfo_children():
            widget.destroy()
        
        contest_key = self.config_data.get("contest", "maraton")
        contest = self.contests.get(contest_key, {})
        
        if not contest:
            return
        
        # Category selector
        tk.Label(self.contest_controls, text=Lang.t("category"),
                bg=THEME["bg"], fg=THEME["fg"], font=self.font_main).pack(side="left", padx=5)
        
        categories = contest.get("categories", ["A"])
        self.cat_var = tk.StringVar()
        
        cat_idx = self.config_data.get("cat", 0)
        if isinstance(cat_idx, int) and 0 <= cat_idx < len(categories):
            self.cat_var.set(categories[cat_idx])
        else:
            self.cat_var.set(categories[0] if categories else "A")
        
        cat_combo = ttk.Combobox(self.contest_controls, textvariable=self.cat_var,
                                values=categories, state="readonly", width=20)
        cat_combo.pack(side="left", padx=5)
        
        # County selector for Maraton
        if contest_key == "maraton":
            tk.Label(self.contest_controls, text=Lang.t("county"),
                    bg=THEME["bg"], fg=THEME["fg"], font=self.font_main).pack(side="left", padx=(20, 5))
            
            self.county_var = tk.StringVar(value=self.config_data.get("county", "NT"))
            county_combo = ttk.Combobox(self.contest_controls, textvariable=self.county_var,
                                       values=["NT", "IS"], state="readonly", width=8)
            county_combo.pack(side="left", padx=5)
        
        # Save button
        tk.Button(self.contest_controls, text="💾 " + Lang.t("save"),
                 command=self.save_contest_settings, bg=THEME["accent"],
                 fg="white", font=self.font_main, cursor="hand2").pack(side="left", padx=10)
    
    def toggle_manual_datetime(self):
        """Toggle manual date/time entry"""
        is_manual = self.manual_dt_var.get()
        state = "normal" if is_manual else "disabled"
        
        self.entries["date"].config(state=state)
        self.entries["time"].config(state=state)
        
        # Update LED
        led_color = THEME["led_off"] if is_manual else THEME["led_on"]
        status_text = Lang.t("offline") if is_manual else Lang.t("online")
        
        self.led_canvas.itemconfig(self.led, fill=led_color)
        self.status_label.config(text=status_text, fg=led_color)
        
        self.config_data["manual_datetime"] = is_manual
        DataManager.save_json("config.json", self.config_data)
    
    def refresh_log(self):
        """Refresh the log treeview"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        contest_key = self.config_data.get("contest", "maraton")
        user_county = self.config_data.get("county", "NT")
        
        # Add items
        for i, qso in enumerate(self.log_data):
            call = qso.get("c", "")
            band = qso.get("b", "")
            mode = qso.get("m", "")
            rst_s = qso.get("s", "59")
            rst_r = qso.get("r", "59")
            note = qso.get("n", "")
            date = qso.get("d", "")
            time = qso.get("t", "")
            
            # Add score to note for Maraton
            if contest_key == "maraton":
                score = ScoringEngine.calculate_qso_score(call, contest_key, 
                                                          self.contests, user_county)
                note = f"{note} ({score}p)" if note else f"({score}p)"
            
            self.tree.insert("", "end", iid=str(i),
                           values=(call, band, mode, rst_s, rst_r, note, date, time))
        
        self.update_info_bar()
    
    # =========================================================================
    # QSO OPERATIONS
    # =========================================================================
    
    def get_datetime(self):
        """Get current date and time"""
        if self.manual_dt_var.get():
            date_str = self.entries["date"].get().strip()
            time_str = self.entries["time"].get().strip()
            
            # Validate format
            try:
                datetime.datetime.strptime(date_str, "%Y-%m-%d")
                datetime.datetime.strptime(time_str, "%H:%M")
                return date_str, time_str
            except ValueError:
                messagebox.showerror(Lang.t("error"), 
                                    "Format invalid! Use YYYY-MM-DD and HH:MM")
                now = datetime.datetime.utcnow()
                return now.strftime("%Y-%m-%d"), now.strftime("%H:%M")
        else:
            now = datetime.datetime.utcnow()
            return now.strftime("%Y-%m-%d"), now.strftime("%H:%M")
    
    def add_qso(self):
        """Add or update QSO"""
        call = self.entries["call"].get().upper().strip()
        
        if not call:
            self.entries["call"].focus()
            return
        
        date_str, time_str = self.get_datetime()
        
        qso = {
            "c": call,
            "b": self.entries["band"].get(),
            "m": self.entries["mode"].get(),
            "s": self.entries["rst_s"].get() or "59",
            "r": self.entries["rst_r"].get() or "59",
            "n": self.entries["note"].get(),
            "d": date_str,
            "t": time_str
        }
        
        if self.edit_index is not None:
            # Update existing QSO
            self.log_data[self.edit_index] = qso
            self.edit_index = None
            self.log_btn.config(text=Lang.t("log"), bg=THEME["accent"])
        else:
            # Add new QSO at beginning
            self.log_data.insert(0, qso)
        
        self.clear_inputs()
        self.refresh_log()
        DataManager.save_json("log.json", self.log_data)
    
    def clear_inputs(self):
        """Clear input fields"""
        self.entries["call"].delete(0, "end")
        self.entries["note"].delete(0, "end")
        self.entries["call"].focus()
        
        # Reset edit state
        if self.edit_index is not None:
            self.edit_index = None
            self.log_btn.config(text=Lang.t("log"), bg=THEME["accent"])
    
    def edit_selected(self):
        """Edit selected QSO"""
        selection = self.tree.selection()
        if not selection:
            return
        
        self.edit_index = int(selection[0])
        qso = self.log_data[self.edit_index]
        
        # Fill entries
        self.entries["call"].delete(0, "end")
        self.entries["call"].insert(0, qso.get("c", ""))
        
        self.entries["band"].set(qso.get("b", "40m"))
        self.entries["mode"].set(qso.get("m", "SSB"))
        
        self.entries["rst_s"].delete(0, "end")
        self.entries["rst_s"].insert(0, qso.get("s", "59"))
        
        self.entries["rst_r"].delete(0, "end")
        self.entries["rst_r"].insert(0, qso.get("r", "59"))
        
        self.entries["note"].delete(0, "end")
        self.entries["note"].insert(0, qso.get("n", ""))
        
        # Date/time
        self.entries["date"].config(state="normal")
        self.entries["date"].delete(0, "end")
        self.entries["date"].insert(0, qso.get("d", ""))
        if not self.manual_dt_var.get():
            self.entries["date"].config(state="disabled")
        
        self.entries["time"].config(state="normal")
        self.entries["time"].delete(0, "end")
        self.entries["time"].insert(0, qso.get("t", ""))
        if not self.manual_dt_var.get():
            self.entries["time"].config(state="disabled")
        
        # Update button
        self.log_btn.config(text=Lang.t("update"), bg=THEME["warning"])
    
    def delete_selected(self):
        """Delete selected QSO"""
        selection = self.tree.selection()
        if not selection:
            return
        
        if messagebox.askyesno(Lang.t("confirm_delete"), Lang.t("confirm_delete_text")):
            indices = sorted([int(x) for x in selection], reverse=True)
            for idx in indices:
                self.log_data.pop(idx)
            
            self.refresh_log()
            DataManager.save_json("log.json", self.log_data)
    
    # =========================================================================
    # EVENT HANDLERS
    # =========================================================================
    
    def on_enter_pressed(self, event):
        """Handle Enter key press"""
        if isinstance(self.focus_get(), tk.Entry):
            self.add_qso()
            return "break"
    
    def on_tree_double_click(self, event):
        """Handle double-click on tree"""
        self.edit_selected()
    
    def on_tree_right_click(self, event):
        """Handle right-click on tree"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.ctx_menu.post(event.x_root, event.y_root)
    
    def on_language_change(self, event):
        """Handle language change"""
        Lang.set(self.lang_var.get())
        self.config_data["lang"] = self.lang_var.get()
        DataManager.save_json("config.json", self.config_data)
        
        # Rebuild UI
        for widget in self.winfo_children():
            widget.destroy()
        
        self.create_menu()
        self.create_ui()
        self.create_context_menu()
        self.refresh_log()
    
    def on_contest_change(self, event):
        """Handle contest change"""
        self.config_data["contest"] = self.contest_var.get()
        self.config_data["cat"] = 0  # Reset category
        DataManager.save_json("config.json", self.config_data)
        
        self.update_contest_controls()
        self.refresh_log()
    
    def save_contest_settings(self):
        """Save contest-specific settings"""
        contest_key = self.config_data.get("contest", "maraton")
        contest = self.contests.get(contest_key, {})
        categories = contest.get("categories", [])
        
        # Find category index
        selected_cat = self.cat_var.get()
        try:
            cat_idx = categories.index(selected_cat)
        except ValueError:
            cat_idx = 0
        
        self.config_data["cat"] = cat_idx
        
        # Save county for Maraton
        if contest_key == "maraton" and hasattr(self, 'county_var'):
            self.config_data["county"] = self.county_var.get()
        
        DataManager.save_json("config.json", self.config_data)
        self.update_info_bar()
        messagebox.showinfo("OK", Lang.t("settings_saved"))
    
    # =========================================================================
    # DIALOGS
    # =========================================================================
    
    def show_about(self):
        """Show about dialog"""
        dialog = tk.Toplevel(self)
        dialog.title(Lang.t("about"))
        dialog.geometry("450x300")
        dialog.resizable(False, False)
        dialog.configure(bg=THEME["bg"])
        dialog.transient(self)
        dialog.grab_set()
        
        # Credits
        tk.Label(dialog, text="YO Log PRO v13.0", bg=THEME["bg"],
                fg=THEME["accent"], font=("Consolas", 16, "bold")).pack(pady=20)
        
        tk.Label(dialog, text=Lang.t("credits"), bg=THEME["bg"],
                fg=THEME["fg"], font=self.font_main, justify="center").pack(pady=10)
        
        tk.Label(dialog, text=Lang.t("usage"), bg=THEME["bg"],
                fg=THEME["fg"], font=("Consolas", 10), justify="left").pack(pady=10, padx=20)
        
        tk.Button(dialog, text=Lang.t("close"), command=dialog.destroy,
                 bg=THEME["accent"], fg="white", width=15).pack(pady=15)
    
    def show_settings(self):
        """Show settings dialog"""
        dialog = tk.Toplevel(self)
        dialog.title(Lang.t("settings"))
        dialog.geometry("400x350")
        dialog.resizable(False, False)
        dialog.configure(bg=THEME["bg"])
        dialog.transient(self)
        dialog.grab_set()
        
        tk.Label(dialog, text=Lang.t("station_info"), bg=THEME["bg"],
                fg=THEME["accent"], font=self.font_bold).pack(pady=10, anchor="w", padx=20)
        
        # Callsign
        tk.Label(dialog, text=Lang.t("call") + ":", bg=THEME["bg"],
                fg=THEME["fg"]).pack(anchor="w", padx=20)
        call_entry = tk.Entry(dialog, bg=THEME["entry_bg"], fg=THEME["fg"],
                             font=self.font_main, width=40)
        call_entry.insert(0, self.config_data.get("call", ""))
        call_entry.pack(pady=2, padx=20, fill="x")
        
        # Locator
        tk.Label(dialog, text=Lang.t("locator"), bg=THEME["bg"],
                fg=THEME["fg"]).pack(anchor="w", padx=20)
        loc_entry = tk.Entry(dialog, bg=THEME["entry_bg"], fg=THEME["fg"],
                            font=self.font_main, width=40)
        loc_entry.insert(0, self.config_data.get("loc", ""))
        loc_entry.pack(pady=2, padx=20, fill="x")
        
        # County
        tk.Label(dialog, text=Lang.t("county") + ":", bg=THEME["bg"],
                fg=THEME["fg"]).pack(anchor="w", padx=20)
        jud_entry = tk.Entry(dialog, bg=THEME["entry_bg"], fg=THEME["fg"],
                            font=self.font_main, width=40)
        jud_entry.insert(0, self.config_data.get("jud", ""))
        jud_entry.pack(pady=2, padx=20, fill="x")
        
        # Address
        tk.Label(dialog, text=Lang.t("address"), bg=THEME["bg"],
                fg=THEME["fg"]).pack(anchor="w", padx=20)
        addr_entry = tk.Entry(dialog, bg=THEME["entry_bg"], fg=THEME["fg"],
                             font=self.font_main, width=40)
        addr_entry.insert(0, self.config_data.get("addr", ""))
        addr_entry.pack(pady=2, padx=20, fill="x")
        
        # Font size
        tk.Label(dialog, text=Lang.t("font_size"), bg=THEME["bg"],
                fg=THEME["fg"]).pack(anchor="w", padx=20)
        fs_entry = tk.Entry(dialog, bg=THEME["entry_bg"], fg=THEME["fg"],
                           font=self.font_main, width=10)
        fs_entry.insert(0, str(self.config_data.get("fs", 12)))
        fs_entry.pack(pady=2, padx=20, anchor="w")
        
        def save():
            self.config_data["call"] = call_entry.get().upper().strip()
            self.config_data["loc"] = loc_entry.get().upper().strip()
            self.config_data["jud"] = jud_entry.get().upper().strip()
            self.config_data["addr"] = addr_entry.get().strip()
            
            try:
                self.config_data["fs"] = int(fs_entry.get())
            except ValueError:
                self.config_data["fs"] = 12
            
            DataManager.save_json("config.json", self.config_data)
            self.update_info_bar()
            messagebox.showinfo("OK", Lang.t("settings_saved"))
            dialog.destroy()
        
        tk.Button(dialog, text=Lang.t("save"), command=save,
                 bg=THEME["accent"], fg="white", width=15,
                 font=self.font_main).pack(pady=20)
    
    def show_stats(self):
        """Show statistics dialog"""
        band_count = Counter(qso.get("b", "") for qso in self.log_data)
        mode_count = Counter(qso.get("m", "") for qso in self.log_data)
        
        stats_text = f"Total QSO: {len(self.log_data)}\n\n"
        stats_text += "Per bandă:\n"
        for band in sorted(band_count.keys()):
            stats_text += f"  {band}: {band_count[band]}\n"
        
        stats_text += "\nPer mod:\n"
        for mode in sorted(mode_count.keys()):
            stats_text += f"  {mode}: {mode_count[mode]}\n"
        
        # Contest-specific stats
        contest_key = self.config_data.get("contest", "maraton")
        user_county = self.config_data.get("county", "NT")
        
        if contest_key == "maraton":
            total_score = sum(
                ScoringEngine.calculate_qso_score(qso.get("c", ""), contest_key, 
                                                   self.contests, user_county)
                for qso in self.log_data
            )
            
            calls = {qso.get("c", "").upper() for qso in self.log_data}
            required = self.contests.get("maraton", {}).get("required_stations", [])
            found = [s for s in required if s in calls]
            
            stats_text += f"\n{Lang.t('stations_worked')}: {len(calls)}"
            stats_text += f"\n{Lang.t('required_stations')}: {', '.join(found) if found else 'Niciuna'}"
            stats_text += f"\n\n{Lang.t('total_score')}: {total_score}"
        
        messagebox.showinfo(Lang.t("stats"), stats_text)
    
    def validate_log(self):
        """Validate log against contest rules"""
        contest_key = self.config_data.get("contest", "maraton")
        
        valid, message, score = ScoringEngine.validate_log(
            self.log_data, contest_key, self.contests, self.config_data
        )
        
        if valid:
            min_qso = self.contests.get(contest_key, {}).get("min_qso_diploma", 100)
            diploma = "DA" if len(self.log_data) >= min_qso else "NU"
            
            messagebox.showinfo(Lang.t("validation_result"),
                               f"✓ {message}\n\nEligibil diplomă: {diploma}")
        else:
            messagebox.showwarning(Lang.t("validation_result"), f"✗ {message}")
    
    def show_export(self):
        """Show export dialog"""
        dialog = tk.Toplevel(self)
        dialog.title(Lang.t("export"))
        dialog.geometry("280x220")
        dialog.resizable(False, False)
        dialog.configure(bg=THEME["bg"])
        dialog.transient(self)
        dialog.grab_set()
        
        tk.Label(dialog, text=Lang.t("select_format"), bg=THEME["bg"],
                fg=THEME["fg"], font=self.font_bold).pack(pady=15)
        
        tk.Button(dialog, text="Cabrillo (.log)", 
                 command=lambda: self.export_cabrillo(dialog),
                 bg=THEME["accent"], fg="white", width=20).pack(pady=5)
        
        tk.Button(dialog, text="ADIF (.adi)",
                 command=lambda: self.export_adif(dialog),
                 bg=THEME["accent"], fg="white", width=20).pack(pady=5)
        
        tk.Button(dialog, text="CSV (.csv)",
                 command=lambda: self.export_csv(dialog),
                 bg=THEME["accent"], fg="white", width=20).pack(pady=5)
        
        tk.Button(dialog, text=Lang.t("cancel"), command=dialog.destroy,
                 bg=THEME["btn_bg"], fg="white", width=20).pack(pady=15)
    
    def export_cabrillo(self, parent):
        """Export to Cabrillo format"""
        try:
            contest_key = self.config_data.get("contest", "maraton")
            contest = self.contests.get(contest_key, {})
            contest_name = contest.get("name_" + Lang.get(), contest_key)
            
            lines = [
                "START-OF-LOG: 3.0",
                f"CONTEST: {contest_name}",
                f"CALLSIGN: {self.config_data.get('call', 'NOCALL')}",
                f"LOCATION: {self.config_data.get('loc', '')}",
                "CATEGORY: ALL",
            ]
            
            for qso in self.log_data:
                line = f"QSO: {qso['b']:>5} {qso['m']:<4} {qso['d']} {qso['t']} "
                line += f"{self.config_data.get('call', 'NOCALL'):<13} {qso['s']} "
                line += f"{qso['c']:<13} {qso['r']}"
                lines.append(line)
            
            lines.append("END-OF-LOG:")
            
            filename = f"cabrillo_{contest_key}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.log"
            filepath = os.path.join(get_data_dir(), filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            
            messagebox.showinfo(Lang.t("export_success"), f"Salvat: {filename}")
            parent.destroy()
        except Exception as e:
            messagebox.showerror(Lang.t("error"), str(e))
    
    def export_adif(self, parent):
        """Export to ADIF format"""
        try:
            lines = ["<ADIF_VER:5>3.1.0", "<EOH>", ""]
            
            for qso in self.log_data:
                record = ""
                record += f"<CALL:{len(qso['c'])}>{qso['c']}"
                record += f"<BAND:{len(qso['b'])}>{qso['b']}"
                record += f"<MODE:{len(qso['m'])}>{qso['m']}"
                
                date_clean = qso['d'].replace("-", "")
                record += f"<QSO_DATE:{len(date_clean)}>{date_clean}"
                
                time_clean = qso['t'].replace(":", "") + "00"
                record += f"<TIME_ON:{len(time_clean)}>{time_clean}"
                
                record += f"<RST_SENT:{len(qso['s'])}>{qso['s']}"
                record += f"<RST_RCVD:{len(qso['r'])}>{qso['r']}"
                
                if qso.get('n'):
                    record += f"<COMMENT:{len(qso['n'])}>{qso['n']}"
                
                record += "<EOR>"
                lines.append(record)
            
            filename = f"adif_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.adi"
            filepath = os.path.join(get_data_dir(), filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            
            messagebox.showinfo(Lang.t("export_success"), f"Salvat: {filename}")
            parent.destroy()
        except Exception as e:
            messagebox.showerror(Lang.t("error"), str(e))
    
    def export_csv(self, parent):
        """Export to CSV format"""
        try:
            lines = ["Date,Time,Call,Band,Mode,RST_Sent,RST_Rcvd,Note"]
            
            for qso in self.log_data:
                line = f"{qso['d']},{qso['t']},{qso['c']},{qso['b']},{qso['m']},"
                line += f"{qso['s']},{qso['r']},{qso.get('n', '')}"
                lines.append(line)
            
            filename = f"log_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv"
            filepath = os.path.join(get_data_dir(), filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            
            messagebox.showinfo(Lang.t("export_success"), f"Salvat: {filename}")
            parent.destroy()
        except Exception as e:
            messagebox.showerror(Lang.t("error"), str(e))
    
    def create_backup(self):
        """Create manual backup"""
        if DataManager.create_backup(self.log_data):
            messagebox.showinfo("OK", Lang.t("backup_success"))
        else:
            messagebox.showerror(Lang.t("error"), Lang.t("backup_error"))
    
    def on_exit(self):
        """Handle application exit"""
        if messagebox.askyesno(Lang.t("exit_confirm"), Lang.t("exit_confirm")):
            DataManager.save_json("log.json", self.log_data)
            DataManager.save_json("config.json", self.config_data)
            DataManager.create_backup(self.log_data)
            self.destroy()


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    app = RadioLogApp()
    app.mainloop()
