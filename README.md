
# 📻 YO Log PRO v14.0 — Multi-Contest Amateur Radio Logger

<p align="center">
  <img src="https://img.shields.io/badge/version-14.0-blue?style=for-the-badge" alt="Version 14.0">
  <img src="https://img.shields.io/badge/python-3.8%2B-green?style=for-the-badge&logo=python" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/license-MIT-orange?style=for-the-badge" alt="MIT License">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey?style=for-the-badge" alt="Platform">
</p>

<p align="center">
  <strong>🇷🇴 Aplicație profesională de logging pentru radioamatori cu manager de concursuri complet configurabil</strong><br>
  <strong>🇬🇧 Professional amateur radio logging application with fully configurable contest manager</strong>
</p>

---

## 📑 Cuprins / Table of Contents

### 🇷🇴 Română
- [Descriere](#-descriere)
- [IMPORTANT: Regula Folderului Dedicat](#-important-regula-folderului-dedicat)
- [Instalare și Prima Pornire](#-instalare-și-prima-pornire)
- [Configurare Stație](#️-configurare-stație)
- [Selectare Limbă](#-selectare-limbă)
- [Alegere și Configurare Concurs](#-alegere-și-configurare-concurs)
- [Manager de Concursuri](#-manager-de-concursuri)
- [Tipuri de Concurs](#-tipuri-de-concurs)
- [Moduri de Punctare](#-moduri-de-punctare)
- [Sistemul de Multiplicatori](#-sistemul-de-multiplicatori)
- [Logare QSO-uri](#-logare-qso-uri)
- [Editare și Ștergere QSO](#️-editare-și-ștergere-qso)
- [Statistici și Validare](#-statistici-și-validare)
- [Backup](#-backup)
- [Export Log](#-export-log)
- [Structura Folderului](#-structura-completă-a-folderului)
- [Ce NU Trebuie Să Faceți](#-ce-nu-trebuie-să-faceți)
- [Ce Trebuie Să Faceți](#-ce-trebuie-să-faceți)
- [Depanare](#-depanare)
- [Checklist Prima Utilizare](#-checklist-prima-utilizare)

### 🇬🇧 English
- [Description](#-description)
- [IMPORTANT: Dedicated Folder Rule](#-important-dedicated-folder-rule)
- [Installation and First Run](#-installation-and-first-run)
- [Station Setup](#️-station-setup)
- [Language Selection](#-language-selection)
- [Contest Selection and Configuration](#-contest-selection-and-configuration)
- [Contest Manager](#-contest-manager)
- [Contest Types](#-contest-types)
- [Scoring Modes](#-scoring-modes)
- [Multiplier System](#-multiplier-system)
- [QSO Logging](#-qso-logging)
- [Editing and Deleting QSOs](#️-editing-and-deleting-qsos)
- [Statistics and Validation](#-statistics-and-validation)
- [Backup System](#-backup-system)
- [Log Export](#-log-export)
- [Folder Structure](#-complete-folder-structure)
- [What NOT To Do](#-what-not-to-do)
- [What To Do](#-what-to-do)
- [Troubleshooting](#-troubleshooting)
- [First Use Checklist](#-first-use-checklist)

### 🔧 Tehnic / Technical
- [Arhitectura Aplicației](#-arhitectura-aplicației--application-architecture)
- [Structura Fișierelor JSON](#-structura-fișierelor-json--json-file-structure)
- [Dezvoltare și Contribuții](#️-dezvoltare-și-contribuții--development-and-contributing)
- [Creare Executabil](#-creare-executabil--build-executable)
- [Changelog](#-changelog)
- [Licență / License](#-licență--license)
- [Contact](#-contact)

---

# 🇷🇴 DOCUMENTAȚIE ROMÂNĂ

## 📋 Descriere

**YO Log PRO v14.0** este o aplicație de logging pentru radioamatori, dezvoltată în Python cu interfață grafică Tkinter. Aplicația oferă un **manager de concursuri complet configurabil**, permițând utilizatorilor să creeze, editeze, duplice și șteargă concursuri cu reguli personalizate de punctare, categorii, benzi, moduri și multiplicatori.

### Funcționalități Principale

- **Logare rapidă** — indicativ + ENTER, cu auto-completare dată/oră UTC
- **Manager de concursuri** — adaugă, editează, duplică, șterge, importă, exportă concursuri
- **12 tipuri de concurs** — Simplu, Maraton, Ștafetă, YO, DX, VHF, UHF, Field Day, Sprint, QSO Party, SOTA, POTA, Custom
- **7 moduri de punctare** — none, per_qso, per_band, maraton, multiplier, distance, custom
- **5 tipuri de multiplicatori** — Fără, Județe, DXCC, Bandă, Grid Square
- **Interfață adaptivă** — benzi, moduri, coloane și câmpuri se ajustează per concurs
- **Export** — Cabrillo (.log), ADIF (.adi), CSV (.csv)
- **Validare** — verificare automată conform regulilor concursului
- **Backup automat** — la fiecare închidere + manual, maxim 50 reținute
- **Bilingv** — Română și Engleză, schimbare instantanee
- **Temă dark** — interfață modernă, profesională

### Captură de Ecran (Reprezentare)

```
┌──────────────────────────────────────────────────────────────────────┐
│  ● Online │ YO8ACR | Maraton [Maraton] | A. Seniori YO | QSO: 47   │
│                                                       [ro▼] [▼con] │
├──────────────────────────────────────────────────────────────────────┤
│  Indicativ   Bandă  Mod   RST S  RST R  Județ / Notă     [  LOG ] │
│  [________]  [40m▼] [SSB▼] [59]   [59]  [_________]      [Reset ] │
│  Dată: [2026-01-15]  Oră: [14:30]  ☐ Manual                       │
│  Categorie: [A. Seniori YO ▼]   Județ: [NT ▼]   [💾 Salvează]     │
├──────────────────────────────────────────────────────────────────────┤
│ Nr │ Indicativ │ Bandă │ Mod │ RST S │ RST R │ Notă  │ Dată  │ Pt │
│ 47 │ YO3ABC    │ 40m   │ SSB │ 59    │ 59    │ NT    │ 01-15 │ 1  │
│ 46 │ YO5DEF    │ 20m   │ CW  │ 599   │ 599   │ BV    │ 01-15 │ 1  │
│ .. │ ...       │ ...   │ ... │ ...   │ ...   │ ...   │ ...   │ .. │
├──────────────────────────────────────────────────────────────────────┤
│[Setări][🏆Concursuri][Statistici][Validează][Export][Șterge][Backup]│
└──────────────────────────────────────────────────────────────────────┘
```

---

## 🚨 IMPORTANT: Regula Folderului Dedicat

```
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║   EXECUTABILUL TREBUIE SĂ RĂMÂNĂ ÎN FOLDERUL LUI DEDICAT!           ║
║                                                                       ║
║   Aplicația creează fișiere de configurare, log și backup             ║
║   ÎN ACELAȘI FOLDER în care se află executabilul.                     ║
║                                                                       ║
║   ❌  NU rulați direct din arhivă (ZIP/RAR)                           ║
║   ❌  NU mutați executabilul fără fișierele JSON                      ║
║   ❌  NU ștergeți fișierele JSON create automat                       ║
║   ❌  NU puneți în C:\Program Files\ (necesită drepturi admin)        ║
║   ✅  Extrageți TOTUL într-un folder dedicat ÎNAINTE de prima rulare  ║
║   ✅  Creați shortcut pe Desktop dacă doriți acces rapid              ║
║   ✅  Dacă mutați, mutați TOTUL: exe + JSON + backups\               ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
```

---

## 📥 Instalare și Prima Pornire

### Cerințe Sistem

| Component | Cerință |
|-----------|---------|
| Python | 3.8 sau mai nou (doar pentru rulare .py) |
| Tkinter | Inclus cu Python |
| OS | Windows 7+, Linux, macOS |
| Spațiu disc | ~5 MB + spațiu pentru loguri |
| Executabil .exe | NU necesită Python instalat |

### Pas 1 — Pregătire Folder

Creați un folder dedicat:
```
Recomandat:
  C:\RadioLog\                           ← Windows
  ~/RadioLog/                            ← Linux / macOS
  Desktop\YO_Log_PRO\                    ← pe Desktop
```

Copiați executabilul (sau scriptul .py) în acest folder:
```
📁 C:\RadioLog\
└── YO_Log_PRO_v14.exe        (sau yo_log_pro.py)
```

### Pas 2 — Prima Pornire

```bash
# Cu executabil (Windows):
Dublu-click pe YO_Log_PRO_v14.exe

# Cu Python (toate platformele):
cd C:\RadioLog
python yo_log_pro.py

# Linux / macOS:
cd ~/RadioLog
python3 yo_log_pro.py
```

### Pas 3 — Fișiere Create Automat

La prima pornire, aplicația creează automat **3 fișiere**:

```
📁 C:\RadioLog\
├── YO_Log_PRO_v14.exe        ← executabilul (existent)
├── config.json                ← ⚡ CREAT — setările stației
├── log.json                   ← ⚡ CREAT — logul gol []
└── contests.json              ← ⚡ CREAT — 7 concursuri predefinite
```

| Fișier | Conținut Inițial |
|--------|-----------------|
| `config.json` | Indicativ: YO8ACR, Locator: KN37, Județ: NT, Limbă: ro |
| `log.json` | `[]` — gol, niciun QSO |
| `contests.json` | 7 concursuri predefinite gata de utilizare |

### (Opțional) Shortcut pe Desktop

```
Windows:
  Click dreapta pe executabil → Trimite la → Desktop (creare comandă rapidă)

⚠️ Mutați doar SHORTCUT-ul, NU executabilul!
```

---

## ⚙️ Configurare Stație

**Aceasta este prima acțiune obligatorie la prima utilizare.**

1. Click pe butonul **[Setări]** din bara de jos
2. Completați:

| Câmp | Ce scrieți | Exemplu |
|------|-----------|---------|
| **Indicativ** | Indicativul DVS | `YO8XYZ` |
| **Locator** | Locatorul Maidenhead (4-6 caractere) | `KN37` |
| **Județ** | Abrevierea județului | `NT` |
| **Adresă** | Orașul/localitatea (opțional) | `Târgu Neamț` |
| **Mărime Font** | 10-16 recomandat | `12` |

3. Click **[Salvează]**
4. Confirmarea: *„Setări salvate!"*

Bara de informații din header se actualizează cu indicativul DVS.

---

## 🌐 Selectare Limbă

Colțul din **dreapta sus** al ferestrei:

| Selector | Limbă |
|----------|-------|
| `ro` | 🇷🇴 Română (implicit) |
| `en` | 🇬🇧 English |

Interfața se reconstruiește complet și instant la schimbarea limbii. Toate mesajele, etichetele, dialogurile și meniurile sunt traduse.

---

## 🏆 Alegere și Configurare Concurs

### Concursuri Predefinite (din fabrică)

| ID | Tip | Descriere | Punctare | Min QSO |
|----|-----|-----------|----------|---------|
| `simplu` | Simplu | Log liber, fără reguli | none | 0 |
| `maraton` | Maraton | Stații speciale, bonusuri | maraton | 100 |
| `stafeta` | Ștafetă | Concurs pe echipe cu seriale | per_qso | 50 |
| `yo-dx-hf` | DX | YO DX HF — puncte per bandă | per_band | 0 |
| `yo-vhf` | VHF | VHF/UHF — bazat pe distanță | distance | 0 |
| `field-day` | Field Day | Ziua Câmpului — portabil | per_qso | 0 |
| `sprint` | Sprint | Concurs rapid cu seriale | per_qso | 0 |

### Selectare Rapidă

**Metoda 1** — Selector din dreapta sus:
```
[simplu ▼] → click și alegeți concursul dorit
```

**Metoda 2** — Din meniu:
```
Concursuri → ⚡ Switch → [concursul dorit]
```

La schimbarea concursului, interfața se reconstruiește automat:
- Benzile și modurile din dropdown se filtrează
- Câmpurile de numere seriale apar/dispar
- Coloana de Puncte apare/dispare
- Eticheta Notă devine „Județ / Notă" dacă concursul folosește județe

### Selectare Categorie și Județ

După alegerea concursului, în zona de control:
```
Categorie: [A. Seniori YO ▼]   Județ: [NT ▼]   [💾 Salvează]
```

1. Alegeți categoria la care participați
2. Alegeți județul (dacă concursul îl folosește)
3. Click **[💾 Salvează]** — **OBLIGATORIU** pentru a reține alegerea

---

## 🏆 Manager de Concursuri

Inima aplicației v14.0. Deschideți din:
- **Meniu:** `Concursuri → Manager`
- **Buton:** `🏆 Concursuri` din bara de jos

### Operații Disponibile

| Buton | Operație | Descriere |
|-------|----------|-----------|
| ➕ | **Adaugă** | Creează un concurs nou de la zero |
| ✏️ | **Editează** | Modifică regulile unui concurs existent (dublu-click sau buton) |
| 📋 | **Duplică** | Copiază un concurs ca punct de plecare pentru unul nou |
| 🗑️ | **Șterge** | Elimină un concurs (excepție: „Log Simplu" nu se poate șterge) |
| 📤 | **Exportă** | Salvează toate concursurile ca fișier JSON (pentru partajare/backup) |
| 📥 | **Importă** | Încarcă concursuri din fișier JSON extern |

### Câmpuri Configurabile per Concurs

| Câmp | Tip | Descriere | Exemplu |
|------|-----|-----------|---------|
| **ID Concurs** | text | Unic, fără spații, litere mici | `cupa-neamt` |
| **Nume RO** | text | Numele afișat în română | `Cupa Județului Neamț` |
| **Nume EN** | text | Numele afișat în engleză | `Neamț County Cup` |
| **Tip Concurs** | selector | Categoria generală | `YO` |
| **Mod Punctare** | selector | Algoritmul de scor | `per_qso` |
| **Puncte per QSO** | număr | Baza de puncte | `2` |
| **Minim QSO** | număr | Prag pentru validare | `25` |
| **Multiplicatori** | selector | Tipul de multiplicatori | `county` |
| **Categorii** | text multilinie | Una per linie | `A. Seniori` / `B. Juniori` |
| **Benzi Permise** | checkbox-uri | Bifați benzile dorite | ☑80m ☑40m ☑20m |
| **Moduri Permise** | checkbox-uri | Bifați modurile dorite | ☑SSB ☑CW |
| **Numere Seriale** | checkbox | Activează Nr S / Nr R | ☑ |
| **Folosește Județ** | checkbox | Activează selectorul de județ | ☑ |
| **Lista Județe** | text | Separate prin virgulă | `NT,IS,BC,SV` |
| **Stații Obligatorii** | text multilinie | Indicative necesare, una per linie | `YP8NT` |
| **Punctare Specială** | text multilinie | `INDICATIV=PUNCTE` per linie | `YP8NT=10` |
| **Puncte per Bandă** | text multilinie | `BANDĂ=PUNCTE` per linie | `160m=4` / `80m=3` |

### ⚠️ Salvare în Manager

```
După orice modificare (adăugare/editare/ștergere/duplicare/import):

  1. Click [Salvează] ÎN EDITORUL concursului (dacă ați editat)
  2. Click [Salvează] ÎN FEREASTRA MANAGER

  Dacă apăsați [Anulează] sau închideți Managerul,
  TOATE modificările nesalvate se pierd!
```

### Exemplu Complet: Creare Concurs Nou

1. Deschideți `Concursuri → Manager`
2. Click `➕ Adaugă Concurs`
3. Completați:

| Câmp | Valoare |
|------|---------|
| ID | `cupa-neamt` |
| Nume RO | `Cupa Județului Neamț` |
| Nume EN | `Neamț County Cup` |
| Tip | `YO` |
| Punctare | `per_qso` |
| Puncte/QSO | `2` |
| Min QSO | `25` |
| Multiplicatori | `county` |
| Categorii | `A. Seniori` / `B. Juniori` / `C. YL` / `D. Club` |
| Benzi | ☑80m ☑40m ☑20m |
| Moduri | ☑SSB ☑CW |
| Seriale | ☑ |
| Județ | ☑ |
| Lista Județe | `NT,IS,BC,SV,BT,VS` |
| Stații Obligatorii | `YP8NT` |
| Punctare Specială | `YP8NT=10` |

4. Click **[Salvează]** în editor
5. Click **[Salvează]** în Manager
6. Selectați `cupa-neamt` din dropdown-ul de concurs

---

## 📡 Tipuri de Concurs

| Tip | Descriere | Utilizare Tipică |
|-----|-----------|------------------|
| **Simplu** | Log liber, fără reguli, fără punctare | Log zilnic, testare |
| **Maraton** | Concurs de anduranță cu stații speciale și bonusuri | Maratoane naționale |
| **Ștafetă** | Concurs pe echipe, cu schimb de operatori | Ștafetele regionale |
| **YO** | Concursuri naționale YO | Concursuri FRR |
| **DX** | Concursuri internaționale | YO DX HF, CQ WW |
| **VHF** | Concursuri pe benzi VHF (2m, 6m) | Contest VHF |
| **UHF** | Concursuri pe benzi UHF (70cm, 23cm) | Contest UHF |
| **Field Day** | Ziua Câmpului — operare portabilă | ARRL/FRR Field Day |
| **Sprint** | Concursuri rapide, durată scurtă | Sprint CW/SSB |
| **QSO Party** | Concursuri informale pe state/regiuni | YO QSO Party |
| **SOTA** | Summits On The Air | Activări montane |
| **POTA** | Parks On The Air | Activări din parcuri |
| **Custom** | Tip definit complet de utilizator | Orice regulament |

---

## 🧮 Moduri de Punctare

| Mod | Descriere | Exemplu |
|-----|-----------|---------|
| `none` | Fără punctare — doar logare | Log Simplu |
| `per_qso` | Puncte fixe per QSO | 1 pt/QSO sau 2 pt/QSO |
| `per_band` | Puncte diferite per bandă | 160m=4p, 80m=3p, 40m=2p |
| `maraton` | Stații speciale cu bonusuri | YP8IC=20p, restul=1p |
| `multiplier` | Puncte QSO × multiplicatori | 150 pts × 23 județe = 3450 |
| `distance` | Bazat pe distanță (VHF/UHF) | km între locatoare |
| `custom` | Formulă personalizată | Utilizatorul definește |

### Formula de Calcul

```
Scor Total = Puncte QSO × Multiplicatori

  Puncte QSO = Σ (puncte per fiecare QSO, conform modului de punctare)
  Multiplicatori = entități unice (județe/DXCC/grid/benzi) sau 1 dacă nu se folosesc
```

---

## 🔢 Sistemul de Multiplicatori

| Tip | Ce se Numără | Sursa Datelor |
|-----|-------------|---------------|
| **Fără** (`none`) | Multiplicator = 1 | — |
| **Județe** (`county`) | Județe unice lucrate | Câmpul Notă |
| **DXCC** (`dxcc`) | Prefixe DXCC unice | Indicativul stației |
| **Bandă** (`band`) | Benzi unice folosite | Câmpul Bandă |
| **Grid** (`grid`) | Grid square-uri unice (4 caractere) | Câmpul Notă |

---

## 📻 Logare QSO-uri

### Câmpurile de Intrare

| Câmp | Obligatoriu | Pre-completat | Descriere |
|------|-------------|---------------|-----------|
| **Indicativ** | ✅ Da | Nu | Indicativul stației lucrate |
| **Bandă** | ✅ Da | `40m` (prima bandă permisă) | Banda de operare |
| **Mod** | ✅ Da | `SSB` (primul mod permis) | Modul de emisie |
| **RST S** | Nu | `59` | Raportul trimis |
| **RST R** | Nu | `59` | Raportul primit |
| **Nr S** | Nu* | Auto-increment | Numărul serial trimis (*doar dacă concursul folosește) |
| **Nr R** | Nu* | Gol | Numărul serial primit (*doar dacă concursul folosește) |
| **Notă** | Nu | Gol | Județ / Locator / Comentariu |

### Fluxul de Logare

**Rapid (minim):**
```
1. Tastați indicativul: YO3ABC
2. Apăsați ENTER
✅ QSO logat cu banda și modul selectate, RST 59/59, dată/oră UTC automate
```

**Complet:**
```
1. Indicativ:              YO3ABC
2. Bandă (dacă e diferită): 20m
3. Mod (dacă e diferit):   CW
4. RST S (dacă e diferit): 599
5. RST R (dacă e diferit): 579
6. Nr R (serial primit):   045
7. Notă/Județ:             BV
8. ENTER sau click [LOG]
✅ QSO-ul apare în tabel cu număr, puncte și toate datele
```

### Ce se Întâmplă Automat După Fiecare QSO

- ✓ Data și ora UTC se completează automat (mod Online)
- ✓ Numărul serial trimis se incrementează (+1)
- ✓ Punctele se calculează conform regulilor concursului
- ✓ QSO-ul se salvează instant în `log.json`
- ✓ Bara de informații se actualizează (total QSO + scor)
- ✓ Cursorul revine pe câmpul Indicativ

### Mod Online vs Manual

| Mod | LED | Dată/Oră | Când se Folosește |
|-----|-----|----------|-------------------|
| **Online** (☐ nebifat) | 🟢 Verde | UTC automat, câmpuri blocate | Operare în timp real |
| **Manual** (☑ bifat) | 🔴 Roșu | Editabile, format `YYYY-MM-DD` și `HH:MM` | Introducere retrospectivă (de pe hârtie) |

---

## ✏️ Editare și Ștergere QSO

### Editare QSO

**Metoda 1:** Dublu-click pe QSO-ul din tabel
**Metoda 2:** Click dreapta pe QSO → `Editează QSO`

Ce se întâmplă:
1. Câmpurile se completează cu datele QSO-ului selectat
2. Butonul **[LOG]** devine **[ACTUALIZEAZĂ]** (portocaliu)
3. Modificați ce doriți
4. Click **[ACTUALIZEAZĂ]** sau **ENTER**
5. QSO-ul se actualizează în tabel

Pentru a **anula** editarea: click **[Reset]**

### Ștergere QSO

**Metoda 1:** Click dreapta pe QSO → `Șterge QSO`
**Metoda 2:** Selectați QSO-ul + click **[Șterge]** din bara de jos

Apare confirmare: *„Sigur ștergeți QSO-ul selectat?"*
- **[Da]** = șters definitiv
- **[Nu]** = anulat

---

## 📊 Statistici și Validare

### Statistici

Click **[Statistici]** — afișează:
- Total QSO-uri
- QSO-uri per bandă
- QSO-uri per mod
- Stații unice lucrate
- Stații obligatorii lucrate / lipsă
- QSO Points / Multipliers / Scor Total (dacă concursul are punctare)

### Validare

Click **[Validează]** — verifică:
- Numărul minim de QSO-uri (dacă e definit)
- Stații obligatorii lucrate
- Benzi permise (semnalează QSO-uri pe benzi interzise)
- Moduri permise (semnalează QSO-uri cu moduri interzise)
- Eligibilitate diplomă

Rezultate posibile:
```
✅ SUCCES: "Log valid! Total: 47 QSO, Scor: 564"
           "Eligibil diplomă: DA"

❌ ERORI:  "Minim 50 QSO necesare, aveți 47"
           "Lipsesc stații obligatorii: YP8NT"
           "QSO #12 (DX1ABC) bandă nepermisă: 6m"
           "QSO #23 (YO5ZZ) mod nepermis: FT8"
```

---

## 💾 Backup

### Backup Manual

Click **[Backup]** → *„Backup creat cu succes!"*

### Backup Automat

La **fiecare închidere** a aplicației (dacă confirmați salvarea), se creează automat un backup.

### Locația Backup-urilor

```
📁 C:\RadioLog\backups\
├── log_backup_20260115_143000.json     ← cel mai vechi
├── log_backup_20260115_160000.json
├── log_backup_20260116_091500.json
└── log_backup_20260116_143000.json     ← cel mai recent
```

Se păstrează **maxim 50** de backup-uri. Cele mai vechi se șterg automat.

### Restaurare din Backup

Dacă pierdeți logul sau ceva merge prost:
1. Închideți aplicația
2. Mergeți în folderul `backups\`
3. Alegeți cel mai recent fișier: `log_backup_XXXXXXXX_XXXXXX.json`
4. Copiați-l în folderul principal
5. Redenumiți-l în `log.json` (înlocuiți fișierul existent)
6. Reporniți aplicația — logul este restaurat!

---

## 📤 Export Log

Click **[Export]** → alegeți formatul:

### Formate Disponibile

| Format | Extensie | Scop Principal |
|--------|----------|----------------|
| **Cabrillo** | `.log` | Trimitere log de concurs la organizator. Format standard internațional. |
| **ADIF** | `.adi` | Încărcare pe LoTW, eQSL, Club Log, QRZ.com. Import în alte programe de logging. |
| **CSV** | `.csv` | Deschidere în Excel / Google Sheets. Analiză, statistici, printare tabelară. |

### Exemple Fișiere Exportate

**Cabrillo:**
```
START-OF-LOG: 3.0
CONTEST: YO DX HF Contest
CALLSIGN: YO8ACR
LOCATION: KN37
CATEGORY: ALL
QSO:   40m SSB  2026-01-15 14:30 YO8ACR        59  YO3ABC        59
END-OF-LOG:
```

**ADIF:**
```
<ADIF_VER:5>3.1.0
<EOH>
<CALL:6>YO3ABC<BAND:3>40m<MODE:3>SSB<QSO_DATE:8>20260115<TIME_ON:6>143000
<RST_SENT:2>59<RST_RCVD:2>59<EOR>
```

**CSV:**
```
Nr,Date,Time,Call,Band,Mode,RST_Sent,RST_Rcvd,Note,Score
47,2026-01-15,14:30,YO3ABC,40m,SSB,59,59,NT,1
```

Fișierele se salvează în **folderul aplicației** cu nume automate:
```
cabrillo_maraton_20260115_1430.log
adif_20260115_1430.adi
log_20260115_1430.csv
```

---

## 📁 Structura Completă a Folderului

```
📁 C:\RadioLog\
│
│── FIȘIERE PRINCIPALE ──────────────────────────────
├── YO_Log_PRO_v14.exe              ← executabilul (NU se mută!)
├── config.json                      ← setările stației
├── log.json                         ← QSO-urile
├── contests.json                    ← concursurile configurate
│
│── EXPORTURI ───────────────────────────────────────
├── cabrillo_maraton_20260115_1430.log
├── cabrillo_yo-dx-hf_20260116_0900.log
├── adif_20260115_1430.adi
├── adif_20260116_0900.adi
├── log_20260115_1430.csv
│
│── EXPORTURI CONCURSURI ────────────────────────────
├── contests_export_20260115_1430.json
│
│── BACKUP-URI ──────────────────────────────────────
└── 📁 backups\
    ├── log_backup_20260115_143000.json
    ├── log_backup_20260115_160000.json
    ├── log_backup_20260116_091500.json
    └── log_backup_20260116_143000.json
        (maxim 50, cele mai vechi se șterg automat)
```

---

## 🚫 Ce NU Trebuie Să Faceți

| ❌ Acțiune Greșită | ⚠️ Consecință |
|---------------------|---------------|
| Rulați din interiorul arhivei ZIP/RAR | Fișierele create nu se salvează permanent |
| Mutați executabilul fără fișierele JSON | Se creează fișiere NOI goale, pierdeți acces la date |
| Ștergeți `config.json` | Se recreează cu valori implicite, trebuie reconfigurat |
| Ștergeți `log.json` | Se recreează GOL — QSO-urile se pierd (restaurați din backup!) |
| Ștergeți `contests.json` | Se recreează cu cele 7 implicite, concursurile create se pierd |
| Editați manual JSON fără backup | Un JSON invalid blochează încărcarea |
| Puneți în `C:\Program Files\` | Necesită drepturi administrator pentru scriere |

---

## ✅ Ce Trebuie Să Faceți

| ✅ Acțiune Corectă | 💡 De ce |
|---------------------|----------|
| Extrageți într-un folder dedicat ÎNAINTE de prima rulare | Fișierele se creează în folderul executabilului |
| Configurați stația la prima pornire | Indicativul apare în exporturi și header |
| Faceți Backup regulat | Protecție împotriva pierderii datelor |
| Validați log-ul înainte de export | Detectează erori conform regulilor concursului |
| Salvați setările din Manager cu [Salvează] | Altfel modificările se pierd |
| Dacă mutați folderul, mutați TOTUL | exe + JSON + backups = unitate inseparabilă |
| Copiați periodic tot folderul pe stick USB / cloud | Backup extern complet |

---

## 🆘 Depanare

| Problemă | Soluție |
|----------|---------|
| Aplicația nu pornește | Verificați Python 3.8+ instalat SAU folosiți executabilul .exe |
| Am pierdut logul | Mergeți în `backups\` → copiați ultimul backup → redenumiți-l `log.json` → reporniți |
| Concursurile mele au dispărut | Dacă ați șters `contests.json`, se recreează cu cele implicite. Importați dintr-un export anterior din Manager → [📥 Importă] |
| Nu pot salva / nu apare nimic | Verificați că folderul NU este read-only și că NU rulați din arhivă |
| Benzile/modurile nu apar toate | Normal! Fiecare concurs filtrează benzile și modurile permise. Schimbați pe `simplu` pentru acces la toate |
| Am mutat executabilul și logul e gol | Fișierele JSON au rămas în folderul vechi. Mutați-le lângă executabil |
| JSON invalid / aplicația nu se deschide corect | Restaurați fișierul JSON din backup sau ștergeți-l (se recreează cu valori implicite) |
| Scorul nu apare în tabel | Concursul selectat are `scoring_mode: none`. Editați concursul sau alegeți altul |
| Câmpurile serial nu apar | Concursul nu are `use_serial` activat. Editați concursul din Manager |

---

## 📌 Checklist Prima Utilizare

```
☐  1. Creez folder dedicat (ex: C:\RadioLog\)
☐  2. Copiez executabilul în folder
☐  3. Pornesc aplicația (se creează config.json, log.json, contests.json)
☐  4. Setări → Indicativ + Locator + Județ → [Salvează]
☐  5. Aleg limba (ro / en) din colțul dreapta sus
☐  6. Selectez concursul dorit (sau creez unul nou din 🏆 Manager)
☐  7. Aleg Categorie + Județ → [💾 Salvează]
☐  8. Loghez primul QSO: tastez indicativul → ENTER
☐  9. Verific [Statistici]
☐ 10. Fac un [Backup] manual
☐ 11. Gata! Operez normal. 73!
```

---

---

# 🇬🇧 ENGLISH DOCUMENTATION

## 📋 Description

**YO Log PRO v14.0** is an amateur radio logging application developed in Python with a Tkinter graphical interface. The application features a **fully configurable contest manager**, allowing users to create, edit, duplicate and delete contests with custom scoring rules, categories, bands, modes and multipliers.

### Main Features

- **Fast logging** — callsign + ENTER, with auto-fill UTC date/time
- **Contest manager** — add, edit, duplicate, delete, import, export contests
- **12 contest types** — Simple, Marathon, Relay, YO, DX, VHF, UHF, Field Day, Sprint, QSO Party, SOTA, POTA, Custom
- **7 scoring modes** — none, per_qso, per_band, maraton, multiplier, distance, custom
- **5 multiplier types** — None, Counties, DXCC, Band, Grid Square
- **Adaptive UI** — bands, modes, columns and fields adjust per contest
- **Export** — Cabrillo (.log), ADIF (.adi), CSV (.csv)
- **Validation** — automatic check against contest rules
- **Auto-backup** — on every exit + manual, max 50 retained
- **Bilingual** — Romanian and English, instant switch
- **Dark theme** — modern, professional interface

---

## 🚨 IMPORTANT: Dedicated Folder Rule

```
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║   THE EXECUTABLE MUST REMAIN IN ITS DEDICATED FOLDER!                ║
║                                                                       ║
║   The application creates configuration, log and backup files         ║
║   IN THE SAME FOLDER where the executable is located.                ║
║                                                                       ║
║   ❌  DO NOT run directly from archive (ZIP/RAR)                      ║
║   ❌  DO NOT move the executable without the JSON files               ║
║   ❌  DO NOT delete the auto-created JSON files                       ║
║   ❌  DO NOT place in C:\Program Files\ (requires admin rights)       ║
║   ✅  Extract EVERYTHING to a dedicated folder BEFORE first run       ║
║   ✅  Create a Desktop shortcut for quick access                      ║
║   ✅  If moving, move EVERYTHING: exe + JSON + backups\               ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
```

---

## 📥 Installation and First Run

### System Requirements

| Component | Requirement |
|-----------|-------------|
| Python | 3.8 or newer (only for .py script) |
| Tkinter | Included with Python |
| OS | Windows 7+, Linux, macOS |
| Disk space | ~5 MB + space for logs |
| .exe executable | Does NOT require Python installed |

### Step 1 — Prepare Folder

Create a dedicated folder:
```
Recommended:
  C:\RadioLog\                           — Windows
  ~/RadioLog/                            — Linux / macOS
  Desktop\YO_Log_PRO\                    — on Desktop
```

Copy the executable (or .py script) into this folder.

### Step 2 — First Run

```bash
# With executable (Windows):
Double-click YO_Log_PRO_v14.exe

# With Python (all platforms):
cd C:\RadioLog
python yo_log_pro.py

# Linux / macOS:
cd ~/RadioLog
python3 yo_log_pro.py
```

### Step 3 — Auto-Created Files

On first run, the application automatically creates **3 files**:

| File | Initial Content |
|------|----------------|
| `config.json` | Callsign: YO8ACR, Locator: KN37, County: NT, Language: ro |
| `log.json` | `[]` — empty, no QSOs |
| `contests.json` | 7 pre-configured contests ready to use |

### (Optional) Desktop Shortcut

```
Windows: Right-click executable → Send to → Desktop (create shortcut)

⚠️ Move only the SHORTCUT, NOT the executable!
```

---

## ⚙️ Station Setup

**This is the first mandatory action on first use.**

1. Click **[Settings]** button in the bottom bar
2. Fill in:

| Field | What to Enter | Example |
|-------|--------------|---------|
| **Callsign** | Your callsign | `YO8XYZ` |
| **Locator** | Maidenhead locator (4-6 chars) | `KN37` |
| **County** | County abbreviation | `NT` |
| **Address** | City/location (optional) | `Târgu Neamț` |
| **Font Size** | 10-16 recommended | `12` |

3. Click **[Save]**

---

## 🌐 Language Selection

Top-right corner of the window:

| Selector | Language |
|----------|---------|
| `ro` | 🇷🇴 Romanian (default) |
| `en` | 🇬🇧 English |

The interface completely and instantly rebuilds on language change.

---

## 🏆 Contest Selection and Configuration

### Pre-configured Contests

| ID | Type | Description | Scoring | Min QSO |
|----|------|-------------|---------|---------|
| `simplu` | Simple | Free log, no rules | none | 0 |
| `maraton` | Marathon | Special stations, bonuses | maraton | 100 |
| `stafeta` | Relay | Team contest with serials | per_qso | 50 |
| `yo-dx-hf` | DX | YO DX HF — band points | per_band | 0 |
| `yo-vhf` | VHF | VHF/UHF — distance-based | distance | 0 |
| `field-day` | Field Day | Portable operation | per_qso | 0 |
| `sprint` | Sprint | Quick contest with serials | per_qso | 0 |

### Quick Selection

**Method 1** — Selector in top-right:
```
[simplu ▼] → click and choose desired contest
```

**Method 2** — From menu:
```
Contests → ⚡ Switch → [desired contest]
```

On contest change, the interface auto-rebuilds:
- Bands and modes in dropdowns are filtered
- Serial number fields appear/disappear
- Score column appears/disappears
- Note label becomes "County / Note" if contest uses counties

### Category and County Selection

After choosing a contest, in the control area:
```
Category: [A. Seniors YO ▼]   County: [NT ▼]   [💾 Save]
```

1. Choose your participation category
2. Choose county (if contest uses it)
3. Click **[💾 Save]** — **MANDATORY** to retain selection

---

## 🏆 Contest Manager

The heart of v14.0. Open from:
- **Menu:** `Contests → Manager`
- **Button:** `🏆 Contests` in the bottom bar

### Available Operations

| Button | Operation | Description |
|--------|-----------|-------------|
| ➕ | **Add** | Create new contest from scratch |
| ✏️ | **Edit** | Modify existing contest rules (double-click or button) |
| 📋 | **Duplicate** | Copy a contest as starting point |
| 🗑️ | **Delete** | Remove a contest (except "Simple Log") |
| 📤 | **Export** | Save all contests as JSON file |
| 📥 | **Import** | Load contests from external JSON file |

### Configurable Fields per Contest

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| **Contest ID** | text | Unique, no spaces, lowercase | `county-cup` |
| **Name RO** | text | Name displayed in Romanian | `Cupa Județului` |
| **Name EN** | text | Name displayed in English | `County Cup` |
| **Contest Type** | selector | General category | `YO` |
| **Scoring Mode** | selector | Score algorithm | `per_qso` |
| **Points per QSO** | number | Base points | `2` |
| **Min QSO** | number | Validation threshold | `25` |
| **Multipliers** | selector | Multiplier type | `county` |
| **Categories** | multiline text | One per line | `A. Seniors` / `B. Juniors` |
| **Allowed Bands** | checkboxes | Check desired bands | ☑80m ☑40m ☑20m |
| **Allowed Modes** | checkboxes | Check desired modes | ☑SSB ☑CW |
| **Serial Numbers** | checkbox | Enable Nr S / Nr R | ☑ |
| **Use County** | checkbox | Enable county selector | ☑ |
| **County List** | text | Comma-separated | `NT,IS,BC,SV` |
| **Required Stations** | multiline text | One callsign per line | `YP8NT` |
| **Special Scoring** | multiline text | `CALLSIGN=POINTS` per line | `YP8NT=10` |
| **Band Points** | multiline text | `BAND=POINTS` per line | `160m=4` |

### ⚠️ Saving in Manager

```
After any modification (add/edit/delete/duplicate/import):

  1. Click [Save] IN THE CONTEST EDITOR (if you edited)
  2. Click [Save] IN THE MANAGER WINDOW

  If you click [Cancel] or close the Manager,
  ALL unsaved changes are lost!
```

---

## 📡 Contest Types

| Type | Description | Typical Use |
|------|-------------|-------------|
| **Simplu** | Free log, no rules, no scoring | Daily log, testing |
| **Maraton** | Endurance contest with special stations | National marathons |
| **Stafeta** | Team contest, operator relay | Regional relays |
| **YO** | YO national contests | FRR contests |
| **DX** | International contests | YO DX HF, CQ WW |
| **VHF** | VHF band contests (2m, 6m) | VHF Contest |
| **UHF** | UHF band contests (70cm, 23cm) | UHF Contest |
| **Field Day** | Portable operation | ARRL/FRR Field Day |
| **Sprint** | Quick, short-duration contests | CW/SSB Sprint |
| **QSO Party** | Informal state/region contests | YO QSO Party |
| **SOTA** | Summits On The Air | Mountain activations |
| **POTA** | Parks On The Air | Park activations |
| **Custom** | Fully user-defined type | Any ruleset |

---

## 🧮 Scoring Modes

| Mode | Description | Example |
|------|-------------|---------|
| `none` | No scoring — logging only | Simple Log |
| `per_qso` | Fixed points per QSO | 1 pt/QSO or 2 pts/QSO |
| `per_band` | Different points per band | 160m=4pts, 80m=3pts |
| `maraton` | Special stations with bonuses | YP8IC=20pts, others=1pt |
| `multiplier` | QSO points × multipliers | 150 pts × 23 counties = 3450 |
| `distance` | Distance-based (VHF/UHF) | km between locators |
| `custom` | Custom formula | User defines rules |

### Score Calculation Formula

```
Total Score = QSO Points × Multipliers

  QSO Points = Σ (points for each QSO, per scoring mode)
  Multipliers = unique entity count (counties/DXCC/grid/bands) or 1 if none
```

---

## 🔢 Multiplier System

| Type | What is Counted | Data Source |
|------|-----------------|-------------|
| **None** (`none`) | Multiplier = 1 | — |
| **Counties** (`county`) | Unique counties worked | Note field |
| **DXCC** (`dxcc`) | Unique DXCC prefixes | Station callsign |
| **Band** (`band`) | Unique bands used | Band field |
| **Grid** (`grid`) | Unique grid squares (4 chars) | Note field |

---

## 📻 QSO Logging

### Input Fields

| Field | Required | Pre-filled | Description |
|-------|----------|------------|-------------|
| **Callsign** | ✅ Yes | No | Worked station callsign |
| **Band** | ✅ Yes | First allowed band | Operating band |
| **Mode** | ✅ Yes | First allowed mode | Emission mode |
| **RST S** | No | `59` | Report sent |
| **RST R** | No | `59` | Report received |
| **Nr S** | No* | Auto-increment | Serial number sent (*if contest uses serials) |
| **Nr R** | No* | Empty | Serial number received (*if contest uses serials) |
| **Note** | No | Empty | County / Locator / Comment |

### Logging Flow

**Quick (minimum):**
```
1. Type callsign: YO3ABC
2. Press ENTER
✅ QSO logged with selected band/mode, RST 59/59, auto UTC date/time
```

**Complete:**
```
1. Callsign:                   YO3ABC
2. Band (if different):        20m
3. Mode (if different):        CW
4. RST S (if different):       599
5. RST R (if different):       579
6. Nr R (serial received):     045
7. Note/County:                BV
8. ENTER or click [LOG]
✅ QSO appears in table with number, score and all data
```

### What Happens Automatically After Each QSO

- ✓ UTC date and time auto-filled (Online mode)
- ✓ Sent serial number incremented (+1)
- ✓ Score calculated per contest rules
- ✓ QSO saved instantly to `log.json`
- ✓ Info bar updated (total QSOs + score)
- ✓ Cursor returns to Callsign field

### Online vs Manual Mode

| Mode | LED | Date/Time | When to Use |
|------|-----|-----------|-------------|
| **Online** (☐ unchecked) | 🟢 Green | Auto UTC, fields locked | Real-time operation |
| **Manual** (☑ checked) | 🔴 Red | Editable, format `YYYY-MM-DD` and `HH:MM` | Retrospective entry (from paper log) |

---

## ✏️ Editing and Deleting QSOs

### Edit QSO

**Method 1:** Double-click on QSO in table
**Method 2:** Right-click on QSO → `Edit QSO`

1. Fields fill with selected QSO data
2. **[LOG]** button becomes **[UPDATE]** (orange)
3. Modify what you need
4. Click **[UPDATE]** or **ENTER**
5. QSO updates in table

To **cancel** editing: click **[Reset]**

### Delete QSO

**Method 1:** Right-click on QSO → `Delete QSO`
**Method 2:** Select QSO + click **[Delete]** in bottom bar

Confirmation dialog: *"Delete selected QSO?"*
- **[Yes]** = permanently deleted
- **[No]** = cancelled

---

## 📊 Statistics and Validation

### Statistics

Click **[Statistics]** — displays:
- Total QSOs
- QSOs per band
- QSOs per mode
- Unique stations worked
- Required stations worked / missing
- QSO Points / Multipliers / Total Score (if contest has scoring)

### Validation

Click **[Validate]** — checks:
- Minimum QSO count (if defined)
- Required stations worked
- Allowed bands (flags QSOs on forbidden bands)
- Allowed modes (flags QSOs with forbidden modes)
- Diploma eligibility

---

## 💾 Backup System

### Manual Backup

Click **[Backup]** → *"Backup created!"*

### Automatic Backup

On **every exit** (if you confirm saving), a backup is automatically created.

### Backup Location

```
📁 C:\RadioLog\backups\
├── log_backup_20260115_143000.json     ← oldest
├── ...
└── log_backup_20260116_143000.json     ← newest
```

**Maximum 50** backups retained. Oldest are auto-deleted.

### Restoring from Backup

If you lose your log or something goes wrong:
1. Close the application
2. Go to `backups\` folder
3. Choose the most recent file: `log_backup_XXXXXXXX_XXXXXX.json`
4. Copy it to the main folder
5. Rename it to `log.json` (replace existing file)
6. Restart the application — log is restored!

---

## 📤 Log Export

Click **[Export]** → choose format:

| Format | Extension | Primary Use |
|--------|-----------|-------------|
| **Cabrillo** | `.log` | Contest log submission to organizer. International standard. |
| **ADIF** | `.adi` | Upload to LoTW, eQSL, Club Log, QRZ.com. Import into other logging software. |
| **CSV** | `.csv` | Open in Excel / Google Sheets. Analysis, statistics, tabular printing. |

Files are saved in the **application folder** with automatic names:
```
cabrillo_maraton_20260115_1430.log
adif_20260115_1430.adi
log_20260115_1430.csv
```

---

## 📁 Complete Folder Structure

```
📁 C:\RadioLog\
│
│── MAIN FILES ──────────────────────────────────────
├── YO_Log_PRO_v14.exe              ← executable (DO NOT move!)
├── config.json                      ← station settings
├── log.json                         ← your QSOs
├── contests.json                    ← configured contests
│
│── EXPORTS ─────────────────────────────────────────
├── cabrillo_maraton_20260115_1430.log
├── adif_20260115_1430.adi
├── log_20260115_1430.csv
│
│── CONTEST EXPORTS ─────────────────────────────────
├── contests_export_20260115_1430.json
│
│── BACKUPS ─────────────────────────────────────────
└── 📁 backups\
    ├── log_backup_20260115_143000.json
    └── log_backup_20260116_143000.json
        (max 50, oldest auto-deleted)
```

---

## 🚫 What NOT To Do

| ❌ Wrong Action | ⚠️ Consequence |
|-----------------|----------------|
| Run from inside ZIP/RAR archive | Created files are not permanently saved |
| Move executable without JSON files | New empty files created, lose access to data |
| Delete `config.json` | Recreated with defaults, must reconfigure |
| Delete `log.json` | Recreated EMPTY — all QSOs lost (restore from backup!) |
| Delete `contests.json` | Recreated with 7 defaults, your custom contests lost |
| Manually edit JSON without backup | Invalid JSON blocks loading |
| Place in `C:\Program Files\` | Requires administrator rights for writing |

---

## ✅ What To Do

| ✅ Correct Action | 💡 Why |
|-------------------|--------|
| Extract to dedicated folder BEFORE first run | Files are created in executable's folder |
| Configure station on first launch | Callsign appears in exports and header |
| Backup regularly | Protection against data loss |
| Validate log before export | Detects errors per contest rules |
| Save contest settings in Manager with [Save] | Otherwise changes are lost |
| If moving folder, move EVERYTHING | exe + JSON + backups = inseparable unit |
| Periodically copy entire folder to USB/cloud | Complete external backup |

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| Application doesn't start | Verify Python 3.8+ installed OR use .exe on Windows |
| Lost my log | Go to `backups\` → copy latest backup → rename to `log.json` → restart |
| My contests disappeared | If you deleted `contests.json`, it recreates with defaults. Import from export file via Manager → [📥 Import] |
| Can't save / nothing appears | Verify folder is NOT read-only and NOT running from archive |
| Not all bands/modes appear | Normal! Each contest filters allowed bands and modes. Switch to `simplu` for full access |
| Moved executable and log is empty | JSON files remained in old folder. Move them next to executable |
| Invalid JSON / app won't open correctly | Restore JSON file from backup or delete it (recreates with defaults) |
| Score doesn't appear in table | Selected contest has `scoring_mode: none`. Edit contest or choose another |
| Serial fields don't appear | Contest doesn't have `use_serial` enabled. Edit contest in Manager |

---

## 📌 First Use Checklist

```
☐  1.  Create dedicated folder (e.g. C:\RadioLog\)
☐  2.  Copy executable into folder
☐  3.  Launch application (config.json, log.json, contests.json auto-created)
☐  4.  Settings → Callsign + Locator + County → [Save]
☐  5.  Choose language (ro / en) from top-right corner
☐  6.  Select contest or create new one from 🏆 Manager
☐  7.  Choose Category + County → [💾 Save]
☐  8.  Log first QSO: type callsign → ENTER
☐  9.  Check [Statistics]
☐  10. Make a manual [Backup]
☐  11. Done! Operate normally. 73!
```

---

---

# 🔧 SECȚIUNE TEHNICĂ / TECHNICAL SECTION

## 🏗️ Arhitectura Aplicației / Application Architecture

```
┌──────────────────────────────────────────────────────┐
│                    RadioLogApp                         │
│                  (Main Tk Window)                      │
├───────────┬───────────┬────────────┬─────────────────┤
│  Header   │  Input    │   Log      │   Button        │
│  Bar      │  Area     │   View     │   Bar           │
│  (status, │  (fields, │ (Treeview, │  (settings,     │
│  lang,    │  manual   │  dynamic   │   contests,     │
│  contest) │  dt, cat) │  columns)  │   export, etc.) │
├───────────┴───────────┴────────────┴─────────────────┤
│                                                       │
│  ┌──────────────┐  ┌──────────────────────────────┐  │
│  │ DataManager   │  │      ScoringEngine            │  │
│  │ • save_json   │  │  • calculate_qso_score        │  │
│  │ • load_json   │  │  • count_multipliers          │  │
│  │ • backup      │  │  • calculate_total_score      │  │
│  └──────────────┘  │  • validate_log                │  │
│                      └──────────────────────────────┘  │
│  ┌──────────────┐  ┌──────────────────────────────┐  │
│  │ Lang          │  │  ContestManagerDialog         │  │
│  │ • set(lang)   │  │  • add / edit / delete        │  │
│  │ • get()       │  │  • duplicate                  │  │
│  │ • t(key)      │  │  • import / export            │  │
│  └──────────────┘  └──────────────────────────────┘  │
│                      ┌──────────────────────────────┐  │
│                      │  ContestEditorDialog          │  │
│                      │  • full contest config form   │  │
│                      │  • bands/modes checkboxes     │  │
│                      │  • scoring/multiplier setup   │  │
│                      └──────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

### Clase / Classes

| Clasă / Class | Responsabilitate / Responsibility |
|---------------|-----------------------------------|
| `RadioLogApp` | Fereastra principală, UI complet, logica aplicației / Main window, full UI, application logic |
| `DataManager` | Citire/scriere JSON, backup atomic / JSON read/write, atomic backup |
| `ScoringEngine` | Calcul punctaje, multiplicatori, validare / Score calculation, multipliers, validation |
| `Lang` | Manager de limbă (RO/EN) cu dicționare de traduceri / Language manager with translation dictionaries |
| `ContestManagerDialog` | CRUD concursuri: listare, adăugare, editare, ștergere, duplicare, import/export / Contest CRUD operations |
| `ContestEditorDialog` | Formular complet de editare concurs cu scroll / Full scrollable contest edit form |

### Constante / Constants

| Constantă / Constant | Conținut / Content |
|----------------------|-------------------|
| `BANDS_HF` | 160m → 10m |
| `BANDS_VHF` | 6m, 2m |
| `BANDS_UHF` | 70cm, 23cm |
| `BANDS_ALL` | HF + VHF + UHF |
| `MODES_ALL` | SSB, CW, DIGI, FT8, FT4, RTTY, AM, FM, PSK31, SSTV, JT65 |
| `SCORING_MODES` | none, per_qso, per_band, maraton, multiplier, distance, custom |
| `CONTEST_TYPES` | Simplu, Maraton, Stafeta, YO, DX, VHF, UHF, Field Day, Sprint, QSO Party, SOTA, POTA, Custom |
| `TRANSLATIONS` | Dicționare complete RO + EN / Complete RO + EN dictionaries |
| `DEFAULT_CONTESTS` | 7 concursuri predefinite / 7 pre-configured contests |
| `THEME` | Culorile interfeței dark / Dark interface colors |

---

## 📄 Structura Fișierelor JSON / JSON File Structure

### config.json

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

| Cheie / Key | Tip / Type | Descriere / Description |
|-------------|-----------|------------------------|
| `call` | string | Indicativul stației / Station callsign |
| `loc` | string | Locator Maidenhead |
| `jud` | string | Județ / County |
| `addr` | string | Adresă / Address |
| `cat` | int | Index categorie / Category index |
| `fs` | int | Mărime font / Font size |
| `contest` | string | ID concurs activ / Active contest ID |
| `county` | string | Județ selectat / Selected county |
| `lang` | string | Limbă: "ro" sau "en" / Language |
| `manual_datetime` | bool | Mod manual activat / Manual mode enabled |

### log.json

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
    "ss": "001",
    "sr": "045"
  }
]
```

| Cheie / Key | Descriere / Description |
|-------------|------------------------|
| `c` | Indicativ / Callsign |
| `b` | Bandă / Band |
| `m` | Mod / Mode |
| `s` | RST trimis / RST sent |
| `r` | RST primit / RST received |
| `n` | Notă/Județ/Locator / Note/County/Locator |
| `d` | Data (YYYY-MM-DD) / Date |
| `t` | Ora (HH:MM) / Time |
| `ss` | Nr serial trimis / Serial sent (opțional/optional) |
| `sr` | Nr serial primit / Serial received (opțional/optional) |

### contests.json — Structură per Concurs / Per Contest Structure

```json
{
  "yo-dx-hf": {
    "name_ro": "YO DX HF Contest",
    "name_en": "YO DX HF Contest",
    "contest_type": "DX",
    "categories": [
      "A. Single-Op All Band High",
      "B. Single-Op All Band Low",
      "C. Single-Op Single Band",
      "D. Multi-Op Single TX",
      "E. Multi-Op Multi TX"
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
    "county_list": ["AB","AR","AG","BC","BH","BN","BT","BV","BR","BZ",
                     "CS","CL","CJ","CT","CV","DB","DJ","GL","GR","GJ",
                     "HR","HD","IL","IS","IF","MM","MH","MS","NT","OT",
                     "PH","SM","SJ","SB","SV","TR","TM","TL","VS","VL",
                     "VN","B"],
    "multiplier_type": "dxcc",
    "band_points": {
      "160m": 4,
      "80m": 3,
      "40m": 2,
      "20m": 1,
      "15m": 1,
      "10m": 2
    },
    "exchange_fields": [],
    "is_default": false
  }
}
```

| Cheie / Key | Tip / Type | Descriere / Description |
|-------------|-----------|------------------------|
| `name_ro` | string | Numele în română / Romanian name |
| `name_en` | string | Numele în engleză / English name |
| `contest_type` | string | Tipul concursului / Contest type |
| `categories` | array | Lista categoriilor / Category list |
| `scoring_mode` | string | Modul de punctare / Scoring mode |
| `points_per_qso` | int | Puncte de bază per QSO / Base points per QSO |
| `min_qso` | int | Minim QSO pentru validare / Minimum QSOs for validation |
| `allowed_bands` | array | Benzile permise / Allowed bands |
| `allowed_modes` | array | Modurile permise / Allowed modes |
| `required_stations` | array | Stațiile obligatorii / Required stations |
| `special_scoring` | object | `{CALL: puncte}` / `{CALL: points}` |
| `use_serial` | bool | Numere seriale / Serial numbers |
| `use_county` | bool | Selector județ / County selector |
| `county_list` | array | Județe valide / Valid counties |
| `multiplier_type` | string | Tip multiplicator / Multiplier type |
| `band_points` | object | `{bandă: puncte}` / `{band: points}` |
| `is_default` | bool | Protejat la ștergere / Protected from deletion |

---

## 🛠️ Dezvoltare și Contribuții / Development and Contributing

### Tehnologii / Technologies

| Component | Tehnologie / Technology |
|-----------|------------------------|
| Limbaj / Language | Python 3.8+ |
| GUI | Tkinter (built-in, fără dependențe externe / no external dependencies) |
| Date / Data | JSON (persistență / persistence) |
| Distribuție / Distribution | PyInstaller (opțional / optional) |

### Rulare în Mod Dezvoltare / Development Run

```bash
# Clonați / Clone
git clone https://github.com/yo8acr/yo-log-pro.git
cd yo-log-pro

# Rulați / Run
python yo_log_pro.py
```

### Contribuții / Contributing

1. Fork repository-ul / Fork the repository
2. Creați un branch / Create a branch: `git checkout -b feature/noua-functie`
3. Commit: `git commit -m "Descriere modificare"`
4. Push: `git push origin feature/noua-functie`
5. Deschideți un Pull Request / Open a Pull Request

---

## 📦 Creare Executabil / Build Executable

### Windows (.exe)

```bash
# Instalați PyInstaller / Install PyInstaller
pip install pyinstaller

# Construiți / Build
pyinstaller --onefile --windowed --name "YO_Log_PRO_v14" yo_log_pro.py

# Executabilul se află în / Executable is in:
# dist\YO_Log_PRO_v14.exe
```

### Linux (AppImage / binary)

```bash
pip install pyinstaller
pyinstaller --onefile --name "yo_log_pro" yo_log_pro.py

# Result: dist/yo_log_pro
chmod +x dist/yo_log_pro
```

### macOS (.app)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "YO_Log_PRO" yo_log_pro.py

# Result: dist/YO_Log_PRO.app
```

### ⚠️ După Construire / After Build

```
Copiați executabilul într-un folder dedicat ÎNAINTE de distribuire!
Copy the executable to a dedicated folder BEFORE distributing!

📁 YO_Log_PRO\
└── YO_Log_PRO_v14.exe    ← doar executabilul, restul se creează automat
                              only the executable, rest auto-created
```

---

## 📋 Changelog

### v14.0 (2025) — Versiune Curentă / Current Version

**Nou / New:**
- ✅ Manager de Concursuri complet configurabil (adaugă/editează/duplică/șterge)
- ✅ 12 tipuri de concurs: Simplu, Maraton, Ștafetă, YO, DX, VHF, UHF, Field Day, Sprint, QSO Party, SOTA, POTA, Custom
- ✅ 7 moduri de punctare: none, per_qso, per_band, maraton, multiplier, distance, custom
- ✅ 5 tipuri de multiplicatori: Fără, Județe, DXCC, Bandă, Grid
- ✅ Import/Export concursuri JSON între utilizatori
- ✅ UI adaptiv — benzi, moduri, coloane, câmpuri se ajustează per concurs
- ✅ Numere seriale opționale per concurs cu auto-increment
- ✅ Coloana Scor dinamică în treeview
- ✅ Coloana Nr. pentru numerotare QSO-uri
- ✅ Meniu „Concursuri" cu sub-meniu switch rapid

**Modificat / Changed:**
- 🔄 Eliminat concursurile hardcodate (Cupa Moldovei, etc.)
- 🔄 ScoringEngine rescris complet cu suport multi-mod
- 🔄 Reconstruire completă UI la schimbarea concursului
- 🔄 Benzi și moduri filtrate automat per concurs

**Protejat / Protected:**
- 🔒 Concursul „Log Simplu" (`simplu`) nu se poate șterge — fallback

### v13.0 (2025)
- Manager multi-contest cu concursuri predefinite
- Export Cabrillo / ADIF / CSV
- Validare log per concurs
- Interfață bilingvă RO/EN
- Temă dark profesională
- Sistem de backup automat (maxim 50)

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
  <em>🇬🇧 "Amateur Radio — the hobby that connects the world"</em>
</p>
```

---

## 📊 Ce Conține README-ul — Rezumat

| Secțiune | Conținut |
|----------|---------|
| **Badges** | Versiune, Python, Licență, Platforme |
| **Descriere + Screenshot** | RO + EN, funcționalități principale, captură ASCII |
| **⚠️ Regula Folderului** | Avertizare prominentă — executabilul creează fișiere |
| **Instalare + Prima Pornire** | Cerințe, creare folder, fișiere auto-create |
| **Configurare Stație** | Pași detaliați cu tabel de câmpuri |
| **Selectare Limbă** | RO/EN switch |
| **Alegere Concurs** | 7 predefinite + instrucțiuni creare concurs nou |
| **Manager Concursuri** | Operații CRUD, câmpuri configurabile, exemplu complet |
| **Tipuri de Concurs** | 12 tipuri cu descriere și utilizare |
| **Moduri de Punctare** | 7 moduri cu formulă de calcul |
| **Multiplicatori** | 5 tipuri cu sursa datelor |
| **Logare QSO** | Câmpuri, flux rapid/complet, auto-acțiuni |
| **Editare/Ștergere** | Metode multiple, confirmare |
| **Statistici + Validare** | Ce afișează, mesaje de eroare |
| **Backup** | Manual + automat, restaurare pas cu pas |
| **Export** | Cabrillo/ADIF/CSV cu exemple și scop |
| **Structura Folder** | Arborescență completă |
| **Ce NU/Ce DA** | Tabele clare cu acțiuni și consecințe |
| **Depanare** | 9 probleme frecvente cu soluții |
| **Checklist** | 11 pași numerotați cu checkbox |
| **Documentație EN** | Totul tradus integral în engleză |
| **Arhitectură** | Diagramă, clase, constante |
| **Structură JSON** | Toate cele 3 fișiere cu tabele de chei |
| **Build** | PyInstaller Windows/Linux/macOS |
| **Changelog** | v13 → v14 detaliat |
| **Licența MIT** | Text complet |
| **Contact** | YO8ACR, email, locator |
