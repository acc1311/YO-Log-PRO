#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YO Log PRO v16.5 FINAL — Professional Multi-Contest Amateur Radio Logger
Developed by: Ardei Constantin-Cătălin (YO8ACR)
Email: yo8acr@gmail.com

FIXES v16.5:
- FIXED: Frequency, band, mode and RST persist between QSOs (only call and note clear)
- Keep all operating parameters until manually changed

FIXES v16.4:
- ADDED: Cabrillo 2.0 export with configurable exchange dialog
- ADDED: Exchange options: County/Grid/Serial/None for sent, Log/None for received
- ADDED: Preview dialog before Cabrillo export
- ADDED: Import Cabrillo 2.0 and 3.0 formats
- ADDED: cabrillo_name field in contest editor
- ADDED: exchange_format field per contest
- ADDED: Email and Soapbox fields in settings
- ADDED: Validation + auto-backup before export
- ADDED: Save dialog for all exports
"""

import os, sys, re, csv, copy, json, math, datetime, io, hashlib
from pathlib import Path
from collections import Counter, deque
import tkinter as tk
from tkinter import ttk, messagebox, Menu, filedialog, scrolledtext

try:
    if sys.platform == "win32":
        import winsound; HAS_SOUND = True
    else: HAS_SOUND = False
except ImportError: HAS_SOUND = False

def get_data_dir():
    if getattr(sys,'frozen',False): return os.path.dirname(sys.executable)
    return os.path.abspath(".")

def beep(kind="info"):
    if not HAS_SOUND: return
    try: winsound.MessageBeep({"error":0x10,"warning":0x30,"success":0x40,"info":0x0}.get(kind,0x0))
    except: pass

def center_dialog(dialog, parent=None):
    dialog.update_idletasks()
    m = re.match(r'(\d+)x(\d+)', dialog.geometry())
    dw, dh = (int(m.group(1)), int(m.group(2))) if m else (dialog.winfo_reqwidth(), dialog.winfo_reqheight())
    if parent and parent.winfo_exists():
        x = parent.winfo_rootx() + (parent.winfo_width()-dw)//2
        y = parent.winfo_rooty() + (parent.winfo_height()-dh)//2
    else:
        x = (dialog.winfo_screenwidth()-dw)//2; y = (dialog.winfo_screenheight()-dh)//2
    dialog.geometry(f"{dw}x{dh}+{max(0,x)}+{max(0,y)}")

class Loc:
    @staticmethod
    def to_latlon(loc):
        loc = loc.upper().strip()
        if len(loc)<4: return None,None
        try:
            lon = (ord(loc[0])-65)*20-180; lat = (ord(loc[1])-65)*10-90
            lon += int(loc[2])*2; lat += int(loc[3])
            if len(loc)>=6: lon += (ord(loc[4])-65)*(2/24)+1/24; lat += (ord(loc[5])-65)*(1/24)+0.5/24
            else: lon += 1.0; lat += 0.5
            return lat, lon
        except: return None, None

    @staticmethod
    def dist(a, b):
        la1,lo1 = Loc.to_latlon(a); la2,lo2 = Loc.to_latlon(b)
        if None in (la1,lo1,la2,lo2): return 0
        d1=math.radians(la2-la1); d2=math.radians(lo2-lo1)
        a_=math.sin(d1/2)**2+math.cos(math.radians(la1))*math.cos(math.radians(la2))*math.sin(d2/2)**2
        return round(6371.0*2*math.atan2(math.sqrt(a_),math.sqrt(1-a_)),1)

    @staticmethod
    def valid(s):
        s = s.upper().strip()
        if len(s)==4: return s[0:2].isalpha() and s[2:4].isdigit() and 'A'<=s[0]<='R' and 'A'<=s[1]<='R'
        if len(s)==6: return s[0:2].isalpha() and s[2:4].isdigit() and s[4:6].isalpha() and 'A'<=s[0]<='R' and 'A'<=s[1]<='R' and 'A'<=s[4]<='X' and 'A'<=s[5]<='X'
        return False

class DXCC:
    DB = {
        "YO":"Romania","YP":"Romania","YQ":"Romania","YR":"Romania",
        "DL":"Germany","DJ":"Germany","DK":"Germany","DA":"Germany","DB":"Germany","DC":"Germany","DD":"Germany","DF":"Germany","DG":"Germany","DH":"Germany","DM":"Germany",
        "G":"England","M":"England","2E":"England","GW":"Wales","GM":"Scotland","GI":"N. Ireland","GD":"Isle of Man","GJ":"Jersey","GU":"Guernsey",
        "F":"France","TM":"France","HB9":"Switzerland","HB":"Switzerland",
        "I":"Italy","IK":"Italy","IZ":"Italy","IW":"Italy","IN3":"Italy",
        "EA":"Spain","EB":"Spain","EC":"Spain","EE":"Spain","CT":"Portugal","CS":"Portugal","CU":"Azores",
        "SP":"Poland","SQ":"Poland","SN":"Poland","SO":"Poland","3Z":"Poland",
        "HA":"Hungary","HG":"Hungary","OK":"Czech Rep.","OL":"Czech Rep.","OM":"Slovak Rep.","LZ":"Bulgaria",
        "UR":"Ukraine","US":"Ukraine","UT":"Ukraine","UX":"Ukraine","UY":"Ukraine",
        "UA":"Russia","RU":"Russia","RV":"Russia","RW":"Russia","RA":"Russia","OE":"Austria",
        "ON":"Belgium","OO":"Belgium","OR":"Belgium","OT":"Belgium",
        "PA":"Netherlands","PB":"Netherlands","PD":"Netherlands","PE":"Netherlands",
        "OZ":"Denmark","OU":"Denmark","5Q":"Denmark",
        "SM":"Sweden","SA":"Sweden","SB":"Sweden","SK":"Sweden",
        "LA":"Norway","LB":"Norway","LC":"Norway",
        "OH":"Finland","OF":"Finland","OG":"Finland","OI":"Finland",
        "ES":"Estonia","YL":"Latvia","LY":"Lithuania",
        "9A":"Croatia","S5":"Slovenia","E7":"Bosnia","Z3":"N. Macedonia","Z6":"Kosovo","ZA":"Albania",
        "SV":"Greece","SW":"Greece","SX":"Greece","SY":"Greece",
        "TA":"Turkey","TC":"Turkey","YM":"Turkey","4X":"Israel","4Z":"Israel",
        "SU":"Egypt","CN":"Morocco","7X":"Algeria","3V":"Tunisia",
        "ZS":"South Africa","ZR":"South Africa","ZU":"South Africa",
        "W":"USA","K":"USA","N":"USA","AA":"USA","AB":"USA","AC":"USA","AD":"USA","AE":"USA","AF":"USA","AG":"USA","AI":"USA","AK":"USA",
        "KH6":"Hawaii","KL7":"Alaska","KP4":"Puerto Rico",
        "VE":"Canada","VA":"Canada","VY":"Canada","VO":"Canada",
        "XE":"Mexico","XA":"Mexico","4A":"Mexico",
        "PY":"Brazil","PP":"Brazil","PR":"Brazil","PS":"Brazil","PT":"Brazil","PU":"Brazil",
        "LU":"Argentina","LW":"Argentina","LO":"Argentina","CE":"Chile","CA":"Chile","XQ":"Chile",
        "JA":"Japan","JH":"Japan","JR":"Japan","JE":"Japan","JF":"Japan","JG":"Japan","JI":"Japan","JJ":"Japan","JK":"Japan","JL":"Japan",
        "BY":"China","BA":"China","BD":"China","BG":"China","BI":"China",
        "HL":"S. Korea","DS":"S. Korea","6K":"S. Korea","DU":"Philippines","DX":"Philippines",
        "HS":"Thailand","E2":"Thailand","VK":"Australia","AX":"Australia","ZL":"New Zealand","ZM":"New Zealand",
        "VU":"India","AT":"India","VT":"India","AP":"Pakistan",
        "A4":"Oman","A6":"UAE","A7":"Qatar","A9":"Bahrain","9K":"Kuwait","HZ":"Saudi Arabia","7Z":"Saudi Arabia",
        "EK":"Armenia","4J":"Azerbaijan","4L":"Georgia","UN":"Kazakhstan","JT":"Mongolia",
        "XV":"Vietnam","3W":"Vietnam","TF":"Iceland","JW":"Svalbard","OX":"Greenland","OY":"Faroe Is.",
        "T7":"San Marino","3A":"Monaco","C3":"Andorra","HV":"Vatican","9H":"Malta","5B":"Cyprus","4O":"Montenegro",
    }
    @staticmethod
    def lookup(call):
        call = call.upper().strip().split("/")[0]
        for n in range(min(4,len(call)),0,-1):
            if call[:n] in DXCC.DB: return DXCC.DB[call[:n]], call[:n]
        if call and call[0] in DXCC.DB: return DXCC.DB[call[0]], call[0]
        return "Unknown", call[:2] if len(call)>=2 else call
    @staticmethod
    def prefix(call): return DXCC.lookup(call)[1]

FREQ_MAP = {(1800,2000):"160m",(3500,3800):"80m",(5351,5367):"60m",(7000,7200):"40m",(10100,10150):"30m",(14000,14350):"20m",(18068,18168):"17m",(21000,21450):"15m",(24890,24990):"12m",(28000,29700):"10m",(50000,54000):"6m",(144000,148000):"2m",(430000,440000):"70cm",(1240000,1300000):"23cm"}
BAND_FREQ = {"160m":1850,"80m":3700,"60m":5355,"40m":7100,"30m":10120,"20m":14200,"17m":18120,"15m":21200,"12m":24940,"10m":28500,"6m":50150,"2m":145000,"70cm":432200,"23cm":1296200}
RST_DEFAULTS = {"SSB":"59","AM":"59","FM":"59","SSTV":"59","CW":"599","RTTY":"599","PSK31":"599","DIGI":"599","FT8":"-10","FT4":"-10","JT65":"-15"}
CAB2_MODE_MAP = {"SSB":"PH","AM":"PH","FM":"PH","SSTV":"PH","CW":"CW","RTTY":"RY","PSK31":"RY","FT8":"DG","FT4":"DG","JT65":"DG","DIGI":"DG"}
CAB2_MODE_REV = {"PH":"SSB","CW":"CW","RY":"RTTY","DG":"FT8"}

def freq2band(f):
    try:
        f = float(f)
        for (lo,hi),b in FREQ_MAP.items():
            if lo<=f<=hi: return b
    except: pass
    return None

BANDS_HF = ["160m","80m","60m","40m","30m","20m","17m","15m","12m","10m"]
BANDS_VHF = ["6m","2m"]; BANDS_UHF = ["70cm","23cm"]; BANDS_ALL = BANDS_HF+BANDS_VHF+BANDS_UHF
MODES_ALL = ["SSB","CW","DIGI","FT8","FT4","RTTY","AM","FM","PSK31","SSTV","JT65"]
SCORING_MODES = ["none","per_qso","per_band","maraton","multiplier","distance","custom"]
EXCHANGE_FORMATS = ["none","county","grid","serial","zone","custom"]
CONTEST_TYPES = ["Simplu","Maraton","Stafeta","YO","DX","VHF","UHF","Field Day","Sprint","QSO Party","SOTA","POTA","Custom"]
YO_COUNTIES = ["AB","AR","AG","BC","BH","BN","BT","BV","BR","BZ","CS","CL","CJ","CT","CV","DB","DJ","GL","GR","GJ","HR","HD","IL","IS","IF","MM","MH","MS","NT","OT","PH","SM","SJ","SB","SV","TR","TM","TL","VS","VL","VN","B"]

EXCH_SENT_OPTIONS = {
    "ro": {"county":"Județ ({jud})","grid":"Locator ({loc})","serial":"Nr. Serial","none":"Nimic (--)"},
    "en": {"county":"County ({jud})","grid":"Locator ({loc})","serial":"Serial Nr.","none":"None (--)"}
}
EXCH_RCVD_OPTIONS = {
    "ro": {"log":"Din log (notă/serial)","none":"Nimic (--)"},
    "en": {"log":"From log (note/serial)","none":"None (--)"}
}

T = {
    "ro": {
        "app_title":"YO Log PRO v16.5","call":"Indicativ","band":"Bandă","mode":"Mod",
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
        "add_c":"➕ Adaugă","edit_c":"✏ Editează","del_c":"🗑 Șterge",
        "dup_c":"📋 Duplică","exp_c":"📤 Export JSON","imp_c":"📥 Import JSON",
        "c_name":"Nume Concurs:","c_type":"Tip:","sc_mode":"Punctare:",
        "cats":"Categorii (o linie):","a_bands":"Benzi permise:","a_modes":"Moduri permise:",
        "req_st_c":"Stații Obligatorii (o linie):","sp_sc":"Punctare Specială (CALL=PTS):",
        "ppq":"Puncte/QSO:","min_qso":"Min QSO:","use_serial":"Nr. Seriale",
        "use_county":"Județ","county_list":"Județe (virgulă):","no_sel":"Neselectat!",
        "del_c_conf":"Ștergeți '{}'?","c_saved":"Salvat!","c_del":"Șters!",
        "c_exists":"ID existent!","c_default":"Protejat!","c_id":"ID Concurs:",
        "mults":"Multiplicatori:","band_pts":"Puncte/Bandă (BAND=PTS):",
        "nr":"Nr.","pts":"Pt",
        "dup_warn":"⚠ Duplicat!","dup_msg":"{} pe {} {}!\nQSO #{}\n\nAdăugați?",
        "search_t":"Căutare","search_l":"Caută:","results":"Rezultate",
        "no_res":"Nimic găsit.","undo":"↩ Undo","undo_ok":"Anulat.",
        "undo_empty":"Nimic de anulat.","rate":"QSO/h","timer":"⏱ Timer",
        "timer_t":"Timer Concurs","timer_start":"▶ Start","timer_stop":"⏸ Stop",
        "timer_reset":"⏹ Reset","elapsed":"Scurs:","remaining":"Rămas:",
        "dur_h":"Durată (ore):","band_sum":"Benzi",
        "distance":"Dist","country":"Țara","utc":"UTC","autosaved":"Salvat",
        "sounds":"Sunete","en_sounds":"Activează sunete",
        "qso_pts":"Puncte QSO","mult_c":"Multiplicatori","new_mult":"✦ MULT NOU!",
        "op":"Operator:","power":"Putere (W):","f_band":"Bandă:","f_mode":"Mod:",
        "all":"Toate","clear_log":"🗑 Golire log",
        "clear_conf":"Goliți COMPLET logul?\nSe va face backup automat!\nIREVERSIBIL!",
        "wb":"Lucrat alt QRG","imp_adif":"Import ADIF","imp_csv":"Import CSV",
        "imp_ok":"Importate {} QSO!","imp_err":"Eroare import!",
        "qso_total":"Total QSO","unique":"Unice","countries":"Țări",
        "print_log":"🖨 Print",
        "verify":"Verificare log","verify_ok":"Log integru: {} QSO, hash: {}",
        "score_f":"Scor","worked_all":"Status Complet",
        "worked_x":"Lucrate: {}/{}","missing_x":"Lipsesc: {}",
        "tools":"🛠 Utilități","clear_c":"Golire log curent",
        "save_cat":"💾 Salvează",
        "exp_edi":"EDI (.edi)","exp_print":"Print (.txt)",
        "hash_ok":"Hash MD5 OK","hash_err":"Eroare hash",
        "exp_cab2":"Cabrillo 2.0 (.log)",
        "email_l":"Email:","soapbox":"SOAPBOX:",
        "cab_name":"Nume Cabrillo:","exch_fmt":"Format Exchange:",
        "soapbox_l":"Soapbox:","imp_cab":"Import Cabrillo",
        "preview":"👁 Previzualizare","preview_t":"Previzualizare Export",
        "exp_warn":"⚠ Atenție!",
        "exp_warn_msg":"Logul are probleme:\n{}\n\nContinuați exportul?",
        "switch_conf":"Schimbați concursul?\nLogul curent va fi salvat.",
        "exch_sent_l":"Exchange TRIMIS:","exch_rcvd_l":"Exchange PRIMIT:",
        "cab2_config":"Configurare Cabrillo 2.0","cab2_export":"📤 Exportă",
    },
    "en": {
        "app_title":"YO Log PRO v16.5","call":"Callsign","band":"Band","mode":"Mode",
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
        "add_c":"➕ Add","edit_c":"✏ Edit","del_c":"🗑 Delete",
        "dup_c":"📋 Duplicate","exp_c":"📤 Export JSON","imp_c":"📥 Import JSON",
        "c_name":"Contest Name:","c_type":"Type:","sc_mode":"Scoring:",
        "cats":"Categories (one per line):","a_bands":"Allowed Bands:",
        "a_modes":"Allowed Modes:",
        "req_st_c":"Required Stations (one per line):",
        "sp_sc":"Special Scoring (CALL=PTS):",
        "ppq":"Points/QSO:","min_qso":"Min QSO:","use_serial":"Serial Numbers",
        "use_county":"County","county_list":"Counties (comma sep):","no_sel":"Not selected!",
        "del_c_conf":"Delete '{}'?","c_saved":"Saved!","c_del":"Deleted!",
        "c_exists":"ID exists!","c_default":"Protected!","c_id":"Contest ID:",
        "mults":"Multipliers:","band_pts":"Band Points (BAND=PTS):",
        "nr":"Nr.","pts":"Pt",
        "dup_warn":"⚠ Duplicate!","dup_msg":"{} on {} {}!\nQSO #{}\n\nAdd anyway?",
        "search_t":"Search","search_l":"Search:","results":"Results",
        "no_res":"No results.","undo":"↩ Undo","undo_ok":"Undone.",
        "undo_empty":"Nothing to undo.","rate":"QSO/h","timer":"⏱ Timer",
        "timer_t":"Contest Timer","timer_start":"▶ Start","timer_stop":"⏸ Stop",
        "timer_reset":"⏹ Reset","elapsed":"Elapsed:","remaining":"Remaining:",
        "dur_h":"Duration (hours):","band_sum":"Bands",
        "distance":"Dist","country":"Country","utc":"UTC","autosaved":"Saved",
        "sounds":"Sounds","en_sounds":"Enable sounds",
        "qso_pts":"QSO Points","mult_c":"Multipliers","new_mult":"✦ NEW MULT!",
        "op":"Operator:","power":"Power (W):","f_band":"Band:","f_mode":"Mode:",
        "all":"All","clear_log":"🗑 Clear log",
        "clear_conf":"Clear ENTIRE log?\nAuto-backup will be created!\nIRREVERSIBLE!",
        "wb":"Worked other QRG","imp_adif":"Import ADIF","imp_csv":"Import CSV",
        "imp_ok":"Imported {} QSOs!","imp_err":"Import error!",
        "qso_total":"Total QSO","unique":"Unique","countries":"Countries",
        "print_log":"🖨 Print",
        "verify":"Verify Log","verify_ok":"Log OK: {} QSOs, hash: {}",
        "score_f":"Score","worked_all":"Completion Status",
        "worked_x":"Worked: {}/{}","missing_x":"Missing: {}",
        "tools":"🛠 Tools","clear_c":"Clear current log",
        "save_cat":"💾 Save",
        "exp_edi":"EDI (.edi)","exp_print":"Print (.txt)",
        "hash_ok":"Hash MD5 OK","hash_err":"Hash error",
        "exp_cab2":"Cabrillo 2.0 (.log)",
        "email_l":"Email:","soapbox":"SOAPBOX:",
        "cab_name":"Cabrillo Name:","exch_fmt":"Exchange Format:",
        "soapbox_l":"Soapbox:","imp_cab":"Import Cabrillo",
        "preview":"👁 Preview","preview_t":"Export Preview",
        "exp_warn":"⚠ Warning!",
        "exp_warn_msg":"Log has issues:\n{}\n\nContinue export?",
        "switch_conf":"Switch contest?\nCurrent log will be saved.",
        "exch_sent_l":"Exchange SENT:","exch_rcvd_l":"Exchange RECEIVED:",
        "cab2_config":"Cabrillo 2.0 Configuration","cab2_export":"📤 Export",
    }
}

DEFAULT_CONTESTS = {
    "simplu": {
        "name_ro":"Log Simplu","name_en":"Simple Log","contest_type":"Simplu",
        "cabrillo_name":"Simple Log",
        "categories":["Individual"],"scoring_mode":"none","points_per_qso":1,
        "min_qso":0,"allowed_bands":list(BANDS_ALL),"allowed_modes":list(MODES_ALL),
        "required_stations":[],"special_scoring":{},"use_serial":False,
        "use_county":False,"county_list":[],"multiplier_type":"none",
        "band_points":{},"exchange_format":"none","is_default":True
    },
    "maraton": {
        "name_ro":"Maraton Ion Creangă","name_en":"Marathon Ion Creanga",
        "contest_type":"Maraton","cabrillo_name":"MARATON ION CREANGA",
        "categories":["A. Seniori YO","B. YL","C. Juniori YO","D. Club","E. DX","F. Receptori"],
        "scoring_mode":"maraton","points_per_qso":1,"min_qso":100,
        "allowed_bands":BANDS_HF+BANDS_VHF,"allowed_modes":list(MODES_ALL),
        "required_stations":[],"special_scoring":{},"use_serial":False,
        "use_county":True,"county_list":list(YO_COUNTIES),
        "multiplier_type":"county","band_points":{},
        "exchange_format":"none","is_default":False
    },
    "stafeta": {
        "name_ro":"Ștafetă","name_en":"Relay","contest_type":"Stafeta",
        "cabrillo_name":"STAFETA",
        "categories":["A. Senior","B. YL","C. Junior"],
        "scoring_mode":"per_qso","points_per_qso":2,"min_qso":50,
        "allowed_bands":BANDS_HF,"allowed_modes":["SSB","CW"],
        "required_stations":[],"special_scoring":{},"use_serial":True,
        "use_county":True,"county_list":list(YO_COUNTIES),
        "multiplier_type":"county","band_points":{},
        "exchange_format":"county","is_default":False
    },
    "yo-dx-hf": {
        "name_ro":"YO DX HF Contest","name_en":"YO DX HF Contest","contest_type":"DX",
        "cabrillo_name":"YO DX HF",
        "categories":["A. SO AB High","B. SO AB Low","C. SO SB"],
        "scoring_mode":"per_band","points_per_qso":1,"min_qso":0,
        "allowed_bands":["160m","80m","40m","20m","15m","10m"],
        "allowed_modes":["SSB","CW"],
        "required_stations":[],"special_scoring":{},"use_serial":True,
        "use_county":True,"county_list":list(YO_COUNTIES),
        "multiplier_type":"dxcc",
        "band_points":{"160m":4,"80m":3,"40m":2,"20m":1,"15m":1,"10m":2},
        "exchange_format":"serial","is_default":False
    },
    "yo-vhf": {
        "name_ro":"YO VHF Contest","name_en":"YO VHF Contest","contest_type":"VHF",
        "cabrillo_name":"YO VHF",
        "categories":["A. Fixed","B. Mobile","C. Portable"],
        "scoring_mode":"distance","points_per_qso":1,"min_qso":0,
        "allowed_bands":["6m","2m","70cm","23cm"],"allowed_modes":["SSB","CW","FM"],
        "required_stations":[],"special_scoring":{},"use_serial":True,
        "use_county":False,"county_list":[],
        "multiplier_type":"grid","band_points":{},
        "exchange_format":"grid","is_default":False
    },
    "field-day": {
        "name_ro":"Field Day","name_en":"Field Day","contest_type":"Field Day",
        "cabrillo_name":"FIELD DAY",
        "categories":["1A","2A","3A","1B","2B"],
        "scoring_mode":"per_qso","points_per_qso":2,"min_qso":0,
        "allowed_bands":list(BANDS_HF),"allowed_modes":list(MODES_ALL),
        "required_stations":[],"special_scoring":{},"use_serial":False,
        "use_county":False,"county_list":[],
        "multiplier_type":"none","band_points":{},
        "exchange_format":"none","is_default":False
    },
    "sprint": {
        "name_ro":"Sprint","name_en":"Sprint","contest_type":"Sprint",
        "cabrillo_name":"SPRINT",
        "categories":["A. Single Op","B. Multi Op"],
        "scoring_mode":"per_qso","points_per_qso":1,"min_qso":0,
        "allowed_bands":["40m","20m","15m","10m"],"allowed_modes":["SSB","CW"],
        "required_stations":[],"special_scoring":{},"use_serial":True,
        "use_county":False,"county_list":[],
        "multiplier_type":"none","band_points":{},
        "exchange_format":"serial","is_default":False
    },
}

DEFAULT_CFG = {
    "call":"YO8ACR","loc":"KN37","jud":"NT","addr":"",
    "cat":0,"fs":11,"contest":"simplu","county":"NT",
    "lang":"ro","manual_dt":False,"sounds":True,
    "op_name":"","power":"100","win_geo":"",
    "email":"","soapbox":"73 GL",
    "cab2_exch_sent":"none","cab2_exch_rcvd":"log"
}

TH = {
    "bg":"#0d1117","fg":"#e6edf3","accent":"#1f6feb",
    "entry_bg":"#161b22","header_bg":"#010409",
    "btn_bg":"#21262d","btn_fg":"#f0f6fc",
    "led_on":"#3fb950","led_off":"#f85149",
    "warn":"#d29922","ok":"#3fb950","err":"#f85149",
    "dup_bg":"#3d1a1a","mult_bg":"#1a3d1a","spec_bg":"#1a1a3d",
    "alt":"#0d1f2d","gold":"#ffd700","cyan":"#58a6ff"
}

class DM:
    @staticmethod
    def fp(fn): return os.path.join(get_data_dir(), fn)
    @staticmethod
    def save(fn, d):
        p=DM.fp(fn); t=p+".tmp"
        try:
            with open(t,"w",encoding="utf-8") as f: json.dump(d,f,indent=2,ensure_ascii=False)
            if os.path.exists(p): os.remove(p)
            os.rename(t,p); return True
        except:
            try: os.remove(t)
            except: pass
            return False
    @staticmethod
    def load(fn, default=None):
        p=DM.fp(fn)
        if not os.path.exists(p):
            if default is not None: DM.save(fn,default)
            return copy.deepcopy(default) if default is not None else {}
        try:
            with open(p,"r",encoding="utf-8") as f: return json.load(f)
        except: return copy.deepcopy(default) if default is not None else {}
    @staticmethod
    def log_fn(cid): return f"log_{re.sub(r'[^a-zA-Z0-9_-]','_',cid)}.json"
    @staticmethod
    def load_log(cid):
        data = DM.load(DM.log_fn(cid),[]); return data if isinstance(data,list) else []
    @staticmethod
    def save_log(cid, d): return DM.save(DM.log_fn(cid), d)
    @staticmethod
    def backup(cid, d):
        try:
            bd=os.path.join(get_data_dir(),"backups"); os.makedirs(bd,exist_ok=True)
            ts=datetime.datetime.now().strftime("%Y%m%d_%H%M%S"); sid=re.sub(r'[^a-zA-Z0-9_-]','_',cid)
            with open(os.path.join(bd,f"log_{sid}_{ts}.json"),"w",encoding="utf-8") as f: json.dump(d,f,indent=2,ensure_ascii=False)
            bks=sorted(Path(bd).glob(f"log_{sid}_*.json"))
            while len(bks)>50: bks[0].unlink(); bks.pop(0)
            return True
        except: return False

class L:
    _c = "ro"
    @classmethod
    def s(cls,lang):
        if lang in T: cls._c=lang
    @classmethod
    def g(cls): return cls._c
    @classmethod
    def t(cls,k): return T.get(cls._c,{}).get(k,k)

class Score:
    @staticmethod
    def qso(q,rules,cfg=None):
        if not rules: return 1
        sm=rules.get("scoring_mode","none")
        if sm=="none": return 0
        call=q.get("c","").upper(); sp=rules.get("special_scoring",{})
        if call in sp:
            try: return int(sp[call])
            except: pass
        if sm=="per_qso": return rules.get("points_per_qso",1)
        elif sm=="per_band": return int(rules.get("band_points",{}).get(q.get("b",""),rules.get("points_per_qso",1)))
        elif sm=="maraton": return int(rules.get("special_scoring",{}).get(call,rules.get("points_per_qso",1)))
        elif sm=="distance":
            n=q.get("n","").strip(); ml=(cfg or {}).get("loc","")
            if Loc.valid(n) and Loc.valid(ml): return max(1,int(Loc.dist(ml,n)))
        return rules.get("points_per_qso",1)

    @staticmethod
    def mults(data,rules):
        mt=rules.get("multiplier_type","none")
        if mt=="none": return 1,set()
        ms=set()
        for q in data:
            n=q.get("n","").upper().strip(); c=q.get("c","").upper(); b=q.get("b","")
            if mt=="county":
                for co in rules.get("county_list",[]):
                    if re.search(r'\b'+re.escape(co.upper())+r'\b',n): ms.add(co.upper()); break
            elif mt=="dxcc": ms.add(DXCC.prefix(c))
            elif mt=="band": ms.add(b)
            elif mt=="grid":
                if len(n)>=4 and Loc.valid(n[:4]): ms.add(n[:4].upper())
        return max(1,len(ms)),ms

    @staticmethod
    def total(data,rules,cfg=None):
        if not data or not rules or rules.get("scoring_mode","none")=="none": return 0,0,0
        qp=sum(Score.qso(q,rules,cfg) for q in data); mc,_=Score.mults(data,rules)
        return (qp,mc,qp*mc) if rules.get("multiplier_type","none")!="none" else (qp,mc,qp)

    @staticmethod
    def is_dup(data,call,band,mode,edit_idx=None):
        cu=call.upper()
        for i,q in enumerate(data):
            if edit_idx is not None and i==edit_idx: continue
            if q.get("c","").upper()==cu and q.get("b")==band and q.get("m")==mode: return True,i
        return False,-1

    @staticmethod
    def worked_other(data,call,band,mode):
        cu=call.upper()
        for q in data:
            if q.get("c","").upper()==cu and (q.get("b")!=band or q.get("m")!=mode): return True
        return False

    @staticmethod
    def is_new_mult(data,qso,rules):
        mt=rules.get("multiplier_type","none")
        if mt=="none": return False
        _,ex=Score.mults(data,rules); n=qso.get("n","").upper().strip(); c=qso.get("c","").upper(); nm=None
        if mt=="county":
            for co in rules.get("county_list",[]):
                if re.search(r'\b'+re.escape(co.upper())+r'\b',n): nm=co.upper(); break
        elif mt=="dxcc": nm=DXCC.prefix(c)
        elif mt=="band": nm=qso.get("b","")
        elif mt=="grid":
            if len(n)>=4 and Loc.valid(n[:4]): nm=n[:4].upper()
        return nm is not None and nm not in ex

    @staticmethod
    def validate(data,rules,cfg=None):
        if not data: return False,"Log gol / Empty log",0
        if not rules: return True,f"OK: {len(data)} QSO",len(data)
        msgs=[]
        mq=rules.get("min_qso",0)
        if mq>0 and len(data)<mq: msgs.append(f"⚠ Min {mq} QSO, aveți/you have {len(data)}")
        seen=set(); dc=0
        for q in data:
            k=(q.get("c","").upper(),q.get("b"),q.get("m"))
            if k in seen: dc+=1
            seen.add(k)
        if dc: msgs.append(f"⚠ {dc} duplicate(s)")
        req=rules.get("required_stations",[])
        if req:
            cl={q.get("c","").upper() for q in data}
            missing=[r for r in req if r.upper() not in cl]
            if missing: msgs.append(f"⚠ Lipsă/Missing: {', '.join(missing)}")
        ab=rules.get("allowed_bands",[]); am=rules.get("allowed_modes",[])
        if ab and sum(1 for q in data if q.get("b") not in ab): msgs.append(f"⚠ Benzi interzise")
        if am and sum(1 for q in data if q.get("m") not in am): msgs.append(f"⚠ Moduri interzise")
        if msgs: return False,"\n".join(msgs),0
        _,_,tot=Score.total(data,rules,cfg)
        return True,f"✓ OK! {len(data)} QSO — Scor: {tot}",tot

class Importer:
    @staticmethod
    def parse_adif(text):
        qsos=[]; eoh=text.upper().find("<EOH>")
        if eoh>=0: text=text[eoh+5:]
        for rec in re.split(r'<EOR>',text,flags=re.IGNORECASE):
            rec=rec.strip()
            if not rec: continue
            fields={}
            for m in re.finditer(r'<(\w+):(\d+)(?::[^>]*)?>(.{0,9999}?)',rec,re.IGNORECASE|re.DOTALL):
                fields[m.group(1).upper()]=m.group(3)[:int(m.group(2))]
            if "CALL" not in fields: continue
            q={"c":fields["CALL"].upper(),"b":fields.get("BAND","40m"),"m":fields.get("MODE","SSB"),
               "s":fields.get("RST_SENT","59"),"r":fields.get("RST_RCVD","59")}
            qd=fields.get("QSO_DATE","")
            q["d"]=f"{qd[:4]}-{qd[4:6]}-{qd[6:8]}" if len(qd)==8 else datetime.datetime.utcnow().strftime("%Y-%m-%d")
            qt=fields.get("TIME_ON",""); q["t"]=f"{qt[:2]}:{qt[2:4]}" if len(qt)>=4 else "00:00"
            fr=fields.get("FREQ","")
            if fr:
                try: fv=float(fr); q["f"]=str(int(round(fv*1000) if fv<1000 else fv))
                except: q["f"]=fr
            else: q["f"]=""
            q["n"]=fields.get("GRIDSQUARE",fields.get("COMMENT",""))
            q["ss"]=fields.get("STX",""); q["sr"]=fields.get("SRX","")
            qsos.append(q)
        return qsos

    @staticmethod
    def parse_csv(text):
        qsos=[]
        try:
            for row in csv.DictReader(io.StringIO(text)):
                call=(row.get("Call") or row.get("CALL") or row.get("call") or row.get("Callsign") or "").upper().strip()
                if not call: continue
                qsos.append({"c":call,"b":row.get("Band") or row.get("BAND") or "40m","m":row.get("Mode") or row.get("MODE") or "SSB",
                    "s":row.get("RST_Sent") or row.get("RST_S") or "59","r":row.get("RST_Rcvd") or row.get("RST_R") or "59",
                    "d":row.get("Date") or row.get("DATE") or datetime.datetime.utcnow().strftime("%Y-%m-%d"),
                    "t":row.get("Time") or row.get("TIME") or "00:00","f":row.get("Freq") or row.get("FREQ") or "",
                    "n":row.get("Note") or row.get("NOTE") or row.get("Comment") or "",
                    "ss":row.get("Nr_S") or row.get("SS") or "","sr":row.get("Nr_R") or row.get("SR") or ""})
        except: pass
        return qsos

    @staticmethod
    def parse_cabrillo(text):
        qsos=[]; version="3.0"
        for line in text.strip().splitlines():
            line=line.strip()
            if line.upper().startswith("START-OF-LOG:"): version=line.split(":",1)[1].strip() or "3.0"
            if not line.upper().startswith("QSO:"): continue
            parts=line[4:].strip()
            q=Importer._parse_cab2_qso(parts) if version.startswith("2") else Importer._parse_cab3_qso(parts)
            if q: qsos.append(q)
        return qsos

    @staticmethod
    def _parse_cab2_qso(parts):
        try:
            tk=parts.split()
            if len(tk)<8: return None
            call=tk[7] if len(tk)>7 else ""
            if not call or call=="--": return None
            d=tk[2]; d=d if "-" in d else f"{d[:4]}-{d[4:6]}-{d[6:8]}" if len(d)==8 else d
            t=f"{tk[3][:2]}:{tk[3][2:4]}" if len(tk[3])>=4 else tk[3]
            return {"c":call.upper(),"b":freq2band(tk[0]) or "40m","m":CAB2_MODE_REV.get(tk[1].upper(),"SSB"),
                    "s":tk[5] if len(tk)>5 else "59","r":tk[8] if len(tk)>8 else "59","d":d,"t":t,"f":tk[0],
                    "n":tk[9] if len(tk)>9 and tk[9]!="--" else "","ss":tk[6] if len(tk)>6 and tk[6]!="--" else "",
                    "sr":tk[9] if len(tk)>9 and tk[9]!="--" else ""}
        except: return None

    @staticmethod
    def _parse_cab3_qso(parts):
        try:
            tk=parts.split()
            if len(tk)<7: return None
            call=tk[7] if len(tk)>7 else ""
            if not call: return None
            d=tk[2]; d=f"{d[:4]}-{d[4:6]}-{d[6:8]}" if len(d)==8 and "-" not in d else d
            t=f"{tk[3][:2]}:{tk[3][2:4]}" if len(tk[3])>=4 else tk[3]
            return {"c":call.upper(),"b":freq2band(tk[0]) or "40m","m":tk[1].upper(),
                    "s":tk[5] if len(tk)>5 else "59","r":tk[8] if len(tk)>8 else "59","d":d,"t":t,"f":tk[0],
                    "n":tk[9] if len(tk)>9 else "","ss":tk[6] if len(tk)>6 else "","sr":tk[9] if len(tk)>9 else ""}
        except: return None

class ContestEditor(tk.Toplevel):
    def __init__(self, parent, cid=None, cdata=None, all_c=None):
        super().__init__(parent)
        self.result=None; self.cid=cid; self.new=cid is None; self.all_c=all_c or {}
        self.d=copy.deepcopy(cdata) if cdata else {"name_ro":"","name_en":"","contest_type":"Simplu","cabrillo_name":"","categories":["Individual"],"scoring_mode":"none","points_per_qso":1,"min_qso":0,"allowed_bands":list(BANDS_ALL),"allowed_modes":list(MODES_ALL),"required_stations":[],"special_scoring":{},"use_serial":False,"use_county":False,"county_list":[],"multiplier_type":"none","band_points":{},"exchange_format":"none","is_default":False}
        self.title(L.t("edit_c") if not self.new else L.t("add_c")); self.geometry("720x880"); self.configure(bg=TH["bg"]); self.transient(parent); self.grab_set(); self._build(); center_dialog(self,parent)

    def _build(self):
        outer=tk.Frame(self,bg=TH["bg"]); outer.pack(fill="both",expand=True)
        canvas=tk.Canvas(outer,bg=TH["bg"],highlightthickness=0); vsb=ttk.Scrollbar(outer,orient="vertical",command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set); vsb.pack(side="right",fill="y"); canvas.pack(side="left",fill="both",expand=True)
        self._inner=tk.Frame(canvas,bg=TH["bg"],padx=15,pady=10); win_id=canvas.create_window((0,0),window=self._inner,anchor="nw")
        self._inner.bind("<Configure>",lambda e:canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",lambda e:canvas.itemconfig(win_id,width=e.width))
        canvas.bind("<MouseWheel>",lambda e:canvas.yview_scroll(int(-1*(e.delta/120)),"units"))
        eo={"bg":TH["entry_bg"],"fg":TH["fg"],"font":("Consolas",11),"insertbackground":TH["fg"]}
        lo={"bg":TH["bg"],"fg":TH["fg"],"font":("Consolas",11)}; f=self._inner; r=0; self._e={}
        if self.new:
            tk.Label(f,text=L.t("c_id"),**lo).grid(row=r,column=0,sticky="w",pady=3)
            self._e["id"]=tk.Entry(f,width=30,**eo); self._e["id"].grid(row=r,column=1,sticky="w",pady=3); r+=1
        for k,lb in [("name_ro",L.t("c_name")+" (RO)"),("name_en",L.t("c_name")+" (EN)"),("cabrillo_name",L.t("cab_name"))]:
            tk.Label(f,text=lb,**lo).grid(row=r,column=0,sticky="w",pady=3)
            e=tk.Entry(f,width=40,**eo); e.insert(0,self.d.get(k,"")); e.grid(row=r,column=1,sticky="w",pady=3); self._e[k]=e; r+=1
        tk.Label(f,text=L.t("c_type"),**lo).grid(row=r,column=0,sticky="w",pady=3)
        self._tv=tk.StringVar(value=self.d.get("contest_type","Simplu")); ttk.Combobox(f,textvariable=self._tv,values=CONTEST_TYPES,state="readonly",width=18).grid(row=r,column=1,sticky="w",pady=3); r+=1
        tk.Label(f,text=L.t("sc_mode"),**lo).grid(row=r,column=0,sticky="w",pady=3)
        self._sv=tk.StringVar(value=self.d.get("scoring_mode","none")); ttk.Combobox(f,textvariable=self._sv,values=SCORING_MODES,state="readonly",width=18).grid(row=r,column=1,sticky="w",pady=3); r+=1
        tk.Label(f,text=L.t("exch_fmt"),**lo).grid(row=r,column=0,sticky="w",pady=3)
        self._efv=tk.StringVar(value=self.d.get("exchange_format","none")); ttk.Combobox(f,textvariable=self._efv,values=EXCHANGE_FORMATS,state="readonly",width=18).grid(row=r,column=1,sticky="w",pady=3); r+=1
        for k,lb in [("points_per_qso",L.t("ppq")),("min_qso",L.t("min_qso"))]:
            tk.Label(f,text=lb,**lo).grid(row=r,column=0,sticky="w",pady=3)
            e=tk.Entry(f,width=10,**eo); e.insert(0,str(self.d.get(k,0))); e.grid(row=r,column=1,sticky="w",pady=3); self._e[k]=e; r+=1
        tk.Label(f,text=L.t("mults"),**lo).grid(row=r,column=0,sticky="w",pady=3)
        self._mv=tk.StringVar(value=self.d.get("multiplier_type","none")); ttk.Combobox(f,textvariable=self._mv,values=["none","county","dxcc","band","grid"],state="readonly",width=18).grid(row=r,column=1,sticky="w",pady=3); r+=1
        self._serv=tk.BooleanVar(value=self.d.get("use_serial",False))
        tk.Checkbutton(f,text=L.t("use_serial"),variable=self._serv,bg=TH["bg"],fg=TH["fg"],selectcolor=TH["entry_bg"],activebackground=TH["bg"]).grid(row=r,column=0,columnspan=2,sticky="w",pady=3); r+=1
        self._couv=tk.BooleanVar(value=self.d.get("use_county",False))
        tk.Checkbutton(f,text=L.t("use_county"),variable=self._couv,bg=TH["bg"],fg=TH["fg"],selectcolor=TH["entry_bg"],activebackground=TH["bg"]).grid(row=r,column=0,columnspan=2,sticky="w",pady=3); r+=1
        tk.Label(f,text=L.t("cats"),**lo).grid(row=r,column=0,sticky="nw",pady=3)
        self._cats_t=tk.Text(f,width=38,height=4,**eo); self._cats_t.insert("1.0","\n".join(self.d.get("categories",[]))); self._cats_t.grid(row=r,column=1,sticky="w",pady=3); r+=1
        tk.Label(f,text=L.t("a_bands"),**lo).grid(row=r,column=0,sticky="nw",pady=3)
        bf=tk.Frame(f,bg=TH["bg"]); bf.grid(row=r,column=1,sticky="w",pady=3); ab_set=set(self.d.get("allowed_bands",BANDS_ALL)); self._band_vars={}
        for i,b in enumerate(BANDS_ALL):
            v=tk.BooleanVar(value=b in ab_set); self._band_vars[b]=v
            tk.Checkbutton(bf,text=b,variable=v,bg=TH["bg"],fg=TH["fg"],selectcolor=TH["entry_bg"],activebackground=TH["bg"],font=("Consolas",9)).grid(row=i//7,column=i%7,sticky="w")
        r+=1
        tk.Label(f,text=L.t("a_modes"),**lo).grid(row=r,column=0,sticky="nw",pady=3)
        mf=tk.Frame(f,bg=TH["bg"]); mf.grid(row=r,column=1,sticky="w",pady=3); am_set=set(self.d.get("allowed_modes",MODES_ALL)); self._mode_vars={}
        for i,m in enumerate(MODES_ALL):
            v=tk.BooleanVar(value=m in am_set); self._mode_vars[m]=v
            tk.Checkbutton(mf,text=m,variable=v,bg=TH["bg"],fg=TH["fg"],selectcolor=TH["entry_bg"],activebackground=TH["bg"],font=("Consolas",9)).grid(row=i//4,column=i%4,sticky="w")
        r+=1
        tk.Label(f,text=L.t("req_st_c"),**lo).grid(row=r,column=0,sticky="nw",pady=3)
        self._req_t=tk.Text(f,width=38,height=3,**eo); self._req_t.insert("1.0","\n".join(self.d.get("required_stations",[]))); self._req_t.grid(row=r,column=1,sticky="w",pady=3); r+=1
        tk.Label(f,text=L.t("sp_sc"),**lo).grid(row=r,column=0,sticky="nw",pady=3)
        self._sp_t=tk.Text(f,width=38,height=3,**eo); self._sp_t.insert("1.0","\n".join(f"{k}={v}" for k,v in self.d.get("special_scoring",{}).items())); self._sp_t.grid(row=r,column=1,sticky="w",pady=3); r+=1
        tk.Label(f,text=L.t("band_pts"),**lo).grid(row=r,column=0,sticky="nw",pady=3)
        self._bp_t=tk.Text(f,width=38,height=3,**eo); self._bp_t.insert("1.0","\n".join(f"{k}={v}" for k,v in self.d.get("band_points",{}).items())); self._bp_t.grid(row=r,column=1,sticky="w",pady=3); r+=1
        tk.Label(f,text=L.t("county_list"),**lo).grid(row=r,column=0,sticky="w",pady=3)
        self._cl_e=tk.Entry(f,width=50,**eo); self._cl_e.insert(0,",".join(self.d.get("county_list",[]))); self._cl_e.grid(row=r,column=1,sticky="w",pady=3); r+=1
        bf2=tk.Frame(f,bg=TH["bg"]); bf2.grid(row=r,column=0,columnspan=2,pady=18)
        tk.Button(bf2,text=L.t("save"),command=self._save,bg=TH["accent"],fg="white",font=("Consolas",12,"bold"),width=12).pack(side="left",padx=8)
        tk.Button(bf2,text=L.t("cancel"),command=self.destroy,bg=TH["btn_bg"],fg="white",font=("Consolas",12),width=12).pack(side="left",padx=8)

    @staticmethod
    def _parse_kv(text):
        result={}
        for line in text.strip().splitlines():
            if "=" in line: k,_,v=line.partition("="); k=k.strip().upper();
            if k: result[k]=v.strip()
        return result

    def _save(self):
        if self.new:
            cid=self._e["id"].get().strip().lower().replace(" ","-")
            if not cid: messagebox.showerror(L.t("error"),"ID invalid!"); return
            if cid in self.all_c: messagebox.showerror(L.t("error"),L.t("c_exists")); return
            self.cid=cid
        self.d["name_ro"]=self._e["name_ro"].get().strip(); self.d["name_en"]=self._e["name_en"].get().strip()
        self.d["cabrillo_name"]=self._e["cabrillo_name"].get().strip(); self.d["contest_type"]=self._tv.get()
        self.d["scoring_mode"]=self._sv.get(); self.d["exchange_format"]=self._efv.get()
        try: self.d["points_per_qso"]=int(self._e["points_per_qso"].get())
        except: self.d["points_per_qso"]=1
        try: self.d["min_qso"]=int(self._e["min_qso"].get())
        except: self.d["min_qso"]=0
        self.d["multiplier_type"]=self._mv.get(); self.d["use_serial"]=self._serv.get(); self.d["use_county"]=self._couv.get()
        cats=[c.strip() for c in self._cats_t.get("1.0","end").splitlines() if c.strip()]; self.d["categories"]=cats or ["Individual"]
        self.d["allowed_bands"]=[b for b,v in self._band_vars.items() if v.get()] or list(BANDS_ALL)
        self.d["allowed_modes"]=[m for m,v in self._mode_vars.items() if v.get()] or list(MODES_ALL)
        self.d["required_stations"]=[s.strip().upper() for s in self._req_t.get("1.0","end").splitlines() if s.strip()]
        self.d["special_scoring"]=self._parse_kv(self._sp_t.get("1.0","end"))
        raw=self._parse_kv(self._bp_t.get("1.0","end")); self.d["band_points"]={k:int(v) for k,v in raw.items() if v.isdigit()}
        cl=self._cl_e.get().strip(); self.d["county_list"]=[c.strip().upper() for c in cl.split(",") if c.strip()] if cl else []
        self.d["is_default"]=False; self.result=(self.cid,self.d); self.destroy()

class ContestMgr(tk.Toplevel):
    def __init__(self,parent,contests):
        super().__init__(parent); self.c=copy.deepcopy(contests); self.result=None
        self.title(L.t("contest_mgr")); self.geometry("750x500"); self.configure(bg=TH["bg"]); self.transient(parent); self.grab_set()
        self._build(); self._fill(); center_dialog(self,parent)
    def _build(self):
        tb=tk.Frame(self,bg=TH["header_bg"],pady=6); tb.pack(fill="x")
        for txt,cmd in [(L.t("add_c"),self._add),(L.t("edit_c"),self._edit),(L.t("dup_c"),self._dup),(L.t("del_c"),self._del),(L.t("exp_c"),self._export),(L.t("imp_c"),self._import)]:
            tk.Button(tb,text=txt,command=cmd,bg=TH["accent"],fg="white",font=("Consolas",10)).pack(side="left",padx=3)
        tf=tk.Frame(self,bg=TH["bg"]); tf.pack(fill="both",expand=True,padx=6,pady=3)
        cols=("id","name","type","sc","mult","minq")
        self.tree=ttk.Treeview(tf,columns=cols,show="headings",selectmode="browse")
        for c,h,w in zip(cols,["ID",L.t("c_name"),L.t("c_type"),L.t("sc_mode"),L.t("mults"),L.t("min_qso")],[110,200,90,90,70,60]):
            self.tree.heading(c,text=h); self.tree.column(c,width=w,anchor="center")
        sb=ttk.Scrollbar(tf,orient="vertical",command=self.tree.yview); self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left",fill="both",expand=True); sb.pack(side="right",fill="y"); self.tree.bind("<Double-1>",lambda e:self._edit())
        bt=tk.Frame(self,bg=TH["bg"],pady=6); bt.pack(fill="x")
        tk.Button(bt,text=L.t("save"),command=self._onsave,bg=TH["ok"],fg="white",font=("Consolas",12,"bold"),width=12).pack(side="left",padx=12)
        tk.Button(bt,text=L.t("cancel"),command=self.destroy,bg=TH["btn_bg"],fg="white",font=("Consolas",12),width=12).pack(side="right",padx=12)
    def _fill(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for cid,cd in self.c.items():
            self.tree.insert("","end",iid=cid,values=(cid,cd.get("name_"+L.g(),cd.get("name_ro",cid)),cd.get("contest_type","?"),cd.get("scoring_mode","none"),cd.get("multiplier_type","none"),cd.get("min_qso",0)))
    def _sel(self):
        s=self.tree.selection(); return s[0] if s else None
    def _add(self):
        d=ContestEditor(self,all_c=self.c); self.wait_window(d)
        if d.result: self.c[d.result[0]]=d.result[1]; self._fill()
    def _edit(self):
        cid=self._sel()
        if not cid: return
        d=ContestEditor(self,cid=cid,cdata=self.c[cid],all_c=self.c); self.wait_window(d)
        if d.result: self.c[cid]=d.result[1]; self._fill()
    def _dup(self):
        cid=self._sel()
        if not cid: return
        nc=cid+"-copy"; i=2
        while nc in self.c: nc=f"{cid}-copy{i}"; i+=1
        self.c[nc]=copy.deepcopy(self.c[cid]); self.c[nc]["is_default"]=False; self.c[nc]["name_ro"]+=" (copie)"; self.c[nc]["name_en"]+=" (copy)"; self._fill()
    def _del(self):
        cid=self._sel()
        if not cid: return
        if self.c.get(cid,{}).get("is_default"): return
        if messagebox.askyesno(L.t("confirm_del"),L.t("del_c_conf").format(cid)): del self.c[cid]; self._fill()
    def _export(self):
        fp=filedialog.asksaveasfilename(defaultextension=".json",filetypes=[("JSON","*.json")])
        if fp:
            try:
                with open(fp,"w",encoding="utf-8") as f: json.dump(self.c,f,indent=2,ensure_ascii=False)
                messagebox.showinfo(L.t("exp_ok"),f"→ {os.path.basename(fp)}")
            except Exception as e: messagebox.showerror(L.t("error"),str(e))
    def _import(self):
        fp=filedialog.askopenfilename(filetypes=[("JSON","*.json")])
        if fp:
            try:
                with open(fp,"r",encoding="utf-8") as f: imp=json.load(f)
                if isinstance(imp,dict):
                    for cid,cd in imp.items():
                        if cid not in self.c: self.c[cid]=cd
                    self._fill()
            except Exception as e: messagebox.showerror(L.t("error"),str(e))
    def _onsave(self): self.result=self.c; self.destroy()

class SearchDialog(tk.Toplevel):
    def __init__(self,parent,log_data):
        super().__init__(parent); self.log_data=log_data; self.title(L.t("search_t")); self.geometry("600x420"); self.configure(bg=TH["bg"]); self.transient(parent)
        eo={"bg":TH["entry_bg"],"fg":TH["fg"],"font":("Consolas",11),"insertbackground":TH["fg"]}
        tk.Label(self,text=L.t("search_l"),bg=TH["bg"],fg=TH["fg"],font=("Consolas",11)).pack(anchor="w",padx=10,pady=(10,0))
        self._sv=tk.StringVar(); e=tk.Entry(self,textvariable=self._sv,width=40,**eo); e.pack(padx=10,pady=4,anchor="w"); e.bind("<KeyRelease>",self._search); e.focus()
        self._lbl=tk.Label(self,text="",bg=TH["bg"],fg=TH["fg"],font=("Consolas",9)); self._lbl.pack(anchor="w",padx=10)
        tf=tk.Frame(self,bg=TH["bg"]); tf.pack(fill="both",expand=True,padx=10,pady=4)
        cols=("nr","call","band","mode","date","note")
        self.tree=ttk.Treeview(tf,columns=cols,show="headings",selectmode="browse")
        for c,h,w in zip(cols,[L.t("nr"),L.t("call"),L.t("band"),L.t("mode"),L.t("data"),L.t("note")],[40,110,55,55,85,180]):
            self.tree.heading(c,text=h); self.tree.column(c,width=w,anchor="center")
        sb=ttk.Scrollbar(tf,orient="vertical",command=self.tree.yview); self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left",fill="both",expand=True); sb.pack(side="right",fill="y")
        tk.Button(self,text=L.t("close"),command=self.destroy,bg=TH["btn_bg"],fg="white").pack(pady=8); center_dialog(self,parent)
    def _search(self,e=None):
        q=self._sv.get().upper().strip()
        for i in self.tree.get_children(): self.tree.delete(i)
        if not q: self._lbl.config(text=""); return
        results=[(len(self.log_data)-i,qso) for i,qso in enumerate(self.log_data) if q in qso.get("c","").upper() or q in qso.get("n","").upper()]
        self._lbl.config(text=f"{L.t('results')}: {len(results)}")
        for nr,qso in results: self.tree.insert("","end",values=(nr,qso.get("c"),qso.get("b"),qso.get("m"),qso.get("d"),qso.get("n")))

class TimerDialog(tk.Toplevel):
    def __init__(self,parent):
        super().__init__(parent); self.title(L.t("timer_t")); self.geometry("300x220"); self.configure(bg=TH["bg"]); self.transient(parent)
        self._running=False; self._end_time=None; self._duration=0; self._elapsed_start=None; self._elapsed_secs=0
        lo={"bg":TH["bg"],"fg":TH["fg"],"font":("Consolas",11)}; eo={"bg":TH["entry_bg"],"fg":TH["fg"],"font":("Consolas",11),"justify":"center","insertbackground":TH["fg"]}
        tk.Label(self,text=L.t("dur_h"),**lo).pack(pady=(15,0)); self._dur_e=tk.Entry(self,width=10,**eo); self._dur_e.insert(0,"4"); self._dur_e.pack(pady=4)
        self._time_lbl=tk.Label(self,text="00:00:00",bg=TH["bg"],fg=TH["gold"],font=("Consolas",28,"bold")); self._time_lbl.pack(pady=10)
        self._rem_lbl=tk.Label(self,text="",**lo); self._rem_lbl.pack()
        bf=tk.Frame(self,bg=TH["bg"]); bf.pack(pady=8)
        self._start_btn=tk.Button(bf,text=L.t("timer_start"),command=self._start,bg=TH["ok"],fg="white",font=("Consolas",11),width=8); self._start_btn.pack(side="left",padx=4)
        tk.Button(bf,text=L.t("timer_reset"),command=self._reset,bg=TH["warn"],fg="white",font=("Consolas",11),width=8).pack(side="left",padx=4)
        self._tick(); center_dialog(self,parent)
    def _start(self):
        if self._running: self._running=False; self._start_btn.config(text=L.t("timer_start"),bg=TH["ok"])
        else:
            try: self._duration=int(float(self._dur_e.get())*3600)
            except: self._duration=0
            self._running=True; self._elapsed_start=datetime.datetime.utcnow()
            if self._duration>0: self._end_time=self._elapsed_start+datetime.timedelta(seconds=self._duration)
            self._start_btn.config(text=L.t("timer_stop"),bg=TH["err"])
    def _reset(self):
        self._running=False; self._elapsed_secs=0; self._end_time=None; self._elapsed_start=None
        self._time_lbl.config(text="00:00:00",fg=TH["gold"]); self._rem_lbl.config(text=""); self._start_btn.config(text=L.t("timer_start"),bg=TH["ok"])
    def _tick(self):
        try:
            if not self.winfo_exists(): return
        except: return
        if self._running and self._elapsed_start:
            now=datetime.datetime.utcnow(); elapsed=int((now-self._elapsed_start).total_seconds())+self._elapsed_secs
            h,rem=divmod(elapsed,3600); m,s=divmod(rem,60)
            try:
                self._time_lbl.config(text=f"{h:02d}:{m:02d}:{s:02d}")
                if self._end_time:
                    remaining=int((self._end_time-now).total_seconds())
                    if remaining<=0: self._running=False; self._time_lbl.config(fg=TH["err"]); self._rem_lbl.config(text="⏰ TIME UP!",fg=TH["err"]); beep("error")
                    else:
                        rh,rr=divmod(remaining,3600); rm,rs=divmod(rr,60)
                        self._rem_lbl.config(text=f"{L.t('remaining')} {rh:02d}:{rm:02d}:{rs:02d}",fg=TH["warn"] if remaining<300 else TH["fg"])
            except: return
        try: self.after(1000,self._tick)
        except: pass

class StatsWindow(tk.Toplevel):
    def __init__(self,parent,log_data,rules,cfg):
        super().__init__(parent); self.title(L.t("stats")); self.geometry("560x520"); self.configure(bg=TH["bg"]); self.transient(parent); center_dialog(self,parent)
        txt=scrolledtext.ScrolledText(self,bg=TH["entry_bg"],fg=TH["fg"],font=("Consolas",10),wrap="word"); txt.pack(fill="both",expand=True,padx=10,pady=10)
        txt.tag_configure("h",foreground=TH["gold"],font=("Consolas",11,"bold")); txt.tag_configure("ok",foreground=TH["ok"]); txt.tag_configure("warn",foreground=TH["warn"])
        def w(t,tag=None): txt.insert("end",t,tag)
        nm=rules.get("name_"+L.g(),rules.get("name_ro","?")) if rules else "?"
        w(f"📊 {L.t('stats')} — {nm}\n\n","h"); w(f"Total QSO: {len(log_data)}\nUnice: {len({q.get('c','').upper() for q in log_data})}\n")
        if log_data:
            try:
                dts=sorted([datetime.datetime.strptime(q.get("d","")+" "+q.get("t",""),"%Y-%m-%d %H:%M") for q in log_data if q.get("d") and q.get("t")])
                if len(dts)>=2:
                    span_h=(dts[-1]-dts[0]).total_seconds()/3600
                    w(f"Duration: {span_h:.1f}h  Rate: {len(log_data)/span_h:.1f} QSO/h\n")
            except: pass
        w("\n─── Benzi ───\n","h")
        bc=Counter(q.get("b","?") for q in log_data)
        for b in BANDS_ALL:
            if b in bc: w(f"  {b:<6} QSO:{bc[b]:<5} Pts:{sum(Score.qso(q,rules,cfg) for q in log_data if q.get('b')==b)}\n")
        w("\n─── Scor ───\n","h")
        if rules and rules.get("scoring_mode","none")!="none":
            qp,mult,tot=Score.total(log_data,rules,cfg); w(f"  {qp}×{mult}={tot}\n","ok")
        else: w("  (no scoring)\n","warn")
        txt.config(state="disabled"); tk.Button(self,text=L.t("close"),command=self.destroy,bg=TH["btn_bg"],fg="white").pack(pady=6)

class Cab2ConfigDialog(tk.Toplevel):
    def __init__(self,parent,cfg):
        super().__init__(parent); self.result=None; self.cfg=cfg; self.title(L.t("cab2_config")); self.geometry("420x250"); self.configure(bg=TH["bg"]); self.transient(parent); self.grab_set()
        lo={"bg":TH["bg"],"fg":TH["fg"],"font":("Consolas",11)}; jud=cfg.get("county",cfg.get("jud","NT")); loc=cfg.get("loc","KN37")
        tk.Label(self,text=L.t("exch_sent_l"),**lo).pack(anchor="w",padx=15,pady=(15,0))
        sent_opts=EXCH_SENT_OPTIONS.get(L.g(),EXCH_SENT_OPTIONS["ro"]); self._sent_labels={}; self._sent_values=[]
        for k,lbl in sent_opts.items():
            display=lbl.format(jud=jud,loc=loc); self._sent_labels[display]=k; self._sent_values.append(display)
        saved=cfg.get("cab2_exch_sent","none"); default_sent=self._sent_values[-1]
        for d,k in self._sent_labels.items():
            if k==saved: default_sent=d; break
        self._sent_v=tk.StringVar(value=default_sent); ttk.Combobox(self,textvariable=self._sent_v,values=self._sent_values,state="readonly",width=30,font=("Consolas",11)).pack(padx=15,pady=4)
        tk.Label(self,text=L.t("exch_rcvd_l"),**lo).pack(anchor="w",padx=15,pady=(10,0))
        rcvd_opts=EXCH_RCVD_OPTIONS.get(L.g(),EXCH_RCVD_OPTIONS["ro"]); self._rcvd_labels={}; self._rcvd_values=[]
        for k,lbl in rcvd_opts.items(): self._rcvd_labels[lbl]=k; self._rcvd_values.append(lbl)
        saved_r=cfg.get("cab2_exch_rcvd","log"); default_rcvd=self._rcvd_values[0]
        for d,k in self._rcvd_labels.items():
            if k==saved_r: default_rcvd=d; break
        self._rcvd_v=tk.StringVar(value=default_rcvd); ttk.Combobox(self,textvariable=self._rcvd_v,values=self._rcvd_values,state="readonly",width=30,font=("Consolas",11)).pack(padx=15,pady=4)
        bf=tk.Frame(self,bg=TH["bg"]); bf.pack(pady=18)
        tk.Button(bf,text=L.t("cab2_export"),command=self._ok,bg=TH["ok"],fg="white",font=("Consolas",12,"bold"),width=14).pack(side="left",padx=8)
        tk.Button(bf,text=L.t("cancel"),command=self.destroy,bg=TH["btn_bg"],fg="white",font=("Consolas",12),width=10).pack(side="left",padx=8)
        center_dialog(self,parent)
    def _ok(self):
        self.result={"sent":self._sent_labels.get(self._sent_v.get(),"none"),"rcvd":self._rcvd_labels.get(self._rcvd_v.get(),"log")}; self.destroy()

class PreviewDialog(tk.Toplevel):
    def __init__(self,parent,title_str,content,save_callback):
        super().__init__(parent); self.title(title_str); self.geometry("750x550"); self.configure(bg=TH["bg"]); self.transient(parent)
        self._save_cb=save_callback; self._content=content
        txt=scrolledtext.ScrolledText(self,bg=TH["entry_bg"],fg=TH["fg"],font=("Consolas",10),wrap="none"); txt.pack(fill="both",expand=True,padx=10,pady=10)
        txt.insert("1.0",content); txt.config(state="disabled")
        bf=tk.Frame(self,bg=TH["bg"]); bf.pack(pady=8)
        tk.Button(bf,text=L.t("save"),command=self._on_save,bg=TH["ok"],fg="white",font=("Consolas",12,"bold"),width=12).pack(side="left",padx=8)
        tk.Button(bf,text=L.t("cancel"),command=self.destroy,bg=TH["btn_bg"],fg="white",font=("Consolas",12),width=12).pack(side="left",padx=8)
        center_dialog(self,parent)
    def _on_save(self): self._save_cb(self._content); self.destroy()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.cfg=DM.load("config.json",DEFAULT_CFG.copy())
        for k,v in DEFAULT_CFG.items():
            if k not in self.cfg: self.cfg[k]=v
        self.contests=DM.load("contests.json",DEFAULT_CONTESTS.copy())
        for k,v in DEFAULT_CONTESTS.items():
            if k not in self.contests: self.contests[k]=copy.deepcopy(v)
            else:
                for fk,fv in v.items():
                    if fk not in self.contests[k]: self.contests[k][fk]=fv
        if self.cfg.get("contest","") not in self.contests: self.cfg["contest"]="simplu"
        self.log=DM.load_log(self.cfg.get("contest","simplu"))
        if not isinstance(self.log,list): self.log=[]
        L.s(self.cfg.get("lang","ro")); self.edit_idx=None; self.ent={}; self.serial=len(self.log)+1; self.undo_stack=deque(maxlen=50)
        self.info_lbl=self.sc_lbl=self.clk=self.rate_lbl=None; self.led_c=self.led=self.st_lbl=self.wb_lbl=self.log_btn=None
        self.tree=self.ctx=self.fb_v=self.fm_v=None; self.cv=self.ccb=self.lang_v=self.man_v=self.cat_v=self.cou_v=None
        self._setup_win(); self._setup_style(); self._build_menu(); self._build_ui(); self._build_ctx(); self._refresh()
        self.protocol("WM_DELETE_WINDOW",self._exit)
        self.bind('<Return>',lambda e:self._add_qso()); self.bind('<Control-s>',lambda e:self._fsave())
        self.bind('<Control-z>',lambda e:self._undo()); self.bind('<Control-f>',lambda e:self._search_dlg())
        self.bind('<F2>',self._cycle_band); self.bind('<F3>',self._cycle_mode)
        self._tick_clock(); self._tick_save()

    def _cc(self): return self.contests.get(self.cfg.get("contest","simplu"),self.contests.get("simplu",{}))
    def _cid(self): return self.cfg.get("contest","simplu")
    def _sounds(self): return self.cfg.get("sounds",True) and HAS_SOUND

    def _setup_win(self):
        self.title(L.t("app_title")); self.configure(bg=TH["bg"])
        geo=self.cfg.get("win_geo","")
        try: self.geometry(geo if geo else "1220x760")
        except: self.geometry("1220x760")
        self.minsize(1000,640)

    def _setup_style(self):
        self.fs=int(self.cfg.get("fs",11)); self.fn=("Consolas",self.fs); self.fb=("Consolas",self.fs,"bold")
        s=ttk.Style()
        try: s.theme_use('clam')
        except: pass
        s.configure("Treeview",background=TH["entry_bg"],foreground=TH["fg"],fieldbackground=TH["entry_bg"],font=self.fn,rowheight=22)
        s.configure("Treeview.Heading",background=TH["header_bg"],foreground=TH["fg"],font=self.fb)
        s.map("Treeview",background=[("selected",TH["accent"])])

    def _build_menu(self):
        mb=tk.Menu(self); self.config(menu=mb)
        cm=tk.Menu(mb,tearoff=0); mb.add_cascade(label=L.t("contests"),menu=cm)
        cm.add_command(label=L.t("contest_mgr"),command=self._mgr); cm.add_separator()
        for cid,cd in self.contests.items():
            cm.add_command(label=f"⚡ {cd.get('name_'+L.g(),cd.get('name_ro',cid))}",command=lambda c=cid:self._switch_contest(c))
        tm=tk.Menu(mb,tearoff=0); mb.add_cascade(label=L.t("tools"),menu=tm)
        tm.add_command(label=L.t("search"),command=self._search_dlg); tm.add_command(label=L.t("timer"),command=self._timer_dlg); tm.add_separator()
        tm.add_command(label=L.t("imp_adif"),command=self._import_adif); tm.add_command(label=L.t("imp_csv"),command=self._import_csv)
        tm.add_command(label=L.t("imp_cab"),command=self._import_cabrillo); tm.add_separator()
        tm.add_command(label=L.t("print_log"),command=self._print_log); tm.add_command(label=L.t("verify"),command=self._verify_hash); tm.add_separator()
        tm.add_command(label=L.t("clear_log"),command=self._clear_log)
        hm=tk.Menu(mb,tearoff=0); mb.add_cascade(label=L.t("help"),menu=hm)
        hm.add_command(label=L.t("about"),command=self._about); hm.add_command(label="Exit",command=self._exit)

    def _build_ctx(self):
        self.ctx=Menu(self,tearoff=0); self.ctx.add_command(label=L.t("edit_qso"),command=self._edit_sel); self.ctx.add_command(label=L.t("delete_qso"),command=self._del_sel)

    def _build_ui(self): self._build_hdr(); self._build_inp(); self._build_flt(); self._build_tree(); self._build_btns()

    def _build_hdr(self):
        h=tk.Frame(self,bg=TH["header_bg"],pady=5); h.pack(fill="x")
        lf=tk.Frame(h,bg=TH["header_bg"]); lf.pack(side="left",padx=10)
        self.led_c=tk.Canvas(lf,width=14,height=14,bg=TH["header_bg"],highlightthickness=0)
        self.led=self.led_c.create_oval(1,1,13,13,fill=TH["led_on"],outline=""); self.led_c.pack(side="left",padx=(0,5))
        self.st_lbl=tk.Label(lf,text=L.t("online"),bg=TH["header_bg"],fg=TH["led_on"],font=self.fn); self.st_lbl.pack(side="left")
        self.info_lbl=tk.Label(lf,text="",bg=TH["header_bg"],fg=TH["fg"],font=self.fn); self.info_lbl.pack(side="left",padx=12)
        rf=tk.Frame(h,bg=TH["header_bg"]); rf.pack(side="right",padx=10)
        self.clk=tk.Label(rf,text="UTC 00:00:00",bg=TH["header_bg"],fg=TH["gold"],font=("Consolas",12,"bold")); self.clk.pack(side="right",padx=8)
        self.rate_lbl=tk.Label(rf,text="",bg=TH["header_bg"],fg=TH["ok"],font=("Consolas",10)); self.rate_lbl.pack(side="right",padx=8)
        self.lang_v=tk.StringVar(value=self.cfg.get("lang","ro"))
        lc=ttk.Combobox(rf,textvariable=self.lang_v,values=["ro","en"],state="readonly",width=4); lc.pack(side="right",padx=3); lc.bind("<<ComboboxSelected>>",self._on_lang)
        self.cv=tk.StringVar(value=self._cid())
        self.ccb=ttk.Combobox(rf,textvariable=self.cv,values=list(self.contests.keys()),state="readonly",width=15); self.ccb.pack(side="right",padx=3); self.ccb.bind("<<ComboboxSelected>>",self._on_cchange)
        self._upd_info()

    def _build_inp(self):
        ip=tk.Frame(self,bg=TH["bg"],pady=8); ip.pack(fill="x",padx=10); r1=tk.Frame(ip,bg=TH["bg"]); r1.pack(fill="x"); cc=self._cc()
        cf=tk.Frame(r1,bg=TH["bg"]); cf.pack(side="left",padx=3)
        tk.Label(cf,text=L.t("call"),bg=TH["bg"],fg=TH["fg"],font=self.fb).pack()
        self.ent["call"]=tk.Entry(cf,width=15,bg=TH["entry_bg"],fg=TH["gold"],font=("Consolas",self.fs+2,"bold"),insertbackground=TH["fg"],justify="center")
        self.ent["call"].pack(ipady=3); self.ent["call"].bind("<KeyRelease>",self._on_call_key)
        self.wb_lbl=tk.Label(cf,text="",bg=TH["bg"],fg=TH["err"],font=("Consolas",9)); self.wb_lbl.pack()
        ff=tk.Frame(r1,bg=TH["bg"]); ff.pack(side="left",padx=3)
        tk.Label(ff,text=L.t("freq"),bg=TH["bg"],fg=TH["fg"],font=self.fn).pack()
        self.ent["freq"]=tk.Entry(ff,width=9,bg=TH["entry_bg"],fg=TH["fg"],font=self.fn,insertbackground=TH["fg"],justify="center"); self.ent["freq"].pack()
        self.ent["freq"].bind("<FocusOut>",self._on_freq_out)
        ab=cc.get("allowed_bands",BANDS_ALL)
        bf2=tk.Frame(r1,bg=TH["bg"]); bf2.pack(side="left",padx=3)
        tk.Label(bf2,text=L.t("band"),bg=TH["bg"],fg=TH["fg"],font=self.fn).pack()
        self.ent["band"]=ttk.Combobox(bf2,values=ab,state="readonly",width=6,font=self.fn); self.ent["band"].set(ab[0] if ab else "40m"); self.ent["band"].pack()
        self.ent["band"].bind("<<ComboboxSelected>>",self._on_band_change)
        am=cc.get("allowed_modes",MODES_ALL)
        mf2=tk.Frame(r1,bg=TH["bg"]); mf2.pack(side="left",padx=3)
        tk.Label(mf2,text=L.t("mode"),bg=TH["bg"],fg=TH["fg"],font=self.fn).pack()
        self.ent["mode"]=ttk.Combobox(mf2,values=am,state="readonly",width=6,font=self.fn); self.ent["mode"].set(am[0] if am else "SSB"); self.ent["mode"].pack()
        self.ent["mode"].bind("<<ComboboxSelected>>",self._on_mode_change)
        drst=RST_DEFAULTS.get(am[0] if am else "SSB","59")
        for k,lb in [("rst_s",L.t("rst_s")),("rst_r",L.t("rst_r"))]:
            frame=tk.Frame(r1,bg=TH["bg"]); frame.pack(side="left",padx=3)
            tk.Label(frame,text=lb,bg=TH["bg"],fg=TH["fg"],font=self.fn).pack()
            e=tk.Entry(frame,width=5,bg=TH["entry_bg"],fg=TH["fg"],font=self.fn,insertbackground=TH["fg"],justify="center"); e.insert(0,drst); e.pack(); self.ent[k]=e
        if cc.get("use_serial"):
            for k,lb in [("ss",L.t("serial_s")),("sr",L.t("serial_r"))]:
                frame=tk.Frame(r1,bg=TH["bg"]); frame.pack(side="left",padx=3)
                tk.Label(frame,text=lb,bg=TH["bg"],fg=TH["fg"],font=self.fn).pack()
                e=tk.Entry(frame,width=5,bg=TH["entry_bg"],fg=TH["fg"],font=self.fn,insertbackground=TH["fg"],justify="center")
                if k=="ss": e.insert(0,str(self.serial))
                e.pack(); self.ent[k]=e
        nf=tk.Frame(r1,bg=TH["bg"]); nf.pack(side="left",padx=3)
        tk.Label(nf,text=L.t("note"),bg=TH["bg"],fg=TH["fg"],font=self.fn).pack()
        self.ent["note"]=tk.Entry(nf,width=13,bg=TH["entry_bg"],fg=TH["fg"],font=self.fn,insertbackground=TH["fg"],justify="center"); self.ent["note"].pack()
        rbf=tk.Frame(r1,bg=TH["bg"]); rbf.pack(side="left",padx=6)
        self.man_v=tk.BooleanVar(value=self.cfg.get("manual_dt",False))
        tk.Checkbutton(rbf,text=L.t("manual"),variable=self.man_v,bg=TH["bg"],fg=TH["fg"],selectcolor=TH["entry_bg"],activebackground=TH["bg"],command=self._tog_man).pack()
        self.log_btn=tk.Button(rbf,text=L.t("log"),command=self._add_qso,bg=TH["accent"],fg="white",font=self.fb,width=10); self.log_btn.pack(pady=1)
        tk.Button(rbf,text=L.t("reset"),command=self._full_clr,bg=TH["btn_bg"],fg=TH["btn_fg"],font=self.fn,width=10).pack(pady=1)
        r2=tk.Frame(ip,bg=TH["bg"]); r2.pack(fill="x",pady=(6,0))
        tk.Label(r2,text=L.t("date_l"),bg=TH["bg"],fg=TH["fg"],font=self.fn).pack(side="left",padx=3)
        self.ent["date"]=tk.Entry(r2,width=11,bg=TH["entry_bg"],fg=TH["fg"],font=self.fn,justify="center",state="disabled"); self.ent["date"].pack(side="left",padx=2)
        tk.Label(r2,text=L.t("time_l"),bg=TH["bg"],fg=TH["fg"],font=self.fn).pack(side="left",padx=3)
        self.ent["time"]=tk.Entry(r2,width=7,bg=TH["entry_bg"],fg=TH["fg"],font=self.fn,justify="center",state="disabled"); self.ent["time"].pack(side="left",padx=2)
        now=datetime.datetime.utcnow()
        for k,v in [("date",now.strftime("%Y-%m-%d")),("time",now.strftime("%H:%M"))]:
            self.ent[k].config(state="normal"); self.ent[k].insert(0,v)
            if not self.man_v.get(): self.ent[k].config(state="disabled")
        tk.Label(r2,text=L.t("category"),bg=TH["bg"],fg=TH["fg"],font=self.fn).pack(side="left",padx=(12,3))
        cats=cc.get("categories",["Individual"]) or ["Individual"]
        saved_cat=min(self.cfg.get("cat",0),max(0,len(cats)-1))
        self.cat_v=tk.StringVar(value=cats[saved_cat]); ttk.Combobox(r2,textvariable=self.cat_v,values=cats,state="readonly",width=20).pack(side="left",padx=2)
        if cc.get("use_county"):
            tk.Label(r2,text=L.t("county"),bg=TH["bg"],fg=TH["fg"],font=self.fn).pack(side="left",padx=(8,3))
            self.cou_v=tk.StringVar(value=self.cfg.get("county","NT"))
            ttk.Combobox(r2,textvariable=self.cou_v,values=cc.get("county_list",YO_COUNTIES),state="readonly",width=6).pack(side="left",padx=2)
        tk.Button(r2,text=L.t("save_cat"),command=self._save_cat,bg=TH["btn_bg"],fg="white",font=("Consolas",10)).pack(side="left",padx=8)

    def _build_flt(self):
        ff=tk.Frame(self,bg=TH["bg"]); ff.pack(fill="x",padx=10,pady=(1,0))
        tk.Label(ff,text=L.t("f_band"),bg=TH["bg"],fg=TH["fg"],font=("Consolas",10)).pack(side="left")
        self.fb_v=tk.StringVar(value=L.t("all"))
        fb=ttk.Combobox(ff,textvariable=self.fb_v,values=[L.t("all")]+self._cc().get("allowed_bands",BANDS_ALL),state="readonly",width=7); fb.pack(side="left",padx=3); fb.bind("<<ComboboxSelected>>",lambda e:self._refresh())
        tk.Label(ff,text=L.t("f_mode"),bg=TH["bg"],fg=TH["fg"],font=("Consolas",10)).pack(side="left",padx=(8,0))
        self.fm_v=tk.StringVar(value=L.t("all"))
        fm=ttk.Combobox(ff,textvariable=self.fm_v,values=[L.t("all")]+self._cc().get("allowed_modes",MODES_ALL),state="readonly",width=7); fm.pack(side="left",padx=3); fm.bind("<<ComboboxSelected>>",lambda e:self._refresh())
        self.sc_lbl=tk.Label(ff,text="",bg=TH["bg"],fg=TH["gold"],font=("Consolas",11,"bold")); self.sc_lbl.pack(side="right",padx=8)

    def _build_tree(self):
        tf=tk.Frame(self,bg=TH["bg"]); tf.pack(fill="both",expand=True,padx=10,pady=3)
        cc=self._cc(); us=cc.get("use_serial",False); hs=cc.get("scoring_mode","none")!="none"
        cols=["nr","call","freq","band","mode","rst_s","rst_r"]; hdrs=[L.t("nr"),L.t("call"),L.t("freq"),L.t("band"),L.t("mode"),L.t("rst_s"),L.t("rst_r")]; wids=[38,115,75,55,55,45,45]
        if us: cols+=["ss","sr"]; hdrs+=[L.t("serial_s"),L.t("serial_r")]; wids+=[45,45]
        cols+=["note","country","date","time"]; hdrs+=[L.t("note"),L.t("country"),L.t("data"),L.t("ora")]; wids+=[95,95,80,50]
        if hs: cols.append("pts"); hdrs.append(L.t("pts")); wids.append(50)
        self.tree=ttk.Treeview(tf,columns=cols,show="headings",selectmode="extended")
        for c,h,w in zip(cols,hdrs,wids):
            self.tree.heading(c,text=h,command=lambda col=c:self._sort_tree(col)); self.tree.column(c,width=w,anchor="center")
        self.tree.tag_configure("dup",background=TH["dup_bg"]); self.tree.tag_configure("alt",background=TH["alt"]); self.tree.tag_configure("spec",background=TH["spec_bg"])
        sb=ttk.Scrollbar(tf,orient="vertical",command=self.tree.yview); self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left",fill="both",expand=True); sb.pack(side="right",fill="y")
        self.tree.bind("<Double-1>",lambda e:self._edit_sel()); self.tree.bind("<Button-3>",self._on_rclick)
        self._sort_col=None; self._sort_rev=False

    def _sort_tree(self,col):
        if self._sort_col==col: self._sort_rev=not self._sort_rev
        else: self._sort_col=col; self._sort_rev=False
        items=[(self.tree.set(k,col),k) for k in self.tree.get_children("")]
        try: items.sort(key=lambda x:float(x[0]) if x[0].lstrip("-").isdigit() else x[0],reverse=self._sort_rev)
        except: items.sort(key=lambda x:x[0],reverse=self._sort_rev)
        for idx,(_,k) in enumerate(items): self.tree.move(k,"",idx)

    def _build_btns(self):
        bb=tk.Frame(self,bg=TH["bg"],pady=6); bb.pack(fill="x",padx=10)
        for txt,cmd,col in [(L.t("settings"),self._settings,TH["warn"]),(L.t("contests"),self._mgr,"#E91E63"),(L.t("stats"),self._stats,"#3F51B5"),(L.t("validate"),self._validate,TH["ok"]),(L.t("export"),self._export_dlg,"#9C27B0"),(L.t("import_log"),self._import_menu,"#FF5722"),(L.t("undo"),self._undo,"#795548"),(L.t("backup"),self._bak,"#607D8B"),(L.t("search"),self._search_dlg,"#00796B"),(L.t("timer"),self._timer_dlg,"#004D40")]:
            tk.Button(bb,text=txt,command=cmd,bg=col,fg="white",font=("Consolas",10),width=11).pack(side="left",padx=2)

    def _refresh(self):
        if not self.tree: return
        for i in self.tree.get_children(): self.tree.delete(i)
        cc=self._cc(); hs=cc.get("scoring_mode","none")!="none"; us=cc.get("use_serial",False)
        fb=self.fb_v.get() if self.fb_v else L.t("all"); fm=self.fm_v.get() if self.fm_v else L.t("all")
        sp_calls=set((cc.get("special_scoring") or {}).keys()); seen=set()
        for i,q in enumerate(self.log):
            b,m,c=q.get("b",""),q.get("m",""),q.get("c","").upper()
            if fb!=L.t("all") and b!=fb: continue
            if fm!=L.t("all") and m!=fm: continue
            nr=len(self.log)-i; key=(c,b,m)
            tag=("dup",) if key in seen else ("spec",) if c in sp_calls else ("alt",) if i%2==0 else ()
            seen.add(key); country,_=DXCC.lookup(c)
            vals=[nr,c,q.get("f",""),b,m,q.get("s","59"),q.get("r","59")]
            if us: vals+=[q.get("ss",""),q.get("sr","")]
            vals+=[q.get("n",""),country if country!="Unknown" else "",q.get("d",""),q.get("t","")]
            if hs: vals.append(Score.qso(q,cc,self.cfg))
            self.tree.insert("","end",iid=str(i),values=vals,tags=tag)
        self._upd_info()

    def _upd_info(self):
        cc=self._cc(); call=self.cfg.get("call","NOCALL"); nm=cc.get("name_"+L.g(),cc.get("name_ro","?"))
        cat=self.cat_v.get() if self.cat_v else ""
        if self.info_lbl: self.info_lbl.config(text=f"{call} | {nm} | {cat} | QSO: {len(self.log)}")
        if self.sc_lbl:
            qp,mc,tot=Score.total(self.log,cc,self.cfg)
            if cc.get("scoring_mode","none")!="none":
                self.sc_lbl.config(text=f"Σ {qp}×{mc}={tot}" if cc.get("multiplier_type","none")!="none" else f"Σ {tot}")
            else: self.sc_lbl.config(text="")
        if self.rate_lbl and len(self.log)>=2:
            try:
                dts=sorted([datetime.datetime.strptime(q.get("d","")+" "+q.get("t",""),"%Y-%m-%d %H:%M") for q in self.log[:20] if q.get("d") and q.get("t")])
                if len(dts)>=2:
                    span=(dts[-1]-dts[0]).total_seconds()/3600
                    if span>0: self.rate_lbl.config(text=f"⚡{len(dts)/span:.0f} {L.t('rate')}")
            except: pass

    def _get_dt(self):
        if self.man_v and self.man_v.get(): return self.ent["date"].get().strip(),self.ent["time"].get().strip()
        now=datetime.datetime.utcnow(); return now.strftime("%Y-%m-%d"),now.strftime("%H:%M")

    def _resolve_exchange_sent(self,q,mode="none"):
        if mode=="county": return self.cfg.get("county",self.cfg.get("jud","--"))
        elif mode=="grid": return self.cfg.get("loc","--")
        elif mode=="serial": return q.get("ss","") or "--"
        return "--"

    def _resolve_exchange_rcvd(self,q,mode="log"):
        if mode=="log": return q.get("sr","").strip() or q.get("n","").strip() or "--"
        return "--"

    def _add_qso(self):
        try: self._do_add_qso()
        except Exception as e:
            import traceback; messagebox.showerror(L.t("error"),f"Error:\n{e}\n{traceback.format_exc()[-300:]}")

    def _do_add_qso(self):
        call=self.ent["call"].get().upper().strip()
        if not call: return
        band=self.ent["band"].get(); mode=self.ent["mode"].get()
        if not band or not mode: return
        if not isinstance(self.log,list): self.log=[]
        if self.edit_idx is not None and self.edit_idx>=len(self.log):
            self.edit_idx=None
            if self.log_btn: self.log_btn.config(text=L.t("log"),bg=TH["accent"])
        dup,di=Score.is_dup(self.log,call,band,mode,self.edit_idx)
        if dup and self.edit_idx is None:
            if self._sounds(): beep("warning")
            if not messagebox.askyesno(L.t("dup_warn"),L.t("dup_msg").format(call,band,mode,len(self.log)-di)): return
        ds,ts=self._get_dt(); cc=self._cc()
        qp={"c":call,"b":band,"m":mode,"n":self.ent["note"].get().upper().strip()}
        if Score.is_new_mult(self.log,qp,cc) and self._sounds(): beep("info")
        q={"c":call,"b":band,"m":mode,"s":self.ent["rst_s"].get().strip() or "59","r":self.ent["rst_r"].get().strip() or "59",
           "n":self.ent["note"].get().strip(),"d":ds,"t":ts,"f":self.ent["freq"].get().strip()}
        if "ss" in self.ent: q["ss"]=self.ent["ss"].get().strip()
        if "sr" in self.ent: q["sr"]=self.ent["sr"].get().strip()
        if self.edit_idx is not None:
            self.log[self.edit_idx]=q; self.edit_idx=None
            if self.log_btn: self.log_btn.config(text=L.t("log"),bg=TH["accent"])
        else: self.log.insert(0,q); self.undo_stack.append(("add",0,q)); self.serial+=1
        self._clr(); self._refresh(); DM.save_log(self._cid(),self.log)

    # ── v16.5 FIX: Only clear call and note — keep freq, band, mode, RST ──
    def _clr(self):
        """Clear only call and note fields. Frequency, band, mode and RST persist."""
        self.ent["call"].delete(0, "end")
        self.ent["note"].delete(0, "end")
        # freq, band, mode, rst_s, rst_r — DO NOT CLEAR
        if "ss" in self.ent:
            self.ent["ss"].delete(0, "end")
            self.ent["ss"].insert(0, str(self.serial))
        if "sr" in self.ent:
            self.ent["sr"].delete(0, "end")
        if self.wb_lbl:
            self.wb_lbl.config(text="")
        self.ent["call"].focus()

    def _full_clr(self):
        """Full reset — clears ALL fields including freq, band, mode, RST."""
        self.ent["call"].delete(0, "end")
        self.ent["note"].delete(0, "end")
        self.ent["freq"].delete(0, "end")
        # Reset RST to defaults based on current mode
        mode = self.ent["mode"].get()
        rst = RST_DEFAULTS.get(mode, "59")
        for k in ("rst_s", "rst_r"):
            self.ent[k].delete(0, "end")
            self.ent[k].insert(0, rst)
        if "ss" in self.ent:
            self.ent["ss"].delete(0, "end")
            self.ent["ss"].insert(0, str(self.serial))
        if "sr" in self.ent:
            self.ent["sr"].delete(0, "end")
        if self.wb_lbl:
            self.wb_lbl.config(text="")
        self.ent["call"].focus()

    def _edit_sel(self):
        sel=self.tree.selection()
        if not sel: return
        try: idx=int(sel[0])
        except: return
        if idx<0 or idx>=len(self.log): return
        self.edit_idx=idx; q=self.log[idx]
        self.ent["call"].delete(0,"end"); self.ent["call"].insert(0,q.get("c",""))
        self.ent["freq"].delete(0,"end"); self.ent["freq"].insert(0,q.get("f",""))
        cc=self._cc()
        if q.get("b","") in cc.get("allowed_bands",BANDS_ALL): self.ent["band"].set(q["b"])
        if q.get("m","") in cc.get("allowed_modes",MODES_ALL): self.ent["mode"].set(q["m"])
        for k,fk in [("rst_s","s"),("rst_r","r"),("note","n")]:
            self.ent[k].delete(0,"end"); self.ent[k].insert(0,q.get(fk,""))
        for k in ["ss","sr"]:
            if k in self.ent: self.ent[k].delete(0,"end"); self.ent[k].insert(0,q.get(k,""))
        if self.log_btn: self.log_btn.config(text=L.t("update"),bg=TH["warn"])

    def _del_sel(self):
        sel=self.tree.selection()
        if sel and messagebox.askyesno(L.t("confirm_del"),L.t("confirm_del_t")):
            for idx in sorted([int(x) for x in sel],reverse=True):
                if 0<=idx<len(self.log): self.undo_stack.append(("del",idx,copy.deepcopy(self.log[idx]))); self.log.pop(idx)
            self._refresh(); DM.save_log(self._cid(),self.log)

    def _undo(self):
        if not self.undo_stack: messagebox.showinfo("",L.t("undo_empty")); return
        act,idx,q=self.undo_stack.pop()
        if act=="add" and 0<=idx<len(self.log): self.log.pop(idx)
        elif act=="del": self.log.insert(idx,q)
        self._refresh(); DM.save_log(self._cid(),self.log)

    def _on_call_key(self,e=None):
        c=self.ent["call"].get().upper(); pos=self.ent["call"].index(tk.INSERT)
        self.ent["call"].delete(0,tk.END); self.ent["call"].insert(0,c)
        try: self.ent["call"].icursor(min(pos,len(c)))
        except: pass
        if self.wb_lbl and len(c)>=3:
            dup,_=Score.is_dup(self.log,c,self.ent["band"].get(),self.ent["mode"].get(),self.edit_idx)
            if dup: self.wb_lbl.config(text="⚠ DUP",fg=TH["err"])
            elif Score.worked_other(self.log,c,self.ent["band"].get(),self.ent["mode"].get()): self.wb_lbl.config(text=f"ℹ {L.t('wb')}",fg=TH["warn"])
            else: self.wb_lbl.config(text="")
        elif self.wb_lbl: self.wb_lbl.config(text="")

    def _on_freq_out(self,e=None):
        f=self.ent["freq"].get().strip()
        if f:
            b=freq2band(f)
            if b and b in self._cc().get("allowed_bands",BANDS_ALL): self.ent["band"].set(b)

    def _on_band_change(self,e=None):
        if not self.ent["freq"].get().strip():
            self.ent["freq"].delete(0,"end"); self.ent["freq"].insert(0,str(BAND_FREQ.get(self.ent["band"].get(),"")))

    def _on_mode_change(self,e=None):
        rst=RST_DEFAULTS.get(self.ent["mode"].get(),"59")
        for k in ("rst_s","rst_r"): self.ent[k].delete(0,"end"); self.ent[k].insert(0,rst)

    def _on_rclick(self,e):
        item=self.tree.identify_row(e.y)
        if item: self.tree.selection_set(item); self.ctx.post(e.x_root,e.y_root)

    def _on_lang(self,e): L.s(self.lang_v.get()); self.cfg["lang"]=self.lang_v.get(); DM.save("config.json",self.cfg); self._rebuild()

    def _on_cchange(self,e):
        DM.save_log(self._cid(),self.log); self.cfg["contest"]=self.cv.get(); DM.save("config.json",self.cfg)
        self.log=DM.load_log(self._cid())
        if not isinstance(self.log,list): self.log=[]
        self.serial=len(self.log)+1; self._rebuild()

    def _cycle_band(self,e=None):
        ab=self._cc().get("allowed_bands",BANDS_ALL) or BANDS_ALL; cur=self.ent["band"].get()
        self.ent["band"].set(ab[(ab.index(cur)+1)%len(ab)] if cur in ab else ab[0]); self._on_band_change()

    def _cycle_mode(self,e=None):
        am=self._cc().get("allowed_modes",MODES_ALL) or MODES_ALL; cur=self.ent["mode"].get()
        self.ent["mode"].set(am[(am.index(cur)+1)%len(am)] if cur in am else am[0]); self._on_mode_change()

    def _tog_man(self):
        m=self.man_v.get()
        self.ent["date"].config(state="normal" if m else "disabled"); self.ent["time"].config(state="normal" if m else "disabled")
        if self.led_c: self.led_c.itemconfig(self.led,fill=TH["led_off"] if m else TH["led_on"])
        if self.st_lbl: self.st_lbl.config(text=L.t("offline") if m else L.t("online"),fg=TH["led_off"] if m else TH["led_on"])
        self.cfg["manual_dt"]=m

    def _save_cat(self):
        if self.cat_v:
            cats=self._cc().get("categories",[])
            self.cfg["cat"]=cats.index(self.cat_v.get()) if self.cat_v.get() in cats else 0
        if self.cou_v: self.cfg["county"]=self.cou_v.get()
        DM.save("config.json",self.cfg); self._upd_info()

    def _switch_contest(self,cid):
        DM.save_log(self._cid(),self.log); self.cfg["contest"]=cid; DM.save("config.json",self.cfg)
        self.log=DM.load_log(cid)
        if not isinstance(self.log,list): self.log=[]
        self.serial=len(self.log)+1; self._rebuild()

    def _rebuild(self):
        self.cfg["win_geo"]=self.geometry()
        for w in self.winfo_children(): w.destroy()
        self.ent={}; self.info_lbl=self.sc_lbl=self.clk=self.rate_lbl=None; self.led_c=self.led=self.st_lbl=self.wb_lbl=self.log_btn=None
        self.tree=self.ctx=self.fb_v=self.fm_v=None; self.cv=self.ccb=self.lang_v=self.man_v=self.cat_v=self.cou_v=None
        self._setup_style(); self._build_menu(); self._build_ui(); self._build_ctx(); self._refresh()

    def _tick_clock(self):
        try:
            if not self.winfo_exists(): return
            if self.clk: self.clk.config(text=f"UTC {datetime.datetime.utcnow().strftime('%H:%M:%S')}")
            self.after(1000,self._tick_clock)
        except: pass

    def _tick_save(self):
        try:
            if not self.winfo_exists(): return
            DM.save_log(self._cid(),self.log); self.after(60000,self._tick_save)
        except: pass

    def _fsave(self):
        DM.save_log(self._cid(),self.log); DM.save("config.json",self.cfg); DM.save("contests.json",self.contests)
        if self._sounds(): beep("success")

    def _mgr(self):
        d=ContestMgr(self,self.contests); self.wait_window(d)
        if d.result: self.contests=d.result; DM.save("contests.json",self.contests); self._rebuild()

    def _about(self):
        d=tk.Toplevel(self); d.title(L.t("about")); d.geometry("460x280"); d.configure(bg=TH["bg"]); d.transient(self)
        tk.Label(d,text="📻 YO Log PRO v16.5",bg=TH["bg"],fg=TH["accent"],font=("Consolas",16,"bold")).pack(pady=12)
        tk.Label(d,text=L.t("credits"),bg=TH["bg"],fg=TH["fg"],font=self.fn).pack(pady=8)
        tk.Label(d,text=L.t("usage"),bg=TH["bg"],fg=TH["fg"],font=("Consolas",9)).pack(pady=6)
        tk.Button(d,text=L.t("close"),command=d.destroy,bg=TH["accent"],fg="white",width=12).pack(pady=10); center_dialog(d,self)

    def _settings(self):
        d=tk.Toplevel(self); d.title(L.t("settings")); d.geometry("420x560"); d.configure(bg=TH["bg"]); d.transient(self)
        eo={"bg":TH["entry_bg"],"fg":TH["fg"],"font":self.fn,"insertbackground":TH["fg"]}
        fields=[("call",L.t("call"),self.cfg.get("call","")),("loc",L.t("locator"),self.cfg.get("loc","")),
                ("jud",L.t("county"),self.cfg.get("jud","")),("addr",L.t("address"),self.cfg.get("addr","")),
                ("op_name",L.t("op"),self.cfg.get("op_name","")),("power",L.t("power"),self.cfg.get("power","100")),
                ("email",L.t("email_l"),self.cfg.get("email","")),("soapbox",L.t("soapbox_l"),self.cfg.get("soapbox","73 GL")),
                ("fs",L.t("font_size"),str(self.cfg.get("fs",11)))]
        es={}
        for k,lb,v in fields:
            tk.Label(d,text=lb,bg=TH["bg"],fg=TH["fg"]).pack(anchor="w",padx=15)
            e=tk.Entry(d,width=35,**eo); e.insert(0,v); e.pack(pady=2,padx=15); es[k]=e
        snd_v=tk.BooleanVar(value=self.cfg.get("sounds",True))
        tk.Checkbutton(d,text=L.t("en_sounds"),variable=snd_v,bg=TH["bg"],fg=TH["fg"],selectcolor=TH["entry_bg"],activebackground=TH["bg"]).pack(anchor="w",padx=15,pady=4)
        def save():
            for k in es:
                v=es[k].get().strip(); self.cfg[k]=v.upper() if k in {"call","loc","jud"} else v
            try: self.cfg["fs"]=int(es["fs"].get().strip())
            except: self.cfg["fs"]=11
            self.cfg["sounds"]=snd_v.get(); DM.save("config.json",self.cfg); d.destroy(); self._rebuild()
        tk.Button(d,text=L.t("save"),command=save,bg=TH["accent"],fg="white",width=12).pack(pady=12); center_dialog(d,self)

    def _stats(self): StatsWindow(self,self.log,self._cc(),self.cfg)
    def _validate(self):
        ok,msg,_=Score.validate(self.log,self._cc(),self.cfg)
        (messagebox.showinfo if ok else messagebox.showwarning)(L.t("val_result"),msg)
    def _search_dlg(self): SearchDialog(self,self.log)
    def _timer_dlg(self): TimerDialog(self)
    def _verify_hash(self):
        try:
            h=hashlib.md5(json.dumps(self.log,ensure_ascii=False,sort_keys=True).encode("utf-8")).hexdigest()
            messagebox.showinfo(L.t("hash_ok"),L.t("verify_ok").format(len(self.log),h))
        except Exception as e: messagebox.showerror(L.t("error"),str(e))
    def _clear_log(self):
        if self.log and messagebox.askyesno(L.t("clear_log"),L.t("clear_conf")):
            DM.backup(self._cid(),self.log); self.log.clear(); self.serial=1; self.undo_stack.clear()
            self._refresh(); DM.save_log(self._cid(),self.log)

    def _import_menu(self):
        d=tk.Toplevel(self); d.title(L.t("import_log")); d.geometry("280x200"); d.configure(bg=TH["bg"]); d.transient(self)
        for txt,cmd in [("ADIF (.adi/.adif)",lambda:[d.destroy(),self._import_adif()]),("CSV (.csv)",lambda:[d.destroy(),self._import_csv()]),("Cabrillo (.log)",lambda:[d.destroy(),self._import_cabrillo()])]:
            tk.Button(d,text=txt,command=cmd,bg=TH["accent"],fg="white",width=24).pack(pady=6)
        center_dialog(d,self)

    def _import_adif(self):
        fp=filedialog.askopenfilename(filetypes=[("ADIF","*.adi *.adif"),("All","*.*")])
        if fp:
            try:
                with open(fp,"r",encoding="utf-8",errors="replace") as f: self._do_import(Importer.parse_adif(f.read()))
            except Exception as e: messagebox.showerror(L.t("error"),str(e))
    def _import_csv(self):
        fp=filedialog.askopenfilename(filetypes=[("CSV","*.csv"),("All","*.*")])
        if fp:
            try:
                with open(fp,"r",encoding="utf-8",errors="replace") as f: self._do_import(Importer.parse_csv(f.read()))
            except Exception as e: messagebox.showerror(L.t("error"),str(e))
    def _import_cabrillo(self):
        fp=filedialog.askopenfilename(filetypes=[("Cabrillo","*.log"),("All","*.*")])
        if fp:
            try:
                with open(fp,"r",encoding="utf-8",errors="replace") as f: self._do_import(Importer.parse_cabrillo(f.read()))
            except Exception as e: messagebox.showerror(L.t("error"),str(e))
    def _do_import(self,qsos):
        if qsos:
            if not isinstance(self.log,list): self.log=[]
            self.log.extend(qsos); self.serial=len(self.log)+1; self._refresh(); DM.save_log(self._cid(),self.log)
            messagebox.showinfo("OK",L.t("imp_ok").format(len(qsos)))
        else: messagebox.showwarning("","0 QSO")

    def _check_before_export(self):
        if not self.log: messagebox.showwarning(L.t("error"),"Log gol!"); return False
        ok,msg,_=Score.validate(self.log,self._cc(),self.cfg)
        if not ok:
            if not messagebox.askyesno(L.t("exp_warn"),L.t("exp_warn_msg").format(msg)): return False
        DM.backup(self._cid(),self.log); return True

    def _export_dlg(self):
        d=tk.Toplevel(self); d.title(L.t("export")); d.geometry("300x310"); d.configure(bg=TH["bg"]); d.transient(self)
        for txt,cmd in [("Cabrillo 3.0 (.log)",lambda:self._exp_cab(d)),(L.t("exp_cab2"),lambda:self._exp_cab2(d)),("ADIF 3.1 (.adi)",lambda:self._exp_adif(d)),("CSV (.csv)",lambda:self._exp_csv(d)),(L.t("exp_edi"),lambda:self._exp_edi(d)),(L.t("exp_print"),lambda:self._exp_print(d))]:
            tk.Button(d,text=txt,command=cmd,bg=TH["accent"],fg="white",width=28).pack(pady=4)
        center_dialog(d,self)

    def _exp_cab(self,parent=None):
        if not self._check_before_export(): return
        try:
            my=self.cfg.get("call","NOCALL"); cc=self._cc()
            nm=cc.get("cabrillo_name","") or cc.get("name_en",cc.get("name_ro","CONTEST"))
            pw=int(self.cfg.get("power","100")); cat_power="QRP" if pw<=5 else ("LOW" if pw<=100 else "HIGH")
            ef=cc.get("exchange_format","none")
            lines=["START-OF-LOG: 3.0",f"CONTEST: {nm}",f"CALLSIGN: {my}",f"GRID-LOCATOR: {self.cfg.get('loc','')}","CATEGORY-OPERATOR: SINGLE-OP","CATEGORY-BAND: ALL",f"CATEGORY-POWER: {cat_power}","CATEGORY-MODE: MIXED",f"NAME: {self.cfg.get('op_name','')}",f"ADDRESS: {self.cfg.get('addr','')}","SOAPBOX: Logged with YO Log PRO v16.5",f"SOAPBOX: {self.cfg.get('soapbox','73 GL')}","CREATED-BY: YO Log PRO v16.5"]
            for q in self.log:
                freq=q.get("f","") or str(BAND_FREQ.get(q.get("b",""),0))
                try: freq=str(int(float(freq)))
                except: pass
                es=self._resolve_exchange_sent(q,ef); er=self._resolve_exchange_rcvd(q,"log")
                date=q.get("d","").replace("-",""); time=q.get("t","").replace(":","")
                lines.append(f"QSO: {freq:>6} {q.get('m','SSB'):<5} {date} {time} {my:<13} {q.get('s','59'):<4} {es:<10} {q.get('c',''):<13} {q.get('r','59'):<4} {er}")
            lines.append("END-OF-LOG:"); content="\n".join(lines)
            def do_save(text):
                fp=filedialog.asksaveasfilename(defaultextension=".log",filetypes=[("Cabrillo","*.log")],initialfile=f"cab3_{self._cid()}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.log")
                if fp:
                    with open(fp,"w",encoding="utf-8") as f: f.write(text)
                    messagebox.showinfo(L.t("exp_ok"),f"→ {os.path.basename(fp)}")
            PreviewDialog(self,L.t("preview_t")+" — Cabrillo 3.0",content,do_save)
            if parent: parent.destroy()
        except Exception as e: messagebox.showerror(L.t("error"),str(e))

    def _exp_cab2(self,parent=None):
        if not self._check_before_export(): return
        cfg_dlg=Cab2ConfigDialog(self,self.cfg); self.wait_window(cfg_dlg)
        if not cfg_dlg.result: return
        exch_sent_mode=cfg_dlg.result["sent"]; exch_rcvd_mode=cfg_dlg.result["rcvd"]
        self.cfg["cab2_exch_sent"]=exch_sent_mode; self.cfg["cab2_exch_rcvd"]=exch_rcvd_mode; DM.save("config.json",self.cfg)
        try:
            my=self.cfg.get("call","NOCALL"); cc=self._cc()
            nm=(cc.get("cabrillo_name","") or cc.get("name_en",cc.get("name_ro","CONTEST"))).upper()
            cat_val=self.cat_v.get() if self.cat_v else ""; cat_num="1"
            if cat_val:
                m_cat=re.match(r'^([A-Za-z])',cat_val)
                if m_cat: cat_num=str(ord(m_cat.group(1).upper())-ord('A')+1)
                else:
                    cats=cc.get("categories",["Individual"])
                    cat_num=str(cats.index(cat_val)+1) if cat_val in cats else "1"
            _,_,tot=Score.total(self.log,cc,self.cfg)
            lines=["START-OF-LOG: 2.0","CREATED BY: YO Log PRO v16.5",f"CONTEST: {nm}",f"CALLSIGN: {my}",f"NAME: {self.cfg.get('op_name','')}",f"CATEGORY: {cat_num}",f"CLAIMED-SCORE: {tot}",f"ADDRESS: {self.cfg.get('addr','')}",f"EMAIL: {self.cfg.get('email','')}","SOAPBOX: Logged with YO Log PRO v16.5",f"SOAPBOX: {self.cfg.get('soapbox','73 GL')}","SOAPBOX:  mo  yyyy mm dd hhmm call         rs exc call          rs exc","SOAPBOX:  ** ********** **** ************* **  ** ************* **  **"]
            for q in self.log:
                freq=q.get("f","") or str(BAND_FREQ.get(q.get("b",""),0))
                try: freq=str(int(float(freq)))
                except: pass
                mode=CAB2_MODE_MAP.get(q.get("m","SSB"),"PH")
                date=q.get("d","")
                if len(date)==8 and "-" not in date: date=f"{date[:4]}-{date[4:6]}-{date[6:8]}"
                time_str=q.get("t","").replace(":","")[:4]
                es=self._resolve_exchange_sent(q,exch_sent_mode); er=self._resolve_exchange_rcvd(q,exch_rcvd_mode)
                lines.append(f"QSO: {freq} {mode} {date} {time_str} {my:<13} {q.get('s','59'):>2}  {es:<2} {q.get('c',''):<13} {q.get('r','59'):>2}  {er:<2}")
            lines.append("END-OF-LOG:"); content="\n".join(lines)
            def do_save(text):
                fp=filedialog.asksaveasfilename(defaultextension=".log",filetypes=[("Cabrillo","*.log")],initialfile=f"cab2_{self._cid()}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.log")
                if fp:
                    with open(fp,"w",encoding="utf-8") as f: f.write(text)
                    messagebox.showinfo(L.t("exp_ok"),f"→ {os.path.basename(fp)}")
            PreviewDialog(self,L.t("preview_t")+" — Cabrillo 2.0",content,do_save)
            if parent: parent.destroy()
        except Exception as e: messagebox.showerror(L.t("error"),str(e))

    def _exp_adif(self,parent=None):
        if not self._check_before_export(): return
        try:
            my_loc=self.cfg.get("loc","")
            lines=["<ADIF_VER:5>3.1.0","<PROGRAMID:14>YO_Log_PRO_v16","<PROGRAMVERSION:5>16.5",f"<MY_GRIDSQUARE:{len(my_loc)}>{my_loc}","<EOH>"]
            for q in self.log:
                dc=q.get("d","").replace("-",""); tc=q.get("t","").replace(":","")+"00"; note=q.get("n","")
                freq_mhz=""
                if q.get("f",""):
                    try: freq_mhz=f"{float(q['f'])/1000:.4f}"
                    except: pass
                def af(tag,val): return f"<{tag}:{len(str(val))}>{val}" if val else ""
                parts=[af("CALL",q.get("c","")),af("BAND",q.get("b","")),af("MODE",q.get("m","")),af("QSO_DATE",dc),af("TIME_ON",tc),af("RST_SENT",q.get("s","59")),af("RST_RCVD",q.get("r","59"))]
                if freq_mhz: parts.append(af("FREQ",freq_mhz))
                if Loc.valid(note[:6] if len(note)>=6 else note): parts.append(af("GRIDSQUARE",note))
                elif note: parts.append(af("COMMENT",note))
                if q.get("ss"): parts.append(af("STX",q["ss"]))
                if q.get("sr"): parts.append(af("SRX",q["sr"]))
                parts.append("<EOR>"); lines.append("".join(p for p in parts if p))
            fp=filedialog.asksaveasfilename(defaultextension=".adi",filetypes=[("ADIF","*.adi")],initialfile=f"adif_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.adi")
            if fp:
                with open(fp,"w",encoding="utf-8") as f: f.write("\n".join(lines))
                messagebox.showinfo(L.t("exp_ok"),f"→ {os.path.basename(fp)}")
            if parent: parent.destroy()
        except Exception as e: messagebox.showerror(L.t("error"),str(e))

    def _exp_csv(self,parent=None):
        if not self._check_before_export(): return
        try:
            fp=filedialog.asksaveasfilename(defaultextension=".csv",filetypes=[("CSV","*.csv")],initialfile=f"log_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv")
            if not fp: return
            cc=self._cc()
            with open(fp,"w",encoding="utf-8",newline='') as f:
                w=csv.writer(f); w.writerow(["Nr","Date","Time","Call","Freq","Band","Mode","RST_S","RST_R","Nr_S","Nr_R","Note","Country","Score"])
                for i,q in enumerate(self.log):
                    c,_=DXCC.lookup(q.get("c",""))
                    w.writerow([len(self.log)-i,q.get("d",""),q.get("t",""),q.get("c",""),q.get("f",""),q.get("b",""),q.get("m",""),q.get("s",""),q.get("r",""),q.get("ss",""),q.get("sr",""),q.get("n",""),c if c!="Unknown" else "",Score.qso(q,cc,self.cfg)])
            messagebox.showinfo(L.t("exp_ok"),f"→ {os.path.basename(fp)}")
            if parent: parent.destroy()
        except Exception as e: messagebox.showerror(L.t("error"),str(e))

    def _exp_edi(self,parent=None):
        if not self._check_before_export(): return
        try:
            my=self.cfg.get("call","NOCALL"); my_loc=self.cfg.get("loc",""); cc=self._cc()
            nm=cc.get("cabrillo_name","") or cc.get("name_en","VHF"); now=datetime.datetime.utcnow()
            lines=["[REG1TEST;1]",f"TName={nm}",f"TDate={now.strftime('%y%m%d')};{now.strftime('%y%m%d')}",f"PCall={my}",f"PWWLo={my_loc}","PExch=",f"PAdr1={self.cfg.get('addr','')}","PBand=144","PSect=","[Remarks]","Logged with YO Log PRO v16.5","[QSORecords]"]
            for q in self.log:
                dt=q.get("d","").replace("-","")[2:]; tm=q.get("t","").replace(":","")[:4]; loc=q.get("n","")
                km=int(Loc.dist(my_loc,loc)) if my_loc and Loc.valid(loc) else 0
                lines.append(f"{dt};{tm};{q.get('c','')};1;{q.get('s','59')};{q.get('ss','')};{q.get('r','59')};{q.get('sr','')};{loc};{km}")
            fp=filedialog.asksaveasfilename(defaultextension=".edi",filetypes=[("EDI","*.edi")],initialfile=f"edi_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.edi")
            if fp:
                with open(fp,"w",encoding="utf-8") as f: f.write("\n".join(lines))
                messagebox.showinfo(L.t("exp_ok"),f"→ {os.path.basename(fp)}")
            if parent: parent.destroy()
        except Exception as e: messagebox.showerror(L.t("error"),str(e))

    def _exp_print(self,parent=None):
        if not self._check_before_export(): return
        try:
            my=self.cfg.get("call","NOCALL"); cc=self._cc(); nm=cc.get("name_"+L.g(),cc.get("name_ro","?"))
            lines=[f"{'='*90}",f"YO Log PRO v16.5 — {my} — {nm}",f"Generated: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC",f"{'='*90}",
                   f"{'Nr':<4} {'Call':<13} {'Freq':<8} {'Band':<6} {'Mode':<6} {'RSTt':<5} {'RSTr':<5} {'Note':<10} {'Country':<15} {'Date':<11} {'Time':<6} {'Pts':<5}",f"{'-'*90}"]
            for i,q in enumerate(self.log):
                c,_=DXCC.lookup(q.get("c",""))
                lines.append(f"{len(self.log)-i:<4} {q.get('c',''):<13} {q.get('f',''):<8} {q.get('b',''):<6} {q.get('m',''):<6} {q.get('s',''):<5} {q.get('r',''):<5} {q.get('n',''):<10} {c[:14]:<15} {q.get('d',''):<11} {q.get('t',''):<6} {Score.qso(q,cc,self.cfg):<5}")
            lines.append(f"{'='*90}"); qp,mc,tot=Score.total(self.log,cc,self.cfg); lines.append(f"Total QSO: {len(self.log)}  |  Score: {qp}×{mc}={tot}")
            fp=filedialog.asksaveasfilename(defaultextension=".txt",filetypes=[("Text","*.txt")],initialfile=f"print_{self._cid()}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt")
            if fp:
                with open(fp,"w",encoding="utf-8") as f: f.write("\n".join(lines))
                messagebox.showinfo(L.t("exp_ok"),f"→ {os.path.basename(fp)}")
            if parent: parent.destroy()
        except Exception as e: messagebox.showerror(L.t("error"),str(e))

    def _print_log(self): self._exp_print()

    def _bak(self):
        if DM.backup(self._cid(),self.log): messagebox.showinfo("OK",L.t("bak_ok"))
        else: messagebox.showerror(L.t("error"),L.t("bak_err"))

    def _exit(self):
        if messagebox.askyesno(L.t("exit_t"),L.t("exit_m")):
            self.cfg["win_geo"]=self.geometry()
            DM.save_log(self._cid(),self.log); DM.save("config.json",self.cfg); DM.save("contests.json",self.contests)
            DM.backup(self._cid(),self.log); self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()
