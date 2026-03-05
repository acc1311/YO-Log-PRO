# 📻 YO Log PRO v16.5 FINAL — Professional Multi-Contest Amateur Radio Logger

## 🆕 README.md — Versiunea 16.5 FINAL

### 🇷🇴 ACTUALIZĂRI v16.5

**REZOLVĂRI MAJORE:**
- ✅ **REZOLVAT:** Frecvența, banda, modul și RST **persistă între QSO-uri**
- ✅ **REZOLVAT:** Doar indicativul și nota se șterg după logare
- ✅ **ÎMBUNĂTĂȚIT:** Fluxul de operare este acum **mult mai rapid** — nu mai trebuie să setați banda/modul/RST la fiecare QSO
- ✅ **NOU:** Buton **Reset** complet separat pentru ștergere totală câmpuri

**ÎMBUNĂTĂȚIRI CABRILLO 2.0 (v16.4 → v16.5):**
- ✅ **ADĂUGAT:** Export Cabrillo 2.0 cu dialog configurare exchange
- ✅ **ADĂUGAT:** Opțiuni exchange TRIMIS: Județ/Locator/Serial/Nimic
- ✅ **ADĂUGAT:** Opțiuni exchange PRIMIT: Din log (notă/serial)/Nimic
- ✅ **ADĂUGAT:** Dialog previzualizare înainte de export
- ✅ **ADĂUGAT:** Import Cabrillo 2.0 și 3.0
- ✅ **ADĂUGAT:** Câmp `cabrillo_name` în editor concurs
- ✅ **ADĂUGAT:** Câmp `exchange_format` per concurs
- ✅ **ADĂUGAT:** Câmpuri Email și Soapbox în setări
- ✅ **ADĂUGAT:** Validare + backup automat înainte de export
- ✅ **ADĂUGAT:** Dialog salvare fișier pentru toate exporturile

---

### 🇬🇧 UPDATES v16.5

**MAJOR FIXES:**
- ✅ **FIXED:** Frequency, band, mode and RST **persist between QSOs**
- ✅ **FIXED:** Only callsign and note clear after logging
- ✅ **IMPROVED:** Operating flow is now **much faster** — no need to set band/mode/RST for every QSO
- ✅ **NEW:** Separate **Reset** button for full field clearing

**CABRILLO 2.0 IMPROVEMENTS (v16.4 → v16.5):**
- ✅ **ADDED:** Cabrillo 2.0 export with exchange configuration dialog
- ✅ **ADDED:** Exchange SENT options: County/Locator/Serial/None
- ✅ **ADDED:** Exchange RECEIVED options: From log (note/serial)/None
- ✅ **ADDED:** Preview dialog before export
- ✅ **ADDED:** Import Cabrillo 2.0 and 3.0
- ✅ **ADDED:** `cabrillo_name` field in contest editor
- ✅ **ADDED:** `exchange_format` field per contest
- ✅ **ADDED:** Email and Soapbox fields in settings
- ✅ **ADDED:** Validation + auto-backup before export
- ✅ **ADDED:** Save file dialog for all exports

---

## 📋 FLUX DE OPERARE NOU / NEW OPERATING FLOW

### 🇷🇴 Flux Rapid v16.5

```
PRIMUL QSO:
1. Setați banda → 40m
2. Setați modul → SSB (RST auto: 59)
3. Tastați indicativul → YO3ABC
4. ENTER → QSO logat!

URMĂTOARELE QSO-URI:
1. Tastați indicativul → YO4XYZ
2. ENTER → QSO logat!
   (banda, modul, RST — RĂMÂN!)

SCHIMBAȚI BANDA/MODUL:
- F2 = bandă următoare
- F3 = mod următor (RST se ajustează automat)

RESETARE COMPLETĂ:
- [Reset] → șterge TOATE câmpurile (freq, bandă, mod, RST)
```

### 🇬🇧 Quick Flow v16.5

