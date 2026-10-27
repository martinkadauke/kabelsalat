# -*- coding: utf-8 -*-
"""Kabelführung – Generator. Fenster zum Erzeugen eigener Teile ohne FreeCAD-Kenntnisse und ohne KI.

Start: "Kabel-Generator.bat" doppelklicken (startet dieses Fenster mit FreeCADs Python).
Das Teil rechnet kabelfuehrung.py (dieselbe Datei wie die FCStd und das Druckset) im Hintergrund mit freecadcmd.
Danach öffnet die STL in Bambu Studio.

Test ohne Fenster:  python.exe kabel_generator.pyw --selbsttest
"""
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import tkinter as tk
from tkinter import filedialog, ttk

ORDNER = os.path.dirname(os.path.abspath(__file__))
FREECADCMD = [os.path.join(os.path.dirname(sys.executable), "freecadcmd.exe"),
              r"C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe"]
BAMBU = [r"C:\Program Files\Bambu Studio\bambu-studio.exe", r"C:\Program Files (x86)\Bambu Studio\bambu-studio.exe"]
GROESSEN = ["3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
TEILE = [("etagen", "Etagenkachel (zwei Bäume)"), ("kachel", "Kabelkachel (flach)"),
         ("kreisverkehr", "Kreisverkehr"), ("leer", "Leerkachel")]
ARBEITER = os.path.join(ORDNER, "kabel_generator_rechnen.py")


def zahl(text, name):
    try:
        return float(str(text).strip().replace(",", "."))
    except ValueError:
        raise ValueError("%s: '%s' ist keine Zahl" % (name, text))


def erstes(pfade):
    return next((p for p in pfade if os.path.exists(p)), None)


def dateiname(art, werte):
    if art == "kachel":
        return "Kabelkachel_%gmm_%dspur.stl" % (werte["Kabeldurchmesser"], werte["Spuren"])
    if art == "kreisverkehr":
        return "Kreisverkehr_bis%gmm.stl" % werte["Kabeldurchmesser"]
    if art == "leer":
        return "Leerkachel.stl"
    teile = []
    for s in "AB":
        n = werte["%s_Etagen" % s]
        teile.append("%s%s" % (s, "-".join("%g" % werte["%s_Kabel%d" % (s, i + 1)] for i in range(n)) or "0"))
    return "Etagen_%s_%s.stl" % tuple(teile)


def rechnen(art, werte, datei):
    """freecadcmd mit dem Auftrag starten, Ergebnis (dict) zurückgeben."""
    fc = erstes(FREECADCMD)
    if fc is None:
        return {"ok": False, "fehler": "FreeCAD (freecadcmd.exe) nicht gefunden"}
    tmp = tempfile.mkdtemp(prefix="kabelgen_")
    auftrag = {"ordner": ORDNER, "art": art, "werte": werte, "datei": datei,
               "ergebnis": os.path.join(tmp, "ergebnis.json")}
    pfad = os.path.join(tmp, "auftrag.json")
    with open(pfad, "w", encoding="utf-8") as fh:
        json.dump(auftrag, fh, ensure_ascii=False)
    env = dict(os.environ, KF_AUFTRAG=pfad)
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    lauf = subprocess.run([fc, ARBEITER], env=env, capture_output=True, text=True, creationflags=flags,
                          timeout=600)
    if not os.path.exists(auftrag["ergebnis"]):
        return {"ok": False, "fehler": "FreeCAD hat kein Ergebnis geliefert", "details": lauf.stdout[-2000:]}
    with open(auftrag["ergebnis"], encoding="utf-8") as fh:
        return json.load(fh)


class Generator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Kabelführung – Generator")
        self.resizable(False, False)
        self.art = tk.StringVar(value="etagen")
        rand = {"padx": 8, "pady": 4}

        kopf = ttk.Frame(self)
        kopf.grid(row=0, column=0, sticky="w", **rand)
        ttk.Label(kopf, text="Teil:").grid(row=0, column=0, sticky="w")
        for i, (wert, text) in enumerate(TEILE):
            ttk.Radiobutton(kopf, text=text, value=wert, variable=self.art, command=self.zeige).grid(
                row=0, column=i + 1, sticky="w", padx=4)

        # Etagenkachel: zwei Bäume
        self.f_etagen = ttk.LabelFrame(self, text="Etagenkachel: zwei Bäume, Schraube in der Mitte")
        self.baum = {}
        vorgabe = {"A": (3, ["4", "6", "4"]), "B": (3, ["10", "10", "10"])}
        for spalte, (s, titel) in enumerate((("A", "Seite A (mit den Taschen)"), ("B", "Seite B (mit den Klammern)"))):
            f = ttk.Frame(self.f_etagen)
            f.grid(row=0, column=spalte, sticky="n", padx=10, pady=4)
            ttk.Label(f, text=titel, font=("Segoe UI", 9, "bold")).grid(row=0, column=0, columnspan=2, sticky="w")
            ttk.Label(f, text="Etagen:").grid(row=1, column=0, sticky="w")
            n = tk.StringVar(value=str(vorgabe[s][0]))
            cb = ttk.Combobox(f, textvariable=n, values=["0", "1", "2", "3"], width=6, state="readonly")
            cb.grid(row=1, column=1, sticky="w", pady=2)
            cb.bind("<<ComboboxSelected>>", lambda e: self.etagen_sperren())
            felder = []
            for i in range(3):
                ttk.Label(f, text="Etage %d%s – Kabel mm:" % (i + 1, " (am Tisch)" if i == 0 else "")).grid(
                    row=2 + i, column=0, sticky="w")
                v = tk.StringVar(value=vorgabe[s][1][i])
                e = ttk.Combobox(f, textvariable=v, values=GROESSEN, width=6)
                e.grid(row=2 + i, column=1, sticky="w", pady=2)
                felder.append((v, e))
            self.baum[s] = (n, felder)
        ttk.Label(self.f_etagen, foreground="#555", justify="left", text=(
            "Etage 1 liegt am Tisch, Etage 3 am weitesten weg. 0 Etagen = kein Baum auf dieser Seite.\n"
            "Seite A hat weniger Platz (Taschen am Rand): dicke Kabel lieber auf Seite B oder weiter oben.")).grid(
            row=1, column=0, columnspan=2, sticky="w", padx=10, pady=(0, 6))

        # Kabelkachel
        self.f_kachel = ttk.LabelFrame(self, text="Kabelkachel: flach, Haken abwechselnd wie im Foto")
        ttk.Label(self.f_kachel, text="Kabel mm:").grid(row=0, column=0, sticky="w", padx=10, pady=4)
        self.k_d = tk.StringVar(value="6")
        ttk.Combobox(self.f_kachel, textvariable=self.k_d, values=GROESSEN, width=6).grid(row=0, column=1, sticky="w")
        ttk.Label(self.f_kachel, text="Spuren:").grid(row=0, column=2, sticky="w", padx=10)
        self.k_n = tk.StringVar(value="2")
        ttk.Combobox(self.f_kachel, textvariable=self.k_n, values=["1", "2"], width=4, state="readonly").grid(
            row=0, column=3, sticky="w", padx=(0, 10))

        # Kreisverkehr
        self.f_kv = ttk.LabelFrame(self, text="Kreisverkehr")
        ttk.Label(self.f_kv, text="Poller für Kabel bis mm:").grid(row=0, column=0, sticky="w", padx=10, pady=4)
        self.kv_d = tk.StringVar(value="10")
        ttk.Combobox(self.f_kv, textvariable=self.kv_d, values=GROESSEN, width=6).grid(row=0, column=1, sticky="w",
                                                                                       padx=(0, 10))
        self.f_leer = ttk.LabelFrame(self, text="Leerkachel")
        ttk.Label(self.f_leer, text="Platte ohne Haken, für Kreuzungen und Lücken.").grid(padx=10, pady=4)

        # Feinheiten
        f = ttk.LabelFrame(self, text="Passung (nur ändern, wenn der Probedruck es verlangt)")
        f.grid(row=2, column=0, sticky="we", **rand)
        self.klemmung = tk.StringVar(value="0.4")
        self.spiel = tk.StringVar(value="0.2")
        ttk.Label(f, text="Klemmung mm (Kabel klickt):").grid(row=0, column=0, sticky="w", padx=10, pady=4)
        ttk.Entry(f, textvariable=self.klemmung, width=6).grid(row=0, column=1, sticky="w")
        ttk.Label(f, text="Puzzle-Spiel mm:").grid(row=0, column=2, sticky="w", padx=10)
        ttk.Entry(f, textvariable=self.spiel, width=6).grid(row=0, column=3, sticky="w", padx=(0, 10))

        # Ausgabe
        f = ttk.Frame(self)
        f.grid(row=3, column=0, sticky="we", **rand)
        ttk.Label(f, text="Speichern in:").grid(row=0, column=0, sticky="w")
        self.ziel = tk.StringVar(value=os.path.join(ORDNER, "generiert"))
        ttk.Entry(f, textvariable=self.ziel, width=58).grid(row=0, column=1, sticky="we", padx=4)
        ttk.Button(f, text="…", width=3, command=self.ordner_waehlen).grid(row=0, column=2)

        f = ttk.Frame(self)
        f.grid(row=4, column=0, sticky="we", **rand)
        self.knopf_bambu = ttk.Button(f, text="STL erzeugen und in Bambu Studio öffnen",
                                      command=lambda: self.los(True))
        self.knopf_bambu.grid(row=0, column=0, padx=(0, 6))
        self.knopf_stl = ttk.Button(f, text="Nur STL erzeugen", command=lambda: self.los(False))
        self.knopf_stl.grid(row=0, column=1)

        self.status = tk.Text(self, width=86, height=12, wrap="word", font=("Consolas", 9), relief="solid",
                              borderwidth=1)
        self.status.grid(row=5, column=0, sticky="we", padx=8, pady=(4, 8))
        self.meldung("Teil wählen, Kabelgrößen eintragen, dann 'STL erzeugen'. Rechnen dauert 5 bis 30 Sekunden.")
        self.zeige()

    # ------------------------------------------------------------------ Formular
    def zeige(self):
        for f in (self.f_etagen, self.f_kachel, self.f_kv, self.f_leer):
            f.grid_forget()
        f = {"etagen": self.f_etagen, "kachel": self.f_kachel, "kreisverkehr": self.f_kv, "leer": self.f_leer}
        f[self.art.get()].grid(row=1, column=0, sticky="we", padx=8, pady=4)
        self.etagen_sperren()

    def etagen_sperren(self):
        for n, felder in self.baum.values():
            k = int(n.get())
            for i, (_, e) in enumerate(felder):
                e.configure(state="normal" if i < k else "disabled")

    def ordner_waehlen(self):
        d = filedialog.askdirectory(initialdir=self.ziel.get() if os.path.isdir(self.ziel.get()) else ORDNER)
        if d:
            self.ziel.set(d)

    def auftrag(self):
        """Formular -> (art, werte). Fehler als ValueError mit Klartext."""
        art = self.art.get()
        werte = {"Klemmung": zahl(self.klemmung.get(), "Klemmung"),
                 "PuzzleSpiel": zahl(self.spiel.get(), "Puzzle-Spiel")}
        if art == "kachel":
            werte.update(Kabeldurchmesser=zahl(self.k_d.get(), "Kabel"), Spuren=int(self.k_n.get()))
        elif art == "kreisverkehr" or art == "leer":
            werte["Kabeldurchmesser"] = zahl(self.kv_d.get(), "Poller")
        else:
            for s, (n, felder) in self.baum.items():
                k = int(n.get())
                werte["%s_Etagen" % s] = k
                for i, (v, _) in enumerate(felder):
                    werte["%s_Kabel%d" % (s, i + 1)] = zahl(v.get(), "Seite %s, Etage %d" % (s, i + 1)) if i < k else 4.0
        return art, werte

    # ------------------------------------------------------------------ Ablauf
    def meldung(self, text, neu=True):
        self.status.configure(state="normal")
        if neu:
            self.status.delete("1.0", "end")
        self.status.insert("end", text + "\n")
        self.status.see("end")
        self.status.configure(state="disabled")

    def los(self, bambu, fertig=None):
        try:
            art, werte = self.auftrag()
        except ValueError as e:
            self.meldung("Bitte korrigieren: %s" % e)
            return
        ziel = self.ziel.get()
        os.makedirs(ziel, exist_ok=True)
        datei = os.path.join(ziel, dateiname(art, werte))
        for k in (self.knopf_bambu, self.knopf_stl):
            k.configure(state="disabled")
        self.meldung("Rechne %s …" % os.path.basename(datei))
        t0 = time.time()

        def arbeit():
            try:
                erg = rechnen(art, werte, datei)
            except Exception as e:  # noqa: BLE001
                erg = {"ok": False, "fehler": "%s: %s" % (type(e).__name__, e)}
            self.after(0, lambda: self.fertig(erg, bambu, time.time() - t0, fertig))

        threading.Thread(target=arbeit, daemon=True).start()

    def fertig(self, erg, bambu, dauer, fertig=None):
        for k in (self.knopf_bambu, self.knopf_stl):
            k.configure(state="normal")
        zeilen = []
        if erg.get("masse"):
            x, y, z = erg["masse"]
            zeilen.append("%s  (%.0f s)" % (os.path.basename(erg["datei"]), dauer))
            zeilen.append("Größe mit Klammern %.0f x %.0f mm, Höhe %.1f mm, ca. %.0f g (voll gerechnet)" %
                          (x, y, z, erg["gramm"]))
        for p in erg.get("pruefung", []):
            zeilen.append("  Etage %-3s Kabel %4.1f mm: %s" % (
                p["etage"], p["kabel"],
                ("gefangen, beim Einlegen am Mittelhaken %.0f mm nach innen biegen" % p["versatz"]) if p["ok"]
                else "PROBLEM: " + ", ".join(t for t, b in (("Kanal zu eng", p["kanal_frei"]),
                                                            ("hält nicht", p["haelt"]),
                                                            ("nicht gefangen", p["gefangen"]),
                                                            ("außen nicht einlegbar", p["einlegen_aussen"]),
                                                            ("Mitte nicht einlegbar", p["einlegen_mitte"]))
                                             if not b)))
        if erg.get("ok"):
            zeilen.insert(0, "Fertig.")
            if bambu:
                prog = erstes(BAMBU)
                if prog:
                    subprocess.Popen([prog, erg["datei"]])
                    zeilen.append("Öffne in Bambu Studio …")
                else:
                    os.startfile(erg["datei"])
                    zeilen.append("Bambu Studio nicht gefunden, öffne mit dem Standardprogramm.")
        else:
            zeilen.insert(0, "Nicht erzeugt: %s" % erg.get("fehler", "unbekannter Fehler"))
            if erg.get("details"):
                zeilen.append(erg["details"][-800:])
        self.meldung("\n".join(zeilen))
        if fertig:
            fertig(erg)


def selbsttest():
    """Formular mit dem Beispiel (A 4-6-4, B 10-10-10) unsichtbar ausfüllen, rechnen lassen, nichts öffnen."""
    app = Generator()
    app.withdraw()
    app.ziel.set(os.path.join(tempfile.gettempdir(), "kabelgen_test"))
    ergebnis = {}

    def fertig(erg):
        ergebnis.update(erg)
        print(app.status.get("1.0", "end"))
        app.destroy()

    app.after(500, lambda: app.los(False, fertig))
    app.mainloop()
    sys.exit(0 if ergebnis.get("ok") else 1)


if __name__ == "__main__":
    if "--selbsttest" in sys.argv:
        selbsttest()
    else:
        Generator().mainloop()
