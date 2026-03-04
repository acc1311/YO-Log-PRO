#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YO Log PRO v16.0 FINAL — Professional Multi-Contest Amateur Radio Logger
Developed by: Ardei Constantin-Cătălin (YO8ACR)
Email: yo8acr@gmail.com

FINAL EDITION — All features, all fixes, production-ready.
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
from collections import Counter, OrderedDict, deque
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


# =============================================================================
# UTILITIES
# =============================================================================

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


# =============================================================================
# LOCATOR UTILITIES (Maidenhead + Haversine)
# =============================================================================

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
        a_ = (math.sin(d1 / 2) ** 2 +
              math.cos(math.radians(la1)) * math.cos(math.radians(la2)) *
              math.sin(d2 / 2) ** 2)
        return round(R * 2 * math.atan2(math.sqrt(a_), math.sqrt(1 - a_)), 1)

    @staticmethod
    def valid(s):
        s = s.upper().strip()
        if len(s) == 4:
            return s[0:2].isalpha() and s[2:4].isdigit() and 'A' <= s[0] <= 'R' and 'A' <= s[1] <= 'R'
        if len(s) == 6:
            return (s[0:2].isalpha() and s[2:4].isdigit() and s[4:6].isalpha() and
                    'A' <= s[0] <= 'R' and 'A' <= s[1] <= 'R' and 'A' <= s[4] <= 'X' and 'A' <= s[5] <= 'X')
        return False


# =============================================================================
# DXCC DATABASE (150+ prefixes)
# =============================================================================

