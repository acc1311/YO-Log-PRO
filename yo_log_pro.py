#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, json, re, datetime, shutil, tempfile, ctypes
from pathlib import Path
from collections import Counter
from tkinter import (
    Tk, Toplevel, Frame, Label, Entry, Button, Text, Scrollbar, Listbox,
    ttk, messagebox, filedialog, StringVar, BooleanVar, IntVar, Menu
)

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

BANDS = ["160m","80m","60m","40m","30m","20m","17m","15m","12m","10m","6m","2m"]
MODES = ["SSB","CW","DIGI","FT8","FT4","RTTY","AM","FM"]

CONTEST_TYPES = {
    "yo-dx-hf": "YO-DX-HF",
    "stafeta": "Cupa Moldovei - Stafeta",
    "maraton": "Maraton Ion Creanga",
    "simple": "Log Simplu"
}

STATION_CATEGORIES = [
    "Single-Op High", "Single-Op Low", "Single-Op QRP",
    "Multi-Op", "Checklog", "SWL"
]

FILES = {"config": "config.json", "log": "log.json", "backup_dir": "backup"}

DEFAULT_CONFIG = {
    "callsign": "YO8ACR",
    "locator": "KN37",
    "operator": "",
    "judet": "NT",
    "category": "Single-Op Low",
    "font_size": 11,
    "active_contest": "simple"
}

def safe_save_json(filepath, data):
    try:
        dir_path = Path(filepath).parent
        dir_path.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode="w", dir=dir_path, delete=False, suffix=".tmp", encoding="utf-8") as tmp:
            json.dump(data, tmp, indent=2, ensure_ascii=False)
            tmp_path = tmp.name
        os.replace(tmp_path, filepath)
        return True
    except:
        return False

def safe_load_json(filepath, default):
    if not Path(filepath).exists(): return default
    try:
        with open(filepath, encoding="utf-8") as f:
            return json.load(f)
    except:
        return default