```
FIRST QSO:
1. Set band → 40m
2. Set mode → SSB (auto RST: 59)
3. Type callsign → YO3ABC
4. ENTER → QSO logged!

NEXT QSOs:
1. Type callsign → YO4XYZ
2. ENTER → QSO logged!
   (band, mode, RST — PERSIST!)

CHANGE BAND/MODE:
- F2 = next band
- F3 = next mode (RST auto-adjusts)

FULL RESET:
- [Reset] → clears ALL fields (freq, band, mode, RST)
```

---

## 📤 EXPORT CABRILLO 2.0 — GHID COMPLET

### 🇷🇴 Configurare Exchange Cabrillo 2.0

**PASUL 1:** Click `[📤 Export]` → `Cabrillo 2.0 (.log)`

**PASUL 2:** Dialog configurare exchange:

| Exchange TRIMIS | Ce trimiteți | Exemplu |
|-----------------|--------------|---------|
| **Județ** | Județ din setări | `NT` |
| **Locator** | Locator din setări | `KN37` |
| **Nr. Serial** | Din coloana Nr S | `001` |
| **Nimic** | `--` | `--` |

| Exchange PRIMIT | Ce primiți | Exemplu |
|-----------------|------------|---------|
| **Din log** | Notă sau Nr R din log | `BV` sau `045` |
| **Nimic** | `--` | `--` |

**PASUL 3:** Click `[📤 Exportă]` → previzualizare

**PASUL 4:** Click `[Salvează]` → alegeți locația

---

### 🇬🇧 Cabrillo 2.0 Exchange Configuration

**STEP 1:** Click `[📤 Export]` → `Cabrillo 2.0 (.log)`

**STEP 2:** Exchange configuration dialog:

| Exchange SENT | What you send | Example |
|---------------|---------------|---------|
| **County** | County from settings | `NT` |
| **Locator** | Locator from settings | `KN37` |
| **Serial Nr.** | From Nr S column | `001` |
| **None** | `--` | `--` |

| Exchange RECEIVED | What you receive | Example |
|-------------------|------------------|---------|
| **From log** | Note or Nr R from log | `BV` or `045` |
| **None** | `--` | `--` |

**STEP 3:** Click `[📤 Export]` → preview

**STEP 4:** Click `[Save]` → choose location

---

## 🆚 COMPARAȚIE VERSIUNI / VERSION COMPARISON

| Funcționalitate | v16.2 | v16.4 | **v16.5** |
|-----------------|-------|-------|-----------|
| **Persistență câmpuri** | ❌ Tot se șterge | ❌ Tot se șterge | ✅ **Freq/Band/Mode/RST persistă** |
| **Export Cabrillo 2.0** | ❌ | ✅ | ✅ **+ Exchange configurabil** |
| **Import Cabrillo** | ❌ | ✅ 3.0 only | ✅ **2.0 + 3.0** |
| **Preview export** | ❌ | ❌ | ✅ **Toate exporturile** |
| **Validare pre-export** | ❌ | ❌ | ✅ **Automat + backup** |
| **Email/Soapbox** | ❌ | ❌ | ✅ **În setări** |
| **Exchange format** | ❌ | ❌ | ✅ **Per concurs** |

---

## 📁 FIȘIERE NOI / NEW FILES

```
📁 C:\RadioLog\
├── config.json               ← NOU: email, soapbox, cab2_exch_sent/rcvd
├── contests.json             ← NOU: cabrillo_name, exchange_format per concurs
├── log_*.json                ← (unchanged)
├── cab2_CONTEST_*.log        ← NOU: Export Cabrillo 2.0
├── cab3_CONTEST_*.log        ← (existing) Export Cabrillo 3.0
└── ...
```

---

## ⚙️ SETĂRI NOI / NEW SETTINGS

### 🇷🇴 Setări adăugate în v16.4-16.5

| Câmp | Descriere | Utilizare |
|------|-----------|-----------|
| **Email** | Adresa de email | Cabrillo 2.0 header |
| **Soapbox** | Comentarii concurs | Cabrillo 2.0/3.0 |
| **Cabrillo Name** | Nume concurs oficial | Per concurs în editor |
| **Exchange Format** | Format schimb implicit | Per concurs: none/county/grid/serial/zone/custom |

