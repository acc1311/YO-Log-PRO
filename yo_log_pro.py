#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YO Log PRO v17.0 — Professional Amateur Radio Contest Logger
Author : Ardei Constantin-Cătălin (YO8ACR)  yo8acr@gmail.com
Rewrite: clean architecture, zero-crash design, full feature set
"""

import os, sys, re, csv, copy, json, math, datetime, io, hashlib
from pathlib import Path
from collections import Counter, deque

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext

# ── optional sound (Windows only) ─────────────────────────────────────────
try:
    import winsound
    _HAS_SOUND = True
except ImportError:
    _HAS_SOUND = False


# ══════════════════════════════════════════════════════════════════════════════
#  UTILITIES
# ══════════════════════════════════════════════════════════════════════════════

def _data_dir():
    return os.path.dirname(sys.executable) if getattr(sys, "frozen", False) \
           else os.path.abspath(".")

def _beep(kind="info"):
    if not _HAS_SOUND:
        return
    codes = {"error": 0x10, "warn": 0x30, "ok": 0x40, "info": 0x0}
    try:
        winsound.MessageBeep(codes.get(kind, 0))
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════════════════════
#  LOCATOR / HAVERSINE
# ══════════════════════════════════════════════════════════════════════════════

class Loc:
    @staticmethod
    def to_ll(loc):
        """Maidenhead → (lat, lon).  Returns (None,None) on error."""
        try:
            s = loc.upper().strip()
            if len(s) < 4:
                return None, None
            lon = (ord(s[0]) - 65) * 20 - 180 + int(s[2]) * 2
            lat = (ord(s[1]) - 65) * 10 - 90  + int(s[3])
            if len(s) >= 6:
                lon += (ord(s[4]) - 65) * (2/24) + 1/24
                lat += (ord(s[5]) - 65) * (1/24) + .5/24
            else:
                lon += 1.0; lat += .5
            return lat, lon
        except Exception:
            return None, None

    @staticmethod
    def dist(a, b):
        la1, lo1 = Loc.to_ll(a);  la2, lo2 = Loc.to_ll(b)
        if None in (la1, lo1, la2, lo2):
            return 0
        R = 6371.0
        d1, d2 = math.radians(la2-la1), math.radians(lo2-lo1)
        x = math.sin(d1/2)**2 + math.cos(math.radians(la1)) \
            * math.cos(math.radians(la2)) * math.sin(d2/2)**2
        return round(R * 2 * math.atan2(math.sqrt(x), math.sqrt(1-x)), 1)

    @staticmethod
    def valid(s):
        s = s.upper().strip()
        if len(s) == 4:
            return s[:2].isalpha() and s[2:4].isdigit() \
                   and 'A' <= s[0] <= 'R' and 'A' <= s[1] <= 'R'
        if len(s) == 6:
            return s[:2].isalpha() and s[2:4].isdigit() and s[4:6].isalpha() \
                   and 'A' <= s[0] <= 'R' and 'A' <= s[1] <= 'R' \
                   and 'A' <= s[4] <= 'X' and 'A' <= s[5] <= 'X'
        return False


# ══════════════════════════════════════════════════════════════════════════════
#  DXCC DATABASE
# ══════════════════════════════════════════════════════════════════════════════

DXCC_DB = {
    "YO":"Romania","YP":"Romania","YQ":"Romania","YR":"Romania",
    "DL":"Germany","DJ":"Germany","DK":"Germany","DA":"Germany","DB":"Germany",
    "DC":"Germany","DD":"Germany","DF":"Germany","DG":"Germany","DH":"Germany","DM":"Germany",
    "G":"England","M":"England","2E":"England","GW":"Wales","GM":"Scotland",
    "GI":"N.Ireland","GD":"Isle of Man","GJ":"Jersey","GU":"Guernsey",
    "F":"France","TM":"France","HB9":"Switzerland","HB":"Switzerland",
    "I":"Italy","IK":"Italy","IZ":"Italy","IW":"Italy","IN3":"Italy",
    "EA":"Spain","EB":"Spain","EC":"Spain","EE":"Spain",
    "CT":"Portugal","CS":"Portugal","CU":"Azores",
    "SP":"Poland","SQ":"Poland","SN":"Poland","SO":"Poland","3Z":"Poland",
    "HA":"Hungary","HG":"Hungary","OK":"Czech Rep.","OL":"Czech Rep.",
    "OM":"Slovak Rep.","LZ":"Bulgaria",
    "UR":"Ukraine","US":"Ukraine","UT":"Ukraine","UX":"Ukraine","UY":"Ukraine",
    "UA":"Russia","RU":"Russia","RV":"Russia","RW":"Russia","RA":"Russia",
    "OE":"Austria","ON":"Belgium","OO":"Belgium","OR":"Belgium","OT":"Belgium",
    "PA":"Netherlands","PB":"Netherlands","PD":"Netherlands","PE":"Netherlands",
    "OZ":"Denmark","OU":"Denmark","5Q":"Denmark",
    "SM":"Sweden","SA":"Sweden","SB":"Sweden","SK":"Sweden",
    "LA":"Norway","LB":"Norway","LC":"Norway",
    "OH":"Finland","OF":"Finland","OG":"Finland","OI":"Finland",
    "ES":"Estonia","YL":"Latvia","LY":"Lithuania",
    "9A":"Croatia","S5":"Slovenia","E7":"Bosnia",
    "Z3":"N.Macedonia","Z6":"Kosovo","ZA":"Albania",
    "SV":"Greece","SW":"Greece","SX":"Greece","SY":"Greece",
    "TA":"Turkey","TC":"Turkey","YM":"Turkey",
    "4X":"Israel","4Z":"Israel",
    "SU":"Egypt","CN":"Morocco","7X":"Algeria","3V":"Tunisia",
    "ZS":"S.Africa","ZR":"S.Africa","ZU":"S.Africa",
    "W":"USA","K":"USA","N":"USA","AA":"USA","AB":"USA","AC":"USA",
    "AD":"USA","AE":"USA","AF":"USA","AG":"USA","AI":"USA","AK":"USA",
    "KH6":"Hawaii","KL7":"Alaska","KP4":"Puerto Rico",
    "VE":"Canada","VA":"Canada","VY":"Canada","VO":"Canada",
    "XE":"Mexico","XA":"Mexico","4A":"Mexico",
    "PY":"Brazil","PP":"Brazil","PR":"Brazil","PS":"Brazil","PT":"Brazil","PU":"Brazil",
    "LU":"Argentina","LW":"Argentina","LO":"Argentina",
    "CE":"Chile","CA":"Chile","XQ":"Chile",
    "JA":"Japan","JH":"Japan","JR":"Japan","JE":"Japan","JF":"Japan",
    "JG":"Japan","JI":"Japan","JJ":"Japan","JK":"Japan","JL":"Japan",
    "BY":"China","BA":"China","BD":"China","BG":"China","BI":"China",
    "HL":"S.Korea","DS":"S.Korea","6K":"S.Korea",
    "DU":"Philippines","DX":"Philippines","HS":"Thailand","E2":"Thailand",
    "VK":"Australia","AX":"Australia","ZL":"New Zealand","ZM":"New Zealand",
    "VU":"India","AT":"India","VT":"India","AP":"Pakistan",
    "A4":"Oman","A6":"UAE","A7":"Qatar","A9":"Bahrain",
    "9K":"Kuwait","HZ":"Saudi Arabia","7Z":"Saudi Arabia",
    "EK":"Armenia","4J":"Azerbaijan","4L":"Georgia",
    "UN":"Kazakhstan","JT":"Mongolia","XV":"Vietnam","3W":"Vietnam",
    "TF":"Iceland","JW":"Svalbard","OX":"Greenland","OY":"Faroe Is.",
    "T7":"San Marino","3A":"Monaco","C3":"Andorra","HV":"Vatican",
    "9H":"Malta","5B":"Cyprus","4O":"Montenegro",
}

def dxcc_lookup(call):
    c = call.upper().strip().split("/")[0]
    for n in range(min(4, len(c)), 0, -1):
        p = c[:n]
        if p in DXCC_DB:
            return DXCC_DB[p], p
    if c and c[0] in DXCC_DB:
        return DXCC_DB[c[0]], c[0]
    return "Unknown", c[:2] if len(c) >= 2 else c


# ══════════════════════════════════════════════════════════════════════════════
#  FREQUENCY / BAND
# ══════════════════════════════════════════════════════════════════════════════

FREQ_RANGES = [
    (1800,2000,"160m"),(3500,3800,"80m"),(5351,5367,"60m"),
    (7000,7200,"40m"),(10100,10150,"30m"),(14000,14350,"20m"),
    (18068,18168,"17m"),(21000,21450,"15m"),(24890,24990,"12m"),
    (28000,29700,"10m"),(50000,54000,"6m"),(144000,148000,"2m"),
    (430000,440000,"70cm"),(1240000,1300000,"23cm"),
]
BAND_DEFAULT_FREQ = {
    "160m":1850,"80m":3700,"60m":5355,"40m":7100,"30m":10120,
    "20m":14200,"17m":18120,"15m":21200,"12m":24940,"10m":28500,
    "6m":50150,"2m":145000,"70cm":432200,"23cm":1296200,
}
BANDS_HF  = ["160m","80m","60m","40m","30m","20m","17m","15m","12m","10m"]
BANDS_VHF = ["6m","2m"]
BANDS_UHF = ["70cm","23cm"]
BANDS_ALL = BANDS_HF + BANDS_VHF + BANDS_UHF

MODES_ALL  = ["SSB","CW","FT8","FT4","DIGI","RTTY","AM","FM","PSK31","SSTV","JT65"]
RST_DEF    = {"SSB":"59","AM":"59","FM":"59","SSTV":"59",
              "CW":"599","RTTY":"599","PSK31":"599","DIGI":"599",
              "FT8":"-10","FT4":"-10","JT65":"-15"}

SCORING_MODES  = ["none","per_qso","per_band","maraton","multiplier","distance","custom"]
CONTEST_TYPES  = ["Simplu","Maraton","Stafeta","YO","DX","VHF","UHF",
                  "Field Day","Sprint","QSO Party","SOTA","POTA","Custom"]
YO_COUNTIES    = ["AB","AR","AG","BC","BH","BN","BT","BV","BR","BZ",
                  "CS","CL","CJ","CT","CV","DB","DJ","GL","GR","GJ",
                  "HR","HD","IL","IS","IF","MM","MH","MS","NT","OT",
                  "PH","SM","SJ","SB","SV","TR","TM","TL","VS","VL","VN","B"]

def freq_to_band(f_str):
    try:
        f = float(f_str)
        for lo, hi, b in FREQ_RANGES:
            if lo <= f <= hi:
                return b
    except Exception:
        pass
    return None


# ══════════════════════════════════════════════════════════════════════════════
#  TRANSLATIONS
# ══════════════════════════════════════════════════════════════════════════════

_STRINGS = {
"ro": dict(
    title="YO Log PRO v17.0",
    call="Indicativ", freq="Frecv(kHz)", band="Bandă", mode="Mod",
    rst_s="RST T", rst_r="RST R", nr_s="Nr.T", nr_r="Nr.R",
    note="Notă/Loc", btn_log="LOG", btn_upd="ACTUALIZEAZĂ", btn_reset="Reset",
    manual="Manual", date_l="Dată", time_l="Oră",
    cat_l="Categorie", jud_l="Județ", btn_save_cfg="💾",
    online="Online UTC", offline="Manual",
    col_nr="Nr", col_call="Indicativ", col_freq="Frecv", col_band="Bandă",
    col_mode="Mod", col_rst_s="RST T", col_rst_r="RST R",
    col_nr_s="Nr.T", col_nr_r="Nr.R", col_note="Notă",
    col_country="Țara", col_date="Data", col_time="Ora", col_pts="Pt",
    all="Toate", f_band="Bandă:", f_mode="Mod:",
    menu_contests="Concursuri", menu_mgr="Manager Concursuri",
    menu_switch="⚡ Schimbă pe",
    menu_tools="Utilități", menu_search="🔍 Caută (Ctrl+F)",
    menu_timer="⏱ Timer Concurs",
    menu_imp_adif="Import ADIF", menu_imp_csv="Import CSV",
    menu_print="🖨 Print", menu_verify="Verificare MD5",
    menu_clear="🗑 Golire Log", menu_help="Ajutor", menu_about="Despre",
    btn_settings="⚙ Setări", btn_mgr="🏆 Concursuri",
    btn_stats="📊 Statistici", btn_validate="✅ Validare",
    btn_export="📤 Export", btn_import="📥 Import",
    btn_undo="↩ Undo", btn_backup="💾 Backup",
    btn_search="🔍 Caută", btn_timer="⏱ Timer",
    dup_title="⚠ Duplicat!", dup_msg="{} pe {}/{}  QSO#{}\nAdăugați oricum?",
    new_mult="✦ MULTIPLICATOR NOU",
    del_title="Confirmare", del_msg="Ștergeți QSO-urile selectate?",
    undo_empty="Nimic de anulat.",
    exit_title="Ieșire", exit_msg="Salvați înainte de ieșire?",
    bak_ok="Backup creat!", bak_err="Eroare backup!",
    exp_ok="Export salvat:\n{}",
    imp_ok="{} QSO importate.",
    imp_none="0 QSO găsite în fișier.",
    err="Eroare",
    save="Salvează", cancel="Anulează", close="Închide",
    settings_title="Setări Stație",
    lbl_call="Indicativ *", lbl_loc="Locator (ex: KN37)",
    lbl_jud="Județ", lbl_addr="Adresă / QTH",
    lbl_op="Operator", lbl_pwr="Putere (W)",
    lbl_font="Font (9-16)", lbl_sounds="Sunete (beep)",
    mgr_title="Manager Concursuri",
    mgr_add="➕ Nou", mgr_edit="✏ Editează", mgr_dup="📋 Duplică",
    mgr_del="🗑 Șterge", mgr_expj="📤 Export JSON", mgr_impj="📥 Import JSON",
    mgr_col_id="ID", mgr_col_name="Nume", mgr_col_type="Tip",
    mgr_col_sc="Punctare", mgr_col_mult="Mult", mgr_col_minq="MinQSO",
    ed_title_new="Concurs Nou", ed_title_edit="Editează Concurs",
    ed_id="ID (unic, fără spații):", ed_name_ro="Nume RO:",
    ed_name_en="Nume EN:", ed_type="Tip:", ed_sc="Mod Punctare:",
    ed_ppq="Puncte/QSO:", ed_minq="Min QSO:", ed_mult="Multiplicatori:",
    ed_serial="Numere Seriale", ed_county="Câmp Județ",
    ed_cats="Categorii (câte una/linie):",
    ed_bands="Benzi permise:", ed_modes="Moduri permise:",
    ed_req="Stații obligatorii (câte una/linie):",
    ed_sp="Punctare specială (CALL=PTS, câte una/linie):",
    ed_bp="Puncte/bandă (BANDĂ=PTS, câte una/linie):",
    ed_cl="Județe permise (separate prin virgulă):",
    ed_id_err="ID invalid sau există deja!",
    ed_save="💾 Salvează Concursul", ed_cancel="Anulează",
    prot="Concursul implicit nu poate fi șters.",
    conf_del_c="Ștergeți concursul '{}'?",
    stats_title="Statistici",
    val_title="Validare Log",
    val_empty="Log gol.",
    search_title="Căutare în Log",
    search_lbl="Caută indicativ / notă:",
    search_res="Rezultate: {}",
    timer_title="Timer Concurs",
    timer_dur="Durată (ore):",
    timer_start="▶ Start", timer_stop="⏸ Stop", timer_reset="⏹ Reset",
    timer_elapsed="Scurs:", timer_remain="Rămas:",
    timer_up="⏰ TIMP EXPIRAT!",
    verify_ok="✓ Log integru — {} QSO\nMD5: {}",
    clear_title="Golire Log",
    clear_msg="Goliți COMPLET logul?\n(backup automat înainte)\nIREVERSIBIL!",
    about_text=(
        "📻 YO Log PRO v17.0\n\n"
        "Aplicație profesională de logging pentru radioamatori\n\n"
        "Autor: Ardei Constantin-Cătălin (YO8ACR)\n"
        "Email: yo8acr@gmail.com  ·  Locator: KN37\n\n"
        "Ctrl+F = Caută    Ctrl+Z = Undo\n"
        "Ctrl+S = Salvează  F2 = Bandă+  F3 = Mod+\n"
        "Enter = LOG  Dublu-click = Editează\n\n"
        "73 de YO8ACR! 📻"
    ),
),
"en": dict(
    title="YO Log PRO v17.0",
    call="Callsign", freq="Freq(kHz)", band="Band", mode="Mode",
    rst_s="RST S", rst_r="RST R", nr_s="Nr.S", nr_r="Nr.R",
    note="Note/Loc", btn_log="LOG", btn_upd="UPDATE", btn_reset="Reset",
    manual="Manual", date_l="Date", time_l="Time",
    cat_l="Category", jud_l="County", btn_save_cfg="💾",
    online="Online UTC", offline="Manual",
    col_nr="Nr", col_call="Callsign", col_freq="Freq", col_band="Band",
    col_mode="Mode", col_rst_s="RST S", col_rst_r="RST R",
    col_nr_s="Nr.S", col_nr_r="Nr.R", col_note="Note",
    col_country="Country", col_date="Date", col_time="Time", col_pts="Pts",
    all="All", f_band="Band:", f_mode="Mode:",
    menu_contests="Contests", menu_mgr="Contest Manager",
    menu_switch="⚡ Switch to",
    menu_tools="Tools", menu_search="🔍 Search (Ctrl+F)",
    menu_timer="⏱ Contest Timer",
    menu_imp_adif="Import ADIF", menu_imp_csv="Import CSV",
    menu_print="🖨 Print", menu_verify="Verify MD5",
    menu_clear="🗑 Clear Log", menu_help="Help", menu_about="About",
    btn_settings="⚙ Settings", btn_mgr="🏆 Contests",
    btn_stats="📊 Stats", btn_validate="✅ Validate",
    btn_export="📤 Export", btn_import="📥 Import",
    btn_undo="↩ Undo", btn_backup="💾 Backup",
    btn_search="🔍 Search", btn_timer="⏱ Timer",
    dup_title="⚠ Duplicate!", dup_msg="{} on {}/{}  QSO#{}\nAdd anyway?",
    new_mult="✦ NEW MULTIPLIER",
    del_title="Confirm", del_msg="Delete selected QSO(s)?",
    undo_empty="Nothing to undo.",
    exit_title="Exit", exit_msg="Save before exit?",
    bak_ok="Backup created!", bak_err="Backup error!",
    exp_ok="Export saved:\n{}",
    imp_ok="{} QSOs imported.",
    imp_none="0 QSOs found in file.",
    err="Error",
    save="Save", cancel="Cancel", close="Close",
    settings_title="Station Settings",
    lbl_call="Callsign *", lbl_loc="Locator (e.g. KN37)",
    lbl_jud="County", lbl_addr="Address / QTH",
    lbl_op="Operator", lbl_pwr="Power (W)",
    lbl_font="Font size (9-16)", lbl_sounds="Sounds (beep)",
    mgr_title="Contest Manager",
    mgr_add="➕ New", mgr_edit="✏ Edit", mgr_dup="📋 Duplicate",
    mgr_del="🗑 Delete", mgr_expj="📤 Export JSON", mgr_impj="📥 Import JSON",
    mgr_col_id="ID", mgr_col_name="Name", mgr_col_type="Type",
    mgr_col_sc="Scoring", mgr_col_mult="Mult", mgr_col_minq="MinQSO",
    ed_title_new="New Contest", ed_title_edit="Edit Contest",
    ed_id="ID (unique, no spaces):", ed_name_ro="Name RO:",
    ed_name_en="Name EN:", ed_type="Type:", ed_sc="Scoring Mode:",
    ed_ppq="Points/QSO:", ed_minq="Min QSO:", ed_mult="Multipliers:",
    ed_serial="Serial Numbers", ed_county="County Field",
    ed_cats="Categories (one per line):",
    ed_bands="Allowed bands:", ed_modes="Allowed modes:",
    ed_req="Required stations (one per line):",
    ed_sp="Special scoring (CALL=PTS, one per line):",
    ed_bp="Band points (BAND=PTS, one per line):",
    ed_cl="Allowed counties (comma-separated):",
    ed_id_err="Invalid ID or already exists!",
    ed_save="💾 Save Contest", ed_cancel="Cancel",
    prot="Default contest cannot be deleted.",
    conf_del_c="Delete contest '{}'?",
    stats_title="Statistics",
    val_title="Log Validation",
    val_empty="Log is empty.",
    search_title="Search Log",
    search_lbl="Search callsign / note:",
    search_res="Results: {}",
    timer_title="Contest Timer",
    timer_dur="Duration (hours):",
    timer_start="▶ Start", timer_stop="⏸ Stop", timer_reset="⏹ Reset",
    timer_elapsed="Elapsed:", timer_remain="Remaining:",
    timer_up="⏰ TIME UP!",
    verify_ok="✓ Log OK — {} QSOs\nMD5: {}",
    clear_title="Clear Log",
    clear_msg="Clear the ENTIRE log?\n(auto-backup first)\nIRREVERSIBLE!",
    about_text=(
        "📻 YO Log PRO v17.0\n\n"
        "Professional amateur radio contest logger\n\n"
        "Author: Ardei Constantin-Cătălin (YO8ACR)\n"
        "Email: yo8acr@gmail.com  ·  Locator: KN37\n\n"
        "Ctrl+F = Search    Ctrl+Z = Undo\n"
        "Ctrl+S = Save     F2 = Band+   F3 = Mode+\n"
        "Enter = LOG   Double-click = Edit\n\n"
        "73 de YO8ACR! 📻"
    ),
),
}

class L:
    """Language manager."""
    _lang = "ro"
    @classmethod
    def set(cls, lang):
        if lang in _STRINGS:
            cls._lang = lang
    @classmethod
    def get(cls):
        return cls._lang
    @classmethod
    def t(cls, key, *args):
        s = _STRINGS.get(cls._lang, _STRINGS["ro"]).get(key, key)
        return s.format(*args) if args else s


# ══════════════════════════════════════════════════════════════════════════════
#  DEFAULT DATA
# ══════════════════════════════════════════════════════════════════════════════

DEFAULT_CFG = {
    "call":"YO8ACR","loc":"KN37","jud":"NT","addr":"","op_name":"","power":"100",
    "fs":11,"contest":"simplu","county":"NT","cat_idx":0,
    "lang":"ro","manual_dt":False,"sounds":True,"win_geo":"1240x760",
}

DEFAULT_CONTESTS = {
"simplu":{
    "name_ro":"Log Simplu","name_en":"Simple Log","contest_type":"Simplu",
    "categories":["Individual"],
    "scoring_mode":"none","points_per_qso":1,"min_qso":0,
    "allowed_bands":list(BANDS_ALL),"allowed_modes":list(MODES_ALL),
    "required_stations":[],"special_scoring":{},"use_serial":False,
    "use_county":False,"county_list":[],"multiplier_type":"none",
    "band_points":{},"is_default":True,
},
"maraton":{
    "name_ro":"Maraton","name_en":"Marathon","contest_type":"Maraton",
    "categories":["A. Seniori YO","B. YL","C. Juniori YO","D. Club","E. DX","F. Receptori"],
    "scoring_mode":"maraton","points_per_qso":1,"min_qso":100,
    "allowed_bands":BANDS_HF+BANDS_VHF,"allowed_modes":list(MODES_ALL),
    "required_stations":[],"special_scoring":{},"use_serial":False,
    "use_county":True,"county_list":list(YO_COUNTIES),
    "multiplier_type":"county","band_points":{},"is_default":False,
},
"stafeta":{
    "name_ro":"Ștafetă","name_en":"Relay","contest_type":"Stafeta",
    "categories":["A. Senior","B. YL","C. Junior"],
    "scoring_mode":"per_qso","points_per_qso":2,"min_qso":50,
    "allowed_bands":BANDS_HF,"allowed_modes":["SSB","CW"],
    "required_stations":[],"special_scoring":{},"use_serial":True,
    "use_county":True,"county_list":list(YO_COUNTIES),
    "multiplier_type":"county","band_points":{},"is_default":False,
},
"yo-dx-hf":{
    "name_ro":"YO DX HF Contest","name_en":"YO DX HF Contest","contest_type":"DX",
    "categories":["A. SO AB High","B. SO AB Low","C. SO SB"],
    "scoring_mode":"per_band","points_per_qso":1,"min_qso":0,
    "allowed_bands":["160m","80m","40m","20m","15m","10m"],
    "allowed_modes":["SSB","CW"],
    "required_stations":[],"special_scoring":{},"use_serial":True,
    "use_county":True,"county_list":list(YO_COUNTIES),
    "multiplier_type":"dxcc",
    "band_points":{"160m":4,"80m":3,"40m":2,"20m":1,"15m":1,"10m":2},
    "is_default":False,
},
"yo-vhf":{
    "name_ro":"YO VHF Contest","name_en":"YO VHF Contest","contest_type":"VHF",
    "categories":["A. Fixed","B. Mobile","C. Portable"],
    "scoring_mode":"distance","points_per_qso":1,"min_qso":0,
    "allowed_bands":["6m","2m","70cm","23cm"],"allowed_modes":["SSB","CW","FM"],
    "required_stations":[],"special_scoring":{},"use_serial":True,
    "use_county":False,"county_list":[],
    "multiplier_type":"grid","band_points":{},"is_default":False,
},
"field-day":{
    "name_ro":"Field Day","name_en":"Field Day","contest_type":"Field Day",
    "categories":["1A","2A","3A","1B","2B"],
    "scoring_mode":"per_qso","points_per_qso":2,"min_qso":0,
    "allowed_bands":list(BANDS_HF),"allowed_modes":list(MODES_ALL),
    "required_stations":[],"special_scoring":{},"use_serial":False,
    "use_county":False,"county_list":[],"multiplier_type":"none",
    "band_points":{},"is_default":False,
},
"sprint":{
    "name_ro":"Sprint","name_en":"Sprint","contest_type":"Sprint",
    "categories":["A. Single Op","B. Multi Op"],
    "scoring_mode":"per_qso","points_per_qso":1,"min_qso":0,
    "allowed_bands":["40m","20m","15m","10m"],"allowed_modes":["SSB","CW"],
    "required_stations":[],"special_scoring":{},"use_serial":True,
    "use_county":False,"county_list":[],"multiplier_type":"none",
    "band_points":{},"is_default":False,
},
}

# Theme
TH = {
    "bg":"#0d1117","fg":"#c9d1d9","fg2":"#8b949e",
    "hdr":"#010409","entry":"#161b22","border":"#30363d",
    "accent":"#1f6feb","accent2":"#388bfd",
    "ok":"#3fb950","warn":"#d29922","err":"#f85149",
    "dup":"#2d1b1b","alt":"#0d1f2d","spec":"#1a1a3d",
    "gold":"#e3b341","cyan":"#58a6ff",
    "btn":"#21262d","btn_fg":"#c9d1d9",
    "led_on":"#3fb950","led_off":"#f85149",
}


# ══════════════════════════════════════════════════════════════════════════════
#  DATA MANAGER
# ══════════════════════════════════════════════════════════════════════════════

class DM:
    @staticmethod
    def path(fn):
        return os.path.join(_data_dir(), fn)

    @staticmethod
    def save(fn, data):
        p = DM.path(fn); tmp = p + ".tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            if os.path.exists(p):
                os.remove(p)
            os.rename(tmp, p)
            return True
        except Exception:
            try: os.remove(tmp)
            except Exception: pass
            return False

    @staticmethod
    def load(fn, default=None):
        p = DM.path(fn)
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        if default is not None:
            DM.save(fn, default)
        return copy.deepcopy(default) if default is not None else {}

    @staticmethod
    def log_fn(cid):
        return "log_" + re.sub(r'[^a-zA-Z0-9_-]', '_', cid) + ".json"

    @staticmethod
    def load_log(cid):
        return DM.load(DM.log_fn(cid), [])

    @staticmethod
    def save_log(cid, data):
        return DM.save(DM.log_fn(cid), data)

    @staticmethod
    def backup(cid, data):
        try:
            bd = os.path.join(_data_dir(), "backups")
            os.makedirs(bd, exist_ok=True)
            ts  = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            sid = re.sub(r'[^a-zA-Z0-9_-]', '_', cid)
            with open(os.path.join(bd, f"log_{sid}_{ts}.json"),
                      "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            # keep last 50
            bks = sorted(Path(bd).glob(f"log_{sid}_*.json"))
            for old in bks[:-50]:
                old.unlink(missing_ok=True)
            return True
        except Exception:
            return False


# ══════════════════════════════════════════════════════════════════════════════
#  SCORING ENGINE
# ══════════════════════════════════════════════════════════════════════════════

class Score:
    @staticmethod
    def qso_pts(q, rules, cfg=None):
        sm = (rules or {}).get("scoring_mode", "none")
        if sm == "none": return 0
        call = q.get("c","").upper()
        sp   = (rules or {}).get("special_scoring", {})
        if call in sp:
            try: return int(sp[call])
            except Exception: pass
        if sm == "per_qso":   return rules.get("points_per_qso", 1)
        if sm == "per_band":
            bp = rules.get("band_points", {})
            return int(bp.get(q.get("b",""), rules.get("points_per_qso",1)))
        if sm == "maraton":
            return int(sp.get(call, rules.get("points_per_qso",1)))
        if sm == "distance":
            n  = q.get("n","").strip()
            ml = (cfg or {}).get("loc","")
            if Loc.valid(n) and Loc.valid(ml):
                return max(1, int(Loc.dist(ml, n)))
        return rules.get("points_per_qso", 1)

    @staticmethod
    def multipliers(log, rules):
        mt = (rules or {}).get("multiplier_type","none")
        if mt == "none": return 1, set()
        ms = set()
        for q in log:
            n = q.get("n","").upper().strip()
            c = q.get("c","").upper()
            b = q.get("b","")
            if mt == "county":
                for co in (rules or {}).get("county_list",[]):
                    if re.search(r'\b' + re.escape(co.upper()) + r'\b', n):
                        ms.add(co.upper()); break
            elif mt == "dxcc":  ms.add(dxcc_lookup(c)[1])
            elif mt == "band":  ms.add(b)
            elif mt == "grid":
                if len(n) >= 4 and Loc.valid(n[:4]): ms.add(n[:4])
        return max(1, len(ms)), ms

    @staticmethod
    def total(log, rules, cfg=None):
        if not log or not rules: return 0, 0, 0
        if rules.get("scoring_mode","none") == "none": return 0, 0, 0
        qp = sum(Score.qso_pts(q, rules, cfg) for q in log)
        mc, _ = Score.multipliers(log, rules)
        if rules.get("multiplier_type","none") != "none":
            return qp, mc, qp * mc
        return qp, mc, qp

    @staticmethod
    def is_dup(log, call, band, mode, skip_idx=None):
        cu = call.upper()
        for i, q in enumerate(log):
            if i == skip_idx: continue
            if q.get("c","").upper() == cu \
               and q.get("b") == band and q.get("m") == mode:
                return True, i
        return False, -1

    @staticmethod
    def worked_before(log, call, band, mode):
        """Returns 'dup', 'other', or ''."""
        cu = call.upper()
        for q in log:
            if q.get("c","").upper() == cu:
                if q.get("b") == band and q.get("m") == mode:
                    return "dup"
                return "other"
        return ""

    @staticmethod
    def is_new_mult(log, q, rules):
        mt = (rules or {}).get("multiplier_type","none")
        if mt == "none": return False
        _, ex = Score.multipliers(log, rules)
        n = q.get("n","").upper().strip(); c = q.get("c","").upper()
        nm = None
        if mt == "county":
            for co in (rules or {}).get("county_list",[]):
                if re.search(r'\b' + re.escape(co.upper()) + r'\b', n):
                    nm = co.upper(); break
        elif mt == "dxcc":  nm = dxcc_lookup(c)[1]
        elif mt == "band":  nm = q.get("b","")
        elif mt == "grid":
            if len(n) >= 4 and Loc.valid(n[:4]): nm = n[:4]
        return nm is not None and nm not in ex

    @staticmethod
    def validate(log, rules, cfg=None):
        if not log:
            return False, L.t("val_empty"), 0
        msgs = []
        mq = (rules or {}).get("min_qso", 0)
        if mq and len(log) < mq:
            msgs.append(f"⚠ Min {mq} QSO — aveți/have {len(log)}")
        seen = set(); dups = 0
        for q in log:
            k = (q.get("c","").upper(), q.get("b"), q.get("m"))
            if k in seen: dups += 1
            seen.add(k)
        if dups: msgs.append(f"⚠ {dups} duplicate(s)")
        req = (rules or {}).get("required_stations", [])
        if req:
            calls = {q.get("c","").upper() for q in log}
            miss  = [r for r in req if r.upper() not in calls]
            if miss: msgs.append(f"⚠ Lipsesc / Missing: {', '.join(miss)}")
        ab = (rules or {}).get("allowed_bands", [])
        am = (rules or {}).get("allowed_modes", [])
        if ab:
            bad_b = sum(1 for q in log if q.get("b") not in ab)
            if bad_b: msgs.append(f"⚠ {bad_b} QSO pe benzi neautorizate")
        if am:
            bad_m = sum(1 for q in log if q.get("m") not in am)
            if bad_m: msgs.append(f"⚠ {bad_m} QSO cu moduri neautorizate")
        if msgs:
            return False, "\n".join(msgs), 0
        _, _, tot = Score.total(log, rules, cfg)
        return True, f"✓ OK  {len(log)} QSO   Scor/Score: {tot}", tot


# ══════════════════════════════════════════════════════════════════════════════
#  IMPORT
# ══════════════════════════════════════════════════════════════════════════════

class Imp:
    @staticmethod
    def adif(text):
        qsos = []
        eoh = text.upper().find("<EOH>")
        body = text[eoh+5:] if eoh >= 0 else text
        for rec in re.split(r'<EOR>', body, flags=re.IGNORECASE):
            rec = rec.strip()
            if not rec: continue
            flds = {}
            for m in re.finditer(r'<(\w+):(\d+)(?::[^>]*)?>(.{0,9999}?)',
                                  rec, re.IGNORECASE|re.DOTALL):
                flds[m.group(1).upper()] = m.group(3)[:int(m.group(2))]
            if "CALL" not in flds: continue
            q = {"c": flds["CALL"].upper()}
            q["b"] = flds.get("BAND","40m")
            q["m"] = flds.get("MODE","SSB")
            q["s"] = flds.get("RST_SENT","59")
            q["r"] = flds.get("RST_RCVD","59")
            qd = flds.get("QSO_DATE","")
            q["d"] = f"{qd[:4]}-{qd[4:6]}-{qd[6:8]}" if len(qd)==8 \
                     else datetime.datetime.utcnow().strftime("%Y-%m-%d")
            qt = flds.get("TIME_ON","")
            q["t"] = f"{qt[:2]}:{qt[2:4]}" if len(qt)>=4 else "00:00"
            fr = flds.get("FREQ","")
            if fr:
                try:
                    fv = float(fr)
                    q["f"] = str(int(fv*1000 if fv < 1000 else fv))
                except Exception:
                    q["f"] = fr
            else:
                q["f"] = ""
            q["n"]  = flds.get("GRIDSQUARE", flds.get("COMMENT",""))
            q["ss"] = flds.get("STX",""); q["sr"] = flds.get("SRX","")
            qsos.append(q)
        return qsos

    @staticmethod
    def csv_file(text):
        qsos = []
        try:
            rdr = csv.DictReader(io.StringIO(text))
            for row in rdr:
                def g(*keys):
                    for k in keys:
                        v = row.get(k,"").strip()
                        if v: return v
                    return ""
                call = g("Call","CALL","call","Callsign").upper()
                if not call: continue
                q = {"c":call,
                     "b": g("Band","BAND") or "40m",
                     "m": g("Mode","MODE") or "SSB",
                     "s": g("RST_Sent","RST_S","rst_s") or "59",
                     "r": g("RST_Rcvd","RST_R","rst_r") or "59",
                     "d": g("Date","DATE") or datetime.datetime.utcnow().strftime("%Y-%m-%d"),
                     "t": g("Time","TIME") or "00:00",
                     "f": g("Freq","FREQ") or "",
                     "n": g("Note","NOTE","Comment") or "",
                     "ss":g("Nr_S","SS") or "",
                     "sr":g("Nr_R","SR") or ""}
                qsos.append(q)
        except Exception:
            pass
        return qsos


# ══════════════════════════════════════════════════════════════════════════════
#  CONTEST EDITOR  (full fields, scrollable)
# ══════════════════════════════════════════════════════════════════════════════

class ContestEditor(tk.Toplevel):
    def __init__(self, parent, cid=None, cdata=None, existing_ids=None):
        super().__init__(parent)
        self.result   = None
        self._cid     = cid
        self._new     = cid is None
        self._ids     = set(existing_ids or [])
        self._data    = copy.deepcopy(cdata) if cdata else {
            "name_ro":"","name_en":"","contest_type":"Simplu",
            "categories":["Individual"],"scoring_mode":"none",
            "points_per_qso":1,"min_qso":0,
            "allowed_bands":list(BANDS_ALL),"allowed_modes":list(MODES_ALL),
            "required_stations":[],"special_scoring":{},"use_serial":False,
            "use_county":False,"county_list":[],"multiplier_type":"none",
            "band_points":{},"is_default":False,
        }
        self.title(L.t("ed_title_new") if self._new else L.t("ed_title_edit"))
        self.geometry("740x830")
        self.configure(bg=TH["bg"])
        self.resizable(True, True)
        self.transient(parent); self.grab_set()
        self._build()

    # ── layout ───────────────────────────────────────────────────────────────
    def _build(self):
        eo = {"bg":TH["entry"],"fg":TH["fg"],"insertbackground":TH["fg"],
              "font":("Consolas",11),"relief":"flat","bd":4}
        lo = {"bg":TH["bg"],"fg":TH["fg2"],"font":("Consolas",10),"anchor":"w"}

        # scrollable canvas
        outer  = tk.Frame(self, bg=TH["bg"])
        outer.pack(fill="both", expand=True)
        canvas = tk.Canvas(outer, bg=TH["bg"], highlightthickness=0)
        vsb    = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        frm = tk.Frame(canvas, bg=TH["bg"], padx=18, pady=12)
        win = canvas.create_window((0,0), window=frm, anchor="nw")
        frm.bind("<Configure>",
                 lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(win, width=e.width-20))
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(int(-1*(e.delta/120)),"units"))

        self._w = {}  # widget dict

        def row_label(text):
            tk.Label(frm, text=text, **lo).pack(fill="x", pady=(6,1))

        def row_entry(key, default="", width=50):
            e = tk.Entry(frm, width=width, **eo)
            e.insert(0, default)
            e.pack(fill="x", pady=(0,3), ipady=3)
            self._w[key] = e

        def row_combo(key, values, default):
            v = tk.StringVar(value=default)
            c = ttk.Combobox(frm, textvariable=v, values=values,
                             state="readonly", font=("Consolas",11))
            c.pack(fill="x", pady=(0,3))
            self._w[key] = v
            return v

        def row_text(key, content, height=4):
            t = tk.Text(frm, height=height, **eo)
            t.insert("1.0", content)
            t.pack(fill="x", pady=(0,3))
            self._w[key] = t

        def row_check(key, text, default):
            v = tk.BooleanVar(value=default)
            tk.Checkbutton(frm, text=text, variable=v,
                           bg=TH["bg"], fg=TH["fg"], selectcolor=TH["entry"],
                           activebackground=TH["bg"],
                           font=("Consolas",11)).pack(anchor="w", pady=(0,3))
            self._w[key] = v

        def sep():
            tk.Frame(frm, bg=TH["border"], height=1).pack(fill="x", pady=6)

        # ID (new only)
        if self._new:
            row_label(L.t("ed_id"))
            row_entry("id", "")
        # Names
        row_label(L.t("ed_name_ro"))
        row_entry("name_ro", self._data.get("name_ro",""))
        row_label(L.t("ed_name_en"))
        row_entry("name_en", self._data.get("name_en",""))
        sep()
        # Type / Scoring / Multiplier
        row_label(L.t("ed_type"))
        row_combo("contest_type", CONTEST_TYPES, self._data.get("contest_type","Simplu"))
        row_label(L.t("ed_sc"))
        row_combo("scoring_mode", SCORING_MODES, self._data.get("scoring_mode","none"))
        row_label(L.t("ed_mult"))
        row_combo("multiplier_type",
                  ["none","county","dxcc","band","grid"],
                  self._data.get("multiplier_type","none"))
        sep()
        # Points / Min QSO
        pf = tk.Frame(frm, bg=TH["bg"])
        pf.pack(fill="x", pady=(0,6))
        tk.Label(pf, text=L.t("ed_ppq"), **{**lo,"anchor":"w"}).pack(side="left")
        e1 = tk.Entry(pf, width=6, **eo)
        e1.insert(0, str(self._data.get("points_per_qso",1)))
        e1.pack(side="left", padx=(4,20))
        self._w["points_per_qso"] = e1
        tk.Label(pf, text=L.t("ed_minq"), **{**lo,"anchor":"w"}).pack(side="left")
        e2 = tk.Entry(pf, width=6, **eo)
        e2.insert(0, str(self._data.get("min_qso",0)))
        e2.pack(side="left", padx=4)
        self._w["min_qso"] = e2
        # Checkboxes
        cf = tk.Frame(frm, bg=TH["bg"])
        cf.pack(fill="x", pady=(0,4))
        row_check("use_serial", L.t("ed_serial"), self._data.get("use_serial",False))
        row_check("use_county", L.t("ed_county"), self._data.get("use_county",False))
        sep()
        # Categories
        row_label(L.t("ed_cats"))
        row_text("categories", "\n".join(self._data.get("categories",["Individual"])), 4)
        # Bands
        row_label(L.t("ed_bands"))
        bf = tk.Frame(frm, bg=TH["bg"])
        bf.pack(fill="x", pady=(0,4))
        ab_set = set(self._data.get("allowed_bands", BANDS_ALL))
        self._band_vars = {}
        for i, b in enumerate(BANDS_ALL):
            v = tk.BooleanVar(value=b in ab_set)
            tk.Checkbutton(bf, text=b, variable=v,
                           bg=TH["bg"], fg=TH["fg"], selectcolor=TH["entry"],
                           activebackground=TH["bg"],
                           font=("Consolas",9)).grid(row=i//7, column=i%7, sticky="w", padx=2)
            self._band_vars[b] = v
        # Modes
        row_label(L.t("ed_modes"))
        mf = tk.Frame(frm, bg=TH["bg"])
        mf.pack(fill="x", pady=(0,4))
        am_set = set(self._data.get("allowed_modes", MODES_ALL))
        self._mode_vars = {}
        for i, m in enumerate(MODES_ALL):
            v = tk.BooleanVar(value=m in am_set)
            tk.Checkbutton(mf, text=m, variable=v,
                           bg=TH["bg"], fg=TH["fg"], selectcolor=TH["entry"],
                           activebackground=TH["bg"],
                           font=("Consolas",9)).grid(row=i//5, column=i%5, sticky="w", padx=2)
            self._mode_vars[m] = v
        sep()
        # Required / Special / BandPts / CountyList
        row_label(L.t("ed_req"))
        row_text("required_stations",
                 "\n".join(self._data.get("required_stations",[])), 3)
        row_label(L.t("ed_sp"))
        row_text("special_scoring",
                 "\n".join(f"{k}={v}" for k,v in
                           self._data.get("special_scoring",{}).items()), 3)
        row_label(L.t("ed_bp"))
        row_text("band_points",
                 "\n".join(f"{k}={v}" for k,v in
                           self._data.get("band_points",{}).items()), 3)
        row_label(L.t("ed_cl"))
        row_entry("county_list", ",".join(self._data.get("county_list",[])))
        sep()
        # Save / Cancel
        bf2 = tk.Frame(frm, bg=TH["bg"])
        bf2.pack(fill="x", pady=10)
        tk.Button(bf2, text=L.t("ed_save"), command=self._save,
                  bg=TH["accent"], fg="white",
                  font=("Consolas",12,"bold"), width=22,
                  relief="flat", cursor="hand2").pack(side="left", padx=4)
        tk.Button(bf2, text=L.t("ed_cancel"), command=self.destroy,
                  bg=TH["btn"], fg=TH["btn_fg"],
                  font=("Consolas",12), width=12,
                  relief="flat", cursor="hand2").pack(side="left", padx=4)

    @staticmethod
    def _kv(text):
        r = {}
        for line in text.strip().splitlines():
            if "=" in line:
                k, _, v = line.partition("=")
                k = k.strip().upper(); v = v.strip()
                if k: r[k] = v
        return r

    def _save(self):
        if self._new:
            cid = self._w["id"].get().strip().lower().replace(" ","-")
            if not cid or cid in self._ids:
                messagebox.showerror(L.t("err"), L.t("ed_id_err"), parent=self)
                return
            self._cid = cid

        d = self._data
        d["name_ro"]       = self._w["name_ro"].get().strip()
        d["name_en"]       = self._w["name_en"].get().strip()
        d["contest_type"]  = self._w["contest_type"].get()
        d["scoring_mode"]  = self._w["scoring_mode"].get()
        d["multiplier_type"] = self._w["multiplier_type"].get()
        try:    d["points_per_qso"] = int(self._w["points_per_qso"].get())
        except: d["points_per_qso"] = 1
        try:    d["min_qso"] = int(self._w["min_qso"].get())
        except: d["min_qso"] = 0
        d["use_serial"] = self._w["use_serial"].get()
        d["use_county"] = self._w["use_county"].get()
        cats = [c.strip() for c in
                self._w["categories"].get("1.0","end").splitlines() if c.strip()]
        d["categories"] = cats or ["Individual"]
        d["allowed_bands"] = [b for b,v in self._band_vars.items() if v.get()] or list(BANDS_ALL)
        d["allowed_modes"] = [m for m,v in self._mode_vars.items() if v.get()] or list(MODES_ALL)
        req = [s.strip().upper() for s in
               self._w["required_stations"].get("1.0","end").splitlines() if s.strip()]
        d["required_stations"] = req
        raw_sp = self._kv(self._w["special_scoring"].get("1.0","end"))
        d["special_scoring"]   = raw_sp
        raw_bp = self._kv(self._w["band_points"].get("1.0","end"))
        d["band_points"] = {k: int(v) for k,v in raw_bp.items()
                            if v.strip().lstrip("-").isdigit()}
        cl_raw = self._w["county_list"].get().strip()
        d["county_list"] = [c.strip().upper() for c in cl_raw.split(",")
                            if c.strip()] if cl_raw else []
        d["is_default"] = False
        self.result = (self._cid, d)
        self.destroy()


# ══════════════════════════════════════════════════════════════════════════════
#  CONTEST MANAGER
# ══════════════════════════════════════════════════════════════════════════════

class ContestMgr(tk.Toplevel):
    def __init__(self, parent, contests):
        super().__init__(parent)
        self.c = copy.deepcopy(contests)
        self.result = None
        self.title(L.t("mgr_title"))
        self.geometry("780x520")
        self.configure(bg=TH["bg"])
        self.resizable(True, True)
        self.transient(parent); self.grab_set()
        self._build(); self._fill()

    def _build(self):
        tb = tk.Frame(self, bg=TH["hdr"], pady=6)
        tb.pack(fill="x")
        for txt, cmd, col in [
            (L.t("mgr_add"),  self._add,    TH["ok"]),
            (L.t("mgr_edit"), self._edit,   TH["accent"]),
            (L.t("mgr_dup"),  self._dup,    TH["warn"]),
            (L.t("mgr_del"),  self._del,    TH["err"]),
            (L.t("mgr_expj"), self._exp,    TH["btn"]),
            (L.t("mgr_impj"), self._imp,    TH["btn"]),
        ]:
            tk.Button(tb, text=txt, command=cmd, bg=col, fg="white",
                      font=("Consolas",10), relief="flat",
                      cursor="hand2", padx=6).pack(side="left", padx=3)

        tf = tk.Frame(self, bg=TH["bg"])
        tf.pack(fill="both", expand=True, padx=8, pady=4)
        cols = ("id","name","type","sc","mult","minq")
        hdrs = [L.t(f"mgr_col_{c}") for c in cols]
        wids = [110, 200, 90, 90, 60, 60]
        self.tree = ttk.Treeview(tf, columns=cols, show="headings",
                                  selectmode="browse")
        for c, h, w in zip(cols, hdrs, wids):
            self.tree.heading(c, text=h); self.tree.column(c, width=w, anchor="center")
        sb = ttk.Scrollbar(tf, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree.bind("<Double-1>", lambda e: self._edit())

        bf = tk.Frame(self, bg=TH["bg"], pady=8)
        bf.pack(fill="x")
        tk.Button(bf, text=L.t("save"), command=self._ok,
                  bg=TH["ok"], fg="white", font=("Consolas",12,"bold"),
                  width=14, relief="flat", cursor="hand2").pack(side="left", padx=12)
        tk.Button(bf, text=L.t("cancel"), command=self.destroy,
                  bg=TH["btn"], fg=TH["btn_fg"], font=("Consolas",11),
                  width=12, relief="flat", cursor="hand2").pack(side="right", padx=12)

    def _fill(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for cid, cd in self.c.items():
            nm = cd.get("name_"+L.get(), cd.get("name_ro", cid))
            self.tree.insert("","end", iid=cid,
                values=(cid, nm, cd.get("contest_type","?"),
                        cd.get("scoring_mode","none"),
                        cd.get("multiplier_type","none"),
                        cd.get("min_qso",0)))

    def _sel(self):
        s = self.tree.selection()
        return s[0] if s else None

    def _add(self):
        d = ContestEditor(self, existing_ids=set(self.c))
        self.wait_window(d)
        if d.result:
            self.c[d.result[0]] = d.result[1]; self._fill()

    def _edit(self):
        cid = self._sel()
        if not cid: return
        d = ContestEditor(self, cid=cid, cdata=self.c[cid],
                          existing_ids=set(self.c))
        self.wait_window(d)
        if d.result:
            self.c[cid] = d.result[1]; self._fill()

    def _dup(self):
        cid = self._sel()
        if not cid: return
        nc = cid+"-copy"; i=2
        while nc in self.c: nc = f"{cid}-copy{i}"; i+=1
        self.c[nc] = copy.deepcopy(self.c[cid])
        self.c[nc]["is_default"] = False
        self.c[nc]["name_ro"] += " (copie)"
        self.c[nc]["name_en"] += " (copy)"
        self._fill()

    def _del(self):
        cid = self._sel()
        if not cid: return
        if self.c.get(cid,{}).get("is_default"):
            messagebox.showwarning("",L.t("prot"),parent=self); return
        if messagebox.askyesno(L.t("del_title"),
                               L.t("conf_del_c",cid), parent=self):
            del self.c[cid]; self._fill()

    def _exp(self):
        fp = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("JSON","*.json")],
            initialfile=f"contests_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.json",
            parent=self)
        if fp:
            try:
                with open(fp,"w",encoding="utf-8") as f:
                    json.dump(self.c,f,indent=2,ensure_ascii=False)
                messagebox.showinfo("OK",L.t("exp_ok",os.path.basename(fp)),parent=self)
            except Exception as e:
                messagebox.showerror(L.t("err"),str(e),parent=self)

    def _imp(self):
        fp = filedialog.askopenfilename(filetypes=[("JSON","*.json")],parent=self)
        if fp:
            try:
                with open(fp,"r",encoding="utf-8") as f:
                    imp = json.load(f)
                if isinstance(imp,dict):
                    added = sum(1 for k,v in imp.items()
                                if k not in self.c and not self.c.update({k:v}))
                    self._fill()
                    messagebox.showinfo("OK",f"Importate/Imported: {added}",parent=self)
            except Exception as e:
                messagebox.showerror(L.t("err"),str(e),parent=self)

    def _ok(self):
        self.result = self.c; self.destroy()


# ══════════════════════════════════════════════════════════════════════════════
#  STATS WINDOW
# ══════════════════════════════════════════════════════════════════════════════

class StatsWin(tk.Toplevel):
    def __init__(self, parent, log, rules, cfg):
        super().__init__(parent)
        self.title(L.t("stats_title"))
        self.geometry("560x560"); self.configure(bg=TH["bg"])
        self.resizable(True, True); self.transient(parent)
        txt = scrolledtext.ScrolledText(self, bg=TH["entry"], fg=TH["fg"],
                                         font=("Consolas",10), wrap="word",
                                         state="normal")
        txt.pack(fill="both",expand=True, padx=8, pady=8)
        for tag, fg in [("h",TH["gold"]),("ok",TH["ok"]),
                        ("err",TH["err"]),("warn",TH["warn"])]:
            txt.tag_configure(tag, foreground=fg,
                              font=("Consolas",11,"bold") if tag=="h" else None)

        def w(t, tag=None):
            txt.insert("end", t, tag)

        nm = (rules or {}).get("name_"+L.get(),
              (rules or {}).get("name_ro","?"))
        w(f"📊 {L.t('stats_title')} — {nm}\n\n","h")
        w(f"Total QSO  : {len(log)}\n")
        w(f"Unice / Unique: {len({q.get('c','').upper() for q in log})}\n")
        # Operating time
        dts = []
        for q in log:
            try:
                dts.append(datetime.datetime.strptime(
                    q.get("d","")+" "+q.get("t",""),"%Y-%m-%d %H:%M"))
            except: pass
        if len(dts) >= 2:
            dts.sort()
            span_h = (dts[-1]-dts[0]).total_seconds()/3600
            rate = len(dts)/span_h if span_h > 0 else 0
            w(f"Primul / First: {dts[0].strftime('%Y-%m-%d %H:%M')}\n")
            w(f"Ultimul / Last:  {dts[-1].strftime('%Y-%m-%d %H:%M')}\n")
            w(f"Durata / Duration: {span_h:.1f}h   Rată / Rate: {rate:.1f} QSO/h\n")
        w("\n─── Benzi / Bands ───\n","h")
        bc = Counter(q.get("b","?") for q in log)
        for b in BANDS_ALL:
            if b in bc:
                pts = sum(Score.qso_pts(q,rules,cfg) for q in log if q.get("b")==b)
                uni = len({q.get("c","").upper() for q in log if q.get("b")==b})
                w(f"  {b:<6}  QSO:{bc[b]:<5} Unice:{uni:<5} Pts:{pts}\n")
        w("\n─── Moduri / Modes ───\n","h")
        for m, cnt in Counter(q.get("m","?") for q in log).most_common():
            w(f"  {m:<8} {cnt}\n")
        w("\n─── Scor / Score ───\n","h")
        if (rules or {}).get("scoring_mode","none") != "none":
            qp, mc, tot = Score.total(log, rules, cfg)
            w(f"  Puncte QSO   : {qp}\n")
            w(f"  Multiplicatori: {mc}\n")
            w(f"  TOTAL = {qp} × {mc} = {tot}\n","ok")
        else:
            w("  (fără punctare / no scoring)\n","warn")
        req = (rules or {}).get("required_stations",[])
        if req:
            w("\n─── Stații obligatorii / Required ───\n","h")
            have = {q.get("c","").upper() for q in log}
            for r in req:
                ok = r.upper() in have
                w(f"  {'✓' if ok else '✗'} {r}\n", "ok" if ok else "err")
        mt = (rules or {}).get("multiplier_type","none")
        if mt == "county":
            all_co  = (rules or {}).get("county_list", YO_COUNTIES)
            _, worked = Score.multipliers(log, rules)
            miss = [c for c in all_co if c.upper() not in worked]
            w(f"\n─── Județe / Counties: {len(worked)}/{len(all_co)} ───\n","h")
            if miss: w(f"  Lipsesc / Missing: {', '.join(sorted(miss))}\n","warn")
        elif mt == "dxcc":
            _, worked = Score.multipliers(log, rules)
            w(f"\n─── DXCC ({len(worked)}) ───\n","h")
            cnt = Counter(dxcc_lookup(q.get("c",""))[0] for q in log)
            for country, n in cnt.most_common(20):
                w(f"  {country:<22} {n}\n")
        txt.config(state="disabled")
        tk.Button(self, text=L.t("close"), command=self.destroy,
                  bg=TH["btn"], fg=TH["btn_fg"], relief="flat",
                  cursor="hand2").pack(pady=6)


# ══════════════════════════════════════════════════════════════════════════════
#  SEARCH DIALOG
# ══════════════════════════════════════════════════════════════════════════════

class SearchDlg(tk.Toplevel):
    def __init__(self, parent, log):
        super().__init__(parent)
        self._log = log
        self.title(L.t("search_title"))
        self.geometry("620x420"); self.configure(bg=TH["bg"])
        self.transient(parent)
        eo = {"bg":TH["entry"],"fg":TH["fg"],"insertbackground":TH["fg"],
               "font":("Consolas",11),"relief":"flat","bd":4}
        tk.Label(self, text=L.t("search_lbl"),
                 bg=TH["bg"], fg=TH["fg2"],
                 font=("Consolas",10)).pack(anchor="w", padx=10, pady=(10,2))
        self._sv = tk.StringVar()
        e = tk.Entry(self, textvariable=self._sv, **eo)
        e.pack(fill="x", padx=10, pady=2, ipady=3); e.focus()
        e.bind("<KeyRelease>", self._search)
        self._lbl = tk.Label(self, text="", bg=TH["bg"], fg=TH["fg2"],
                             font=("Consolas",9))
        self._lbl.pack(anchor="w", padx=10)
        tf = tk.Frame(self, bg=TH["bg"])
        tf.pack(fill="both",expand=True, padx=10, pady=4)
        cols = ("nr","call","band","mode","date","note")
        self.tree = ttk.Treeview(tf, columns=cols, show="headings")
        for c, h, w in zip(cols,
            [L.t("col_nr"),L.t("col_call"),L.t("col_band"),
             L.t("col_mode"),L.t("col_date"),L.t("col_note")],
            [40,110,55,55,90,200]):
            self.tree.heading(c,text=h); self.tree.column(c,width=w,anchor="center")
        sb = ttk.Scrollbar(tf, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left",fill="both",expand=True)
        sb.pack(side="right",fill="y")
        tk.Button(self, text=L.t("close"), command=self.destroy,
                  bg=TH["btn"], fg=TH["btn_fg"], relief="flat",
                  cursor="hand2").pack(pady=6)

    def _search(self, _=None):
        q = self._sv.get().upper().strip()
        for i in self.tree.get_children(): self.tree.delete(i)
        if not q: self._lbl.config(text=""); return
        res = [(len(self._log)-i, e)
               for i, e in enumerate(self._log)
               if q in e.get("c","").upper() or q in e.get("n","").upper()]
        self._lbl.config(text=L.t("search_res", len(res)))
        for nr, e in res:
            self.tree.insert("","end",
                values=(nr,e.get("c"),e.get("b"),e.get("m"),e.get("d"),e.get("n")))


# ══════════════════════════════════════════════════════════════════════════════
#  TIMER DIALOG
# ══════════════════════════════════════════════════════════════════════════════

class TimerDlg(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(L.t("timer_title"))
        self.geometry("300x230"); self.configure(bg=TH["bg"])
        self.resizable(False,False); self.transient(parent)
        self._run = False; self._end = None; self._start_dt = None
        eo = {"bg":TH["entry"],"fg":TH["fg"],"insertbackground":TH["fg"],
               "font":("Consolas",11),"justify":"center","relief":"flat","bd":4}
        tk.Label(self, text=L.t("timer_dur"), bg=TH["bg"], fg=TH["fg2"],
                 font=("Consolas",10)).pack(pady=(14,2))
        self._dur = tk.Entry(self, width=8, **eo)
        self._dur.insert(0,"4"); self._dur.pack(pady=2)
        self._clk = tk.Label(self, text="00:00:00", bg=TH["bg"], fg=TH["gold"],
                              font=("Consolas",30,"bold"))
        self._clk.pack(pady=6)
        self._rem = tk.Label(self, text="", bg=TH["bg"], fg=TH["fg"],
                             font=("Consolas",10))
        self._rem.pack()
        bf = tk.Frame(self, bg=TH["bg"]); bf.pack(pady=8)
        self._sb = tk.Button(bf, text=L.t("timer_start"), command=self._toggle,
                              bg=TH["ok"], fg="white", font=("Consolas",10),
                              width=8, relief="flat", cursor="hand2")
        self._sb.pack(side="left", padx=4)
        tk.Button(bf, text=L.t("timer_reset"), command=self._reset,
                  bg=TH["warn"], fg="white", font=("Consolas",10),
                  width=8, relief="flat", cursor="hand2").pack(side="left", padx=4)
        self._tick()

    def _toggle(self):
        if self._run:
            self._run = False; self._sb.config(text=L.t("timer_start"),bg=TH["ok"])
        else:
            try: h = float(self._dur.get())
            except: h = 0
            self._start_dt = datetime.datetime.utcnow()
            self._end = self._start_dt + datetime.timedelta(hours=h) if h > 0 else None
            self._run = True; self._sb.config(text=L.t("timer_stop"),bg=TH["err"])

    def _reset(self):
        self._run = False; self._end = None; self._start_dt = None
        try: self._clk.config(text="00:00:00",fg=TH["gold"]); self._rem.config(text="")
        except Exception: pass
        self._sb.config(text=L.t("timer_start"),bg=TH["ok"])

    def _tick(self):
        try:
            if not self.winfo_exists(): return
        except Exception: return
        try:
            if self._run and self._start_dt:
                now = datetime.datetime.utcnow()
                el  = int((now - self._start_dt).total_seconds())
                h,r = divmod(el,3600); m,s = divmod(r,60)
                self._clk.config(text=f"{h:02d}:{m:02d}:{s:02d}")
                if self._end:
                    rem = int((self._end - now).total_seconds())
                    if rem <= 0:
                        self._run = False
                        self._clk.config(fg=TH["err"])
                        self._rem.config(text=L.t("timer_up"),fg=TH["err"])
                        _beep("error")
                    else:
                        rh,rr=divmod(rem,3600); rm,rs=divmod(rr,60)
                        self._rem.config(
                            text=f"{L.t('timer_remain')} {rh:02d}:{rm:02d}:{rs:02d}",
                            fg=TH["warn"] if rem<300 else TH["fg"])
        except Exception: pass
        try: self.after(1000, self._tick)
        except Exception: pass


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ══════════════════════════════════════════════════════════════════════════════

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        # ── load config / contests / log ────────────────────────────────────
        self.cfg      = DM.load("config.json", copy.deepcopy(DEFAULT_CFG))
        self.contests = DM.load("contests.json", copy.deepcopy(DEFAULT_CONTESTS))
        for k, v in DEFAULT_CONTESTS.items():
            if k not in self.contests:
                self.contests[k] = copy.deepcopy(v)
        if self._cid() not in self.contests:
            self.cfg["contest"] = "simplu"
        self.log   = DM.load_log(self._cid())
        self.serial = max((int(q.get("ss","0") or 0)
                           for q in self.log if q.get("ss","").isdigit()),
                          default=0) + 1
        L.set(self.cfg.get("lang","ro"))
        self.edit_idx  = None
        self.undo_stack = deque(maxlen=50)
        # ── window ──────────────────────────────────────────────────────────
        self.title(L.t("title"))
        self.configure(bg=TH["bg"])
        try:    self.geometry(self.cfg.get("win_geo","1240x760"))
        except: self.geometry("1240x760")
        self.minsize(1020, 660)
        self._style()
        self._menu()
        self._ui()
        self.protocol("WM_DELETE_WINDOW", self._exit)
        # ── key bindings ────────────────────────────────────────────────────
        self.bind("<Control-s>", lambda e: self._fsave())
        self.bind("<Control-z>", lambda e: self._undo())
        self.bind("<Control-f>", lambda e: self._search())
        self.bind("<F2>",  lambda e: self._cycle_band())
        self.bind("<F3>",  lambda e: self._cycle_mode())
        # ── tickers ─────────────────────────────────────────────────────────
        self._tick_clock()
        self._tick_save()
        self._refresh()

    # ── helpers ──────────────────────────────────────────────────────────────
    def _cid(self):  return self.cfg.get("contest","simplu")
    def _cc(self):   return self.contests.get(self._cid(), self.contests.get("simplu",{}))
    def _sounds(self): return self.cfg.get("sounds",True)

    # ── style ────────────────────────────────────────────────────────────────
    def _style(self):
        fs = int(self.cfg.get("fs",11))
        self.fn  = ("Consolas", fs)
        self.fnb = ("Consolas", fs, "bold")
        s = ttk.Style()
        try: s.theme_use("clam")
        except Exception: pass
        s.configure("Treeview",
                     background=TH["entry"], foreground=TH["fg"],
                     fieldbackground=TH["entry"], font=self.fn, rowheight=22)
        s.configure("Treeview.Heading",
                     background=TH["hdr"], foreground=TH["gold"],
                     font=("Consolas",fs,"bold"))
        s.map("Treeview", background=[("selected",TH["accent"])])
        s.configure("TCombobox",
                     fieldbackground=TH["entry"], background=TH["entry"],
                     foreground=TH["fg"], selectbackground=TH["accent"])
        s.map("TCombobox", fieldbackground=[("readonly",TH["entry"])])

    # ── menu ─────────────────────────────────────────────────────────────────
    def _menu(self):
        mb = tk.Menu(self, bg=TH["hdr"], fg=TH["fg"],
                     activebackground=TH["accent"], activeforeground="white",
                     relief="flat", bd=0)
        self.config(menu=mb)
        # Contests
        cm = tk.Menu(mb, tearoff=0, bg=TH["hdr"], fg=TH["fg"],
                     activebackground=TH["accent"], activeforeground="white")
        mb.add_cascade(label=L.t("menu_contests"), menu=cm)
        cm.add_command(label=L.t("menu_mgr"), command=self._mgr)
        cm.add_separator()
        for cid, cd in self.contests.items():
            nm = cd.get("name_"+L.get(), cd.get("name_ro",cid))
            cm.add_command(label=f"⚡ {nm}",
                           command=lambda c=cid: self._switch(c))
        # Tools
        tm = tk.Menu(mb, tearoff=0, bg=TH["hdr"], fg=TH["fg"],
                     activebackground=TH["accent"], activeforeground="white")
        mb.add_cascade(label=L.t("menu_tools"), menu=tm)
        tm.add_command(label=L.t("menu_search"),  command=self._search)
        tm.add_command(label=L.t("menu_timer"),   command=self._timer)
        tm.add_separator()
        tm.add_command(label=L.t("menu_imp_adif"),command=self._imp_adif)
        tm.add_command(label=L.t("menu_imp_csv"), command=self._imp_csv)
        tm.add_separator()
        tm.add_command(label=L.t("menu_print"),   command=self._print)
        tm.add_command(label=L.t("menu_verify"),  command=self._verify)
        tm.add_separator()
        tm.add_command(label=L.t("menu_clear"),   command=self._clear_log)
        # Help
        hm = tk.Menu(mb, tearoff=0, bg=TH["hdr"], fg=TH["fg"],
                     activebackground=TH["accent"], activeforeground="white")
        mb.add_cascade(label=L.t("menu_help"), menu=hm)
        hm.add_command(label=L.t("menu_about"), command=self._about)
        hm.add_separator()
        hm.add_command(label="Exit", command=self._exit)

    # ── full UI build ─────────────────────────────────────────────────────────
    def _ui(self):
        self._ui_header()
        self._ui_input()
        self._ui_filter()
        self._ui_tree()
        self._ui_buttons()

    # ── header ────────────────────────────────────────────────────────────────
    def _ui_header(self):
        h = tk.Frame(self, bg=TH["hdr"], pady=5)
        h.pack(fill="x")
        # left: LED + status + info
        lf = tk.Frame(h, bg=TH["hdr"]); lf.pack(side="left", padx=10)
        self._led_cv = tk.Canvas(lf, width=14, height=14,
                                  bg=TH["hdr"], highlightthickness=0)
        self._led    = self._led_cv.create_oval(2,2,12,12,
                                                 fill=TH["led_on"], outline="")
        self._led_cv.pack(side="left", padx=(0,4))
        self._led_lbl = tk.Label(lf, text=L.t("online"),
                                  bg=TH["hdr"], fg=TH["led_on"], font=self.fn)
        self._led_lbl.pack(side="left")
        self._info = tk.Label(lf, text="", bg=TH["hdr"], fg=TH["fg"], font=self.fn)
        self._info.pack(side="left", padx=10)
        # right: rate, lang, contest selector, clock
        rf = tk.Frame(h, bg=TH["hdr"]); rf.pack(side="right", padx=10)
        self._clk = tk.Label(rf, text="UTC 00:00:00",
                              bg=TH["hdr"], fg=TH["gold"],
                              font=("Consolas",12,"bold"))
        self._clk.pack(side="right", padx=8)
        self._rate = tk.Label(rf, text="", bg=TH["hdr"],
                               fg=TH["ok"], font=("Consolas",10))
        self._rate.pack(side="right", padx=6)
        # lang
        self._lang_v = tk.StringVar(value=L.get())
        lc = ttk.Combobox(rf, textvariable=self._lang_v,
                          values=["ro","en"], state="readonly", width=4)
        lc.pack(side="right", padx=3)
        lc.bind("<<ComboboxSelected>>", self._on_lang)
        # contest selector
        self._cv = tk.StringVar(value=self._cid())
        self._ccb = ttk.Combobox(rf, textvariable=self._cv,
                                   values=list(self.contests.keys()),
                                   state="readonly", width=16)
        self._ccb.pack(side="right", padx=3)
        self._ccb.bind("<<ComboboxSelected>>", self._on_contest)

    # ── input area ────────────────────────────────────────────────────────────
    def _ui_input(self):
        self._ent   = {}        # all entry/combobox widgets
        self._wb    = None      # worked-before label
        self._log_btn = None    # LOG button reference

        ip = tk.Frame(self, bg=TH["bg"], pady=6)
        ip.pack(fill="x", padx=8)

        cc  = self._cc()
        ab  = cc.get("allowed_bands", BANDS_ALL) or BANDS_ALL
        am  = cc.get("allowed_modes", MODES_ALL) or MODES_ALL
        def_rst = RST_DEF.get(am[0] if am else "SSB", "59")

        eo = {"bg":TH["entry"],"fg":TH["fg"],"insertbackground":TH["fg"],
               "relief":"flat","bd":4,"justify":"center"}

        def lbl(parent, text):
            return tk.Label(parent, text=text, bg=TH["bg"],
                            fg=TH["fg2"], font=("Consolas",9))

        # ── ROW 1 ─────────────────────────────────────────────────────────
        r1 = tk.Frame(ip, bg=TH["bg"]); r1.pack(fill="x")

        # Callsign
        cf = tk.Frame(r1, bg=TH["bg"]); cf.pack(side="left", padx=(0,4))
        lbl(cf, L.t("call")).pack()
        self._ent["call"] = tk.Entry(cf, width=14, font=("Consolas",13,"bold"),
                                      fg=TH["gold"], **eo)
        self._ent["call"].pack(ipady=4)
        self._wb = tk.Label(cf, text="", bg=TH["bg"],
                             fg=TH["err"], font=("Consolas",8))
        self._wb.pack()
        self._ent["call"].bind("<KeyRelease>", self._on_call)

        # Freq
        ff = tk.Frame(r1, bg=TH["bg"]); ff.pack(side="left", padx=(0,4))
        lbl(ff, L.t("freq")).pack()
        self._ent["freq"] = tk.Entry(ff, width=9, font=self.fn, **eo)
        self._ent["freq"].pack(ipady=4)
        self._ent["freq"].bind("<FocusOut>", self._on_freq)
        self._ent["freq"].bind("<Return>",   self._on_freq)

        # Band
        bf3 = tk.Frame(r1, bg=TH["bg"]); bf3.pack(side="left", padx=(0,4))
        lbl(bf3, L.t("band")).pack()
        self._ent["band"] = ttk.Combobox(bf3, values=ab, state="readonly",
                                          width=6, font=self.fn)
        self._ent["band"].set(ab[0])
        self._ent["band"].pack()
        self._ent["band"].bind("<<ComboboxSelected>>", self._on_band)

        # Mode
        mf3 = tk.Frame(r1, bg=TH["bg"]); mf3.pack(side="left", padx=(0,4))
        lbl(mf3, L.t("mode")).pack()
        self._ent["mode"] = ttk.Combobox(mf3, values=am, state="readonly",
                                          width=6, font=self.fn)
        self._ent["mode"].set(am[0] if am else "SSB")
        self._ent["mode"].pack()
        self._ent["mode"].bind("<<ComboboxSelected>>", self._on_mode)

        # RST S/R
        for key, lb in [("rst_s", L.t("rst_s")), ("rst_r", L.t("rst_r"))]:
            xf = tk.Frame(r1, bg=TH["bg"]); xf.pack(side="left", padx=(0,4))
            lbl(xf, lb).pack()
            self._ent[key] = tk.Entry(xf, width=5, font=self.fn, **eo)
            self._ent[key].insert(0, def_rst)
            self._ent[key].pack(ipady=4)

        # Serials (if contest uses them)
        if cc.get("use_serial"):
            for key, lb in [("nr_s", L.t("nr_s")), ("nr_r", L.t("nr_r"))]:
                xf = tk.Frame(r1, bg=TH["bg"]); xf.pack(side="left", padx=(0,4))
                lbl(xf, lb).pack()
                e = tk.Entry(xf, width=5, font=self.fn, **eo)
                if key == "nr_s":
                    e.insert(0, str(self.serial))
                e.pack(ipady=4)
                self._ent[key] = e

        # Note
        nf = tk.Frame(r1, bg=TH["bg"]); nf.pack(side="left", padx=(0,4))
        lbl(nf, L.t("note")).pack()
        self._ent["note"] = tk.Entry(nf, width=12, font=self.fn, **eo)
        self._ent["note"].pack(ipady=4)

        # Manual checkbox + LOG + Reset  (right side, vertically stacked)
        rbf = tk.Frame(r1, bg=TH["bg"]); rbf.pack(side="left", padx=(8,0))
        self._man_v = tk.BooleanVar(value=self.cfg.get("manual_dt",False))
        tk.Checkbutton(rbf, text=L.t("manual"), variable=self._man_v,
                       bg=TH["bg"], fg=TH["fg2"], font=("Consolas",9),
                       selectcolor=TH["entry"], activebackground=TH["bg"],
                       command=self._tog_man).pack(anchor="w")
        self._log_btn = tk.Button(rbf, text=L.t("btn_log"),
                                   command=self._add_qso,
                                   bg=TH["accent"], fg="white",
                                   font=("Consolas",12,"bold"),
                                   width=10, relief="flat", cursor="hand2")
        self._log_btn.pack(pady=2)
        tk.Button(rbf, text=L.t("btn_reset"), command=self._clr,
                  bg=TH["btn"], fg=TH["btn_fg"], font=self.fn,
                  width=10, relief="flat", cursor="hand2").pack()

        # ── ROW 2 — date/time + category + county + save ─────────────────
        r2 = tk.Frame(ip, bg=TH["bg"]); r2.pack(fill="x", pady=(6,0))

        now = datetime.datetime.utcnow()
        st  = "normal" if self._man_v.get() else "disabled"

        for key, lb, val, w in [
            ("date", L.t("date_l"), now.strftime("%Y-%m-%d"), 11),
            ("time", L.t("time_l"), now.strftime("%H:%M"),     7),
        ]:
            xf = tk.Frame(r2, bg=TH["bg"]); xf.pack(side="left", padx=(0,4))
            lbl(xf, lb).pack(anchor="w")
            e = tk.Entry(xf, width=w, font=self.fn, state=st, **eo)
            e.config(disabledbackground=TH["hdr"],
                     disabledforeground=TH["fg2"])
            e.config(state="normal"); e.insert(0, val); e.config(state=st)
            e.pack(ipady=3)
            self._ent[key] = e

        # Category
        cats = cc.get("categories", ["Individual"]) or ["Individual"]
        cat_idx = min(self.cfg.get("cat_idx",0), len(cats)-1)
        cf2 = tk.Frame(r2, bg=TH["bg"]); cf2.pack(side="left", padx=(8,4))
        lbl(cf2, L.t("cat_l")).pack(anchor="w")
        self._cat_v = tk.StringVar(value=cats[cat_idx])
        ttk.Combobox(cf2, textvariable=self._cat_v, values=cats,
                     state="readonly", width=20, font=self.fn).pack()

        # County (only if contest uses it)
        self._jud_v = None
        if cc.get("use_county"):
            jlist = cc.get("county_list", YO_COUNTIES) or YO_COUNTIES
            jf = tk.Frame(r2, bg=TH["bg"]); jf.pack(side="left", padx=(0,4))
            lbl(jf, L.t("jud_l")).pack(anchor="w")
            self._jud_v = tk.StringVar(value=self.cfg.get("county","NT"))
            ttk.Combobox(jf, textvariable=self._jud_v, values=jlist,
                         state="readonly", width=6, font=self.fn).pack()

        # Save cat/county
        sf = tk.Frame(r2, bg=TH["bg"]); sf.pack(side="left", padx=(4,0))
        lbl(sf, L.t("btn_save_cfg")).pack(anchor="w")
        tk.Button(sf, text=L.t("btn_save_cfg"), command=self._save_cat,
                  bg=TH["btn"], fg=TH["btn_fg"], font=self.fn,
                  relief="flat", cursor="hand2", width=3).pack()

        # ── Enter binding on all text entries (LOG) ────────────────────────
        for key in ("call","freq","rst_s","rst_r","note","nr_s","nr_r","date","time"):
            if key in self._ent:
                self._ent[key].bind("<Return>", lambda e: self._add_qso())

    # ── filter bar ────────────────────────────────────────────────────────────
    def _ui_filter(self):
        ff = tk.Frame(self, bg=TH["bg"]); ff.pack(fill="x", padx=8, pady=(2,0))
        tk.Label(ff, text=L.t("f_band"), bg=TH["bg"],
                 fg=TH["fg2"], font=("Consolas",10)).pack(side="left")
        ab = [L.t("all")] + (self._cc().get("allowed_bands", BANDS_ALL) or BANDS_ALL)
        self._fb_v = tk.StringVar(value=L.t("all"))
        fbcb = ttk.Combobox(ff, textvariable=self._fb_v, values=ab,
                             state="readonly", width=7)
        fbcb.pack(side="left", padx=3)
        fbcb.bind("<<ComboboxSelected>>", lambda e: self._refresh())
        tk.Label(ff, text=L.t("f_mode"), bg=TH["bg"],
                 fg=TH["fg2"], font=("Consolas",10)).pack(side="left", padx=(8,0))
        am = [L.t("all")] + (self._cc().get("allowed_modes", MODES_ALL) or MODES_ALL)
        self._fm_v = tk.StringVar(value=L.t("all"))
        fmcb = ttk.Combobox(ff, textvariable=self._fm_v, values=am,
                             state="readonly", width=7)
        fmcb.pack(side="left", padx=3)
        fmcb.bind("<<ComboboxSelected>>", lambda e: self._refresh())
        self._sc_lbl = tk.Label(ff, text="", bg=TH["bg"],
                                 fg=TH["gold"], font=("Consolas",11,"bold"))
        self._sc_lbl.pack(side="right", padx=10)

    # ── treeview ──────────────────────────────────────────────────────────────
    def _ui_tree(self):
        tf = tk.Frame(self, bg=TH["bg"])
        tf.pack(fill="both", expand=True, padx=8, pady=3)
        cc  = self._cc()
        us  = cc.get("use_serial", False)
        hs  = cc.get("scoring_mode","none") != "none"
        cols = ["nr","call","freq","band","mode","rst_s","rst_r"]
        hdrs = [L.t(f"col_{c}") for c in cols]
        wids = [38, 115, 72, 56, 56, 46, 46]
        if us:
            cols += ["nr_s","nr_r"]
            hdrs += [L.t("col_nr_s"), L.t("col_nr_r")]
            wids += [46, 46]
        cols += ["note","country","date","time"]
        hdrs += [L.t("col_note"),L.t("col_country"),L.t("col_date"),L.t("col_time")]
        wids += [95, 95, 82, 50]
        if hs:
            cols.append("pts"); hdrs.append(L.t("col_pts")); wids.append(46)
        self._tree_cols = cols
        self.tree = ttk.Treeview(tf, columns=cols, show="headings",
                                  selectmode="extended")
        for c, h, w in zip(cols, hdrs, wids):
            self.tree.heading(c, text=h,
                               command=lambda col=c: self._sort(col))
            self.tree.column(c, width=w, anchor="center", minwidth=30)
        self.tree.tag_configure("dup",  background=TH["dup"])
        self.tree.tag_configure("alt",  background=TH["alt"])
        self.tree.tag_configure("spec", background=TH["spec"])
        sb = ttk.Scrollbar(tf, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree.bind("<Double-1>", lambda e: self._edit_sel())
        self.tree.bind("<Button-3>",  self._rclick)
        self.tree.bind("<Delete>",    lambda e: self._del_sel())
        self._sort_col = None; self._sort_rev = False
        # context menu
        self._ctx = tk.Menu(self, tearoff=0, bg=TH["hdr"], fg=TH["fg"],
                             activebackground=TH["accent"], activeforeground="white")
        self._ctx.add_command(label="✏ "+L.t("btn_log"), command=self._edit_sel)
        self._ctx.add_command(label="🗑 Delete",         command=self._del_sel)

    # ── button bar ────────────────────────────────────────────────────────────
    def _ui_buttons(self):
        bb = tk.Frame(self, bg=TH["bg"], pady=5); bb.pack(fill="x", padx=8)
        btns = [
            (L.t("btn_settings"), self._settings, TH["warn"]),
            (L.t("btn_mgr"),      self._mgr,      "#E91E63"),
            (L.t("btn_stats"),    self._stats,    "#3F51B5"),
            (L.t("btn_validate"), self._validate, TH["ok"]),
            (L.t("btn_export"),   self._export,   "#9C27B0"),
            (L.t("btn_import"),   self._import,   "#FF5722"),
            (L.t("btn_undo"),     self._undo,     "#795548"),
            (L.t("btn_backup"),   self._backup,   "#607D8B"),
            (L.t("btn_search"),   self._search,   "#00796B"),
            (L.t("btn_timer"),    self._timer,    "#004D40"),
        ]
        for txt, cmd, col in btns:
            tk.Button(bb, text=txt, command=cmd, bg=col, fg="white",
                      font=("Consolas",10), width=11, relief="flat",
                      cursor="hand2").pack(side="left", padx=2)

    # ══════════════════════════════════════════════════════════════════════════
    #  REFRESH
    # ══════════════════════════════════════════════════════════════════════════

    def _refresh(self):
        if not hasattr(self, "tree") or self.tree is None:
            return
        for i in self.tree.get_children():
            self.tree.delete(i)
        cc  = self._cc()
        hs  = cc.get("scoring_mode","none") != "none"
        us  = cc.get("use_serial", False)
        sp  = set((cc.get("special_scoring") or {}).keys())
        fb  = getattr(self,"_fb_v",None)
        fm  = getattr(self,"_fm_v",None)
        f_band = fb.get() if fb else L.t("all")
        f_mode = fm.get() if fm else L.t("all")
        seen = set()
        for i, q in enumerate(self.log):
            b = q.get("b",""); m = q.get("m",""); c = q.get("c","").upper()
            if f_band != L.t("all") and b != f_band: continue
            if f_mode != L.t("all") and m != f_mode: continue
            nr  = len(self.log) - i
            key = (c, b, m)
            tag = "dup" if key in seen else ("spec" if c in sp else ("alt" if i%2==0 else ""))
            seen.add(key)
            country, _ = dxcc_lookup(c)
            vals = [nr, c, q.get("f",""), b, m, q.get("s","59"), q.get("r","59")]
            if us: vals += [q.get("ss",""), q.get("sr","")]
            vals += [q.get("n",""), "" if country=="Unknown" else country,
                     q.get("d",""), q.get("t","")]
            if hs: vals.append(Score.qso_pts(q, cc, self.cfg))
            self.tree.insert("","end", iid=str(i),
                              values=vals, tags=(tag,) if tag else ())
        self._upd_info()

    def _upd_info(self):
        cc   = self._cc()
        call = self.cfg.get("call","NOCALL")
        nm   = cc.get("name_"+L.get(), cc.get("name_ro","?"))
        cat  = self._cat_v.get() if hasattr(self,"_cat_v") and self._cat_v else ""
        if hasattr(self,"_info") and self._info:
            self._info.config(
                text=f"{call}  |  {nm}  |  {cat}  |  QSO: {len(self.log)}")
        if hasattr(self,"_sc_lbl") and self._sc_lbl:
            if cc.get("scoring_mode","none") != "none":
                qp, mc, tot = Score.total(self.log, cc, self.cfg)
                sep = "×" if cc.get("multiplier_type","none") != "none" else ""
                txt = f"Σ {qp}{sep}{mc if sep else ''}={tot}" if sep \
                      else f"Σ {tot}"
                self._sc_lbl.config(text=txt)
            else:
                self._sc_lbl.config(text="")
        # Rate meter
        if hasattr(self,"_rate") and self._rate and len(self.log) >= 2:
            try:
                dts = []
                for q in self.log[:30]:
                    try:
                        dts.append(datetime.datetime.strptime(
                            q.get("d","")+" "+q.get("t",""),"%Y-%m-%d %H:%M"))
                    except: pass
                if len(dts) >= 2:
                    dts.sort()
                    span = (dts[-1]-dts[0]).total_seconds()/3600
                    if span > 0:
                        self._rate.config(text=f"⚡{len(dts)/span:.0f} QSO/h")
            except Exception: pass

    # ══════════════════════════════════════════════════════════════════════════
    #  QSO OPERATIONS
    # ══════════════════════════════════════════════════════════════════════════

    def _add_qso(self):
        call = self._ent["call"].get().upper().strip()
        if not call: return
        band = self._ent["band"].get()
        mode = self._ent["mode"].get()
        if not band or not mode: return

        # bounds-check edit_idx
        if self.edit_idx is not None and self.edit_idx >= len(self.log):
            self.edit_idx = None
            self._log_btn.config(text=L.t("btn_log"), bg=TH["accent"])

        cc = self._cc()
        dup, di = Score.is_dup(self.log, call, band, mode, self.edit_idx)
        if dup and self.edit_idx is None:
            if self._sounds(): _beep("warn")
            if not messagebox.askyesno(
                    L.t("dup_title"),
                    L.t("dup_msg", call, band, mode, len(self.log)-di)):
                return

        ds, ts = self._get_dt()
        q_prev = {"c":call,"b":band,"m":mode,
                  "n":self._ent["note"].get().strip().upper()}
        if Score.is_new_mult(self.log, q_prev, cc):
            if self._sounds(): _beep("info")

        q = {
            "c": call, "b": band, "m": mode,
            "s": self._ent["rst_s"].get().strip() or "59",
            "r": self._ent["rst_r"].get().strip() or "59",
            "n": self._ent["note"].get().strip(),
            "d": ds, "t": ts,
            "f": self._ent["freq"].get().strip(),
        }
        if "nr_s" in self._ent: q["ss"] = self._ent["nr_s"].get().strip()
        if "nr_r" in self._ent: q["sr"] = self._ent["nr_r"].get().strip()

        if self.edit_idx is not None:
            self.log[self.edit_idx] = q
            self.edit_idx = None
            self._log_btn.config(text=L.t("btn_log"), bg=TH["accent"])
        else:
            self.log.insert(0, q)
            self.undo_stack.append(("add", 0, copy.deepcopy(q)))
            self.serial += 1

        self._clr()
        self._refresh()
        DM.save_log(self._cid(), self.log)

    def _clr(self):
        for key in ("call","freq","note"):
            if key in self._ent:
                self._ent[key].delete(0,"end")
        if "nr_s" in self._ent:
            self._ent["nr_s"].delete(0,"end")
            self._ent["nr_s"].insert(0, str(self.serial))
        if "nr_r" in self._ent:
            self._ent["nr_r"].delete(0,"end")
        if self._wb: self._wb.config(text="")
        self._ent["call"].focus_set()

    def _edit_sel(self):
        sel = self.tree.selection()
        if not sel: return
        try:   idx = int(sel[0])
        except: return
        if idx < 0 or idx >= len(self.log): return
        self.edit_idx = idx
        q = self.log[idx]
        cc = self._cc()
        ab = cc.get("allowed_bands", BANDS_ALL) or BANDS_ALL
        am = cc.get("allowed_modes", MODES_ALL) or MODES_ALL
        self._ent["call"].delete(0,"end"); self._ent["call"].insert(0,q.get("c",""))
        self._ent["freq"].delete(0,"end"); self._ent["freq"].insert(0,q.get("f",""))
        b = q.get("b","40m")
        if b in ab: self._ent["band"].set(b)
        m = q.get("m","SSB")
        if m in am: self._ent["mode"].set(m)
        self._ent["rst_s"].delete(0,"end"); self._ent["rst_s"].insert(0,q.get("s","59"))
        self._ent["rst_r"].delete(0,"end"); self._ent["rst_r"].insert(0,q.get("r","59"))
        self._ent["note"].delete(0,"end"); self._ent["note"].insert(0,q.get("n",""))
        if "nr_s" in self._ent:
            self._ent["nr_s"].delete(0,"end"); self._ent["nr_s"].insert(0,q.get("ss",""))
        if "nr_r" in self._ent:
            self._ent["nr_r"].delete(0,"end"); self._ent["nr_r"].insert(0,q.get("sr",""))
        self._log_btn.config(text=L.t("btn_upd"), bg=TH["warn"])

    def _del_sel(self):
        sel = self.tree.selection()
        if not sel: return
        if not messagebox.askyesno(L.t("del_title"),L.t("del_msg")): return
        for idx in sorted([int(x) for x in sel], reverse=True):
            if 0 <= idx < len(self.log):
                self.undo_stack.append(("del", idx, copy.deepcopy(self.log[idx])))
                self.log.pop(idx)
        self._refresh()
        DM.save_log(self._cid(), self.log)

    def _undo(self):
        if not self.undo_stack:
            messagebox.showinfo("", L.t("undo_empty")); return
        act, idx, q = self.undo_stack.pop()
        if act == "add" and 0 <= idx < len(self.log):
            self.log.pop(idx)
        elif act == "del":
            self.log.insert(idx, q)
        self._refresh()
        DM.save_log(self._cid(), self.log)

    # ══════════════════════════════════════════════════════════════════════════
    #  EVENT HANDLERS
    # ══════════════════════════════════════════════════════════════════════════

    def _on_call(self, _=None):
        c = self._ent["call"].get().upper()
        pos = self._ent["call"].index(tk.INSERT)
        self._ent["call"].delete(0,"end")
        self._ent["call"].insert(0, c)
        try: self._ent["call"].icursor(min(pos, len(c)))
        except: pass
        if self._wb and len(c) >= 3:
            wb = Score.worked_before(self.log, c,
                 self._ent["band"].get(), self._ent["mode"].get())
            if wb == "dup":
                self._wb.config(text="⚠ DUP", fg=TH["err"])
            elif wb == "other":
                self._wb.config(text="ℹ "+L.t("manual"), fg=TH["warn"])
            else:
                self._wb.config(text="")
        elif self._wb:
            self._wb.config(text="")

    def _on_freq(self, _=None):
        f = self._ent["freq"].get().strip()
        if not f: return
        b = freq_to_band(f)
        if b:
            ab = self._cc().get("allowed_bands", BANDS_ALL) or BANDS_ALL
            if b in ab: self._ent["band"].set(b)

    def _on_band(self, _=None):
        b = self._ent["band"].get()
        if not self._ent["freq"].get().strip():
            self._ent["freq"].delete(0,"end")
            self._ent["freq"].insert(0, str(BAND_DEFAULT_FREQ.get(b,"")))

    def _on_mode(self, _=None):
        m = self._ent["mode"].get()
        rst = RST_DEF.get(m,"59")
        for k in ("rst_s","rst_r"):
            self._ent[k].delete(0,"end")
            self._ent[k].insert(0, rst)

    def _tog_man(self):
        m = self._man_v.get()
        st = "normal" if m else "disabled"
        for k in ("date","time"):
            if k in self._ent:
                self._ent[k].config(state=st)
        if hasattr(self,"_led_cv") and self._led_cv:
            self._led_cv.itemconfig(self._led,
                fill=TH["led_off"] if m else TH["led_on"])
        if hasattr(self,"_led_lbl") and self._led_lbl:
            self._led_lbl.config(
                text=L.t("offline") if m else L.t("online"),
                fg=TH["led_off"] if m else TH["led_on"])
        self.cfg["manual_dt"] = m

    def _get_dt(self):
        if self._man_v.get():
            return (self._ent["date"].get().strip(),
                    self._ent["time"].get().strip())
        now = datetime.datetime.utcnow()
        return now.strftime("%Y-%m-%d"), now.strftime("%H:%M")

    def _on_lang(self, _=None):
        L.set(self._lang_v.get())
        self.cfg["lang"] = L.get()
        DM.save("config.json", self.cfg)
        self._rebuild()

    def _on_contest(self, _=None):
        DM.save_log(self._cid(), self.log)
        self.cfg["contest"] = self._cv.get()
        DM.save("config.json", self.cfg)
        self.log = DM.load_log(self._cid())
        self.serial = max((int(q.get("ss","0") or 0)
                           for q in self.log if q.get("ss","").isdigit()),
                          default=0) + 1
        self._rebuild()

    def _rclick(self, e):
        item = self.tree.identify_row(e.y)
        if item:
            self.tree.selection_set(item)
            self._ctx.post(e.x_root, e.y_root)

    def _sort(self, col):
        if self._sort_col == col:
            self._sort_rev = not self._sort_rev
        else:
            self._sort_col = col; self._sort_rev = False
        items = [(self.tree.set(k,col),k) for k in self.tree.get_children("")]
        try:
            items.sort(key=lambda x: float(x[0]) if x[0].lstrip("-").replace(".","").isdigit()
                       else x[0], reverse=self._sort_rev)
        except Exception:
            items.sort(key=lambda x: x[0], reverse=self._sort_rev)
        for i,(_, k) in enumerate(items):
            self.tree.move(k,"",i)

    def _cycle_band(self):
        ab = self._cc().get("allowed_bands", BANDS_ALL) or BANDS_ALL
        if not ab: return
        cur = self._ent["band"].get()
        idx = ((ab.index(cur)+1) % len(ab)) if cur in ab else 0
        self._ent["band"].set(ab[idx]); self._on_band()

    def _cycle_mode(self):
        am = self._cc().get("allowed_modes", MODES_ALL) or MODES_ALL
        if not am: return
        cur = self._ent["mode"].get()
        idx = ((am.index(cur)+1) % len(am)) if cur in am else 0
        self._ent["mode"].set(am[idx]); self._on_mode()

    def _save_cat(self):
        cats = self._cc().get("categories",[]) or []
        v = self._cat_v.get() if hasattr(self,"_cat_v") else ""
        self.cfg["cat_idx"] = cats.index(v) if v in cats else 0
        if self._jud_v:
            self.cfg["county"] = self._jud_v.get()
        DM.save("config.json", self.cfg)
        self._upd_info()

    # ══════════════════════════════════════════════════════════════════════════
    #  TICKERS
    # ══════════════════════════════════════════════════════════════════════════

    def _tick_clock(self):
        try:
            if not self.winfo_exists(): return
            if hasattr(self,"_clk") and self._clk:
                self._clk.config(
                    text=f"UTC {datetime.datetime.utcnow().strftime('%H:%M:%S')}")
            self.after(1000, self._tick_clock)
        except Exception: pass

    def _tick_save(self):
        try:
            if not self.winfo_exists(): return
            DM.save_log(self._cid(), self.log)
            self.after(60000, self._tick_save)
        except Exception: pass

    # ══════════════════════════════════════════════════════════════════════════
    #  REBUILD (language / contest switch)
    # ══════════════════════════════════════════════════════════════════════════

    def _rebuild(self):
        try: self.cfg["win_geo"] = self.geometry()
        except: pass
        for w in self.winfo_children():
            w.destroy()
        self._ent = {}; self.edit_idx = None
        self._wb = self._log_btn = None
        self._info = self._sc_lbl = self._clk = self._rate = None
        self._led_cv = self._led = self._led_lbl = None
        self.tree = None
        self._cv = self._ccb = self._lang_v = None
        self._man_v = self._cat_v = self._jud_v = None
        self._fb_v = self._fm_v = None
        self._style()
        self._menu()
        self._ui()
        self._refresh()

    def _switch(self, cid):
        DM.save_log(self._cid(), self.log)
        self.cfg["contest"] = cid
        DM.save("config.json", self.cfg)
        self.log    = DM.load_log(cid)
        self.serial = max((int(q.get("ss","0") or 0)
                           for q in self.log if q.get("ss","").isdigit()),
                          default=0) + 1
        self._rebuild()

    def _fsave(self):
        DM.save_log(self._cid(), self.log)
        DM.save("config.json", self.cfg)
        DM.save("contests.json", self.contests)
        if self._sounds(): _beep("ok")

    # ══════════════════════════════════════════════════════════════════════════
    #  DIALOGS
    # ══════════════════════════════════════════════════════════════════════════

    def _mgr(self):
        d = ContestMgr(self, self.contests)
        self.wait_window(d)
        if d.result:
            self.contests = d.result
            DM.save("contests.json", self.contests)
            self._rebuild()

    def _settings(self):
        dlg = tk.Toplevel(self)
        dlg.title(L.t("settings_title"))
        dlg.geometry("420x480"); dlg.configure(bg=TH["bg"])
        dlg.resizable(False, False); dlg.transient(self); dlg.grab_set()
        eo = {"bg":TH["entry"],"fg":TH["fg"],"insertbackground":TH["fg"],
               "relief":"flat","bd":4,"font":("Consolas",11)}
        lo = {"bg":TH["bg"],"fg":TH["fg2"],"font":("Consolas",10),"anchor":"w"}
        ws = {}
        for key, lbl, val in [
            ("call",    L.t("lbl_call"),   self.cfg.get("call","")),
            ("loc",     L.t("lbl_loc"),    self.cfg.get("loc","")),
            ("jud",     L.t("lbl_jud"),    self.cfg.get("jud","")),
            ("addr",    L.t("lbl_addr"),   self.cfg.get("addr","")),
            ("op_name", L.t("lbl_op"),     self.cfg.get("op_name","")),
            ("power",   L.t("lbl_pwr"),    self.cfg.get("power","100")),
            ("fs",      L.t("lbl_font"),   str(self.cfg.get("fs",11))),
        ]:
            tk.Label(dlg, text=lbl, **lo).pack(anchor="w", padx=14, pady=(4,0))
            e = tk.Entry(dlg, width=38, **eo)
            e.insert(0, val); e.pack(fill="x", padx=14, ipady=3)
            ws[key] = e
        snd_v = tk.BooleanVar(value=self.cfg.get("sounds",True))
        tk.Checkbutton(dlg, text=L.t("lbl_sounds"), variable=snd_v,
                       bg=TH["bg"], fg=TH["fg"], selectcolor=TH["entry"],
                       activebackground=TH["bg"],
                       font=("Consolas",11)).pack(anchor="w", padx=14, pady=6)
        def _save():
            for k in ws:
                v = ws[k].get().strip()
                self.cfg[k] = v.upper() if k in ("call","loc","jud") else v
            try:    self.cfg["fs"] = max(9,min(16,int(ws["fs"].get().strip())))
            except: self.cfg["fs"] = 11
            self.cfg["sounds"] = snd_v.get()
            DM.save("config.json", self.cfg)
            dlg.destroy(); self._rebuild()
        tk.Button(dlg, text=L.t("save"), command=_save,
                  bg=TH["accent"], fg="white", font=("Consolas",12,"bold"),
                  width=16, relief="flat", cursor="hand2").pack(pady=12)

    def _stats(self):
        StatsWin(self, self.log, self._cc(), self.cfg)

    def _validate(self):
        ok, msg, _ = Score.validate(self.log, self._cc(), self.cfg)
        (messagebox.showinfo if ok else messagebox.showwarning)(
            L.t("val_title"), msg)

    def _search(self):
        SearchDlg(self, self.log)

    def _timer(self):
        TimerDlg(self)

    def _about(self):
        dlg = tk.Toplevel(self)
        dlg.title(L.t("menu_about")); dlg.geometry("440x280")
        dlg.configure(bg=TH["bg"]); dlg.transient(self)
        tk.Label(dlg, text="📻 YO Log PRO v17.0",
                 bg=TH["bg"], fg=TH["accent"],
                 font=("Consolas",16,"bold")).pack(pady=10)
        tk.Label(dlg, text=L.t("about_text"),
                 bg=TH["bg"], fg=TH["fg"],
                 font=("Consolas",9), justify="center").pack()
        tk.Button(dlg, text=L.t("close"), command=dlg.destroy,
                  bg=TH["btn"], fg=TH["btn_fg"], relief="flat",
                  width=12, cursor="hand2").pack(pady=10)

    def _verify(self):
        try:
            h = hashlib.md5(
                json.dumps(self.log, ensure_ascii=False,
                           sort_keys=True).encode()).hexdigest()
            messagebox.showinfo("MD5", L.t("verify_ok", len(self.log), h))
        except Exception as e:
            messagebox.showerror(L.t("err"), str(e))

    def _clear_log(self):
        if not self.log: return
        if messagebox.askyesno(L.t("clear_title"), L.t("clear_msg")):
            DM.backup(self._cid(), self.log)
            self.log.clear(); self.serial = 1; self.undo_stack.clear()
            self._refresh(); DM.save_log(self._cid(), self.log)

    # ── import ────────────────────────────────────────────────────────────────
    def _import(self):
        dlg = tk.Toplevel(self); dlg.title(L.t("btn_import"))
        dlg.geometry("240,140".replace(",","x")); dlg.configure(bg=TH["bg"])
        dlg.transient(self)
        tk.Button(dlg, text="ADIF (.adi / .adif)",
                  command=lambda:[dlg.destroy(),self._imp_adif()],
                  bg=TH["accent"], fg="white", width=24, relief="flat",
                  cursor="hand2").pack(pady=8)
        tk.Button(dlg, text="CSV (.csv)",
                  command=lambda:[dlg.destroy(),self._imp_csv()],
                  bg=TH["accent"], fg="white", width=24, relief="flat",
                  cursor="hand2").pack(pady=4)

    def _imp_adif(self):
        fp = filedialog.askopenfilename(
            filetypes=[("ADIF","*.adi *.adif"),("All","*.*")])
        if not fp: return
        try:
            with open(fp,"r",encoding="utf-8",errors="replace") as f:
                qsos = Imp.adif(f.read())
            if not qsos:
                messagebox.showwarning("",L.t("imp_none")); return
            self.log.extend(qsos); self._refresh()
            DM.save_log(self._cid(), self.log)
            messagebox.showinfo("OK", L.t("imp_ok",len(qsos)))
        except Exception as e:
            messagebox.showerror(L.t("err"), str(e))

    def _imp_csv(self):
        fp = filedialog.askopenfilename(
            filetypes=[("CSV","*.csv"),("All","*.*")])
        if not fp: return
        try:
            with open(fp,"r",encoding="utf-8",errors="replace") as f:
                qsos = Imp.csv_file(f.read())
            if not qsos:
                messagebox.showwarning("",L.t("imp_none")); return
            self.log.extend(qsos); self._refresh()
            DM.save_log(self._cid(), self.log)
            messagebox.showinfo("OK", L.t("imp_ok",len(qsos)))
        except Exception as e:
            messagebox.showerror(L.t("err"), str(e))

    # ── export ────────────────────────────────────────────────────────────────
    def _export(self):
        dlg = tk.Toplevel(self); dlg.title(L.t("btn_export"))
        dlg.geometry("250x220"); dlg.configure(bg=TH["bg"])
        dlg.transient(self)
        for txt, cmd in [
            ("Cabrillo 3.0 (.log)", lambda:[dlg.destroy(),self._exp_cabrillo()]),
            ("ADIF 3.1 (.adi)",     lambda:[dlg.destroy(),self._exp_adif()]),
            ("CSV (.csv)",          lambda:[dlg.destroy(),self._exp_csv()]),
            ("EDI (.edi)",          lambda:[dlg.destroy(),self._exp_edi()]),
            ("Print (.txt)",        lambda:[dlg.destroy(),self._exp_print()]),
        ]:
            tk.Button(dlg, text=txt, command=cmd, bg=TH["accent"], fg="white",
                      width=26, relief="flat", cursor="hand2").pack(pady=4)

    def _exp_cabrillo(self):
        try:
            my = self.cfg.get("call","NOCALL")
            cc = self._cc()
            nm = cc.get("name_en", cc.get("name_ro","CONTEST"))
            pw = int(self.cfg.get("power","100"))
            cat_pwr = "QRP" if pw<=5 else ("LOW" if pw<=100 else "HIGH")
            lines = [
                "START-OF-LOG: 3.0",
                f"CONTEST: {nm}",
                f"CALLSIGN: {my}",
                f"GRID-LOCATOR: {self.cfg.get('loc','')}",
                f"CATEGORY-OPERATOR: SINGLE-OP",
                f"CATEGORY-BAND: ALL",
                f"CATEGORY-POWER: {cat_pwr}",
                f"CATEGORY-MODE: MIXED",
                f"NAME: {self.cfg.get('op_name','')}",
                f"ADDRESS: {self.cfg.get('addr','')}",
                "SOAPBOX: Logged with YO Log PRO v17.0",
                "CREATED-BY: YO Log PRO v17.0",
            ]
            for q in self.log:
                freq  = q.get("f","") or str(BAND_DEFAULT_FREQ.get(q.get("b",""),0))
                mode  = q.get("m","SSB")
                date  = q.get("d","").replace("-","")
                time  = q.get("t","").replace(":","")
                call  = q.get("c","")
                rst_s = q.get("s","59"); rst_r = q.get("r","59")
                ex_s  = q.get("ss", q.get("n",""))
                ex_r  = q.get("sr", q.get("n",""))
                lines.append(
                    f"QSO: {freq:>6} {mode:<5} {date} {time} "
                    f"{my:<13} {rst_s:<4} {ex_s:<10} "
                    f"{call:<13} {rst_r:<4} {ex_r}")
            lines.append("END-OF-LOG:")
            fn = f"cabrillo_{self._cid()}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.log"
            fp = os.path.join(_data_dir(), fn)
            with open(fp,"w",encoding="utf-8") as f: f.write("\n".join(lines))
            messagebox.showinfo(L.t("btn_export"), L.t("exp_ok",fn))
        except Exception as e:
            messagebox.showerror(L.t("err"), str(e))

    def _exp_adif(self):
        try:
            my_loc = self.cfg.get("loc","")
            lines  = [
                "<ADIF_VER:5>3.1.0",
                "<PROGRAMID:14>YO_Log_PRO_v17",
                f"<MY_GRIDSQUARE:{len(my_loc)}>{my_loc}",
                "<EOH>",
            ]
            def af(tag, val):
                val = str(val)
                return f"<{tag}:{len(val)}>{val}" if val else ""
            for q in self.log:
                dc  = q.get("d","").replace("-","")
                tc  = q.get("t","").replace(":","")+"00"
                fr  = q.get("f","")
                fmhz = ""
                if fr:
                    try: fmhz = f"{float(fr)/1000:.4f}"
                    except: pass
                note = q.get("n","")
                parts = [
                    af("CALL",q.get("c","")), af("BAND",q.get("b","40m")),
                    af("MODE",q.get("m","SSB")), af("QSO_DATE",dc),
                    af("TIME_ON",tc), af("RST_SENT",q.get("s","59")),
                    af("RST_RCVD",q.get("r","59")),
                ]
                if fmhz: parts.append(af("FREQ",fmhz))
                if Loc.valid(note[:6] if len(note)>=6 else note):
                    parts.append(af("GRIDSQUARE",note))
                elif note:
                    parts.append(af("COMMENT",note))
                if q.get("ss"): parts.append(af("STX",q["ss"]))
                if q.get("sr"): parts.append(af("SRX",q["sr"]))
                parts.append("<EOR>")
                lines.append("".join(p for p in parts if p))
            fn = f"adif_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.adi"
            fp = os.path.join(_data_dir(), fn)
            with open(fp,"w",encoding="utf-8") as f: f.write("\n".join(lines))
            messagebox.showinfo(L.t("btn_export"), L.t("exp_ok",fn))
        except Exception as e:
            messagebox.showerror(L.t("err"), str(e))

    def _exp_csv(self):
        try:
            fn = f"log_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv"
            fp = os.path.join(_data_dir(), fn)
            cc = self._cc()
            with open(fp,"w",encoding="utf-8",newline="") as f:
                w = csv.writer(f)
                w.writerow(["Nr","Date","Time","Call","Freq","Band","Mode",
                             "RST_S","RST_R","Nr_S","Nr_R","Note","Country","Pts"])
                for i, q in enumerate(self.log):
                    cty, _ = dxcc_lookup(q.get("c",""))
                    w.writerow([
                        len(self.log)-i,
                        q.get("d",""), q.get("t",""), q.get("c",""),
                        q.get("f",""), q.get("b",""), q.get("m",""),
                        q.get("s",""), q.get("r",""),
                        q.get("ss",""), q.get("sr",""),
                        q.get("n",""),
                        "" if cty=="Unknown" else cty,
                        Score.qso_pts(q,cc,self.cfg)
                    ])
            messagebox.showinfo(L.t("btn_export"), L.t("exp_ok",fn))
        except Exception as e:
            messagebox.showerror(L.t("err"), str(e))

    def _exp_edi(self):
        try:
            my = self.cfg.get("call","NOCALL")
            cc = self._cc()
            nm = cc.get("name_en", cc.get("name_ro","VHF"))
            now = datetime.datetime.utcnow()
            lines = [
                "[REG1TEST;1]",
                f"TName={nm}",
                f"TDate={now.strftime('%y%m%d')};{now.strftime('%y%m%d')}",
                f"PCall={my}", f"PWWLo={self.cfg.get('loc','')}",
                f"PAdr1={self.cfg.get('addr','')}",
                "PBand=144","PSect=","[Remarks]",
                "Logged with YO Log PRO v17.0","[QSORecords]",
            ]
            for q in self.log:
                dt   = q.get("d","").replace("-","")[2:]
                tm   = q.get("t","").replace(":","")[:4]
                loc  = q.get("n","")
                km   = int(Loc.dist(self.cfg.get("loc",""), loc)) \
                       if loc and Loc.valid(loc) else 0
                lines.append(
                    f"{dt};{tm};{q.get('c','')};1;"
                    f"{q.get('s','59')};{q.get('ss','')};"
                    f"{q.get('r','59')};{q.get('sr','')};{loc};{km}")
            fn = f"edi_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.edi"
            fp = os.path.join(_data_dir(), fn)
            with open(fp,"w",encoding="utf-8") as f: f.write("\n".join(lines))
            messagebox.showinfo(L.t("btn_export"), L.t("exp_ok",fn))
        except Exception as e:
            messagebox.showerror(L.t("err"), str(e))

    def _exp_print(self):
        try:
            my  = self.cfg.get("call","NOCALL")
            cc  = self._cc()
            nm  = cc.get("name_"+L.get(), cc.get("name_ro","?"))
            now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
            W   = 100
            lines = [
                "="*W,
                f"  YO Log PRO v17.0   {my}   {nm}   {now}",
                "="*W,
                f"{'Nr':<5}{'Call':<13}{'Freq':<8}{'Band':<7}{'Mode':<7}"
                f"{'RST-T':<6}{'RST-R':<6}{'Note':<11}{'Country':<16}"
                f"{'Date':<12}{'Time':<7}{'Pts'}",
                "-"*W,
            ]
            for i, q in enumerate(self.log):
                cty, _ = dxcc_lookup(q.get("c",""))
                pts    = Score.qso_pts(q, cc, self.cfg)
                lines.append(
                    f"{len(self.log)-i:<5}{q.get('c',''):<13}"
                    f"{q.get('f',''):<8}{q.get('b',''):<7}{q.get('m',''):<7}"
                    f"{q.get('s',''):<6}{q.get('r',''):<6}"
                    f"{q.get('n',''):<11}"
                    f"{('' if cty=='Unknown' else cty)[:15]:<16}"
                    f"{q.get('d',''):<12}{q.get('t',''):<7}{pts}")
            lines.append("="*W)
            qp, mc, tot = Score.total(self.log, cc, self.cfg)
            lines.append(f"  Total: {len(self.log)} QSO   Score: {qp}×{mc}={tot}")
            fn = f"print_{self._cid()}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt"
            fp = os.path.join(_data_dir(), fn)
            with open(fp,"w",encoding="utf-8") as f: f.write("\n".join(lines))
            messagebox.showinfo(L.t("btn_export"), L.t("exp_ok",fn))
        except Exception as e:
            messagebox.showerror(L.t("err"), str(e))

    def _print(self):
        self._exp_print()

    # ── backup / exit ─────────────────────────────────────────────────────────
    def _backup(self):
        if DM.backup(self._cid(), self.log):
            messagebox.showinfo("OK", L.t("bak_ok"))
        else:
            messagebox.showerror(L.t("err"), L.t("bak_err"))

    def _exit(self):
        if messagebox.askyesno(L.t("exit_title"), L.t("exit_msg")):
            try: self.cfg["win_geo"] = self.geometry()
            except: pass
            DM.save_log(self._cid(), self.log)
            DM.save("config.json", self.cfg)
            DM.save("contests.json", self.contests)
            DM.backup(self._cid(), self.log)
            self.destroy()


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = App()
    app.mainloop()
