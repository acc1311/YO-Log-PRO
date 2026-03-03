# 📡 YO Log PRO v9.0 
### Professional Amateur Radio Contest Logger

**YO Log PRO** este un logger avansat pentru radioamatori, dezvoltat special pentru concursurile românești și trafic curent. Este conceput să fie rapid, ușor de utilizat (stil N1MM) și extrem de sigur în gestionarea datelor.

---

## 🌟 Caracteristici Principale

### 🏆 Concursuri Suportate
*   **YO-DX-HF:** Gestionare automată de numere seriale și multiplicatori.
*   **Cupa Moldovei (Stafeta):** Scoring bazat pe categorii (A-E).
*   **Maraton Ion Creangă:** Verificare automată a stațiilor obligatorii (YP8IC, YR8TGN), calcul punctaj /IC și verificare eligibilitate diplomă (100 QSO).
*   **Log Simplu:** Pentru trafic de zi cu zi (frecvență, nume, locator, județ).

### 🔍 Căutare Online (Multi-Source)
*   Căutare paralelă pe: **QRZ.com**, **Radioamator.ro**, **Callbook** și **eQSL**.
*   Extragere automată nume, QTH, județ și locator.
*   Interfață non-blocking (interfața nu se blochează în timpul căutării).

### 💾 Integritatea Datelor
*   **Atomic Saves:** Previne coruperea fișierelor prin scriere temporară și redenumire.
*   **Sistem de Backup:** Salvare automată în folderul `backup` (până la 50 de versiuni) și backup suplimentar în format `.txt`.
*   **Recuperare Automată:** Programul poate restaura datele din cel mai recent backup în caz de eroare.

### 📤 Export Profesional
*   **Cabrillo (toate formatele):** Generare log-uri gata pentru arbitraj (conforme cu site-urile YO).
*   **ADIF 3.1.0+:** Compatibil cu eQSL, QRZ.com, LoTW și ClubLog.
*   **CSV:** Pentru prelucrare în Excel sau Google Sheets.

---

## 💻 Cerințe de Sistem
*   **Sistem de Operare:** Windows 7, 10 sau 11 (Optimizat pentru rezoluții mari/DPI).
*   **Python:** Versiunea 3.7 sau mai noua.
*   **Dependențe:** Folosește exclusiv librăriile standard Python (nu necesită instalări suplimentare).

---

## 🛠️ Instalare și Utilizare

1.  **Descarcă proiectul:**
    ```bash
    git clone https://github.com/UTILIZATORUL_TAU/YO-Log-PRO.git
    cd YO-Log-PRO
    ```

2.  **Lansează aplicația:**
    ```bash
    python main.py
    ```

---

## ⌨️ Scurtături de Tastatură (Shortcuts)
*   **ENTER:** Salvează QSO-ul în log.
*   **CTRL + S:** Salvare manuală și creare backup.
*   **CTRL + L:** Deschide fereastra de căutare online (Lookup).
*   **F1:** Deschide ghidul rapid de utilizare.

---

## 🎨 Personalizare
Programul suportă teme vizuale:
*   **Dark Mode (Default):** Protejează ochii în timpul concursurilor de noapte.
*   **Light Mode:** Pentru vizibilitate maximă în lumină naturală.
*   **Font Scalabil:** Dimensiunea textului poate fi ajustată din configurări.

---

## 👨‍💻 Autor
**Ardei Constantin-Cătălin (YO8ACR)**
*   **Email:** yo8acr@gmail.com
*   **QTH:** Târgu Neamț, România

---

## 📄 Licență
Acest software este dedicat comunității radioamatorilor. Poate fi utilizat și distribuit gratuit în scopuri necomerciale.

73 de YO8ACR! 📻