class App(Tk):
    def __init__(self):
        super().__init__()
        self.title("YO Log PRO v9.5")
        self.geometry("1300x850")
        self.app_config = safe_load_json(FILES["config"], DEFAULT_CONFIG)
        self.log = safe_load_json(FILES["log"], [])
        self._editing_index = None
        fs = int(self.app_config.get("font_size", 11))
        self.font_size = fs
        self.theme = {"bg": "#1e1e1e", "fg": "white", "accent": "#007acc", "entry_bg": "#333333", "header": "#2d2d2d"}
        self.configure(bg=self.theme["bg"])
        self.default_font = ("Consolas", self.font_size)
        self.bold_font = ("Consolas", self.font_size, "bold")
        self._build_ui()
        self._refresh_log()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        header = Frame(self, bg=self.theme["header"], pady=5)
        header.pack(fill="x")
        Label(header, text="YO Log PRO", font=("Consolas", self.font_size + 4, "bold"), fg="#4fc3f7", bg=self.theme["header"]).pack(side="left", padx=15)
        Label(header, text="Mod:", fg="white", bg=self.theme["header"], font=self.default_font).pack(side="left", padx=5)
        self.cb_mode = ttk.Combobox(header, values=list(CONTEST_TYPES.values()), state="readonly", width=25)
        ck = self.app_config.get("active_contest", "simple")
        self.cb_mode.set(CONTEST_TYPES.get(ck, "Log Simplu"))
        self.cb_mode.pack(side="left", padx=5)
        self.cb_mode.bind("<<ComboboxSelected>>", self._on_mode_change)
        it = str(self.app_config["callsign"]) + " | " + str(self.app_config["locator"])
        self.info_lbl = Label(header, text=it, fg="#81c784", bg=self.theme["header"], font=self.bold_font)
        self.info_lbl.pack(side="right", padx=15)
        self.form_frame = Frame(self, bg=self.theme["bg"], pady=15)
        self.form_frame.pack(fill="x", padx=10)
        self._draw_form()
        table_frame = Frame(self, bg=self.theme["bg"])
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        cols = ("Data", "Ora", "Call", "Band", "Mode", "RST_S", "RST_R", "Note")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings")
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(side="left", fill="both", expand=True)
        sb = Scrollbar(table_frame, command=self.tree.yview)
        sb.pack(side="right", fill="y")
        self.tree.config(yscrollcommand=sb.set)
        self.tree.bind("<Double-1>", self._on_tree_double_click)
        footer = Frame(self, bg=self.theme["header"], pady=5)
        footer.pack(fill="x")
        Button(footer, text="Setari Statie", command=self._open_settings, bg="#444", fg="white").pack(side="left", padx=10)
        Button(footer, text="Statistici", command=self._show_stats, bg="#444", fg="white").pack(side="left", padx=5)
        Button(footer, text="Sterge QSO", command=self._delete_qso, bg="#c62828", fg="white").pack(side="right", padx=10)
        Button(footer, text="Salveaza Log", command=self._save_data, bg="#2e7d32", fg="white").pack(side="right", padx=5)

    def _draw_form(self):
        for widget in self.form_frame.winfo_children(): widget.destroy()
        fields = [("Callsign", "call", 12), ("Band", "band", 8), ("Mode", "mode", 8), ("RST S", "rst_s", 5), ("RST R", "rst_r", 5), ("Note", "note", 20)]
        self.entries = {}
        for i, (label, key, width) in enumerate(fields):
            f = Frame(self.form_frame, bg=self.theme["bg"])
            f.grid(row=0, column=i, padx=5)
            Label(f, text=label, fg="#bbb", bg=self.theme["bg"], font=("Consolas", 10)).pack()
            if key == "band":
                e = ttk.Combobox(f, values=BANDS, width=width, state="readonly")
                e.set("40m")
            elif key == "mode":
                e = ttk.Combobox(f, values=MODES, width=width, state="readonly")
                e.set("SSB")
            else:
                e = Entry(f, font=self.default_font, width=width, bg=self.theme["entry_bg"], fg="white", insertbackground="white")
                if key.startswith("rst"): e.insert(0, "59")
            e.pack(); self.entries[key] = e
        self.btn_log = Button(self.form_frame, text="LOG QSO", command=self._log_qso, bg=self.theme["accent"], fg="white", font=self.bold_font, padx=20)
        self.btn_log.grid(row=0, column=len(fields), padx=15, sticky="s")

    def _log_qso(self):
        c = self.entries["call"].get().upper().strip()
        if not c: return
        n = datetime.datetime.utcnow()
        d = {"date": n.strftime("%Y-%m-%d"), "time": n.strftime("%H%M"), "call": c, "band": self.entries["band"].get(), "mode": self.entries["mode"].get(), "rst_s": self.entries["rst_s"].get(), "rst_r": self.entries["rst_r"].get(), "note": self.entries["note"].get(), "contest": self.cb_mode.get()}
        if self._editing_index is not None:
            self.log[self._editing_index] = d
            self._editing_index = None
            self.btn_log.config(text="LOG QSO", bg=self.theme["accent"])
        else:
            self.log.insert(0, d)
        self._refresh_log(); self._clear_form(); self._save_data()

    def _refresh_log(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for i, q in enumerate(self.log):
            v = (q["date"], q["time"], q["call"], q["band"], q["mode"], q["rst_s"], q["rst_r"], q["note"])
            self.tree.insert("", "end", iid=i, values=v)

    def _clear_form(self):
        self.entries["call"].delete(0, "end")
        self.entries["note"].delete(0, "end")
        self.entries["call"].focus_set()

    def _on_tree_double_click(self, event):
        id = self.tree.identify_row(event.y)
        if not id: return
        idx = int(id)
        q = self.log[idx]
        self._editing_index = idx
        self.entries["call"].delete(0, "end")
        self.entries["call"].insert(0, q["call"])
        self.entries["band"].set(q["band"])
        self.entries["mode"].set(q["mode"])
        self.entries["rst_s"].delete(0, "end")
        self.entries["rst_s"].insert(0, q["rst_s"])
        self.entries["rst_r"].delete(0, "end")
        self.entries["rst_r"].insert(0, q["rst_r"])
        self.entries["note"].delete(0, "end")
        self.entries["note"].insert(0, q["note"])
        self.btn_log.config(text="UPDATE QSO", bg="#f57c00")

    def _delete_qso(self):
        s = self.tree.selection()
        if not s: return
        if messagebox.askyesno("Stergere", "Stergeti QSO?"):
            ids = sorted([int(x) for x in s], reverse=True)
            for i in ids: self.log.pop(i)
            self._refresh_log(); self._save_data()

    def _open_settings(self):
        dlg = Toplevel(self); dlg.title("Setari"); dlg.geometry("400x550"); dlg.configure(bg=self.theme["bg"]); dlg.grab_set()
        fields = [("Callsign:", "callsign"), ("Locator:", "locator"), ("Judet:", "judet"), ("Operator:", "operator")]
        se = {}
        for l, k in fields:
            f = Frame(dlg, bg=self.theme["bg"], pady=5); f.pack(fill="x", padx=20)
            Label(f, text=l, fg="white", bg=self.theme["bg"]).pack(side="left")
            e = Entry(f, width=15); e.insert(0, self.app_config.get(k, "")); e.pack(side="right")
            se[k] = e
        f_cat = Frame(dlg, bg=self.theme["bg"], pady=5); f_cat.pack(fill="x", padx=20)
        Label(f_cat, text="Categorie:", fg="white", bg=self.theme["bg"]).pack(side="left")
        cb_cat = ttk.Combobox(f_cat, values=STATION_CATEGORIES, state="readonly")
        cb_cat.set(self.app_config.get("category", "Single-Op Low")); cb_cat.pack(side="right")
        f_fnt = Frame(dlg, bg=self.theme["bg"], pady=5); f_fnt.pack(fill="x", padx=20)
        Label(f_fnt, text="Font:", fg="white", bg=self.theme["bg"]).pack(side="left")
        sp = ttk.Spinbox(f_fnt, from_=8, to=24, width=5); sp.set(self.app_config.get("font_size", 11)); sp.pack(side="right")
        def sv():
            for k in se: self.app_config[k] = se[k].get().upper()
            self.app_config["category"] = cb_cat.get()
            self.app_config["font_size"] = int(sp.get())
            safe_save_json(FILES["config"], self.app_config)
            messagebox.showinfo("OK", "Salvat! Restartati programul.")
            it = str(self.app_config["callsign"]) + " | " + str(self.app_config["locator"])
            self.info_lbl.config(text=it); dlg.destroy()
        Button(dlg, text="SALVEAZA", command=sv, bg=self.theme["accent"], fg="white", pady=10).pack(fill="x", padx=20, pady=20)

    def _on_mode_change(self, event):
        m = self.cb_mode.get()
        for k, v in CONTEST_TYPES.items():
            if v == m: self.app_config["active_contest"] = k
        safe_save_json(FILES["config"], self.app_config)

    def _show_stats(self):
        bnd = Counter(q["band"] for q in self.log)
        msg = "Total: " + str(len(self.log)) + " QSO

"
        for b in sorted(bnd.keys()): msg += str(b) + ": " + str(bnd[b]) + " QSO
"
        messagebox.showinfo("Stats", msg)

    def _save_data(self): safe_save_json(FILES["log"], self.log)
    def _on_close(self): self._save_data(); self.destroy()

if __name__ == "__main__":
    app = App(); app.mainloop()
