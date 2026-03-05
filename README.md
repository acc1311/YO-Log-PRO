
# 📻 YO Log PRO v16.2 FINAL — Professional Multi-Contest Amateur Radio Logger
"""
YO Log PRO v16.1 FINAL — Professional Multi-Contest Amateur Radio Logger
Developed by: Ardei Constantin-Cătălin (YO8ACR)
Email: yo8acr@gmail.com

FIXES v16.2:
- FIXED: 'dict' object has no attribute 'insert' — DM.load() returned {} instead of []
- FIXED: All popup dialogs now center on parent window
- ContestEditor: fields for categories, bands, modes, required_stations, special_scoring, band_points, county_list fully editable
- ContestMgr: Duplicate + Export + Import buttons added
- Stats window: full detailed stats (bands, modes, DXCC, worked-all, operating time, rate)
- Cabrillo export: full 3.0 header with CONTEST, CATEGORY-*, NAME, ADDRESS, SOAPBOX
- ADIF export: FREQ in MHz, GRIDSQUARE, MY_GRIDSQUARE, STX, SRX
- EDI export: added
- Print text export: added
- Validate: improved messages, checks forbidden bands/modes
- Score label: shows Σ QSO×MULT=TOTAL format
- Worked-before indicator: shows worked other band/mode in yellow
- Search dialog: Ctrl+F, live filter
- Timer dialog: contest countdown
- Hash verify: MD5 check
- Sound: beep on new multiplier, duplicate
- Settings: addr, font size, sounds checkbox
- Config: category/county save button fixed
- Rate meter: QSO/h live
- Geometry save/restore
- Scrollbar on ContestEditor (tall form)
- Auto-RST on band change fix
- Clear log with backup
"""
<p align="center">
  <img src="https://img.shields.io/badge/version-16.2_FINAL-blue?style=for-the-badge" alt="Version">
  <img src="https://img.shields.io/badge/python-3.8%2B-green?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-orange?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey?style=for-the-badge" alt="Platform">
  <img src="https://img.shields.io/badge/dependencies-ZERO-brightgreen?style=for-the-badge" alt="Dependencies">
</p>

<p align="center">
  <strong>🇷🇴 Aplicație profesională definitivă de logging pentru radioamatori</strong><br>
  <strong>🇬🇧 Definitive professional amateur radio logging application</strong>
</p>

---

## 📑 Cuprins / Table of Contents

