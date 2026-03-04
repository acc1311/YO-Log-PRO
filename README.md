
# 📻 YO Log PRO v14.0 — Multi-Contest Amateur Radio Logger

<p align="center">
  <img src="https://img.shields.io/badge/version-14.0-blue?style=for-the-badge" alt="Version 14.0">
  <img src="https://img.shields.io/badge/python-3.8%2B-green?style=for-the-badge&logo=python" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/license-MIT-orange?style=for-the-badge" alt="MIT License">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey?style=for-the-badge" alt="Platform">
</p>

<p align="center">
  <strong>🇷🇴 Aplicație de logging pentru radioamatori cu manager de concursuri complet configurabil</strong><br>
  <strong>🇬🇧 Amateur radio logging application with fully configurable contest manager</strong>
</p>

---

## 📑 Cuprins / Table of Contents

- [🇷🇴 Descriere](#-descriere)
- [🇬🇧 Description](#-description)
- [📸 Capturi de Ecran / Screenshots](#-capturi-de-ecran--screenshots)
- [⚡ Instalare Rapidă / Quick Install](#-instalare-rapidă--quick-install)
- [🇷🇴 Documentație Română](#-documentație-română)
  - [Funcționalități Principale](#funcționalități-principale)
  - [Manager de Concursuri](#-manager-de-concursuri)
  - [Tipuri de Concurs Disponibile](#-tipuri-de-concurs-disponibile)
  - [Moduri de Punctare](#-moduri-de-punctare)
  - [Sistemul de Multiplicatori](#-sistemul-de-multiplicatori)
  - [Ghid de Utilizare](#-ghid-de-utilizare)
  - [Export Log](#-export-log)
  - [Structura Fișierelor](#-structura-fișierelor)
  - [Configurare Concurs Pas cu Pas](#-configurare-concurs-pas-cu-pas)
- [🇬🇧 English Documentation](#-english-documentation)
  - [Main Features](#main-features)
  - [Contest Manager](#-contest-manager-1)
  - [Available Contest Types](#-available-contest-types)
  - [Scoring Modes](#-scoring-modes)
  - [Multiplier System](#-multiplier-system)
  - [Usage Guide](#-usage-guide)
  - [Log Export](#-log-export)
  - [File Structure](#-file-structure)
  - [Step-by-Step Contest Setup](#-step-by-step-contest-setup)
- [🛠️ Dezvoltare / Development](#️-dezvoltare--development)
- [📋 Changelog](#-changelog)
- [📜 Licență / License](#-licență--license)
- [👤 Contact](#-contact)

---

## 🇷🇴 Descriere

**YO Log PRO v14.0** este o aplicație de logging pentru radioamatori, dezvoltată în Python cu interfață grafică Tkinter. Aplicația oferă un **manager de concursuri complet configurabil**, permițând utilizatorilor să creeze, editeze, duplice și șteargă concursuri cu reguli personalizate de punctare, categorii, benzi, moduri și multiplicatori.

Aplicația este concepută atât pentru operatori experimentați care participă la concursuri naționale și internaționale, cât și pentru începători care doresc un log simplu și intuitiv.

## 🇬🇧 Description

**YO Log PRO v14.0** is an amateur radio logging application developed in Python with a Tkinter graphical interface. The application features a **fully configurable contest manager**, allowing users to create, edit, duplicate and delete contests with custom scoring rules, categories, bands, modes and multipliers.

The application is designed for both experienced operators participating in national and international contests, and beginners who want a simple and intuitive log.

---

## 📸 Capturi de Ecran / Screenshots

```
┌─────────────────────────────────────────────────────────────────────┐
│  ● Online  │ YO8ACR | Maraton [Maraton] | A. Seniori YO | QSO: 47 │
│                                                          [ro] [▼]  │
├─────────────────────────────────────────────────────────────────────┤
│  Indicativ   Bandă  Mod   RST S  RST R  Județ / Notă    [  LOG  ] │
│  [________]  [40m]  [SSB] [59]   [59]   [_________]     [ Reset ] │
│  Dată: [2025-01-15]  Oră: [14:30]  ☐ Manual                       │
│  Categorie: [A. Seniori YO ▼]  Județ: [NT ▼]  [Maraton/maraton]   │
├─────────────────────────────────────────────────────────────────────┤
│  Nr. │ Indicativ │ Bandă │ Mod │ RST S │ RST R │ Notă   │ Puncte  │
│  47  │ YO8ACR    │ 40m   │ SSB │ 59    │ 59    │ NT     │ 1       │
│  46  │ YO3ABC    │ 20m   │ CW  │ 599   │ 599   │ BV     │ 1       │
│  ... │ ...       │ ...   │ ... │ ...   │ ...   │ ...    │ ...     │
├─────────────────────────────────────────────────────────────────────┤
│ [Setări] [🏆Concursuri] [Statistici] [Validează] [Export] [Backup] │
└─────────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Instalare Rapidă / Quick Install

### Cerințe / Requirements

| Component | Versiune / Version |
|-----------|-------------------|
| Python    | 3.8 sau mai nou / 3.8 or newer |
| Tkinter   | Inclus cu Python / Included with Python |
| OS        | Windows, Linux, macOS |

### Instalare / Installation

```bash
# 1. Clonați repository-ul / Clone the repository
git clone https://github.com/yo8acr/yo-log-pro.git
cd yo-log-pro

# 2. Rulați aplicația / Run the application
python yo_log_pro.py

# SAU pe Linux/macOS / OR on Linux/macOS
python3 yo_log_pro.py
```

### Creare Executabil / Create Executable (Windows)

```bash
# Instalați PyInstaller / Install PyInstaller
pip install pyinstaller

# Creați executabilul / Create executable
pyinstaller --onefile --windowed --name "YO_Log_PRO_v14" yo_log_pro.py
```

> **💡 Notă / Note:** Nu sunt necesare dependențe externe — aplicația folosește doar biblioteca standard Python.
> No external dependencies required — the application uses only the Python standard library.

---

# 🇷🇴 Documentație Română

## Funcționalități Principale

### 📻 Logging QSO
- **Înregistrare rapidă** — completați indicativul, banda, modul și apăsați ENTER sau butonul LOG
- **Auto-timestamp** — data și ora UTC se completează automat (mod Online)
- **Mod Manual** — posibilitate de a introduce data și ora manual (mod Offline)
- **Editare QSO** — dublu-click sau click dreapta pe orice QSO pentru editare
- **Ștergere QSO** — cu confirmare, din meniul contextual sau butonul Șterge
- **Numere seriale** — incrementare automată (pentru concursurile care le necesită)

### 🌍 Interfață Bilingvă
- **Română** și **Engleză** — schimbare instantanee din selectorul de limbă
- Interfața se reconstruiește complet la schimbarea limbii
- Toate mesajele, etichetele și dialogurile sunt traduse

### 🎨 Temă Dark Profesională
- Interfață modernă dark cu accent albastru
- Font monospace (Consolas) pentru lizibilitate maximă
- Indicator LED pentru starea Online/Manual
- Bara de informații contextuală cu scor live

---

## 🏆 Manager de Concursuri

Inima aplicației v14.0. Accesibil din:
- **Meniul** `Concursuri → Manager`
- **Butonul** `🏆 Concursuri` din bara de jos

### Operații Disponibile

| Operație | Descriere |
|----------|-----------|
| ➕ **Adaugă** | Creează un concurs nou de la zero |
| ✏️ **Editează** | Modifică regulile unui concurs existent |
| 📋 **Duplică** | Copiază un concurs ca punct de plecare |
| 🗑️ **Șterge** | Elimină un concurs (cu excepția „Log Simplu") |
| 📤 **Exportă** | Salvează toate concursurile ca fișier JSON |
| 📥 **Importă** | Încarcă concursuri din fișier JSON extern |

### Câmpuri Configurabile per Concurs

| Câmp | Tip | Descriere |
|------|-----|-----------|
| **ID Concurs** | text | Identificator unic, fără spații (ex: `yo-dx-hf`) |
| **Nume RO** | text | Numele concursului în limba română |
| **Nume EN** | text | Numele concursului în limba engleză |
| **Tip Concurs** | selector | Categoria generală a concursului |
| **Mod Punctare** | selector | Algoritmul de calcul al scorului |
| **Puncte per QSO** | număr | Punctele de bază pentru fiecare QSO |
| **Minim QSO** | număr | Numărul minim de QSO-uri pentru validare |
| **Multiplicatori** | selector | Tipul de multiplicatori folosiți |
| **Categorii** | text multilinie | Lista categoriilor (una per linie) |
| **Benzi Permise** | checkbox-uri | Benzile pe care se poate opera |
| **Moduri Permise** | checkbox-uri | Modurile de emisie permise |
| **Numere Seriale** | checkbox | Activează câmpurile Nr S / Nr R |
| **Folosește Județ** | checkbox | Activează selectorul de județ |
| **Lista Județe** | text | Județele valide, separate prin virgulă |
| **Stații Obligatorii** | text multilinie | Indicativele care trebuie lucrate |
| **Punctare Specială** | text multilinie | Format: `INDICATIV=PUNCTE` |
| **Puncte per Bandă** | text multilinie | Format: `BANDĂ=PUNCTE` |

---

## 📡 Tipuri de Concurs Disponibile

| Tip | Descriere | Exemplu |
|-----|-----------|---------|
| **Simplu** | Log fără concurs, înregistrare liberă | Log zilnic |
| **Maraton** | Concurs de anduranță cu stații speciale | Maratoane naționale |
| **Ștafetă** | Concurs pe echipe, cu schimb de operatori | Ștafetele regionale |
| **YO** | Concursuri naționale YO | Concursuri FRR |
| **DX** | Concursuri internaționale | YO DX HF Contest |
| **VHF** | Concursuri pe benzi VHF | Contest VHF 2m |
| **UHF** | Concursuri pe benzi UHF | Contest UHF 70cm |
| **Field Day** | Ziua Câmpului — operare portabilă | ARRL Field Day |
| **Sprint** | Concursuri rapide, durată scurtă | Sprint CW |
| **QSO Party** | Concursuri informale pe state/regiuni | YO QSO Party |
| **SOTA** | Summits On The Air | Activări montane |
| **POTA** | Parks On The Air | Activări din parcuri |
| **Custom** | Tip definit de utilizator | Orice regulament |

---

## 🧮 Moduri de Punctare

| Mod | Descriere | Exemplu |
|-----|-----------|---------|
| `none` | Fără punctare — doar logare | Log Simplu |
| `per_qso` | Puncte fixe per QSO | 1 punct/QSO sau 2 puncte/QSO |
| `per_band` | Puncte diferite per bandă | 160m=4p, 80m=3p, 40m=2p |
| `maraton` | Stații speciale cu bonusuri | YP8IC=20p, restul=1p |
| `multiplier` | Puncte QSO × multiplicatori | 150 QSO pts × 23 județe = 3450 |
| `distance` | Bazat pe distanță (VHF/UHF) | km între locatoare |
| `custom` | Formulă personalizată | Utilizator definește regulile |

### Formulă de Calcul Scor

```
Scor Total = Puncte QSO × Multiplicatori

unde:
  Puncte QSO = Σ (puncte per fiecare QSO, conform modului de punctare)
  Multiplicatori = număr unic de entități (județe, DXCC, grid, benzi)
                   sau 1 dacă nu se folosesc multiplicatori
```

---

## 🔢 Sistemul de Multiplicatori

| Tip | Ce se numără | Cum se extrage |
|-----|-------------|----------------|
| **Fără** | Multiplicator = 1 | — |
| **Județe** | Județe unice lucrate | Din câmpul Notă |
| **DXCC** | Prefixe DXCC unice | Din indicativul stației |
| **Bandă** | Benzi unice folosite | Din câmpul Bandă |
| **Grid** | Grid square-uri unice (4 caractere) | Din câmpul Notă |

---

## 📖 Ghid de Utilizare

### Pornire Aplicație

1. Rulați `python yo_log_pro.py`
2. La prima pornire se creează automat:
   - `config.json` — setările stației
   - `log.json` — logul gol
   - `contests.json` — concursurile implicite

### Flux de Lucru Standard

```
1. ⚙️  Configurați stația (Setări → Indicativ, Locator, Județ)
2. 🏆  Selectați sau creați concursul dorit (Concursuri → Manager)
3. 📡  Alegeți categoria din zona de control
4. 📻  Introduceți QSO-uri:
       Indicativ → Bandă → Mod → RST → Notă → ENTER
5. 📊  Verificați statisticile periodic
6. ✅  Validați log-ul înainte de export
7. 💾  Exportați în Cabrillo / ADIF / CSV
8. 🔄  Faceți backup regulat!
```

### Comenzi Rapide

| Tastă / Acțiune | Efect |
|-----------------|-------|
| `ENTER` | Adaugă QSO (când focus pe câmp de intrare) |
| Dublu-click pe QSO | Editează QSO-ul selectat |
| Click dreapta pe QSO | Meniu contextual (Editează / Șterge) |

### Mod Online vs Manual

| Mod | LED | Dată/Oră | Folosire |
|-----|-----|----------|----------|
| **Online** | 🟢 Verde | UTC automat | Operare în timp real |
| **Manual** | 🔴 Roșu | Editabile | Introducere log retrospectiv |

---

## 📤 Export Log

### Cabrillo (.log)
Format standard pentru trimiterea logurilor de concurs. Include header cu informații despre stație și contest, urmat de liniile QSO.

```
START-OF-LOG: 3.0
CONTEST: YO DX HF Contest
CALLSIGN: YO8ACR
LOCATION: KN37
CATEGORY: ALL
QSO:   40m SSB  2025-01-15 14:30 YO8ACR        59  YO3ABC        59
END-OF-LOG:
```

### ADIF (.adi)
Format universal de schimb de date între aplicații de logging.

```
<ADIF_VER:5>3.1.0
<EOH>
<CALL:6>YO3ABC<BAND:3>40m<MODE:3>SSB<QSO_DATE:8>20250115...
```

### CSV (.csv)
Format tabelar, importabil în Excel, Google Sheets sau orice aplicație de calcul tabelar.

```
Nr,Date,Time,Call,Band,Mode,RST_Sent,RST_Rcvd,Note,Score
47,2025-01-15,14:30,YO3ABC,40m,SSB,59,59,NT,1
```

---

## 📁 Structura Fișierelor

```
yo-log-pro/
│
├── yo_log_pro.py          # Codul sursă principal
├── README.md              # Acest fișier
│
├── config.json            # Setările stației (generat automat)
├── log.json               # Log-ul curent (generat automat)
├── contests.json          # Baza de date concursuri (generat automat)
│
├── backups/               # Director backup-uri automate
│   ├── log_backup_20250115_143000.json
│   ├── log_backup_20250115_160000.json
│   └── ...                # Maxim 50 backup-uri, cele mai vechi se șterg
│
├── cabrillo_*.log         # Export-uri Cabrillo
├── adif_*.adi             # Export-uri ADIF
└── log_*.csv              # Export-uri CSV
```

### config.json — Structură

```json
{
  "call": "YO8ACR",
  "loc": "KN37",
  "jud": "NT",
  "addr": "Târgu Neamț",
  "cat": 0,
  "fs": 12,
  "contest": "maraton",
  "county": "NT",
  "lang": "ro",
  "manual_datetime": false
}
```

### contests.json — Structură per Concurs

```json
{
  "yo-dx-hf": {
    "name_ro": "YO DX HF Contest",
    "name_en": "YO DX HF Contest",
    "contest_type": "DX",
    "categories": [
      "A. Single-Op All Band High",
      "B. Single-Op All Band Low"
    ],
    "scoring_mode": "per_band",
    "points_per_qso": 1,
    "min_qso": 0,
    "allowed_bands": ["160m","80m","40m","20m","15m","10m"],
    "allowed_modes": ["SSB", "CW"],
    "required_stations": [],
    "special_scoring": {},
    "use_serial": true,
    "use_county": true,
    "county_list": ["AB","AR","AG","BC","..."],
    "multiplier_type": "dxcc",
    "band_points": {
      "160m": 4, "80m": 3, "40m": 2,
      "20m": 1, "15m": 1, "10m": 2
    }
  }
}
```

---

## 🔧 Configurare Concurs Pas cu Pas

### Exemplu: Crearea unui concurs „Cupa Județului Neamț"

1. **Deschideți** `Concursuri → Manager`
2. **Click** `➕ Adaugă Concurs`
3. **Completați:**

| Câmp | Valoare |
|------|---------|
| ID Concurs | `cupa-neamt` |
| Nume RO | `Cupa Județului Neamț` |
| Nume EN | `Neamț County Cup` |
| Tip Concurs | `YO` |
| Mod Punctare | `per_qso` |
| Puncte per QSO | `2` |
| Minim QSO | `25` |
| Multiplicatori | `county` |
| Categorii | `A. Seniori`<br>`B. Juniori`<br>`C. YL` |
| Benzi | ☑ 80m ☑ 40m ☑ 20m |
| Moduri | ☑ SSB ☑ CW |
| Numere Seriale | ☑ |
| Folosește Județ | ☑ |
| Lista Județe | `NT,IS,BC,SV,BT,VS` |
| Stații Obligatorii | `YP8NT` |
| Punctare Specială | `YP8NT=10` |

4. **Click** `Salvează`
5. **Click** `Salvează` în Manager
6. **Selectați** `cupa-neamt` din selectorul de concurs

---

# 🇬🇧 English Documentation

## Main Features

### 📻 QSO Logging
- **Fast logging** — enter callsign, band, mode and press ENTER or LOG button
- **Auto-timestamp** — UTC date and time filled automatically (Online mode)
- **Manual mode** — option to enter date and time manually (Offline mode)
- **Edit QSO** — double-click or right-click any QSO to edit
- **Delete QSO** — with confirmation, from context menu or Delete button
- **Serial numbers** — auto-increment (for contests that require them)

### 🌍 Bilingual Interface
- **Romanian** and **English** — instant switch from language selector
- Interface completely rebuilds on language change
- All messages, labels and dialogs are translated

### 🎨 Professional Dark Theme
- Modern dark interface with blue accent
- Monospace font (Consolas) for maximum readability
- LED indicator for Online/Manual status
- Contextual info bar with live score

---

## 🏆 Contest Manager

The heart of v14.0. Accessible from:
- **Menu** `Contests → Manager`
- **Button** `🏆 Contests` in the bottom bar

### Available Operations

| Operation | Description |
|-----------|-------------|
| ➕ **Add** | Create a new contest from scratch |
| ✏️ **Edit** | Modify an existing contest's rules |
| 📋 **Duplicate** | Copy a contest as starting point |
| 🗑️ **Delete** | Remove a contest (except "Simple Log") |
| 📤 **Export** | Save all contests as JSON file |
| 📥 **Import** | Load contests from external JSON file |

### Configurable Fields per Contest

| Field | Type | Description |
|-------|------|-------------|
| **Contest ID** | text | Unique identifier, no spaces (e.g. `yo-dx-hf`) |
| **Name RO** | text | Contest name in Romanian |
| **Name EN** | text | Contest name in English |
| **Contest Type** | selector | General contest category |
| **Scoring Mode** | selector | Score calculation algorithm |
| **Points per QSO** | number | Base points for each QSO |
| **Min QSO** | number | Minimum QSOs for validation |
| **Multipliers** | selector | Type of multipliers used |
| **Categories** | multiline text | List of categories (one per line) |
| **Allowed Bands** | checkboxes | Bands that can be operated |
| **Allowed Modes** | checkboxes | Permitted emission modes |
| **Serial Numbers** | checkbox | Enable Nr S / Nr R fields |
| **Use County** | checkbox | Enable county selector |
| **County List** | text | Valid counties, comma-separated |
| **Required Stations** | multiline text | Callsigns that must be worked |
| **Special Scoring** | multiline text | Format: `CALLSIGN=POINTS` |
| **Band Points** | multiline text | Format: `BAND=POINTS` |

---

## 📡 Available Contest Types

| Type | Description | Example |
|------|-------------|---------|
| **Simplu** | No contest, free logging | Daily log |
| **Maraton** | Endurance contest with special stations | National marathons |
| **Stafeta** | Team contest, operator relay | Regional relays |
| **YO** | YO national contests | FRR contests |
| **DX** | International contests | YO DX HF Contest |
| **VHF** | VHF band contests | VHF 2m Contest |
| **UHF** | UHF band contests | UHF 70cm Contest |
| **Field Day** | Portable operation | ARRL Field Day |
| **Sprint** | Quick, short-duration contests | CW Sprint |
| **QSO Party** | Informal state/region contests | YO QSO Party |
| **SOTA** | Summits On The Air | Mountain activations |
| **POTA** | Parks On The Air | Park activations |
| **Custom** | User-defined type | Any ruleset |

---

## 🧮 Scoring Modes

| Mode | Description | Example |
|------|-------------|---------|
| `none` | No scoring — logging only | Simple Log |
| `per_qso` | Fixed points per QSO | 1 pt/QSO or 2 pts/QSO |
| `per_band` | Different points per band | 160m=4pts, 80m=3pts, 40m=2pts |
| `maraton` | Special stations with bonuses | YP8IC=20pts, others=1pt |
| `multiplier` | QSO points × multipliers | 150 QSO pts × 23 counties = 3450 |
| `distance` | Distance-based (VHF/UHF) | km between locators |
| `custom` | Custom formula | User defines rules |

### Score Calculation Formula

```
Total Score = QSO Points × Multipliers

where:
  QSO Points = Σ (points for each QSO, per scoring mode)
  Multipliers = unique entity count (counties, DXCC, grid, bands)
                or 1 if no multipliers are used
```

---

## 🔢 Multiplier System

| Type | What is Counted | How it's Extracted |
|------|-----------------|-------------------|
| **None** | Multiplier = 1 | — |
| **Counties** | Unique counties worked | From Note field |
| **DXCC** | Unique DXCC prefixes | From station callsign |
| **Band** | Unique bands used | From Band field |
| **Grid** | Unique grid squares (4 chars) | From Note field |

---

## 📖 Usage Guide

### Starting the Application

1. Run `python yo_log_pro.py`
2. On first start, these files are auto-created:
   - `config.json` — station settings
   - `log.json` — empty log
   - `contests.json` — default contests

### Standard Workflow

```
1. ⚙️  Configure station (Settings → Callsign, Locator, County)
2. 🏆  Select or create contest (Contests → Manager)
3. 📡  Choose category from control area
4. 📻  Enter QSOs:
       Callsign → Band → Mode → RST → Note → ENTER
5. 📊  Check statistics periodically
6. ✅  Validate log before export
7. 💾  Export to Cabrillo / ADIF / CSV
8. 🔄  Backup regularly!
```

### Keyboard Shortcuts

| Key / Action | Effect |
|-------------|--------|
| `ENTER` | Add QSO (when focus on input field) |
| Double-click on QSO | Edit selected QSO |
| Right-click on QSO | Context menu (Edit / Delete) |

### Online vs Manual Mode

| Mode | LED | Date/Time | Usage |
|------|-----|-----------|-------|
| **Online** | 🟢 Green | Auto UTC | Real-time operation |
| **Manual** | 🔴 Red | Editable | Retrospective log entry |

---

## 📤 Log Export

### Cabrillo (.log)
Standard format for submitting contest logs. Includes header with station and contest info, followed by QSO lines.

### ADIF (.adi)
Universal data exchange format between logging applications. Compatible with LoTW, eQSL, Club Log, QRZ.com and others.

### CSV (.csv)
Tabular format, importable in Excel, Google Sheets or any spreadsheet application. Includes QSO number, score column and serial numbers when applicable.

---

## 📁 File Structure

```
yo-log-pro/
│
├── yo_log_pro.py          # Main source code
├── README.md              # This file
│
├── config.json            # Station settings (auto-generated)
├── log.json               # Current log (auto-generated)
├── contests.json          # Contest database (auto-generated)
│
├── backups/               # Auto-backup directory
│   ├── log_backup_20250115_143000.json
│   └── ...                # Max 50 backups, oldest are deleted
│
├── cabrillo_*.log         # Cabrillo exports
├── adif_*.adi             # ADIF exports
└── log_*.csv              # CSV exports
```

---

## 🔧 Step-by-Step Contest Setup

### Example: Creating a "Field Day Romania" contest

1. **Open** `Contests → Manager`
2. **Click** `➕ Add Contest`
3. **Fill in:**

| Field | Value |
|-------|-------|
| Contest ID | `field-day-ro` |
| Name RO | `Ziua Câmpului România` |
| Name EN | `Field Day Romania` |
| Contest Type | `Field Day` |
| Scoring Mode | `per_qso` |
| Points per QSO | `2` |
| Min QSO | `0` |
| Multipliers | `none` |
| Categories | `A. 1 Operator`<br>`B. 2 Operators`<br>`C. Club` |
| Bands | ☑ All bands |
| Modes | ☑ All modes |
| Serial Numbers | ☐ |
| Use County | ☐ |

4. **Click** `Save`
5. **Click** `Save` in Manager
6. **Select** `field-day-ro` from contest selector

---

# 🛠️ Dezvoltare / Development

### Tehnologii / Technologies

| Component | Tehnologie / Technology |
|-----------|------------------------|
| Limbaj / Language | Python 3.8+ |
| GUI | Tkinter (built-in) |
| Date / Data | JSON |
| Distribuție / Distribution | PyInstaller (opțional) |

### Arhitectura / Architecture

```
┌─────────────────────────────────────────────┐
│                RadioLogApp                   │
│              (Main Window)                   │
├──────────┬──────────┬──────────┬────────────┤
│  Header  │  Input   │  Log     │  Button    │
│  Bar     │  Area    │  View    │  Bar       │
├──────────┴──────────┴──────────┴────────────┤
│                                              │
│  ┌──────────────┐  ┌────────────────────┐   │
│  │ DataManager   │  │  ScoringEngine     │   │
│  │ (JSON I/O)    │  │  (Score Calc)      │   │
│  └──────────────┘  └────────────────────┘   │
│                                              │
│  ┌──────────────┐  ┌────────────────────┐   │
│  │ Lang          │  │  ContestManager    │   │
│  │ (i18n)        │  │  (CRUD Dialogs)    │   │
│  └──────────────┘  └────────────────────┘   │
│                                              │
│  ┌──────────────────────────────────────┐   │
│  │         ContestEditorDialog           │   │
│  │   (Full contest configuration UI)     │   │
│  └──────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

### Clase Principale / Main Classes

| Clasă / Class | Responsabilitate / Responsibility |
|---------------|-----------------------------------|
| `RadioLogApp` | Fereastra principală, UI, logica aplicației / Main window, UI, app logic |
| `DataManager` | Persistența datelor JSON, backup-uri / JSON data persistence, backups |
| `ScoringEngine` | Calcul punctaje, validare, multiplicatori / Score calculation, validation, multipliers |
| `Lang` | Managementul limbilor (RO/EN) / Language management (RO/EN) |
| `ContestManagerDialog` | CRUD pentru concursuri / Contest CRUD operations |
| `ContestEditorDialog` | Formular complet de editare concurs / Full contest edit form |

### Contribuții / Contributing

1. Fork repository-ul / Fork the repository
2. Creați un branch: `git checkout -b feature/noua-functionalitate`
3. Commit: `git commit -m "Adaugă funcționalitate nouă"`
4. Push: `git push origin feature/noua-functionalitate`
5. Deschideți un Pull Request

---

## 📋 Changelog

### v14.0 (2026)
- ✅ **Manager de Concursuri** complet configurabil (adaugă/editează/duplică/șterge)
- ✅ **12 tipuri de concurs**: Simplu, Maraton, Ștafetă, YO, DX, VHF, UHF, Field Day, Sprint, QSO Party, SOTA, POTA, Custom
- ✅ **7 moduri de punctare**: none, per_qso, per_band, maraton, multiplier, distance, custom
- ✅ **5 tipuri de multiplicatori**: Fără, Județe, DXCC, Bandă, Grid
- ✅ **Import/Export** concursuri JSON
- ✅ **UI adaptiv** — benzi, moduri, coloane, câmpuri se ajustează per concurs
- ✅ **Numere seriale** opționale per concurs
- ✅ **Coloana Scor** dinamică în treeview
- ✅ **Coloana Nr.** pentru numerotare QSO-uri
- ✅ Eliminat concursurile hardcodate
- ✅ Concursul „Log Simplu" protejat ca fallback

### v13.0 (2026)
- Manager multi-contest cu concursuri predefinite
- Export Cabrillo / ADIF / CSV
- Validare log per concurs
- Interfață bilingvă RO/EN
- Temă dark profesională
- Sistem de backup automat

---

## 📜 Licență / License

Acest proiect este distribuit sub **Licența MIT**.
This project is distributed under the **MIT License**.

```
MIT License

Copyright (c) 2026 Ardei Constantin-Cătălin (YO8ACR)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

---

## 👤 Contact

| | |
|---|---|
| **Dezvoltator / Developer** | Ardei Constantin-Cătălin |
| **Indicativ / Callsign** | **YO8ACR** |
| **Email** | yo8acr@gmail.com |
| **Locator** | KN37 |
| **QTH** | Neamț, România |

---

<p align="center">
  <strong>73 de YO8ACR! 📻</strong><br>
  <em>„Radioamatorismul — hobby-ul care conectează lumea"</em><br>
  <em>"Amateur Radio — the hobby that connects the world"</em>
</p>
```

---