### 🇬🇧 Settings added in v16.4-16.5

| Field | Description | Used In |
|-------|-------------|---------|
| **Email** | Email address | Cabrillo 2.0 header |
| **Soapbox** | Contest comments | Cabrillo 2.0/3.0 |
| **Cabrillo Name** | Official contest name | Per contest in editor |
| **Exchange Format** | Default exchange format | Per contest: none/county/grid/serial/zone/custom |

---

## 🔧 CONFIGURARE CONCURS NOU / NEW CONTEST SETUP

### 🇷🇴 Exemplu: Concurs cu Cabrillo 2.0

```
1. [🏆 Concursuri] → [➕ Adaugă]
2. Completați:
   - ID: cupa-neamt
   - Nume RO: Cupa Neamț
   - Nume EN: Neamt Cup
   - Nume Cabrillo: NEAMT CUP       ← NOU!
   - Exchange Format: county         ← NOU!
   - Tip: YO
   - Punctare: per_qso
   - Puncte/QSO: 2
   - Min QSO: 25
   - Benzi: ☑80m ☑40m ☑20m
   - Moduri: ☑SSB ☑CW
   - Nr. Seriale: ☑
   - Județ: ☑
   - Listă județe: NT,IS,BC,BV
3. [Salvează]
```

### 🇬🇧 Example: Contest with Cabrillo 2.0

```
1. [🏆 Contests] → [➕ Add]
2. Fill in:
   - ID: county-cup
   - Name RO: Cupa Județelor
   - Name EN: County Cup
   - Cabrillo Name: COUNTY CUP      ← NEW!
   - Exchange Format: county         ← NEW!
   - Type: YO
   - Scoring: per_qso
   - Points/QSO: 2
   - Min QSO: 25
   - Bands: ☑80m ☑40m ☑20m
   - Modes: ☑SSB ☑CW
   - Serial Numbers: ☑
   - County: ☑
   - County List: NT,IS,BC,BV
3. [Save]
```

---

## 📊 STATISTICI EXPORT / EXPORT STATISTICS

### 🇷🇴 Înainte vs După v16.5

| Operațiune | v16.2 (vechi) | **v16.5 (nou)** |
|------------|---------------|-----------------|
| **Setare bandă/mod** | La fiecare QSO | O dată per run |
| **Timp per QSO** | ~15 secunde | **~5 secunde** |
| **Verificare export** | Manuală | **Automată** |
| **Preview export** | Nu | **Da** |
| **Configurare exchange** | Hardcodat | **Dialog GUI** |

### 🇬🇧 Before vs After v16.5

| Operation | v16.2 (old) | **v16.5 (new)** |
|-----------|-------------|-----------------|
| **Set band/mode** | Every QSO | Once per run |
| **Time per QSO** | ~15 seconds | **~5 seconds** |
| **Export check** | Manual | **Automatic** |
| **Export preview** | No | **Yes** |
| **Exchange config** | Hardcoded | **GUI dialog** |

---

## 🚀 ÎMBUNĂTĂȚIRI PERFORMANȚĂ / PERFORMANCE IMPROVEMENTS

### 🇷🇴 Timp Economisit în Concurs

**Exemplu: 100 QSO într-un concurs**

| Versiune | Timp setare/QSO | Timp total setări | **Diferență** |
|----------|-----------------|-------------------|---------------|
| v16.2 | 10 sec × 100 | 16 min 40 sec | — |
| **v16.5** | 1 sec × 100 | **1 min 40 sec** | **-15 minute!** |

**Plus:**
- ✅ Reducere erori de introducere bandă/mod
- ✅ Flux natural de operare
- ✅ Concentrare pe indicativ, nu pe setări

### 🇬🇧 Time Saved in Contest

**Example: 100 QSOs in a contest**

| Version | Time setup/QSO | Total setup time | **Difference** |
|---------|----------------|------------------|----------------|
| v16.2 | 10 sec × 100 | 16 min 40 sec | — |
| **v16.5** | 1 sec × 100 | **1 min 40 sec** | **-15 minutes!** |