class DXCC:
    DB = {
        "YO":"Romania","YP":"Romania","YQ":"Romania","YR":"Romania",
        "DL":"Germany","DJ":"Germany","DK":"Germany","DA":"Germany","DB":"Germany",
        "DC":"Germany","DD":"Germany","DF":"Germany","DG":"Germany","DH":"Germany","DM":"Germany",
        "G":"England","M":"England","2E":"England","GW":"Wales","GM":"Scotland","GI":"N. Ireland",
        "GD":"Isle of Man","GJ":"Jersey","GU":"Guernsey",
        "F":"France","TM":"France","HB9":"Switzerland","HB":"Switzerland",
        "I":"Italy","IK":"Italy","IZ":"Italy","IW":"Italy","IN3":"Italy",
        "EA":"Spain","EB":"Spain","EC":"Spain","EE":"Spain",
        "CT":"Portugal","CS":"Portugal","CU":"Azores",
        "SP":"Poland","SQ":"Poland","SN":"Poland","SO":"Poland","3Z":"Poland",
        "HA":"Hungary","HG":"Hungary",
        "OK":"Czech Rep.","OL":"Czech Rep.",
        "OM":"Slovak Rep.",
        "LZ":"Bulgaria",
        "UR":"Ukraine","US":"Ukraine","UT":"Ukraine","UX":"Ukraine","UY":"Ukraine",
        "UA":"Russia","RU":"Russia","RV":"Russia","RW":"Russia","RA":"Russia",
        "R1":"Russia","R3":"Russia","R6":"Russia","R9":"Russia",
        "OE":"Austria",
        "ON":"Belgium","OO":"Belgium","OR":"Belgium","OT":"Belgium",
        "PA":"Netherlands","PB":"Netherlands","PD":"Netherlands","PE":"Netherlands",
        "PH":"Netherlands","PI":"Netherlands",
        "OZ":"Denmark","OU":"Denmark","5Q":"Denmark",
        "SM":"Sweden","SA":"Sweden","SB":"Sweden","SK":"Sweden",
        "LA":"Norway","LB":"Norway","LC":"Norway",
        "OH":"Finland","OF":"Finland","OG":"Finland","OI":"Finland",
        "ES":"Estonia",
        "YL":"Latvia",
        "LY":"Lithuania",
        "9A":"Croatia",
        "S5":"Slovenia","S51":"Slovenia","S52":"Slovenia","S57":"Slovenia",
        "E7":"Bosnia",
        "Z3":"N. Macedonia","Z6":"Kosovo",
        "ZA":"Albania",
        "SV":"Greece","SW":"Greece","SX":"Greece","SY":"Greece",
        "TA":"Turkey","TC":"Turkey","YM":"Turkey",
        "4X":"Israel","4Z":"Israel",
        "SU":"Egypt","SU9":"Egypt",
        "CN":"Morocco",
        "7X":"Algeria",
        "3V":"Tunisia",
        "5A":"Libya",
        "ST":"Sudan",
        "ZS":"South Africa","ZR":"South Africa","ZU":"South Africa",
        "5Z":"Kenya","5H":"Tanzania","9J":"Zambia","9Q":"DR Congo",
        "5N":"Nigeria","5V":"Togo","5X":"Uganda",
        "W":"USA","K":"USA","N":"USA","AA":"USA","AB":"USA","AC":"USA",
        "AD":"USA","AE":"USA","AF":"USA","AG":"USA","AI":"USA","AK":"USA",
        "KH6":"Hawaii","KL7":"Alaska","KP4":"Puerto Rico",
        "VE":"Canada","VA":"Canada","VY":"Canada","VO":"Canada",
        "XE":"Mexico","XA":"Mexico","4A":"Mexico",
        "PY":"Brazil","PP":"Brazil","PR":"Brazil","PS":"Brazil","PT":"Brazil","PU":"Brazil",
        "LU":"Argentina","LW":"Argentina","LO":"Argentina",
        "CE":"Chile","CA":"Chile","XQ":"Chile",
        "HK":"Colombia","HJ":"Colombia",
        "HC":"Ecuador","HD":"Ecuador",
        "OA":"Peru","OB":"Peru",
        "CX":"Uruguay",
        "YV":"Venezuela","YW":"Venezuela","YX":"Venezuela",
        "HI":"Dominican Rep.","HH":"Haiti","CO":"Cuba","CM":"Cuba",
        "HP":"Panama","HR":"Honduras","TG":"Guatemala","YS":"El Salvador",
        "TI":"Costa Rica","V3":"Belize","J7":"Dominica",
        "JA":"Japan","JH":"Japan","JR":"Japan","JE":"Japan","JF":"Japan",
        "JG":"Japan","JI":"Japan","JJ":"Japan","JK":"Japan","JL":"Japan",
        "JM":"Japan","JN":"Japan","JO":"Japan","JP":"Japan","JS":"Japan",
        "BV":"Taiwan","BM":"Taiwan","BN":"Taiwan","BO":"Taiwan","BP":"Taiwan",
        "BY":"China","BA":"China","BD":"China","BG":"China","BI":"China",
        "HL":"S. Korea","DS":"S. Korea","6K":"S. Korea",
        "DU":"Philippines","DX":"Philippines",
        "HS":"Thailand","E2":"Thailand",
        "9M":"W. Malaysia","9W":"W. Malaysia",
        "YB":"Indonesia","YC":"Indonesia","YD":"Indonesia","YE":"Indonesia",
        "VK":"Australia","AX":"Australia",
        "ZL":"New Zealand","ZM":"New Zealand",
        "VU":"India","AT":"India","VT":"India",
        "AP":"Pakistan","AS":"Pakistan",
        "S2":"Bangladesh",
        "4S":"Sri Lanka",
        "A4":"Oman","A6":"UAE","A7":"Qatar","A9":"Bahrain",
        "9K":"Kuwait","HZ":"Saudi Arabia","7Z":"Saudi Arabia",
        "EK":"Armenia","4J":"Azerbaijan","4L":"Georgia",
        "EX":"Kyrgyzstan","UN":"Kazakhstan","EY":"Tajikistan","UK":"Uzbekistan",
        "JT":"Mongolia",
        "XV":"Vietnam","3W":"Vietnam",
        "9N":"Nepal","A5":"Bhutan",
        "P2":"Papua New Guinea","H4":"Solomon Is.",
        "V8":"Brunei","XW":"Laos","XU":"Cambodia",
        "ZK":"Niue","FK":"New Caledonia","FO":"Fr. Polynesia",
        "VP9":"Bermuda","VP5":"Turks & Caicos","VP2":"Anguilla",
        "ZB":"Gibraltar","EA6":"Balearic Is.",
        "SV5":"Dodecanese","SV9":"Crete",
        "IS":"Sardinia","IT9":"Sicily",
        "TF":"Iceland","JX":"Jan Mayen","JW":"Svalbard",
        "OX":"Greenland","OY":"Faroe Is.",
        "T7":"San Marino","3A":"Monaco","C3":"Andorra",
        "HV":"Vatican","1A":"Sov. Mil. Order Malta",
        "9H":"Malta","ZC4":"UK Sov. Cyprus","5B":"Cyprus",
        "4O":"Montenegro","E7":"Bosnia-Herz.",
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


# =============================================================================
# FREQUENCY UTILITIES
# =============================================================================

FREQ_MAP = {
    (1800,2000):"160m",(3500,3800):"80m",(5351,5367):"60m",(7000,7200):"40m",
    (10100,10150):"30m",(14000,14350):"20m",(18068,18168):"17m",
    (21000,21450):"15m",(24890,24990):"12m",(28000,29700):"10m",
    (50000,54000):"6m",(144000,148000):"2m",(430000,440000):"70cm",
    (1240000,1300000):"23cm",
}

BAND_FREQ = {
    "160m":1850,"80m":3700,"60m":5355,"40m":7100,"30m":10120,
    "20m":14200,"17m":18120,"15m":21200,"12m":24940,"10m":28500,
    "6m":50150,"2m":145000,"70cm":432200,"23cm":1296200,
}

RST_DEFAULTS = {
    "SSB":"59","AM":"59","FM":"59",
    "CW":"599","RTTY":"599","PSK31":"599",
    "DIGI":"599","FT8":"-10","FT4":"-10","JT65":"-15","SSTV":"59",
}


def freq2band(f):
    try:
        f = float(f)
        for (lo, hi), b in FREQ_MAP.items():
            if lo <= f <= hi:
                return b
    except:
        pass
    return None


# =============================================================================
# CONSTANTS
# =============================================================================

BANDS_HF = ["160m","80m","60m","40m","30m","20m","17m","15m","12m","10m"]
BANDS_VHF = ["6m","2m"]
BANDS_UHF = ["70cm","23cm"]
BANDS_ALL = BANDS_HF + BANDS_VHF + BANDS_UHF
MODES_ALL = ["SSB","CW","DIGI","FT8","FT4","RTTY","AM","FM","PSK31","SSTV","JT65"]
SCORING_MODES = ["none","per_qso","per_band","maraton","multiplier","distance","custom"]
CONTEST_TYPES = ["Simplu","Maraton","Stafeta","YO","DX","VHF","UHF",
                 "Field Day","Sprint","QSO Party","SOTA","POTA","Custom"]

YO_COUNTIES = [
    "AB","AR","AG","BC","BH","BN","BT","BV","BR","BZ","CS","CL","CJ","CT","CV",
    "DB","DJ","GL","GR","GJ","HR","HD","IL","IS","IF","MM","MH","MS","NT","OT",
    "PH","SM","SJ","SB","SV","TR","TM","TL","VS","VL","VN","B",
]

T = {
    "ro": {
        "app_title":"YO Log PRO v16.0 FINAL","call":"Indicativ","band":"Bandă","mode":"Mod",
        "rst_s":"RST S","rst_r":"RST R","serial_s":"Nr S","serial_r":"Nr R",
        "freq":"Frecv (kHz)","note":"Notă/Locator","log":"LOG","update":"ACTUALIZEAZĂ",
        "search":"🔍 Caută","reset":"Reset","settings":"⚙ Setări",
        "stats":"📊 Statistici","validate":"✅ Validează","export":"📤 Export",
        "import_log":"📥 Import","delete":"Șterge","backup":"💾 Backup",
        "online":"Online UTC","offline":"Manual","category":"Categorie","county":"Județ",
        "req_st":"Stații Obligatorii","worked":"Stații Lucrate","total_score":"Scor Total",
        "val_result":"Validare","date_l":"Dată:","time_l":"Oră:","manual":"Manual",
        "confirm_del":"Confirmare","confirm_del_t":"Sigur ștergeți?",
        "bak_ok":"Backup creat!","bak_err":"Eroare backup!",
        "exit_t":"Ieșire","exit_m":"Salvați înainte de ieșire?",
        "help":"Ajutor","about":"Despre","save":"Salvează","close":"Închide",
        "credits":"Dezvoltat de:\nArdei Constantin-Cătălin (YO8ACR)\nyo8acr@gmail.com",
        "usage":"Ctrl+F=Caută  Ctrl+Z=Undo  Ctrl+S=Save  F2=Bandă+  F3=Mod+  Enter=LOG",
        "edit_qso":"Editează","delete_qso":"Șterge","data":"Data","ora":"Ora",
        "sel_fmt":"Format:","cancel":"Anulează","exp_ok":"Export reușit!","error":"Eroare",
        "sett_ok":"Setări salvate!","locator":"Locator:","address":"Adresă:",
        "font_size":"Font:","station_info":"Info Stație:",
        "contest_mgr":"Manager Concursuri","contests":"Concursuri",
        "add_c":"➕ Adaugă","edit_c":"✏ Editează","del_c":"🗑 Șterge","dup_c":"📋 Duplică",
        "c_name":"Nume Concurs:","c_type":"Tip:","sc_mode":"Punctare:",
        "cats":"Categorii:","a_bands":"Benzi:","a_modes":"Moduri:",
        "req_st_c":"Stații Obligatorii:","sp_sc":"Punctare Specială:",
        "ppq":"Puncte/QSO:","min_qso":"Min QSO:","use_serial":"Nr. Seriale",
        "use_county":"Județ","county_list":"Județe:","no_sel":"Neselectat!",
        "del_c_conf":"Ștergeți '{}'?","c_saved":"Salvat!","c_del":"Șters!",
        "c_exists":"ID existent!","c_default":"Protejat!","c_id":"ID Concurs:",
        "mults":"Multiplicatori:","band_pts":"Puncte/Bandă:","nr":"Nr.","pts":"Pt",
        "imp_c":"📥 Import","exp_c":"📤 Export",
        "dup_warn":"⚠ Duplicat!","dup_msg":"{} pe {} {}!\nQSO #{}\n\nAdăugați?",
        "search_t":"Căutare","search_l":"Caută:","results":"Rezultate",
        "no_res":"Nimic găsit.","undo":"↩ Undo","undo_ok":"Anulat.",
        "undo_empty":"Nimic de anulat.","rate":"QSO/h","timer":"⏱ Timer",
        "timer_t":"Timer","timer_start":"▶ Start","timer_stop":"⏸ Stop",
        "timer_reset":"⏹ Reset","elapsed":"Scurs:","remaining":"Rămas:",
        "dur_h":"Durată (h):","band_sum":"Benzi","distance":"Dist",
        "country":"Țara","utc":"UTC","autosaved":"Salvat",
        "sounds":"Sunete","en_sounds":"Activează sunete",
        "qso_pts":"Puncte QSO","mult_c":"Multiplicatori","new_mult":"✦ MULT NOU!",
        "op":"Operator:","power":"Putere (W):","f_band":"Bandă:","f_mode":"Mod:",
        "all":"Toate","clear_log":"🗑 Golire","clear_conf":"Goliți COMPLET logul?\nIREVERSIBIL!",
        "wb":"Lucrat","imp_adif":"Import ADIF","imp_csv":"Import CSV",
        "imp_ok":"Importate {} QSO!","imp_err":"Eroare import!",
        "off_time":"Pauze","op_time":"Timp operare","qso_total":"Total QSO",
        "unique":"Unice","countries":"Țări","print_log":"🖨 Print",
        "verify":"Verificare log","verify_ok":"Log integru: {} QSO, hash: {}",
        "score_f":"Scor","worked_all":"Status Complet",
        "worked_x":"Lucrate: {}/{}","missing_x":"Lipsesc: {}",
    },
    "en": {
        "app_title":"YO Log PRO v16.0 FINAL","call":"Callsign","band":"Band","mode":"Mode",
        "rst_s":"RST S","rst_r":"RST R","serial_s":"Nr S","serial_r":"Nr R",
        "freq":"Freq (kHz)","note":"Note/Locator","log":"LOG","update":"UPDATE",
        "search":"🔍 Search","reset":"Reset","settings":"⚙ Settings",
        "stats":"📊 Stats","validate":"✅ Validate","export":"📤 Export",
        "import_log":"📥 Import","delete":"Delete","backup":"💾 Backup",
        "online":"Online UTC","offline":"Manual","category":"Category","county":"County",
        "req_st":"Required Stations","worked":"Stations Worked","total_score":"Total Score",
        "val_result":"Validation","date_l":"Date:","time_l":"Time:","manual":"Manual",
        "confirm_del":"Confirm","confirm_del_t":"Delete selected?",
        "bak_ok":"Backup created!","bak_err":"Backup error!",
        "exit_t":"Exit","exit_m":"Save before exit?",
        "help":"Help","about":"About","save":"Save","close":"Close",
        "credits":"Developed by:\nArdei Constantin-Cătălin (YO8ACR)\nyo8acr@gmail.com",
        "usage":"Ctrl+F=Search  Ctrl+Z=Undo  Ctrl+S=Save  F2=Band+  F3=Mode+  Enter=LOG",
        "edit_qso":"Edit","delete_qso":"Delete","data":"Date","ora":"Time",
        "sel_fmt":"Format:","cancel":"Cancel","exp_ok":"Export done!","error":"Error",
        "sett_ok":"Settings saved!","locator":"Locator:","address":"Address:",
        "font_size":"Font:","station_info":"Station Info:",
        "contest_mgr":"Contest Manager","contests":"Contests",
        "add_c":"➕ Add","edit_c":"✏ Edit","del_c":"🗑 Delete","dup_c":"📋 Duplicate",
        "c_name":"Contest Name:","c_type":"Type:","sc_mode":"Scoring:",
        "cats":"Categories:","a_bands":"Bands:","a_modes":"Modes:",
        "req_st_c":"Required Stations:","sp_sc":"Special Scoring:",
        "ppq":"Points/QSO:","min_qso":"Min QSO:","use_serial":"Serial Numbers",
        "use_county":"County","county_list":"Counties:","no_sel":"Not selected!",
        "del_c_conf":"Delete '{}'?","c_saved":"Saved!","c_del":"Deleted!",
        "c_exists":"ID exists!","c_default":"Protected!","c_id":"Contest ID:",
        "mults":"Multipliers:","band_pts":"Band Points:","nr":"Nr.","pts":"Pt",
        "imp_c":"📥 Import","exp_c":"📤 Export",
        "dup_warn":"⚠ Duplicate!","dup_msg":"{} on {} {}!\nQSO #{}\n\nAdd anyway?",
        "search_t":"Search","search_l":"Search:","results":"Results",
        "no_res":"No results.","undo":"↩ Undo","undo_ok":"Undone.",
        "undo_empty":"Nothing to undo.","rate":"QSO/h","timer":"⏱ Timer",
        "timer_t":"Timer","timer_start":"▶ Start","timer_stop":"⏸ Stop",
        "timer_reset":"⏹ Reset","elapsed":"Elapsed:","remaining":"Remaining:",
        "dur_h":"Duration (h):","band_sum":"Bands","distance":"Dist",
        "country":"Country","utc":"UTC","autosaved":"Saved",
        "sounds":"Sounds","en_sounds":"Enable sounds",
        "qso_pts":"QSO Points","mult_c":"Multipliers","new_mult":"✦ NEW MULT!",
        "op":"Operator:","power":"Power (W):","f_band":"Band:","f_mode":"Mode:",
        "all":"All","clear_log":"🗑 Clear","clear_conf":"Clear ENTIRE log?\nIRREVERSIBLE!",
        "wb":"Worked","imp_adif":"Import ADIF","imp_csv":"Import CSV",
        "imp_ok":"Imported {} QSOs!","imp_err":"Import error!",
        "off_time":"Off Time","op_time":"Op Time","qso_total":"Total QSO",
        "unique":"Unique","countries":"Countries","print_log":"🖨 Print",
        "verify":"Verify Log","verify_ok":"Log OK: {} QSOs, hash: {}",
        "score_f":"Score","worked_all":"Completion Status",
        "worked_x":"Worked: {}/{}","missing_x":"Missing: {}",
    }
}

DEFAULT_CONTESTS = {
    "simplu":{"name_ro":"Log Simplu","name_en":"Simple Log","contest_type":"Simplu",
        "categories":["Individual"],"scoring_mode":"none","points_per_qso":1,"min_qso":0,
        "allowed_bands":list(BANDS_ALL),"allowed_modes":list(MODES_ALL),
        "required_stations":[],"special_scoring":{},"use_serial":False,
        "use_county":False,"county_list":[],"multiplier_type":"none",
        "band_points":{},"is_default":True},
    "maraton":{"name_ro":"Maraton","name_en":"Marathon","contest_type":"Maraton",
        "categories":["A. Seniori YO","B. YL","C. Juniori YO","D. Club","E. DX","F. Receptori"],
        "scoring_mode":"maraton","points_per_qso":1,"min_qso":100,
        "allowed_bands":BANDS_HF+BANDS_VHF,"allowed_modes":list(MODES_ALL),
        "required_stations":[],"special_scoring":{},"use_serial":False,
        "use_county":True,"county_list":list(YO_COUNTIES),
        "multiplier_type":"county","band_points":{},"is_default":False},
    "stafeta":{"name_ro":"Ștafetă","name_en":"Relay","contest_type":"Stafeta",
        "categories":["A. Echipe Seniori","B. Echipe Juniori","C. Echipe Mixte"],
        "scoring_mode":"per_qso","points_per_qso":1,"min_qso":50,
        "allowed_bands":BANDS_HF,"allowed_modes":["SSB","CW"],
        "required_stations":[],"special_scoring":{},"use_serial":True,
        "use_county":True,"county_list":list(YO_COUNTIES),
        "multiplier_type":"county","band_points":{},"is_default":False},
    "yo-dx-hf":{"name_ro":"YO DX HF Contest","name_en":"YO DX HF Contest","contest_type":"DX",
        "categories":["A. SO AB High","B. SO AB Low","C. SO SB","D. MO Single TX","E. MO Multi TX"],
        "scoring_mode":"per_band","points_per_qso":1,"min_qso":0,
        "allowed_bands":["160m","80m","40m","20m","15m","10m"],"allowed_modes":["SSB","CW"],
        "required_stations":[],"special_scoring":{},"use_serial":True,
        "use_county":True,"county_list":list(YO_COUNTIES),
        "multiplier_type":"dxcc",
        "band_points":{"160m":4,"80m":3,"40m":2,"20m":1,"15m":1,"10m":2},
        "is_default":False},
    "yo-vhf":{"name_ro":"Contest VHF/UHF","name_en":"VHF/UHF Contest","contest_type":"VHF",
        "categories":["A. SO 2m","B. SO 70cm","C. Multi-Band"],
        "scoring_mode":"distance","points_per_qso":1,"min_qso":0,
        "allowed_bands":["2m","70cm","23cm"],"allowed_modes":["SSB","CW","FM"],
        "required_stations":[],"special_scoring":{},"use_serial":True,
        "use_county":False,"county_list":[],"multiplier_type":"grid",
        "band_points":{},"is_default":False},
    "field-day":{"name_ro":"Ziua Câmpului","name_en":"Field Day","contest_type":"Field Day",
        "categories":["A. 1-Op","B. 2-Op","C. Club"],
        "scoring_mode":"per_qso","points_per_qso":2,"min_qso":0,
        "allowed_bands":list(BANDS_ALL),"allowed_modes":list(MODES_ALL),
        "required_stations":[],"special_scoring":{},"use_serial":False,
        "use_county":False,"county_list":[],"multiplier_type":"none",
        "band_points":{},"is_default":False},
    "sprint":{"name_ro":"Sprint","name_en":"Sprint","contest_type":"Sprint",
        "categories":["A. Single-Op"],
        "scoring_mode":"per_qso","points_per_qso":1,"min_qso":0,
        "allowed_bands":BANDS_HF,"allowed_modes":["SSB","CW"],
        "required_stations":[],"special_scoring":{},"use_serial":True,
        "use_county":False,"county_list":[],"multiplier_type":"none",
        "band_points":{},"is_default":False},
}

DEFAULT_CFG = {
    "call":"YO8ACR","loc":"KN37","jud":"NT","addr":"","cat":0,"fs":11,
    "contest":"simplu","county":"NT","lang":"ro","manual_dt":False,
    "sounds":True,"op_name":"","power":"100",
    "win_geo":"","col_widths":{},
}

TH = {
    "bg":"#0d1117","fg":"#e6edf3","accent":"#1f6feb","entry_bg":"#161b22",
    "header_bg":"#010409","btn_bg":"#21262d","btn_fg":"#f0f6fc",
    "led_on":"#3fb950","led_off":"#f85149","warn":"#d29922","ok":"#3fb950",
    "err":"#f85149","dup_bg":"#3d1a1a","mult_bg":"#1a3d1a","spec_bg":"#1a1a3d",
    "alt":"#0d1f2d","gold":"#ffd700","cyan":"#58a6ff",
}


# =============================================================================
# DATA MANAGER
# =============================================================================

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
        except Exception as e:
            print(f"Save err: {e}")
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
        return f"log_{re.sub(r'[^a-zA-Z0-9_-]','_',cid)}.json"

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


# =============================================================================
# LANGUAGE
# =============================================================================

class L:
    _c = "ro"
    @classmethod
    def s(cls, l):
        if l in T: cls._c = l
    @classmethod
    def g(cls):
        return cls._c
    @classmethod
    def t(cls, k):
        return T.get(cls._c, {}).get(k, k)


# =============================================================================
# SCORING ENGINE
# =============================================================================

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
            try: return int(sp[call])
            except: pass
        if sm == "per_qso":
            return rules.get("points_per_qso", 1)
        elif sm == "per_band":
            bp = rules.get("band_points", {})
            return int(bp.get(q.get("b", ""), rules.get("points_per_qso", 1)))
        elif sm == "maraton":
            return rules.get("points_per_qso", 1)
        elif sm == "multiplier":
            return rules.get("points_per_qso", 1)
        elif sm == "distance":
            n = q.get("n", "").strip()
            ml = (cfg or {}).get("loc", "")
            if Loc.valid(n) and Loc.valid(ml):
                return max(1, int(Loc.dist(ml, n)))
            return rules.get("points_per_qso", 1)
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
                        ms.add(co.upper()); break
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
                    nm = co.upper(); break
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
        req = rules.get("required_stations", [])
        if req:
            calls = {q.get("c", "").upper() for q in data}
            miss = [s for s in req if s.upper() not in calls]
            if miss:
                msgs.append(f"Lipsesc: {', '.join(miss)}")
        mq = rules.get("min_qso", 0)
        if mq > 0 and len(data) < mq:
            msgs.append(f"Min {mq} QSO, aveți {len(data)}")
        ab = rules.get("allowed_bands", [])
        if ab:
            for i, q in enumerate(data):
                if q.get("b") not in ab:
                    msgs.append(f"#{i+1} {q.get('c','')} bandă: {q.get('b','')}")
        am = rules.get("allowed_modes", [])
        if am:
            for i, q in enumerate(data):
                if q.get("m") not in am:
                    msgs.append(f"#{i+1} {q.get('c','')} mod: {q.get('m','')}")
        seen = set()
        dc = 0
        for q in data:
            k = (q.get("c", "").upper(), q.get("b"), q.get("m"))
            if k in seen: dc += 1
            seen.add(k)
        if dc:
            msgs.append(f"⚠ {dc} duplicate")
        if msgs:
            return False, "\n".join(msgs[:20]), 0
        _, _, tot = Score.total(data, rules, cfg)
        return True, f"✓ OK! {len(data)} QSO, Scor: {tot}", tot


# =============================================================================
# IMPORT ENGINE
# =============================================================================

class Importer:
    @staticmethod
    def parse_adif(text):
        """Parse ADIF text into list of QSO dicts"""
        qsos = []
        # Skip header
        eoh = text.upper().find("<EOH>")
        if eoh >= 0:
            text = text[eoh + 5:]
        # Split by EOR
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
            # Date
            qd = fields.get("QSO_DATE", "")
            if len(qd) == 8:
                q["d"] = f"{qd[:4]}-{qd[4:6]}-{qd[6:8]}"
            else:
                q["d"] = datetime.datetime.utcnow().strftime("%Y-%m-%d")
            # Time
            qt = fields.get("TIME_ON", "")
            if len(qt) >= 4:
                q["t"] = f"{qt[:2]}:{qt[2:4]}"
            else:
                q["t"] = "00:00"
            q["f"] = fields.get("FREQ", "")
            q["n"] = fields.get("GRIDSQUARE", fields.get("COMMENT", ""))
            q["ss"] = fields.get("STX", "")
            q["sr"] = fields.get("SRX", "")
            qsos.append(q)
        return qsos

    @staticmethod
    def parse_csv(text):
        """Parse CSV text into list of QSO dicts"""
        qsos = []
        reader = csv.DictReader(io.StringIO(text))
        for row in reader:
            # Try various common column names
            call = (row.get("Call") or row.get("CALL") or row.get("call") or
                    row.get("Callsign") or row.get("callsign") or "").upper().strip()
            if not call:
                continue
            q = {"c": call}
            q["b"] = row.get("Band") or row.get("BAND") or row.get("band") or "40m"
            q["m"] = row.get("Mode") or row.get("MODE") or row.get("mode") or "SSB"
            q["s"] = row.get("RST_Sent") or row.get("RST_S") or row.get("rst_s") or "59"
            q["r"] = row.get("RST_Rcvd") or row.get("RST_R") or row.get("rst_r") or "59"
            q["d"] = row.get("Date") or row.get("DATE") or row.get("date") or datetime.datetime.utcnow().strftime("%Y-%m-%d")
            q["t"] = row.get("Time") or row.get("TIME") or row.get("time") or "00:00"
            q["f"] = row.get("Freq") or row.get("FREQ") or row.get("freq") or ""
            q["n"] = row.get("Note") or row.get("NOTE") or row.get("note") or row.get("Comment") or ""
            q["ss"] = row.get("Serial_Sent") or row.get("STX") or ""
            q["sr"] = row.get("Serial_Rcvd") or row.get("SRX") or ""
            qsos.append(q)
        return qsos


# =============================================================================
# CONTEST EDITOR
# =============================================================================

class ContestEditor(tk.Toplevel):
    def __init__(self, parent, cid=None, cdata=None, all_c=None):
        super().__init__(parent)
        self.result = None
        self.cid = cid
        self.new = cid is None
        self.all_c = all_c or {}
        self.d = copy.deepcopy(cdata) if cdata else {
            "name_ro":"","name_en":"","contest_type":"Simplu",
            "categories":["Individual"],"scoring_mode":"none","points_per_qso":1,
            "min_qso":0,"allowed_bands":list(BANDS_ALL),"allowed_modes":list(MODES_ALL),
            "required_stations":[],"special_scoring":{},"use_serial":False,
            "use_county":False,"county_list":[],"multiplier_type":"none",
            "band_points":{},"is_default":False}
        self.title(L.t("edit_c") if not self.new else L.t("add_c"))
        self.geometry("700x850")
        self.configure(bg=TH["bg"])
        self.transient(parent)
        self.grab_set()
        self._build()
        self.update_idletasks()
        self.geometry(f"+{(self.winfo_screenwidth()-700)//2}+{(self.winfo_screenheight()-850)//2}")

    def _build(self):
        cv = tk.Canvas(self, bg=TH["bg"], highlightthickness=0)
        sb = ttk.Scrollbar(self, orient="vertical", command=cv.yview)
        self.sf = tk.Frame(cv, bg=TH["bg"])
        self.sf.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.create_window((0,0), window=self.sf, anchor="nw")
        cv.configure(yscrollcommand=sb.set)
        cv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        cv.bind("<MouseWheel>", lambda e: cv.yview_scroll(int(-e.delta/120), "units"))
        cv.bind("<Enter>", lambda e: cv.focus_set())

        f = self.sf
        eo = {"bg":TH["entry_bg"],"fg":TH["fg"],"font":("Consolas",11),"insertbackground":TH["fg"]}
        lo = {"bg":TH["bg"],"fg":TH["fg"],"font":("Consolas",11)}
        p = {"padx":12,"pady":3}
        r = 0
        self._e = {}

        if self.new:
            tk.Label(f, text=L.t("c_id"), **lo).grid(row=r, column=0, sticky="w", **p)
            self._e["id"] = tk.Entry(f, width=30, **eo)
            self._e["id"].grid(row=r, column=1, sticky="w", **p); r += 1
        else:
            tk.Label(f, text=f"ID: {self.cid}", **lo).grid(row=r, column=0, columnspan=2, sticky="w", **p); r += 1

        for k, lb in [("name_ro", L.t("c_name")+" (RO)"), ("name_en", L.t("c_name")+" (EN)")]:
            tk.Label(f, text=lb, **lo).grid(row=r, column=0, sticky="w", **p)
            e = tk.Entry(f, width=40, **eo); e.insert(0, self.d.get(k,"")); e.grid(row=r, column=1, sticky="w", **p)
            self._e[k] = e; r += 1

        tk.Label(f, text=L.t("c_type"), **lo).grid(row=r, column=0, sticky="w", **p)
        self._tv = tk.StringVar(value=self.d.get("contest_type","Simplu"))
        ttk.Combobox(f, textvariable=self._tv, values=CONTEST_TYPES, state="readonly", width=18).grid(row=r, column=1, sticky="w", **p); r += 1

        tk.Label(f, text=L.t("sc_mode"), **lo).grid(row=r, column=0, sticky="w", **p)
        self._sv = tk.StringVar(value=self.d.get("scoring_mode","none"))
        ttk.Combobox(f, textvariable=self._sv, values=SCORING_MODES, state="readonly", width=18).grid(row=r, column=1, sticky="w", **p); r += 1

        for k, lb in [("points_per_qso",L.t("ppq")), ("min_qso",L.t("min_qso"))]:
            tk.Label(f, text=lb, **lo).grid(row=r, column=0, sticky="w", **p)
            e = tk.Entry(f, width=10, **eo); e.insert(0, str(self.d.get(k,0))); e.grid(row=r, column=1, sticky="w", **p)
            self._e[k] = e; r += 1

        tk.Label(f, text=L.t("mults"), **lo).grid(row=r, column=0, sticky="w", **p)
        self._mv = tk.StringVar(value=self.d.get("multiplier_type","none"))
        ttk.Combobox(f, textvariable=self._mv, values=["none","county","dxcc","band","grid"], state="readonly", width=18).grid(row=r, column=1, sticky="w", **p); r += 1

        tk.Label(f, text=L.t("cats"), **lo).grid(row=r, column=0, sticky="nw", **p)
        self._cat_t = tk.Text(f, width=40, height=4, **eo)
        self._cat_t.insert("1.0", "\n".join(self.d.get("categories",[])))
        self._cat_t.grid(row=r, column=1, sticky="w", **p); r += 1

        tk.Label(f, text=L.t("a_bands"), **lo).grid(row=r, column=0, sticky="nw", **p)
        bf = tk.Frame(f, bg=TH["bg"]); bf.grid(row=r, column=1, sticky="w", **p)
        self._bv = {}
        ab = self.d.get("allowed_bands", BANDS_ALL)
        for i, b in enumerate(BANDS_ALL):
            v = tk.BooleanVar(value=b in ab)
            tk.Checkbutton(bf, text=b, variable=v, bg=TH["bg"], fg=TH["fg"],
                          selectcolor=TH["entry_bg"], activebackground=TH["bg"]).grid(row=i//7, column=i%7, sticky="w", padx=1)
            self._bv[b] = v
        r += 1

        tk.Label(f, text=L.t("a_modes"), **lo).grid(row=r, column=0, sticky="nw", **p)
        mf = tk.Frame(f, bg=TH["bg"]); mf.grid(row=r, column=1, sticky="w", **p)
        self._modv = {}
        ams = self.d.get("allowed_modes", MODES_ALL)
        for i, m in enumerate(MODES_ALL):
            v = tk.BooleanVar(value=m in ams)
            tk.Checkbutton(mf, text=m, variable=v, bg=TH["bg"], fg=TH["fg"],
                          selectcolor=TH["entry_bg"], activebackground=TH["bg"]).grid(row=i//6, column=i%6, sticky="w", padx=1)
            self._modv[m] = v
        r += 1

        self._serv = tk.BooleanVar(value=self.d.get("use_serial",False))
        tk.Checkbutton(f, text=L.t("use_serial"), variable=self._serv, bg=TH["bg"], fg=TH["fg"],
                      selectcolor=TH["entry_bg"], font=("Consolas",11)).grid(row=r, column=0, columnspan=2, sticky="w", **p); r += 1

        self._couv = tk.BooleanVar(value=self.d.get("use_county",False))
        tk.Checkbutton(f, text=L.t("use_county"), variable=self._couv, bg=TH["bg"], fg=TH["fg"],
                      selectcolor=TH["entry_bg"], font=("Consolas",11)).grid(row=r, column=0, columnspan=2, sticky="w", **p); r += 1

        tk.Label(f, text=L.t("county_list"), **lo).grid(row=r, column=0, sticky="w", **p)
        self._cl = tk.Entry(f, width=50, **eo); self._cl.insert(0, ",".join(self.d.get("county_list",[])))
        self._cl.grid(row=r, column=1, sticky="w", **p); r += 1

        for k, lb, h, src in [
            ("req", L.t("req_st_c"), 3, "\n".join(self.d.get("required_stations",[]))),
            ("spec", L.t("sp_sc"), 3, "\n".join(f"{a}={b}" for a,b in self.d.get("special_scoring",{}).items())),
            ("bpts", L.t("band_pts"), 3, "\n".join(f"{a}={b}" for a,b in self.d.get("band_points",{}).items())),
        ]:
            tk.Label(f, text=lb, **lo).grid(row=r, column=0, sticky="nw", **p)
            t = tk.Text(f, width=40, height=h, **eo); t.insert("1.0", src)
            t.grid(row=r, column=1, sticky="w", **p); self._e[k] = t; r += 1

        bf2 = tk.Frame(f, bg=TH["bg"]); bf2.grid(row=r, column=0, columnspan=2, pady=12)
        tk.Button(bf2, text=L.t("save"), command=self._save, bg=TH["accent"], fg="white",
                 font=("Consolas",12,"bold"), width=12, cursor="hand2").pack(side="left", padx=8)
        tk.Button(bf2, text=L.t("cancel"), command=self.destroy, bg=TH["btn_bg"], fg="white",
                 font=("Consolas",12), width=12, cursor="hand2").pack(side="left", padx=8)

    def _lines(self, w):
        return [l.strip() for l in w.get("1.0","end").strip().split("\n") if l.strip()]

    def _kv(self, w):
        r = {}
        for l in w.get("1.0","end").strip().split("\n"):
            l = l.strip()
            if "=" in l:
                k, v = l.split("=",1)
                if k.strip(): r[k.strip()] = v.strip()
        return r

    def _save(self):
        if self.new:
            cid = self._e["id"].get().strip().lower().replace(" ","-")
            if not cid: messagebox.showerror(L.t("error"),"ID!"); return
            if cid in self.all_c: messagebox.showerror(L.t("error"),L.t("c_exists")); return
            self.cid = cid
        self.d["name_ro"] = self._e["name_ro"].get().strip()
        self.d["name_en"] = self._e["name_en"].get().strip()
        self.d["contest_type"] = self._tv.get()
        self.d["scoring_mode"] = self._sv.get()
        try: self.d["points_per_qso"] = int(self._e["points_per_qso"].get())
        except: self.d["points_per_qso"] = 1
        try: self.d["min_qso"] = int(self._e["min_qso"].get())
        except: self.d["min_qso"] = 0
        self.d["multiplier_type"] = self._mv.get()
        self.d["categories"] = self._lines(self._cat_t) or ["Individual"]
        self.d["allowed_bands"] = [b for b,v in self._bv.items() if v.get()]
        self.d["allowed_modes"] = [m for m,v in self._modv.items() if v.get()]
        self.d["use_serial"] = self._serv.get()
        self.d["use_county"] = self._couv.get()
        self.d["county_list"] = [c.strip().upper() for c in self._cl.get().split(",") if c.strip()]
        self.d["required_stations"] = [s.upper() for s in self._lines(self._e["req"])]
        sp = self._kv(self._e["spec"])
        self.d["special_scoring"] = {k.upper():int(v) if v.isdigit() else 1 for k,v in sp.items()}
        bp = self._kv(self._e["bpts"])
        self.d["band_points"] = {k.lower():int(v) if v.isdigit() else 1 for k,v in bp.items()}
        self.d["is_default"] = False
        self.result = (self.cid, self.d)
        self.destroy()


# =============================================================================
# CONTEST MANAGER
# =============================================================================

class ContestMgr(tk.Toplevel):
    def __init__(self, parent, contests):
        super().__init__(parent)
        self.c = copy.deepcopy(contests)
        self.result = None
        self.title(L.t("contest_mgr"))
        self.geometry("760x500")
        self.configure(bg=TH["bg"])
        self.transient(parent)
        self.grab_set()
        self._build()
        self._fill()
        self.update_idletasks()
        self.geometry(f"+{(self.winfo_screenwidth()-760)//2}+{(self.winfo_screenheight()-500)//2}")

    def _build(self):
        tb = tk.Frame(self, bg=TH["header_bg"], pady=5); tb.pack(fill="x")
        bo = {"bg":TH["accent"],"fg":"white","font":("Consolas",10),"cursor":"hand2"}
        for txt, cmd in [(L.t("add_c"),self._add),(L.t("edit_c"),self._edit),
                         (L.t("dup_c"),self._dup)]:
            tk.Button(tb, text=txt, command=cmd, **bo).pack(side="left", padx=3)
        tk.Button(tb, text=L.t("del_c"), command=self._del, bg=TH["err"], fg="white",
                 font=("Consolas",10), cursor="hand2").pack(side="left", padx=3)
        tk.Button(tb, text=L.t("exp_c"), command=self._exp, **bo).pack(side="right", padx=3)
        tk.Button(tb, text=L.t("imp_c"), command=self._imp, **bo).pack(side="right", padx=3)

        tf = tk.Frame(self, bg=TH["bg"]); tf.pack(fill="both", expand=True, padx=6, pady=3)
        cols = ("id","name","type","sc","cats","min")
        self.tree = ttk.Treeview(tf, columns=cols, show="headings", selectmode="browse")
        for c, h, w in zip(cols, ["ID",L.t("c_name"),L.t("c_type"),L.t("sc_mode"),L.t("cats"),L.t("min_qso")],
                           [90,170,85,85,200,45]):
            self.tree.heading(c, text=h); self.tree.column(c, width=w, anchor="center")
        sb = ttk.Scrollbar(tf, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True); sb.pack(side="right", fill="y")
        self.tree.bind("<Double-1>", lambda e: self._edit())

        bt = tk.Frame(self, bg=TH["bg"], pady=6); bt.pack(fill="x")
        tk.Button(bt, text=L.t("save"), command=self._onsave, bg=TH["ok"], fg="white",
                 font=("Consolas",12,"bold"), width=12, cursor="hand2").pack(side="left", padx=12)
        tk.Button(bt, text=L.t("cancel"), command=self.destroy, bg=TH["btn_bg"], fg="white",
                 font=("Consolas",12), width=12, cursor="hand2").pack(side="right", padx=12)

    def _fill(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        lk = "name_" + L.g()
        for cid, cd in self.c.items():
            nm = cd.get(lk, cd.get("name_ro", cid))
            cats = ", ".join(cd.get("categories",[])[:3])
            if len(cd.get("categories",[])) > 3: cats += "..."
            self.tree.insert("","end",iid=cid,values=(cid,nm,cd.get("contest_type","?"),
                cd.get("scoring_mode","none"),cats,cd.get("min_qso",0)))

    def _sel(self):
        s = self.tree.selection()
        if not s: messagebox.showwarning(L.t("error"),L.t("no_sel")); return None
        return s[0]

    def _add(self):
        d = ContestEditor(self, all_c=self.c); self.wait_window(d)
        if d.result: self.c[d.result[0]] = d.result[1]; self._fill()

    def _edit(self):
        cid = self._sel()
        if not cid: return
        d = ContestEditor(self, cid=cid, cdata=self.c[cid], all_c=self.c); self.wait_window(d)
        if d.result: self.c[cid] = d.result[1]; self._fill()

    def _dup(self):
        cid = self._sel()
        if not cid: return
        nid = cid+"-copy"; c=1
        while nid in self.c: nid=f"{cid}-copy{c}"; c+=1
        nd = copy.deepcopy(self.c[cid])
        nd["name_ro"]+=" (Copie)"; nd["name_en"]+=" (Copy)"; nd["is_default"]=False
        self.c[nid] = nd; self._fill()

    def _del(self):
        cid = self._sel()
        if not cid: return
        if self.c.get(cid,{}).get("is_default"): messagebox.showwarning(L.t("error"),L.t("c_default")); return
        nm = self.c[cid].get("name_"+L.g(), cid)
        if messagebox.askyesno(L.t("confirm_del"),L.t("del_c_conf").format(nm)):
            del self.c[cid]; self._fill()

    def _exp(self):
        try:
            fn = f"contests_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.json"
            with open(os.path.join(get_data_dir(),fn),"w",encoding="utf-8") as f:
                json.dump(self.c, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("OK", f"Export: {fn}")
        except Exception as e: messagebox.showerror(L.t("error"),str(e))

    def _imp(self):
        fp = filedialog.askopenfilename(filetypes=[("JSON","*.json")], initialdir=get_data_dir())
        if not fp: return
        try:
            with open(fp,"r",encoding="utf-8") as f: imp=json.load(f)
            if isinstance(imp, dict):
                n=0
                for cid, cd in imp.items():
                    if isinstance(cd, dict):
                        while cid in self.c: cid+="-imp"
                        self.c[cid]=cd; n+=1
                self._fill(); messagebox.showinfo("OK",f"Importate: {n}")
        except Exception as e: messagebox.showerror(L.t("error"),str(e))

    def _onsave(self):
        self.result = self.c; self.destroy()


# =============================================================================
# STATISTICS WINDOW (proper dialog, not messagebox)
# =============================================================================

class StatsWindow(tk.Toplevel):
    def __init__(self, parent, log_data, contest, cfg):
        super().__init__(parent)
        self.title(L.t("stats"))
        self.geometry("600x700")
        self.configure(bg=TH["bg"])
        self.transient(parent)

        tf = tk.Frame(self, bg=TH["bg"])
        tf.pack(fill="both", expand=True, padx=10, pady=5)

        txt = tk.Text(tf, bg=TH["entry_bg"], fg=TH["fg"], font=("Consolas",11),
                     wrap="word", insertbackground=TH["fg"])
        sb = ttk.Scrollbar(tf, orient="vertical", command=txt.yview)
        txt.configure(yscrollcommand=sb.set)
        txt.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # Tags for colors
        txt.tag_configure("title", foreground=TH["gold"], font=("Consolas",13,"bold"))
        txt.tag_configure("head", foreground=TH["cyan"], font=("Consolas",11,"bold"))
        txt.tag_configure("ok", foreground=TH["ok"])
        txt.tag_configure("warn", foreground=TH["warn"])
        txt.tag_configure("err", foreground=TH["err"])

        n = len(log_data)
        calls = {q.get("c","").upper() for q in log_data}

        txt.insert("end", f"  📊 {L.t('stats')} — {cfg.get('call','')}\n\n", "title")

        # General
        txt.insert("end", f"  {L.t('qso_total')}: {n}\n", "head")
        txt.insert("end", f"  {L.t('unique')}: {len(calls)}\n\n")

        # Band summary table
        bc = Counter(q.get("b","") for q in log_data)
        txt.insert("end", f"  ═══ {L.t('band_sum')} ═══\n", "head")
        txt.insert("end", f"  {'Band':<8}{'QSO':>6}{'Pts':>8}{'Unique':>8}\n")
        txt.insert("end", f"  {'─'*30}\n")
        for band in sorted(bc.keys()):
            bq = [q for q in log_data if q.get("b")==band]
            pts = sum(Score.qso(q, contest, cfg) for q in bq)
            uniq = len({q.get("c","").upper() for q in bq})
            txt.insert("end", f"  {band:<8}{bc[band]:>6}{pts:>8}{uniq:>8}\n")
        txt.insert("end", f"  {'─'*30}\n\n")

        # Mode summary
        mc = Counter(q.get("m","") for q in log_data)
        txt.insert("end", f"  ═══ Moduri / Modes ═══\n", "head")
        for m in sorted(mc.keys()):
            txt.insert("end", f"  {m:<8}{mc[m]:>6}\n")
        txt.insert("end", "\n")

        # Required stations
        req = contest.get("required_stations", [])
        if req:
            txt.insert("end", f"  ═══ {L.t('req_st')} ═══\n", "head")
            for s in req:
                if s.upper() in calls:
                    txt.insert("end", f"  ✓ {s}\n", "ok")
                else:
                    txt.insert("end", f"  ✗ {s}\n", "err")
            txt.insert("end", "\n")

        # Scoring
        qp, mult, total = Score.total(log_data, contest, cfg)
        if contest.get("scoring_mode","none") != "none":
            txt.insert("end", f"  ═══ {L.t('score_f')} ═══\n", "head")
            txt.insert("end", f"  {L.t('qso_pts')}: {qp}\n")
            if contest.get("multiplier_type","none") != "none":
                txt.insert("end", f"  {L.t('mult_c')}: {mult}\n")
            txt.insert("end", f"  {L.t('total_score')}: {total}\n", "ok")
            txt.insert("end", "\n")

        # Worked-all tracker
        mt = contest.get("multiplier_type","none")
        if mt == "county" and contest.get("county_list"):
            _, worked = Score.mults(log_data, contest)
            all_c = set(c.upper() for c in contest.get("county_list",[]))
            missing = sorted(all_c - worked)
            txt.insert("end", f"  ═══ {L.t('worked_all')} ({L.t('county')}) ═══\n", "head")
            txt.insert("end", f"  {L.t('worked_x').format(len(worked), len(all_c))}\n",
                       "ok" if len(missing)==0 else "warn")
            if missing:
                txt.insert("end", f"  {L.t('missing_x').format(', '.join(missing[:30]))}\n", "err")
            txt.insert("end", "\n")

        # Countries
        countries = Counter()
        for q in log_data:
            c, _ = DXCC.lookup(q.get("c",""))
            if c != "Unknown": countries[c] += 1
        if countries:
            txt.insert("end", f"  ═══ DXCC ({len(countries)}) ═══\n", "head")
            for c, n in countries.most_common(20):
                txt.insert("end", f"  {c:<25}{n:>4}\n")
            if len(countries) > 20:
                txt.insert("end", f"  ... +{len(countries)-20}\n")
            txt.insert("end", "\n")

        # Operating time
        if log_data:
            times = []
            for q in log_data:
                try:
                    t = datetime.datetime.strptime(f"{q.get('d','')} {q.get('t','')}", "%Y-%m-%d %H:%M")
                    times.append(t)
                except: pass
            if len(times) >= 2:
                times.sort()
                total_span = (times[-1] - times[0]).total_seconds() / 3600
                txt.insert("end", f"  ═══ {L.t('op_time')} ═══\n", "head")
                txt.insert("end", f"  Span: {total_span:.1f}h\n")
                txt.insert("end", f"  First: {times[0].strftime('%Y-%m-%d %H:%M')}\n")
                txt.insert("end", f"  Last:  {times[-1].strftime('%Y-%m-%d %H:%M')}\n")
                if total_span > 0:
                    txt.insert("end", f"  Rate: {n/total_span:.1f} QSO/h\n")
                txt.insert("end", "\n")

        txt.configure(state="disabled")

        tk.Button(self, text=L.t("close"), command=self.destroy,
                 bg=TH["accent"], fg="white", font=("Consolas",11),
                 width=12, cursor="hand2").pack(pady=8)


# =============================================================================
# MAIN APPLICATION
# =============================================================================

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.cfg = DM.load("config.json", DEFAULT_CFG.copy())
        self.contests = DM.load("contests.json", DEFAULT_CONTESTS.copy())
        if "simplu" not in self.contests:
            self.contests["simplu"] = DEFAULT_CONTESTS["simplu"]
            DM.save("contests.json", self.contests)
        if self.cfg.get("contest","") not in self.contests:
            self.cfg["contest"] = "simplu"
            DM.save("config.json", self.cfg)
        self._migrate()
        self.log = DM.load_log(self.cfg.get("contest","simplu"))
        L.s(self.cfg.get("lang","ro"))
        self.edit_idx = None
        self.ent = {}
        self.serial = len(self.log) + 1
        self.undo_stack = deque(maxlen=50)
        self._sort_col = None
        self._sort_rev = False

        self._setup_win()
        self._setup_style()
        self._build_menu()
        self._build_ui()
        self._build_ctx()
        self._refresh()

        self.protocol("WM_DELETE_WINDOW", self._exit)
        self.bind('<Return>', self._on_enter)
        self.bind('<Control-f>', lambda e: self._search_dlg())
        self.bind('<Control-F>', lambda e: self._search_dlg())
        self.bind('<Control-z>', lambda e: self._undo())
        self.bind('<Control-Z>', lambda e: self._undo())
        self.bind('<Control-s>', lambda e: self._fsave())
        self.bind('<Control-S>', lambda e: self._fsave())
        self.bind('<F2>', self._cycle_band)
        self.bind('<F3>', self._cycle_mode)

        self._tick_clock()
        self._tick_save()

    def _migrate(self):
        old = DM.fp("log.json")
        if os.path.exists(old):
            try:
                with open(old,"r",encoding="utf-8") as f: od=json.load(f)
                if isinstance(od, list) and od:
                    cid = self.cfg.get("contest","simplu")
                    if not DM.load_log(cid):
                        DM.save_log(cid, od)
                os.rename(old, old+".migrated")
            except: pass

    def _cc(self):
        return self.contests.get(self.cfg.get("contest","simplu"),
                                 self.contests.get("simplu",{}))

    def _cid(self):
        return self.cfg.get("contest","simplu")

    def _setup_win(self):
        self.title(L.t("app_title"))
        self.configure(bg=TH["bg"])
        geo = self.cfg.get("win_geo","")
        if geo:
            try: self.geometry(geo)
            except: self.geometry("1220x780")
        else:
            w, h = 1220, 780
            self.geometry(f"{w}x{h}+{(self.winfo_screenwidth()-w)//2}+{(self.winfo_screenheight()-h)//2}")
        self.minsize(1000, 640)

    def _setup_style(self):
        self.fs = int(self.cfg.get("fs",11))
        self.fn = ("Consolas", self.fs)
        self.fb = ("Consolas", self.fs, "bold")
        s = ttk.Style(); s.theme_use('clam')
        s.configure("Treeview", background=TH["entry_bg"], foreground=TH["fg"],
                    fieldbackground=TH["entry_bg"], font=self.fn, rowheight=22)
        s.configure("Treeview.Heading", background=TH["header_bg"],
                    foreground=TH["fg"], font=self.fb)
        s.map("Treeview", background=[("selected",TH["accent"])])

    def _build_menu(self):
        mb = tk.Menu(self); self.config(menu=mb)
        cm = tk.Menu(mb, tearoff=0)
        mb.add_cascade(label=L.t("contests"), menu=cm)
        cm.add_command(label=L.t("contest_mgr"), command=self._mgr)
        cm.add_separator()
        sm = tk.Menu(cm, tearoff=0)
        cm.add_cascade(label="⚡ Switch", menu=sm)
        for cid in self.contests:
            c = self.contests[cid]
            nm = c.get("name_"+L.g(), c.get("name_ro",cid))
            sm.add_command(label=nm, command=lambda k=cid: self._switch(k))

        tm = tk.Menu(mb, tearoff=0)
        mb.add_cascade(label="🛠", menu=tm)
        tm.add_command(label=L.t("search")+" (Ctrl+F)", command=self._search_dlg)
        tm.add_command(label=L.t("timer"), command=self._timer_dlg)
        tm.add_command(label=L.t("undo")+" (Ctrl+Z)", command=self._undo)
        tm.add_separator()
        tm.add_command(label=L.t("imp_adif"), command=self._import_adif)
        tm.add_command(label=L.t("imp_csv"), command=self._import_csv)
        tm.add_separator()
        tm.add_command(label=L.t("print_log"), command=self._print_log)
        tm.add_command(label=L.t("verify"), command=self._verify)
        tm.add_separator()
        tm.add_command(label=L.t("clear_log"), command=self._clear)

        hm = tk.Menu(mb, tearoff=0)
        mb.add_cascade(label=L.t("help"), menu=hm)
        hm.add_command(label=L.t("about"), command=self._about)
        hm.add_separator()
        hm.add_command(label="Exit", command=self._exit)

    def _build_ctx(self):
        self.ctx = Menu(self, tearoff=0)
        self.ctx.add_command(label=L.t("edit_qso"), command=self._edit_sel)
        self.ctx.add_separator()
        self.ctx.add_command(label=L.t("delete_qso"), command=self._del_sel)

    def _build_ui(self):
        self._build_hdr()
        self._build_inp()
        self._build_flt()
        self._build_tree()
        self._build_btns()

    def _build_hdr(self):
        h = tk.Frame(self, bg=TH["header_bg"], pady=5); h.pack(fill="x")
        lf = tk.Frame(h, bg=TH["header_bg"]); lf.pack(side="left", padx=10)
        self.led_c = tk.Canvas(lf, width=14, height=14, bg=TH["header_bg"], highlightthickness=0)
        self.led = self.led_c.create_oval(1,1,13,13, fill=TH["led_on"], outline="")
        self.led_c.pack(side="left", padx=(0,5))
        self.st_lbl = tk.Label(lf, text=L.t("online"), bg=TH["header_bg"], fg=TH["led_on"], font=self.fn)
        self.st_lbl.pack(side="left")
        self.info_lbl = tk.Label(lf, text="", bg=TH["header_bg"], fg=TH["fg"], font=self.fn)
        self.info_lbl.pack(side="left", padx=12)

        rf = tk.Frame(h, bg=TH["header_bg"]); rf.pack(side="right", padx=10)
        self.clk = tk.Label(rf, text="UTC 00:00:00", bg=TH["header_bg"], fg=TH["gold"],
                           font=("Consolas",12,"bold"))
        self.clk.pack(side="right", padx=8)
        self.rate_lbl = tk.Label(rf, text="", bg=TH["header_bg"], fg=TH["ok"], font=("Consolas",10))
        self.rate_lbl.pack(side="right", padx=8)

        self.lang_v = tk.StringVar(value=self.cfg.get("lang","ro"))
        lc = ttk.Combobox(rf, textvariable=self.lang_v, values=["ro","en"], state="readonly", width=4)
        lc.pack(side="right", padx=3)
        lc.bind("<<ComboboxSelected>>", self._on_lang)

        self.cv = tk.StringVar(value=self._cid())
        self.ccb = ttk.Combobox(rf, textvariable=self.cv, values=list(self.contests.keys()),
                                state="readonly", width=15)
        self.ccb.pack(side="right", padx=3)
        self.ccb.bind("<<ComboboxSelected>>", self._on_cchange)
        self._upd_info()

    def _build_inp(self):
        ip = tk.Frame(self, bg=TH["bg"], pady=8); ip.pack(fill="x", padx=10)
        r1 = tk.Frame(ip, bg=TH["bg"]); r1.pack(fill="x")
        cc = self._cc()

        # Call
        cf = tk.Frame(r1, bg=TH["bg"]); cf.pack(side="left", padx=3)
        tk.Label(cf, text=L.t("call"), bg=TH["bg"], fg=TH["fg"], font=self.fb).pack()
        self.ent["call"] = tk.Entry(cf, width=15, bg=TH["entry_bg"], fg=TH["gold"],
                                    font=("Consolas",self.fs+2,"bold"), insertbackground=TH["fg"], justify="center")
        self.ent["call"].pack(ipady=3)
        self.ent["call"].bind("<KeyRelease>", self._on_call_key)
        self.wb_lbl = tk.Label(cf, text="", bg=TH["bg"], fg=TH["err"], font=("Consolas",9))
        self.wb_lbl.pack()

        # Freq
        ff = tk.Frame(r1, bg=TH["bg"]); ff.pack(side="left", padx=3)
        tk.Label(ff, text=L.t("freq"), bg=TH["bg"], fg=TH["fg"], font=self.fn).pack()
        self.ent["freq"] = tk.Entry(ff, width=9, bg=TH["entry_bg"], fg=TH["fg"],
                                    font=self.fn, insertbackground=TH["fg"], justify="center")
        self.ent["freq"].pack()
        self.ent["freq"].bind("<FocusOut>", self._on_freq_out)

        # Band
        ab = cc.get("allowed_bands", BANDS_ALL)
        bf = tk.Frame(r1, bg=TH["bg"]); bf.pack(side="left", padx=3)
        tk.Label(bf, text=L.t("band"), bg=TH["bg"], fg=TH["fg"], font=self.fn).pack()
        self.ent["band"] = ttk.Combobox(bf, values=ab, state="readonly", width=6, font=self.fn)
        self.ent["band"].set(ab[0] if ab else "40m")
        self.ent["band"].pack()
        self.ent["band"].bind("<<ComboboxSelected>>", self._on_band_change)

        # Mode
        am = cc.get("allowed_modes", MODES_ALL)
        mf = tk.Frame(r1, bg=TH["bg"]); mf.pack(side="left", padx=3)
        tk.Label(mf, text=L.t("mode"), bg=TH["bg"], fg=TH["fg"], font=self.fn).pack()
        self.ent["mode"] = ttk.Combobox(mf, values=am, state="readonly", width=6, font=self.fn)
        self.ent["mode"].set(am[0] if am else "SSB")
        self.ent["mode"].pack()
        self.ent["mode"].bind("<<ComboboxSelected>>", self._on_mode_change)

        # RST
        for k, lb in [("rst_s",L.t("rst_s")),("rst_r",L.t("rst_r"))]:
            frame = tk.Frame(r1, bg=TH["bg"]); frame.pack(side="left", padx=3)
            tk.Label(frame, text=lb, bg=TH["bg"], fg=TH["fg"], font=self.fn).pack()
            e = tk.Entry(frame, width=5, bg=TH["entry_bg"], fg=TH["fg"], font=self.fn,
                        insertbackground=TH["fg"], justify="center")
            rst = RST_DEFAULTS.get(am[0] if am else "SSB", "59")
            e.insert(0, rst)
            e.pack()
            self.ent[k] = e

        # Serials
        if cc.get("use_serial"):
            for k, lb in [("ss",L.t("serial_s")),("sr",L.t("serial_r"))]:
                frame = tk.Frame(r1, bg=TH["bg"]); frame.pack(side="left", padx=3)
                tk.Label(frame, text=lb, bg=TH["bg"], fg=TH["fg"], font=self.fn).pack()
                e = tk.Entry(frame, width=5, bg=TH["entry_bg"], fg=TH["fg"], font=self.fn,
                            insertbackground=TH["fg"], justify="center")
                if k == "ss": e.insert(0, str(self.serial))
                e.pack()
                self.ent[k] = e

        # Note
        nf = tk.Frame(r1, bg=TH["bg"]); nf.pack(side="left", padx=3)
        nl = L.t("county")+"/"+L.t("note") if cc.get("use_county") else L.t("note")
        tk.Label(nf, text=nl, bg=TH["bg"], fg=TH["fg"], font=self.fn).pack()
        self.ent["note"] = tk.Entry(nf, width=13, bg=TH["entry_bg"], fg=TH["fg"],
                                    font=self.fn, insertbackground=TH["fg"], justify="center")
        self.ent["note"].pack()

        # Buttons
        rbf = tk.Frame(r1, bg=TH["bg"]); rbf.pack(side="left", padx=6)
        self.man_v = tk.BooleanVar(value=self.cfg.get("manual_dt",False))
        tk.Checkbutton(rbf, text=L.t("manual"), variable=self.man_v, bg=TH["bg"], fg=TH["fg"],
                      selectcolor=TH["entry_bg"], command=self._tog_man).pack()
        self.log_btn = tk.Button(rbf, text=L.t("log"), command=self._add_qso,
                                bg=TH["accent"], fg="white", font=self.fb, width=10, cursor="hand2")
        self.log_btn.pack(pady=1)
        tk.Button(rbf, text=L.t("reset"), command=self._clr, bg=TH["btn_bg"], fg=TH["btn_fg"],
                 font=self.fn, width=10, cursor="hand2").pack(pady=1)

        # Row 2
        r2 = tk.Frame(ip, bg=TH["bg"]); r2.pack(fill="x", pady=(6,0))
        tk.Label(r2, text=L.t("date_l"), bg=TH["bg"], fg=TH["fg"], font=self.fn).pack(side="left", padx=3)
        self.ent["date"] = tk.Entry(r2, width=11, bg=TH["entry_bg"], fg=TH["fg"],
                                    font=self.fn, justify="center", state="disabled")
        self.ent["date"].pack(side="left", padx=2)
        tk.Label(r2, text=L.t("time_l"), bg=TH["bg"], fg=TH["fg"], font=self.fn).pack(side="left", padx=3)
        self.ent["time"] = tk.Entry(r2, width=7, bg=TH["entry_bg"], fg=TH["fg"],
                                    font=self.fn, justify="center", state="disabled")
        self.ent["time"].pack(side="left", padx=2)
        now = datetime.datetime.utcnow()
        for k, v in [("date",now.strftime("%Y-%m-%d")),("time",now.strftime("%H:%M"))]:
            self.ent[k].config(state="normal"); self.ent[k].insert(0,v); self.ent[k].config(state="disabled")

        tk.Label(r2, text=L.t("category"), bg=TH["bg"], fg=TH["fg"], font=self.fn).pack(side="left", padx=(12,3))
        cats = cc.get("categories",["A"])
        self.cat_v = tk.StringVar()
        ci = self.cfg.get("cat",0)
        self.cat_v.set(cats[ci] if 0<=ci<len(cats) else cats[0] if cats else "A")
        ttk.Combobox(r2, textvariable=self.cat_v, values=cats, state="readonly", width=20).pack(side="left", padx=2)

        if cc.get("use_county"):
            tk.Label(r2, text=L.t("county"), bg=TH["bg"], fg=TH["fg"], font=self.fn).pack(side="left", padx=(8,3))
            self.cou_v = tk.StringVar(value=self.cfg.get("county","NT"))
            ttk.Combobox(r2, textvariable=self.cou_v, values=cc.get("county_list",[]),
                        state="readonly", width=5).pack(side="left", padx=2)

        tk.Button(r2, text="💾", command=self._save_cc, bg=TH["accent"], fg="white",
                 font=self.fn, cursor="hand2").pack(side="left", padx=6)

        ctype = cc.get("contest_type","?")
        sc = cc.get("scoring_mode","none")
        tk.Label(r2, text=f"[{ctype}/{sc}]", bg=TH["bg"], fg=TH["warn"],
                font=("Consolas",9,"italic")).pack(side="left", padx=4)

    def _build_flt(self):
        ff = tk.Frame(self, bg=TH["bg"]); ff.pack(fill="x", padx=10, pady=(1,0))
        tk.Label(ff, text=L.t("f_band"), bg=TH["bg"], fg=TH["fg"], font=("Consolas",10)).pack(side="left")
        ab = [L.t("all")] + self._cc().get("allowed_bands", BANDS_ALL)
        self.fb_v = tk.StringVar(value=L.t("all"))
        fb = ttk.Combobox(ff, textvariable=self.fb_v, values=ab, state="readonly", width=7)
        fb.pack(side="left", padx=3); fb.bind("<<ComboboxSelected>>", lambda e: self._refresh())
        tk.Label(ff, text=L.t("f_mode"), bg=TH["bg"], fg=TH["fg"], font=("Consolas",10)).pack(side="left", padx=(8,0))
        am2 = [L.t("all")] + self._cc().get("allowed_modes", MODES_ALL)
        self.fm_v = tk.StringVar(value=L.t("all"))
        fm = ttk.Combobox(ff, textvariable=self.fm_v, values=am2, state="readonly", width=7)
        fm.pack(side="left", padx=3); fm.bind("<<ComboboxSelected>>", lambda e: self._refresh())
        self.sc_lbl = tk.Label(ff, text="", bg=TH["bg"], fg=TH["gold"], font=("Consolas",11,"bold"))
        self.sc_lbl.pack(side="right", padx=8)

    def _build_tree(self):
        tf = tk.Frame(self, bg=TH["bg"]); tf.pack(fill="both", expand=True, padx=10, pady=3)
        cc = self._cc()
        us = cc.get("use_serial",False)
        hs = cc.get("scoring_mode","none") != "none"
        isd = cc.get("scoring_mode") == "distance"

        cols = ["nr","call","freq","band","mode","rst_s","rst_r"]
        hdrs = [L.t("nr"),L.t("call"),L.t("freq"),L.t("band"),L.t("mode"),L.t("rst_s"),L.t("rst_r")]
        wids = [38,115,75,55,55,45,45]
        if us:
            cols += ["ss","sr"]; hdrs += [L.t("serial_s"),L.t("serial_r")]; wids += [45,45]
        cols += ["note","country","date","time"]
        hdrs += [L.t("note"),L.t("country"),L.t("data"),L.t("ora")]
        wids += [95,95,80,50]
        if isd:
            cols.append("dist"); hdrs.append("km"); wids.append(55)
        if hs:
            cols.append("pts"); hdrs.append(L.t("pts")); wids.append(50)

        self.tree = ttk.Treeview(tf, columns=cols, show="headings", selectmode="extended")
        for c, h, w in zip(cols, hdrs, wids):
            self.tree.heading(c, text=h, command=lambda c2=c: self._sort(c2))
            self.tree.column(c, width=w, anchor="center")

        self.tree.tag_configure("dup", background=TH["dup_bg"])
        self.tree.tag_configure("spec", background=TH["spec_bg"])
        self.tree.tag_configure("alt", background=TH["alt"])

        sb = ttk.Scrollbar(tf, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree.bind("<Double-1>", lambda e: self._edit_sel())
        self.tree.bind("<Button-3>", self._on_rclick)

    def _build_btns(self):
        bb = tk.Frame(self, bg=TH["bg"], pady=6); bb.pack(fill="x", padx=10)
        btns = [
            (L.t("settings"),self._settings,TH["warn"]),
            ("🏆"+L.t("contests"),self._mgr,"#E91E63"),
            (L.t("search"),self._search_dlg,"#2196F3"),
            (L.t("timer"),self._timer_dlg,"#009688"),
            (L.t("stats"),self._stats,"#3F51B5"),
            (L.t("validate"),self._validate,TH["ok"]),
            (L.t("export"),self._export_dlg,"#9C27B0"),
            (L.t("import_log"),self._import_menu,"#FF5722"),
            (L.t("undo"),self._undo,"#795548"),
            (L.t("backup"),self._bak,"#607D8B"),
        ]
        for txt, cmd, col in btns:
            tk.Button(bb, text=txt, command=cmd, bg=col, fg="white",
                     font=("Consolas",10), width=11, cursor="hand2").pack(side="left", padx=2)

    # ── Clock / Autosave / Rate ──────────────────────────────────────────────

    def _tick_clock(self):
        now = datetime.datetime.utcnow()
        self.clk.config(text=f"UTC {now.strftime('%H:%M:%S')}")
        # Rate
        cnt = 0
        for q in self.log:
            try:
                qt = datetime.datetime.strptime(f"{q.get('d','')} {q.get('t','')}", "%Y-%m-%d %H:%M")
                if (now-qt).total_seconds() <= 3600: cnt += 1
            except: pass
        self.rate_lbl.config(text=f"⚡{cnt} {L.t('rate')}" if cnt else "")
        self.after(1000, self._tick_clock)

    def _tick_save(self):
        DM.save_log(self._cid(), self.log)
        self.after(60000, self._tick_save)

    def _fsave(self):
        DM.save_log(self._cid(), self.log)
        DM.save("config.json", self.cfg)
        beep("success")

    # ── Info & Score ─────────────────────────────────────────────────────────

    def _upd_info(self):
        cc = self._cc()
        call = self.cfg.get("call","NOCALL")
        lk = "name_"+L.g()
        nm = cc.get(lk, cc.get("name_ro","?"))
        ci = self.cfg.get("cat",0)
        cats = cc.get("categories",["A"])
        cat = cats[ci] if 0<=ci<len(cats) else cats[0] if cats else "A"
        self.info_lbl.config(text=f"{call} | {nm} | {cat} | QSO: {len(self.log)}")
        qp, mc, tot = Score.total(self.log, cc, self.cfg)
        if cc.get("scoring_mode","none") != "none":
            mt = cc.get("multiplier_type","none")
            self.sc_lbl.config(text=f"Σ {qp}×{mc}={tot}" if mt!="none" else f"Σ {tot}")
        else:
            self.sc_lbl.config(text="")

    # ── Refresh Log ──────────────────────────────────────────────────────────

    def _refresh(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        cc = self._cc()
        hs = cc.get("scoring_mode","none") != "none"
        us = cc.get("use_serial",False)
        isd = cc.get("scoring_mode") == "distance"
        spc = set(k.upper() for k in cc.get("special_scoring",{}).keys())
        ml = self.cfg.get("loc","")

        fb = self.fb_v.get() if hasattr(self,'fb_v') else L.t("all")
        fm = self.fm_v.get() if hasattr(self,'fm_v') else L.t("all")

        seen = set()
        for i, q in enumerate(self.log):
            b = q.get("b",""); m = q.get("m",""); c = q.get("c","").upper()
            if fb != L.t("all") and b != fb: continue
            if fm != L.t("all") and m != fm: continue

            nr = len(self.log)-i
            tag = ()
            key = (c, b, m)
            if key in seen: tag = ("dup",)
            elif c in spc: tag = ("spec",)
            elif i%2==0: tag = ("alt",)
            seen.add(key)

            country, _ = DXCC.lookup(c)
            if country == "Unknown": country = ""

            vals = [nr, c, q.get("f",""), b, m, q.get("s","59"), q.get("r","59")]
            if us: vals += [q.get("ss",""), q.get("sr","")]
            vals += [q.get("n",""), country, q.get("d",""), q.get("t","")]
            if isd:
                n = q.get("n","").strip()
                vals.append(str(int(Loc.dist(ml,n))) if Loc.valid(n) and Loc.valid(ml) else "")
            if hs:
                vals.append(Score.qso(q, cc, self.cfg))

            self.tree.insert("","end",iid=str(i), values=vals, tags=tag)

        self._upd_info()

    # ── QSO Operations ───────────────────────────────────────────────────────

    def _get_dt(self):
        if self.man_v.get():
            ds = self.ent["date"].get().strip()
            ts = self.ent["time"].get().strip()
            try:
                datetime.datetime.strptime(ds,"%Y-%m-%d")
                datetime.datetime.strptime(ts,"%H:%M")
                return ds, ts
            except:
                messagebox.showerror(L.t("error"),"YYYY-MM-DD / HH:MM")
                now = datetime.datetime.utcnow()
                return now.strftime("%Y-%m-%d"), now.strftime("%H:%M")
        now = datetime.datetime.utcnow()
        return now.strftime("%Y-%m-%d"), now.strftime("%H:%M")

    def _add_qso(self):
        call = self.ent["call"].get().upper().strip()
        if not call: self.ent["call"].focus(); return
        band = self.ent["band"].get()
        mode = self.ent["mode"].get()
        cc = self._cc()

        dup, di = Score.is_dup(self.log, call, band, mode, self.edit_idx)
        if dup:
            beep("warning")
            if not messagebox.askyesno(L.t("dup_warn"),
                    L.t("dup_msg").format(call,band,mode,len(self.log)-di)):
                return

        ds, ts = self._get_dt()
        q = {"c":call,"b":band,"m":mode,"s":self.ent["rst_s"].get() or "59",
             "r":self.ent["rst_r"].get() or "59","n":self.ent["note"].get(),
             "d":ds,"t":ts,"f":self.ent["freq"].get()}
        if "ss" in self.ent: q["ss"] = self.ent["ss"].get()
        if "sr" in self.ent: q["sr"] = self.ent["sr"].get()

        nm = Score.is_new_mult(self.log, q, cc)

        if self.edit_idx is not None:
            self.log[self.edit_idx] = q
            self.edit_idx = None
            self.log_btn.config(text=L.t("log"), bg=TH["accent"])
        else:
            self.log.insert(0, q)
            self.undo_stack.append(("add",0,q))
            self.serial += 1

        if nm and not dup: beep("success")

        self._clr()
        self._refresh()
        DM.save_log(self._cid(), self.log)

    def _clr(self):
        self.ent["call"].delete(0,"end")
        self.ent["note"].delete(0,"end")
        self.ent["freq"].delete(0,"end")
        if "ss" in self.ent:
            self.ent["ss"].delete(0,"end"); self.ent["ss"].insert(0,str(self.serial))
        if "sr" in self.ent:
            self.ent["sr"].delete(0,"end")
        self.wb_lbl.config(text="")
        self.ent["call"].focus()
        if self.edit_idx is not None:
            self.edit_idx = None
            self.log_btn.config(text=L.t("log"), bg=TH["accent"])

    def _edit_sel(self):
        sel = self.tree.selection()
        if not sel: return
        self.edit_idx = int(sel[0])
        q = self.log[self.edit_idx]
        self.ent["call"].delete(0,"end"); self.ent["call"].insert(0,q.get("c",""))
        self.ent["freq"].delete(0,"end"); self.ent["freq"].insert(0,q.get("f",""))
        self.ent["band"].set(q.get("b","40m"))
        self.ent["mode"].set(q.get("m","SSB"))
        self.ent["rst_s"].delete(0,"end"); self.ent["rst_s"].insert(0,q.get("s","59"))
        self.ent["rst_r"].delete(0,"end"); self.ent["rst_r"].insert(0,q.get("r","59"))
        self.ent["note"].delete(0,"end"); self.ent["note"].insert(0,q.get("n",""))
        if "ss" in self.ent:
            self.ent["ss"].delete(0,"end"); self.ent["ss"].insert(0,q.get("ss",""))
        if "sr" in self.ent:
            self.ent["sr"].delete(0,"end"); self.ent["sr"].insert(0,q.get("sr",""))
        for k in ("date","time"):
            self.ent[k].config(state="normal")
            self.ent[k].delete(0,"end")
            self.ent[k].insert(0, q.get("d" if k=="date" else "t",""))
            if not self.man_v.get(): self.ent[k].config(state="disabled")
        self.log_btn.config(text=L.t("update"), bg=TH["warn"])

    def _del_sel(self):
        sel = self.tree.selection()
        if not sel: return
        if messagebox.askyesno(L.t("confirm_del"),L.t("confirm_del_t")):
            indices = sorted([int(x) for x in sel], reverse=True)
            for idx in indices:
                rem = self.log.pop(idx)
                self.undo_stack.append(("del",idx,rem))
            self._refresh()
            DM.save_log(self._cid(), self.log)

    def _undo(self):
        if not self.undo_stack:
            messagebox.showinfo(L.t("undo"),L.t("undo_empty")); return
        act, idx, q = self.undo_stack.pop()
        if act == "add":
            if idx < len(self.log) and self.log[idx] == q:
                self.log.pop(idx)
                self.serial = max(1, self.serial-1)
        elif act == "del":
            self.log.insert(idx, q)
        self._refresh()
        DM.save_log(self._cid(), self.log)
        beep("info")

    def _clear(self):
        if messagebox.askyesno("⚠",L.t("clear_conf")):
            DM.backup(self._cid(), self.log)
            self.log.clear(); self.serial=1; self.undo_stack.clear()
            self._refresh(); DM.save_log(self._cid(), self.log)

    # ── Events ───────────────────────────────────────────────────────────────

    def _on_enter(self, e):
        if isinstance(self.focus_get(), tk.Entry):
            self._add_qso(); return "break"

    def _on_call_key(self, e=None):
        c = self.ent["call"].get().upper().strip()
        if len(c) >= 3:
            b = self.ent["band"].get(); m = self.ent["mode"].get()
            dup, _ = Score.is_dup(self.log, c, b, m, self.edit_idx)
            if dup:
                self.wb_lbl.config(text=f"⚠ DUP {b}/{m}", fg=TH["err"])
            elif any(q.get("c","").upper()==c for q in self.log):
                self.wb_lbl.config(text=f"ℹ {L.t('wb')} (alt QRG)", fg=TH["warn"])
            else:
                self.wb_lbl.config(text="")
        else:
            self.wb_lbl.config(text="")

    def _on_freq_out(self, e=None):
        f = self.ent["freq"].get().strip()
        if f:
            b = freq2band(f)
            if b and b in self._cc().get("allowed_bands",BANDS_ALL):
                self.ent["band"].set(b)

    def _on_band_change(self, e=None):
        # Update default frequency
        b = self.ent["band"].get()
        if not self.ent["freq"].get().strip():
            self.ent["freq"].delete(0,"end")
            self.ent["freq"].insert(0, str(BAND_FREQ.get(b,"")))

    def _on_mode_change(self, e=None):
        m = self.ent["mode"].get()
        rst = RST_DEFAULTS.get(m, "59")
        for k in ("rst_s","rst_r"):
            self.ent[k].delete(0,"end")
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
        self.cfg["contest"] = self.cv.get(); self.cfg["cat"] = 0
        DM.save("config.json", self.cfg)
        self.log = DM.load_log(self._cid())
        self.serial = len(self.log)+1; self.undo_stack.clear()
        self._rebuild()

    def _switch(self, cid):
        DM.save_log(self._cid(), self.log)
        self.cfg["contest"] = cid; self.cfg["cat"] = 0
        DM.save("config.json", self.cfg)
        self.log = DM.load_log(cid)
        self.serial = len(self.log)+1; self.undo_stack.clear()
        self._rebuild()

    def _cycle_band(self, e=None):
        ab = self._cc().get("allowed_bands",BANDS_ALL)
        if not ab: return
        cur = self.ent["band"].get()
        try: idx = (ab.index(cur)+1) % len(ab)
        except: idx = 0
        self.ent["band"].set(ab[idx])

    def _cycle_mode(self, e=None):
        am = self._cc().get("allowed_modes",MODES_ALL)
        if not am: return
        cur = self.ent["mode"].get()
        try: idx = (am.index(cur)+1) % len(am)
        except: idx = 0
        self.ent["mode"].set(am[idx])
        self._on_mode_change()

    def _tog_man(self):
        m = self.man_v.get()
        st = "normal" if m else "disabled"
        self.ent["date"].config(state=st); self.ent["time"].config(state=st)
        lc = TH["led_off"] if m else TH["led_on"]
        self.led_c.itemconfig(self.led, fill=lc)
        self.st_lbl.config(text=L.t("offline") if m else L.t("online"), fg=lc)
        self.cfg["manual_dt"] = m; DM.save("config.json",self.cfg)

    def _save_cc(self):
        cc = self._cc()
        cats = cc.get("categories",[])
        try: self.cfg["cat"] = cats.index(self.cat_v.get())
        except: self.cfg["cat"] = 0
        if cc.get("use_county") and hasattr(self,'cou_v'):
            self.cfg["county"] = self.cou_v.get()
        DM.save("config.json",self.cfg); self._upd_info(); beep("info")

    def _sort(self, col):
        if self._sort_col == col: self._sort_rev = not self._sort_rev
        else: self._sort_col = col; self._sort_rev = False
        items = [(self.tree.set(k,col),k) for k in self.tree.get_children("")]
        try: items.sort(key=lambda t: int(t[0]) if t[0].lstrip('-').isdigit() else t[0], reverse=self._sort_rev)
        except: items.sort(key=lambda t: t[0], reverse=self._sort_rev)
        for idx,(v,k) in enumerate(items): self.tree.move(k,'',idx)

    def _rebuild(self):
        geo = self.geometry()
        for w in self.winfo_children(): w.destroy()
        self.ent = {}
        self.cfg["win_geo"] = geo
        self._build_menu(); self._build_ui(); self._build_ctx(); self._refresh()

    def _mgr(self):
        d = ContestMgr(self, self.contests); self.wait_window(d)
        if d.result is not None:
            self.contests = d.result; DM.save("contests.json",self.contests)
            if self._cid() not in self.contests:
                self.cfg["contest"]="simplu"; DM.save("config.json",self.cfg)
                self.log = DM.load_log("simplu")
            self._rebuild()

    # ── Dialogs ──────────────────────────────────────────────────────────────

    def _about(self):
        d = tk.Toplevel(self); d.title(L.t("about")); d.geometry("480x340")
        d.resizable(False,False); d.configure(bg=TH["bg"]); d.transient(self); d.grab_set()
        tk.Label(d, text="📻 YO Log PRO v16.0 FINAL", bg=TH["bg"], fg=TH["accent"],
                font=("Consolas",16,"bold")).pack(pady=12)
        tk.Label(d, text="Professional Multi-Contest Logger\nFinal Edition", bg=TH["bg"],
                fg=TH["warn"], font=("Consolas",11)).pack()
        tk.Label(d, text=L.t("credits"), bg=TH["bg"], fg=TH["fg"], font=self.fn,
                justify="center").pack(pady=8)
        tk.Label(d, text=L.t("usage"), bg=TH["bg"], fg=TH["fg"],
                font=("Consolas",10), justify="left").pack(pady=6, padx=15)
        tk.Button(d, text=L.t("close"), command=d.destroy, bg=TH["accent"],
                 fg="white", width=12).pack(pady=10)

    def _settings(self):
        d = tk.Toplevel(self); d.title(L.t("settings")); d.geometry("410x440")
        d.resizable(False,False); d.configure(bg=TH["bg"]); d.transient(self); d.grab_set()
        eo = {"bg":TH["entry_bg"],"fg":TH["fg"],"font":self.fn}
        tk.Label(d, text=L.t("station_info"), bg=TH["bg"], fg=TH["accent"],
                font=self.fb).pack(pady=6, anchor="w", padx=15)
        es = {}
        for k, lb, v in [
            ("call",L.t("call"),self.cfg.get("call","")),
            ("loc",L.t("locator"),self.cfg.get("loc","")),
            ("jud",L.t("county"),self.cfg.get("jud","")),
            ("addr",L.t("address"),self.cfg.get("addr","")),
            ("op_name",L.t("op"),self.cfg.get("op_name","")),
            ("power",L.t("power"),self.cfg.get("power","100")),
        ]:
            tk.Label(d, text=lb, bg=TH["bg"], fg=TH["fg"]).pack(anchor="w", padx=15)
            e = tk.Entry(d, width=38, **eo); e.insert(0,v); e.pack(pady=1, padx=15, fill="x")
            es[k] = e
        tk.Label(d, text=L.t("font_size"), bg=TH["bg"], fg=TH["fg"]).pack(anchor="w", padx=15)
        fs_e = tk.Entry(d, width=8, **eo); fs_e.insert(0,str(self.cfg.get("fs",11)))
        fs_e.pack(pady=1, padx=15, anchor="w")
        sv = tk.BooleanVar(value=self.cfg.get("sounds",True))
        tk.Checkbutton(d, text=L.t("en_sounds"), variable=sv, bg=TH["bg"], fg=TH["fg"],
                      selectcolor=TH["entry_bg"]).pack(anchor="w", padx=15, pady=3)
        def save():
            self.cfg["call"]=es["call"].get().upper().strip()
            self.cfg["loc"]=es["loc"].get().upper().strip()
            self.cfg["jud"]=es["jud"].get().upper().strip()
            self.cfg["addr"]=es["addr"].get().strip()
            self.cfg["op_name"]=es["op_name"].get().strip()
            self.cfg["power"]=es["power"].get().strip()
            self.cfg["sounds"]=sv.get()
            try: self.cfg["fs"]=int(fs_e.get())
            except: self.cfg["fs"]=11
            DM.save("config.json",self.cfg); self._upd_info()
            messagebox.showinfo("OK",L.t("sett_ok")); d.destroy()
        tk.Button(d, text=L.t("save"), command=save, bg=TH["accent"], fg="white",
                 width=12, font=self.fn).pack(pady=10)

    def _search_dlg(self):
        d = tk.Toplevel(self); d.title(L.t("search_t")); d.geometry("500x380")
        d.configure(bg=TH["bg"]); d.transient(self); d.grab_set()
        tf = tk.Frame(d, bg=TH["bg"], pady=8); tf.pack(fill="x", padx=8)
        tk.Label(tf, text=L.t("search_l"), bg=TH["bg"], fg=TH["fg"], font=self.fn).pack(side="left")
        se = tk.Entry(tf, width=22, bg=TH["entry_bg"], fg=TH["fg"], font=("Consolas",12),
                     insertbackground=TH["fg"]); se.pack(side="left", padx=6); se.focus()
        rf = tk.Frame(d, bg=TH["bg"]); rf.pack(fill="both", expand=True, padx=8, pady=3)
        cols = ("nr","call","band","mode","date","time")
        tree2 = ttk.Treeview(rf, columns=cols, show="headings", height=12)
        for c, h, w in zip(cols,["#",L.t("call"),L.t("band"),L.t("mode"),L.t("data"),L.t("ora")],
                           [38,110,55,55,80,55]):
            tree2.heading(c, text=h); tree2.column(c, width=w, anchor="center")
        tree2.pack(fill="both", expand=True)
        cl = tk.Label(d, text="", bg=TH["bg"], fg=TH["fg"], font=("Consolas",10)); cl.pack(pady=3)
        def srch(e=None):
            q = se.get().upper().strip()
            for i in tree2.get_children(): tree2.delete(i)
            if not q: cl.config(text=""); return
            res = []
            for i, qso in enumerate(self.log):
                if q in qso.get("c","").upper() or q in qso.get("n","").upper():
                    res.append((len(self.log)-i, qso))
            for nr, qso in res:
                tree2.insert("","end",values=(nr,qso.get("c",""),qso.get("b",""),
                    qso.get("m",""),qso.get("d",""),qso.get("t","")))
            cl.config(text=f"{len(res)} {L.t('results').lower()}" if res else L.t("no_res"))
        se.bind("<KeyRelease>", srch)

    def _timer_dlg(self):
        d = tk.Toplevel(self); d.title(L.t("timer_t")); d.geometry("300x200")
        d.configure(bg=TH["bg"]); d.transient(self); d.resizable(False,False)
        run = [False]; st = [None]
        f = tk.Frame(d, bg=TH["bg"], pady=8); f.pack(fill="both", expand=True, padx=12)
        tk.Label(f, text=L.t("dur_h"), bg=TH["bg"], fg=TH["fg"], font=self.fn).pack()
        de = tk.Entry(f, width=8, bg=TH["entry_bg"], fg=TH["fg"], font=("Consolas",13),
                     justify="center", insertbackground=TH["fg"])
        de.insert(0,"4"); de.pack(pady=3)
        el = tk.Label(f, text=L.t("elapsed")+" 00:00:00", bg=TH["bg"], fg=TH["ok"],
                     font=("Consolas",14,"bold")); el.pack(pady=2)
        rl = tk.Label(f, text=L.t("remaining")+" --:--:--", bg=TH["bg"], fg=TH["warn"],
                     font=("Consolas",12)); rl.pack(pady=2)
        def tick():
            if run[0] and st[0]:
                delta = (datetime.datetime.utcnow()-st[0]).total_seconds()
                h,m,s = int(delta//3600),int(delta%3600//60),int(delta%60)
                el.config(text=f"{L.t('elapsed')} {h:02d}:{m:02d}:{s:02d}")
                try: dh = float(de.get())
                except: dh = 4
                rem = max(0, dh*3600-delta)
                rh,rm,rs = int(rem//3600),int(rem%3600//60),int(rem%60)
                rl.config(text=f"{L.t('remaining')} {rh:02d}:{rm:02d}:{rs:02d}",
                         fg=TH["err"] if rem<=1800 else TH["warn"])
                if rem <= 0: beep("warning")
            d.after(1000, tick)
        def tog():
            if not run[0]:
                st[0]=datetime.datetime.utcnow(); run[0]=True
                sb.config(text=L.t("timer_stop"), bg=TH["warn"])
            else:
                run[0]=False; sb.config(text=L.t("timer_start"), bg=TH["ok"])
        bf = tk.Frame(f, bg=TH["bg"]); bf.pack(pady=6)
        sb = tk.Button(bf, text=L.t("timer_start"), command=tog, bg=TH["ok"], fg="white",
                      font=self.fn, width=9, cursor="hand2"); sb.pack(side="left", padx=4)
        tk.Button(bf, text=L.t("timer_reset"), command=lambda: [run.__setitem__(0,False),
            st.__setitem__(0,None), el.config(text=L.t("elapsed")+" 00:00:00"),
            rl.config(text=L.t("remaining")+" --:--:--"),
            sb.config(text=L.t("timer_start"),bg=TH["ok"])],
            bg=TH["err"], fg="white", font=self.fn, width=9, cursor="hand2").pack(side="left", padx=4)
        tick()

    def _stats(self):
        StatsWindow(self, self.log, self._cc(), self.cfg)

    def _validate(self):
        ok, msg, sc = Score.validate(self.log, self._cc(), self.cfg)
        if ok:
            mq = self._cc().get("min_qso",0)
            if mq > 0:
                msg += f"\nDiplomă: {'DA/YES' if len(self.log)>=mq else 'NU/NO'}"
            messagebox.showinfo(L.t("val_result"), msg); beep("success")
        else:
            messagebox.showwarning(L.t("val_result"), msg); beep("error")

    # ── Import ───────────────────────────────────────────────────────────────

    def _import_menu(self):
        d = tk.Toplevel(self); d.title(L.t("import_log")); d.geometry("260x160")
        d.resizable(False,False); d.configure(bg=TH["bg"]); d.transient(self); d.grab_set()
        tk.Label(d, text=L.t("sel_fmt"), bg=TH["bg"], fg=TH["fg"], font=self.fb).pack(pady=10)
        tk.Button(d, text=L.t("imp_adif")+" (.adi)", command=lambda: [d.destroy(), self._import_adif()],
                 bg=TH["accent"], fg="white", width=20).pack(pady=3)
        tk.Button(d, text=L.t("imp_csv")+" (.csv)", command=lambda: [d.destroy(), self._import_csv()],
                 bg=TH["accent"], fg="white", width=20).pack(pady=3)
        tk.Button(d, text=L.t("cancel"), command=d.destroy, bg=TH["btn_bg"], fg="white", width=20).pack(pady=8)

    def _import_adif(self):
        fp = filedialog.askopenfilename(filetypes=[("ADIF","*.adi *.adif"),("All","*.*")])
        if not fp: return
        try:
            with open(fp, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
            qsos = Importer.parse_adif(text)
            if qsos:
                self.log.extend(qsos)
                self._refresh()
                DM.save_log(self._cid(), self.log)
                messagebox.showinfo("OK", L.t("imp_ok").format(len(qsos)))
            else:
                messagebox.showwarning(L.t("error"), L.t("no_res"))
        except Exception as e:
            messagebox.showerror(L.t("error"), f"{L.t('imp_err')}\n{e}")

    def _import_csv(self):
        fp = filedialog.askopenfilename(filetypes=[("CSV","*.csv"),("All","*.*")])
        if not fp: return
        try:
            with open(fp, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
            qsos = Importer.parse_csv(text)
            if qsos:
                self.log.extend(qsos)
                self._refresh()
                DM.save_log(self._cid(), self.log)
                messagebox.showinfo("OK", L.t("imp_ok").format(len(qsos)))
            else:
                messagebox.showwarning(L.t("error"), L.t("no_res"))
        except Exception as e:
            messagebox.showerror(L.t("error"), f"{L.t('imp_err')}\n{e}")

    # ── Export ───────────────────────────────────────────────────────────────

    def _export_dlg(self):
        d = tk.Toplevel(self); d.title(L.t("export")); d.geometry("280x260")
        d.resizable(False,False); d.configure(bg=TH["bg"]); d.transient(self); d.grab_set()
        tk.Label(d, text=L.t("sel_fmt"), bg=TH["bg"], fg=TH["fg"], font=self.fb).pack(pady=10)
        for txt, cmd in [
            ("Cabrillo 3.0 (.log)", lambda: self._exp_cab(d)),
            ("ADIF 3.1 (.adi)", lambda: self._exp_adif(d)),
            ("CSV (.csv)", lambda: self._exp_csv(d)),
            ("EDI (.edi)", lambda: self._exp_edi(d)),
        ]:
            tk.Button(d, text=txt, command=cmd, bg=TH["accent"], fg="white", width=22).pack(pady=2)
        tk.Button(d, text=L.t("cancel"), command=d.destroy, bg=TH["btn_bg"], fg="white", width=22).pack(pady=8)

    def _exp_cab(self, parent):
        try:
            cc = self._cc(); cid = self._cid()
            my = self.cfg.get("call","NOCALL")
            nm = cc.get("name_"+L.g(), cid)
            ci = self.cfg.get("cat",0)
            cats = cc.get("categories",["ALL"])
            cat = cats[ci] if 0<=ci<len(cats) else "ALL"
            lines = [
                "START-OF-LOG: 3.0", f"CONTEST: {nm}", f"CALLSIGN: {my}",
                f"LOCATION: {self.cfg.get('loc','')}", f"GRID-LOCATOR: {self.cfg.get('loc','')}",
                "CATEGORY-OPERATOR: SINGLE-OP", "CATEGORY-BAND: ALL",
                f"CATEGORY-POWER: {self.cfg.get('power','100')}W", "CATEGORY-MODE: MIXED",
                f"CATEGORY: {cat}", f"CLUB: ",
                "CREATED-BY: YO Log PRO v16.0 FINAL",
                f"NAME: {self.cfg.get('op_name','')}", f"ADDRESS: {self.cfg.get('addr','')}",
                "SOAPBOX: Generated by YO Log PRO v16.0 FINAL",
            ]
            for q in self.log:
                freq = q.get("f","") or str(BAND_FREQ.get(q.get("b",""),0))
                l = f"QSO: {freq:>6} {q['m']:<4} {q['d']} {q['t']} {my:<13} {q.get('s','59'):>3}"
                if q.get('ss'): l += f" {q['ss']:>4}"
                l += f" {q['c']:<13} {q.get('r','59'):>3}"
                if q.get('sr'): l += f" {q['sr']:>4}"
                if q.get('n'): l += f" {q['n']}"
                lines.append(l)
            lines.append("END-OF-LOG:")
            fn = f"cabrillo_{cid}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.log"
            with open(os.path.join(get_data_dir(),fn),"w",encoding="utf-8") as f:
                f.write("\n".join(lines))
            messagebox.showinfo(L.t("exp_ok"),f"→ {fn}"); parent.destroy()
        except Exception as e: messagebox.showerror(L.t("error"),str(e))

    def _exp_adif(self, parent):
        try:
            lines = ["ADIF export by YO Log PRO v16.0","<ADIF_VER:5>3.1.0",
                     "<PROGRAMID:14>YO_Log_PRO_v16","<PROGRAMVERSION:4>16.0","<EOH>",""]
            for q in self.log:
                r = ""
                for tag, k in [("CALL","c"),("BAND","b"),("MODE","m")]:
                    v=q.get(k,""); r+=f"<{tag}:{len(v)}>{v}"
                dc=q.get('d','').replace("-","")
                r+=f"<QSO_DATE:{len(dc)}>{dc}"
                tc=q.get('t','').replace(":","")+"00"
                r+=f"<TIME_ON:{len(tc)}>{tc}"
                r+=f"<RST_SENT:{len(q.get('s','59'))}>{q.get('s','59')}"
                r+=f"<RST_RCVD:{len(q.get('r','59'))}>{q.get('r','59')}"
                if q.get("f"):
                    # ADIF freq in MHz
                    try:
                        mhz = f"{float(q['f'])/1000:.6f}"
                        r+=f"<FREQ:{len(mhz)}>{mhz}"
                    except: pass
                if q.get("ss"): r+=f"<STX:{len(q['ss'])}>{q['ss']}"
                if q.get("sr"): r+=f"<SRX:{len(q['sr'])}>{q['sr']}"
                n=q.get("n","")
                if n:
                    if Loc.valid(n): r+=f"<GRIDSQUARE:{len(n)}>{n}"
                    else: r+=f"<COMMENT:{len(n)}>{n}"
                ml=self.cfg.get("loc","")
                if ml: r+=f"<MY_GRIDSQUARE:{len(ml)}>{ml}"
                r+="<EOR>"; lines.append(r)
            fn = f"adif_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.adi"
            with open(os.path.join(get_data_dir(),fn),"w",encoding="utf-8") as f:
                f.write("\n".join(lines))
            messagebox.showinfo(L.t("exp_ok"),f"→ {fn}"); parent.destroy()
        except Exception as e: messagebox.showerror(L.t("error"),str(e))

    def _exp_csv(self, parent):
        try:
            cc=self._cc(); us=cc.get("use_serial",False)
            fn = f"log_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv"
            with open(os.path.join(get_data_dir(),fn),"w",encoding="utf-8",newline='') as f:
                w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
                h=["Nr","Date","Time","Call","Freq","Band","Mode","RST_S","RST_R"]
                if us: h+=["Serial_S","Serial_R"]
                h+=["Note","Country","Score"]
                w.writerow(h)
                for i, q in enumerate(self.log):
                    sc=Score.qso(q,cc,self.cfg); co,_=DXCC.lookup(q.get("c",""))
                    row=[len(self.log)-i,q.get('d',''),q.get('t',''),q.get('c',''),
                         q.get('f',''),q.get('b',''),q.get('m',''),q.get('s',''),q.get('r','')]
                    if us: row+=[q.get('ss',''),q.get('sr','')]
                    row+=[q.get('n',''),co,sc]
                    w.writerow(row)
            messagebox.showinfo(L.t("exp_ok"),f"→ {fn}"); parent.destroy()
        except Exception as e: messagebox.showerror(L.t("error"),str(e))

    def _exp_edi(self, parent):
        try:
            cc=self._cc(); my=self.cfg.get("call","NOCALL"); ml=self.cfg.get("loc","")
            lines=[
                "[REG1TEST;1]",f"TName={cc.get('name_en','Contest')}",
                f"TDate={datetime.datetime.now().strftime('%Y%m%d')};{datetime.datetime.now().strftime('%Y%m%d')}",
                f"PCall={my}",f"PWWLo={ml}",f"PExch=",
                f"PAdr1={self.cfg.get('addr','')}",f"PSect={self.cfg.get('jud','')}",
                f"PBand=","PClub=",f"RName={self.cfg.get('op_name','')}",f"RCall={my}",
                f"RPow={self.cfg.get('power','100')}","RHBF=2","MODe=","STXFreq=",
                "Mession=0",f"[QSORecords;{len(self.log)}]",
            ]
            for q in self.log:
                dt=q.get("d","").replace("-","")[2:]
                tm=q.get("t","").replace(":","")
                n=q.get("n",""); loc=n if Loc.valid(n) else ""
                dist=int(Loc.dist(ml,loc)) if loc and ml else 0
                lines.append(f"{dt};{tm};{q.get('c','')};{q.get('s','59')};{q.get('ss','001')};{q.get('r','59')};{q.get('sr','001')};{loc};{dist};;")
            fn = f"edi_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.edi"
            with open(os.path.join(get_data_dir(),fn),"w",encoding="utf-8") as f:
                f.write("\n".join(lines))
            messagebox.showinfo(L.t("exp_ok"),f"→ {fn}"); parent.destroy()
        except Exception as e: messagebox.showerror(L.t("error"),str(e))

    # ── Print / Verify / Backup ──────────────────────────────────────────────

    def _print_log(self):
        try:
            cc = self._cc()
            fn = f"print_{self._cid()}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt"
            fp = os.path.join(get_data_dir(), fn)
            with open(fp, "w", encoding="utf-8") as f:
                f.write(f"{'='*70}\n")
                f.write(f"  YO Log PRO v16.0 — {self.cfg.get('call','')} — {cc.get('name_'+L.g(),self._cid())}\n")
                f.write(f"  Printed: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
                f.write(f"{'='*70}\n\n")
                f.write(f"{'Nr':>4} {'Call':<14} {'Band':<6} {'Mode':<5} {'RST S':<6} {'RST R':<6} {'Note':<12} {'Date':<11} {'Time':<6}\n")
                f.write(f"{'-'*70}\n")
                for i, q in enumerate(self.log):
                    nr = len(self.log)-i
                    f.write(f"{nr:>4} {q.get('c',''):<14} {q.get('b',''):<6} {q.get('m',''):<5} {q.get('s',''):<6} {q.get('r',''):<6} {q.get('n',''):<12} {q.get('d',''):<11} {q.get('t',''):<6}\n")
                f.write(f"\n{'='*70}\n")
                qp,mc,tot = Score.total(self.log, cc, self.cfg)
                f.write(f"  Total: {len(self.log)} QSO | Score: {tot}\n")
                f.write(f"{'='*70}\n")
            messagebox.showinfo(L.t("print_log"), f"→ {fn}")
        except Exception as e:
            messagebox.showerror(L.t("error"), str(e))

    def _verify(self):
        raw = json.dumps(self.log, sort_keys=True, ensure_ascii=False)
        h = hashlib.md5(raw.encode()).hexdigest()[:12]
        messagebox.showinfo(L.t("verify"), L.t("verify_ok").format(len(self.log), h))

    def _bak(self):
        if DM.backup(self._cid(), self.log):
            messagebox.showinfo("OK",L.t("bak_ok"))
        else:
            messagebox.showerror(L.t("error"),L.t("bak_err"))

    def _exit(self):
        if messagebox.askyesno(L.t("exit_t"),L.t("exit_m")):
            self.cfg["win_geo"] = self.geometry()
            DM.save_log(self._cid(), self.log)
            DM.save("config.json", self.cfg)
            DM.save("contests.json", self.contests)
            DM.backup(self._cid(), self.log)
            self.destroy()


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    app = App()
    app.mainloop()
