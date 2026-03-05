# 📻 YO Log PRO v16.5 FINAL — Professional Multi-Contest Amateur Radio Logger

### 🖥️ Windows 10 / 11

---

## 📥 Descărcare / Download

Mergi la [**Releases**](../../releases) și descarcă `YO_Log_PRO_v16.5`

> ✅ **Nu necesită instalare Python** — executabil standalone  
> ✅ **Dacă apare eroare DLL: instalează [vcredist\_x64.exe](https://aka.ms/vs/17/release/vc_redist.x64.exe)**

---

## 🖥️ COMPATIBILITATE / COMPATIBILITY

| Sistem / System | Status |
|----------------|--------|
| Windows 10 | ✅ |
| Windows 11 | ✅ |

---

## 🆕 NOU ÎN ACEASTĂ VERSIUNE / NEW IN THIS VERSION

### ⏱ Timer Concurs Îmbunătățit

* ✅ **Durata în ore SAU minute** — selectezi cu buton radio înainte de start
* ✅ **Avertizare sonoră la 5 minute rămase** — 2 beep-uri (galben)
* ✅ **Avertizare sonoră la 1 minut rămas** — 3 beep-uri rapide (roșu)
* ✅ **Beep triplu la TIME UP / final** — mesaj roșu pe ecran
* ✅ **Checkbox activare/dezactivare sunete** timer independent
* ✅ Culoarea timpului rămas se schimbă: alb → galben (5min) → roșu (1min)

### 📝 Log Nou

* ✅ **Creare log nou cu nume personalizat** — păstrează logurile vechi
* ✅ Alegi concursul din listă
* ✅ Dai un nume (implicit data curentă: `20260305`)
* ✅ **Logul curent se salvează automat** înainte de a crea unul nou
* ✅ Accesibil din meniu `📝 Log` și buton din bara jos

### 🎨 Teme și Culori

* ✅ **6 teme predefinite:**

| Temă | Stil |
|------|------|
| Dark Blue (implicit) | Negru + albastru — tema originală |
| Dark Green | Negru + verde |
| Dark Red | Negru + roșu |
| Dark Purple | Negru + violet |
| Light (Zi) | Alb + albastru — pentru lumină puternică |
| Light Sepia | Crem + maro — odihnitor pentru ochi |

* ✅ **Editor culori custom** — dublu-click pe orice culoare pentru color picker
* ✅ **Preview live** înainte să aplici tema
* ✅ Tema se **salvează automat** și se încarcă la fiecare pornire
* ✅ Accesibil din meniu `📝 Log` și buton din bara jos

---

## 💾 BACKUP AUTOMAT / AUTO BACKUP

| Eveniment | Când |
|-----------|------|
| **Autosave** log curent | La fiecare **60 secunde** |
| La **ieșirea din program** | La fiecare închidere |
| Înainte de orice **export** | Cabrillo, ADIF, EDI, CSV |
| La **golirea logului** | Înainte de ștergere |

**Locație backup:**
```
📁 folderul programului\
└── backups\
    ├── log_simplu_20260305_143022.json
    ├── log_simplu_20260305_150011.json
    └── ... (maxim 50 per concurs)
```

---

## 📋 FUNCȚIONALITĂȚI COMPLETE / FULL FEATURES

### 🇷🇴 Operare rapidă v16.5

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
- [Reset] → șterge TOATE câmpurile
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
- [Reset] → clears ALL fields
```

---

## 📤 EXPORTURI DISPONIBILE / AVAILABLE EXPORTS

| Format | Descriere |
|--------|-----------|
| **Cabrillo 3.0** (.log) | Standard internațional |
| **Cabrillo 2.0** (.log) | Cu dialog configurare exchange |
| **ADIF 3.1** (.adi) | Universal, import în orice logger |
| **CSV** (.csv) | Excel, foi de calcul |
| **EDI / REG1TEST** (.edi) | Concursuri VHF/UHF europene |
| **Print** (.txt) | Raport text formatat |

### Exchange Cabrillo 2.0

| Exchange TRIMIS | Exemplu |
|----------------|---------|
| Județ din setări | `NT` |
| Locator din setări | `KN37` |
| Nr. Serial | `001` |
| Nimic | `--` |

---

## 📥 IMPORTURI DISPONIBILE / AVAILABLE IMPORTS

* ✅ **ADIF** (.adi / .adif)
* ✅ **CSV** (.csv)
* ✅ **Cabrillo 2.0** (.log)
* ✅ **Cabrillo 3.0** (.log)

---

## ⚙️ SETĂRI / SETTINGS

| Câmp | Descriere |
|------|-----------|
| Indicativ | Call-sign-ul tău |
| Locator | Maidenhead (ex: KN37) |
| Județ | Codul județului (ex: NT) |
| Operator | Numele operatorului |
| Putere | Wați (pentru Cabrillo) |
| Email | Pentru header Cabrillo |
| Soapbox | Comentarii concurs |
| Font | Dimensiunea fontului (9-16) |
| Sunete | Activare/dezactivare beep |

---

## 🔧 TASTE RAPIDE / KEYBOARD SHORTCUTS

| Tastă | Acțiune |
|-------|---------|
| **Enter** | LOG QSO |
| **F2** | Bandă următoare |
| **F3** | Mod următor |
| **Ctrl+S** | Salvare forțată |
| **Ctrl+Z** | Undo ultimul QSO |
| **Ctrl+F** | Căutare în log |

---

## 🐛 DEPANARE / TROUBLESHOOTING

| Problemă | Cauză | Soluție |
|----------|-------|---------|
| Eroare DLL la pornire | Visual C++ lipsă | Instalează vcredist_x64.exe |
| Banda nu se schimbă cu F2 | Concursul are o singură bandă | Normal |
| Exchange dialog gol | Județ/Locator nesetat | ⚙ Setări → Completează |
| Preview nu apare | Pop-up blocat | Verifică taskbar |
| Timer nu sună | Sunete dezactivate | Bifează checkbox în timer |

---

## 📜 CHANGELOG

### v16.5 FINAL
* ✅ **NOU:** Timer cu ore/minute și avertizări sonore (5min, 1min, final)
* ✅ **NOU:** Log Nou cu nume personalizat
* ✅ **NOU:** 6 teme predefinite + editor culori custom
* ✅ **FIX:** Freq/Band/Mode/RST persistă între QSO-uri
* ✅ **NOU:** Buton Reset separat pentru ștergere completă

### v16.4 FINAL
* ✅ Export Cabrillo 2.0 cu dialog exchange configurabil
* ✅ Import Cabrillo 2.0 și 3.0
* ✅ Preview dialog pentru toate exporturile
* ✅ Câmpuri Email și Soapbox în setări
* ✅ Validare + backup automat înainte de export

### v16.2 FINAL
* ✅ Manager concursuri complet
* ✅ Fereastră statistici
* ✅ Export ADIF/EDI
* ✅ Toate dialogurile centrate

---

## 📞 CONTACT

| | |
|---|---|
| **Dezvoltator** | Ardei Constantin-Cătălin |
| **Indicativ** | **YO8ACR** |
| **Email** | yo8acr@gmail.com |
| **Versiune** | 16.5 FINAL |

---

**🎯 REMEMBER:**
`F2` = Bandă · `F3` = Mod · `Enter` = LOG · `[Reset]` = Ștergere · `Ctrl+S` = Save

**73 de YO8ACR! 📻**  
*"v16.5 — Mai rapid, mai inteligent, mai profesional!"*
