# 📻 YO Log PRO v3.0 — Multi-Contest Amateur Radio Logger

<p align="center">
  <img src="https://img.shields.io/badge/Version-13.0-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/Tkinter-GUI-orange?style=for-the-badge" />
  <img src="https://img.shields.io/badge/License-MIT-lightgrey?style=for-the-badge" />
</p>

**Dezvoltat de / Developed by:** Ardei Constantin-Cătălin (YO8ACR)  
**Email:** yo8acr@gmail.com

---

## 🇷🇴 Română

### Descriere

**YO Log PRO v13.0** este o aplicație desktop dedicată radioamatorilor pentru înregistrarea QSO-urilor în concursuri și sesiuni de operare generală. Interfața modernă cu temă întunecată (dark theme), suport multi-concurs, export în formatele standard și backup automat fac din această aplicație un instrument de încredere pentru operatorii YO.

### Funcționalități principale

- **Înregistrare QSO rapidă** — Introduci indicativul, banda, modul și apeși ENTER sau butonul LOG
- **Multi-concurs** — Suport pentru Maraton Ion Creangă, Cupa Moldovei, Ștafetă, YO-DX-HF și Log Simplu
- **Calcul punctaj automat** — Reguli specifice per concurs, inclusiv stații cu punctaj special pentru Maraton
- **Validare log** — Verifică stațiile obligatorii, numărul minim de QSO-uri și eligibilitatea pentru diplomă
- **Export multiple formate** — Cabrillo (`.log`), ADIF (`.adi`), CSV (`.csv`)
- **Backup automat** — La ieșire din aplicație și manual; păstrează ultimele 50 de backup-uri
- **Dată/oră manuală sau automată (UTC)** — Comutare simplă printr-un checkbox
- **Bilingv RO/EN** — Interfață complet tradusă, comutare din header
- **Editare și ștergere QSO** — Dublu-click sau click dreapta pe înregistrare
- **Statistici detaliate** — QSO-uri per bandă, per mod, scor total, stații obligatorii găsite

### Concursuri suportate

| Cheie         | Nume                         | Mod scoring       |
|---------------|------------------------------|--------------------|
| `maraton`     | Maraton Ion Creangă          | Maraton (special) |
| `stafeta`     | Cupa Tomisului               | Standard          |
| `yo-dx`       | YO-DX-HF                     | Standard          |
| `log_simplu`  | Log Simplu                   | Fără              |

### Cerințe sistem

- Python **3.8** sau mai nou
- Modulul `tkinter` (inclus implicit cu Python pe Windows și macOS; pe Linux: `sudo apt install python3-tk`)
- Nu sunt necesare dependențe externe (pip)

### Instalare și rulare

```bash
# 1. Clonează sau descarcă fișierul principal
git clone https://github.com/YO8ACR/yolog-pro.git
cd yolog-pro

# 2. Rulează aplicația
python yolog_pro.py
```

> **PyInstaller (executabil standalone):**
> ```bash
> pip install pyinstaller
> pyinstaller --onefile --windowed yolog_pro.py
> ```
> Executabilul se va găsi în directorul `dist/`.

### Fișiere generate

Toate fișierele sunt salvate în **același director** cu executabilul sau scriptul Python:

| Fișier              | Descriere                            |
|---------------------|--------------------------------------|
| `log.json`          | Log-ul principal (QSO-uri)           |
| `config.json`       | Configurație (indicativ, locator...) |
| `contests.json`     | Regulamente concursuri               |
| `backups/`          | Directorul cu backup-uri timestampate |

### Ghid de utilizare

1. **La prima rulare** — Mergi la **Setări** și completează indicativul, locatorul și județul
2. **Alege concursul** — Din combo-box-ul din header (dreapta)
3. **Alege categoria și județul** — Din controalele afișate sub câmpurile de input
4. **Înregistrează QSO** — Completează indicativul, selectează banda și modul, apasă **LOG** sau `Enter`
5. **Editare** — Dublu-click pe un QSO din lista de jos sau click dreapta → Editează
6. **Ștergere** — Click dreapta → Șterge sau butonul **Șterge** din bara de jos
7. **Validare** — Apasă **Validează** pentru a verifica log-ul față de regulamentul concursului
8. **Export** — Apasă **Export** și alege formatul dorit
9. **Backup** — Apasă **Backup** oricând; se face automat și la ieșire

### Scoring Maraton Ion Creangă

| Stație / Condiție             | Puncte |
|-------------------------------|--------|
| YP8IC                         | 20     |
| YR8TGN                        | 20     |
| YO8RRC, YO8K, YO8ACR          | 5      |
| Stații cu sufix `/IC` (club)  | 10     |
| Stații cu sufix `/IC` (altele)| 5      |
| Restul QSO-urilor             | 1      |

