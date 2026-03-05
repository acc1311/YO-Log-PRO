#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YO Log PRO v16.0 FINAL — Professional Multi-Contest Amateur Radio Logger
Developed by: Ardei Constantin-Cătălin (YO8ACR)
Email: yo8acr@gmail.com
"""

import os
import sys
import re
import csv
import copy
import json
import math
import datetime
import io
import hashlib
from pathlib import Path
from collections import Counter, deque
import tkinter as tk
from tkinter import ttk, messagebox, Menu, filedialog

try:
    if sys.platform == "win32":
        import winsound
        HAS_SOUND = True
    else:
        HAS_SOUND = False
except ImportError:
    HAS_SOUND = False


def get_data_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.abspath(".")


def beep(kind="info"):
    if not HAS_SOUND:
        return
    try:
        m = {"error": 0x10, "warning": 0x30, "success": 0x40, "info": 0x0}
        winsound.MessageBeep(m.get(kind, 0x0))
    except:
        pass


class Loc:
    @staticmethod
    def to_latlon(loc):
        loc = loc.upper().strip()
        if len(loc) < 4:
            return None, None
        try:
            lon = (ord(loc[0]) - 65) * 20 - 180
            lat = (ord(loc[1]) - 65) * 10 - 90
            lon += int(loc[2]) * 2
            lat += int(loc[3])
            if len(loc) >= 6:
                lon += (ord(loc[4]) - 65) * (2 / 24) + 1 / 24
                lat += (ord(loc[5]) - 65) * (1 / 24) + 0.5 / 24
            else:
                lon += 1
                lat += 0.5
            return lat, lon
        except:
            return None, None

    @staticmethod
    def dist(a, b):
        la1, lo1 = Loc.to_latlon(a)
        la2, lo2 = Loc.to_latlon(b)
        if None in (la1, lo1, la2, lo2):
            return 0
        R = 6371.0
        d1 = math.radians(la2 - la1)
        d2 = math.radians(lo2 - lo1)
        a_ = (math.sin(d1 / 2) ** 2 + math.cos(math.radians(la1)) * math.cos(math.radians(la2)) * math.sin(d2 / 2) ** 2)
        return round(R * 2 * math.atan2(math.sqrt(a_), math.sqrt(1 - a_)), 1)

    @staticmethod
    def valid(s):
        s = s.upper().strip()
        if len(s) == 4:
            return s[0:2].isalpha() and s[2:4].isdigit() and 'A' <= s[0] <= 'R' and 'A' <= s[1] <= 'R'
        if len(s) == 6:
            return (s[0:2].isalpha() and s[2:4].isdigit() and s[4:6].isalpha() and 'A' <= s[0] <= 'R' and 'A' <= s[1] <= 'R' and 'A' <= s[4] <= 'X' and 'A' <= s[5] <= 'X')
        return False


class DXCC:
    DB = {
        "YO": "Romania", "YP": "Romania", "YQ": "Romania", "YR": "Romania",
        "DL": "Germany", "DJ": "Germany", "DK": "Germany", "DA": "Germany", "DB": "Germany",
        "DC": "Germany", "DD": "Germany", "DF": "Germany", "DG": "Germany", "DH": "Germany", "DM": "Germany",
        "G": "England", "M": "England", "2E": "England", "GW": "Wales", "GM": "Scotland",
        "GI": "N. Ireland", "GD": "Isle of Man", "GJ": "Jersey", "GU": "Guernsey",
        "F": "France", "TM": "France", "HB9": "Switzerland", "HB": "Switzerland",
        "I": "Italy", "IK": "Italy", "IZ": "Italy", "IW": "Italy", "IN3": "Italy",
        "EA": "Spain", "EB": "Spain", "EC": "Spain", "EE": "Spain",
        "CT": "Portugal", "CS": "Portugal", "CU": "Azores",
        "SP": "Poland", "SQ": "Poland", "SN": "Poland", "SO": "Poland", "3Z": "Poland",
        "HA": "Hungary", "HG": "Hungary", "OK": "Czech Rep.", "OL": "Czech Rep.",
        "OM": "Slovak Rep.", "LZ": "Bulgaria",
        "UR": "Ukraine", "US": "Ukraine", "UT": "Ukraine", "UX": "Ukraine", "UY": "Ukraine",
        "UA": "Russia", "RU": "Russia", "RV": "Russia", "RW": "Russia", "RA": "Russia",
        "OE": "Austria", "ON": "Belgium", "OO": "Belgium", "OR": "Belgium", "OT": "Belgium",
        "PA": "Netherlands", "PB": "Netherlands", "PD": "Netherlands", "PE": "Netherlands",
        "OZ": "Denmark", "OU": "Denmark", "5Q": "Denmark",
        "SM": "Sweden", "SA": "Sweden", "SB": "Sweden", "SK": "Sweden",
        "LA": "Norway", "LB": "Norway", "LC": "Norway",
        "OH": "Finland", "OF": "Finland", "OG": "Finland", "OI": "Finland",
        "ES": "Estonia", "YL": "Latvia", "LY": "Lithuania", "9A": "Croatia",
        "S5": "Slovenia", "S51": "Slovenia", "S52": "Slovenia", "S57": "Slovenia",
        "E7": "Bosnia", "Z3": "N. Macedonia", "Z6": "Kosovo", "ZA": "Albania",
        "SV": "Greece", "SW": "Greece", "SX": "Greece", "SY": "Greece",
        "TA": "Turkey", "TC": "Turkey", "YM": "Turkey", "4X": "Israel", "4Z": "Israel",
        "SU": "Egypt", "CN": "Morocco", "7X": "Algeria", "3V": "Tunisia",
        "ZS": "South Africa", "ZR": "South Africa", "ZU": "South Africa",
        "W": "USA", "K": "USA", "N": "USA", "AA": "USA", "AB": "USA", "AC": "USA",
        "AD": "USA", "AE": "USA", "AF": "USA", "AG": "USA", "AI": "USA", "AK": "USA",
        "KH6": "Hawaii", "KL7": "Alaska", "KP4": "Puerto Rico",
        "VE": "Canada", "VA": "Canada", "VY": "Canada", "VO": "Canada",
        "XE": "Mexico", "XA": "Mexico", "4A": "Mexico",
        "PY": "Brazil", "PP": "Brazil", "PR": "Brazil", "PS": "Brazil", "PT": "Brazil", "PU": "Brazil",
        "LU": "Argentina", "LW": "Argentina", "LO": "Argentina",
        "CE": "Chile", "CA": "Chile", "XQ": "Chile",
        "JA": "Japan", "JH": "Japan", "JR": "Japan", "JE": "Japan", "JF": "Japan",
        "JG": "Japan", "JI": "Japan", "JJ": "Japan", "JK": "Japan", "JL": "Japan",
        "BY": "China", "BA": "China", "BD": "China", "BG": "China", "BI": "China",
        "HL": "S. Korea", "DS": "S. Korea", "6K": "S. Korea",
        "DU": "Philippines", "DX": "Philippines", "HS": "Thailand", "E2": "Thailand",
        "VK": "Australia", "AX": "Australia", "ZL": "New Zealand", "ZM": "New Zealand",
        "VU": "India", "AT": "India", "VT": "India", "AP": "Pakistan",
        "A4": "Oman", "A6": "UAE", "A7": "Qatar", "A9": "Bahrain",
        "9K": "Kuwait", "HZ": "Saudi Arabia", "7Z": "Saudi Arabia",
        "EK": "Armenia", "4J": "Azerbaijan", "4L": "Georgia",
        "UN": "Kazakhstan", "JT": "Mongolia", "XV": "Vietnam", "3W": "Vietnam",
        "TF": "Iceland", "JW": "Svalbard", "OX": "Greenland", "OY": "Faroe Is.",
        "T7": "San Marino", "3A": "Monaco", "C3": "Andorra", "HV": "Vatican",
        "9H": "Malta", "5B": "Cyprus", "4O": "Montenegro",
    }

    @staticmethod
    def lookup(call):
        call = call.upper().strip().split("/")[0]
        for n in range(min(4, len(call)), 0, -1):
            p = call[:n]
            if p in DXCC.DB:
                return DXCC.DB[p], p
        if call and call[0] in DXCC.DB:
            return DXCC.DB[call[0]], call[0]
        return "Unknown", call[:2] if len(call) >= 2 else call

    @staticmethod
    def prefix(call):
        _, p = DXCC.lookup(call)
        return p


FREQ_MAP = {
    (1800, 2000): "160m", (3500, 3800): "80m", (5351, 5367): "60m",
    (7000, 7200): "40m", (10100, 10150): "30m", (14000, 14350): "20m",
    (18068, 18168): "17m", (21000, 21450): "15m", (24890, 24990): "12m",
    (28000, 29700): "10m", (50000, 54000): "6m", (144000, 148000): "2m",
    (430000, 440000): "70cm", (1240000, 1300000): "23cm",
}

BAND_FREQ = {
    "160m": 1850, "80m": 3700, "60m": 5355, "40m": 7100, "30m": 10120,
    "20m": 14200, "17m": 18120, "15m": 21200, "12m": 24940, "10m": 28500,
    "6m": 50150, "2m": 145000, "70cm": 432200, "23cm": 1296200,
}

RST_DEFAULTS = {"SSB": "59", "AM": "59", "FM": "59", "CW": "599", "RTTY": "599", "PSK31": "599", "DIGI": "599", "FT8": "-10", "FT4": "-10", "JT65": "-15", "SSTV": "59"}


def freq2band(f):
    try:
        f = float(f)
        for (lo, hi), b in FREQ_MAP.items():
            if lo <= f <= hi:
                return b
    except:
        pass
    return None


BANDS_HF = ["160m", "80m", "60m", "40m", "30m", "20m", "17m", "15m", "12m", "10m"]
BANDS_VHF = ["6m", "2m"]
BANDS_UHF = ["70cm", "23cm"]
BANDS_ALL = BANDS_HF + BANDS_VHF + BANDS_UHF
MODES_ALL = ["SSB", "CW", "DIGI", "FT8", "FT4", "RTTY", "AM", "FM", "PSK31", "SSTV", "JT65"]
SCORING_MODES = ["none", "per_qso", "per_band", "maraton", "multiplier", "distance", "custom"]
CONTEST_TYPES = ["Simplu", "Maraton", "Stafeta", "YO", "DX", "VHF", "UHF", "Field Day", "Sprint", "QSO Party", "SOTA", "POTA", "Custom"]
YO_COUNTIES = ["AB", "AR", "AG", "BC", "BH", "BN", "BT", "BV", "BR", "BZ", "CS", "CL", "CJ", "CT", "CV", "DB", "DJ", "GL", "GR", "GJ", "HR", "HD", "IL", "IS", "IF", "MM", "MH", "MS", "NT", "OT", "PH", "SM", "SJ", "SB", "SV", "TR", "TM", "TL", "VS", "VL", "VN", "B"]

T = {
    "ro": {
        "app_title": "YO Log PRO v16.0 FINAL", "call": "Indicativ", "band": "Bandă", "mode": "Mod",
        "rst_s": "RST S", "rst_r": "RST R", "serial_s": "Nr S", "serial_r": "Nr R",
        "freq": "Frecv (kHz)", "note": "Notă/Locator", "log": "LOG", "update": "ACTUALIZEAZĂ",
        "search": "🔍 Caută", "reset": "Reset", "settings": "⚙ Setări",
        "stats": "📊 Statistici", "validate": "✅ Validează", "export": "📤 Export",
        "import_log": "📥 Import", "delete": "Șterge", "backup": "💾 Backup",
        "online": "Online UTC", "offline": "Manual", "category": "Categorie", "county": "Județ",
        "req_st": "Stații Obligatorii", "worked": "Stații Lucrate", "total_score": "Scor Total",
        "val_result": "Validare", "date_l": "Dată:", "time_l": "Oră:", "manual": "Manual",
        "confirm_del": "Confirmare", "confirm_del_t": "Sigur ștergeți?",
        "bak_ok": "Backup creat!", "bak_err": "Eroare backup!",
        "exit_t": "Ieșire", "exit_m": "Salvați înainte de ieșire?",
        "help": "Ajutor", "about": "Despre", "save": "Salvează", "close": "Închide",
        "credits": "Dezvoltat de:\nArdei Constantin-Cătălin (YO8ACR)\nyo8acr@gmail.com",
        "usage": "Ctrl+F=Caută  Ctrl+Z=Undo  Ctrl+S=Save  F2=Bandă+  F3=Mod+  Enter=LOG",
        "edit_qso": "Editează", "delete_qso": "Șterge", "data": "Data", "ora": "Ora",
        "sel_fmt": "Format:", "cancel": "Anulează", "exp_ok": "Export reușit!", "error": "Eroare",
        "sett_ok": "Setări salvate!", "locator": "Locator:", "address": "Adresă:",
        "font_size": "Font:", "station_info": "Info Stație:",
        "contest_mgr": "Manager Concursuri", "contests": "Concursuri",
        "add_c": "➕ Adaugă", "edit_c": "✏ Editează", "del_c": "🗑 Șterge", "dup_c": "📋 Duplică",
        "c_name": "Nume Concurs:", "c_type": "Tip:", "sc_mode": "Punctare:",
        "cats": "Categorii:", "a_bands": "Benzi:", "a_modes": "Moduri:",
        "req_st_c": "Stații Obligatorii:", "sp_sc": "Punctare Specială:",
        "ppq": "Puncte/QSO:", "min_qso": "Min QSO:", "use_serial": "Nr. Seriale",
        "use_county": "Județ", "county_list": "Județe:", "no_sel": "Neselectat!",
        "del_c_conf": "Ștergeți '{}'?", "c_saved": "Salvat!", "c_del": "Șters!",
        "c_exists": "ID existent!", "c_default": "Protejat!", "c_id": "ID Concurs:",
        "mults": "Multiplicatori:", "band_pts": "Puncte/Bandă:", "nr": "Nr.", "pts": "Pt",
        "imp_c": "📥 Import", "exp_c": "📤 Export",
        "dup_warn": "⚠ Duplicat!", "dup_msg": "{} pe {} {}!\nQSO #{}\n\nAdăugați?",
        "search_t": "Căutare", "search_l": "Caută:", "results": "Rezultate",
        "no_res": "Nimic găsit.", "undo": "↩ Undo", "undo_ok": "Anulat.",
        "undo_empty": "Nimic de anulat.", "rate": "QSO/h", "timer": "⏱ Timer",
        "timer_t": "Timer", "timer_start": "▶ Start", "timer_stop": "⏸ Stop",
        "timer_reset": "⏹ Reset", "elapsed": "Scurs:", "remaining": "Rămas:",
        "dur_h": "Durată (h):", "band_sum": "Benzi", "distance": "Dist",
        "country": "Țara", "utc": "UTC", "autosaved": "Salvat",
        "sounds": "Sunete", "en_sounds": "Activează sunete",
        "qso_pts": "Puncte QSO", "mult_c": "Multiplicatori", "new_mult": "✦ MULT NOU!",
        "op": "Operator:", "power": "Putere (W):", "f_band": "Bandă:", "f_mode": "Mod:",
        "all": "Toate", "clear_log": "🗑 Golire", "clear_conf": "Goliți COMPLET logul?\nIREVERSIBIL!",
        "wb": "Lucrat", "imp_adif": "Import ADIF", "imp_csv": "Import CSV",
        "imp_ok": "Importate {} QSO!", "imp_err": "Eroare import!",
        "qso_total": "Total QSO", "unique": "Unice", "countries": "Țări", "print_log": "🖨 Print",
        "verify": "Verificare log", "verify_ok": "Log integru: {} QSO, hash: {}",
        "score_f": "Scor", "worked_all": "Status Complet", "worked_x": "Lucrate: {}/{}", "missing_x": "Lipsesc: {}",
    },
    "en": {
        "app_title": "YO Log PRO v16.0 FINAL", "call": "Callsign", "band": "Band", "mode": "Mode",
        "rst_s": "RST S", "rst_r": "RST R", "serial_s": "Nr S", "serial_r": "Nr R",
        "freq": "Freq (kHz)", "note": "Note/Locator", "log": "LOG", "update": "UPDATE",
        "search": "🔍 Search", "reset": "Reset", "settings": "⚙ Settings",
        "stats": "📊 Stats", "validate": "✅ Validate", "export": "📤 Export",
        "import_log": "📥 Import", "delete": "Delete", "backup": "💾 Backup",
        "online": "Online UTC", "offline": "Manual", "category": "Category", "county": "County",
        "req_st": "Required Stations", "worked": "Stations Worked", "total_score": "Total Score",
        "val_result": "Validation", "date_l": "Date:", "time_l": "Time:", "manual": "Manual",
        "confirm_del": "Confirm", "confirm_del_t": "Delete selected?",
        "bak_ok": "Backup created!", "bak_err": "Backup error!",
        "exit_t": "Exit", "exit_m": "Save before exit?",
        "help": "Help", "about": "About", "save": "Save", "close": "Close",
        "credits": "Developed by:\nArdei Constantin-Cătălin (YO8ACR)\nyo8acr@gmail.com",
        "usage": "Ctrl+F=Search  Ctrl+Z=Undo  Ctrl+S=Save  F2=Band+  F3=Mode+  Enter=LOG",
        "edit_qso": "Edit", "delete_qso": "Delete", "data": "Date", "ora": "Time",
        "sel_fmt": "Format:", "cancel": "Cancel", "exp_ok": "Export done!", "error": "Error",
        "sett_ok": "Settings saved!", "locator": "Locator:", "address": "Address:",
        "font_size": "Font:", "station_info": "Station Info:",
        "contest_mgr": "Contest Manager", "contests": "Contests",
        "add_c": "➕ Add", "edit_c": "✏ Edit", "del_c": "🗑 Delete", "dup_c": "📋 Duplicate",
        "c_name": "Contest Name:", "c_type": "Type:", "sc_mode": "Scoring:",
        "cats": "Categories:", "a_bands": "Bands:", "a_modes": "Modes:",
        "req_st_c": "Required Stations:", "sp_sc": "Special Scoring:",
        "ppq": "Points/QSO:", "min_qso": "Min QSO:", "use_serial": "Serial Numbers",
        "use_county": "County", "county_list": "Counties:", "no_sel": "Not selected!",
        "del_c_conf": "Delete '{}'?", "c_saved": "Saved!", "c_del": "Deleted!",
        "c_exists": "ID exists!", "c_default": "Protected!", "c_id": "Contest ID:",
        "mults": "Multipliers:", "band_pts": "Band Points:", "nr": "Nr.", "pts": "Pt",
        "imp_c": "📥 Import", "exp_c": "📤 Export",
        "dup_warn": "⚠ Duplicate!", "dup_msg": "{} on {} {}!\nQSO #{}\n\nAdd anyway?",
        "search_t": "Search", "search_l": "Search:", "results": "Results",
        "no_res": "No results.", "undo": "↩ Undo", "undo_ok": "Undone.",
        "undo_empty": "Nothing to undo.", "rate": "QSO/h", "timer": "⏱ Timer",
        "timer_t": "Timer", "timer_start": "▶ Start", "timer_stop": "⏸ Stop",
        "timer_reset": "⏹ Reset", "elapsed": "Elapsed:", "remaining": "Remaining:",
        "dur_h": "Duration (h):", "band_sum": "Bands", "distance": "Dist",
        "country": "Country", "utc": "UTC", "autosaved": "Saved",
        "sounds": "Sounds", "en_sounds": "Enable sounds",
        "qso_pts": "QSO Points", "mult_c": "Multipliers", "new_mult": "✦ NEW MULT!",
        "op": "Operator:", "power": "Power (W):", "f_band": "Band:", "f_mode": "Mode:",
        "all": "All", "clear_log": "🗑 Clear", "clear_conf": "Clear ENTIRE log?\nIRREVERSIBLE!",
        "wb": "Worked", "imp_adif": "Import ADIF", "imp_csv": "Import CSV",
        "imp_ok": "Imported {} QSOs!", "imp_err": "Import error!",
        "qso_total": "Total QSO", "unique": "Unique", "countries": "Countries", "print_log": "🖨 Print",
        "verify": "Verify Log", "verify_ok": "Log OK: {} QSOs, hash: {}",
        "score_f": "Score", "worked_all": "Completion Status", "worked_x": "Worked: {}/{}", "missing_x": "Missing: {}",
    }
}

DEFAULT_CONTESTS = {
    "simplu": {"name_ro": "Log Simplu", "name_en": "Simple Log", "contest_type": "Simplu", "categories": ["Individual"], "scoring_mode": "none", "points_per_qso": 1, "min_qso": 0, "allowed_bands": list(BANDS_ALL), "allowed_modes": list(MODES_ALL), "required_stations": [], "special_scoring": {}, "use_serial": False, "use_county": False, "county_list": [], "multiplier_type": "none", "band_points": {}, "is_default": True},
    "maraton": {"name_ro": "Maraton", "name_en": "Marathon", "contest_type": "Maraton", "categories": ["A. Seniori YO", "B. YL", "C. Juniori YO", "D. Club", "E. DX", "F. Receptori"], "scoring_mode": "maraton", "points_per_qso": 1, "min_qso": 100, "allowed_bands": BANDS_HF + BANDS_VHF, "allowed_modes": list(MODES_ALL), "required_stations": [], "special_scoring": {}, "use_serial": False, "use_county": True, "county_list": list(YO_COUNTIES), "multiplier_type": "county", "band_points": {}, "is_default": False},
    "yo-dx-hf": {"name_ro": "YO DX HF Contest", "name_en": "YO DX HF Contest", "contest_type": "DX", "categories": ["A. SO AB High", "B. SO AB Low", "C. SO SB"], "scoring_mode": "per_band", "points_per_qso": 1, "min_qso": 0, "allowed_bands": ["160m", "80m", "40m", "20m", "15m", "10m"], "allowed_modes": ["SSB", "CW"], "required_stations": [], "special_scoring": {}, "use_serial": True, "use_county": True, "county_list": list(YO_COUNTIES), "multiplier_type": "dxcc", "band_points": {"160m": 4, "80m": 3, "40m": 2, "20m": 1, "15m": 1, "10m": 2}, "is_default": False},
}

DEFAULT_CFG = {"call": "YO8ACR", "loc": "KN37", "jud": "NT", "addr": "", "cat": 0, "fs": 11, "contest": "simplu", "county": "NT", "lang": "ro", "manual_dt": False, "sounds": True, "op_name": "", "power": "100", "win_geo": ""}

TH = {"bg": "#0d1117", "fg": "#e6edf3", "accent": "#1f6feb", "entry_bg": "#161b22", "header_bg": "#010409", "btn_bg": "#21262d", "btn_fg": "#f0f6fc", "led_on": "#3fb950", "led_off": "#f85149", "warn": "#d29922", "ok": "#3fb950", "err": "#f85149", "dup_bg": "#3d1a1a", "mult_bg": "#1a3d1a", "spec_bg": "#1a1a3d", "alt": "#0d1f2d", "gold": "#ffd700", "cyan": "#58a6ff"}


class DM:
    @staticmethod
    def fp(fn):
        return os.path.join(get_data_dir(), fn)

    @staticmethod
    def save(fn, d):
        p = DM.fp(fn)
        t = p + ".tmp"
        try:
            with open(t, "w", encoding="utf-8") as f:
                json.dump(d, f, indent=2, ensure_ascii=False)
            if os.path.exists(p):
                os.remove(p)
            os.rename(t, p)
            return True
        except:
            try:
                os.remove(t)
            except:
                pass
            return False

    @staticmethod
    def load(fn, default=None):
        p = DM.fp(fn)
        if not os.path.exists(p):
            if default is not None:
                DM.save(fn, default)
            return copy.deepcopy(default) if default else {}
        try:
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return copy.deepcopy(default) if default else {}

    @staticmethod
    def log_fn(cid):
        return f"log_{re.sub(r'[^a-zA-Z0-9_-]', '_', cid)}.json"

    @staticmethod
    def load_log(cid):
        return DM.load(DM.log_fn(cid), [])

    @staticmethod
    def save_log(cid, d):
        return DM.save(DM.log_fn(cid), d)

    @staticmethod
    def backup(cid, d):
        try:
            bd = os.path.join(get_data_dir(), "backups")
            os.makedirs(bd, exist_ok=True)
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            sid = re.sub(r'[^a-zA-Z0-9_-]', '_', cid)
            bf = os.path.join(bd, f"log_{sid}_{ts}.json")
            with open(bf, "w", encoding="utf-8") as f:
                json.dump(d, f, indent=2, ensure_ascii=False)
            bks = sorted(Path(bd).glob(f"log_{sid}_*.json"))
            while len(bks) > 50:
                bks[0].unlink()
                bks.pop(0)
            return True
        except:
            return False


class L:
    _c = "ro"

    @classmethod
    def s(cls, l):
        if l in T:
            cls._c = l

    @classmethod
    def g(cls):
        return cls._c

    @classmethod
    def t(cls, k):
        return T.get(cls._c, {}).get(k, k)


class Score:
    @staticmethod
    def qso(q, rules, cfg=None):
        if not rules:
            return 1
        sm = rules.get("scoring_mode", "none")
        if sm == "none":
            return 0
        call = q.get("c", "").upper()
        sp = rules.get("special_scoring", {})
        if call in sp:
            try:
                return int(sp[call])
            except:
                pass
        if sm == "per_qso":
            return rules.get("points_per_qso", 1)
        elif sm == "per_band":
            bp = rules.get("band_points", {})
            return int(bp.get(q.get("b", ""), rules.get("points_per_qso", 1)))
        elif sm == "distance":
            n = q.get("n", "").strip()
            ml = (cfg or {}).get("loc", "")
            if Loc.valid(n) and Loc.valid(ml):
                return max(1, int(Loc.dist(ml, n)))
        return rules.get("points_per_qso", 1)

    @staticmethod
    def mults(data, rules):
        mt = rules.get("multiplier_type", "none")
        if mt == "none":
            return 1, set()
        ms = set()
        for q in data:
            n = q.get("n", "").upper().strip()
            c = q.get("c", "").upper()
            b = q.get("b", "")
            if mt == "county":
                for co in rules.get("county_list", []):
                    if re.search(r'\b' + re.escape(co.upper()) + r'\b', n):
                        ms.add(co.upper())
                        break
            elif mt == "dxcc":
                ms.add(DXCC.prefix(c))
            elif mt == "band":
                ms.add(b)
            elif mt == "grid":
                if len(n) >= 4 and Loc.valid(n[:4]):
                    ms.add(n[:4])
        return max(1, len(ms)), ms

    @staticmethod
    def total(data, rules, cfg=None):
        if not data or not rules:
            return 0, 0, 0
        if rules.get("scoring_mode", "none") == "none":
            return 0, 0, 0
        qp = sum(Score.qso(q, rules, cfg) for q in data)
        mc, _ = Score.mults(data, rules)
        if rules.get("multiplier_type", "none") != "none":
            return qp, mc, qp * mc
        return qp, mc, qp

    @staticmethod
    def is_dup(data, call, band, mode, edit_idx=None):
        cu = call.upper()
        for i, q in enumerate(data):
            if edit_idx is not None and i == edit_idx:
                continue
            if q.get("c", "").upper() == cu and q.get("b") == band and q.get("m") == mode:
                return True, i
        return False, -1

    @staticmethod
    def is_new_mult(data, qso, rules):
        mt = rules.get("multiplier_type", "none")
        if mt == "none":
            return False
        _, ex = Score.mults(data, rules)
        n = qso.get("n", "").upper().strip()
        c = qso.get("c", "").upper()
        nm = None
        if mt == "county":
            for co in rules.get("county_list", []):
                if re.search(r'\b' + re.escape(co.upper()) + r'\b', n):
                    nm = co.upper()
                    break
        elif mt == "dxcc":
            nm = DXCC.prefix(c)
        elif mt == "band":
            nm = qso.get("b", "")
        elif mt == "grid":
            if len(n) >= 4 and Loc.valid(n[:4]):
                nm = n[:4]
        return nm is not None and nm not in ex

    @staticmethod
    def validate(data, rules, cfg=None):
        if not data:
            return False, "Log gol / Empty log", 0
        if not rules:
            return True, f"OK: {len(data)} QSO", len(data)
        msgs = []
        mq = rules.get("min_qso", 0)
        if mq > 0 and len(data) < mq:
            msgs.append(f"Min {mq} QSO, aveți {len(data)}")
        seen = set()
        dc = 0
        for q in data:
            k = (q.get("c", "").upper(), q.get("b"), q.get("m"))
            if k in seen:
                dc += 1
            seen.add(k)
        if dc:
            msgs.append(f"⚠ {dc} duplicate")
        if msgs:
            return False, "\n".join(msgs[:20]), 0
        _, _, tot = Score.total(data, rules, cfg)
        return True, f"✓ OK! {len(data)} QSO, Scor: {tot}", tot


class Importer:
    @staticmethod
    def parse_adif(text):
        qsos = []
        eoh = text.upper().find("<EOH>")
        if eoh >= 0:
            text = text[eoh + 5:]
        records = re.split(r'<EOR>', text, flags=re.IGNORECASE)
        for rec in records:
            rec = rec.strip()
            if not rec:
                continue
            fields = {}
            for m in re.finditer(r'<(\w+):(\d+)(?::[^>]*)?>(.{0,999}?)', rec, re.IGNORECASE | re.DOTALL):
                tag = m.group(1).upper()
                length = int(m.group(2))
                val = m.group(3)[:length]
                fields[tag] = val
            if "CALL" not in fields:
                continue
            q = {"c": fields.get("CALL", "").upper()}
            q["b"] = fields.get("BAND", "40m")
            q["m"] = fields.get("MODE", "SSB")
            q["s"] = fields.get("RST_SENT", "59")
            q["r"] = fields.get("RST_RCVD", "59")
            qd = fields.get("QSO_DATE", "")
            q["d"] = f"{qd[:4]}-{qd[4:6]}-{qd[6:8]}" if len(qd) == 8 else datetime.datetime.utcnow().strftime("%Y-%m-%d")
            qt = fields.get("TIME_ON", "")
            q["t"] = f"{qt[:2]}:{qt[2:4]}" if len(qt) >= 4 else "00:00"
            q["f"] = fields.get("FREQ", "")
            q["n"] = fields.get("GRIDSQUARE", fields.get("COMMENT", ""))
            q["ss"] = fields.get("STX", "")
            q["sr"] = fields.get("SRX", "")
            qsos.append(q)
        return qsos

    @staticmethod
    def parse_csv(text):
        qsos = []
        reader = csv.DictReader(io.StringIO(text))
        for row in reader:
            call = (row.get("Call") or row.get("CALL") or row.get("call") or row.get("Callsign") or "").upper().strip()
            if not call:
                continue
            q = {"c": call}
            q["b"] = row.get("Band") or row.get("BAND") or "40m"
            q["m"] = row.get("Mode") or row.get("MODE") or "SSB"
            q["s"] = row.get("RST_Sent") or row.get("RST_S") or "59"
            q["r"] = row.get("RST_Rcvd") or row.get("RST_R") or "59"
            q["d"] = row.get("Date") or row.get("DATE") or datetime.datetime.utcnow().strftime("%Y-%m-%d")
            q["t"] = row.get("Time") or row.get("TIME") or "00:00"
            q["f"] = row.get("Freq") or row.get("FREQ") or ""
            q["n"] = row.get("Note") or row.get("NOTE") or row.get("Comment") or ""
            qsos.append(q)
        return qsos

class ContestEditor(tk.Toplevel):
    def __init__(self, parent, cid=None, cdata=None, all_c=None):
        super().__init__(parent)
        self.result = None
        self.cid = cid
        self.new = cid is None
        self.all_c = all_c or {}
        self.d = copy.deepcopy(cdata) if cdata else {"name_ro": "", "name_en": "", "contest_type": "Simplu", "categories": ["Individual"], "scoring_mode": "none", "points_per_qso": 1, "min_qso": 0, "allowed_bands": list(BANDS_ALL), "allowed_modes": list(MODES_ALL), "required_stations": [], "special_scoring": {}, "use_serial": False, "use_county": False, "county_list": [], "multiplier_type": "none", "band_points": {}, "is_default": False}
        self.title(L.t("edit_c") if not self.new else L.t("add_c"))
        self.geometry("700x800")
        self.configure(bg=TH["bg"])
        self.transient(parent)
        self.grab_set()
        self._build()

    def _build(self):
        f = tk.Frame(self, bg=TH["bg"], padx=15, pady=10)
        f.pack(fill="both", expand=True)
        eo = {"bg": TH["entry_bg"], "fg": TH["fg"], "font": ("Consolas", 11), "insertbackground": TH["fg"]}
        lo = {"bg": TH["bg"], "fg": TH["fg"], "font": ("Consolas", 11)}
        r = 0
        self._e = {}
        if self.new:
            tk.Label(f, text=L.t("c_id"), **lo).grid(row=r, column=0, sticky="w", pady=3)
            self._e["id"] = tk.Entry(f, width=30, **eo)
            self._e["id"].grid(row=r, column=1, sticky="w", pady=3)
            r += 1
        for k, lb in [("name_ro", L.t("c_name") + " (RO)"), ("name_en", L.t("c_name") + " (EN)")]:
            tk.Label(f, text=lb, **lo).grid(row=r, column=0, sticky="w", pady=3)
            e = tk.Entry(f, width=40, **eo)
            e.insert(0, self.d.get(k, ""))
            e.grid(row=r, column=1, sticky="w", pady=3)
            self._e[k] = e
            r += 1
        tk.Label(f, text=L.t("c_type"), **lo).grid(row=r, column=0, sticky="w", pady=3)
        self._tv = tk.StringVar(value=self.d.get("contest_type", "Simplu"))
        ttk.Combobox(f, textvariable=self._tv, values=CONTEST_TYPES, state="readonly", width=18).grid(row=r, column=1, sticky="w", pady=3)
        r += 1
        tk.Label(f, text=L.t("sc_mode"), **lo).grid(row=r, column=0, sticky="w", pady=3)
        self._sv = tk.StringVar(value=self.d.get("scoring_mode", "none"))
        ttk.Combobox(f, textvariable=self._sv, values=SCORING_MODES, state="readonly", width=18).grid(row=r, column=1, sticky="w", pady=3)
        r += 1
        for k, lb in [("points_per_qso", L.t("ppq")), ("min_qso", L.t("min_qso"))]:
            tk.Label(f, text=lb, **lo).grid(row=r, column=0, sticky="w", pady=3)
            e = tk.Entry(f, width=10, **eo)
            e.insert(0, str(self.d.get(k, 0)))
            e.grid(row=r, column=1, sticky="w", pady=3)
            self._e[k] = e
            r += 1
        tk.Label(f, text=L.t("mults"), **lo).grid(row=r, column=0, sticky="w", pady=3)
        self._mv = tk.StringVar(value=self.d.get("multiplier_type", "none"))
        ttk.Combobox(f, textvariable=self._mv, values=["none", "county", "dxcc", "band", "grid"], state="readonly", width=18).grid(row=r, column=1, sticky="w", pady=3)
        r += 1
        self._serv = tk.BooleanVar(value=self.d.get("use_serial", False))
        tk.Checkbutton(f, text=L.t("use_serial"), variable=self._serv, bg=TH["bg"], fg=TH["fg"], selectcolor=TH["entry_bg"]).grid(row=r, column=0, columnspan=2, sticky="w", pady=3)
        r += 1
        self._couv = tk.BooleanVar(value=self.d.get("use_county", False))
        tk.Checkbutton(f, text=L.t("use_county"), variable=self._couv, bg=TH["bg"], fg=TH["fg"], selectcolor=TH["entry_bg"]).grid(row=r, column=0, columnspan=2, sticky="w", pady=3)
        r += 1
        bf = tk.Frame(f, bg=TH["bg"])
        bf.grid(row=r, column=0, columnspan=2, pady=15)
        tk.Button(bf, text=L.t("save"), command=self._save, bg=TH["accent"], fg="white", font=("Consolas", 12, "bold"), width=12).pack(side="left", padx=8)
        tk.Button(bf, text=L.t("cancel"), command=self.destroy, bg=TH["btn_bg"], fg="white", font=("Consolas", 12), width=12).pack(side="left", padx=8)

    def _save(self):
        if self.new:
            cid = self._e["id"].get().strip().lower().replace(" ", "-")
            if not cid or cid in self.all_c:
                messagebox.showerror(L.t("error"), L.t("c_exists") if cid in self.all_c else "ID!")
                return
            self.cid = cid
        self.d["name_ro"] = self._e["name_ro"].get().strip()
        self.d["name_en"] = self._e["name_en"].get().strip()
        self.d["contest_type"] = self._tv.get()
        self.d["scoring_mode"] = self._sv.get()
        try:
            self.d["points_per_qso"] = int(self._e["points_per_qso"].get())
        except:
            self.d["points_per_qso"] = 1
        try:
            self.d["min_qso"] = int(self._e["min_qso"].get())
        except:
            self.d["min_qso"] = 0
        self.d["multiplier_type"] = self._mv.get()
        self.d["use_serial"] = self._serv.get()
        self.d["use_county"] = self._couv.get()
        self.d["is_default"] = False
        self.result = (self.cid, self.d)
        self.destroy()


class ContestMgr(tk.Toplevel):
    def __init__(self, parent, contests):
        super().__init__(parent)
        self.c = copy.deepcopy(contests)
        self.result = None
        self.title(L.t("contest_mgr"))
        self.geometry("700x450")
        self.configure(bg=TH["bg"])
        self.transient(parent)
        self.grab_set()
        self._build()
        self._fill()

    def _build(self):
        tb = tk.Frame(self, bg=TH["header_bg"], pady=5)
        tb.pack(fill="x")
        for txt, cmd in [(L.t("add_c"), self._add), (L.t("edit_c"), self._edit), (L.t("del_c"), self._del)]:
            tk.Button(tb, text=txt, command=cmd, bg=TH["accent"], fg="white", font=("Consolas", 10)).pack(side="left", padx=3)
        tf = tk.Frame(self, bg=TH["bg"])
        tf.pack(fill="both", expand=True, padx=6, pady=3)
        cols = ("id", "name", "type", "sc")
        self.tree = ttk.Treeview(tf, columns=cols, show="headings", selectmode="browse")
        for c, h, w in zip(cols, ["ID", L.t("c_name"), L.t("c_type"), L.t("sc_mode")], [100, 200, 100, 100]):
            self.tree.heading(c, text=h)
            self.tree.column(c, width=w, anchor="center")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", lambda e: self._edit())
        bt = tk.Frame(self, bg=TH["bg"], pady=6)
        bt.pack(fill="x")
        tk.Button(bt, text=L.t("save"), command=self._onsave, bg=TH["ok"], fg="white", font=("Consolas", 12, "bold"), width=12).pack(side="left", padx=12)
        tk.Button(bt, text=L.t("cancel"), command=self.destroy, bg=TH["btn_bg"], fg="white", font=("Consolas", 12), width=12).pack(side="right", padx=12)

    def _fill(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for cid, cd in self.c.items():
            nm = cd.get("name_" + L.g(), cd.get("name_ro", cid))
            self.tree.insert("", "end", iid=cid, values=(cid, nm, cd.get("contest_type", "?"), cd.get("scoring_mode", "none")))

    def _sel(self):
        s = self.tree.selection()
        return s[0] if s else None

    def _add(self):
        d = ContestEditor(self, all_c=self.c)
        self.wait_window(d)
        if d.result:
            self.c[d.result[0]] = d.result[1]
            self._fill()

    def _edit(self):
        cid = self._sel()
        if not cid:
            return
        d = ContestEditor(self, cid=cid, cdata=self.c[cid], all_c=self.c)
        self.wait_window(d)
        if d.result:
            self.c[cid] = d.result[1]
            self._fill()

    def _del(self):
        cid = self._sel()
        if cid and not self.c.get(cid, {}).get("is_default") and messagebox.askyesno(L.t("confirm_del"), L.t("del_c_conf").format(cid)):
            del self.c[cid]
            self._fill()

    def _onsave(self):
        self.result = self.c
        self.destroy()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.cfg = DM.load("config.json", DEFAULT_CFG.copy())
        self.contests = DM.load("contests.json", DEFAULT_CONTESTS.copy())
        if "simplu" not in self.contests:
            self.contests["simplu"] = DEFAULT_CONTESTS["simplu"]
        if self.cfg.get("contest", "") not in self.contests:
            self.cfg["contest"] = "simplu"
        self.log = DM.load_log(self.cfg.get("contest", "simplu"))
        L.s(self.cfg.get("lang", "ro"))
        self.edit_idx = None
        self.ent = {}
        self.serial = len(self.log) + 1
        self.undo_stack = deque(maxlen=50)
        self.info_lbl = self.sc_lbl = self.clk = self.rate_lbl = None
        self.led_c = self.led = self.st_lbl = self.wb_lbl = self.log_btn = None
        self.tree = self.ctx = self.fb_v = self.fm_v = None
        self.cv = self.ccb = self.lang_v = self.man_v = self.cat_v = self.cou_v = None
        self._setup_win()
        self._setup_style()
        self._build_menu()
        self._build_ui()
        self._build_ctx()
        self._refresh()
        self.protocol("WM_DELETE_WINDOW", self._exit)
        self.bind('<Return>', lambda e: self._add_qso())
        self.bind('<Control-s>', lambda e: self._fsave())
        self.bind('<Control-z>', lambda e: self._undo())
        self.bind('<F2>', self._cycle_band)
        self.bind('<F3>', self._cycle_mode)
        self._tick_clock()
        self._tick_save()

    def _cc(self):
        return self.contests.get(self.cfg.get("contest", "simplu"), self.contests.get("simplu", {}))

    def _cid(self):
        return self.cfg.get("contest", "simplu")

    def _setup_win(self):
        self.title(L.t("app_title"))
        self.configure(bg=TH["bg"])
        self.geometry("1200x750")
        self.minsize(1000, 640)

    def _setup_style(self):
        self.fs = int(self.cfg.get("fs", 11))
        self.fn = ("Consolas", self.fs)
        self.fb = ("Consolas", self.fs, "bold")
        s = ttk.Style()
        try:
            s.theme_use('clam')
        except:
            pass
        s.configure("Treeview", background=TH["entry_bg"], foreground=TH["fg"], fieldbackground=TH["entry_bg"], font=self.fn, rowheight=22)
        s.configure("Treeview.Heading", background=TH["header_bg"], foreground=TH["fg"], font=self.fb)
        s.map("Treeview", background=[("selected", TH["accent"])])

    def _build_menu(self):
        mb = tk.Menu(self)
        self.config(menu=mb)
        cm = tk.Menu(mb, tearoff=0)
        mb.add_cascade(label=L.t("contests"), menu=cm)
        cm.add_command(label=L.t("contest_mgr"), command=self._mgr)
        hm = tk.Menu(mb, tearoff=0)
        mb.add_cascade(label=L.t("help"), menu=hm)
        hm.add_command(label=L.t("about"), command=self._about)
        hm.add_command(label="Exit", command=self._exit)

    def _build_ctx(self):
        self.ctx = Menu(self, tearoff=0)
        self.ctx.add_command(label=L.t("edit_qso"), command=self._edit_sel)
        self.ctx.add_command(label=L.t("delete_qso"), command=self._del_sel)

    def _build_ui(self):
        self._build_hdr()
        self._build_inp()
        self._build_flt()
        self._build_tree()
        self._build_btns()

    def _build_hdr(self):
        h = tk.Frame(self, bg=TH["header_bg"], pady=5)
        h.pack(fill="x")
        lf = tk.Frame(h, bg=TH["header_bg"])
        lf.pack(side="left", padx=10)
        self.led_c = tk.Canvas(lf, width=14, height=14, bg=TH["header_bg"], highlightthickness=0)
        self.led = self.led_c.create_oval(1, 1, 13, 13, fill=TH["led_on"], outline="")
        self.led_c.pack(side="left", padx=(0, 5))
        self.st_lbl = tk.Label(lf, text=L.t("online"), bg=TH["header_bg"], fg=TH["led_on"], font=self.fn)
        self.st_lbl.pack(side="left")
        self.info_lbl = tk.Label(lf, text="", bg=TH["header_bg"], fg=TH["fg"], font=self.fn)
        self.info_lbl.pack(side="left", padx=12)
        rf = tk.Frame(h, bg=TH["header_bg"])
        rf.pack(side="right", padx=10)
        self.clk = tk.Label(rf, text="UTC 00:00:00", bg=TH["header_bg"], fg=TH["gold"], font=("Consolas", 12, "bold"))
        self.clk.pack(side="right", padx=8)
        self.rate_lbl = tk.Label(rf, text="", bg=TH["header_bg"], fg=TH["ok"], font=("Consolas", 10))
        self.rate_lbl.pack(side="right", padx=8)
        self.lang_v = tk.StringVar(value=self.cfg.get("lang", "ro"))
        lc = ttk.Combobox(rf, textvariable=self.lang_v, values=["ro", "en"], state="readonly", width=4)
        lc.pack(side="right", padx=3)
        lc.bind("<<ComboboxSelected>>", self._on_lang)
        self.cv = tk.StringVar(value=self._cid())
        self.ccb = ttk.Combobox(rf, textvariable=self.cv, values=list(self.contests.keys()), state="readonly", width=15)
        self.ccb.pack(side="right", padx=3)
        self.ccb.bind("<<ComboboxSelected>>", self._on_cchange)
        self._upd_info()

    def _build_inp(self):
        ip = tk.Frame(self, bg=TH["bg"], pady=8)
        ip.pack(fill="x", padx=10)
        r1 = tk.Frame(ip, bg=TH["bg"])
        r1.pack(fill="x")
        cc = self._cc()
        cf = tk.Frame(r1, bg=TH["bg"])
        cf.pack(side="left", padx=3)
        tk.Label(cf, text=L.t("call"), bg=TH["bg"], fg=TH["fg"], font=self.fb).pack()
        self.ent["call"] = tk.Entry(cf, width=15, bg=TH["entry_bg"], fg=TH["gold"], font=("Consolas", self.fs + 2, "bold"), insertbackground=TH["fg"], justify="center")
        self.ent["call"].pack(ipady=3)
        self.ent["call"].bind("<KeyRelease>", self._on_call_key)
        self.wb_lbl = tk.Label(cf, text="", bg=TH["bg"], fg=TH["err"], font=("Consolas", 9))
        self.wb_lbl.pack()
        ff = tk.Frame(r1, bg=TH["bg"])
        ff.pack(side="left", padx=3)
        tk.Label(ff, text=L.t("freq"), bg=TH["bg"], fg=TH["fg"], font=self.fn).pack()
        self.ent["freq"] = tk.Entry(ff, width=9, bg=TH["entry_bg"], fg=TH["fg"], font=self.fn, insertbackground=TH["fg"], justify="center")
        self.ent["freq"].pack()
        self.ent["freq"].bind("<FocusOut>", self._on_freq_out)
        ab = cc.get("allowed_bands", BANDS_ALL)
        bf = tk.Frame(r1, bg=TH["bg"])
        bf.pack(side="left", padx=3)
        tk.Label(bf, text=L.t("band"), bg=TH["bg"], fg=TH["fg"], font=self.fn).pack()
        self.ent["band"] = ttk.Combobox(bf, values=ab, state="readonly", width=6, font=self.fn)
        self.ent["band"].set(ab[0] if ab else "40m")
        self.ent["band"].pack()
        self.ent["band"].bind("<<ComboboxSelected>>", self._on_band_change)
        am = cc.get("allowed_modes", MODES_ALL)
        mf = tk.Frame(r1, bg=TH["bg"])
        mf.pack(side="left", padx=3)
        tk.Label(mf, text=L.t("mode"), bg=TH["bg"], fg=TH["fg"], font=self.fn).pack()
        self.ent["mode"] = ttk.Combobox(mf, values=am, state="readonly", width=6, font=self.fn)
        self.ent["mode"].set(am[0] if am else "SSB")
        self.ent["mode"].pack()
        self.ent["mode"].bind("<<ComboboxSelected>>", self._on_mode_change)
        for k, lb in [("rst_s", L.t("rst_s")), ("rst_r", L.t("rst_r"))]:
            frame = tk.Frame(r1, bg=TH["bg"])
            frame.pack(side="left", padx=3)
            tk.Label(frame, text=lb, bg=TH["bg"], fg=TH["fg"], font=self.fn).pack()
            e = tk.Entry(frame, width=5, bg=TH["entry_bg"], fg=TH["fg"], font=self.fn, insertbackground=TH["fg"], justify="center")
            e.insert(0, RST_DEFAULTS.get(am[0] if am else "SSB", "59"))
            e.pack()
            self.ent[k] = e
        if cc.get("use_serial"):
            for k, lb in [("ss", L.t("serial_s")), ("sr", L.t("serial_r"))]:
                frame = tk.Frame(r1, bg=TH["bg"])
                frame.pack(side="left", padx=3)
                tk.Label(frame, text=lb, bg=TH["bg"], fg=TH["fg"], font=self.fn).pack()
                e = tk.Entry(frame, width=5, bg=TH["entry_bg"], fg=TH["fg"], font=self.fn, insertbackground=TH["fg"], justify="center")
                if k == "ss":
                    e.insert(0, str(self.serial))
                e.pack()
                self.ent[k] = e
        nf = tk.Frame(r1, bg=TH["bg"])
        nf.pack(side="left", padx=3)
        tk.Label(nf, text=L.t("note"), bg=TH["bg"], fg=TH["fg"], font=self.fn).pack()
        self.ent["note"] = tk.Entry(nf, width=13, bg=TH["entry_bg"], fg=TH["fg"], font=self.fn, insertbackground=TH["fg"], justify="center")
        self.ent["note"].pack()
        rbf = tk.Frame(r1, bg=TH["bg"])
        rbf.pack(side="left", padx=6)
        self.man_v = tk.BooleanVar(value=self.cfg.get("manual_dt", False))
        tk.Checkbutton(rbf, text=L.t("manual"), variable=self.man_v, bg=TH["bg"], fg=TH["fg"], selectcolor=TH["entry_bg"], command=self._tog_man).pack()
        self.log_btn = tk.Button(rbf, text=L.t("log"), command=self._add_qso, bg=TH["accent"], fg="white", font=self.fb, width=10)
        self.log_btn.pack(pady=1)
        tk.Button(rbf, text=L.t("reset"), command=self._clr, bg=TH["btn_bg"], fg=TH["btn_fg"], font=self.fn, width=10).pack(pady=1)
        r2 = tk.Frame(ip, bg=TH["bg"])
        r2.pack(fill="x", pady=(6, 0))
        tk.Label(r2, text=L.t("date_l"), bg=TH["bg"], fg=TH["fg"], font=self.fn).pack(side="left", padx=3)
        self.ent["date"] = tk.Entry(r2, width=11, bg=TH["entry_bg"], fg=TH["fg"], font=self.fn, justify="center", state="disabled")
        self.ent["date"].pack(side="left", padx=2)
        tk.Label(r2, text=L.t("time_l"), bg=TH["bg"], fg=TH["fg"], font=self.fn).pack(side="left", padx=3)
        self.ent["time"] = tk.Entry(r2, width=7, bg=TH["entry_bg"], fg=TH["fg"], font=self.fn, justify="center", state="disabled")
        self.ent["time"].pack(side="left", padx=2)
        now = datetime.datetime.utcnow()
        for k, v in [("date", now.strftime("%Y-%m-%d")), ("time", now.strftime("%H:%M"))]:
            self.ent[k].config(state="normal")
            self.ent[k].insert(0, v)
            self.ent[k].config(state="disabled")
        tk.Label(r2, text=L.t("category"), bg=TH["bg"], fg=TH["fg"], font=self.fn).pack(side="left", padx=(12, 3))
        cats = cc.get("categories", ["A"])
        self.cat_v = tk.StringVar(value=cats[0] if cats else "A")
        ttk.Combobox(r2, textvariable=self.cat_v, values=cats, state="readonly", width=20).pack(side="left", padx=2)

    def _build_flt(self):
        ff = tk.Frame(self, bg=TH["bg"])
        ff.pack(fill="x", padx=10, pady=(1, 0))
        tk.Label(ff, text=L.t("f_band"), bg=TH["bg"], fg=TH["fg"], font=("Consolas", 10)).pack(side="left")
        ab = [L.t("all")] + self._cc().get("allowed_bands", BANDS_ALL)
        self.fb_v = tk.StringVar(value=L.t("all"))
        fb_cb = ttk.Combobox(ff, textvariable=self.fb_v, values=ab, state="readonly", width=7)
        fb_cb.pack(side="left", padx=3)
        fb_cb.bind("<<ComboboxSelected>>", lambda e: self._refresh())
        tk.Label(ff, text=L.t("f_mode"), bg=TH["bg"], fg=TH["fg"], font=("Consolas", 10)).pack(side="left", padx=(8, 0))
        am2 = [L.t("all")] + self._cc().get("allowed_modes", MODES_ALL)
        self.fm_v = tk.StringVar(value=L.t("all"))
        fm_cb = ttk.Combobox(ff, textvariable=self.fm_v, values=am2, state="readonly", width=7)
        fm_cb.pack(side="left", padx=3)
        fm_cb.bind("<<ComboboxSelected>>", lambda e: self._refresh())
        self.sc_lbl = tk.Label(ff, text="", bg=TH["bg"], fg=TH["gold"], font=("Consolas", 11, "bold"))
        self.sc_lbl.pack(side="right", padx=8)

    def _build_tree(self):
        tf = tk.Frame(self, bg=TH["bg"])
        tf.pack(fill="both", expand=True, padx=10, pady=3)
        cc = self._cc()
        us = cc.get("use_serial", False)
        hs = cc.get("scoring_mode", "none") != "none"
        cols = ["nr", "call", "freq", "band", "mode", "rst_s", "rst_r"]
        hdrs = [L.t("nr"), L.t("call"), L.t("freq"), L.t("band"), L.t("mode"), L.t("rst_s"), L.t("rst_r")]
        wids = [38, 115, 75, 55, 55, 45, 45]
        if us:
            cols += ["ss", "sr"]
            hdrs += [L.t("serial_s"), L.t("serial_r")]
            wids += [45, 45]
        cols += ["note", "country", "date", "time"]
        hdrs += [L.t("note"), L.t("country"), L.t("data"), L.t("ora")]
        wids += [95, 95, 80, 50]
        if hs:
            cols.append("pts")
            hdrs.append(L.t("pts"))
            wids.append(50)
        self.tree = ttk.Treeview(tf, columns=cols, show="headings", selectmode="extended")
        for c, h, w in zip(cols, hdrs, wids):
            self.tree.heading(c, text=h)
            self.tree.column(c, width=w, anchor="center")
        self.tree.tag_configure("dup", background=TH["dup_bg"])
        self.tree.tag_configure("alt", background=TH["alt"])
        sb = ttk.Scrollbar(tf, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree.bind("<Double-1>", lambda e: self._edit_sel())
        self.tree.bind("<Button-3>", self._on_rclick)

    def _build_btns(self):
        bb = tk.Frame(self, bg=TH["bg"], pady=6)
        bb.pack(fill="x", padx=10)
        btns = [(L.t("settings"), self._settings, TH["warn"]), (L.t("contests"), self._mgr, "#E91E63"), (L.t("stats"), self._stats, "#3F51B5"), (L.t("validate"), self._validate, TH["ok"]), (L.t("export"), self._export_dlg, "#9C27B0"), (L.t("import_log"), self._import_menu, "#FF5722"), (L.t("undo"), self._undo, "#795548"), (L.t("backup"), self._bak, "#607D8B")]
        for txt, cmd, col in btns:
            tk.Button(bb, text=txt, command=cmd, bg=col, fg="white", font=("Consolas", 10), width=11).pack(side="left", padx=2)

    def _tick_clock(self):
        now = datetime.datetime.utcnow()
        if self.clk:
            self.clk.config(text=f"UTC {now.strftime('%H:%M:%S')}")
        self.after(1000, self._tick_clock)

    def _tick_save(self):
        DM.save_log(self._cid(), self.log)
        self.after(60000, self._tick_save)

    def _fsave(self):
        DM.save_log(self._cid(), self.log)
        DM.save("config.json", self.cfg)
        beep("success")

    def _upd_info(self):
        cc = self._cc()
        call = self.cfg.get("call", "NOCALL")
        nm = cc.get("name_" + L.g(), cc.get("name_ro", "?"))
        if self.info_lbl:
            self.info_lbl.config(text=f"{call} | {nm} | QSO: {len(self.log)}")
        if self.sc_lbl:
            qp, mc, tot = Score.total(self.log, cc, self.cfg)
            self.sc_lbl.config(text=f"Σ {tot}" if cc.get("scoring_mode", "none") != "none" else "")

    def _refresh(self):
        if not self.tree:
            return
        for i in self.tree.get_children():
            self.tree.delete(i)
        cc = self._cc()
        hs = cc.get("scoring_mode", "none") != "none"
        us = cc.get("use_serial", False)
        fb = self.fb_v.get() if self.fb_v else L.t("all")
        fm = self.fm_v.get() if self.fm_v else L.t("all")
        seen = set()
        for i, q in enumerate(self.log):
            b, m, c = q.get("b", ""), q.get("m", ""), q.get("c", "").upper()
            if fb != L.t("all") and b != fb:
                continue
            if fm != L.t("all") and m != fm:
                continue
            nr = len(self.log) - i
            tag = ()
            key = (c, b, m)
            if key in seen:
                tag = ("dup",)
            elif i % 2 == 0:
                tag = ("alt",)
            seen.add(key)
            country, _ = DXCC.lookup(c)
            vals = [nr, c, q.get("f", ""), b, m, q.get("s", "59"), q.get("r", "59")]
            if us:
                vals += [q.get("ss", ""), q.get("sr", "")]
            vals += [q.get("n", ""), country if country != "Unknown" else "", q.get("d", ""), q.get("t", "")]
            if hs:
                vals.append(Score.qso(q, cc, self.cfg))
            self.tree.insert("", "end", iid=str(i), values=vals, tags=tag)
        self._upd_info()

    def _get_dt(self):
        if self.man_v and self.man_v.get():
            return self.ent["date"].get().strip(), self.ent["time"].get().strip()
        now = datetime.datetime.utcnow()
        return now.strftime("%Y-%m-%d"), now.strftime("%H:%M")

    def _add_qso(self):
        call = self.ent["call"].get().upper().strip()
        if not call:
            return
        band, mode = self.ent["band"].get(), self.ent["mode"].get()
        dup, di = Score.is_dup(self.log, call, band, mode, self.edit_idx)
        if dup and not messagebox.askyesno(L.t("dup_warn"), L.t("dup_msg").format(call, band, mode, len(self.log) - di)):
            return
        ds, ts = self._get_dt()
        q = {"c": call, "b": band, "m": mode, "s": self.ent["rst_s"].get() or "59", "r": self.ent["rst_r"].get() or "59", "n": self.ent["note"].get(), "d": ds, "t": ts, "f": self.ent["freq"].get()}
        if "ss" in self.ent:
            q["ss"] = self.ent["ss"].get()
        if "sr" in self.ent:
            q["sr"] = self.ent["sr"].get()
        if self.edit_idx is not None:
            self.log[self.edit_idx] = q
            self.edit_idx = None
            self.log_btn.config(text=L.t("log"), bg=TH["accent"])
        else:
            self.log.insert(0, q)
            self.undo_stack.append(("add", 0, q))
            self.serial += 1
        self._clr()
        self._refresh()
        DM.save_log(self._cid(), self.log)

    def _clr(self):
        for k in ["call", "note", "freq"]:
            self.ent[k].delete(0, "end")
        if "ss" in self.ent:
            self.ent["ss"].delete(0, "end")
            self.ent["ss"].insert(0, str(self.serial))
        if "sr" in self.ent:
            self.ent["sr"].delete(0, "end")
        if self.wb_lbl:
            self.wb_lbl.config(text="")
        self.ent["call"].focus()

    def _edit_sel(self):
        sel = self.tree.selection()
        if not sel:
            return
        self.edit_idx = int(sel[0])
        q = self.log[self.edit_idx]
        self.ent["call"].delete(0, "end")
        self.ent["call"].insert(0, q.get("c", ""))
        self.ent["freq"].delete(0, "end")
        self.ent["freq"].insert(0, q.get("f", ""))
        self.ent["band"].set(q.get("b", "40m"))
        self.ent["mode"].set(q.get("m", "SSB"))
        self.ent["rst_s"].delete(0, "end")
        self.ent["rst_s"].insert(0, q.get("s", "59"))
        self.ent["rst_r"].delete(0, "end")
        self.ent["rst_r"].insert(0, q.get("r", "59"))
        self.ent["note"].delete(0, "end")
        self.ent["note"].insert(0, q.get("n", ""))
        self.log_btn.config(text=L.t("update"), bg=TH["warn"])

    def _del_sel(self):
        sel = self.tree.selection()
        if sel and messagebox.askyesno(L.t("confirm_del"), L.t("confirm_del_t")):
            for idx in sorted([int(x) for x in sel], reverse=True):
                self.undo_stack.append(("del", idx, self.log.pop(idx)))
            self._refresh()
            DM.save_log(self._cid(), self.log)

    def _undo(self):
        if not self.undo_stack:
            return
        act, idx, q = self.undo_stack.pop()
        if act == "add" and idx < len(self.log):
            self.log.pop(idx)
        elif act == "del":
            self.log.insert(idx, q)
        self._refresh()
        DM.save_log(self._cid(), self.log)

    def _on_call_key(self, e=None):
        c = self.ent["call"].get().upper()
        pos = self.ent["call"].index(tk.INSERT)
        self.ent["call"].delete(0, tk.END)
        self.ent["call"].insert(0, c)
        self.ent["call"].icursor(min(pos, len(c)))
        if len(c) >= 3 and self.wb_lbl:
            dup, _ = Score.is_dup(self.log, c, self.ent["band"].get(), self.ent["mode"].get(), self.edit_idx)
            self.wb_lbl.config(text=f"⚠ DUP" if dup else "", fg=TH["err"])

    def _on_freq_out(self, e=None):
        f = self.ent["freq"].get().strip()
        if f:
            b = freq2band(f)
            if b:
                self.ent["band"].set(b)

    def _on_band_change(self, e=None):
        b = self.ent["band"].get()
        if not self.ent["freq"].get().strip():
            self.ent["freq"].delete(0, "end")
            self.ent["freq"].insert(0, str(BAND_FREQ.get(b, "")))

    def _on_mode_change(self, e=None):
        m = self.ent["mode"].get()
        rst = RST_DEFAULTS.get(m, "59")
        for k in ("rst_s", "rst_r"):
            self.ent[k].delete(0, "end")
            self.ent[k].insert(0, rst)

    def _on_rclick(self, e):
        item = self.tree.identify_row(e.y)
        if item:
            self.tree.selection_set(item)
            self.ctx.post(e.x_root, e.y_root)

    def _on_lang(self, e):
        L.s(self.lang_v.get())
        self.cfg["lang"] = self.lang_v.get()
        DM.save("config.json", self.cfg)
        self._rebuild()

    def _on_cchange(self, e):
        DM.save_log(self._cid(), self.log)
        self.cfg["contest"] = self.cv.get()
        DM.save("config.json", self.cfg)
        self.log = DM.load_log(self._cid())
        self.serial = len(self.log) + 1
        self._rebuild()

    def _cycle_band(self, e=None):
        ab = self._cc().get("allowed_bands", BANDS_ALL)
        cur = self.ent["band"].get()
        idx = (ab.index(cur) + 1) % len(ab) if cur in ab else 0
        self.ent["band"].set(ab[idx])

    def _cycle_mode(self, e=None):
        am = self._cc().get("allowed_modes", MODES_ALL)
        cur = self.ent["mode"].get()
        idx = (am.index(cur) + 1) % len(am) if cur in am else 0
        self.ent["mode"].set(am[idx])
        self._on_mode_change()

    def _tog_man(self):
        m = self.man_v.get()
        self.ent["date"].config(state="normal" if m else "disabled")
        self.ent["time"].config(state="normal" if m else "disabled")
        if self.led_c:
            self.led_c.itemconfig(self.led, fill=TH["led_off"] if m else TH["led_on"])
        if self.st_lbl:
            self.st_lbl.config(text=L.t("offline") if m else L.t("online"), fg=TH["led_off"] if m else TH["led_on"])

    def _rebuild(self):
        for w in self.winfo_children():
            w.destroy()
        self.ent = {}
        self._build_menu()
        self._build_ui()
        self._build_ctx()
        self._refresh()

    def _mgr(self):
        d = ContestMgr(self, self.contests)
        self.wait_window(d)
        if d.result:
            self.contests = d.result
            DM.save("contests.json", self.contests)
            self._rebuild()

    def _about(self):
        d = tk.Toplevel(self)
        d.title(L.t("about"))
        d.geometry("450x300")
        d.configure(bg=TH["bg"])
        tk.Label(d, text="📻 YO Log PRO v16.0 FINAL", bg=TH["bg"], fg=TH["accent"], font=("Consolas", 16, "bold")).pack(pady=12)
        tk.Label(d, text=L.t("credits"), bg=TH["bg"], fg=TH["fg"], font=self.fn).pack(pady=8)
        tk.Label(d, text=L.t("usage"), bg=TH["bg"], fg=TH["fg"], font=("Consolas", 9)).pack(pady=6)
        tk.Button(d, text=L.t("close"), command=d.destroy, bg=TH["accent"], fg="white", width=12).pack(pady=10)

    def _settings(self):
        d = tk.Toplevel(self)
        d.title(L.t("settings"))
        d.geometry("400x380")
        d.configure(bg=TH["bg"])
        eo = {"bg": TH["entry_bg"], "fg": TH["fg"], "font": self.fn}
        es = {}
        for k, lb, v in [("call", L.t("call"), self.cfg.get("call", "")), ("loc", L.t("locator"), self.cfg.get("loc", "")), ("jud", L.t("county"), self.cfg.get("jud", "")), ("op_name", L.t("op"), self.cfg.get("op_name", "")), ("power", L.t("power"), self.cfg.get("power", "100"))]:
            tk.Label(d, text=lb, bg=TH["bg"], fg=TH["fg"]).pack(anchor="w", padx=15)
            e = tk.Entry(d, width=35, **eo)
            e.insert(0, v)
            e.pack(pady=2, padx=15)
            es[k] = e

        def save():
            for k in es:
                self.cfg[k] = es[k].get().upper().strip() if k in ["call", "loc", "jud"] else es[k].get().strip()
            DM.save("config.json", self.cfg)
            self._upd_info()
            d.destroy()

        tk.Button(d, text=L.t("save"), command=save, bg=TH["accent"], fg="white", width=12).pack(pady=15)

    def _stats(self):
        d = tk.Toplevel(self)
        d.title(L.t("stats"))
        d.geometry("500x400")
        d.configure(bg=TH["bg"])
        txt = tk.Text(d, bg=TH["entry_bg"], fg=TH["fg"], font=("Consolas", 11))
        txt.pack(fill="both", expand=True, padx=10, pady=10)
        cc = self._cc()
        txt.insert("end", f"📊 {L.t('stats')}\n\n")
        txt.insert("end", f"Total QSO: {len(self.log)}\n")
        txt.insert("end", f"Unique: {len({q.get('c', '').upper() for q in self.log})}\n\n")
        bc = Counter(q.get("b", "") for q in self.log)
        for b in sorted(bc.keys()):
            txt.insert("end", f"{b}: {bc[b]}\n")
        qp, mc, tot = Score.total(self.log, cc, self.cfg)
        txt.insert("end", f"\nScore: {tot}\n")
        txt.config(state="disabled")

    def _validate(self):
        ok, msg, _ = Score.validate(self.log, self._cc(), self.cfg)
        messagebox.showinfo(L.t("val_result"), msg) if ok else messagebox.showwarning(L.t("val_result"), msg)

    def _import_menu(self):
        d = tk.Toplevel(self)
        d.title(L.t("import_log"))
        d.geometry("250x140")
        d.configure(bg=TH["bg"])
        tk.Button(d, text="ADIF (.adi)", command=lambda: [d.destroy(), self._import_adif()], bg=TH["accent"], fg="white", width=20).pack(pady=8)
        tk.Button(d, text="CSV (.csv)", command=lambda: [d.destroy(), self._import_csv()], bg=TH["accent"], fg="white", width=20).pack(pady=8)

    def _import_adif(self):
        fp = filedialog.askopenfilename(filetypes=[("ADIF", "*.adi *.adif")])
        if fp:
            try:
                with open(fp, "r", encoding="utf-8", errors="replace") as f:
                    qsos = Importer.parse_adif(f.read())
                if qsos:
                    self.log.extend(qsos)
                    self._refresh()
                    DM.save_log(self._cid(), self.log)
                    messagebox.showinfo("OK", L.t("imp_ok").format(len(qsos)))
            except Exception as e:
                messagebox.showerror(L.t("error"), str(e))

    def _import_csv(self):
        fp = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if fp:
            try:
                with open(fp, "r", encoding="utf-8", errors="replace") as f:
                    qsos = Importer.parse_csv(f.read())
                if qsos:
                    self.log.extend(qsos)
                    self._refresh()
                    DM.save_log(self._cid(), self.log)
                    messagebox.showinfo("OK", L.t("imp_ok").format(len(qsos)))
            except Exception as e:
                messagebox.showerror(L.t("error"), str(e))

    def _export_dlg(self):
        d = tk.Toplevel(self)
        d.title(L.t("export"))
        d.geometry("250x180")
        d.configure(bg=TH["bg"])
        for txt, cmd in [("Cabrillo (.log)", lambda: self._exp_cab(d)), ("ADIF (.adi)", lambda: self._exp_adif(d)), ("CSV (.csv)", lambda: self._exp_csv(d))]:
            tk.Button(d, text=txt, command=cmd, bg=TH["accent"], fg="white", width=20).pack(pady=5)

    def _exp_cab(self, parent):
        try:
            my = self.cfg.get("call", "NOCALL")
            lines = ["START-OF-LOG: 3.0", f"CALLSIGN: {my}", f"GRID-LOCATOR: {self.cfg.get('loc', '')}", "CREATED-BY: YO Log PRO v16.0"]
            for q in self.log:
                freq = q.get("f", "") or str(BAND_FREQ.get(q.get("b", ""), 0))
                lines.append(f"QSO: {freq} {q['m']} {q['d']} {q['t']} {my} {q.get('s', '59')} {q['c']} {q.get('r', '59')}")
            lines.append("END-OF-LOG:")
            fn = f"cabrillo_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.log"
            with open(os.path.join(get_data_dir(), fn), "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            messagebox.showinfo(L.t("exp_ok"), f"→ {fn}")
            parent.destroy()
        except Exception as e:
            messagebox.showerror(L.t("error"), str(e))

    def _exp_adif(self, parent):
        try:
            lines = ["<ADIF_VER:5>3.1.0", "<PROGRAMID:14>YO_Log_PRO_v16", "<EOH>"]
            for q in self.log:
                r = f"<CALL:{len(q['c'])}>{q['c']}<BAND:{len(q['b'])}>{q['b']}<MODE:{len(q['m'])}>{q['m']}"
                dc = q.get('d', '').replace("-", "")
                r += f"<QSO_DATE:{len(dc)}>{dc}"
                tc = q.get('t', '').replace(":", "") + "00"
                r += f"<TIME_ON:{len(tc)}>{tc}"
                r += f"<RST_SENT:{len(q.get('s', '59'))}>{q.get('s', '59')}<RST_RCVD:{len(q.get('r', '59'))}>{q.get('r', '59')}<EOR>"
                lines.append(r)
            fn = f"adif_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.adi"
            with open(os.path.join(get_data_dir(), fn), "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            messagebox.showinfo(L.t("exp_ok"), f"→ {fn}")
            parent.destroy()
        except Exception as e:
            messagebox.showerror(L.t("error"), str(e))

    def _exp_csv(self, parent):
        try:
            fn = f"log_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv"
            with open(os.path.join(get_data_dir(), fn), "w", encoding="utf-8", newline='') as f:
                w = csv.writer(f)
                w.writerow(["Nr", "Date", "Time", "Call", "Freq", "Band", "Mode", "RST_S", "RST_R", "Note"])
                for i, q in enumerate(self.log):
                    w.writerow([len(self.log) - i, q.get('d', ''), q.get('t', ''), q.get('c', ''), q.get('f', ''), q.get('b', ''), q.get('m', ''), q.get('s', ''), q.get('r', ''), q.get('n', '')])
            messagebox.showinfo(L.t("exp_ok"), f"→ {fn}")
            parent.destroy()
        except Exception as e:
            messagebox.showerror(L.t("error"), str(e))

    def _bak(self):
        if DM.backup(self._cid(), self.log):
            messagebox.showinfo("OK", L.t("bak_ok"))
        else:
            messagebox.showerror(L.t("error"), L.t("bak_err"))

    def _exit(self):
        if messagebox.askyesno(L.t("exit_t"), L.t("exit_m")):
            DM.save_log(self._cid(), self.log)
            DM.save("config.json", self.cfg)
            DM.save("contests.json", self.contests)
            self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()
