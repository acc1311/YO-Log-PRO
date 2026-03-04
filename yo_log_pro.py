#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YO Log PRO v14.0 - Multi-Contest Amateur Radio Logger
Developed by: Ardei Constantin-Cătălin (YO8ACR)
Email: yo8acr@gmail.com

Features:
  - Fully configurable contest manager (add/edit/delete)
  - Operating modes: Maraton, Stafeta, Simplu, YO, DX, VHF, UHF, Field Day, Custom
  - Per-contest scoring, categories, required stations
  - Cabrillo / ADIF / CSV export
  - Bilingual RO/EN interface
"""

import os
import sys
import json
import copy
import datetime
from pathlib import Path
from collections import Counter
import tkinter as tk
from tkinter import ttk, messagebox, Menu, simpledialog


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

BANDS_HF = ["160m", "80m", "60m", "40m", "30m", "20m", "17m", "15m", "12m", "10m"]
BANDS_VHF = ["6m", "2m"]
BANDS_UHF = ["70cm", "23cm"]
BANDS_ALL = BANDS_HF + BANDS_VHF + BANDS_UHF

MODES_ALL = ["SSB", "CW", "DIGI", "FT8", "FT4", "RTTY", "AM", "FM", "PSK31", "SSTV", "JT65"]

# Scoring modes available for contests
SCORING_MODES = [
    "none",        # No scoring - simple log
    "per_qso",     # Fixed points per QSO
    "per_band",    # Points vary by band
    "maraton",     # Marathon-style with special stations
    "multiplier",  # QSO points × multipliers (counties, DXCC, etc.)
    "distance",    # Distance-based (VHF/UHF)
    "custom",      # Custom formula
]

# Operating/contest type modes
CONTEST_TYPES = [
    "Simplu",       # Simple logging, no contest
    "Maraton",      # Marathon - endurance, special stations
    "Stafeta",      # Relay - team contest
    "YO",           # YO national contest
    "DX",           # DX contest (international)
    "VHF",          # VHF contest
    "UHF",          # UHF contest
    "Field Day",    # Field Day
    "Sprint",       # Sprint contest
    "QSO Party",    # QSO Party
    "SOTA",         # Summits On The Air
    "POTA",         # Parks On The Air
    "Custom",       # User-defined
]

TRANSLATIONS = {
    "ro": {
        "app_title": "YO Log PRO v14.0 - Multi-Contest",
        "call": "Indicativ",
        "band": "Bandă",
        "mode": "Mod",
        "rst_s": "RST S",
        "rst_r": "RST R",
        "serial_s": "Nr S",
        "serial_r": "Nr R",
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
        "usage": (
            "1. Configurați concursurile din Concursuri → Manager.\n"
            "2. Introduceți Indicativul, Banda și Modul.\n"
            "3. Apăsați LOG sau ENTER.\n"
            "4. Click Dreapta pentru editare/ștergere.\n"
            "5. Validați log-ul înainte de export.\n"
            "6. Faceți Backup periodic!"
        ),
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
        "station_info": "Info Stație:",
        # Contest manager translations
        "contest_manager": "Manager Concursuri",
        "contests_menu": "Concursuri",
        "add_contest": "➕ Adaugă Concurs",
        "edit_contest": "✏️ Editează Concurs",
        "delete_contest": "🗑️ Șterge Concurs",
        "duplicate_contest": "📋 Duplică Concurs",
        "contest_name": "Nume Concurs:",
        "contest_type": "Tip Concurs:",
        "scoring_mode": "Mod Punctare:",
        "categories": "Categorii (una per linie):",
        "allowed_bands": "Benzi Permise:",
        "allowed_modes": "Moduri Permise:",
        "required_stations_cfg": "Stații Obligatorii (una per linie):",
        "special_scoring_cfg": "Punctare Specială (CALL=PUNCTE, una per linie):",
        "points_per_qso": "Puncte per QSO:",
        "min_qso": "Minim QSO:",
        "exchange_sent": "Schimb Trimis:",
        "exchange_rcvd": "Schimb Primit:",
        "use_serial": "Folosește Numere Seriale",
        "use_county": "Folosește Județ",
        "county_list": "Lista Județe (separate prin virgulă):",
        "no_contest_selected": "Niciun concurs selectat!",
        "confirm_delete_contest": "Sigur ștergeți concursul '{}'?",
        "contest_saved": "Concursul a fost salvat!",
        "contest_deleted": "Concursul a fost șters!",
        "contest_exists": "Un concurs cu acest ID există deja!",
        "default_contest_warn": "Nu puteți șterge concursul implicit (Simplu)!",
        "contest_id": "ID Concurs (fără spații):",
        "multipliers": "Multiplicatori:",
        "mult_none": "Fără",
        "mult_county": "Județe",
        "mult_dxcc": "DXCC",
        "mult_band": "Bandă",
        "mult_grid": "Grid Square",
        "band_points": "Puncte per Bandă (BANDĂ=PUNCTE, una per linie):",
        "qso_nr": "Nr.",
        "score_col": "Puncte",
        "import_contest": "📥 Importă",
        "export_contest": "📤 Exportă",
    },
    "en": {
        "app_title": "YO Log PRO v14.0 - Multi-Contest",
        "call": "Callsign",
        "band": "Band",
        "mode": "Mode",
        "rst_s": "RST S",
        "rst_r": "RST R",
        "serial_s": "Nr S",
        "serial_r": "Nr R",
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
        "usage": (
            "1. Configure contests from Contests → Manager.\n"
            "2. Enter Callsign, Band and Mode.\n"
            "3. Press LOG or ENTER.\n"
            "4. Right Click to edit/delete.\n"
            "5. Validate before export.\n"
            "6. Backup regularly!"
        ),
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
        "station_info": "Station Info:",
        # Contest manager translations
        "contest_manager": "Contest Manager",
        "contests_menu": "Contests",
        "add_contest": "➕ Add Contest",
        "edit_contest": "✏️ Edit Contest",
        "delete_contest": "🗑️ Delete Contest",
        "duplicate_contest": "📋 Duplicate Contest",
        "contest_name": "Contest Name:",
        "contest_type": "Contest Type:",
        "scoring_mode": "Scoring Mode:",
        "categories": "Categories (one per line):",
        "allowed_bands": "Allowed Bands:",
        "allowed_modes": "Allowed Modes:",
        "required_stations_cfg": "Required Stations (one per line):",
        "special_scoring_cfg": "Special Scoring (CALL=POINTS, one per line):",
        "points_per_qso": "Points per QSO:",
        "min_qso": "Minimum QSOs:",
        "exchange_sent": "Exchange Sent:",
        "exchange_rcvd": "Exchange Received:",
        "use_serial": "Use Serial Numbers",
        "use_county": "Use County",
        "county_list": "County List (comma separated):",
        "no_contest_selected": "No contest selected!",
        "confirm_delete_contest": "Delete contest '{}'?",
        "contest_saved": "Contest saved!",
        "contest_deleted": "Contest deleted!",
        "contest_exists": "A contest with this ID already exists!",
        "default_contest_warn": "Cannot delete the default contest (Simple)!",
        "contest_id": "Contest ID (no spaces):",
        "multipliers": "Multipliers:",
        "mult_none": "None",
        "mult_county": "Counties",
        "mult_dxcc": "DXCC",
        "mult_band": "Band",
        "mult_grid": "Grid Square",
        "band_points": "Band Points (BAND=POINTS, one per line):",
        "qso_nr": "Nr.",
        "score_col": "Score",
        "import_contest": "📥 Import",
        "export_contest": "📤 Export",
    }
}

# Default contests - templates that come with the app
DEFAULT_CONTESTS = {
    "simplu": {
        "name_ro": "Log Simplu",
        "name_en": "Simple Log",
        "contest_type": "Simplu",
        "categories": ["Individual"],
        "scoring_mode": "none",
        "points_per_qso": 1,
        "min_qso": 0,
        "allowed_bands": BANDS_ALL,
        "allowed_modes": MODES_ALL,
        "required_stations": [],
        "special_scoring": {},
        "use_serial": False,
        "use_county": False,
        "county_list": [],
        "multiplier_type": "none",
        "band_points": {},
        "exchange_fields": [],
        "is_default": True,
    },
    "maraton": {
        "name_ro": "Maraton",
        "name_en": "Marathon",
        "contest_type": "Maraton",
        "categories": [
            "A. Seniori YO",
            "B. YL",
            "C. Juniori YO",
            "D. Club",
            "E. DX",
            "F. Receptori",
        ],
        "scoring_mode": "maraton",
        "points_per_qso": 1,
        "min_qso": 100,
        "allowed_bands": BANDS_HF + BANDS_VHF,
        "allowed_modes": MODES_ALL,
        "required_stations": [],
        "special_scoring": {},
        "use_serial": False,
        "use_county": True,
        "county_list": [
            "AB","AR","AG","BC","BH","BN","BT","BV","BR","BZ","CS","CL",
            "CJ","CT","CV","DB","DJ","GL","GR","GJ","HR","HD","IL","IS",
            "IF","MM","MH","MS","NT","OT","PH","SM","SJ","SB","SV","TR",
            "TM","TL","VS","VL","VN","B",
        ],
        "multiplier_type": "county",
        "band_points": {},
        "exchange_fields": [],
        "is_default": False,
    },
    "stafeta": {
        "name_ro": "Ștafetă",
        "name_en": "Relay",
        "contest_type": "Stafeta",
        "categories": [
            "A. Echipe Seniori",
            "B. Echipe Juniori",
            "C. Echipe Mixte",
        ],
        "scoring_mode": "per_qso",
        "points_per_qso": 1,
        "min_qso": 50,
        "allowed_bands": BANDS_HF,
        "allowed_modes": ["SSB", "CW"],
        "required_stations": [],
        "special_scoring": {},
        "use_serial": True,
        "use_county": True,
        "county_list": [
            "AB","AR","AG","BC","BH","BN","BT","BV","BR","BZ","CS","CL",
            "CJ","CT","CV","DB","DJ","GL","GR","GJ","HR","HD","IL","IS",
            "IF","MM","MH","MS","NT","OT","PH","SM","SJ","SB","SV","TR",
            "TM","TL","VS","VL","VN","B",
        ],
        "multiplier_type": "county",
        "band_points": {},
        "exchange_fields": [],
        "is_default": False,
    },
    "yo-dx-hf": {
        "name_ro": "YO DX HF Contest",
        "name_en": "YO DX HF Contest",
        "contest_type": "DX",
        "categories": [
            "A. Single-Op All Band High",
            "B. Single-Op All Band Low",
            "C. Single-Op Single Band",
            "D. Multi-Op Single TX",
            "E. Multi-Op Multi TX",
        ],
        "scoring_mode": "per_band",
        "points_per_qso": 1,
        "min_qso": 0,
        "allowed_bands": ["160m","80m","40m","20m","15m","10m"],
        "allowed_modes": ["SSB", "CW"],
        "required_stations": [],
        "special_scoring": {},
        "use_serial": True,
        "use_county": True,
        "county_list": [
            "AB","AR","AG","BC","BH","BN","BT","BV","BR","BZ","CS","CL",
            "CJ","CT","CV","DB","DJ","GL","GR","GJ","HR","HD","IL","IS",
            "IF","MM","MH","MS","NT","OT","PH","SM","SJ","SB","SV","TR",
            "TM","TL","VS","VL","VN","B",
        ],
        "multiplier_type": "dxcc",
        "band_points": {
            "160m": 4, "80m": 3, "40m": 2, "20m": 1, "15m": 1, "10m": 2,
        },
        "exchange_fields": [],
        "is_default": False,
    },
    "yo-vhf": {
        "name_ro": "Contest VHF/UHF",
        "name_en": "VHF/UHF Contest",
        "contest_type": "VHF",
        "categories": [
            "A. Single-Op 2m",
            "B. Single-Op 70cm",
            "C. Multi-Band",
        ],
        "scoring_mode": "distance",
        "points_per_qso": 1,
        "min_qso": 0,
        "allowed_bands": ["2m", "70cm", "23cm"],
        "allowed_modes": ["SSB", "CW", "FM"],
        "required_stations": [],
        "special_scoring": {},
        "use_serial": True,
        "use_county": False,
        "county_list": [],
        "multiplier_type": "grid",
        "band_points": {},
        "exchange_fields": [],
        "is_default": False,
    },
    "field-day": {
        "name_ro": "Ziua Câmpului",
        "name_en": "Field Day",
        "contest_type": "Field Day",
        "categories": [
            "A. 1 Operator",
            "B. 2 Operatori",
            "C. Club",
        ],
        "scoring_mode": "per_qso",
        "points_per_qso": 2,
        "min_qso": 0,
        "allowed_bands": BANDS_ALL,
        "allowed_modes": MODES_ALL,
        "required_stations": [],
        "special_scoring": {},
        "use_serial": False,
        "use_county": False,
        "county_list": [],
        "multiplier_type": "none",
        "band_points": {},
        "exchange_fields": [],
        "is_default": False,
    },
    "sprint": {
        "name_ro": "Sprint",
        "name_en": "Sprint",
        "contest_type": "Sprint",
        "categories": [
            "A. Single-Op",
        ],
        "scoring_mode": "per_qso",
        "points_per_qso": 1,
        "min_qso": 0,
        "allowed_bands": BANDS_HF,
        "allowed_modes": ["SSB", "CW"],
        "required_stations": [],
        "special_scoring": {},
        "use_serial": True,
        "use_county": False,
        "county_list": [],
        "multiplier_type": "none",
        "band_points": {},
        "exchange_fields": [],
        "is_default": False,
    },
}

DEFAULT_CONFIG = {
    "call": "YO8ACR",
    "loc": "KN37",
    "jud": "NT",
    "addr": "",
    "cat": 0,
    "fs": 12,
    "contest": "simplu",
    "county": "NT",
    "lang": "ro",
    "manual_datetime": False,
}

THEME = {
    "bg":        "#1E1E1E",
    "fg":        "#E0E0E0",
    "accent":    "#007ACC",
    "entry_bg":  "#2D2D2D",
    "header_bg": "#252526",
    "btn_bg":    "#3C3C3C",
    "btn_fg":    "#FFFFFF",
    "led_on":    "#4CAF50",
    "led_off":   "#F44336",
    "warning":   "#FF9800",
    "success":   "#4CAF50",
    "error":     "#F44336",
}


# =============================================================================
# DATA MANAGER
# =============================================================================

class DataManager:
    """Handles all data persistence operations"""

    @staticmethod
    def get_file_path(filename):
        return os.path.join(get_data_dir(), filename)

    @staticmethod
    def save_json(filename, data):
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
        try:
            backup_dir = os.path.join(get_data_dir(), "backups")
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_dir, f"log_backup_{timestamp}.json")
            with open(backup_file, "w", encoding="utf-8") as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
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
        return TRANSLATIONS.get(cls._current, {}).get(key, key)


# =============================================================================
# SCORING ENGINE
# =============================================================================

class ScoringEngine:
    """Calculates scores based on contest rules"""

    @staticmethod
    def calculate_qso_score(qso, contest_rules, user_config=None):
        """Calculate score for a single QSO based on contest rules"""
        if not contest_rules:
            return 1

        call = qso.get("c", "").upper()
        band = qso.get("b", "")
        mode = qso.get("m", "")
        scoring_mode = contest_rules.get("scoring_mode", "none")

        if scoring_mode == "none":
            return 0

        # Check special scoring first
        special = contest_rules.get("special_scoring", {})
        if call in special:
            try:
                return int(special[call])
            except (ValueError, TypeError):
                pass

        if scoring_mode == "per_qso":
            return contest_rules.get("points_per_qso", 1)

        elif scoring_mode == "per_band":
            band_pts = contest_rules.get("band_points", {})
            if band in band_pts:
                try:
                    return int(band_pts[band])
                except (ValueError, TypeError):
                    pass
            return contest_rules.get("points_per_qso", 1)

        elif scoring_mode == "maraton":
            return contest_rules.get("points_per_qso", 1)

        elif scoring_mode == "multiplier":
            return contest_rules.get("points_per_qso", 1)

        elif scoring_mode == "distance":
            # Distance-based; locator needed for real calc, use 1 as placeholder
            return contest_rules.get("points_per_qso", 1)

        elif scoring_mode == "custom":
            return contest_rules.get("points_per_qso", 1)

        return 1

    @staticmethod
    def count_multipliers(log_data, contest_rules):
        """Count multipliers based on contest rules"""
        mult_type = contest_rules.get("multiplier_type", "none")
        if mult_type == "none":
            return 1

        multipliers = set()

        for qso in log_data:
            call = qso.get("c", "").upper()
            note = qso.get("n", "").upper()
            band = qso.get("b", "")

            if mult_type == "county":
                # Try to extract county from note field
                county_list = contest_rules.get("county_list", [])
                for county in county_list:
                    if county.upper() in note:
                        multipliers.add(county.upper())
                        break

            elif mult_type == "dxcc":
                # Simple prefix extraction for DXCC
                prefix = ""
                for ch in call:
                    if ch.isdigit():
                        prefix += ch
                        break
                    prefix += ch
                if prefix:
                    multipliers.add(prefix)

            elif mult_type == "band":
                multipliers.add(band)

            elif mult_type == "grid":
                # Extract grid from note
                if len(note) >= 4 and note[:2].isalpha() and note[2:4].isdigit():
                    multipliers.add(note[:4])

        return max(1, len(multipliers))

    @staticmethod
    def calculate_total_score(log_data, contest_rules, user_config=None):
        """Calculate total score for the log"""
        if not log_data or not contest_rules:
            return 0, 0, 0  # qso_points, multipliers, total

        scoring_mode = contest_rules.get("scoring_mode", "none")
        if scoring_mode == "none":
            return 0, 0, 0

        qso_points = sum(
            ScoringEngine.calculate_qso_score(qso, contest_rules, user_config)
            for qso in log_data
        )

        multipliers = ScoringEngine.count_multipliers(log_data, contest_rules)

        if contest_rules.get("multiplier_type", "none") != "none":
            total = qso_points * multipliers
        else:
            total = qso_points

        return qso_points, multipliers, total

    @staticmethod
    def validate_log(log_data, contest_rules, user_config=None):
        """Validate log against contest rules"""
        if not log_data:
            return False, "Log-ul este gol / Log is empty", 0

        if not contest_rules:
            return True, f"Log valid: {len(log_data)} QSO", len(log_data)

        scoring_mode = contest_rules.get("scoring_mode", "none")
        messages = []

        # Check required stations
        required = contest_rules.get("required_stations", [])
        if required:
            calls_in_log = {qso.get("c", "").upper() for qso in log_data}
            missing = [s for s in required if s.upper() not in calls_in_log]
            if missing:
                messages.append(f"Lipsesc stații obligatorii: {', '.join(missing)}")

        # Check minimum QSOs
        min_qso = contest_rules.get("min_qso", 0)
        if min_qso > 0 and len(log_data) < min_qso:
            messages.append(f"Minim {min_qso} QSO necesare, aveți {len(log_data)}")

        # Check allowed bands
        allowed_bands = contest_rules.get("allowed_bands", [])
        if allowed_bands:
            for i, qso in enumerate(log_data):
                if qso.get("b", "") not in allowed_bands:
                    messages.append(
                        f"QSO #{i+1} ({qso.get('c','')}) bandă nepermisă: {qso.get('b','')}"
                    )

        # Check allowed modes
        allowed_modes = contest_rules.get("allowed_modes", [])
        if allowed_modes:
            for i, qso in enumerate(log_data):
                if qso.get("m", "") not in allowed_modes:
                    messages.append(
                        f"QSO #{i+1} ({qso.get('c','')}) mod nepermis: {qso.get('m','')}"
                    )

        if messages:
            return False, "\n".join(messages), 0

        # Calculate score
        _, _, total = ScoringEngine.calculate_total_score(
            log_data, contest_rules, user_config
        )

        return True, f"Log valid! Total: {len(log_data)} QSO, Scor: {total}", total


# =============================================================================
# CONTEST EDITOR DIALOG
# =============================================================================

class ContestEditorDialog(tk.Toplevel):
    """Dialog for adding/editing a contest"""

    def __init__(self, parent, contest_id=None, contest_data=None, all_contests=None):
        super().__init__(parent)
        self.parent = parent
        self.result = None
        self.contest_id = contest_id
        self.is_new = contest_id is None
        self.all_contests = all_contests or {}

        if contest_data:
            self.data = copy.deepcopy(contest_data)
        else:
            self.data = {
                "name_ro": "",
                "name_en": "",
                "contest_type": "Simplu",
                "categories": ["Individual"],
                "scoring_mode": "none",
                "points_per_qso": 1,
                "min_qso": 0,
                "allowed_bands": list(BANDS_ALL),
                "allowed_modes": list(MODES_ALL),
                "required_stations": [],
                "special_scoring": {},
                "use_serial": False,
                "use_county": False,
                "county_list": [],
                "multiplier_type": "none",
                "band_points": {},
                "exchange_fields": [],
                "is_default": False,
            }

        title = Lang.t("edit_contest") if not self.is_new else Lang.t("add_contest")
        self.title(title)
        self.geometry("700x850")
        self.configure(bg=THEME["bg"])
        self.transient(parent)
        self.grab_set()

        self.build_ui()
        self.center_window()

    def center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"+{x}+{y}")

    def build_ui(self):
        canvas = tk.Canvas(self, bg=THEME["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas, bg=THEME["bg"])

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        f = self.scroll_frame
        pad = {"padx": 15, "pady": 3}
        entry_opts = {
            "bg": THEME["entry_bg"], "fg": THEME["fg"],
            "font": ("Consolas", 11), "insertbackground": THEME["fg"],
        }
        lbl_opts = {"bg": THEME["bg"], "fg": THEME["fg"], "font": ("Consolas", 11)}

        row = 0

        # --- Contest ID ---
        if self.is_new:
            tk.Label(f, text=Lang.t("contest_id"), **lbl_opts).grid(
                row=row, column=0, sticky="w", **pad)
            self.id_entry = tk.Entry(f, width=30, **entry_opts)
            self.id_entry.grid(row=row, column=1, sticky="w", **pad)
            row += 1
        else:
            tk.Label(f, text=f"ID: {self.contest_id}", **lbl_opts).grid(
                row=row, column=0, columnspan=2, sticky="w", **pad)
            row += 1

        # --- Name RO ---
        tk.Label(f, text=Lang.t("contest_name") + " (RO)", **lbl_opts).grid(
            row=row, column=0, sticky="w", **pad)
        self.name_ro_entry = tk.Entry(f, width=40, **entry_opts)
        self.name_ro_entry.insert(0, self.data.get("name_ro", ""))
        self.name_ro_entry.grid(row=row, column=1, sticky="w", **pad)
        row += 1

        # --- Name EN ---
        tk.Label(f, text=Lang.t("contest_name") + " (EN)", **lbl_opts).grid(
            row=row, column=0, sticky="w", **pad)
        self.name_en_entry = tk.Entry(f, width=40, **entry_opts)
        self.name_en_entry.insert(0, self.data.get("name_en", ""))
        self.name_en_entry.grid(row=row, column=1, sticky="w", **pad)
        row += 1

        # --- Contest Type ---
        tk.Label(f, text=Lang.t("contest_type"), **lbl_opts).grid(
            row=row, column=0, sticky="w", **pad)
        self.type_var = tk.StringVar(value=self.data.get("contest_type", "Simplu"))
        type_combo = ttk.Combobox(f, textvariable=self.type_var,
                                  values=CONTEST_TYPES, state="readonly", width=20)
        type_combo.grid(row=row, column=1, sticky="w", **pad)
        row += 1

        # --- Scoring Mode ---
        tk.Label(f, text=Lang.t("scoring_mode"), **lbl_opts).grid(
            row=row, column=0, sticky="w", **pad)
        self.scoring_var = tk.StringVar(value=self.data.get("scoring_mode", "none"))
        scoring_combo = ttk.Combobox(f, textvariable=self.scoring_var,
                                     values=SCORING_MODES, state="readonly", width=20)
        scoring_combo.grid(row=row, column=1, sticky="w", **pad)
        row += 1

        # --- Points per QSO ---
        tk.Label(f, text=Lang.t("points_per_qso"), **lbl_opts).grid(
            row=row, column=0, sticky="w", **pad)
        self.ppq_entry = tk.Entry(f, width=10, **entry_opts)
        self.ppq_entry.insert(0, str(self.data.get("points_per_qso", 1)))
        self.ppq_entry.grid(row=row, column=1, sticky="w", **pad)
        row += 1

        # --- Min QSO ---
        tk.Label(f, text=Lang.t("min_qso"), **lbl_opts).grid(
            row=row, column=0, sticky="w", **pad)
        self.min_qso_entry = tk.Entry(f, width=10, **entry_opts)
        self.min_qso_entry.insert(0, str(self.data.get("min_qso", 0)))
        self.min_qso_entry.grid(row=row, column=1, sticky="w", **pad)
        row += 1

        # --- Multiplier Type ---
        tk.Label(f, text=Lang.t("multipliers"), **lbl_opts).grid(
            row=row, column=0, sticky="w", **pad)
        mult_options = ["none", "county", "dxcc", "band", "grid"]
        self.mult_var = tk.StringVar(value=self.data.get("multiplier_type", "none"))
        mult_combo = ttk.Combobox(f, textvariable=self.mult_var,
                                  values=mult_options, state="readonly", width=20)
        mult_combo.grid(row=row, column=1, sticky="w", **pad)
        row += 1

        # --- Categories ---
        tk.Label(f, text=Lang.t("categories"), **lbl_opts).grid(
            row=row, column=0, sticky="nw", **pad)
        self.cat_text = tk.Text(f, width=40, height=5, **entry_opts)
        cats = self.data.get("categories", [])
        self.cat_text.insert("1.0", "\n".join(cats))
        self.cat_text.grid(row=row, column=1, sticky="w", **pad)
        row += 1

        # --- Allowed Bands ---
        tk.Label(f, text=Lang.t("allowed_bands"), **lbl_opts).grid(
            row=row, column=0, sticky="nw", **pad)
        self.band_frame = tk.Frame(f, bg=THEME["bg"])
        self.band_frame.grid(row=row, column=1, sticky="w", **pad)
        self.band_vars = {}
        allowed = self.data.get("allowed_bands", BANDS_ALL)
        col_count = 0
        for i, band in enumerate(BANDS_ALL):
            var = tk.BooleanVar(value=band in allowed)
            chk = tk.Checkbutton(self.band_frame, text=band, variable=var,
                                 bg=THEME["bg"], fg=THEME["fg"],
                                 selectcolor=THEME["entry_bg"],
                                 activebackground=THEME["bg"])
            chk.grid(row=i // 6, column=i % 6, sticky="w", padx=2)
            self.band_vars[band] = var
        row += 1

        # --- Allowed Modes ---
        tk.Label(f, text=Lang.t("allowed_modes"), **lbl_opts).grid(
            row=row, column=0, sticky="nw", **pad)
        self.mode_frame = tk.Frame(f, bg=THEME["bg"])
        self.mode_frame.grid(row=row, column=1, sticky="w", **pad)
        self.mode_vars = {}
        allowed_modes = self.data.get("allowed_modes", MODES_ALL)
        for i, mode in enumerate(MODES_ALL):
            var = tk.BooleanVar(value=mode in allowed_modes)
            chk = tk.Checkbutton(self.mode_frame, text=mode, variable=var,
                                 bg=THEME["bg"], fg=THEME["fg"],
                                 selectcolor=THEME["entry_bg"],
                                 activebackground=THEME["bg"])
            chk.grid(row=i // 6, column=i % 6, sticky="w", padx=2)
            self.mode_vars[mode] = var
        row += 1

        # --- Use Serial Numbers ---
        self.serial_var = tk.BooleanVar(value=self.data.get("use_serial", False))
        tk.Checkbutton(f, text=Lang.t("use_serial"), variable=self.serial_var,
                       bg=THEME["bg"], fg=THEME["fg"],
                       selectcolor=THEME["entry_bg"],
                       activebackground=THEME["bg"],
                       font=("Consolas", 11)).grid(
            row=row, column=0, columnspan=2, sticky="w", **pad)
        row += 1

        # --- Use County ---
        self.county_var = tk.BooleanVar(value=self.data.get("use_county", False))
        tk.Checkbutton(f, text=Lang.t("use_county"), variable=self.county_var,
                       bg=THEME["bg"], fg=THEME["fg"],
                       selectcolor=THEME["entry_bg"],
                       activebackground=THEME["bg"],
                       font=("Consolas", 11)).grid(
            row=row, column=0, columnspan=2, sticky="w", **pad)
        row += 1

        # --- County List ---
        tk.Label(f, text=Lang.t("county_list"), **lbl_opts).grid(
            row=row, column=0, sticky="nw", **pad)
        self.county_list_entry = tk.Entry(f, width=50, **entry_opts)
        cl = self.data.get("county_list", [])
        self.county_list_entry.insert(0, ",".join(cl))
        self.county_list_entry.grid(row=row, column=1, sticky="w", **pad)
        row += 1

        # --- Required Stations ---
        tk.Label(f, text=Lang.t("required_stations_cfg"), **lbl_opts).grid(
            row=row, column=0, sticky="nw", **pad)
        self.req_text = tk.Text(f, width=40, height=3, **entry_opts)
        req = self.data.get("required_stations", [])
        self.req_text.insert("1.0", "\n".join(req))
        self.req_text.grid(row=row, column=1, sticky="w", **pad)
        row += 1

        # --- Special Scoring ---
        tk.Label(f, text=Lang.t("special_scoring_cfg"), **lbl_opts).grid(
            row=row, column=0, sticky="nw", **pad)
        self.special_text = tk.Text(f, width=40, height=4, **entry_opts)
        sp = self.data.get("special_scoring", {})
        sp_lines = [f"{k}={v}" for k, v in sp.items()]
        self.special_text.insert("1.0", "\n".join(sp_lines))
        self.special_text.grid(row=row, column=1, sticky="w", **pad)
        row += 1

        # --- Band Points ---
        tk.Label(f, text=Lang.t("band_points"), **lbl_opts).grid(
            row=row, column=0, sticky="nw", **pad)
        self.band_pts_text = tk.Text(f, width=40, height=4, **entry_opts)
        bp = self.data.get("band_points", {})
        bp_lines = [f"{k}={v}" for k, v in bp.items()]
        self.band_pts_text.insert("1.0", "\n".join(bp_lines))
        self.band_pts_text.grid(row=row, column=1, sticky="w", **pad)
        row += 1

        # --- Buttons ---
        btn_frame = tk.Frame(f, bg=THEME["bg"])
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)

        tk.Button(btn_frame, text=Lang.t("save"), command=self.on_save,
                  bg=THEME["accent"], fg="white", font=("Consolas", 12, "bold"),
                  width=15, cursor="hand2").pack(side="left", padx=10)

        tk.Button(btn_frame, text=Lang.t("cancel"), command=self.destroy,
                  bg=THEME["btn_bg"], fg="white", font=("Consolas", 12),
                  width=15, cursor="hand2").pack(side="left", padx=10)

    def _parse_key_value_text(self, text_widget):
        """Parse KEY=VALUE lines from a Text widget into a dict"""
        content = text_widget.get("1.0", "end").strip()
        result = {}
        for line in content.split("\n"):
            line = line.strip()
            if "=" in line:
                k, v = line.split("=", 1)
                k = k.strip().upper()
                v = v.strip()
                if k:
                    result[k] = v
            elif line:
                result[line.upper()] = "1"
        return result

    def _parse_lines(self, text_widget):
        """Parse non-empty lines from a Text widget into a list"""
        content = text_widget.get("1.0", "end").strip()
        return [line.strip() for line in content.split("\n") if line.strip()]

    def on_save(self):
        # Get contest ID
        if self.is_new:
            cid = self.id_entry.get().strip().lower().replace(" ", "-")
            if not cid:
                messagebox.showerror(Lang.t("error"), Lang.t("contest_id"))
                return
            if cid in self.all_contests:
                messagebox.showerror(Lang.t("error"), Lang.t("contest_exists"))
                return
            self.contest_id = cid

        # Gather data
        self.data["name_ro"] = self.name_ro_entry.get().strip()
        self.data["name_en"] = self.name_en_entry.get().strip()
        self.data["contest_type"] = self.type_var.get()
        self.data["scoring_mode"] = self.scoring_var.get()

        try:
            self.data["points_per_qso"] = int(self.ppq_entry.get())
        except ValueError:
            self.data["points_per_qso"] = 1

        try:
            self.data["min_qso"] = int(self.min_qso_entry.get())
        except ValueError:
            self.data["min_qso"] = 0

        self.data["multiplier_type"] = self.mult_var.get()

        # Categories
        self.data["categories"] = self._parse_lines(self.cat_text) or ["Individual"]

        # Bands
        self.data["allowed_bands"] = [b for b, v in self.band_vars.items() if v.get()]

        # Modes
        self.data["allowed_modes"] = [m for m, v in self.mode_vars.items() if v.get()]

        # Checkboxes
        self.data["use_serial"] = self.serial_var.get()
        self.data["use_county"] = self.county_var.get()

        # County list
        cl_str = self.county_list_entry.get().strip()
        self.data["county_list"] = [c.strip().upper() for c in cl_str.split(",") if c.strip()]

        # Required stations
        self.data["required_stations"] = [
            s.upper() for s in self._parse_lines(self.req_text)
        ]

        # Special scoring
        sp = self._parse_key_value_text(self.special_text)
        self.data["special_scoring"] = {}
        for k, v in sp.items():
            try:
                self.data["special_scoring"][k] = int(v)
            except ValueError:
                self.data["special_scoring"][k] = 1

        # Band points
        bp = self._parse_key_value_text(self.band_pts_text)
        self.data["band_points"] = {}
        for k, v in bp.items():
            # Band keys should be lowercase
            bk = k.lower()
            try:
                self.data["band_points"][bk] = int(v)
            except ValueError:
                self.data["band_points"][bk] = 1

        self.data["is_default"] = False

        self.result = (self.contest_id, self.data)
        self.destroy()


# =============================================================================
# CONTEST MANAGER DIALOG
# =============================================================================

class ContestManagerDialog(tk.Toplevel):
    """Dialog listing all contests with add/edit/delete/duplicate"""

    def __init__(self, parent, contests):
        super().__init__(parent)
        self.parent = parent
        self.contests = copy.deepcopy(contests)
        self.result = None

        self.title(Lang.t("contest_manager"))
        self.geometry("750x550")
        self.configure(bg=THEME["bg"])
        self.transient(parent)
        self.grab_set()

        self.build_ui()
        self.populate_list()
        self.center_window()

    def center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"+{x}+{y}")

    def build_ui(self):
        # Toolbar
        toolbar = tk.Frame(self, bg=THEME["header_bg"], pady=8)
        toolbar.pack(fill="x")

        btn_opts = {
            "bg": THEME["accent"], "fg": "white",
            "font": ("Consolas", 10), "cursor": "hand2",
        }

        tk.Button(toolbar, text=Lang.t("add_contest"),
                  command=self.add_contest, **btn_opts).pack(side="left", padx=5)
        tk.Button(toolbar, text=Lang.t("edit_contest"),
                  command=self.edit_contest, **btn_opts).pack(side="left", padx=5)
        tk.Button(toolbar, text=Lang.t("duplicate_contest"),
                  command=self.duplicate_contest, **btn_opts).pack(side="left", padx=5)
        tk.Button(toolbar, text=Lang.t("delete_contest"),
                  command=self.delete_contest,
                  bg=THEME["error"], fg="white",
                  font=("Consolas", 10), cursor="hand2").pack(side="left", padx=5)

        tk.Button(toolbar, text=Lang.t("export_contest"),
                  command=self.export_contests, **btn_opts).pack(side="right", padx=5)
        tk.Button(toolbar, text=Lang.t("import_contest"),
                  command=self.import_contests, **btn_opts).pack(side="right", padx=5)

        # Treeview for contests list
        tree_frame = tk.Frame(self, bg=THEME["bg"])
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("id", "name", "type", "scoring", "categories", "min_qso")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                                 selectmode="browse")

        headers = ["ID", Lang.t("contest_name"), Lang.t("contest_type"),
                   Lang.t("scoring_mode"), Lang.t("categories"), Lang.t("min_qso")]
        widths = [100, 180, 100, 100, 180, 60]

        for col, header, width in zip(columns, headers, widths):
            self.tree.heading(col, text=header)
            self.tree.column(col, width=width, anchor="center")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", lambda e: self.edit_contest())

        # Bottom buttons
        bottom = tk.Frame(self, bg=THEME["bg"], pady=10)
        bottom.pack(fill="x")

        tk.Button(bottom, text=Lang.t("save"), command=self.on_save,
                  bg=THEME["success"], fg="white",
                  font=("Consolas", 12, "bold"), width=15,
                  cursor="hand2").pack(side="left", padx=20)

        tk.Button(bottom, text=Lang.t("cancel"), command=self.destroy,
                  bg=THEME["btn_bg"], fg="white",
                  font=("Consolas", 12), width=15,
                  cursor="hand2").pack(side="right", padx=20)

    def populate_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        lang_key = "name_" + Lang.get()
        for cid, cdata in self.contests.items():
            name = cdata.get(lang_key, cdata.get("name_ro", cid))
            ctype = cdata.get("contest_type", "?")
            scoring = cdata.get("scoring_mode", "none")
            cats = ", ".join(cdata.get("categories", [])[:3])
            if len(cdata.get("categories", [])) > 3:
                cats += "..."
            min_q = cdata.get("min_qso", 0)

            self.tree.insert("", "end", iid=cid,
                             values=(cid, name, ctype, scoring, cats, min_q))

    def get_selected_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning(Lang.t("error"), Lang.t("no_contest_selected"))
            return None
        return sel[0]

    def add_contest(self):
        dlg = ContestEditorDialog(self, contest_id=None, contest_data=None,
                                  all_contests=self.contests)
        self.wait_window(dlg)
        if dlg.result:
            cid, cdata = dlg.result
            self.contests[cid] = cdata
            self.populate_list()

    def edit_contest(self):
        cid = self.get_selected_id()
        if not cid:
            return
        cdata = self.contests.get(cid, {})
        dlg = ContestEditorDialog(self, contest_id=cid, contest_data=cdata,
                                  all_contests=self.contests)
        self.wait_window(dlg)
        if dlg.result:
            _, new_data = dlg.result
            self.contests[cid] = new_data
            self.populate_list()

    def duplicate_contest(self):
        cid = self.get_selected_id()
        if not cid:
            return
        new_id = cid + "-copy"
        counter = 1
        while new_id in self.contests:
            new_id = f"{cid}-copy{counter}"
            counter += 1

        new_data = copy.deepcopy(self.contests[cid])
        new_data["name_ro"] = new_data.get("name_ro", "") + " (Copie)"
        new_data["name_en"] = new_data.get("name_en", "") + " (Copy)"
        new_data["is_default"] = False

        self.contests[new_id] = new_data
        self.populate_list()

    def delete_contest(self):
        cid = self.get_selected_id()
        if not cid:
            return

        cdata = self.contests.get(cid, {})
        if cdata.get("is_default", False):
            messagebox.showwarning(Lang.t("error"), Lang.t("default_contest_warn"))
            return

        name = cdata.get("name_" + Lang.get(), cid)
        if messagebox.askyesno(
            Lang.t("confirm_delete"),
            Lang.t("confirm_delete_contest").format(name)
        ):
            del self.contests[cid]
            self.populate_list()

    def export_contests(self):
        """Export contests to a JSON file"""
        try:
            filename = f"contests_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.json"
            filepath = os.path.join(get_data_dir(), filename)
            with open(filepath, "w", encoding="utf-8") as f_out:
                json.dump(self.contests, f_out, indent=2, ensure_ascii=False)
            messagebox.showinfo("OK", f"Exportat: {filename}")
        except Exception as e:
            messagebox.showerror(Lang.t("error"), str(e))

    def import_contests(self):
        """Import contests from a JSON file"""
        from tkinter import filedialog
        filepath = filedialog.askopenfilename(
            title="Import Contests",
            filetypes=[("JSON", "*.json")],
            initialdir=get_data_dir()
        )
        if not filepath:
            return
        try:
            with open(filepath, "r", encoding="utf-8") as f_in:
                imported = json.load(f_in)
            if isinstance(imported, dict):
                count = 0
                for cid, cdata in imported.items():
                    if isinstance(cdata, dict):
                        if cid in self.contests:
                            cid = cid + "-imported"
                        self.contests[cid] = cdata
                        count += 1
                self.populate_list()
                messagebox.showinfo("OK", f"Importate: {count} concursuri")
            else:
                messagebox.showerror(Lang.t("error"), "Format invalid!")
        except Exception as e:
            messagebox.showerror(Lang.t("error"), str(e))

    def on_save(self):
        self.result = self.contests
        self.destroy()


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

        # Ensure 'simplu' always exists as fallback
        if "simplu" not in self.contests:
            self.contests["simplu"] = DEFAULT_CONTESTS["simplu"]
            DataManager.save_json("contests.json", self.contests)

        # Ensure selected contest exists
        if self.config_data.get("contest", "") not in self.contests:
            self.config_data["contest"] = "simplu"
            DataManager.save_json("config.json", self.config_data)

        Lang.set(self.config_data.get("lang", "ro"))

        self.edit_index = None
        self.entries = {}
        self.serial_counter = len(self.log_data) + 1

        self.setup_window()
        self.setup_styles()
        self.create_menu()
        self.create_ui()
        self.create_context_menu()
        self.refresh_log()

        self.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.bind('<Return>', self.on_enter_pressed)

    def get_current_contest(self):
        """Get current contest rules dict"""
        key = self.config_data.get("contest", "simplu")
        return self.contests.get(key, self.contests.get("simplu", {}))

    def setup_window(self):
        self.title(Lang.t("app_title"))
        self.configure(bg=THEME["bg"])
        width, height = 1150, 750
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.minsize(950, 600)

    def setup_styles(self):
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
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # Contests menu
        contest_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=Lang.t("contests_menu"), menu=contest_menu)
        contest_menu.add_command(label=Lang.t("contest_manager"),
                                command=self.open_contest_manager)
        contest_menu.add_separator()

        # Quick-switch submenu
        switch_menu = tk.Menu(contest_menu, tearoff=0)
        contest_menu.add_cascade(label="⚡ Switch", menu=switch_menu)
        for cid in self.contests:
            c = self.contests[cid]
            name = c.get("name_" + Lang.get(), c.get("name_ro", cid))
            switch_menu.add_command(
                label=f"{name} ({cid})",
                command=lambda k=cid: self.switch_contest(k)
            )

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=Lang.t("help"), menu=help_menu)
        help_menu.add_command(label=Lang.t("about"), command=self.show_about)
        help_menu.add_separator()
        help_menu.add_command(label="Exit", command=self.on_exit)

    def create_context_menu(self):
        self.ctx_menu = Menu(self, tearoff=0)
        self.ctx_menu.add_command(label=Lang.t("edit_qso"), command=self.edit_selected)
        self.ctx_menu.add_separator()
        self.ctx_menu.add_command(label=Lang.t("delete_qso"), command=self.delete_selected)

    def create_ui(self):
        self.create_header()
        self.create_input_area()
        self.create_log_view()
        self.create_button_bar()

    def create_header(self):
        header = tk.Frame(self, bg=THEME["header_bg"], pady=8)
        header.pack(fill="x")

        left_frame = tk.Frame(header, bg=THEME["header_bg"])
        left_frame.pack(side="left", padx=15)

        self.led_canvas = tk.Canvas(left_frame, width=18, height=18,
                                    bg=THEME["header_bg"], highlightthickness=0)
        self.led = self.led_canvas.create_oval(2, 2, 16, 16,
                                               fill=THEME["led_on"], outline="")
        self.led_canvas.pack(side="left", padx=(0, 8))

        self.status_label = tk.Label(left_frame, text=Lang.t("online"),
                                     bg=THEME["header_bg"], fg=THEME["led_on"],
                                     font=self.font_main)
        self.status_label.pack(side="left")

        self.info_label = tk.Label(left_frame, text="", bg=THEME["header_bg"],
                                   fg=THEME["fg"], font=self.font_main)
        self.info_label.pack(side="left", padx=20)
        self.update_info_bar()

        right_frame = tk.Frame(header, bg=THEME["header_bg"])
        right_frame.pack(side="right", padx=15)

        # Language selector
        self.lang_var = tk.StringVar(value=self.config_data.get("lang", "ro"))
        lang_combo = ttk.Combobox(right_frame, textvariable=self.lang_var,
                                  values=["ro", "en"], state="readonly", width=5)
        lang_combo.pack(side="left", padx=5)
        lang_combo.bind("<<ComboboxSelected>>", self.on_language_change)

        # Contest selector
        self.contest_var = tk.StringVar(value=self.config_data.get("contest", "simplu"))
        self.contest_combo = ttk.Combobox(right_frame, textvariable=self.contest_var,
                                          values=list(self.contests.keys()),
                                          state="readonly", width=18)
        self.contest_combo.pack(side="left", padx=5)
        self.contest_combo.bind("<<ComboboxSelected>>", self.on_contest_change)

        # Contest type label
        contest = self.get_current_contest()
        ctype = contest.get("contest_type", "?")
        self.type_label = tk.Label(right_frame, text=f"[{ctype}]",
                                   bg=THEME["header_bg"], fg=THEME["warning"],
                                   font=self.font_bold)
        self.type_label.pack(side="left", padx=5)

    def create_input_area(self):
        input_frame = tk.Frame(self, bg=THEME["bg"], pady=15)
        input_frame.pack(fill="x", padx=15)

        row1 = tk.Frame(input_frame, bg=THEME["bg"])
        row1.pack(fill="x")

        contest = self.get_current_contest()

        # Callsign
        call_frame = tk.Frame(row1, bg=THEME["bg"])
        call_frame.pack(side="left", padx=5)
        tk.Label(call_frame, text=Lang.t("call"), bg=THEME["bg"],
                 fg=THEME["fg"], font=self.font_bold).pack()
        self.entries["call"] = tk.Entry(call_frame, width=18, bg=THEME["entry_bg"],
                                        fg=THEME["fg"], font=self.font_bold,
                                        insertbackground=THEME["fg"], justify="center")
        self.entries["call"].pack(ipady=5)

        # Band - filtered by contest
        allowed_bands = contest.get("allowed_bands", BANDS_ALL)
        band_frame = tk.Frame(row1, bg=THEME["bg"])
        band_frame.pack(side="left", padx=5)
        tk.Label(band_frame, text=Lang.t("band"), bg=THEME["bg"],
                 fg=THEME["fg"], font=self.font_main).pack()
        self.entries["band"] = ttk.Combobox(band_frame, values=allowed_bands,
                                            state="readonly", width=8,
                                            font=self.font_main)
        self.entries["band"].set(allowed_bands[0] if allowed_bands else "40m")
        self.entries["band"].pack()

        # Mode - filtered by contest
        allowed_modes = contest.get("allowed_modes", MODES_ALL)
        mode_frame = tk.Frame(row1, bg=THEME["bg"])
        mode_frame.pack(side="left", padx=5)
        tk.Label(mode_frame, text=Lang.t("mode"), bg=THEME["bg"],
                 fg=THEME["fg"], font=self.font_main).pack()
        self.entries["mode"] = ttk.Combobox(mode_frame, values=allowed_modes,
                                            state="readonly", width=8,
                                            font=self.font_main)
        self.entries["mode"].set(allowed_modes[0] if allowed_modes else "SSB")
        self.entries["mode"].pack()

        # RST fields
        for key, label, default in [("rst_s", Lang.t("rst_s"), "59"),
                                     ("rst_r", Lang.t("rst_r"), "59")]:
            frame = tk.Frame(row1, bg=THEME["bg"])
            frame.pack(side="left", padx=5)
            tk.Label(frame, text=label, bg=THEME["bg"],
                     fg=THEME["fg"], font=self.font_main).pack()
            entry = tk.Entry(frame, width=6, bg=THEME["entry_bg"],
                            fg=THEME["fg"], font=self.font_main,
                            insertbackground=THEME["fg"], justify="center")
            entry.insert(0, default)
            entry.pack()
            self.entries[key] = entry

        # Serial numbers (if contest uses them)
        if contest.get("use_serial", False):
            for key, label in [("serial_s", Lang.t("serial_s")),
                                ("serial_r", Lang.t("serial_r"))]:
                frame = tk.Frame(row1, bg=THEME["bg"])
                frame.pack(side="left", padx=5)
                tk.Label(frame, text=label, bg=THEME["bg"],
                         fg=THEME["fg"], font=self.font_main).pack()
                entry = tk.Entry(frame, width=6, bg=THEME["entry_bg"],
                                fg=THEME["fg"], font=self.font_main,
                                insertbackground=THEME["fg"], justify="center")
                if key == "serial_s":
                    entry.insert(0, str(self.serial_counter))
                entry.pack()
                self.entries[key] = entry

        # Note / Locator
        note_frame = tk.Frame(row1, bg=THEME["bg"])
        note_frame.pack(side="left", padx=5)
        note_label = Lang.t("note")
        if contest.get("use_county", False):
            note_label = Lang.t("county") + " / " + Lang.t("note")
        tk.Label(note_frame, text=note_label, bg=THEME["bg"],
                 fg=THEME["fg"], font=self.font_main).pack()
        self.entries["note"] = tk.Entry(note_frame, width=15, bg=THEME["entry_bg"],
                                       fg=THEME["fg"], font=self.font_main,
                                       insertbackground=THEME["fg"], justify="center")
        self.entries["note"].pack()
        self.entries["note"] = self.entries["note"]

        # Manual datetime checkbox
        dt_frame = tk.Frame(row1, bg=THEME["bg"])
        dt_frame.pack(side="left", padx=10)

        self.manual_dt_var = tk.BooleanVar(
            value=self.config_data.get("manual_datetime", False))
        chk = tk.Checkbutton(dt_frame, text=Lang.t("enable_manual"),
                             variable=self.manual_dt_var, bg=THEME["bg"],
                             fg=THEME["fg"], selectcolor=THEME["entry_bg"],
                             activebackground=THEME["bg"],
                             command=self.toggle_manual_datetime)
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

        # Row 2: Manual date/time
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

        now = datetime.datetime.now()
        self.entries["date"].config(state="normal")
        self.entries["date"].insert(0, now.strftime("%Y-%m-%d"))
        self.entries["date"].config(state="disabled")
        self.entries["time"].config(state="normal")
        self.entries["time"].insert(0, now.strftime("%H:%M"))
        self.entries["time"].config(state="disabled")

        # Row 3: Contest controls
        self.contest_controls = tk.Frame(input_frame, bg=THEME["bg"])
        self.contest_controls.pack(fill="x", pady=(10, 0))
        self.update_contest_controls()

    def create_log_view(self):
        tree_frame = tk.Frame(self, bg=THEME["bg"])
        tree_frame.pack(fill="both", expand=True, padx=15, pady=5)

        contest = self.get_current_contest()
        use_serial = contest.get("use_serial", False)
        has_scoring = contest.get("scoring_mode", "none") != "none"

        # Build columns dynamically based on contest
        columns = ["nr", "call", "band", "mode", "rst_s", "rst_r"]
        headers = [Lang.t("qso_nr"), Lang.t("call"), Lang.t("band"),
                   Lang.t("mode"), Lang.t("rst_s"), Lang.t("rst_r")]
        widths = [45, 130, 65, 65, 55, 55]

        if use_serial:
            columns += ["serial_s", "serial_r"]
            headers += [Lang.t("serial_s"), Lang.t("serial_r")]
            widths += [55, 55]

        columns += ["note", "date", "time"]
        headers += [Lang.t("note"), Lang.t("data"), Lang.t("ora")]
        widths += [160, 95, 70]

        if has_scoring:
            columns.append("score")
            headers.append(Lang.t("score_col"))
            widths.append(60)

        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                                 selectmode="browse")

        for col, header, width in zip(columns, headers, widths):
            self.tree.heading(col, text=header)
            self.tree.column(col, width=width, anchor="center")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical",
                                  command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", self.on_tree_double_click)
        self.tree.bind("<Button-3>", self.on_tree_right_click)

    def create_button_bar(self):
        btn_bar = tk.Frame(self, bg=THEME["bg"], pady=10)
        btn_bar.pack(fill="x", padx=15)

        buttons = [
            (Lang.t("settings"), self.show_settings, THEME["warning"]),
            ("🏆 " + Lang.t("contests_menu"), self.open_contest_manager, "#E91E63"),
            (Lang.t("stats"), self.show_stats, "#2196F3"),
            (Lang.t("validate"), self.validate_log, THEME["success"]),
            (Lang.t("export"), self.show_export, "#9C27B0"),
            (Lang.t("delete"), self.delete_selected, THEME["error"]),
            (Lang.t("backup"), self.create_backup, "#607D8B"),
        ]

        for text, command, color in buttons:
            tk.Button(btn_bar, text=text, command=command, bg=color, fg="white",
                      font=self.font_main, width=14, cursor="hand2").pack(
                side="left", padx=4)

    # =========================================================================
    # UI UPDATE METHODS
    # =========================================================================

    def update_info_bar(self):
        call = self.config_data.get("call", "NOCALL")
        contest_key = self.config_data.get("contest", "simplu")
        contest = self.contests.get(contest_key, {})
        lang_key = "name_" + Lang.get()
        contest_name = contest.get(lang_key, contest.get("name_ro", contest_key))
        ctype = contest.get("contest_type", "?")

        cat_idx = self.config_data.get("cat", 0)
        categories = contest.get("categories", ["A"])
        if isinstance(cat_idx, int) and 0 <= cat_idx < len(categories):
            category = categories[cat_idx]
        else:
            category = categories[0] if categories else "A"

        qso_count = len(self.log_data)

        # Calculate score
        _, _, total = ScoringEngine.calculate_total_score(
            self.log_data, contest, self.config_data
        )

        info_text = f"{call} | {contest_name} [{ctype}] | {category} | QSO: {qso_count}"
        if contest.get("scoring_mode", "none") != "none":
            info_text += f" | Scor: {total}"

        self.info_label.config(text=info_text)

    def update_contest_controls(self):
        for widget in self.contest_controls.winfo_children():
            widget.destroy()

        contest_key = self.config_data.get("contest", "simplu")
        contest = self.contests.get(contest_key, {})

        if not contest:
            return

        # Category selector
        tk.Label(self.contest_controls, text=Lang.t("category"),
                 bg=THEME["bg"], fg=THEME["fg"],
                 font=self.font_main).pack(side="left", padx=5)

        categories = contest.get("categories", ["A"])
        self.cat_var = tk.StringVar()

        cat_idx = self.config_data.get("cat", 0)
        if isinstance(cat_idx, int) and 0 <= cat_idx < len(categories):
            self.cat_var.set(categories[cat_idx])
        else:
            self.cat_var.set(categories[0] if categories else "A")

        cat_combo = ttk.Combobox(self.contest_controls, textvariable=self.cat_var,
                                 values=categories, state="readonly", width=25)
        cat_combo.pack(side="left", padx=5)

        # County selector (if contest uses county)
        if contest.get("use_county", False):
            tk.Label(self.contest_controls, text=Lang.t("county"),
                     bg=THEME["bg"], fg=THEME["fg"],
                     font=self.font_main).pack(side="left", padx=(20, 5))

            county_list = contest.get("county_list", [])
            self.county_var = tk.StringVar(
                value=self.config_data.get("county", "NT"))
            county_combo = ttk.Combobox(self.contest_controls,
                                        textvariable=self.county_var,
                                        values=county_list, state="readonly",
                                        width=8)
            county_combo.pack(side="left", padx=5)

        # Contest type badge
        ctype = contest.get("contest_type", "?")
        scoring = contest.get("scoring_mode", "none")
        tk.Label(self.contest_controls,
                 text=f"  [{ctype} / {scoring}]",
                 bg=THEME["bg"], fg=THEME["warning"],
                 font=("Consolas", 10, "italic")).pack(side="left", padx=10)

        # Save button
        tk.Button(self.contest_controls, text="💾 " + Lang.t("save"),
                  command=self.save_contest_settings, bg=THEME["accent"],
                  fg="white", font=self.font_main,
                  cursor="hand2").pack(side="left", padx=10)

    def toggle_manual_datetime(self):
        is_manual = self.manual_dt_var.get()
        state = "normal" if is_manual else "disabled"
        self.entries["date"].config(state=state)
        self.entries["time"].config(state=state)

        led_color = THEME["led_off"] if is_manual else THEME["led_on"]
        status_text = Lang.t("offline") if is_manual else Lang.t("online")
        self.led_canvas.itemconfig(self.led, fill=led_color)
        self.status_label.config(text=status_text, fg=led_color)

        self.config_data["manual_datetime"] = is_manual
        DataManager.save_json("config.json", self.config_data)

    def refresh_log(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        contest = self.get_current_contest()
        has_scoring = contest.get("scoring_mode", "none") != "none"
        use_serial = contest.get("use_serial", False)

        for i, qso in enumerate(self.log_data):
            call = qso.get("c", "")
            band = qso.get("b", "")
            mode = qso.get("m", "")
            rst_s = qso.get("s", "59")
            rst_r = qso.get("r", "59")
            note = qso.get("n", "")
            date = qso.get("d", "")
            time = qso.get("t", "")
            serial_s = qso.get("ss", "")
            serial_r = qso.get("sr", "")
            nr = len(self.log_data) - i

            values = [nr, call, band, mode, rst_s, rst_r]

            if use_serial:
                values += [serial_s, serial_r]

            values += [note, date, time]

            if has_scoring:
                score = ScoringEngine.calculate_qso_score(
                    qso, contest, self.config_data)
                values.append(score)

            self.tree.insert("", "end", iid=str(i), values=values)

        self.update_info_bar()

    def rebuild_ui(self):
        """Rebuild entire UI (after contest or language change)"""
        for widget in self.winfo_children():
            widget.destroy()
        self.entries = {}
        self.create_menu()
        self.create_ui()
        self.create_context_menu()
        self.refresh_log()

    # =========================================================================
    # QSO OPERATIONS
    # =========================================================================

    def get_datetime(self):
        if self.manual_dt_var.get():
            date_str = self.entries["date"].get().strip()
            time_str = self.entries["time"].get().strip()
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
            "t": time_str,
        }

        # Serial numbers
        if "serial_s" in self.entries:
            qso["ss"] = self.entries["serial_s"].get()
        if "serial_r" in self.entries:
            qso["sr"] = self.entries["serial_r"].get()

        if self.edit_index is not None:
            self.log_data[self.edit_index] = qso
            self.edit_index = None
            self.log_btn.config(text=Lang.t("log"), bg=THEME["accent"])
        else:
            self.log_data.insert(0, qso)
            self.serial_counter += 1

        self.clear_inputs()
        self.refresh_log()
        DataManager.save_json("log.json", self.log_data)

    def clear_inputs(self):
        self.entries["call"].delete(0, "end")
        if "note" in self.entries:
            self.entries["note"].delete(0, "end")
        if "serial_s" in self.entries:
            self.entries["serial_s"].delete(0, "end")
            self.entries["serial_s"].insert(0, str(self.serial_counter))
        if "serial_r" in self.entries:
            self.entries["serial_r"].delete(0, "end")
        self.entries["call"].focus()

        if self.edit_index is not None:
            self.edit_index = None
            self.log_btn.config(text=Lang.t("log"), bg=THEME["accent"])

    def edit_selected(self):
        selection = self.tree.selection()
        if not selection:
            return

        self.edit_index = int(selection[0])
        qso = self.log_data[self.edit_index]

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

        if "serial_s" in self.entries:
            self.entries["serial_s"].delete(0, "end")
            self.entries["serial_s"].insert(0, qso.get("ss", ""))
        if "serial_r" in self.entries:
            self.entries["serial_r"].delete(0, "end")
            self.entries["serial_r"].insert(0, qso.get("sr", ""))

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

        self.log_btn.config(text=Lang.t("update"), bg=THEME["warning"])

    def delete_selected(self):
        selection = self.tree.selection()
        if not selection:
            return
        if messagebox.askyesno(Lang.t("confirm_delete"),
                               Lang.t("confirm_delete_text")):
            indices = sorted([int(x) for x in selection], reverse=True)
            for idx in indices:
                self.log_data.pop(idx)
            self.refresh_log()
            DataManager.save_json("log.json", self.log_data)

    # =========================================================================
    # EVENT HANDLERS
    # =========================================================================

    def on_enter_pressed(self, event):
        if isinstance(self.focus_get(), tk.Entry):
            self.add_qso()
            return "break"

    def on_tree_double_click(self, event):
        self.edit_selected()

    def on_tree_right_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.ctx_menu.post(event.x_root, event.y_root)

    def on_language_change(self, event):
        Lang.set(self.lang_var.get())
        self.config_data["lang"] = self.lang_var.get()
        DataManager.save_json("config.json", self.config_data)
        self.rebuild_ui()

    def on_contest_change(self, event):
        self.config_data["contest"] = self.contest_var.get()
        self.config_data["cat"] = 0
        DataManager.save_json("config.json", self.config_data)
        self.serial_counter = len(self.log_data) + 1
        self.rebuild_ui()

    def switch_contest(self, contest_key):
        """Quick-switch contest from menu"""
        self.config_data["contest"] = contest_key
        self.config_data["cat"] = 0
        DataManager.save_json("config.json", self.config_data)
        self.serial_counter = len(self.log_data) + 1
        self.rebuild_ui()

    def save_contest_settings(self):
        contest_key = self.config_data.get("contest", "simplu")
        contest = self.contests.get(contest_key, {})
        categories = contest.get("categories", [])

        selected_cat = self.cat_var.get()
        try:
            cat_idx = categories.index(selected_cat)
        except ValueError:
            cat_idx = 0

        self.config_data["cat"] = cat_idx

        if contest.get("use_county", False) and hasattr(self, 'county_var'):
            self.config_data["county"] = self.county_var.get()

        DataManager.save_json("config.json", self.config_data)
        self.update_info_bar()
        messagebox.showinfo("OK", Lang.t("settings_saved"))

    def open_contest_manager(self):
        """Open the contest manager dialog"""
        dlg = ContestManagerDialog(self, self.contests)
        self.wait_window(dlg)

        if dlg.result is not None:
            self.contests = dlg.result
            DataManager.save_json("contests.json", self.contests)

            # Ensure current contest still exists
            if self.config_data.get("contest", "") not in self.contests:
                self.config_data["contest"] = "simplu"
                self.config_data["cat"] = 0
                DataManager.save_json("config.json", self.config_data)

            self.rebuild_ui()

    # =========================================================================
    # DIALOGS
    # =========================================================================

    def show_about(self):
        dialog = tk.Toplevel(self)
        dialog.title(Lang.t("about"))
        dialog.geometry("500x350")
        dialog.resizable(False, False)
        dialog.configure(bg=THEME["bg"])
        dialog.transient(self)
        dialog.grab_set()

        tk.Label(dialog, text="YO Log PRO v14.0", bg=THEME["bg"],
                 fg=THEME["accent"],
                 font=("Consolas", 16, "bold")).pack(pady=20)

        tk.Label(dialog, text="Multi-Contest Configurable Logger",
                 bg=THEME["bg"], fg=THEME["warning"],
                 font=("Consolas", 11)).pack()

        tk.Label(dialog, text=Lang.t("credits"), bg=THEME["bg"],
                 fg=THEME["fg"], font=self.font_main,
                 justify="center").pack(pady=10)

        tk.Label(dialog, text=Lang.t("usage"), bg=THEME["bg"],
                 fg=THEME["fg"], font=("Consolas", 10),
                 justify="left").pack(pady=10, padx=20)

        tk.Button(dialog, text=Lang.t("close"), command=dialog.destroy,
                  bg=THEME["accent"], fg="white", width=15).pack(pady=15)

    def show_settings(self):
        dialog = tk.Toplevel(self)
        dialog.title(Lang.t("settings"))
        dialog.geometry("400x350")
        dialog.resizable(False, False)
        dialog.configure(bg=THEME["bg"])
        dialog.transient(self)
        dialog.grab_set()

        tk.Label(dialog, text=Lang.t("station_info"), bg=THEME["bg"],
                 fg=THEME["accent"], font=self.font_bold).pack(
            pady=10, anchor="w", padx=20)

        fields = [
            ("call", Lang.t("call") + ":", self.config_data.get("call", "")),
            ("loc", Lang.t("locator"), self.config_data.get("loc", "")),
            ("jud", Lang.t("county") + ":", self.config_data.get("jud", "")),
            ("addr", Lang.t("address"), self.config_data.get("addr", "")),
        ]
        entries = {}
        for key, label, value in fields:
            tk.Label(dialog, text=label, bg=THEME["bg"],
                     fg=THEME["fg"]).pack(anchor="w", padx=20)
            e = tk.Entry(dialog, bg=THEME["entry_bg"], fg=THEME["fg"],
                        font=self.font_main, width=40)
            e.insert(0, value)
            e.pack(pady=2, padx=20, fill="x")
            entries[key] = e

        tk.Label(dialog, text=Lang.t("font_size"), bg=THEME["bg"],
                 fg=THEME["fg"]).pack(anchor="w", padx=20)
        fs_entry = tk.Entry(dialog, bg=THEME["entry_bg"], fg=THEME["fg"],
                           font=self.font_main, width=10)
        fs_entry.insert(0, str(self.config_data.get("fs", 12)))
        fs_entry.pack(pady=2, padx=20, anchor="w")

        def save():
            self.config_data["call"] = entries["call"].get().upper().strip()
            self.config_data["loc"] = entries["loc"].get().upper().strip()
            self.config_data["jud"] = entries["jud"].get().upper().strip()
            self.config_data["addr"] = entries["addr"].get().strip()
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
        band_count = Counter(qso.get("b", "") for qso in self.log_data)
        mode_count = Counter(qso.get("m", "") for qso in self.log_data)

        stats_text = f"Total QSO: {len(self.log_data)}\n\n"
        stats_text += "Per bandă / Per band:\n"
        for band in sorted(band_count.keys()):
            stats_text += f"  {band}: {band_count[band]}\n"

        stats_text += "\nPer mod / Per mode:\n"
        for mode in sorted(mode_count.keys()):
            stats_text += f"  {mode}: {mode_count[mode]}\n"

        contest = self.get_current_contest()
        qso_pts, mult, total = ScoringEngine.calculate_total_score(
            self.log_data, contest, self.config_data)

        calls = {qso.get("c", "").upper() for qso in self.log_data}
        stats_text += f"\n{Lang.t('stations_worked')}: {len(calls)}"

        required = contest.get("required_stations", [])
        if required:
            found = [s for s in required if s.upper() in calls]
            missing = [s for s in required if s.upper() not in calls]
            stats_text += f"\n{Lang.t('required_stations')} ✓: {', '.join(found) if found else '-'}"
            if missing:
                stats_text += f"\nLipsesc / Missing: {', '.join(missing)}"

        if contest.get("scoring_mode", "none") != "none":
            stats_text += f"\n\nQSO Points: {qso_pts}"
            if contest.get("multiplier_type", "none") != "none":
                stats_text += f"\nMultipliers: {mult}"
            stats_text += f"\n{Lang.t('total_score')}: {total}"

        messagebox.showinfo(Lang.t("stats"), stats_text)

    def validate_log(self):
        contest = self.get_current_contest()
        valid, message, score = ScoringEngine.validate_log(
            self.log_data, contest, self.config_data)

        if valid:
            min_qso = contest.get("min_qso", 0)
            if min_qso > 0:
                diploma = "DA / YES" if len(self.log_data) >= min_qso else "NU / NO"
                message += f"\n\nEligibil diplomă: {diploma}"
            messagebox.showinfo(Lang.t("validation_result"), f"✓ {message}")
        else:
            messagebox.showwarning(Lang.t("validation_result"), f"✗ {message}")

    def show_export(self):
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
        try:
            contest_key = self.config_data.get("contest", "simplu")
            contest = self.get_current_contest()
            contest_name = contest.get("name_" + Lang.get(),
                                       contest.get("name_ro", contest_key))

            lines = [
                "START-OF-LOG: 3.0",
                f"CONTEST: {contest_name}",
                f"CALLSIGN: {self.config_data.get('call', 'NOCALL')}",
                f"LOCATION: {self.config_data.get('loc', '')}",
                f"CATEGORY: ALL",
            ]

            for qso in self.log_data:
                line = f"QSO: {qso['b']:>5} {qso['m']:<4} {qso['d']} {qso['t']} "
                line += f"{self.config_data.get('call', 'NOCALL'):<13} {qso['s']} "
                if qso.get('ss'):
                    line += f"{qso['ss']:>4} "
                line += f"{qso['c']:<13} {qso['r']}"
                if qso.get('sr'):
                    line += f" {qso['sr']:>4}"
                lines.append(line)

            lines.append("END-OF-LOG:")

            filename = (f"cabrillo_{contest_key}_"
                       f"{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.log")
            filepath = os.path.join(get_data_dir(), filename)

            with open(filepath, "w", encoding="utf-8") as f_out:
                f_out.write("\n".join(lines))

            messagebox.showinfo(Lang.t("export_success"), f"Salvat: {filename}")
            parent.destroy()
        except Exception as e:
            messagebox.showerror(Lang.t("error"), str(e))

    def export_adif(self, parent):
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

                if qso.get('ss'):
                    stx = str(qso['ss'])
                    record += f"<STX:{len(stx)}>{stx}"
                if qso.get('sr'):
                    srx = str(qso['sr'])
                    record += f"<SRX:{len(srx)}>{srx}"

                if qso.get('n'):
                    record += f"<COMMENT:{len(qso['n'])}>{qso['n']}"

                record += "<EOR>"
                lines.append(record)

            filename = f"adif_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.adi"
            filepath = os.path.join(get_data_dir(), filename)

            with open(filepath, "w", encoding="utf-8") as f_out:
                f_out.write("\n".join(lines))

            messagebox.showinfo(Lang.t("export_success"), f"Salvat: {filename}")
            parent.destroy()
        except Exception as e:
            messagebox.showerror(Lang.t("error"), str(e))

    def export_csv(self, parent):
        try:
            contest = self.get_current_contest()
            use_serial = contest.get("use_serial", False)

            header = "Nr,Date,Time,Call,Band,Mode,RST_Sent,RST_Rcvd"
            if use_serial:
                header += ",Serial_Sent,Serial_Rcvd"
            header += ",Note,Score"
            lines = [header]

            for i, qso in enumerate(self.log_data):
                score = ScoringEngine.calculate_qso_score(
                    qso, contest, self.config_data)

                line = (f"{len(self.log_data)-i},{qso['d']},{qso['t']},"
                       f"{qso['c']},{qso['b']},{qso['m']},"
                       f"{qso['s']},{qso['r']}")
                if use_serial:
                    line += f",{qso.get('ss','')},{qso.get('sr','')}"
                line += f",{qso.get('n','')},{score}"
                lines.append(line)

            filename = f"log_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv"
            filepath = os.path.join(get_data_dir(), filename)

            with open(filepath, "w", encoding="utf-8") as f_out:
                f_out.write("\n".join(lines))

            messagebox.showinfo(Lang.t("export_success"), f"Salvat: {filename}")
            parent.destroy()
        except Exception as e:
            messagebox.showerror(Lang.t("error"), str(e))

    def create_backup(self):
        if DataManager.create_backup(self.log_data):
            messagebox.showinfo("OK", Lang.t("backup_success"))
        else:
            messagebox.showerror(Lang.t("error"), Lang.t("backup_error"))

    def on_exit(self):
        if messagebox.askyesno(Lang.t("exit_confirm"), Lang.t("exit_confirm")):
            DataManager.save_json("log.json", self.log_data)
            DataManager.save_json("config.json", self.config_data)
            DataManager.save_json("contests.json", self.contests)
            DataManager.create_backup(self.log_data)
            self.destroy()


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    app = RadioLogApp()
    app.mainloop()