- [🇷🇴 Documentație Română](#-documentație-română)
  - [Descriere și Funcționalități](#-descriere-și-funcționalități)
  - [IMPORTANT: Regula Folderului](#-important-regula-folderului-dedicat)
  - [Instalare și Prima Pornire](#-instalare-și-prima-pornire)
  - [Configurare Inițială](#️-configurare-inițială)
  - [Logare QSO-uri](#-logare-qso-uri)
  - [Manager de Concursuri](#-manager-de-concursuri)
  - [Tipuri de Concurs și Punctare](#-tipuri-de-concurs-și-punctare)
  - [Căutare, Filtrare, Sortare](#-căutare-filtrare-sortare)
  - [Import Log](#-import-log)
  - [Export Log](#-export-log)
  - [Statistici și Validare](#-statistici-și-validare)
  - [Backup și Restaurare](#-backup-și-restaurare)
  - [Scurtături Tastatură](#-scurtături-tastatură)
  - [Structura Folderului](#-structura-completă-a-folderului)
  - [Reguli și Sfaturi](#-reguli-și-sfaturi)
  - [Depanare](#-depanare)
  - [Checklist Prima Utilizare](#-checklist-prima-utilizare)
- [🇬🇧 English Documentation](#-english-documentation)
  - [Description and Features](#-description-and-features)
  - [IMPORTANT: Dedicated Folder Rule](#-important-dedicated-folder-rule)
  - [Installation and First Run](#-installation-and-first-run)
  - [Initial Setup](#️-initial-setup)
  - [QSO Logging](#-qso-logging)
  - [Contest Manager](#-contest-manager)
  - [Contest Types and Scoring](#-contest-types-and-scoring)
  - [Search, Filter, Sort](#-search-filter-sort)
  - [Log Import](#-log-import)
  - [Log Export](#-log-export)
  - [Statistics and Validation](#-statistics-and-validation)
  - [Backup and Restore](#-backup-and-restore)
  - [Keyboard Shortcuts](#-keyboard-shortcuts)
  - [Folder Structure](#-complete-folder-structure)
  - [Rules and Tips](#-rules-and-tips)
  - [Troubleshooting](#-troubleshooting)
  - [First Use Checklist](#-first-use-checklist)
- [🔧 Secțiune Tehnică / Technical Section](#-secțiune-tehnică--technical-section)
  - [Arhitectura](#️-arhitectura--architecture)
  - [Structura JSON](#-structura-json--json-structure)
  - [Creare Executabil](#-creare-executabil--build-executable)
  - [Changelog](#-changelog)
  - [Licență / License](#-licență--license)
  - [Contact](#-contact)

---

# 🇷🇴 Documentație Română

## 📋 Descriere și Funcționalități

**YO Log PRO v16.0 FINAL** este versiunea definitivă a aplicației de logging pentru radioamatori. Zero dependențe externe — doar Python standard. Un singur fișier, gata de producție.

### Ce Conține

| Categorie | Funcționalități |
|-----------|----------------|
| **Core** | Log separat per concurs, auto-save la 60s, backup automat la ieșire |
| **Input** | Câmp frecvență cu auto-detecție bandă, auto-RST per mod (59/599/-10), indicator „Worked Before" live |
| **Tabel** | Colorare duplicate (roșu) / stații speciale (albastru), sortare pe coloane, filtre bandă/mod, coloana Țară + km |
| **Tastatură** | Ctrl+F, Ctrl+Z, Ctrl+S, F2=bandă următoare, F3=mod următor, Enter=LOG |
| **Concursuri** | Manager complet (adaugă/editează/duplică/șterge/import/export), 7 predefinite, 13 tipuri, 7 moduri punctare |
| **Punctare** | per_qso, per_band, maraton, multiplier, distance (Haversine real), custom |
| **Multiplicatori** | Județe (regex exact), DXCC (150+ prefixe), Bandă, Grid Square, Worked-All tracker |
| **Export** | Cabrillo 3.0 complet, ADIF 3.1 (frecvență MHz), CSV (escaped), EDI (VHF/UHF) |
| **Import** | ADIF (.adi/.adif) + CSV — parsare robustă |
| **Statistici** | Fereastră dedicată: bandă/mod/DXCC/județe/worked-all/timp operare/rată |
| **Validare** | Min QSO, stații obligatorii, benzi/moduri interzise, duplicate |
| **Utilități** | Timer concurs (countdown), căutare live, undo 50 operații, print text, verificare hash MD5 |
| **UI** | Ceas UTC live, rate meter QSO/h, temă dark profesională, geometry salvată |
| **Sunet** | Beep la duplicat, multiplicator nou, save, erori (Windows) |
| **i18n** | Română + Engleză complet, switch instant |
| **DXCC** | Bază de date integrată 150+ prefixe cu lookup automat |
| **Locator** | Calcul distanță Haversine între locatoare Maidenhead |

### Captură de Ecran

```
┌───────────────────────────────────────────────────────────────────────┐
│ ●Online UTC │ YO8ACR | Maraton | A.Seniori | QSO:47  ⚡12QSO/h  UTC│
│                                              [ro▼] [maraton▼] 14:32 │
├───────────────────────────────────────────────────────────────────────┤
│ Indicativ  Frecv   Bandă Mod  RST S RST R Nr S Nr R Județ/Notă     │
│ [YO3ABC ] [14200] [20m▼][SSB▼][59]  [59]  [48] [__] [BV____]      │
│ ⚠ DUP 20m/SSB                          ☐Manual [LOG] [Reset]       │
│ Dată:[2026-01-15] Oră:[14:32]  Cat:[A.Seniori▼] Jud:[NT▼] 💾      │
│ Bandă:[Toate▼]  Mod:[Toate▼]                        Σ 123×18=2214  │
├───────────────────────────────────────────────────────────────────────┤
│ Nr│Indicativ│Frecv │Bandă│Mod│RS│RR│SS│SR│Notă│Țara    │Data │Ora│Pt│
│ 47│YO3ABC   │14200 │20m  │SSB│59│59│48│23│BV  │Romania │01-15│14 │1 │
│ 46│DL1ABC   │ 7100 │40m  │CW │599│599│47│  │  │Germany │01-15│14 │2 │
│ 45│YO3ABC   │ 7100 │40m  │SSB│59│59│46│22│BV  │Romania │01-15│13 │1 │ ← roșu (dup)
│ ..│...      │      │     │   │  │  │  │  │    │        │     │   │  │
├───────────────────────────────────────────────────────────────────────┤
│[⚙Setări][🏆Concurs][🔍Caută][⏱Timer][📊Stats][✅Valid][📤Exp][📥Imp]│
└───────────────────────────────────────────────────────────────────────┘
```

---

## 🚨 IMPORTANT: Regula Folderului Dedicat

```
╔════════════════════════════════════════════════════════════════════════╗
║                                                                        ║
║   EXECUTABILUL CREEAZĂ FIȘIERE ÎN FOLDERUL ÎN CARE SE AFLĂ!          ║
║                                                                        ║
║   ❌  NU rulați din arhivă (ZIP/RAR)                                   ║
║   ❌  NU mutați exe-ul fără fișierele JSON                             ║
║   ❌  NU puneți în C:\Program Files\                                   ║
║   ✅  Extrageți într-un folder dedicat ÎNAINTE de prima rulare         ║
║   ✅  Shortcut pe Desktop — mutați doar shortcut-ul                    ║
║   ✅  Dacă mutați, mutați TOT: exe + JSON + backups\                  ║
║                                                                        ║
╚════════════════════════════════════════════════════════════════════════╝
```

---

## 📥 Instalare și Prima Pornire

### Cerințe

| Component | Cerință |
|-----------|---------|
| Python | 3.8+ (doar pentru .py) |
| Tkinter | Inclus cu Python |
| OS | Windows 7+, Linux, macOS |
| .exe | NU necesită Python |
| Dependențe | **ZERO** — doar biblioteca standard |

### Instalare

```bash
# 1. Creați folder dedicat
mkdir C:\RadioLog
# sau: mkdir ~/RadioLog

# 2. Copiați executabilul sau scriptul în folder

# 3. Rulați
python yo_log_pro.py          # Windows
python3 yo_log_pro.py         # Linux/macOS
# SAU dublu-click pe .exe     # Windows
```

### Fișiere Create Automat la Prima Pornire

```
📁 C:\RadioLog\
├── yo_log_pro.exe              ← executabilul (existent)
├── config.json                  ← ⚡ setările stației
├── contests.json                ← ⚡ 7 concursuri predefinite
└── log_simplu.json              ← ⚡ logul gol pentru concursul implicit
```

---

## ⚙️ Configurare Inițială

### Pas 1 — Setări Stație (OBLIGATORIU)

Click **[⚙ Setări]** → completați:

| Câmp | Exemplu | Utilizare |
|------|---------|-----------|
| **Indicativ** | `YO8XYZ` | Header, export Cabrillo/ADIF |
| **Locator** | `KN37` | Calcul distanță VHF/UHF, ADIF |
| **Județ** | `NT` | Concursuri cu județe |
| **Adresă** | `Târgu Neamț` | Cabrillo |
| **Operator** | `Nume Prenume` | Cabrillo header |
| **Putere (W)** | `100` | Cabrillo header |
| **Font** | `11` | 10-14 recomandat |
| **Sunete** | ☑ | Beep la duplicate/multiplicatori |

### Pas 2 — Selectare Limbă

Colțul dreapta sus: `[ro▼]` sau `[en▼]` — interfața se reconstruiește instant.

### Pas 3 — Selectare Concurs

Dropdown din header: `[simplu▼]` → alegeți concursul.

La schimbarea concursului:
- Se încarcă logul separat al concursului
- Benzile/modurile se filtrează automat
- Câmpurile seriale apar/dispar
- RST-urile se ajustează automat per mod
- Coloana Puncte/km apare/dispare

### Pas 4 — Categorie și Județ

În zona de control: `Categorie: [▼]  Județ: [▼]  [💾]`

**Click [💾] pentru a salva** — OBLIGATORIU.

---

## 📻 Logare QSO-uri

### Câmpuri

| Câmp | Obligatoriu | Auto | Descriere |
|------|:-----------:|:----:|-----------|
| **Indicativ** | ✅ | | Stația lucrată |
| **Frecvență** | | | kHz — detectează banda automat |
| **Bandă** | ✅ | Din frecvență | Sau selecție manuală |
| **Mod** | ✅ | | SSB/CW/FT8/etc. |
| **RST S/R** | | ✅ | Auto per mod: SSB→59, CW→599, FT8→-10 |
| **Nr S** | * | ✅ | Auto-increment (dacă concursul folosește) |
| **Nr R** | * | | Serial primit |
| **Notă** | | | Județ / Locator / Comentariu |
| **Dată/Oră** | | ✅ | UTC automat (mod Online) |

### Flux Rapid

```
1. Tastați indicativul → YO3ABC
   (indicator live: ⚠ DUP sau ℹ Lucrat alt QRG sau gol)
2. Tastați frecvența → 14250
   (banda se setează automat pe 20m)
3. ENTER
✅ QSO logat! Cursor revine pe Indicativ. Serial incrementat.
```

### Indicator „Worked Before"

Sub câmpul indicativ apare live:
- **⚠ DUP 20m/SSB** (roșu) — duplicat exact pe aceeași bandă/mod
- **ℹ Lucrat alt QRG** (galben) — lucrat pe altă bandă/mod
- **(gol)** — stație nouă

La duplicate, apare dialog de confirmare cu beep.

### Auto-RST per Mod

| Mod | RST implicit |
|-----|-------------|
| SSB, AM, FM | 59 |
| CW, RTTY, DIGI, PSK31 | 599 |
| FT8, FT4 | -10 |
| JT65 | -15 |

Se ajustează automat la schimbarea modului (F3).

### Mod Online vs Manual

| Mod | LED | Dată/Oră | Utilizare |
|-----|-----|----------|-----------|
| **Online** ☐ | 🟢 | UTC automat, blocate | Operare live |
| **Manual** ☑ | 🔴 | Editabile YYYY-MM-DD / HH:MM | Retrospectiv |

---

## 🏆 Manager de Concursuri

### Deschidere

- Meniu: `Concursuri → Manager`
- Buton: `🏆 Concursuri`
- Switch rapid: `Concursuri → ⚡ Switch → [concurs]`

### Operații

| Buton | Acțiune |
|-------|---------|
| ➕ Adaugă | Concurs nou de la zero |
| ✏ Editează | Modifică regulile (sau dublu-click) |
| 📋 Duplică | Copiază ca bază pentru altul |
| 🗑 Șterge | Elimină (excepție: Log Simplu) |
| 📤 Exportă | Toate concursurile → JSON |
| 📥 Importă | Din JSON extern |

### Câmpuri per Concurs

| Câmp | Descriere | Exemplu |
|------|-----------|---------|
| **ID** | Unic, fără spații | `cupa-neamt` |
| **Nume RO/EN** | Afișat bilingv | `Cupa Neamț` |
| **Tip** | 13 tipuri disponibile | `YO` |
| **Punctare** | 7 moduri | `per_qso` |
| **Puncte/QSO** | Baza de puncte | `2` |
| **Min QSO** | Prag validare | `25` |
| **Multiplicatori** | 5 tipuri | `county` |
| **Categorii** | Una per linie | `A. Seniori` |
| **Benzi** | Checkbox-uri | ☑80m ☑40m |
| **Moduri** | Checkbox-uri | ☑SSB ☑CW |
| **Nr. Seriale** | On/Off | ☑ |
| **Județ** | On/Off + listă | ☑ + `NT,IS,BC` |
| **Stații obligatorii** | Una per linie | `YP8NT` |
| **Punctare specială** | `CALL=PUNCTE` | `YP8NT=10` |
| **Puncte/Bandă** | `BANDĂ=PUNCTE` | `160m=4` |

### ⚠ Salvare

```
1. [Salvează] în Editorul concursului
2. [Salvează] în fereastra Manager
Dacă închideți Managerul fără [Salvează], modificările se pierd!
```

### Concursuri Predefinite

| ID | Tip | Punctare | Min QSO | Seriale | Județ | Mult |
|----|-----|----------|---------|---------|-------|------|
| `simplu` | Simplu | none | 0 | ☐ | ☐ | — |
| `maraton` | Maraton | maraton | 100 | ☐ | ☑ | county |
| `stafeta` | Ștafetă | per_qso | 50 | ☑ | ☑ | county |
| `yo-dx-hf` | DX | per_band | 0 | ☑ | ☑ | dxcc |
| `yo-vhf` | VHF | distance | 0 | ☑ | ☐ | grid |
| `field-day` | Field Day | per_qso (×2) | 0 | ☐ | ☐ | — |
| `sprint` | Sprint | per_qso | 0 | ☑ | ☐ | — |

---

## 📡 Tipuri de Concurs și Punctare

### 13 Tipuri de Concurs

| Tip | Descriere |
|-----|-----------|
| **Simplu** | Log liber, fără reguli |
| **Maraton** | Anduranță, stații speciale cu bonusuri |
| **Ștafetă** | Echipe, schimb operatori |
| **YO** | Concursuri naționale |
| **DX** | Concursuri internaționale |
| **VHF** | Benzi VHF (2m, 6m) |
| **UHF** | Benzi UHF (70cm, 23cm) |
| **Field Day** | Operare portabilă |
| **Sprint** | Concurs rapid, durată scurtă |
| **QSO Party** | Concursuri informale |
| **SOTA** | Summits On The Air |
| **POTA** | Parks On The Air |
| **Custom** | Orice regulament |

### 7 Moduri de Punctare

| Mod | Descriere | Exemplu |
|-----|-----------|---------|
| `none` | Fără punctare | Log Simplu |
| `per_qso` | Puncte fixe | 2 pt/QSO |
| `per_band` | Puncte per bandă | 160m=4, 80m=3, 40m=2 |
| `maraton` | Stații speciale + normal | YP8IC=20, rest=1 |
| `multiplier` | QSO × multiplicatori | 150×23=3450 |
| `distance` | km Haversine (VHF/UHF) | 523 km |
| `custom` | Personalizat | Puncte/QSO configurabile |

### 5 Tipuri de Multiplicatori

| Tip | Sursă | Notă |
|-----|-------|------|
| **none** | Mult = 1 | — |
| **county** | Câmpul Notă | Regex word boundary (nu match parțial) |
| **dxcc** | Indicativ | 150+ prefixe integrate |
| **band** | Câmpul Bandă | Benzi unice |
| **grid** | Câmpul Notă | Grid square 4 char |

### Formulă Scor

```
Scor Total = Σ(Puncte QSO) × Multiplicatori
```

Afișat live în header: `Σ 123×18=2214`

---

## 🔍 Căutare, Filtrare, Sortare

### Căutare (Ctrl+F)

Dialog cu filtru live — tastați și rezultatele apar instant. Caută în indicativ și notă.

### Filtre

Deasupra tabelului: `Bandă: [Toate▼]  Mod: [Toate▼]`

Selectați o bandă/mod specific pentru a filtra tabelul. Nu afectează logul, doar vizualizarea.

### Sortare

Click pe orice header de coloană = sortare ascendentă/descendentă. Click din nou = inversare.

---

## 📥 Import Log

### Din meniu: `🛠 → Import ADIF` sau `Import CSV`
### Din buton: `[📥 Import]`

### ADIF (.adi / .adif)

Parsare robustă cu suport pentru:
- Toate câmpurile standard: CALL, BAND, MODE, QSO_DATE, TIME_ON, RST_SENT, RST_RCVD
- Câmpuri opționale: FREQ, GRIDSQUARE, COMMENT, STX, SRX
- Gestionare EOH/EOR

### CSV (.csv)

Acceptă coloane cu nume variate:
- `Call` / `CALL` / `call` / `Callsign`
- `Band` / `BAND` / `Mode` / `MODE`
- `Date` / `DATE` / `Time` / `TIME`
- `RST_Sent` / `RST_S` / `Note` / `Comment`

QSO-urile importate se adaugă la logul curent al concursului activ.

---

## 📤 Export Log

Click **[📤 Export]** → alegeți formatul:

### Cabrillo 3.0 (.log)

Header complet incluzând:
- `CONTEST`, `CALLSIGN`, `GRID-LOCATOR`
- `CATEGORY-OPERATOR`, `CATEGORY-BAND`, `CATEGORY-POWER`, `CATEGORY-MODE`
- `CREATED-BY: YO Log PRO v16.0 FINAL`
- `NAME`, `ADDRESS`, `SOAPBOX`
- Frecvență per QSO (din câmpul freq sau default din bandă)

### ADIF 3.1 (.adi)

- Frecvență în **MHz** (standard ADIF)
- `PROGRAMID`, `PROGRAMVERSION`
- `GRIDSQUARE` pentru note care sunt locatoare valide
- `MY_GRIDSQUARE` din setările stației
- `STX`, `SRX` pentru seriale

### CSV (.csv)

- Export cu `csv.writer` (escapare corectă a virgulelor)
- Include Nr, Date, Time, Call, Freq, Band, Mode, RST, Seriale, Note, Country, Score

### EDI (.edi)

- Format standard VHF/UHF european
- `[REG1TEST;1]` header complet
- Distanță km calculată automat din locatoare

### Print Text (.txt)

Meniu `🛠 → 🖨 Print` — generează fișier text formatat tabelar pentru printare.

---

## 📊 Statistici și Validare

### Statistici (fereastră dedicată)

Click **[📊 Stats]** → fereastră cu text colorat:

- **Total QSO** și **Stații unice**
- **Rezumat pe Benzi** — tabel cu QSO, Puncte, Unice per bandă
- **Rezumat pe Moduri**
- **Stații Obligatorii** — ✓ verde / ✗ roșu
- **Scor** — QSO Points, Multiplicatori, Total
- **Worked-All Tracker** — câte județe/DXCC lucrate din total, lista celor lipsă
- **DXCC Summary** — top 20 țări lucrate
- **Timp Operare** — span, first/last QSO, rată medie QSO/h

### Validare

Click **[✅ Valid]** → verifică:

| Verificare | Descriere |
|-----------|-----------|
| Log gol | Eroare dacă 0 QSO |
| Min QSO | Compară cu pragul concursului |
| Stații obligatorii | Listează cele lipsă |
| Benzi interzise | Semnalează QSO-uri pe benzi nepermise |
| Moduri interzise | Semnalează QSO-uri cu moduri nepermise |
| Duplicate | Contorizează și avertizează |
| Diplomă | Eligibilitate DA/NU |

### Verificare Hash

Meniu `🛠 → Verificare Log` — calculează hash MD5 al logului pentru integritate.

---

## 💾 Backup și Restaurare

### Backup Automat

La **fiecare ieșire** din aplicație (cu confirmare salvare) se creează backup automat.

### Backup Manual

Click **[💾 Backup]** — backup instant.

### Locație

```
📁 backups\
├── log_simplu_20260115_143000.json
├── log_maraton_20260115_160000.json
└── ...  (max 50 per concurs, cele vechi se șterg)
```

### Auto-Save

Logul se salvează automat la **fiecare 60 secunde** + la fiecare QSO adăugat/șters.

### Restaurare

1. Închideți aplicația
2. Mergeți în `backups\`
3. Copiați `log_CONCURS_TIMESTAMP.json` → redenumiți în `log_CONCURS.json`
4. Reporniți

---

## ⌨ Scurtături Tastatură

| Scurtătură | Acțiune |
|-----------|---------|
| `Enter` | Adaugă QSO (când focus pe Entry) |
| `Ctrl+F` | Deschide căutare |
| `Ctrl+Z` | Undo ultima operație |
| `Ctrl+S` | Salvare forțată (log + config) |
| `F2` | Ciclează banda următoare |
| `F3` | Ciclează modul următor (+ auto-RST) |
| `Dublu-click` pe QSO | Editează |
| `Click dreapta` pe QSO | Meniu contextual |

---

## 📁 Structura Completă a Folderului

```
📁 C:\RadioLog\
│
│── FIȘIERE PRINCIPALE ──────────────────────────
├── yo_log_pro.exe                ← executabilul (NU se mută!)
├── config.json                    ← setări stație + preferințe
├── contests.json                  ← concursuri configurate
│
│── LOG-URI SEPARATE PER CONCURS ────────────────
├── log_simplu.json                ← QSO-uri „Log Simplu"
├── log_maraton.json               ← QSO-uri „Maraton"
├── log_stafeta.json               ← QSO-uri „Ștafetă"
├── log_yo-dx-hf.json              ← QSO-uri „YO DX HF"
├── log_cupa-neamt.json            ← QSO-uri concurs creat de DVS
│
│── EXPORTURI ───────────────────────────────────
├── cabrillo_maraton_20250115_1430.log
├── adif_20260115_1430.adi
├── log_20260115_1430.csv
├── edi_20260115_1430.edi
├── print_maraton_20260115_1430.txt
│
│── EXPORT CONCURSURI ───────────────────────────
├── contests_20260115_1430.json
│
│── BACKUP-URI ──────────────────────────────────
└── 📁 backups\
    ├── log_simplu_20260115_143000.json
    ├── log_maraton_20260116_091500.json
    └── ...  (max 50 per concurs)
```

---

## 📌 Reguli și Sfaturi

### ❌ Ce NU Trebuie Să Faceți

| Acțiune | Consecință |
|---------|-----------|
| Rulați din arhivă ZIP/RAR | Fișierele nu se salvează |
| Mutați exe fără JSON | Se creează fișiere noi goale |
| Ștergeți config.json | Se recreează cu valori implicite |
| Ștergeți log_*.json | QSO-urile se pierd (restaurați din backup) |
| Ștergeți contests.json | Concursurile custom se pierd |
| Editați JSON manual fără backup | JSON invalid = aplicația nu pornește corect |
| Puneți în C:\Program Files\ | Drepturi admin necesare |

### ✅ Ce Trebuie Să Faceți

| Acțiune | De ce |
|---------|-------|
| Folder dedicat ÎNAINTE de prima rulare | Fișierele se creează lângă exe |
| Configurați stația la prima pornire | Indicativul apare în export |
| Backup regulat | Protecție date |
| Validați înainte de export | Detectează erori |
| [Salvează] în Manager | Altfel modificările se pierd |
| Mutați TOTUL împreună | exe + JSON + backups = unitate |
| Copie folder pe USB/cloud | Backup extern |

---

## 🆘 Depanare

| Problemă | Soluție |
|----------|---------|
| Nu pornește | Python 3.8+ sau folosiți .exe |
| Log pierdut | `backups\` → copie → redenumire `log_CONCURS.json` |
| Concursuri dispărute | Reimportați din export JSON |
| Nu salvează | Folder read-only? Rulați din arhivă? |
| Nu apar toate benzile | Normal — concursul filtrează. Schimbați pe `simplu` |
| Exe mutat, log gol | JSON-urile au rămas în folderul vechi |
| Scor nu apare | Concursul are `scoring_mode: none` |
| Seriale nu apar | Concursul nu are `use_serial` activat |
| RST arată -10 | Modul FT8/FT4 — auto-RST. Modificați manual dacă doriți |
| Frecvența nu detectează banda | Verificați că e în kHz (ex: 14200, nu 14.200) |

---

## 📋 Checklist Prima Utilizare

```
☐  1.  Creez folder dedicat (C:\RadioLog\)
☐  2.  Copiez executabilul în folder
☐  3.  Pornesc aplicația
☐  4.  ⚙ Setări → Indicativ + Locator + Județ + Operator + Putere → [Salvează]
☐  5.  Aleg limba (ro/en)
☐  6.  Selectez concursul (sau creez din 🏆 Manager)
☐  7.  Aleg Categorie + Județ → [💾]
☐  8.  Primul QSO: indicativ → ENTER
☐  9.  Verific 📊 Statistici
☐ 10.  Fac un 💾 Backup
☐ 11.  73!
```

---

---

# 🇬🇧 English Documentation

## 📋 Description and Features

**YO Log PRO v16.0 FINAL** is the definitive version of the amateur radio logging application. Zero external dependencies — only Python standard library. One file, production-ready.

### What's Included

| Category | Features |
|----------|----------|
| **Core** | Separate log per contest, auto-save 60s, auto-backup on exit |
| **Input** | Frequency field with auto-band, auto-RST per mode (59/599/-10), live worked-before |
| **Table** | Duplicate coloring (red) / special (blue), column sorting, band/mode filters, Country+km column |
| **Keyboard** | Ctrl+F, Ctrl+Z, Ctrl+S, F2=next band, F3=next mode, Enter=LOG |
| **Contests** | Full manager (CRUD+import/export), 7 presets, 13 types, 7 scoring modes |
| **Scoring** | per_qso, per_band, maraton, multiplier, distance (real Haversine), custom |
| **Multipliers** | Counties (exact regex), DXCC (150+ prefixes), Band, Grid, Worked-All tracker |
| **Export** | Cabrillo 3.0 full, ADIF 3.1 (MHz freq), CSV (escaped), EDI (VHF/UHF) |
| **Import** | ADIF (.adi/.adif) + CSV — robust parsing |
| **Stats** | Dedicated window: band/mode/DXCC/counties/worked-all/operating time/rate |
| **Validation** | Min QSO, required stations, forbidden bands/modes, duplicates |
| **Utilities** | Contest timer (countdown), live search, undo 50 ops, text print, MD5 hash verify |
| **UI** | Live UTC clock, QSO/h rate meter, pro dark theme, saved geometry |
| **Sound** | Beep on duplicate, new multiplier, save, errors (Windows) |
| **i18n** | Romanian + English fully translated, instant switch |
| **DXCC** | Built-in database 150+ prefixes with auto-lookup |
| **Locator** | Haversine distance calculation between Maidenhead locators |

---

## 🚨 IMPORTANT: Dedicated Folder Rule

```
╔════════════════════════════════════════════════════════════════════════╗
║                                                                        ║
║   THE EXECUTABLE CREATES FILES IN THE FOLDER WHERE IT IS LOCATED!     ║
║                                                                        ║
║   ❌  DO NOT run from archive (ZIP/RAR)                                ║
║   ❌  DO NOT move exe without JSON files                               ║
║   ❌  DO NOT place in C:\Program Files\                                ║
║   ✅  Extract to dedicated folder BEFORE first run                     ║
║   ✅  Desktop shortcut — move only the shortcut                        ║
║   ✅  If moving, move EVERYTHING: exe + JSON + backups\                ║
║                                                                        ║
╚════════════════════════════════════════════════════════════════════════╝
```

---

## 📥 Installation and First Run

### Requirements

| Component | Requirement |
|-----------|-------------|
| Python | 3.8+ (only for .py) |
| Tkinter | Included with Python |
| OS | Windows 7+, Linux, macOS |
| .exe | Does NOT require Python |
| Dependencies | **ZERO** — standard library only |

### Installation

```bash
# 1. Create dedicated folder
mkdir C:\RadioLog

# 2. Copy executable or script into folder

# 3. Run
python yo_log_pro.py          # Windows
python3 yo_log_pro.py         # Linux/macOS
# OR double-click .exe        # Windows
```

### Auto-Created Files on First Run

| File | Content |
|------|---------|
| `config.json` | Station settings, defaults |
| `contests.json` | 7 pre-configured contests |
| `log_simplu.json` | Empty log for default contest |

---

## ⚙️ Initial Setup

### Step 1 — Station Settings (MANDATORY)

Click **[⚙ Settings]** → fill in:

| Field | Example | Used In |
|-------|---------|---------|
| **Callsign** | `YO8XYZ` | Header, Cabrillo, ADIF |
| **Locator** | `KN37` | VHF distance calc, ADIF |
| **County** | `NT` | County contests |
| **Address** | `City` | Cabrillo |
| **Operator** | `Name` | Cabrillo header |
| **Power (W)** | `100` | Cabrillo header |
| **Font** | `11` | 10-14 recommended |
| **Sounds** | ☑ | Beep on dup/new mult |

### Step 2 — Language

Top-right: `[ro▼]` or `[en▼]` — instant rebuild.

### Step 3 — Contest Selection

Header dropdown → choose contest. On change:
- Separate log loaded
- Bands/modes filtered
- Serial fields appear/disappear
- RST auto-adjusted per mode
- Score/km column appears/disappears

### Step 4 — Category and County

Control area: `Category: [▼]  County: [▼]  [💾]`

**Click [💾] to save** — MANDATORY.

---

## 📻 QSO Logging

### Fields

| Field | Required | Auto | Description |
|-------|:--------:|:----:|-------------|
| **Callsign** | ✅ | | Worked station |
| **Frequency** | | | kHz — auto-detects band |
| **Band** | ✅ | From freq | Or manual select |
| **Mode** | ✅ | | SSB/CW/FT8/etc. |
| **RST S/R** | | ✅ | Auto per mode: SSB→59, CW→599, FT8→-10 |
| **Nr S** | * | ✅ | Auto-increment (if contest uses serials) |
| **Nr R** | * | | Received serial |
| **Note** | | | County / Locator / Comment |
| **Date/Time** | | ✅ | UTC auto (Online mode) |

### Quick Flow

```
1. Type callsign → YO3ABC
   (live indicator: ⚠ DUP or ℹ Worked other QRG or blank)
2. Type frequency → 14250
   (band auto-sets to 20m)
3. ENTER
✅ QSO logged! Cursor back to Callsign. Serial incremented.
```

### Worked-Before Indicator

Below callsign field, live:
- **⚠ DUP 20m/SSB** (red) — exact duplicate same band/mode
- **ℹ Worked other QRG** (yellow) — worked on different band/mode
- **(blank)** — new station

### Auto-RST per Mode

| Mode | Default RST |
|------|-------------|
| SSB, AM, FM | 59 |
| CW, RTTY, DIGI, PSK31 | 599 |
| FT8, FT4 | -10 |
| JT65 | -15 |

Auto-adjusts when mode changes (F3).

---

## 🏆 Contest Manager

### Opening

- Menu: `Contests → Manager`
- Button: `🏆 Contests`
- Quick switch: `Contests → ⚡ Switch → [contest]`

### Operations

| Button | Action |
|--------|--------|
| ➕ Add | New contest from scratch |
| ✏ Edit | Modify rules (or double-click) |
| 📋 Duplicate | Copy as starting point |
| 🗑 Delete | Remove (except Simple Log) |
| 📤 Export | All contests → JSON |
| 📥 Import | From external JSON |

### Configurable Fields

| Field | Description | Example |
|-------|-------------|---------|
| **ID** | Unique, no spaces | `county-cup` |
| **Name RO/EN** | Bilingual display | `County Cup` |
| **Type** | 13 types available | `YO` |
| **Scoring** | 7 modes | `per_qso` |
| **Points/QSO** | Base points | `2` |
| **Min QSO** | Validation threshold | `25` |
| **Multipliers** | 5 types | `county` |
| **Categories** | One per line | `A. Seniors` |
| **Bands** | Checkboxes | ☑80m ☑40m |
| **Modes** | Checkboxes | ☑SSB ☑CW |
| **Serials** | On/Off | ☑ |
| **County** | On/Off + list | ☑ + `NT,IS,BC` |
| **Required Stations** | One per line | `YP8NT` |
| **Special Scoring** | `CALL=POINTS` | `YP8NT=10` |
| **Band Points** | `BAND=POINTS` | `160m=4` |

### Pre-configured Contests

| ID | Type | Scoring | Min | Serials | County | Mult |
|----|------|---------|-----|---------|--------|------|
| `simplu` | Simple | none | 0 | ☐ | ☐ | — |
| `maraton` | Marathon | maraton | 100 | ☐ | ☑ | county |
| `stafeta` | Relay | per_qso | 50 | ☑ | ☑ | county |
| `yo-dx-hf` | DX | per_band | 0 | ☑ | ☑ | dxcc |
| `yo-vhf` | VHF | distance | 0 | ☑ | ☐ | grid |
| `field-day` | Field Day | per_qso×2 | 0 | ☐ | ☐ | — |
| `sprint` | Sprint | per_qso | 0 | ☑ | ☐ | — |

---

## 📡 Contest Types and Scoring

### 13 Contest Types

Simplu, Maraton, Stafeta, YO, DX, VHF, UHF, Field Day, Sprint, QSO Party, SOTA, POTA, Custom

### 7 Scoring Modes

| Mode | Description |
|------|-------------|
| `none` | No scoring |
| `per_qso` | Fixed points per QSO |
| `per_band` | Different points per band |
| `maraton` | Special station bonuses |
| `multiplier` | QSO pts × multipliers |
| `distance` | Haversine km (VHF/UHF) |
| `custom` | User-defined |

### Score Formula

```
Total = Σ(QSO Points) × Multipliers
```

Live display: `Σ 123×18=2214`

---

## 🔍 Search, Filter, Sort

- **Ctrl+F** — Search dialog with live filtering (callsign + note)
- **Band/Mode filters** — dropdowns above table, display only
- **Column sort** — click any header, click again to reverse

---

## 📥 Log Import

Menu `🛠` or button `[📥 Import]`

- **ADIF** (.adi/.adif) — robust parser, all standard fields
- **CSV** (.csv) — flexible column name matching

Imported QSOs append to current contest log.

---

## 📤 Log Export

Button `[📤 Export]` → choose format:

| Format | Extension | Use |
|--------|-----------|-----|
| **Cabrillo 3.0** | .log | Contest submission (full header) |
| **ADIF 3.1** | .adi | LoTW, eQSL, Club Log (freq in MHz) |
| **CSV** | .csv | Excel, Sheets (properly escaped) |
| **EDI** | .edi | VHF/UHF European contests |
| **Print** | .txt | Formatted text for printing |

---

## 📊 Statistics and Validation

### Statistics Window

Dedicated colored-text window with:
- Total QSOs, unique stations
- Band summary table (QSO, Points, Unique per band)
- Mode summary
- Required stations (✓/✗ colored)
- Score breakdown (QSO pts, multipliers, total)
- Worked-All tracker (counties/DXCC worked vs total, missing list)
- DXCC summary (top 20 countries)
- Operating time (span, first/last, average rate)

### Validation

Checks: empty log, min QSO, required stations, allowed bands/modes, duplicates, diploma eligibility.

### Hash Verify

Menu `🛠 → Verify Log` — MD5 hash for integrity.

---

## 💾 Backup and Restore

- **Auto-backup** on every exit (with confirmation)
- **Auto-save** every 60 seconds + on every QSO add/delete
- **Manual backup** via [💾 Backup] button
- **Location**: `backups\log_CONTESTID_TIMESTAMP.json` (max 50 per contest)
- **Restore**: copy backup → rename to `log_CONTESTID.json` → restart

---

## ⌨ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Enter` | Add QSO |
| `Ctrl+F` | Search |
| `Ctrl+Z` | Undo |
| `Ctrl+S` | Force save |
| `F2` | Cycle next band |
| `F3` | Cycle next mode (+auto RST) |
| `Double-click` | Edit QSO |
| `Right-click` | Context menu |

---

## 📁 Complete Folder Structure

```
📁 C:\RadioLog\
├── yo_log_pro.exe              ← executable (DO NOT move alone!)
├── config.json                  ← station settings
├── contests.json                ← contest configurations
├── log_simplu.json              ← Simple Log QSOs
├── log_maraton.json             ← Marathon QSOs
├── log_yo-dx-hf.json            ← YO DX HF QSOs
├── cabrillo_*.log               ← Cabrillo exports
├── adif_*.adi                   ← ADIF exports
├── log_*.csv                    ← CSV exports
├── edi_*.edi                    ← EDI exports
├── print_*.txt                  ← Print exports
├── contests_*.json              ← Contest exports
└── 📁 backups\
    └── log_*_*.json             ← auto-backups (max 50/contest)
```

---

## 📌 Rules and Tips

### ❌ What NOT To Do

| Action | Consequence |
|--------|-------------|
| Run from ZIP/RAR | Files not saved |
| Move exe without JSON | New empty files created |
| Delete config.json | Recreated with defaults |
| Delete log_*.json | QSOs lost (restore from backup) |
| Delete contests.json | Custom contests lost |
| Edit JSON manually without backup | Invalid JSON blocks app |
| Place in Program Files | Admin rights needed |

### ✅ What To Do

| Action | Why |
|--------|-----|
| Dedicated folder BEFORE first run | Files created next to exe |
| Configure station first | Callsign in exports |
| Backup regularly | Data protection |
| Validate before export | Catches errors |
| [Save] in Manager | Changes lost otherwise |
| Move EVERYTHING together | exe+JSON+backups = unit |
| Copy folder to USB/cloud | External backup |

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| Won't start | Python 3.8+ or use .exe |
| Lost log | `backups\` → copy → rename to `log_CONTEST.json` |
| Contests gone | Re-import from JSON export |
| Can't save | Read-only folder? Running from archive? |
| Not all bands | Normal — contest filters. Switch to `simplu` |
| Moved exe, log empty | JSON files stayed in old folder |
| No score | Contest has `scoring_mode: none` |
| No serials | Contest doesn't have `use_serial` |
| RST shows -10 | FT8/FT4 auto-RST. Edit manually if needed |
| Freq doesn't detect band | Must be in kHz (14200, not 14.200) |

---

## 📋 First Use Checklist

```
☐  1.  Create dedicated folder
☐  2.  Copy executable
☐  3.  Launch app
☐  4.  ⚙ Settings → Callsign+Locator+County+Operator+Power → [Save]
☐  5.  Choose language (ro/en)
☐  6.  Select contest or create from 🏆 Manager
☐  7.  Choose Category+County → [💾]
☐  8.  First QSO: callsign → ENTER
☐  9.  Check 📊 Stats
☐ 10.  Make a 💾 Backup
☐ 11.  73!
```

---

---

# 🔧 Secțiune Tehnică / Technical Section

## 🏗️ Arhitectura / Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         App (Tk)                             │
│              Main window, UI, event loop                     │
├──────────┬──────────┬──────────┬──────────┬────────────────┤
│  Header  │  Input   │ Filters  │ Treeview │  Button Bar    │
│ (clock,  │ (call,   │ (band,   │ (log,    │ (settings,     │
│  rate,   │  freq,   │  mode)   │  color,  │  contests,     │
│  status) │  band,   │          │  sort)   │  stats, etc.)  │
│          │  mode,   │          │          │                │
│          │  rst,    │          │          │                │
│          │  serial) │          │          │                │
├──────────┴──────────┴──────────┴──────────┴────────────────┤
│                                                             │
│  ┌─────────┐ ┌─────────┐ ┌────────┐ ┌──────────────────┐  │
│  │   DM    │ │  Score  │ │  Lang  │ │    Importer      │  │
│  │  JSON   │ │  calc,  │ │  i18n  │ │  ADIF + CSV      │  │
│  │  I/O,   │ │  mults, │ │  RO/EN │ │  parser          │  │
│  │  backup │ │  valid  │ │        │ │                  │  │
│  └─────────┘ └─────────┘ └────────┘ └──────────────────┘  │
│                                                             │
│  ┌─────────┐ ┌─────────┐ ┌────────────────────────────┐   │
│  │   Loc   │ │  DXCC   │ │   ContestMgr + Editor      │   │
│  │  latlon  │ │  150+   │ │   CRUD, import/export      │   │
│  │  dist   │ │  prefix │ │   full config form         │   │
│  └─────────┘ └─────────┘ └────────────────────────────┘   │
│                                                             │
│  ┌───────────────────┐  ┌────────────────────────────┐    │
│  │   StatsWindow     │  │   TimerDialog / Search     │    │
│  │   colored text    │  │   countdown / live filter  │    │
│  └───────────────────┘  └────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Clase / Classes

| Clasă | Responsabilitate |
|-------|------------------|
| `App` | Fereastra principală, UI complet, toate operațiile / Main window, full UI, all operations |
| `DM` | Persistență JSON, log per concurs, backup atomic / JSON persistence, per-contest log, atomic backup |
| `Score` | Calcul puncte, multiplicatori (regex), validare, detecție duplicate / Score calc, multipliers, validation, dup detection |
| `L` | Manager limbă RO/EN / Language manager |
| `Loc` | Conversie Maidenhead ↔ lat/lon, distanță Haversine / Maidenhead ↔ lat/lon, Haversine distance |
| `DXCC` | Bază de date 150+ prefixe, lookup din indicativ / 150+ prefix DB, callsign lookup |
| `Importer` | Parser ADIF + CSV robust / Robust ADIF + CSV parser |
| `ContestEditor` | Formular complet editare concurs cu scroll / Full scrollable contest edit form |
| `ContestMgr` | CRUD concursuri + import/export JSON / Contest CRUD + JSON import/export |
| `StatsWindow` | Statistici colorate într-o fereastră dedicată / Colored stats in dedicated window |
| `TimerDialog` | Cronometru concurs cu countdown / Contest timer with countdown |
| `SearchDialog` | Căutare live în log / Live log search |

---

## 📄 Structura JSON / JSON Structure

### config.json

```json
{
  "call": "YO8ACR",
  "loc": "KN37",
  "jud": "NT",
  "addr": "Târgu Neamț",
  "cat": 0,
  "fs": 11,
  "contest": "maraton",
  "county": "NT",
  "lang": "ro",
  "manual_dt": false,
  "sounds": true,
  "op_name": "Ardei Constantin",
  "power": "100",
  "win_geo": "1220x780+350+150"
}
```

### log_CONTESTID.json

```json
[
  {
    "c": "YO3ABC",
    "b": "40m",
    "m": "SSB",
    "s": "59",
    "r": "59",
    "n": "NT",
    "d": "2026-01-15",
    "t": "14:30",
    "f": "7100",
    "ss": "001",
    "sr": "045"
  }
]
```

| Cheie | Descriere |
|-------|-----------|
| `c` | Indicativ / Callsign |
| `b` | Bandă / Band |
| `m` | Mod / Mode |
| `s` | RST trimis / RST sent |
| `r` | RST primit / RST received |
| `n` | Notă (județ/locator/comentariu) |
| `d` | Data YYYY-MM-DD |
| `t` | Ora HH:MM (UTC) |
| `f` | Frecvență kHz |
| `ss` | Nr serial trimis (opțional) |
| `sr` | Nr serial primit (opțional) |

### contests.json — Per Contest

```json
{
  "yo-dx-hf": {
    "name_ro": "YO DX HF Contest",
    "name_en": "YO DX HF Contest",
    "contest_type": "DX",
    "categories": ["A. SO AB High", "B. SO AB Low"],
    "scoring_mode": "per_band",
    "points_per_qso": 1,
    "min_qso": 0,
    "allowed_bands": ["160m","80m","40m","20m","15m","10m"],
    "allowed_modes": ["SSB","CW"],
    "required_stations": [],
    "special_scoring": {},
    "use_serial": true,
    "use_county": true,
    "county_list": ["AB","AR","...","B"],
    "multiplier_type": "dxcc",
    "band_points": {"160m":4,"80m":3,"40m":2,"20m":1,"15m":1,"10m":2},
    "is_default": false
  }
}
```

---

## 📦 Creare Executabil / Build Executable

### Windows

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "YO_Log_PRO_v16_FINAL" yo_log_pro.py
# Result: dist\YO_Log_PRO_v16_FINAL.exe
```

### Linux

```bash
pip install pyinstaller
pyinstaller --onefile --name "yo_log_pro" yo_log_pro.py
chmod +x dist/yo_log_pro
```

### macOS

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "YO_Log_PRO" yo_log_pro.py
```

**După build:** copiați executabilul într-un folder dedicat înainte de distribuire.

---

## 📋 Changelog

### v16.0 FINAL (2026) — Versiunea Definitivă

**Bug-uri Fixate:**
- ✅ Detecție duplicate (call+band+mode) cu avertizare vizuală live + dialog
- ✅ CSV export cu `csv.writer` (escapare corectă virgule/ghilimele)
- ✅ Mousewheel bind doar pe canvas (nu global)
- ✅ Exit dialog texte separate titlu/mesaj
- ✅ County match regex word boundary (nu match parțial)
- ✅ Distanță reală Haversine din locatoare Maidenhead
- ✅ ADIF frecvență în MHz (standard ADIF 3.1)
- ✅ Log separat per concurs (nu se amestecă)
- ✅ Migrare automată din log.json vechi
- ✅ Serial counter reset corect per concurs
- ✅ Multi-select delete
- ✅ Cabrillo 3.0 cu toate câmpurile obligatorii

**Funcționalități Noi:**
- ✅ **Import ADIF + CSV** cu parsare robustă
- ✅ **Auto-RST per mod** (59/599/-10/-15)
- ✅ **Bază DXCC 150+ prefixe** cu coloana Țară
- ✅ **Câmp frecvență** cu auto-detecție bandă
- ✅ **Calcul distanță Haversine** real pentru VHF/UHF
- ✅ **Statistici fereastră dedicată** cu text colorat
- ✅ **Worked-All tracker** (județe/DXCC lucrate vs lipsă)
- ✅ **Timp operare** și rată medie în statistici
- ✅ **Export EDI** format standard VHF/UHF european
- ✅ **Print text** formatat tabelar
- ✅ **Verificare hash MD5** pentru integritate log
- ✅ **Window geometry salvată** între sesiuni
- ✅ **F2 = bandă+**, **F3 = mod+** cu auto-RST
- ✅ **Filtre bandă/mod** deasupra tabelului
- ✅ **Sortare coloane** click pe header
- ✅ **Undo** cu stack de 50 operații (add + delete)
- ✅ **Timer concurs** countdown cu alertă sonoră
- ✅ **Căutare live** Ctrl+F
- ✅ **Ceas UTC** actualizat la fiecare secundă
- ✅ **Rate meter** QSO/h live
- ✅ **Auto-save** la 60 secunde
- ✅ **Sunete** la duplicate, multiplicator nou, save, erori
- ✅ **Clear log** cu backup automat înainte

### v15.0 (2026)
- Log separat per concurs, căutare, ceas UTC, auto-save
- Detecție duplicate, colorare rânduri, calcul distanță
- DXCC lookup, undo, timer, EDI export
- Cabrillo 3.0 complet, scurtături tastatură

### v14.0 (2026)
- Manager concursuri configurabil (CRUD)
- 12 tipuri concurs, 7 moduri punctare, 5 multiplicatori
- Import/Export concursuri JSON
- UI adaptiv per concurs

### v13.0 (2026)
- Multi-contest cu concursuri predefinite
- Export Cabrillo/ADIF/CSV
- Interfață bilingvă RO/EN
- Temă dark, backup automat

---

## 📜 Licență / License

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
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
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
  <strong>73 de YO8ACR! 📻</strong><br><br>
  <em>🇷🇴 „Radioamatorismul — hobby-ul care conectează lumea"</em><br>
  <em>🇬🇧 "Amateur Radio — the hobby that connects the world"</em><br><br>
  <strong>v16.0 FINAL — Versiunea Definitivă / Final Edition</strong>
</p>
```