**Plus:**
- ✅ Reduced band/mode input errors
- ✅ Natural operating flow
- ✅ Focus on callsign, not settings

---

## 📋 CHECKLIST ACTUALIZARE / UPDATE CHECKLIST

### 🇷🇴 Pentru utilizatori existenți

```
☐ 1. Backup folder complet (C:\RadioLog\ → USB)
☐ 2. Înlocuiți yo_log_pro.exe cu v16.5
☐ 3. Pornire normală (config.json se actualizează automat)
☐ 4. Verificați setări: [⚙ Setări]
☐ 5. Completați Email și Soapbox (opțional)
☐ 6. Testați export Cabrillo 2.0 pe un concurs
☐ 7. Verificați persistența freq/band/mode
☐ 8. 73!
```

### 🇬🇧 For existing users

```
☐ 1. Backup complete folder (C:\RadioLog\ → USB)
☐ 2. Replace yo_log_pro.exe with v16.5
☐ 3. Normal startup (config.json auto-updates)
☐ 4. Check settings: [⚙ Settings]
☐ 5. Fill Email and Soapbox (optional)
☐ 6. Test Cabrillo 2.0 export on a contest
☐ 7. Verify freq/band/mode persistence
☐ 8. 73!
```

---

## 🐛 DEPANARE v16.5 / TROUBLESHOOTING v16.5

| Problemă | Cauză | Soluție |
|----------|-------|---------|
| Banda nu se schimbă cu F2 | Concursul are o singură bandă | Normal — verificați concursul |
| RST nu se schimbă cu F3 | RST manual setat | Apăsați F3 din nou pentru auto-RST |
| Exchange dialog gol | Județ/Locator nesetat | [⚙ Setări] → Completați |
| Preview nu apare | Pop-up blocat | Verificați taskbar |
| Import Cabrillo eșuat | Format invalid | Verificați că e Cabrillo 2.0 sau 3.0 |

---

## 📞 CONTACT ȘI SUPORT / CONTACT AND SUPPORT

| | |
|---|---|
| **Dezvoltator / Developer** | Ardei Constantin-Cătălin |
| **Indicativ / Callsign** | **YO8ACR** |
| **Email** | yo8acr@gmail.com |
| **Versiune / Version** | **16.5 FINAL** |
| **Data lansare / Release** | 2026-01-15 |

---

<p align="center">
  <strong>73 de YO8ACR! 📻</strong><br><br>
  <em>🇷🇴 „v16.5 — Mai rapid, mai inteligent, mai profesional!"</em><br>
  <em>🇬🇧 "v16.5 — Faster, smarter, more professional!"</em><br><br>
  <strong>YO Log PRO v16.5 FINAL — The ULTIMATE Amateur Radio Logger</strong>
</p>

---

## 📜 CHANGELOG COMPLET / COMPLETE CHANGELOG

### v16.5 FINAL (2026-01-15)
**MAJOR:**
- ✅ Freq/Band/Mode/RST persist between QSOs (only call+note clear)
- ✅ Separate Reset button for full clearing

### v16.4 FINAL (2026-01-14)
**MAJOR:**
- ✅ Cabrillo 2.0 export with exchange dialog
- ✅ Import Cabrillo 2.0 and 3.0
- ✅ Preview dialog for all exports
- ✅ Email and Soapbox fields
- ✅ Validation + auto-backup before export

### v16.2 FINAL (2026-01-12)
- ✅ Contest manager improvements
- ✅ Statistics window
- ✅ ADIF/EDI export
- ✅ All dialogs centered

### v16.0 FINAL (2026-01-01)
- ✅ Initial stable release

---

**🎯 REMEMBER:**
- **F2** = Bandă următoare / Next band
- **F3** = Mod următor / Next mode
- **Enter** = LOG QSO
- **[Reset]** = Ștergere completă / Full clear
- **Ctrl+S** = Salvare forțată / Force save

**Happy contesting! 🏆**