### Scurtături tastatură

| Tastă     | Acțiune                   |
|-----------|---------------------------|
| `Enter`   | Adaugă / actualizează QSO |
| Dublu-click pe QSO | Editează QSO   |
| Click dreapta pe QSO | Meniu context |

---

## 🇬🇧 English

### Description

**YO Log PRO v13.0** is a desktop logging application for amateur radio operators, designed for contest and general operation logging. It features a modern dark-theme UI, multi-contest support, standard export formats, and automatic backup functionality.

### Key Features

- **Fast QSO logging** — Enter callsign, band, mode and press ENTER or click LOG
- **Multi-contest support** — Maraton Ion Creangă, Moldova Cup (Relay), YO-DX-HF, and Simple Log
- **Automatic scoring** — Contest-specific rules with special station multipliers for Maraton
- **Log validation** — Checks for required stations, minimum QSO count, and diploma eligibility
- **Multiple export formats** — Cabrillo (`.log`), ADIF (`.adi`), CSV (`.csv`)
- **Automatic backup** — On exit and on demand; retains the last 50 timestamped backups
- **Manual or automatic UTC date/time** — Toggle via a checkbox in the input area
- **Bilingual RO/EN** — Fully translated interface, switchable from the header
- **QSO edit and delete** — Double-click or right-click on any log entry
- **Detailed statistics** — QSOs by band, by mode, total score, required stations found

### Supported Contests

| Key           | Name                         | Scoring mode      |
|---------------|------------------------------|-------------------|
| `maraton`     | Marathon Ion Creangă         | Maraton (special) |
| `stafeta`     | Tomis Cup (Relay)            | Standard          |
| `yo-dx`       | YO-DX-HF                     | Standard          |
| `log_simplu`  | Simple Log                   | None              |

### System Requirements

- Python **3.8** or newer
- `tkinter` module (bundled with Python on Windows and macOS; on Linux: `sudo apt install python3-tk`)
- No external pip dependencies required

### Installation & Running

```bash
# 1. Clone or download the main file
git clone https://github.com/YO8ACR/yolog-pro.git
cd yolog-pro

# 2. Run the application
python yolog_pro.py
```

> **Building a standalone executable with PyInstaller:**
> ```bash
> pip install pyinstaller
> pyinstaller --onefile --windowed yolog_pro.py
> ```
> The executable will be found in the `dist/` directory.

### Generated Files

All files are saved in the **same directory** as the executable or Python script:

| File                | Description                          |
|---------------------|--------------------------------------|
| `log.json`          | Main log file (QSO records)          |
| `config.json`       | Configuration (callsign, locator...) |
| `contests.json`     | Contest rules                        |
| `backups/`          | Timestamped backup directory         |

### Usage Guide

1. **First run** — Go to **Settings** and fill in your callsign, locator and county
2. **Select contest** — From the combo box in the header (top right)
3. **Select category and county** — From the controls shown below the input fields
4. **Log a QSO** — Fill in callsign, select band and mode, press **LOG** or `Enter`
5. **Edit** — Double-click a QSO in the list, or right-click → Edit
6. **Delete** — Right-click → Delete, or use the **Delete** button in the bottom bar
7. **Validate** — Press **Validate** to check the log against contest rules
8. **Export** — Press **Export** and choose a format
9. **Backup** — Press **Backup** anytime; also done automatically on exit

### Maraton Ion Creangă Scoring

| Station / Condition              | Points |
|----------------------------------|--------|
| YP8IC                            | 20     |
| YR8TGN                           | 20     |
| YO8RRC, YO8K, YO8ACR             | 5      |
| Stations with `/IC` suffix (club)| 10     |
| Stations with `/IC` suffix (other)| 5     |
| All other QSOs                   | 1      |

### Keyboard Shortcuts

| Key              | Action                      |
|------------------|-----------------------------|
| `Enter`          | Add / update QSO            |
| Double-click QSO | Edit QSO                    |
| Right-click QSO  | Context menu (edit/delete)  |

---

## 📁 Project Structure

```
yolog-pro/
├── yolog_pro.py       # Main application file
├── config.json        # Auto-generated on first run
├── log.json           # Auto-generated on first run
├── contests.json      # Auto-generated on first run
├── backups/           # Auto-created backup directory
└── README.md          # This file
```

---

## 📜 License

This project is open-source and free to use for personal and educational purposes.  
© 2026 Ardei Constantin-Cătălin (YO8ACR) — yo8acr@gmail.com

---

<p align="center">73 de YO8ACR 📡</p>
