#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YO Log PRO v9.0 - Professional Contest Logger
Author: YO8ACR Ardei Constantin-Cătălin
v9.0: N1MM-compatible, Stafeta, export multi-format, lookup online, arbitrare-ready

Caracteristici:
• Multi-contest: YO-DX-HF, Stafeta, Maraton Ion Creangă, Simple Log
• N1MM-like: multipliers, dupe check, serial auto, RST auto, scoring real-time
• Export: Cabrillo (all formats), ADIF 3.1.0+, CSV, compatible cu orice site
• Data integrity: atomic saves, backup rotation, corruption recovery
• UI: dark/light themes, scalable fonts, DPI aware, keyboard shortcuts
• Online lookup: QRZ, Radioamator.ro, Callbook, eQSL
• Maraton: categories A-F, special stations, /IC scoring, diploma check
• Stafeta: station categories A-E, category-based scoring
"""

import os, sys, json, re, datetime, shutil, tempfile, ctypes, threading, urllib.parse
from pathlib import Path
from collections import Counter, defaultdict
from tkinter import (
    Tk, Toplevel, Frame, Label, Entry, Button, Text, Scrollbar, Listbox,
    ttk, messagebox, filedialog, StringVar, BooleanVar, IntVar, Menu
)
import urllib.request
import urllib.error
import ssl

# ═══════════════════════════════════════════════════════════════
#  DPI AWARENESS - Windows 7/10/11 Compatibility
# ═══════════════════════════════════════════════════════════════
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)  # Windows 8.1+
except:
    try:
        ctypes.windll.user32.SetProcessDPIAware()    # Windows Vista/7
    except:
        pass  # Continue without DPI awareness

# ═══════════════════════════════════════════════════════════════
#  GLOBAL CONSTANTS
# ═══════════════════════════════════════════════════════════════

# Bands and modes
BANDS = ["160m","80m","60m","40m","30m","20m","17m","15m","12m","10m","6m","2m"]
MODES_CONTEST = ["SSB","CW","DIGI"]
MODES_FULL = ["SSB","CW","FT8","FT4","DIGI","PSK31","RTTY","AM","FM","JS8"]
MODES_DIGITAL = {"FT8","FT4","JS8","PSK31","RTTY","DIGI"}

# Validation
CALLSIGN_REGEX = re.compile(r"^[A-Z0-9/]{3,}$")
LOCATOR_REGEX = re.compile(r"^[A-R]{2}\d{2}[A-X]{2}$", re.I)
MAX_BACKUPS = 50

# Frequency tables (kHz / MHz / ranges)
BAND_FREQ_KHZ = {
    "160m":"1800","80m":"3500","60m":"5357","40m":"7000","30m":"10100",
    "20m":"14000","17m":"18068","15m":"21000","12m":"24890","10m":"28000",
    "6m":"50000","2m":"144000"
}
BAND_FREQ_MHZ = {
    "160m":1.8,"80m":3.5,"60m":5.357,"40m":7.0,"30m":10.1,
    "20m":14.0,"17m":18.068,"15m":21.0,"12m":24.89,"10m":28.0,
    "6m":50.0,"2m":144.0
}
BAND_RANGES = {
    "160m":(1.8,2.0),"80m":(3.5,3.8),"60m":(5.3,5.4),"40m":(7.0,7.2),
    "30m":(10.1,10.15),"20m":(14.0,14.35),"17m":(18.068,18.168),
    "15m":(21.0,21.45),"12m":(24.89,24.99),"10m":(28.0,29.7),
    "6m":(50.0,52.0),"2m":(144.0,146.0)
}

# ═══════════════════════════════════════════════════════════════
#  CONTEST DEFINITIONS (N1MM-style)
# ═══════════════════════════════════════════════════════════════

CONTEST_TYPES = {
    "yo-dx-hf": {
        "name": "YO-DX-HF",
        "exchange": "RST + Serial",
        "serial_required": True,
        "multipliers": ["dxcc_prefix"],
        "scoring": "1 point/QSO × multipliers",
        "cabrillo_template": "yo-dx"
    },
    "stafeta": {
        "name": "Cupa Moldovei - Stafeta",
        "exchange": "RST + Category (A/B/C/D/E)",
        "categories": {
            "A": "Stații fixe (club)",
            "B": "Stații mobile", 
            "C": "Stații portabile",
            "D": "Stații QRP (<5W)",
            "E": "Stații speciale"
        },
        "scoring": "Points vary by category",
        "cabrillo_template": "stafeta"
    },
    "maraton": {
        "name": "Maraton Ion Creangă",
        "exchange": "RST + Points",
        "categories": {
            "A": "Seniori YO (18+ ani)",
            "B": "YL (doamne/domnișoare)",
            "C": "Juniori YO (<18 ani)",
            "D": "Stații de club",
            "E": "Din afara țării",
            "F": "Receptori (SWL)"
        },
        "special_stations": {
            "YP8IC": {"points": 20, "mandatory": True},
            "YR8TGN": {"points": 20, "mandatory": True}
        },
        "ic_scoring": {
            "club_pattern": r"^YO8K[A-Z]{0,3}$",
            "club_points": 10,
            "individual_points": 5
        },
        "scoring": "20/10/5/1 points, 1 QSO/day/station limit",
        "cabrillo_template": "maraton"
    },
    "simple": {
        "name": "Log Simplu",
        "exchange": "Full QSO details",
        "scoring": "No scoring",
        "cabrillo_template": None
    }
}

# ═══════════════════════════════════════════════════════════════
#  COUNTIES (JUDEȚE) - Editable
# ═══════════════════════════════════════════════════════════════

DEFAULT_JUDETE = {
    "AB": "Alba", "AR": "Arad", "AG": "Argeș", "BC": "Bacău", "BH": "Bihor",
    "BN": "Bistrița-Năsăud", "BT": "Botoșani", "BV": "Brașov", "BR": "Brăila",
    "B": "București", "BZ": "Buzău", "CS": "Caraș-Severin", "CL": "Călărași",
    "CJ": "Cluj", "CT": "Constanța", "CV": "Covasna", "DB": "Dâmbovița",
    "DJ": "Dolj", "GL": "Galați", "GR": "Giurgiu", "GJ": "Gorj", "HR": "Harghita",
    "HD": "Hunedoara", "IL": "Ialomița", "IS": "Iași", "IF": "Ilfov",
    "MM": "Maramureș", "MH": "Mehedinți", "MS": "Mureș", "NT": "Neamț",
    "OT": "Olt", "PH": "Prahova", "SM": "Satu Mare", "SJ": "Sălaj",
    "SB": "Sibiu", "SV": "Suceava", "TR": "Teleorman", "TM": "Timiș",
    "TL": "Tulcea", "VS": "Vaslui", "VL": "Vâlcea", "VN": "Vrancea"
}

# ═══════════════════════════════════════════════════════════════
#  THEMES
# ═══════════════════════════════════════════════════════════════

THEMES = {
    "dark": {
        "bg_dark": "#1e1e1e", "bg_panel": "#2b2b2b", "bg_card": "#333333",
        "bg_header": "#0d1117", "fg_primary": "lime", "fg_secondary": "#58a6ff",
        "fg_accent": "#e0a85c", "fg_warning": "#e3b341", "fg_error": "#f85149",
        "fg_success": "#238636", "fg_muted": "#888", "accent_btn": "#1f6feb",
        "fg_text": "white", "bg_entry": "#333333", "fg_link": "#58a6ff"
    },
    "light": {
        "bg_dark": "#f0f0f0", "bg_panel": "#ffffff", "bg_card": "#e8e8e8",
        "bg_header": "#e0e0e0", "fg_primary": "#0066cc", "fg_secondary": "#0055aa",
        "fg_accent": "#cc6600", "fg_warning": "#cc9900", "fg_error": "#cc0000",
        "fg_success": "#009900", "fg_muted": "#666", "accent_btn": "#0066cc",
        "fg_text": "black", "bg_entry": "#ffffff", "fg_link": "#0066cc"
    }
}

# ═══════════════════════════════════════════════════════════════
#  FILE PATHS
# ═══════════════════════════════════════════════════════════════

FILES = {
    "config": "config.json",
    "contests": "contests.json",
    "judete": "judete.json",
    "log": "log.json",
    "backup_txt": "_Back_up.txt",
    "backup_dir": "backup",
    "archive_dir": "arhiva_concursuri"
}

# ═══════════════════════════════════════════════════════════════
#  UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def safe_save_json(filepath, data):
    """Atomic JSON save with temp file + rename (prevents corruption)."""
    try:
        dir_path = Path(filepath).parent
        dir_path.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode="w", dir=dir_path, delete=False, 
                                        suffix=".tmp", encoding="utf-8") as tmp:
            json.dump(data, tmp, indent=2, ensure_ascii=False)
            tmp_path = tmp.name
        os.replace(tmp_path, filepath)  # Atomic on Windows/Linux
        return True
    except Exception as e:
        print(f"❌ Save error: {e}")
        return False

def safe_load_json(filepath, default=None):
    """Load JSON with backup recovery on corruption."""
    if default is None:
        default = {}
    if not Path(filepath).exists():
        return default
    try:
        with open(filepath, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError, ValueError):
        # Try recovery from backup
        backup_dir = Path(filepath).parent / FILES["backup_dir"]
        if backup_dir.exists():
            backups = sorted(
                [f for f in backup_dir.glob("*.json")],
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            for bk in backups:
                try:
                    with open(bk, encoding="utf-8") as f:
                        data = json.load(f)
                    messagebox.showwarning(
                        "Recuperare",
                        f"{filepath.name} era corupt.\nRestaurat din: {bk.name}"
                    )
                    return data
                except:
                    continue
        messagebox.showerror(
            "Eroare critică",
            f"{filepath.name} este corupt și nu există backup valid.\nSe pornește cu date goale."
        )
        return default

def rotate_backups(folder, max_count=MAX_BACKUPS):
    """Delete oldest backups beyond limit."""
    folder = Path(folder)
    if not folder.exists():
        return
    backups = sorted(
        [f for f in folder.glob("*.json")],
        key=lambda x: x.stat().st_mtime
    )
    while len(backups) > max_count:
        try:
            backups.pop(0).unlink()
        except:
            pass

def clean_callsign(call):
    """Remove suffixes (/IC, /YL, /J) for unique identification."""
    return call.split('/')[0].upper().strip()

def get_suffixes(call):
    """Extract suffixes from callsign."""
    parts = call.upper().split('/')
    return [p for p in parts[1:] if p in ['IC', 'YL', 'J', 'P', 'M', 'AM']] if len(parts) > 1 else []

def format_cabrillo_time(t):
    """Format time as HHMM for Cabrillo."""
    return (t + "00")[:4]

def get_dxcc_prefix(call):
    """Extract DXCC prefix from callsign."""
    call = clean_callsign(call)
    # YO prefixes
    if call.startswith("YO"):
        if len(call) >= 4 and call[2].isdigit():
            return call[:3]  # YO1, YO2, etc.
        return "YO"
    # Generic: first 1-3 letters
    match = re.match(r"^([A-Z]{1,3})", call)
    return match.group(1) if match else call[:2]

# ═══════════════════════════════════════════════════════════════
#  ONLINE CALLSIGN LOOKUP - Multi-Source
# ═══════════════════════════════════════════════════════════════

class CallsignLookup:
    """Multi-source online callsign lookup with SSL handling."""
    
    _ssl_context = ssl.create_default_context()
    _ssl_context.check_hostname = False
    _ssl_context.verify_mode = ssl.CERT_NONE
    
    @staticmethod
    def _fetch_url(url, timeout=8):
        """Fetch URL with error handling."""
        try:
            headers = {'User-Agent': 'YO-Log-PRO/9.0 (Amateur Radio Logger)'}
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=CallsignLookup._ssl_context, timeout=timeout) as response:
                return response.read().decode('utf-8', errors='ignore')
        except urllib.error.HTTPError as e:
            return f"__HTTP_{e.code}__"
        except urllib.error.URLError as e:
            return f"__URL_{str(e.reason)}__"
        except Exception as e:
            return f"__ERR_{str(e)}__"
    
    @classmethod
    def lookup_qrz(cls, callsign):
        """Lookup on QRZ.com."""
        try:
            url = f"https://www.qrz.com/db/{callsign}"
            html = cls._fetch_url(url)
            if html.startswith("__"):
                return {"source": "QRZ.com", "callsign": callsign, "found": False, "error": html}
            
            info = {"source": "QRZ.com", "callsign": callsign, "found": True}
            
            # Extract name from title
            title_match = re.search(r'<title>([^<]+)</title>', html)
            if title_match:
                info['name'] = title_match.group(1).split('-')[0].strip()
            
            # Extract country
            country_match = re.search(r'Country:\s*<[^>]+>([^<]+)', html)
            if country_match:
                info['country'] = country_match.group(1).strip()
            
            # Extract grid
            grid_match = re.search(r'[Gg]rid\s*[Ss]quare[:\s]*[^>]*>([A-R]{2}\d{2}[a-x]{2})', html, re.I)
            if not grid_match:
                grid_match = re.search(r'[Gg]rid[:\s]*([A-R]{2}\d{2}[a-x]{2})', html)
            if grid_match:
                info['grid'] = grid_match.group(1).upper()
            
            return info
        except Exception as e:
            return {"source": "QRZ.com", "callsign": callsign, "found": False, "error": str(e)}
    
    @classmethod
    def lookup_radioamator_ro(cls, callsign):
        """Lookup on Radioamator.ro (YO database)."""
        try:
            url = f"https://www.radioamator.ro/callsign/{callsign}"
            html = cls._fetch_url(url)
            if html.startswith("__"):
                return {"source": "Radioamator.ro", "callsign": callsign, "found": False, "error": html}
            
            info = {"source": "Radioamator.ro", "callsign": callsign, "found": True}
            
            if "Nu am gasit" in html or "not found" in html.lower():
                info['found'] = False
                return info
            
            patterns = {
                'name': r'Nume:\s*</b>\s*([^<]+)',
                'locator': r'Locator:\s*</b>\s*([A-R]{2}\d{2}[a-x]{2})',
                'city': r'Oraș:\s*</b>\s*([^<]+)',
                'county': r'Județ:\s*</b>\s*([^<]+)',
                'qth': r'QTH:\s*</b>\s*([^<]+)'
            }
            for key, pattern in patterns.items():
                match = re.search(pattern, html)
                if match:
                    info[key] = match.group(1).strip()
            
            return info
        except Exception as e:
            return {"source": "Radioamator.ro", "callsign": callsign, "found": False, "error": str(e)}
    
    @classmethod
    def lookup_callbook(cls, callsign):
        """Lookup on Callbook.com (subscription required for full data)."""
        try:
            url = f"http://www.callbook.com/lookup.php?callsign={callsign}"
            html = cls._fetch_url(url)
            if html.startswith("__"):
                return {"source": "Callbook", "callsign": callsign, "found": False, "error": html}
            
            info = {"source": "Callbook", "callsign": callsign, "found": "not found" not in html.lower()}
            if info['found']:
                name_match = re.search(r'<b>Name:</b>\s*([^<]+)', html)
                if name_match:
                    info['name'] = name_match.group(1).strip()
            return info
        except Exception as e:
            return {"source": "Callbook", "callsign": callsign, "found": False, "error": str(e)}
    
    @classmethod
    def lookup_eqsl(cls, callsign):
        """Check eQSL.cc membership (limited public data)."""
        try:
            url = f"https://www.eqsl.cc/qslcard/MemberDetails.cfm?{callsign}"
            html = cls._fetch_url(url, timeout=5)
            if html.startswith("__"):
                return {"source": "eQSL.cc", "callsign": callsign, "found": False, "error": html}
            
            info = {"source": "eQSL.cc", "callsign": callsign, "found": True}
            if "Member not found" in html or "Invalid callsign" in html:
                info['found'] = False
            info['note'] = "eQSL nu expune date public. Verifică manual pe site."
            return info
        except Exception as e:
            return {"source": "eQSL.cc", "callsign": callsign, "found": False, "error": str(e)}
    
    @classmethod
    def lookup_all(cls, callsign, sources=None):
        """Lookup on all specified sources (parallel)."""
        if sources is None:
            sources = ['qrz', 'radioamator', 'callbook', 'eqsl']
        
        results = {}
        threads = {}
        source_funcs = {
            'qrz': cls.lookup_qrz,
            'radioamator': cls.lookup_radioamator_ro,
            'callbook': cls.lookup_callbook,
            'eqsl': cls.lookup_eqsl
        }
        
        def lookup_wrapper(key, func):
            try:
                results[key] = func(callsign)
            except Exception as e:
                results[key] = {"source": key, "callsign": callsign, "found": False, "error": str(e)}
        
        for key in sources:
            if key in source_funcs:
                t = threading.Thread(target=lookup_wrapper, args=(key, source_funcs[key]))
                t.start()
                threads[key] = t
        
        for t in threads.values():
            t.join(timeout=15)
        
        return results

# ═══════════════════════════════════════════════════════════════
#  SCORING ENGINE - Contest-specific rules
# ═══════════════════════════════════════════════════════════════

class ScoringEngine:
    """Contest scoring engine with multi-contest support."""
    
    @staticmethod
    def get_maraton_points(callsign: str) -> int:
        """Calculate Maraton Ion Creangă points."""
        call = callsign.upper().strip()
        base = clean_callsign(call)
        suffixes = get_suffixes(call)
        
        # Special mandatory stations: 20 points
        if base in CONTEST_TYPES["maraton"]["special_stations"]:
            return CONTEST_TYPES["maraton"]["special_stations"][base]["points"]
        
        # /IC suffix scoring
        if "IC" in suffixes:
            pattern = CONTEST_TYPES["maraton"]["ic_scoring"]["club_pattern"]
            if re.match(pattern, base):
                return CONTEST_TYPES["maraton"]["ic_scoring"]["club_points"]
            return CONTEST_TYPES["maraton"]["ic_scoring"]["individual_points"]
        
        return 0  # No points
    
    @staticmethod
    def get_stafeta_points(callsign: str, category: str) -> int:
        """Calculate Stafeta points by category."""
        # Example scoring - customize per contest rules
        points_by_cat = {"A": 3, "B": 2, "C": 2, "D": 5, "E": 10}
        return points_by_cat.get(category, 1)
    
    @staticmethod
    def calculate_maraton_total(log: list, my_call: str) -> dict:
        """Calculate full Maraton scoring with 1 QSO/day/station limit."""
        daily_points = {}  # {call_date: points}
        worked_special = set()
        
        for q in log:
            if q.get("contest") != "Maraton Ion Creangă":
                continue
            call = q["call"]
            date = q.get("date", "")
            key = f"{clean_callsign(call)}_{date}"
            
            # Track mandatory stations
            base = clean_callsign(call)
            if base in CONTEST_TYPES["maraton"]["special_stations"]:
                worked_special.add(base)
            
            # Only first QSO/day/station counts for points
            if key not in daily_points:
                points = ScoringEngine.get_maraton_points(call)
                if points > 0:
                    daily_points[key] = points
        
        total = sum(daily_points.values())
        eligible = len(log) >= 100 and len(CONTEST_TYPES["maraton"]["special_stations"]) == len(worked_special)
        
        return {
            "total_points": total,
            "total_qsos": len([q for q in log if q.get("contest") == "Maraton Ion Creangă"]),
            "eligible_for_diploma": eligible,
            "mandatory_worked": list(worked_special),
            "mandatory_missing": list(CONTEST_TYPES["maraton"]["special_stations"].keys() - worked_special)
        }

# ═══════════════════════════════════════════════════════════════
#  EXPORT ENGINE - Cabrillo/ADIF/CSV
# ═══════════════════════════════════════════════════════════════

class ExportEngine:
    """Multi-format export compatible with all arbitration sites."""
    
    @staticmethod
    def to_cabrillo(log: list, app_config: dict, contest_type: str) -> str:
        """Generate Cabrillo format log (YO-DX-HF, Stafeta, Maraton compatible)."""
        call = app_config.get("callsign", "CALLSIGN")
        contest_name = CONTEST_TYPES.get(contest_type, {}).get("name", contest_type)
        category = app_config.get("category", "SINGLE-OP")
        
        # Calculate claimed score
        if contest_type == "maraton":
            scoring = ScoringEngine.calculate_maraton_total(log, call)
            claimed_score = scoring["total_points"]
        else:
            claimed_score = len([q for q in log if q.get("contest") == contest_name])
        
        lines = [
            "START-OF-LOG: 3.0",
            f"CREATED-BY: YO Log PRO v9.0",
            f"CALLSIGN: {call}",
            f"CONTEST: {contest_name}",
            f"CATEGORY-OPERATOR: {category}",
            f"OPERATORS: {app_config.get('operator', call)}",
            f"CLAIMED-SCORE: {claimed_score}",
            f"LOCATION: {app_config.get('judet', 'RO')}",
            "SOAPBOX: Log generated with YO Log PRO v9.0 - https://github.com/YO8ACR/YO-Log-PRO",
        ]
        
        for q in log:
            if contest_type and q.get("contest") != contest_name:
                continue
            
            freq = BAND_FREQ_KHZ.get(q["band"], "14000")
            mode = "PH" if q["mode"] == "SSB" else ("CW" if q["mode"] == "CW" else "DG")
            date = q.get("date", "19700101").replace("-", "")
            time = format_cabrillo_time(q.get("time", "0000"))
            
            # Cabrillo QSO line format
            qso_line = (f"QSO: {freq:>5} {mode:<2} {date} {time} "
                       f"{call:<13} {q.get('rst_s', '59'):>3} {q.get('serial', '001'):>3}  "
                       f"{q['call']:<13} {q.get('rst_r', '59'):>3} {q.get('serial_r', '001'):>3}")
            lines.append(qso_line)
        
        lines.append("END-OF-LOG:")
        return "\n".join(lines)
    
    @staticmethod
    def to_adif(log: list, app_config: dict) -> str:
        """Generate ADIF 3.1.0+ format (eQSL/QRZ/ClubLog compatible)."""
        def tag(key, value):
            if value is None:
                return ""
            val_str = str(value).strip()
            return f"<{key}:{len(val_str)}>{val_str}"
        
        lines = [
            "<ADIF_VER:5>3.1.0",
            "<PROGRAMID:15>YO Log PRO v9.0",
            f"<CREATED_TIMESTAMP:15>{datetime.datetime.utcnow().strftime('%Y%m%d %H%M%S')}",
            "<EOH>"
        ]
        
        for q in log:
            parts = [
                tag("CALL", q["call"]),
                tag("QSO_DATE", q.get("date", "").replace("-", "")),
                tag("TIME_ON", (q.get("time", "0000") + "00")[:6]),
                tag("BAND", q["band"]),
                tag("FREQ", BAND_FREQ_MHZ.get(q["band"], 14.0)),
                tag("MODE", q["mode"] if q["mode"] in ["SSB","CW","AM","FM"] else "DIGI"),
                tag("RST_SENT", q.get("rst_s", "59")),
                tag("RST_RCVD", q.get("rst_r", "59")),
            ]
            
            # Optional fields
            if q.get("name"):
                parts.append(tag("NAME", q["name"]))
            if q.get("locator") and LOCATOR_REGEX.match(q["locator"]):
                parts.append(tag("GRIDSQUARE", q["locator"].upper()))
            if q.get("judet"):
                parts.append(tag("STATE", q["judet"]))  # Romanian counties as STATE
            if q.get("note"):
                parts.append(tag("COMMENT", q["note"]))
            if q.get("points"):
                parts.append(tag("POINTS", q["points"]))
            if q.get("contest"):
                parts.append(tag("CONTEST_ID", q["contest"].upper().replace(" ", "-")))
            if q.get("category"):
                parts.append(tag("CATEGORY", q["category"]))
            
            parts.append("<EOR>")
            lines.append(" ".join(parts))
        
        return "\n".join(lines)
    
    @staticmethod
    def to_csv(log: list) -> str:
        """Generate CSV for custom processing/spreadsheet import."""
        headers = ["Date", "Time", "Call", "Band", "Mode", "RST_S", "RST_R", 
                  "Name", "Locator", "County", "Points", "Contest", "Notes"]
        lines = [",".join(headers)]
        
        for q in log:
            row = [
                q.get("date", ""), q.get("time", ""), q["call"], q["band"], q["mode"],
                q.get("rst_s", "59"), q.get("rst_r", "59"),
                q.get("name", ""), q.get("locator", ""), q.get("judet", ""),
                str(q.get("points", "")), q.get("contest", ""), q.get("note", "")
            ]
            # Escape commas in fields
            row = [f'"{r}"' if "," in str(r) else str(r) for r in row]
            lines.append(",".join(row))
        
        return "\n".join(lines)

# ═══════════════════════════════════════════════════════════════
#  DIALOG: CALLSIGN LOOKUP (Multi-Source)
# ═══════════════════════════════════════════════════════════════

class LookupDialog(Toplevel):
    """Multi-source callsign lookup dialog with tabbed results."""
    
    SOURCES = [
        ('qrz', 'QRZ.com', '#58a6ff'),
        ('radioamator', 'Radioamator.ro', '#238636'),
        ('callbook', 'Callbook', '#a371f7'),
        ('eqsl', 'eQSL.cc', '#e3b341')
    ]
    
    def __init__(self, master, callsign="", theme="dark", font_size=10):
        super().__init__(master)
        self.title("🔍 Căutare Callsign Online")
        self.theme = THEMES.get(theme, THEMES["dark"])
        self.configure(bg=self.theme["bg_dark"])
        self.resizable(False, False)
        self.grab_set()
        
        self.font_size = font_size
        self.lookup = CallsignLookup()
        
        self._setup_geometry()
        self._build_ui()
        
        if callsign:
            self.e_call.insert(0, callsign)
            self._do_lookup()
    
    def _setup_geometry(self):
        w, h = 750, 550
        self.geometry(f"{w}x{h}")
        self.update_idletasks()
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
    
    def _build_ui(self):
        pad = {"padx": 10, "pady": 5}
        base_font = ("Consolas", self.font_size)
        title_font = ("Consolas", self.font_size + 2, "bold")
        
        # Title
        Label(self, text="🔍 Căutare Callsign Online",
              font=title_font, fg=self.theme["fg_primary"],
              bg=self.theme["bg_dark"]).pack(pady=10)
        
        # Input
        input_frame = Frame(self, bg=self.theme["bg_dark"])
        input_frame.pack(fill="x", padx=10, pady=5)
        
        Label(input_frame, text="Callsign:", fg=self.theme["fg_muted"],
              bg=self.theme["bg_dark"], font=base_font).pack(side="left", **pad)
        
        self.e_call = Entry(input_frame, font=("Consolas", self.font_size + 1), width=15,
                           bg=self.theme["bg_entry"], fg=self.theme["fg_text"],
                           insertbackground=self.theme["fg_text"])
        self.e_call.pack(side="left", **pad)
        
        Button(input_frame, text="🔍 Caută pe toate", command=self._do_lookup,
               bg=self.theme["accent_btn"], fg="white", font=base_font,
               relief="flat", padx=12).pack(side="left", padx=10)
        
        # Source buttons
        src_frame = Frame(self, bg=self.theme["bg_dark"])
        src_frame.pack(fill="x", padx=10, pady=2)
        
        self.src_btns = {}
        for key, label, color in self.SOURCES:
            btn = Button(src_frame, text=label,
                        command=lambda k=key: self._lookup_single(k),
                        bg=self.theme["bg_card"], fg=color, font=("Consolas", self.font_size - 1),
                        relief="flat", padx=8, pady=2)
            btn.pack(side="left", padx=3)
            self.src_btns[key] = btn
        
        Button(input_frame, text="✖ Închide", command=self.destroy,
               bg=self.theme["bg_card"], fg=self.theme["fg_muted"], font=base_font,
               relief="flat", padx=12).pack(side="right", **pad)
        
        # Results notebook
        tabs = Frame(self, bg=self.theme["bg_dark"])
        tabs.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.notebook = ttk.Notebook(tabs)
        self.notebook.pack(fill="both", expand=True)
        
        self.results = {}
        for key, label, color in self.SOURCES:
            f = Frame(self.notebook, bg=self.theme["bg_panel"])
            self.notebook.add(f, text=label)
            
            txt = Text(f, font=base_font, bg=self.theme["bg_entry"],
                      fg=self.theme["fg_text"], wrap="word", state="disabled")
            txt.pack(fill="both", expand=True, padx=5, pady=5)
            
            sb = Scrollbar(f, command=txt.yview)
            sb.pack(side="right", fill="y")
            txt.config(yscrollcommand=sb.set)
            
            self.results[key] = txt
        
        # Status
        self.status = Label(self, text="Gata", anchor="w",
                           fg=self.theme["fg_muted"], bg=self.theme["bg_dark"],
                           font=("Consolas", self.font_size - 1))
        self.status.pack(fill="x", padx=10, pady=2)
    
    def _do_lookup(self):
        call = self.e_call.get().upper().strip()
        if not call or not CALLSIGN_REGEX.match(call):
            messagebox.showerror("Eroare", "Callsign invalid!", parent=self)
            return
        
        self._clear()
        self.status.config(text=f"🔍 Căutare: {call}...")
        self.update()
        
        results = self.lookup.lookup_all(call)
        self._show_results(call, results)
        self.status.config(text="✓ Gata")
    
    def _lookup_single(self, source):
        call = self.e_call.get().upper().strip()
        if not call or not CALLSIGN_REGEX.match(call):
            messagebox.showerror("Eroare", "Callsign invalid!", parent=self)
            return
        
        src_name = dict(self.SOURCES).get(source, source)
        self.status.config(text=f"🔍 {src_name}: {call}...")
        self.update()
        
        func = getattr(self.lookup, f"lookup_{source}", None)
        if func:
            result = func(call)
            self._show_single(source, call, result)
        
        self.status.config(text="✓ Gata")
    
    def _clear(self):
        for txt in self.results.values():
            txt.config(state="normal")
            txt.delete("1.0", "end")
            txt.config(state="disabled")
    
    def _show_results(self, call, results):
        for key, txt in self.results.items():
            self._format(txt, call, results.get(key, {"found": False}))
    
    def _show_single(self, key, call, result):
        if key in self.results:
            self._format(self.results[key], call, result)
    
    def _format(self, txt, call, result):
        txt.config(state="normal")
        txt.delete("1.0", "end")
        
        src = result.get("source", "Unknown")
        txt.insert("end", f"📡 {src}\n", ("hdr",))
        txt.insert("end", "=" * 50 + "\n\n")
        
        if result.get("found"):
            txt.insert("end", f"✅ Găsit: {call}\n\n")
            for k in ['name', 'country', 'grid', 'locator', 'city', 'county', 'qth', 'note']:
                if k in result and result[k]:
                    txt.insert("end", f"  {k.title()}: {result[k]}\n")
        else:
            txt.insert("end", f"❌ Nu a fost găsit\n")
            if "error" in result:
                err = result["error"]
                if err.startswith("__HTTP_"):
                    txt.insert("end", f"  Eroare HTTP: {err.split('_')[2]}\n")
                elif err.startswith("__URL_"):
                    txt.insert("end", f"  Eroare conexiune: {err.split('_',1)[1]}\n")
                else:
                    txt.insert("end", f"  Eroare: {err}\n")
        
        txt.insert("end", "\n" + "-" * 50 + "\n")
        txt.see("end")
        txt.config(state="disabled")
        txt.tag_configure("hdr", font=("Consolas", self.font_size + 1, "bold"),
                         foreground=self.theme["fg_primary"])

# ═══════════════════════════════════════════════════════════════
#  DIALOG: COUNTY MANAGER (Editable)
# ═══════════════════════════════════════════════════════════════

class CountyManagerDialog(Toplevel):
    """Manage Romanian counties (add/edit/delete)."""
    
    def __init__(self, master, counties, on_save, theme="dark", font_size=10):
        super().__init__(master)
        self.title("🗺 Manager Județe")
        self.theme = THEMES.get(theme, THEMES["dark"])
        self.configure(bg=self.theme["bg_dark"])
        self.resizable(False, False)
        self.grab_set()
        
        self.counties = counties.copy() if counties else DEFAULT_JUDETE.copy()
        self.on_save = on_save
        self.font_size = font_size
        self.selected = None
        
        self._setup_geometry()
        self._build_ui()
    
    def _setup_geometry(self):
        w, h = 550, 600
        self.geometry(f"{w}x{h}")
        self.update_idletasks()
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
    
    def _build_ui(self):
        pad = {"padx": 14, "pady": 8}
        base_font = ("Consolas", self.font_size)
        title_font = ("Consolas", self.font_size + 2, "bold")
        
        Label(self, text="🗺 Manager Județe România",
              font=title_font, fg=self.theme["fg_primary"],
              bg=self.theme["bg_dark"]).pack(pady=14)
        
        Label(self, text="⭐ Județe care acordă puncte: NT (Neamț), IS (Iași)",
              fg=self.theme["fg_accent"], bg=self.theme["bg_dark"],
              font=base_font).pack(pady=5)
        
        # List
        lst_frame = Frame(self, bg=self.theme["bg_panel"])
        lst_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.lst = Listbox(lst_frame, font=base_font,
                          bg=self.theme["bg_card"], fg=self.theme["fg_text"],
                          height=20, selectbackground=self.theme["accent_btn"])
        self.lst.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        self.lst.bind("<<ListboxSelect>>", self._on_select)
        
        sb = Scrollbar(lst_frame, command=self.lst.yview)
        sb.pack(side="right", fill="y")
        self.lst.config(yscrollcommand=sb.set)
        
        self._refresh()
        
        # Form
        frm = Frame(self, bg=self.theme["bg_dark"])
        frm.pack(fill="x", padx=10, pady=5)
        
        Label(frm, text="Cod:", fg=self.theme["fg_muted"],
              bg=self.theme["bg_dark"], font=base_font).grid(row=0, column=0, sticky="e", **pad)
        self.e_code = Entry(frm, font=base_font, width=10,
                           bg=self.theme["bg_entry"], fg=self.theme["fg_text"])
        self.e_code.grid(row=0, column=1, sticky="w", **pad)
        
        Label(frm, text="Nume:", fg=self.theme["fg_muted"],
              bg=self.theme["bg_dark"], font=base_font).grid(row=0, column=2, sticky="e", **pad)
        self.e_name = Entry(frm, font=base_font, width=25,
                           bg=self.theme["bg_entry"], fg=self.theme["fg_text"])
        self.e_name.grid(row=0, column=3, sticky="w", **pad)
        
        # Buttons
        btn_frame = Frame(self, bg=self.theme["bg_dark"])
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        Button(btn_frame, text="➕ Adaugă", command=self._add,
               bg=self.theme["fg_success"], fg="white", font=base_font,
               relief="flat", padx=12).pack(side="left", padx=3)
        Button(btn_frame, text="✏️ Editează", command=self._edit,
               bg=self.theme["accent_btn"], fg="white", font=base_font,
               relief="flat", padx=12).pack(side="left", padx=3)
        Button(btn_frame, text="🗑 Șterge", command=self._delete,
               bg=self.theme["fg_error"], fg="white", font=base_font,
               relief="flat", padx=12).pack(side="left", padx=3)
        Button(btn_frame, text="💾 Salvează", command=self._save,
               bg=self.theme["bg_panel"], fg=self.theme["fg_primary"],
               font=base_font, relief="flat", padx=12).pack(side="right", padx=3)
        Button(btn_frame, text="✖ Închide", command=self.destroy,
               bg=self.theme["bg_card"], fg=self.theme["fg_muted"],
               font=base_font, relief="flat", padx=12).pack(side="right", padx=3)
        
        self._clear()
    
    def _refresh(self):
        self.lst.delete(0, "end")
        for code in sorted(self.counties.keys()):
            name = self.counties[code]
            mark = " ⭐" if code in ["NT", "IS"] else ""
            self.lst.insert("end", f"{code} - {name}{mark}")
    
    def _on_select(self, event=None):
        sel = self.lst.curselection()
        if not sel:
            self._clear()
            return
        code = self.lst.get(sel[0]).split(" - ")[0]
        self.selected = code
        self.e_code.delete(0, "end")
        self.e_code.insert(0, code)
        self.e_name.delete(0, "end")
        self.e_name.insert(0, self.counties.get(code, ""))
    
    def _clear(self):
        self.e_code.delete(0, "end")
        self.e_name.delete(0, "end")
        self.selected = None
    
    def _add(self):
        self._clear()
        self.e_code.focus_set()
    
    def _edit(self):
        code = self.e_code.get().upper().strip()
        name = self.e_name.get().strip()
        if not code or len(code) != 2:
            messagebox.showerror("Eroare", "Codul trebuie să aibă 2 litere!", parent=self)
            return
        if not name:
            messagebox.showerror("Eroare", "Numele este obligatoriu!", parent=self)
            return
        if self.selected and self.selected != code:
            del self.counties[self.selected]
        self.counties[code] = name
        self._refresh()
        messagebox.showinfo("Succes", f"Județul {code} salvat!", parent=self)
    
    def _delete(self):
        sel = self.lst.curselection()
        if not sel:
            messagebox.showwarning("Atenție", "Selectează un județ!", parent=self)
            return
        code = self.lst.get(sel[0]).split(" - ")[0]
        if code in ["NT", "IS"]:
            messagebox.showwarning("Atenție", f"{code} acordă puncte! Sigur ștergi?", parent=self)
        if messagebox.askyesno("Confirmare", f"Ștergi {code}?", parent=self):
            del self.counties[code]
            self._refresh()
            self._clear()
    
    def _save(self):
        self.on_save(self.counties)
        messagebox.showinfo("Succes", f"{len(self.counties)} județe salvate!", parent=self)

# ═══════════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════

class App(Tk):
    MODE_CONTEST = "contest"
    MODE_SIMPLE = "simple"
    
    def __init__(self):
        super().__init__()
        self.title("YO Log PRO v9.0 - Professional Logger")
        self.geometry("1400x900")
        self.minsize(1200, 750)
        
        self._init_data()
        self._apply_theme()
        self._build_ui()
        self._update_title()
        self._refresh_log()
        
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.bind("<Control-s>", lambda e: self._save())
        self.bind("<Control-l>", lambda e: self._open_lookup())
        self.bind("<F1>", lambda e: self._show_help())
    
    def _init_data(self):
        self.app_config = safe_load_json(FILES["config"], {})
        self.contests = safe_load_json(FILES["contests"], {})
        self.counties = safe_load_json(FILES["judete"], DEFAULT_JUDETE)
        self.log = safe_load_json(FILES["log"], [])
        
        self.active_contest = self.app_config.get("active_contest", "")
        self.app_mode = StringVar(value=self.MODE_SIMPLE)
        self.online_mode = self.app_config.get("online_mode", True)
        self.offline_date = datetime.datetime.utcnow().strftime("%Y-%m-%d")
        
        self.theme_name = self.app_config.get("theme", "dark")
        self.font_size = self.app_config.get("font_size", 10)
        self.theme = THEMES.get(self.theme_name, THEMES["dark"])
        
        self._modified = False
        self._serial = 1
        Path(FILES["backup_dir"]).mkdir(exist_ok=True)
    
    def _apply_theme(self):
        self.configure(bg=self.theme["bg_dark"])
    
    def _build_ui(self):
        self._build_menu()
        self._build_toolbar()
        self._build_contest_panel()
        self._build_form()
        self._build_actions()
        self._build_search()
        self._build_log_view()
        self._build_status()
    
    def _build_menu(self):
        menubar = Menu(self)
        self.config(menu=menubar)
        
        # File menu
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="📁 Fișier", menu=file_menu)
        file_menu.add_command(label="💾 Salvează Log", command=self._save, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="⬇ Export Cabrillo", command=self._export_cabrillo)
        file_menu.add_command(label="⬇ Export ADIF", command=self._export_adif)
        file_menu.add_command(label="⬇ Export CSV", command=self._export_csv)
        file_menu.add_separator()
        file_menu.add_command(label="🚪 Ieșire", command=self._on_close)
        
        # Tools menu
        tools_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🔧 Unelte", menu=tools_menu)
        tools_menu.add_command(label="🔍 Lookup Online", command=self._open_lookup, accelerator="Ctrl+L")
        tools_menu.add_command(label="🗺 Manager Județe", command=self._open_counties)
        tools_menu.add_separator()
        tools_menu.add_command(label="⚙ Configurare Stație", command=self._open_config)
        
        # Help menu
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="❓ Ajutor", menu=help_menu)
        help_menu.add_command(label="📖 Ghid Utilizare", command=self._show_help, accelerator="F1")
        help_menu.add_command(label="ℹ️ Despre", command=self._show_about)
    
    def _build_toolbar(self):
        tb = Frame(self, bg=self.theme["bg_header"], pady=4)
        tb.pack(fill="x")
        
        Label(tb, text="📡 YO Log PRO v9.0",
              font=("Consolas", self.font_size + 3, "bold"),
              fg=self.theme["fg_primary"], bg=self.theme["bg_header"]
              ).pack(side="left", padx=12)
        
        # Mode toggle
        self.btn_contest = Button(tb, text="🏆 Concurs",
            command=lambda: self._set_mode(self.MODE_CONTEST),
            font=("Consolas", self.font_size), relief="flat", padx=10, pady=2)
        self.btn_contest.pack(side="left", padx=4)
        
        self.btn_simple = Button(tb, text="📻 Log Simplu",
            command=lambda: self._set_mode(self.MODE_SIMPLE),
            font=("Consolas", self.font_size), relief="flat", padx=10, pady=2)
        self.btn_simple.pack(side="left", padx=4)
        
        # Online/Offline
        self.mode_btn = Button(tb,
            text="🟢 ON-LINE" if self.online_mode else "🔴 OFF-LINE",
            command=self._toggle_mode, font=("Consolas", self.font_size),
            relief="flat", padx=10, pady=2,
            bg=self.theme["fg_success"] if self.online_mode else self.theme["fg_warning"],
            fg="white")
        self.mode_btn.pack(side="left", padx=8)
        
        # Contest selector
        Label(tb, text="Concurs:", fg=self.theme["fg_muted"],
              bg=self.theme["bg_header"], font=("Consolas", self.font_size)
              ).pack(side="left", padx=(20, 4))
        
        self.cb_contest = ttk.Combobox(tb, values=[""] + sorted(self.contests.keys()),
                                       width=22, state="readonly")
        self.cb_contest.set(self.active_contest)
        self.cb_contest.pack(side="left", padx=4)
        self.cb_contest.bind("<<ComboboxSelected>>", self._on_contest_change)
        
        # Quick lookup
        Button(tb, text="🔍 Lookup", command=self._open_lookup,
               bg=self.theme["bg_card"], fg=self.theme["fg_secondary"],
               font=("Consolas", self.font_size), relief="flat", padx=8
               ).pack(side="left", padx=8)
        
        # Status right
        self.status_lbl = Label(tb, text="Gata", anchor="e",
                                fg=self.theme["fg_muted"], bg=self.theme["bg_header"],
                                font=("Consolas", self.font_size))
        self.status_lbl.pack(side="right", fill="x", expand=True, padx=12)
        
        self.date_lbl = Label(tb, text=f"📅 {self.offline_date}",
                              fg=self.theme["fg_secondary"], bg=self.theme["bg_header"],
                              font=("Consolas", self.font_size + 1))
        self.date_lbl.pack(side="right", padx=10)
        
        self.call_lbl = Label(tb, text=f"📡 {self.app_config.get('callsign', '?')}",
                              fg=self.theme["fg_secondary"], bg=self.theme["bg_header"],
                              font=("Consolas", self.font_size + 2))
        self.call_lbl.pack(side="right", padx=10)
        
        self._update_mode_buttons()
    
    def _build_contest_panel(self):
        """Contest-specific panel (Maraton/Stafeta info)."""
        panel = Frame(self, bg=self.theme["bg_panel"])
        panel.pack(fill="x", padx=10, pady=5)
        
        contest = CONTEST_TYPES.get(self.active_contest, {})
        if contest.get("name"):
            Label(panel, text=f"🏁 {contest['name']}",
                  fg=self.theme["fg_accent"], bg=self.theme["bg_panel"],
                  font=("Consolas", self.font_size + 1, "bold")).pack(side="left", padx=5)
            
            if self.active_contest == "maraton":
                Button(panel, text="🏆 Diplomă", command=self._check_diploma,
                       bg=self.theme["accent_btn"], fg="white",
                       font=("Consolas", self.font_size), relief="flat", padx=8
                       ).pack(side="left", padx=5)
                
                self.pct_lbl = Label(panel, text="",
                                     fg=self.theme["fg_accent"], bg=self.theme["bg_panel"],
                                     font=("Consolas", self.font_size, "bold"))
                self.pct_lbl.pack(side="right", padx=10)
                
                self.mand_lbl = Label(panel, text="",
                                      fg=self.theme["fg_warning"], bg=self.theme["bg_panel"],
                                      font=("Consolas", self.font_size))
                self.mand_lbl.pack(side="right", padx=10)
                
                self._update_maraton_info()
    
    def _build_form(self):
        self.form = Frame(self, bg=self.theme["bg_panel"], pady=8)
        self.form.pack(fill="x", padx=10, pady=(5, 0))
        self._build_log_form()
    
    def _build_log_form(self):
        for w in self.form.winfo_children():
            w.destroy()
        
        is_maraton = self.active_contest == "maraton"
        is_stafeta = self.active_contest == "stafeta"
        is_simple = self.app_mode.get() == self.MODE_SIMPLE
        
        pad = {"padx": (8, 2), "pady": 6}
        base_font = ("Consolas", self.font_size)
        
        # Dynamic fields based on mode/contest
        if is_simple:
            fields = [("Call*", "call", 12), ("Freq", "freq", 9), ("Band", "band", 6),
                     ("Mode", "mode", 7), ("RST-S", "rst_s", 5), ("RST-R", "rst_r", 5),
                     ("Name", "name", 10), ("Loc", "locator", 8), ("Jud", "judet", 5), ("Note", "note", 15)]
        elif is_maraton:
            fields = [("Call*", "call", 14), ("Band", "band", 7), ("Mode", "mode", 8),
                     ("RST", "rst", 5), ("Pct*", "points", 6), ("Name", "name", 12),
                     ("Jud", "judet", 5), ("Note", "note", 20)]
        elif is_stafeta:
            fields = [("Call*", "call", 14), ("Band", "band", 7), ("Mode", "mode", 8),
                     ("Cat*", "category", 6), ("RST", "rst", 5), ("Pct", "points", 6),
                     ("Name", "name", 12), ("Jud", "judet", 5), ("Note", "note", 20)]
        else:
            fields = [("Call*", "call", 12), ("RST-S", "rst_s", 5), ("RST-R", "rst_r", 5),
                     ("Band", "band", 6), ("Mode", "mode", 6), ("Serial", "serial", 6),
                     ("Name", "name", 12), ("Note", "note", 20)]
        
        self.entries = {}
        for i, (label, key, width) in enumerate(fields):
            Label(self.form, text=label, fg=self.theme["fg_muted"],
                  bg=self.theme["bg_panel"], font=base_font
                  ).grid(row=0, column=i, sticky="w", **pad)
            
            if key in ("band", "mode"):
                vals = BANDS if key == "band" else MODES_FULL
                e = ttk.Combobox(self.form, values=vals, width=width,
                                state="readonly" if key == "band" else "")
                e.set(BANDS[3] if key == "band" else "SSB")
            elif key == "judet":
                e = ttk.Combobox(self.form, values=sorted(self.counties.keys()), width=width)
                e.set(self.app_config.get("judet", "NT"))
            elif key == "category" and is_stafeta:
                e = ttk.Combobox(self.form, values=list(CONTEST_TYPES["stafeta"]["categories"].keys()), width=width)
                e.set("A")
            else:
                e = Entry(self.form, font=base_font, width=width,
                         bg=self.theme["bg_entry"], fg=self.theme["fg_text"],
                         insertbackground=self.theme["fg_text"])
                if key.startswith("rst"):
                    e.insert(0, "59")
                elif key == "freq" and is_simple:
                    e.insert(0, "14.000")
                elif key == "points":
                    e.insert(0, "1")
                elif key == "serial":
                    e.insert(0, str(self._serial).zfill(3))
            
            e.grid(row=1, column=i, **pad)
            self.entries[key] = e
            
            # Auto-detect bindings
            if key == "call":
                e.bind("<KeyRelease>", lambda ev: self._auto_points())
            elif key == "band" and is_simple:
                e.bind("<<ComboboxSelected>>", lambda ev: self._autofill_freq())
        
        Button(self.form, text="📝 LOG", command=self._log_qso,
               bg=self.theme["accent_btn"], fg="white",
               font=("Consolas", self.font_size + 1, "bold"),
               relief="flat", padx=16).grid(row=1, column=len(fields), padx=12)
        
        self.bind("<Return>", lambda e: self._log_qso())
        self.entries["call"].focus_set()
        
        # Offline date
        if not self.online_mode:
            Label(self.form, text=f"📅 {self.offline_date}",
                  fg=self.theme["fg_warning"], bg=self.theme["bg_panel"],
                  font=("Consolas", self.font_size, "bold")
                  ).grid(row=2, column=0, sticky="w", padx=8)
            Button(self.form, text="Schimbă", command=self._set_date,
                   bg=self.theme["bg_panel"], fg=self.theme["fg_muted"],
                   font=("Consolas", self.font_size - 1), relief="flat", padx=6
                   ).grid(row=2, column=1, sticky="w")
    
    def _build_actions(self):
        actions = Frame(self, bg=self.theme["bg_dark"], pady=4)
        actions.pack(fill="x", padx=10)
        
        style = {"font": ("Consolas", self.font_size), "relief": "flat", "padx": 10, "pady": 3}
        
        Button(actions, text="📊 Stats", command=self._show_stats,
               bg=self.theme["bg_panel"], fg=self.theme["fg_accent"], **style).pack(side="left", padx=2)
        Button(actions, text="⬇ Cabrillo", command=self._export_cabrillo,
               bg=self.theme["bg_panel"], fg=self.theme["fg_secondary"], **style).pack(side="left", padx=2)
        Button(actions, text="⬇ ADIF", command=self._export_adif,
               bg=self.theme["bg_panel"], fg="#a371f7", **style).pack(side="left", padx=2)
        Button(actions, text="⬇ CSV", command=self._export_csv,
               bg=self.theme["bg_panel"], fg="#58a6ff", **style).pack(side="left", padx=2)
        Button(actions, text="🔄 Refresh", command=self._save,
               bg=self.theme["bg_panel"], fg=self.theme["fg_success"], **style).pack(side="left", padx=2)
        Button(actions, text="🗑 Delete", command=self._delete_selected,
               bg=self.theme["bg_panel"], fg=self.theme["fg_error"], **style).pack(side="left", padx=2)
        Button(actions, text="⚙ Config", command=self._open_config,
               bg=self.theme["bg_panel"], fg=self.theme["fg_muted"], **style).pack(side="left", padx=2)
    
    def _build_search(self):
        search = Frame(self, bg=self.theme["bg_dark"], pady=3)
        search.pack(fill="x", padx=10)
        
        Label(search, text="🔍", bg=self.theme["bg_dark"],
              fg=self.theme["fg_muted"]).pack(side="left")
        
        self.search_var = StringVar()
        self.search_var.trace_add("write", lambda *a: self._refresh_log())
        
        Entry(search, textvariable=self.search_var,
              font=("Consolas", self.font_size), width=25,
              bg=self.theme["bg_entry"], fg=self.theme["fg_text"],
              insertbackground=self.theme["fg_text"]
              ).pack(side="left", padx=4)
        
        Label(search, text="(call/band/mode/note)",
              fg=self.theme["fg_muted"], bg=self.theme["bg_dark"],
              font=("Consolas", self.font_size - 1)).pack(side="left")
        
        self.count_lbl = Label(search, text="", fg=self.theme["fg_secondary"],
                                  bg=self.theme["bg_dark"], font=("Consolas", self.font_size))
        self.count_lbl.pack(side="right", padx=10)
    
    def _build_log_view(self):
        frame = Frame(self, bg=self.theme["bg_dark"])
        frame.pack(fill="both", expand=True, padx=10, pady=(5, 0))
        
        is_maraton = self.active_contest == "maraton"
        is_stafeta = self.active_contest == "stafeta"
        is_simple = self.app_mode.get() == self.MODE_SIMPLE
        
        if is_simple:
            cols = [("Date",80),("Time",50),("Call",100),("Freq",70),("Band",60),
                   ("Mode",60),("RST",40),("Name",100),("Jud",40),("Note",200)]
        elif is_maraton or is_stafeta:
            cols = [("Date",80),("Time",50),("Call",100),("Band",60),("Mode",60),
                   ("RST",40),("Pct",60),("Jud",40),("Note",200)]
        else:
            cols = [("Date",80),("Time",50),("Call",110),("Band",60),("Mode",60),
                   ("RST-S",45),("RST-R",45),("Serial",50),("Note",200)]
        
        style = ttk.Style()
        style.configure("Treeview", background=self.theme["bg_dark"],
                       fieldbackground=self.theme["bg_dark"],
                       foreground=self.theme["fg_text"],
                       font=("Consolas", self.font_size))
        style.configure("Treeview.Heading", background=self.theme["bg_panel"],
                       foreground=self.theme["fg_primary"],
                       font=("Consolas", self.font_size, "bold"))
        
        self.tree = ttk.Treeview(frame, columns=[c[0] for c in cols],
                                show="headings", height=15)
        for name, width in cols:
            self.tree.heading(name, text=name)
            self.tree.column(name, width=width, minwidth=width)
        
        self.tree.tag_configure("odd", background=self.theme["bg_card"])
        self.tree.tag_configure("even", background=self.theme["bg_dark"])
        self.tree.tag_configure("special", foreground=self.theme["fg_accent"])
        self.tree.tag_configure("mandatory", foreground=self.theme["fg_warning"])
        
        sb_y = Scrollbar(frame, command=self.tree.yview)
        sb_x = Scrollbar(frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)
        
        sb_y.pack(side="right", fill="y")
        sb_x.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)
    
    def _build_status(self):
        self.bottom = Label(self, text="", anchor="w",
                           bg=self.theme["bg_header"], fg=self.theme["fg_muted"],
                           font=("Consolas", self.font_size))
        self.bottom.pack(fill="x")
    
    # ═══════════════════════════════════════════════════════════
    #  CORE FUNCTIONS
    # ═══════════════════════════════════════════════════════════
    
    def _set_mode(self, mode):
        self.app_mode.set(mode)
        self._update_mode_buttons()
        self._build_log_form()
        self._refresh_log()
        name = "Concurs" if mode == self.MODE_CONTEST else "Log Simplu"
        self._status(f"Mod: {name}")
    
    def _update_mode_buttons(self):
        mode = self.app_mode.get()
        if mode == self.MODE_CONTEST:
            self.btn_contest.config(bg=self.theme["accent_btn"], fg="white")
            self.btn_simple.config(bg=self.theme["bg_card"], fg=self.theme["fg_muted"])
        else:
            self.btn_simple.config(bg=self.theme["fg_success"], fg="white")
            self.btn_contest.config(bg=self.theme["bg_card"], fg=self.theme["fg_muted"])
    
    def _toggle_mode(self):
        self.online_mode = not self.online_mode
        self.mode_btn.config(
            text="🟢 ON-LINE" if self.online_mode else "🔴 OFF-LINE",
            bg=self.theme["fg_success"] if self.online_mode else self.theme["fg_warning"])
        self._build_log_form()
        self._update_title()
        self._status(f"Mod: {'ON-LINE' if self.online_mode else 'OFF-LINE'}")
    
    def _set_date(self):
        dlg = Toplevel(self)
        dlg.title("📅 Setare Dată")
        dlg.configure(bg=self.theme["bg_dark"])
        dlg.resizable(False, False)
        dlg.grab_set()
        
        base_font = ("Consolas", self.font_size)
        Label(dlg, text="Data (YYYY-MM-DD):",
              fg=self.theme["fg_muted"], bg=self.theme["bg_dark"],
              font=base_font).pack(pady=15)
        
        entry = Entry(dlg, font=("Consolas", self.font_size + 1), width=15,
                     bg=self.theme["bg_entry"], fg=self.theme["fg_text"],
                     insertbackground=self.theme["fg_text"])
        entry.insert(0, self.offline_date)
        entry.pack(pady=5)
        
        def ok():
            d = entry.get().strip()
            if re.match(r"^\d{4}-\d{2}-\d{2}$", d):
                self.offline_date = d
                self.date_lbl.config(text=f"📅 {self.offline_date}")
                self._build_log_form()
                dlg.destroy()
            else:
                messagebox.showerror("Eroare", "Format invalid! YYYY-MM-DD", parent=dlg)
        
        btn_frame = Frame(dlg, bg=self.theme["bg_dark"])
        btn_frame.pack(pady=15)
        Button(btn_frame, text="OK", command=ok, bg=self.theme["fg_success"],
               fg="white", font=("Consolas", self.font_size, "bold"),
               relief="flat", padx=20).pack(side="left", padx=10)
        Button(btn_frame, text="Anulează", command=dlg.destroy,
               bg=self.theme["bg_card"], fg=self.theme["fg_muted"],
               font=("Consolas", self.font_size), relief="flat", padx=20).pack(side="left")
        
        entry.focus_set()
        dlg.bind("<Return>", lambda e: ok())
    
    def _on_contest_change(self, event=None):
        self.active_contest = self.cb_contest.get()
        self.app_config["active_contest"] = self.active_contest
        safe_save_json(FILES["config"], self.app_config)
        self._build_log_form()
        self._refresh_log()
        self._update_maraton_info()
        self._status(f"Concurs: {self.active_contest or 'Niciunul'}")
    
    def _auto_points(self):
        """Auto-detect points for Maraton."""
        if self.active_contest != "maraton":
            return
        call = self.entries.get("call", Entry()).get().upper().strip()
        if not call:
            return
        pts = ScoringEngine.get_maraton_points(call)
        if pts > 0 and "points" in self.entries:
            self.entries["points"].delete(0, "end")
            self.entries["points"].insert(0, str(pts))
            base = clean_callsign(call)
            if base in CONTEST_TYPES["maraton"]["special_stations"]:
                self.entries["call"].config(bg="#4a2a2a")
            else:
                self.entries["call"].config(bg=self.theme["bg_entry"])
    
    def _autofill_freq(self):
        """Auto-fill frequency based on band."""
        band = self.entries.get("band", ttk.Combobox()).get()
        if band and "freq" in self.entries:
            self.entries["freq"].delete(0, "end")
            self.entries["freq"].insert(0, str(BAND_FREQ_MHZ.get(band, 14.0)))
    
    def _update_maraton_info(self):
        """Update Maraton scoring display."""
        if self.active_contest != "maraton":
            if hasattr(self, 'pct_lbl'):
                self.pct_lbl.config(text="")
                self.mand_lbl.config(text="")
            return
        
        scoring = ScoringEngine.calculate_maraton_total(self.log, self.app_config.get("callsign", ""))
        if hasattr(self, 'pct_lbl'):
            self.pct_lbl.config(text=f"Puncte: {scoring['total_points']}")
            self.mand_lbl.config(text=f"Obligatorii: {len(scoring['mandatory_worked'])}/2")
            if scoring['mandatory_missing']:
                self.mand_lbl.config(fg=self.theme["fg_warning"])
            else:
                self.mand_lbl.config(fg=self.theme["fg_success"])
    
    def _log_qso(self):
        """Log a new QSO with validation."""
        call = clean_callsign(self.entries["call"].get())
        if not CALLSIGN_REGEX.match(call):
            messagebox.showerror("Eroare", "Callsign invalid!")
            return
        
        now = datetime.datetime.utcnow()
        is_maraton = self.active_contest == "maraton"
        is_stafeta = self.active_contest == "stafeta"
        is_simple = self.app_mode.get() == self.MODE_SIMPLE
        
        qso = {
            "date": self.offline_date if not self.online_mode else now.strftime("%Y-%m-%d"),
            "time": "0000" if not self.online_mode else now.strftime("%H%M"),
            "call": self.entries["call"].get().upper().strip(),
            "band": self.entries["band"].get(),
            "mode": self.entries["mode"].get(),
            "rst_s": self.entries.get("rst_s", Entry()).get() or "59",
            "rst_r": self.entries.get("rst_r", Entry()).get() or "59",
            "contest": self.active_contest or None,
            "qso_type": "simple" if is_simple else "contest",
        }
        
        # Mode-specific fields
        if is_simple:
            qso.update({
                "freq": self.entries.get("freq", Entry()).get(),
                "name": self.entries.get("name", Entry()).get().strip(),
                "locator": self.entries.get("locator", Entry()).get().upper().strip(),
                "judet": self.entries.get("judet", Entry()).get().upper().strip(),
                "note": self.entries.get("note", Entry()).get().strip(),
            })
        elif is_maraton:
            try:
                qso["points"] = int(self.entries["points"].get() or 1)
            except:
                qso["points"] = ScoringEngine.get_maraton_points(qso["call"])
            qso.update({
                "name": self.entries.get("name", Entry()).get().strip(),
                "judet": self.entries.get("judet", Entry()).get().upper().strip(),
                "note": self.entries.get("note", Entry()).get().strip(),
                "is_maraton": True,
            })
        elif is_stafeta:
            cat = self.entries.get("category", Entry()).get()
            qso["category"] = cat
            qso["points"] = ScoringEngine.get_stafeta_points(qso["call"], cat)
            qso.update({
                "name": self.entries.get("name", Entry()).get().strip(),
                "judet": self.entries.get("judet", Entry()).get().upper().strip(),
                "note": self.entries.get("note", Entry()).get().strip(),
                "is_stafeta": True,
            })
        else:
            qso["serial"] = str(self._serial).zfill(3)
            qso["name"] = self.entries.get("name", Entry()).get().strip()
            qso["note"] = self.entries.get("note", Entry()).get().strip()
            self._serial += 1
        
        self.log.append(qso)
        self._modified = True
        self._refresh_log()
        self._update_maraton_info()
        
        # Clear form
        self.entries["call"].delete(0, "end")
        for k in ["name", "note", "locator"]:
            if k in self.entries:
                self.entries[k].delete(0, "end")
        self.entries["call"].focus_set()
        
        self._status(f"✔ Logat: {qso['call']} @ {qso['band']} [{qso['mode']}]")
    
    def _refresh_log(self):
        """Refresh log display with filtering."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        query = self.search_var.get().upper().strip()
        contest_filter = self.active_contest if self.active_contest else None
        is_maraton = self.active_contest == "maraton"
        is_stafeta = self.active_contest == "stafeta"
        is_simple = self.app_mode.get() == self.MODE_SIMPLE
        
        for i, q in enumerate(self.log):
            if contest_filter and q.get("contest") != contest_filter:
                continue
            if query and not any(query in str(q.get(k, "")).upper()
                               for k in ["call", "band", "mode", "note", "name", "judet", "freq"]):
                continue
            
            tags = ("even" if i % 2 == 0 else "odd",)
            base = clean_callsign(q["call"])
            if base in CONTEST_TYPES.get("maraton", {}).get("special_stations", {}):
                tags += ("mandatory",)
            
            if is_simple:
                vals = (q["date"], q["time"], q["call"], q.get("freq", ""),
                       q["band"], q["mode"], f"{q.get('rst_s','59')}/{q.get('rst_r','59')}",
                       q.get("name", ""), q.get("judet", ""), q.get("note", ""))
            elif is_maraton or is_stafeta:
                vals = (q["date"], q["time"], q["call"], q["band"], q["mode"],
                       q.get("rst_s", "59"), q.get("points", 1),
                       q.get("judet", ""), q.get("note", ""))
            else:
                vals = (q["date"], q["time"], q["call"], q["band"], q["mode"],
                       q.get("rst_s", "59"), q.get("rst_r", "59"),
                       q.get("serial", ""), q.get("note", ""))
            
            self.tree.insert("", "end", iid=i, values=vals, tags=tags)
        
        cnt = len(self.tree.get_children())
        self.count_lbl.config(text=f"{cnt} QSO" if cnt != 1 else "1 QSO")
    
    def _delete_selected(self):
        """Delete selected QSO."""
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Selectează un QSO!", parent=self)
            return
        if messagebox.askyesno("Confirmare", "Ștergi QSO-ul selectat?"):
            idx = int(sel[0])
            deleted = self.log.pop(idx)
            self._modified = True
            self._refresh_log()
            self._save()
            self._status(f"🗑 Șters: {deleted['call']}")
    
    # ═══════════════════════════════════════════════════════════
    #  EXPORT FUNCTIONS
    # ═══════════════════════════════════════════════════════════
    
    def _export_cabrillo(self):
        if not self.log:
            messagebox.showinfo("Export", "Log-ul este gol!", parent=self)
            return
        
        call = self.app_config.get("callsign", "CALLSIGN")
        path = filedialog.asksaveasfilename(initialfile=f"{call}.log",
                                           defaultextension=".log",
                                           filetypes=[("Cabrillo", "*.log")],
                                           title="Salvează Cabrillo")
        if not path:
            return
        
        content = ExportEngine.to_cabrillo(self.log, self.app_config, self.active_contest)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        
        messagebox.showinfo("Export Cabrillo", f"Salvat: {path}\nCompatibil cu YO-DX-HF, Stafeta, Maraton", parent=self)
    
    def _export_adif(self):
        if not self.log:
            return
        path = filedialog.asksaveasfilename(initialfile="log.adi",
                                           defaultextension=".adi",
                                           filetypes=[("ADIF", "*.adi")],
                                           title="Salvează ADIF")
        if not path:
            return
        
        content = ExportEngine.to_adif(self.log, self.app_config)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        
        messagebox.showinfo("Export ADIF", f"Salvat: {path}\nCompatibil cu eQSL, QRZ, ClubLog", parent=self)
    
    def _export_csv(self):
        if not self.log:
            return
        path = filedialog.asksaveasfilename(initialfile="log.csv",
                                           defaultextension=".csv",
                                           filetypes=[("CSV", "*.csv")],
                                           title="Salvează CSV")
        if not path:
            return
        
        content = ExportEngine.to_csv(self.log)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        
        messagebox.showinfo("Export CSV", f"Salvat: {path}\nDeschide în Excel/LibreOffice", parent=self)
    
    # ═══════════════════════════════════════════════════════════
    #  PERSISTENCE & UTILS
    # ═══════════════════════════════════════════════════════════
    
    def _save(self):
        if not self._modified:
            self._status("✓ Nimic de salvat")
            return
        
        safe_save_json(FILES["log"], self.log)
        
        # Rotating backup
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy(FILES["log"], f"{FILES['backup_dir']}/log_{ts}.json")
        rotate_backups(FILES["backup_dir"])
        
        # Text backup
        try:
            with open(FILES["backup_txt"], "w", encoding="utf-8") as f:
                f.write(f"# Backup YO Log PRO - {datetime.datetime.now()}\n")
                for q in self.log:
                    line = (f"{q['date']} | {q['time']} | {q['call']} | {q['band']} | "
                           f"{q['mode']} | {q.get('rst_s','59')}/{q.get('rst_r','59')} | "
                           f"{q.get('judet','')} | {q.get('name','')}\n")
                    f.write(line)
        except Exception as e:
            self._status(f"⚠ Backup text eșuat: {e}")
        
        self._modified = False
        self._status("✓ Log salvat + backup creat")
    
    def _update_title(self):
        call = self.app_config.get("callsign", "?")
        mode = "ON-LINE" if self.online_mode else f"OFF-LINE {self.offline_date}"
        contest = f" • {self.active_contest}" if self.active_contest else ""
        mode_name = "Concurs" if self.app_mode.get() == self.MODE_CONTEST else "Log Simplu"
        self.title(f"{call} {mode} {mode_name}{contest} — YO Log PRO v9.0")
    
    def _status(self, msg):
        self.status_lbl.config(text=msg)
        self.bottom.config(text=msg)
        self.after(5000, lambda: self.status_lbl.config(text="Gata")
                  if self.status_lbl.cget("text") == msg else None)
    
    def _on_close(self):
        if self._modified:
            if not messagebox.askyesno("Confirmare",
                                      "Există modificări nesalvate. Salvezi înainte de ieșire?"):
                return
            self._save()
        self.destroy()
    
    # ═══════════════════════════════════════════════════════════
    #  DIALOGS
    # ═══════════════════════════════════════════════════════════
    
    def _open_lookup(self):
        call = self.entries.get("call", Entry()).get().upper().strip()
        LookupDialog(self, call, self.theme_name, self.font_size)
    
    def _open_counties(self):
        CountyManagerDialog(self, self.counties, self._apply_counties,
                           self.theme_name, self.font_size)
    
    def _apply_counties(self, new_counties):
        self.counties = new_counties
        safe_save_json(FILES["judete"], self.counties)
        self._status(f"✓ {len(self.counties)} județe actualizate")
    
    def _open_config(self):
        # Simplified config dialog
        dlg = Toplevel(self)
        dlg.title("⚙ Configurare")
        dlg.configure(bg=self.theme["bg_dark"])
        dlg.geometry("500x400")
        dlg.resizable(False, False)
        dlg.grab_set()
        
        base_font = ("Consolas", self.font_size)
        pad = {"padx": 14, "pady": 8}
        
        Label(dlg, text="⚙ Configurare Stație", font=("Consolas", self.font_size + 2, "bold"),
              fg=self.theme["fg_primary"], bg=self.theme["bg_dark"]).pack(pady=14)
        
        fields = [("Callsign", "callsign", "YO8ACR"), ("Locator", "locator", "KN46"),
                 ("Putere", "power", "100"), ("Operator", "operator", ""),
                 ("Județ", "judet", "NT"), ("Categorie", "category", "SINGLE-OP")]
        
        entries = {}
        for label, key, default in fields:
            f = Frame(dlg, bg=self.theme["bg_dark"])
            f.pack(fill="x", padx=14, pady=4)
            Label(f, text=label+":", fg=self.theme["fg_muted"],
                  bg=self.theme["bg_dark"], font=base_font).pack(side="left")
            e = Entry(f, font=base_font, width=25,
                     bg=self.theme["bg_entry"], fg=self.theme["fg_text"],
                     insertbackground=self.theme["fg_text"])
            e.insert(0, self.app_config.get(key, default))
            e.pack(side="left", padx=10)
            entries[key] = e
        
        def save():
            for k, e in entries.items():
                self.app_config[k] = e.get().strip()
            safe_save_json(FILES["config"], self.app_config)
            self.call_lbl.config(text=f"📡 {self.app_config.get('callsign', '?')}")
            dlg.destroy()
            self._status("✓ Configurare salvată")
        
        Button(dlg, text="💾 Salvează", command=save,
               bg=self.theme["accent_btn"], fg="white", font=("Consolas", self.font_size, "bold"),
               relief="flat", padx=20, pady=4).pack(pady=20)
    
    def _check_diploma(self):
        if self.active_contest != "maraton":
            messagebox.showinfo("Info", "Selectează Maraton Ion Creangă!", parent=self)
            return
        
        scoring = ScoringEngine.calculate_maraton_total(self.log, self.app_config.get("callsign", ""))
        
        dlg = Toplevel(self)
        dlg.title("🏆 Diplomă Maraton")
        dlg.configure(bg=self.theme["bg_dark"])
        dlg.geometry("450x350")
        dlg.resizable(False, False)
        dlg.grab_set()
        
        base_font = ("Consolas", self.font_size)
        color = self.theme["fg_success"] if scoring["eligible_for_diploma"] else self.theme["fg_error"]
        status = "✅ ELIGIBIL" if scoring["eligible_for_diploma"] else "❌ NU ÎNCĂ"
        
        Label(dlg, text=f"🏆 Diplomă Maraton Ion Creangă\n\n{status}",
              font=("Consolas", self.font_size + 3, "bold"), fg=color,
              bg=self.theme["bg_dark"]).pack(pady=20)
        
        Frame(dlg, bg=self.theme["bg_panel"], height=2).pack(fill="x", padx=20)
        
        details = [
            ("QSO totale", f"{scoring['total_qsos']} / 100"),
            ("Puncte", str(scoring["total_points"])),
            ("Obligatorii", f"{len(scoring['mandatory_worked'])}/2"),
        ]
        for label, value in details:
            f = Frame(dlg, bg=self.theme["bg_dark"])
            f.pack(fill="x", padx=20, pady=4)
            Label(f, text=f"{label}:", fg=self.theme["fg_muted"],
                  bg=self.theme["bg_dark"], font=base_font).pack(side="left")
            Label(f, text=value, fg=self.theme["fg_primary"],
                  bg=self.theme["bg_dark"], font=("Consolas", self.font_size + 1, "bold")).pack(side="left", padx=10)
        
        if scoring["mandatory_missing"]:
            Label(dlg, text=f"⚠️ NE-LUCRATE: {', '.join(scoring['mandatory_missing'])}",
                  fg=self.theme["fg_warning"], bg=self.theme["bg_dark"], font=base_font).pack(pady=10)
        
        Button(dlg, text="Închide", command=dlg.destroy,
               bg=self.theme["bg_card"], fg=self.theme["fg_text"], font=base_font,
               relief="flat", padx=20, pady=4).pack(pady=14)
    
    def _show_stats(self):
        if not self.log:
            messagebox.showinfo("Statistici", "Log-ul este gol!", parent=self)
            return
        
        total = len(self.log)
        by_band = Counter(q["band"] for q in self.log)
        by_mode = Counter(q["mode"] for q in self.log)
        
        msg = f"📊 STATISTICI\n{'─'*40}\nTotal QSO: {total}\n"
        if self.active_contest == "maraton":
            scoring = ScoringEngine.calculate_maraton_total(self.log, self.app_config.get("callsign", ""))
            msg += f"Puncte Maraton: {scoring['total_points']}\n"
            msg += f"Diplomă: {'✅ ELIGIBIL' if scoring['eligible_for_diploma'] else '❌ NU ÎNCĂ'}\n"
        msg += f"\nBenzi: {len(by_band)} | Moduri: {len(by_mode)}"
        
        messagebox.showinfo("Statistici", msg, parent=self)
    
    def _show_help(self):
        help_text = (
            "📖 YO Log PRO v9.0 - Ghid Rapid\n\n"
            "🔹 MODURI:\n"
            "  • 🏆 Concurs: Logare rapidă cu serial auto\n"
            "  • 📻 Log Simplu: QSO complete cu frecvență, locator, județ\n\n"
            "🔹 FUNCȚII:\n"
            "  • Ctrl+S: Salvează log\n"
            "  • Ctrl+L: Lookup online callsign\n"
            "  • F1: Acest ghid\n\n"
            "🔹 EXPORT:\n"
            "  • Cabrillo: Pentru arbitraj concursuri\n"
            "  • ADIF: Pentru eQSL/QRZ/ClubLog\n"
            "  • CSV: Pentru Excel/processing\n\n"
            "🔹 MARATON:\n"
            "  • YP8IC/YR8TGN = 20 pct (OBLIGATORII)\n"
            "  • /IC din NT/IS = 10/5 pct\n"
            "  • 1 QSO/zi/stație pentru punctaj\n"
            "  • Diplomă: 100 QSO + stații obligatorii\n\n"
            "🔹 STAFETA:\n"
            "  • Categorii A-E cu punctaj diferit\n"
            "  • Selectează categoria la logare\n\n"
            "Suport: yo8acr@gmail.com"
        )
        messagebox.showinfo("Ajutor", help_text, parent=self)
    
    def _show_about(self):
        about = (
            "📡 YO Log PRO v9.0\n\n"
            "Professional Contest Logger\n\n"
            "Author: YO8ACR Ardei Constantin-Cătălin\n"
            "QTH: Târgu Neamț, România\n\n"
            "Caracteristici:\n"
            "• Multi-contest: YO-DX-HF, Stafeta, Maraton, Simple\n"
            "• N1MM-compatible: multipliers, dupe check, scoring\n"
            "• Export: Cabrillo, ADIF 3.1.0+, CSV\n"
            "• Online lookup: QRZ, Radioamator.ro, Callbook, eQSL\n"
            "• Windows 7/10/11 optimized\n\n"
            "https://github.com/YO8ACR/YO-Log-PRO\n\n"
            "73! 📻"
        )
        messagebox.showinfo("Despre", about, parent=self)

# ═══════════════════════════════════════════════════════════════
#  MAIN ENTRY
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    if sys.version_info < (3, 7):
        print("⚠ YO Log PRO necesită Python 3.7+")
        sys.exit(1)
    app = App()
    app.mainloop()
