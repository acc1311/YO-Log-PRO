import os, sys, json, re, datetime, shutil, tempfile, ctypes
from pathlib import Path
from collections import Counter
from tkinter import (Tk, Toplevel, Frame, Label, Entry, Button, 
    ttk, messagebox, Scrollbar)

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

BANDS = ["160m","80m","60m","40m","30m","20m","17m","15m","12m","10m","6m","2m"]
MODES = ["SSB","CW","DIGI","FT8","FT4","RTTY","AM","FM"]
CON_T = {"yo-dx": "YO-DX-HF", "stafeta": "Stafeta", "maraton": "Maraton", "simple": "Log"}
CAT_T = ["Single-Op High", "Single-Op Low", "Single-Op QRP", "Multi-Op", "Checklog"]
FLS = {"config": "config.json", "log": "log.json"}

DEF_C = {"call": "YO8ACR", "loc": "KN37", "jud": "NT", "cat": "Single-Op Low", "fs": 11, "mode": "simple"}

def s_save(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True
    except: return False

def s_load(path, default):
    if not Path(path).exists(): return default
    try:
        with open(path, encoding="utf-8") as f: return json.load(f)
    except: return default

class App(Tk):
    def __init__(self):
        super().__init__()
        self.title("YO Log PRO v9.6")
        self.geometry("1200x800")
        self.cfg = s_load(FLS["config"], DEF_C)
        self.log = s_load(FLS["log"], [])
        self.idx = None
        self.fs = int(self.cfg.get("fs", 11))
        self.th = {"bg": "#1e1e1e", "fg": "white", "ac": "#007acc", "eb": "#333", "hd": "#2d2d2d"}
        self.configure(bg=self.th["bg"])
        self.fnt = ("Consolas", self.fs)
        self.ui()
        self.ref()

    def ui(self):
        h = Frame(self, bg=self.th["hd"], pady=5)
        h.pack(fill="x")
        Label(h, text="YO Log", font=("Consolas", self.fs+4, "bold"), fg="#4fc3f7", bg=self.th["hd"]).pack(side="left", padx=10)
        self.cb = ttk.Combobox(h, values=list(CON_T.values()), state="readonly")
        self.cb.set(CON_T.get(self.cfg["mode"], "Log"))
        self.cb.pack(side="left", padx=5)
        self.inf = Label(h, text=self.cfg["call"] + " | " + self.cfg["loc"], fg="#81c784", bg=self.th["hd"])
        self.inf.pack(side="right", padx=10)

        f = Frame(self, bg=self.th["bg"], pady=10)
        f.pack(fill="x")
        self.en = {}
        for i, (l, k, w) in enumerate([("Call","c",12),("Band","b",8),("Mode","m",8),("RST_S","s",5),("RST_R","r",5),("Note","n",20)]):
            px = Frame(f, bg=self.th["bg"])
            px.grid(row=0, column=i, padx=5)
            Label(px, text=l, fg="#bbb", bg=self.th["bg"]).pack()
            if k == "b":
                e = ttk.Combobox(px, values=BANDS, width=w, state="readonly")
                e.set("40m")
            elif k == "m":
                e = ttk.Combobox(px, values=MODES, width=w, state="readonly")
                e.set("SSB")
            else:
                e = Entry(px, width=w, bg=self.th["eb"], fg="white", insertbackground="white")
                if k in ["s","r"]: e.insert(0, "59")
            e.pack(); self.en[k] = e
        self.bl = Button(f, text="LOG", command=self.do_l, bg=self.th["ac"], fg="white")
        self.bl.grid(row=0, column=6, padx=10)

        t_f = Frame(self)
        t_f.pack(fill="both", expand=True, padx=10)
        self.tr = ttk.Treeview(t_f, columns=(1,2,3,4,5,6,7,8), show="headings")
        for i, n in enumerate(["Data", "Ora", "Call", "Band", "Mode", "RST_S", "RST_R", "Note"], 1):
            self.tr.heading(i, text=n); self.tr.column(i, width=90)
        self.tr.pack(side="left", fill="both", expand=True)
        sb = Scrollbar(t_f, command=self.tr.yview)
        sb.pack(side="right", fill="y"); self.tr.config(yscrollcommand=sb.set)
        self.tr.bind("<Double-1>", self.ed)

        bt = Frame(self, bg=self.th["hd"])
        bt.pack(fill="x")
        Button(bt, text="Setari", command=self.set).pack(side="left", padx=10)
        Button(bt, text="Stats", command=self.st).pack(side="left")
        Button(bt, text="Sterge", command=self.dl).pack(side="right", padx=10)

    def do_l(self):
        c = self.en["c"].get().upper().strip()
        if not c: return
        n = datetime.datetime.utcnow()
        q = {"d": n.strftime("%Y-%m-%d"), "t": n.strftime("%H%M"), "c": c, "b": self.en["b"].get(), "m": self.en["m"].get(), "s": self.en["s"].get(), "r": self.en["r"].get(), "n": self.en["n"].get()}
        if self.idx is not None:
            self.log[self.idx] = q; self.idx = None
            self.bl.config(text="LOG", bg=self.th["ac"])
        else: self.log.insert(0, q)
        self.ref(); self.clr(); s_save(FLS["log"], self.log)

    def ref(self):
        for i in self.tr.get_children(): self.tr.delete(i)
        for i, q in enumerate(self.log):
            self.tr.insert("", "end", iid=i, values=(q["d"], q["t"], q["c"], q["b"], q["m"], q["s"], q["r"], q["n"]))

    def clr(self):
        self.en["c"].delete(0, "end"); self.en["n"].delete(0, "end"); self.en["c"].focus()

    def ed(self, e):
        id = self.tr.identify_row(e.y)
        if not id: return
        self.idx = int(id); q = self.log[self.idx]
        for k, v in zip(["c","b","m","s","r","n"], [q["c"],q["b"],q["m"],q["s"],q["r"],q["n"]]):
            if k in ["b","m"]: self.en[k].set(v)
            else: self.en[k].delete(0, "end"); self.en[k].insert(0, v)
        self.bl.config(text="UPDATE", bg="#f57c00")

    def dl(self):
        s = self.tr.selection()
        if not s: return
        if messagebox.askyesno("?", "Stergeti?"):
            for i in sorted([int(x) for x in s], reverse=True): self.log.pop(i)
            self.ref(); s_save(FLS["log"], self.log)

    def set(self):
        d = Toplevel(self); d.title("Setari"); d.geometry("300x400"); d.grab_set()
        Label(d, text="Callsign:").pack(); e1 = Entry(d); e1.insert(0, self.cfg["call"]); e1.pack()
        Label(d, text="Locator:").pack(); e2 = Entry(d); e2.insert(0, self.cfg["loc"]); e2.pack()
        Label(d, text="Font:").pack(); e3 = Entry(d); e3.insert(0, self.cfg["fs"]); e3.pack()
        def sv():
            self.cfg.update({"call": e1.get().upper(), "loc": e2.get().upper(), "fs": int(e3.get())})
            s_save(FLS["config"], self.cfg); d.destroy()
            messagebox.showinfo("OK", "Restartati programul")
        Button(d, text="Save", command=sv).pack(pady=20)

    def st(self):
        b = Counter(q["b"] for q in self.log)
        m = "Total: " + str(len(self.log)) + " QSO
"
        for k in sorted(b.keys()): m += str(k) + ": " + str(b[k]) + "
"
        messagebox.showinfo("Stats", m)

if __name__ == "__main__":
    App().mainloop()
