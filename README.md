# 📻 YO Log PRO v12.0

<div align="center">

![YO Log PRO Banner](https://img.shields.io/badge/YO%20Log%20PRO-v12.0-crimson?style=for-the-badge&logo=radio&logoColor=white)

[![Build Status](https://img.shields.io/github/actions/workflow/status/youruser/yologpro/build.yml?branch=main&style=flat-square&logo=github-actions&label=Build)](https://github.com/youruser/yologpro/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey?style=flat-square)](https://github.com/youruser/yologpro/releases)
[![Release](https://img.shields.io/github/v/release/youruser/yologpro?style=flat-square&logo=github)](https://github.com/youruser/yologpro/releases/latest)

**Aplicație profesională de logging pentru radioamatori români**  
*Professional Contest Logging Software for Romanian Amateur Radio Operators*

[📥 Descarcă / Download](#-instalare--installation) · [📖 Documentație / Docs](#-ghid-de-utilizare--user-guide) · [🛠️ Dezvoltatori / Developers](#️-ghid-pentru-dezvoltatori--developer-guide) · [🗺️ Roadmap](#️-roadmap) · [🐛 Raportează un bug](https://github.com/youruser/yologpro/issues)

</div>

---

## 📖 Descriere / About

**YO Log PRO** este o aplicație desktop modernă, specializată în înregistrarea legăturilor radio (*QSO*) în cadrul concursurilor de radioamatorism. Proiectată special pentru operatorii din România, oferă suport complet pentru cele mai populare concursuri naționale, inclusiv logica avansată de punctaj pentru **Maratonul Radioamatorilor** (YP8IC / YR8TGN).

**YO Log PRO** is a modern desktop application specialized in logging radio contacts (QSOs) during amateur radio contests. Designed specifically for Romanian operators, it provides full support for the most popular national contests, including advanced scoring logic for the **Romanian Radio Marathon** (YP8IC / YR8TGN).

> 🎯 **Scop dual / Dual purpose:** Accesibilă pentru utilizatorii finali (fără Python), complet documentată pentru dezvoltatori.

---

## ✨ Caracteristici Principale / Key Features

### 🏆 Suport Multi-Concurs / Multi-Contest Support

| Concurs / Contest | Mod / Mode | Reguli Speciale / Special Rules |
|---|---|---|
| Maratonul Radioamatorilor (YP8IC) | SSB / CW / Digital | Punctaj special pentru `/IC` și `/YR8TGN` |
| Concursul Național YO | SSB / CW | Multiplicatori județe YO |
| IARU Region 1 | Mixed | Reguli IARU complete |
| WAE (Worked All Europe) | SSB / CW | QTC support |
| *și altele / and more...* | — | — |

### 📝 Logging Avansat / Advanced QSO Logging

- **Introducere rapidă** prin tastatură — câmpuri în ordine logică (callsign → RST → schimb)
- **Validare în timp real** a callsign-urilor (format, prefixe YO, sufixe speciale `/IC`, `/P`, `/M`)
- **Deduplicare automată** — alertă la dubluri (dupe) cu opțiune de confirmare manuală
- **Căutare online** callsign cu afișare informații QRZ / HamDB *(Online Search)*
- **UTC sync automat** — ora se preia din sistemul local și se afișează în timp real

### 🧮 Logica de Punctaj Maraton / Marathon Scoring Engine

Motor de reguli modular care implementează complet punctajul **Maratonul Radioamatorilor**:

```
Stație normală:          1 punct / QSO pe bandă nouă
Stație /IC sau /YR8TGN: 5 puncte / QSO (bonus operator special)
Multiplicator:           Fiecare județ YO nou per bandă
```

- Calculul se face **în timp real** pe măsură ce se adaugă QSO-uri
- Tabela de scor afișează: Total QSO / QSO valide / Multiplicatori / **Scor final**
- **Poate fi schimbat concursul** oricând din sesiune, cu recalculare automată

### 💾 Integritate Date / Data Integrity

- **Salvare atomică** — fișierul `.log` nu se corupe niciodată în caz de oprire bruscă
- **Backup automat** înainte de fiecare salvare în directorul `backups/`
- **Format ADIF standard** — compatibil cu orice software de logging
- Suport **JSON nativ** pentru configurare și reguli concurs

### 📤 Export / Export Options

- Export **ADIF** (`.adi`) — standard universal pentru logging
- Export **Cabrillo** (`.cbr` / `.log`) — pentru trimiterea scorurilor la concursuri
- Export **CSV** — pentru analiză în Excel / LibreOffice Calc
- **Raport HTML** cu statistici complete și grafice per bandă

### 🎨 Interfață Modernă / Modern UI

- Interfață bilingvă **Română / Engleză** (comutabilă din setări)
- Teme vizuale: **Dark Mode** și **Light Mode**
- Tabele sortabile, coloane redimensionabile
- **Shortcut-uri tastatură** pentru operare rapidă în contest

---

## 🖼️ Capturi de Ecran / Screenshots

> 📌 *Capturi de ecran reale vor fi adăugate la prima versiune publică.*  
> *Actual screenshots will be added with the first public release.*

```
┌─────────────────────────────────────────────────────┐
│  📻 YO Log PRO v12.0          [Dark Mode] [EN/RO]   │
├──────────────┬──────────────────────────────────────┤
│ CONTEST:     │  Maratonul Radioamatorilor YP8IC      │
│ OPERATOR:    │  YO8XXX / Iași                        │
│ BAND:        │  40m    MODE: SSB    PWR: 100W        │
├──────────────┴──────────────────────────────────────┤
│  Callsign: [YO8ABC____]  RST S: [59] R: [59]        │
│  Exchange:  [IS________]  UTC: 14:32:07              │
│                              [  LOG QSO  ] [CLEAR]  │
├─────────────────────────────────────────────────────┤
│ #  │ UTC   │ Callsign │ Band │ RST  │ Exch │ Pts    │
│ 1  │ 14:20 │ YO8ABC   │ 40m  │ 59/59│ IS   │  1     │
│ 2  │ 14:25 │ YR8TGN/IC│ 40m  │ 59/59│ TL   │  5 ★  │
│ 3  │ 14:31 │ YP8IC    │ 40m  │ 59/59│ IS   │  5 ★  │
├─────────────────────────────────────────────────────┤
│  QSO Total: 3 │ Valid: 3 │ Mult: 2 │ SCORE: 33      │
└─────────────────────────────────────────────────────┘
```

*[Placeholder — Fereastră principală / Main Window]*

---

## 📥 Instalare / Installation

### 👤 Utilizatori Finali / End Users (No Python Required)

**Nu ai nevoie de Python sau orice alt program instalat!**  
*No Python or additional software needed!*

1. **Descarcă** ultima versiune din pagina [Releases](https://github.com/youruser/yologpro/releases/latest)
2. Alege fișierul potrivit pentru sistemul tău:

   | Sistem / System | Fișier / File |
   |---|---|
   | Windows 10/11 (64-bit) | `YOLogPRO-v12.0-win64.zip` |
   | Linux (Ubuntu/Debian) | `YOLogPRO-v12.0-linux-x86_64.tar.gz` |
   | macOS (Intel / Apple Silicon) | `YOLogPRO-v12.0-macos.dmg` |

3. **Dezarhivează** în directorul dorit (ex: `C:\YOLogPRO\`)
4. **Rulează** `YOLogPRO.exe` (Windows) sau `./YOLogPRO` (Linux/macOS)

> ⚠️ **Notă Windows:** La prima rulare, Windows Defender poate afișa un avertisment SmartScreen. Apasă **"More info" → "Run anyway"**. Executabilul este semnat și verificat prin GitHub Actions.

---

## ⚙️ Configurare Inițială / Initial Configuration

La prima pornire, aplicația creează automat `config.json` în directorul de date al utilizatorului:

**Windows:** `%APPDATA%\YOLogPRO\config.json`  
**Linux/macOS:** `~/.config/yologpro/config.json`

```json
{
  "operator": {
    "callsign": "YO8XXX",
    "name": "Ion Ionescu",
    "qth": "Iași",
    "county": "IS",
    "grid": "KN46",
    "power_w": 100
  },
  "ui": {
    "language": "ro",
    "theme": "dark",
    "font_size": 12
  },
  "logging": {
    "auto_backup": true,
    "backup_count": 10,
    "log_directory": "~/YOLogPRO/logs"
  }
}
```

Toate setările pot fi modificate și din interfața grafică: **Meniu → Setări / Settings**.

---

## 📖 Ghid de Utilizare / User Guide

### Pasul 1: Configurează Stația / Configure Your Station

1. Deschide **Setări → Date Stație**
2. Completează: Indicativ, Nume, QTH, Județ, Locator Maidenhead, Putere
3. Apasă **Salvează / Save**

### Pasul 2: Selectează Concursul / Select Contest

1. Din bara de meniu: **Concurs → Schimbă Concursul**
2. Selectează din lista de concursuri disponibile
3. Configurează banda și modul activ

> 💡 Poți schimba concursul în orice moment — log-ul curent se salvează automat, iar scorul este recalculat după noile reguli.

### Pasul 3: Înregistrează QSO-uri / Log QSOs

Fluxul standard de introducere:

```
1. Tastează callsign-ul în câmpul "Callsign" → ENTER
2. Sistemul validează formatul și verifică dublurile (dupes)
3. Completează RST Sent / Received
4. Completează schimbul (județ, serial, etc.)
5. Apasă ENTER sau butonul "LOG QSO"
6. QSO-ul apare instant în tabela de mai jos
```

**Shortcut-uri rapide / Quick shortcuts:**

| Tastă / Key | Acțiune / Action |
|---|---|
| `F1` | Focus câmp Callsign |
| `F2` | Căutare online callsign |
| `F3` | Schimbă banda |
| `F4` | Schimbă modul (SSB/CW/Digital) |
| `F9` | Șterge ultimul QSO |
| `Ctrl+S` | Salvează log manual |
| `Ctrl+E` | Export ADIF |

### Pasul 4: Validare și Verificare / Validation & Review

- **Coloana "Pts"** arată punctele acordate per QSO (★ pentru stații bonus)
- Bara de status afișează în timp real: **QSO Total / Valid / Multiplicatori / Scor Final**
- Accesează **Vizualizare → Statistici** pentru grafice per bandă/mod/oră

### Pasul 5: Export și Trimitere / Export & Submit

1. **Meniu → Export → ADIF** — pentru arhivă personală
2. **Meniu → Export → Cabrillo** — pentru trimitere la organizatori
3. **Meniu → Export → Raport HTML** — pentru publicare pe site/club

---

## 🛠️ Ghid pentru Dezvoltatori / Developer Guide

### Tehnologii Utilizate / Tech Stack

| Componentă / Component | Tehnologie / Technology |
|---|---|
| Limbaj / Language | Python 3.10+ |
| GUI Framework | Tkinter + `ttk` themed widgets |
| Date / Data | JSON (config, reguli concurs) + ADIF |
| Build / Packaging | PyInstaller + GitHub Actions CI/CD |
| Testare / Testing | `pytest` + `unittest.mock` |
| Linting | `flake8` + `black` |

### Cerințe Preliminare / Prerequisites

```bash
# Python 3.10 sau mai nou
python --version  # Python 3.10.x

# Clonează repository-ul
git clone https://github.com/youruser/yologpro.git
cd yologpro

# Creează un mediu virtual
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate.bat       # Windows

# Instalează dependențele
pip install -r requirements.txt
```

### Structura Proiectului / Project Structure

```
yologpro/
├── main.py                     # Entry point principal
├── config.json                 # Configurare implicită (template)
├── contests.json               # Definițiile concursurilor și regulile de punctaj
├── requirements.txt
├── yologpro.spec               # Fișier PyInstaller pentru build
│
├── core/
│   ├── __init__.py
│   ├── logger.py               # Engine-ul principal de logging QSO
│   ├── validator.py            # Validare callsign și exchange
│   ├── scorer.py               # Motor de calcul scor (modular per concurs)
│   ├── adif.py                 # Import/Export ADIF
│   ├── cabrillo.py             # Export Cabrillo
│   └── backup.py               # Salvare atomică și backup automat
│
├── contests/
│   ├── __init__.py
│   ├── base_contest.py         # Clasă abstractă pentru concursuri
│   ├── maraton_yo.py           # Regulile Maratonului Radioamatorilor
│   ├── concurs_national.py     # Concursul Național YO
│   └── iaru_r1.py              # IARU Region 1
│
├── ui/
│   ├── __init__.py
│   ├── main_window.py          # Fereastra principală
│   ├── qso_table.py            # Tabela de QSO-uri (sortabilă)
│   ├── score_panel.py          # Panoul de scor în timp real
│   ├── settings_dialog.py      # Dialog setări
│   └── themes.py               # Teme Dark/Light
│
├── data/
│   └── contests.json           # Date concursuri și reguli
│
├── tests/
│   ├── test_validator.py
│   ├── test_scorer.py
│   └── test_adif.py
│
└── .github/
    └── workflows/
        └── build.yml           # CI/CD: build automat pe Windows/Linux/macOS
```

### Motorul de Reguli Modular / Modular Contest Rules Engine

Fiecare concurs extinde clasa de bază `BaseContest`:

```python
# contests/base_contest.py
from abc import ABC, abstractmethod

class BaseContest(ABC):
    """Clasă abstractă pentru toate concursurile."""

    @abstractmethod
    def get_qso_points(self, qso: dict, log: list) -> int:
        """Returnează punctele pentru un QSO dat."""
        ...

    @abstractmethod
    def get_multipliers(self, log: list) -> list:
        """Returnează lista de multiplicatori activi."""
        ...

    @abstractmethod
    def calculate_final_score(self, log: list) -> int:
        """Calculează scorul final conform regulilor concursului."""
        ...
```

Exemplu implementare pentru Maraton:

```python
# contests/maraton_yo.py
from .base_contest import BaseContest

class MaratonRadioamatori(BaseContest):
    """
    Regulile Maratonului Radioamatorilor (YP8IC / YR8TGN).
    
    Punctaj:
      - Stație normală:   1 punct per QSO per bandă nouă
      - /IC sau /YR8TGN:  5 puncte per QSO (stație specială)
      - Multiplicatori:   Județe YO noi per bandă
    """

    SPECIAL_STATIONS = ["YP8IC", "YR8TGN"]
    SPECIAL_SUFFIX = "/IC"
    SPECIAL_POINTS = 5
    NORMAL_POINTS = 1

    def get_qso_points(self, qso: dict, log: list) -> int:
        callsign = qso.get("callsign", "").upper()

        # Verifică dacă este stație specială
        is_special = (
            any(s in callsign for s in self.SPECIAL_STATIONS)
            or callsign.endswith(self.SPECIAL_SUFFIX)
        )

        return self.SPECIAL_POINTS if is_special else self.NORMAL_POINTS

    def get_multipliers(self, log: list) -> list:
        """Județe YO unice per bandă."""
        seen = set()
        multipliers = []
        for qso in log:
            key = (qso.get("band"), qso.get("exchange", "").upper())
            if key not in seen:
                seen.add(key)
                multipliers.append(key)
        return multipliers

    def calculate_final_score(self, log: list) -> int:
        total_pts = sum(self.get_qso_points(q, log) for q in log)
        total_mult = len(self.get_multipliers(log))
        return total_pts * total_mult
```

### Fișierul `contests.json` / Contest Definitions

Regulile de bază ale concursurilor pot fi definite și în JSON, fără a modifica codul Python:

```json
{
  "contests": [
    {
      "id": "maraton_yo",
      "name": "Maratonul Radioamatorilor",
      "short_name": "YP8IC",
      "handler": "MaratonRadioamatori",
      "exchange": "county_ro",
      "bands": ["160m", "80m", "40m", "20m", "15m", "10m"],
      "modes": ["SSB", "CW", "Digital"],
      "scoring": {
        "normal_qso": 1,
        "special_station": 5,
        "special_callsigns": ["YP8IC", "YR8TGN"],
        "special_suffixes": ["/IC"],
        "multiplier": "county_per_band"
      }
    }
  ]
}
```

### Build cu PyInstaller / Building with PyInstaller

```bash
# Build simplu
pyinstaller yologpro.spec

# Build manual (cu resurse)
pyinstaller main.py \
  --name "YOLogPRO" \
  --onefile \
  --windowed \
  --add-data "data/contests.json:data" \
  --add-data "ui/themes:ui/themes" \
  --icon assets/icon.ico
```

Executabilul final se găsește în `dist/YOLogPRO.exe`.

### CI/CD cu GitHub Actions / GitHub Actions Build

Fișierul `.github/workflows/build.yml` automatizează build-ul pe toate platformele la fiecare push pe `main` sau la crearea unui tag de release:

```yaml
# .github/workflows/build.yml (fragment)
jobs:
  build:
    strategy:
      matrix:
        os: [windows-latest, ubuntu-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt pyinstaller
      - run: pyinstaller yologpro.spec
      - uses: actions/upload-artifact@v4
        with:
          name: YOLogPRO-${{ matrix.os }}
          path: dist/
```

### Rulare din Sursă / Running from Source

```bash
# Activează mediul virtual
source venv/bin/activate   # Linux/macOS

# Pornește aplicația
python main.py

# Rulează testele
pytest tests/ -v

# Verifică stilul codului
flake8 core/ ui/ contests/
black --check .
```

---

## 🗺️ Roadmap

### v12.1 — Planificat / Planned
- [ ] 🌐 Integrare **QRZ.com API** pentru căutare callsign (înlocuiește simularea actuală)
- [ ] 📡 **CAT Control** — control radio via Hamlib (schimb automat bandă/mod)
- [ ] 🔄 **Sync în cloud** — backup opțional pe Google Drive / Dropbox

### v12.2 — În considerare / Under Consideration
- [ ] 🗣️ **CW Keyer** integrat (via soundcard sau USB keyer)
- [ ] 📊 **Dashboard live** cu grafice animate (QSO/oră, rate, bandmap)
- [ ] 🤝 **Multi-op networking** — logging în rețea pentru stații multi-operator

### v13.0 — Viziune / Vision
- [ ] 🐧 **Portare completă cross-platform** cu UI bazat pe Qt6/PySide6
- [ ] 📱 **Companion app** pentru Android (vizualizare scor live)
- [ ] 🧠 **AI callsign assist** — predicție callsign parțial din baza de date locală

---

## 🤝 Contribuții / Contributing

Contribuțiile sunt binevenite! Te rugăm să:

1. Fork-uiești repository-ul
2. Creezi un branch nou: `git checkout -b feature/NumeleFeaturii`
3. Commit-uiești modificările: `git commit -m 'Add: descriere scurtă'`
4. Push la branch: `git push origin feature/NumeleFeaturii`
5. Deschizi un **Pull Request** cu descriere detaliată

Consultă [CONTRIBUTING.md](CONTRIBUTING.md) pentru ghidul complet de contribuție.

---

## 📄 Licență / License

Distribuit sub licența **MIT**. Vezi [LICENSE](LICENSE) pentru detalii complete.

```
MIT License — Copyright (c) 2024 YO Log PRO Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software...
```

---

## 📬 Contact

| | |
|---|---|
| 📧 **Email** | `yo8xxx@example.com` |
| 🌐 **Website** | `https://yologpro.ro` *(în construcție)* |
| 💬 **Forum YO** | [radioamatori.ro](https://radioamatori.ro) |
| 🐛 **Bug Reports** | [GitHub Issues](https://github.com/youruser/yologpro/issues) |
| 📢 **Anunțuri** | [GitHub Discussions](https://github.com/youruser/yologpro/discussions) |

---

<div align="center">

**73 de YO8XXX** 📻

*Făcut cu ❤️ pentru comunitatea radioamatorilor din România*  
*Made with ❤️ for the Romanian amateur radio community*

[![GitHub Stars](https://img.shields.io/github/stars/youruser/yologpro?style=social)](https://github.com/youruser/yologpro)
[![GitHub Forks](https://img.shields.io/github/forks/youruser/yologpro?style=social)](https://github.com/youruser/yologpro/fork)

</div>
 
