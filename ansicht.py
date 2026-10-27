# -*- coding: utf-8 -*-
"""Echte FreeCAD-Screenshots + farbige, gruppierte kabelfuehrung.FCStd in EIGENER GUI-Instanz (ansicht.sh).

Die FCStd ist parametrisch: Tabelle "Parameter" -> Kabelkachel, Kreisverkehr, Leerkachel (FeaturePython aus
kabelfuehrung.py). Der Beispielaufbau besteht aus Links auf diese drei Teile mit Platzierungen per Ausdruck,
passt sich also mit an. Nur die Beispielkabel sind feste Körper (für die aktuellen Werte gelegt).
"""
import math
import os
import struct
import sys
import time

import FreeCAD as App
import FreeCADGui as Gui
import Part

HERE = os.path.dirname(os.path.abspath(next((a for a in sys.argv if os.path.basename(a) == "ansicht.py"),
                                            "ansicht.py")))
sys.path.insert(0, HERE)
import kabelfuehrung as kf  # noqa: E402

V = App.Vector
OUT = os.path.join(HERE, "bilder")
os.makedirs(OUT, exist_ok=True)
LOG = os.path.join(OUT, "log.txt")
FCSTD = os.path.join(HERE, "kabelfuehrung.FCStd")
BW, BH = 1800, 1250

_v = App.ParamGet("User parameter:BaseApp/Preferences/View")
_v.SetBool("Simple", True)
_v.SetBool("Gradient", False)
_v.SetUnsigned("BackgroundColor", 0xFFFFFFFF)
_v.SetBool("UseNavigationAnimations", False)

FARBE = {"Kabelkachel": (0.80, 0.83, 0.87), "Kreisverkehr": (0.96, 0.70, 0.36), "Leerkachel": (0.72, 0.84, 0.74),
         "Etagenkachel": (0.62, 0.75, 0.93), "Kabel": (0.16, 0.16, 0.18)}


def log(*a):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(time.strftime("%H:%M:%S ") + " ".join(str(x) for x in a) + "\n")


def strip_png(path):
    keep = (b"IHDR", b"PLTE", b"tRNS", b"IDAT", b"IEND")
    data = open(path, "rb").read()
    out, i = [data[:8]], 8
    while i < len(data):
        n = struct.unpack(">I", data[i:i + 4])[0]
        if data[i + 4:i + 8] in keep:
            out.append(data[i:i + 12 + n])
        i += 12 + n
    open(path, "wb").write(b"".join(out))


def kabel_kurve(name, pts, r, doc, gruppe, schritt=12.0):
    """Kabel als Rohr entlang einer glatten Kurve durch pts (x, y, z). Lange Strecken werden mit Zwischenpunkten
    gerade gehalten, Parameter nach Bogenlänge - sonst schlägt die Kurve Schleifen."""
    dicht = [V(*pts[0])]
    for q in pts[1:]:
        a, b = dicht[-1], V(*q)
        n = max(1, int((b - a).Length // schritt))
        dicht += [a + (b - a) * (k / n) for k in range(1, n + 1)]
    par = [0.0]
    for a, b in zip(dicht, dicht[1:]):
        par.append(par[-1] + (b - a).Length)
    bs = Part.BSplineCurve()
    bs.interpolate(Points=dicht, Parameters=par)
    pfad = Part.Wire([bs.toShape()])
    t0 = bs.tangent(bs.FirstParameter)[0]
    profil = Part.Wire([Part.Circle(V(*pts[0]), t0, r).toShape()])
    # ebene Kurve mit Wendepunkten: Frenet kippt dort -> Profil mit fester Binormale (z) führen
    ps = Part.BRepOffsetAPI.MakePipeShell(pfad)
    ps.setBiNormalMode(V(0, 0, 1))
    ps.add(profil, False, False)
    ps.build()
    ps.makeSolid()
    rohr = ps.shape()
    o = doc.addObject("Part::Feature", name)
    o.Shape = rohr
    o.ViewObject.ShapeColor = FARBE["Kabel"]
    gruppe.addObject(o)
    return o


def kabel_gerade(name, x0, x1, y, z, r, doc, gruppe):
    o = doc.addObject("Part::Feature", name)
    o.Shape = Part.makeCylinder(r, x1 - x0, V(x0, y, z), V(1, 0, 0))
    o.ViewObject.ShapeColor = FARBE["Kabel"]
    gruppe.addObject(o)
    return o


def baue():
    doc = App.newDocument("kabelfuehrung")
    doc.License = "CERN-OHL-P-2.0"
    doc.LicenseURL = "https://ohwr.org/cern_ohl_p_v2.txt"
    teile = kf.neues_set(doc)
    k = teile["Kabelkachel"]
    g_teile = doc.addObject("App::DocumentObjectGroup", "Grundformen")
    g_teile.Label = "Grundformen (Werte in Tabelle Parameter)"
    for n in ("Parameter", "Kabelkachel", "Kreisverkehr", "Leerkachel", "Etagenkachel"):
        g_teile.addObject(teile[n])
        if n != "Parameter":
            teile[n].ViewObject.ShapeColor = FARBE[n]
            teile[n].ViewObject.Deviation = 0.05
    doc.recompute()

    # Beispielaufbau aus Links, Platzierung per Ausdruck (passt sich bei anderen Werten an)
    g_feld = doc.addObject("App::DocumentObjectGroup", "Aufbau")
    g_feld.Label = "Beispielaufbau (Links)"
    W, H = k.Laenge.Value, k.Breite.Value
    feld = [  # Name, Teil, a*W + b*H (x), c*W + d*H (y, relativ zur Feldbasis), Drehung
        ("A_Kachel_1", "Kabelkachel", (0, 0), (0, 0), 0), ("A_Kachel_2", "Kabelkachel", (1, 0), (0, 0), 0),
        ("A_Kachel_3", "Kabelkachel", (2, 0), (0, 0), 0), ("A_Kreisverkehr", "Kreisverkehr", (3, 0), (0, 0), 0),
        ("A_Kachel_4", "Kabelkachel", (3, 1), (0, 0), 0),
        ("V_Kachel_1", "Kabelkachel", (3, 1), (0, 1), 90), ("V_Kachel_2", "Kabelkachel", (3, 1), (1, 1), 90),
        ("B_Kachel_1", "Kabelkachel", (0, 0), (0, -1), 0), ("B_Kachel_2", "Kabelkachel", (1, 0), (0, -1), 0),
        ("B_Kachel_3", "Kabelkachel", (2, 0), (0, -1), 0), ("B_Leerkachel", "Leerkachel", (3, 0), (0, -1), 0),
        ("B_Kachel_4", "Kabelkachel", (3, 1), (0, -1), 0),
        ("C_Etagen_1", "Etagenkachel", (0, 0), (0, -2), 0), ("C_Etagen_2", "Etagenkachel", (1, 0), (0, -2), 0),
        ("C_Etagen_3", "Etagenkachel", (2, 0), (0, -2), 0),
    ]
    links = {}
    for name, teil, (a, b), (c, d), dreh in feld:
        lk = doc.addObject("App::Link", name)
        lk.setLink(teile[teil])
        lk.Label = name
        lk.Placement = App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), dreh))
        lk.setExpression("Placement.Base.x", "%g * Parameter.Laenge + %g * Parameter.Breite" % (a, b))
        # Feldbasis: drei Kachelbreiten + 100 mm über den Grundformen
        lk.setExpression("Placement.Base.y", "%g * Parameter.Laenge + %g * Parameter.Breite + 100 mm" %
                         (c, d + 3))
        g_feld.addObject(lk)
        links[name] = lk
    doc.recompute()

    # Beispielkabel (feste Körper für die aktuellen Werte)
    g_kabel = doc.addObject("App::DocumentObjectGroup", "Kabel")
    g_kabel.Label = "Beispielkabel (nur Anschauung, nicht parametrisch)"
    p = kf.STANDARD
    r, R, ys, _, _, _ = kf.masse(p)
    t = p["Dicke"]
    z = t + r
    Y0 = 3 * H + 100
    xa, xe, _, _ = kf.kachel_lagen(p)
    b = p["Hakenbreite"]
    dp = kf.poller_masse(p)[0]
    cx, cy = 3 * W + H / 2, Y0 + H / 2
    r1 = dp / 2 + r                     # innen am Poller
    r2 = r1 + 2 * r + 0.6               # außen herum
    ende = 4 * W + H + 15
    # Reihe B: zwei Kabel gerade über die Leerkachel
    for i, y in enumerate(ys):
        kabel_gerade("Kabel_B%d" % (i + 1), -15, ende, Y0 - H + y, z, r, doc, g_kabel)
    # Reihe A, obere Spur: links rein, innen um den Poller, nach oben in die senkrechte Reihe
    x_frei = 2 * W + xe + b / 2 + 3
    xv = 3 * W + H - ys[0]              # Spur der gedrehten Kachel
    bogen = [(cx + r1 * math.cos(math.radians(a)), cy + r1 * math.sin(math.radians(a))) for a in (-90, -60, -30, 0)]
    pts = [(-15, Y0 + ys[1]), (x_frei - 20, Y0 + ys[1]), (x_frei, Y0 + ys[1]), (x_frei + 12, Y0 + ys[1] - 7)] + \
        bogen + [(cx + r1 - 0.5, cy + 10), (xv + 3, Y0 + H + xa - b / 2 - 4), (xv, Y0 + H + xa),
                 (xv, Y0 + H + W), (xv, Y0 + H + 2 * W + 15)]
    kabel_kurve("Kabel_A_um_Poller", [(x, y, z) for x, y in pts], r, doc, g_kabel)
    # Reihe A, untere Spur: außen um den Poller herum und rechts weiter
    xr = 3 * W + H
    pts = [(-15, Y0 + ys[0]), (x_frei - 20, Y0 + ys[0]), (x_frei, Y0 + ys[0]), (cx - 9, cy - r2 + 1.5),
           (cx, cy - r2), (cx + 9, cy - r2 + 1.5), (xr + xa - b / 2 - 4, Y0 + ys[0] - 1), (xr + xa, Y0 + ys[0]),
           (xr + W, Y0 + ys[0]), (ende, Y0 + ys[0])]
    kabel_kurve("Kabel_A_gerade", [(x, y, z) for x, y in pts], r, doc, g_kabel)
    # Reihe C: je Etage beider Bäume ein Kabel
    for seite, i, d, y, zk in kf.etagen_kabel(p):
        kabel_gerade("Kabel_C%s%d" % (seite, i), -15, 3 * W + 15, Y0 - 2 * H + y, zk, d / 2.0, doc, g_kabel)
    # Probekabel über der einzelnen Kabelkachel und Etagenkachel (für die Profilansicht)
    for i, y in enumerate(ys):
        kabel_gerade("Kabel_Probe%d" % (i + 1), -12, W + 12, y, z, r, doc, g_kabel)
    xe0 = W + 2 * H + 60
    for seite, i, d, y, zk in kf.etagen_kabel(p):
        kabel_gerade("Kabel_Etage%s%d" % (seite, i), xe0 - 12, xe0 + W + 12, y, zk, d / 2.0, doc, g_kabel)
    doc.recompute()
    doc.saveAs(FCSTD)
    return doc


def cam(view, eye, up=(0, 0, 1), zoom=0.8):
    z = V(*eye).normalize()
    x = V(*up).cross(z).normalize()
    y = z.cross(x)
    m = App.Matrix(x.x, y.x, z.x, 0, x.y, y.y, z.y, 0, x.z, y.z, z.z, 0, 0, 0, 0, 1)
    view.setCameraType("Orthographic")
    view.setCameraOrientation(App.Placement(m).Rotation)
    view.fitAll()
    Gui.updateGui()
    view.fitAll()
    from pivy import coin  # noqa: F401
    c = view.getCameraNode()
    if hasattr(c, "height"):
        c.height.setValue(c.height.getValue() * zoom)


def zeige(doc, sichtbar):
    for o in doc.Objects:
        if o.isDerivedFrom("App::DocumentObjectGroup") or o.TypeId.startswith("Spreadsheet"):
            continue
        if hasattr(o, "ViewObject") and o.ViewObject is not None:
            o.ViewObject.Visibility = any(o.Name.startswith(s) for s in sichtbar)


def foto(view, name):
    path = os.path.join(OUT, name + ".png")
    for i in range(8):
        Gui.updateGui()
        time.sleep(0.4)
        try:
            view.saveImage(path, BW, BH, "Current", "Framebuffer")
        except TypeError:
            view.saveImage(path, BW, BH, "Current")
        if os.path.exists(path) and os.path.getsize(path) > 12000:
            strip_png(path)
            log("bild", name, os.path.getsize(path))
            return
    log("LEER", name)


def nur_ansicht(doc):
    """Schnitte und 1-Spur-Kachel nur für die Bilder (vor dem Speichern wieder entfernt, die FCStd bleibt
    rein parametrisch)."""
    p = kf.STANDARD
    r, R, ys, H, G, Go = kf.masse(p)
    W, t = p["Laenge"], p["Dicke"]
    xa, _, xm, lm = kf.kachel_lagen(p)
    k = kf.baue_kachel()
    sch = kf.schacht(p)
    xt = xm - sch / 2 - (lm - sch) / 4          # Mitte der linken Zunge
    neu = []

    def teil(name, form, farbe, dy):
        o = doc.addObject("Part::Feature", name)
        f = form.copy()
        f.translate(V(0, dy, 0))
        o.Shape = f
        o.ViewObject.ShapeColor = farbe
        o.ViewObject.Deviation = 0.05
        neu.append(o)

    for name, x, dy in (("Z_SchnittA", xa, -400), ("Z_SchnittM", xt, -600)):
        rest = Part.makeBox(W + 40, H + 40, 40, V(x, -20, -5))
        teil(name, k.cut(rest), FARBE["Kabelkachel"], dy)
        kabel = Part.makeCylinder(r, x + 12, V(-12, ys[0], t + r), V(1, 0, 0))
        for y in ys[1:]:
            kabel = kabel.fuse(Part.makeCylinder(r, x + 12, V(-12, y, t + r), V(1, 0, 0)))
        teil(name + "_Kabel", kabel, FARBE["Kabel"], dy)
    p1 = dict(p, Spuren=1)
    ys1 = kf.masse(p1)[2]
    teil("Z_Einspur", kf.baue_kachel(p1), FARBE["Kabelkachel"], -200)
    teil("Z_Kabel_Einspur", Part.makeCylinder(r, W + 24, V(-12, ys1[0], t + r), V(1, 0, 0)), FARBE["Kabel"], -200)

    # Etagenkachel im Schnitt durch einen Außenhaken und durch den Schraubenschacht, mit Kabeln
    e = kf.baue_etagenkachel()
    kabel = None
    for _, _, d, y, zk in kf.etagen_kabel(p):
        z1 = Part.makeCylinder(d / 2.0, xa + 12, V(-12, y, zk), V(1, 0, 0))
        kabel = z1 if kabel is None else kabel.fuse(z1)
    for name, x, dy in (("Z_EtagenSchnitt", xa, -1000), ("Z_EtagenMitte", xm, -1200)):
        teil(name, e.cut(Part.makeBox(W + 40, H + 40, 80, V(x, -20, -5))), FARBE["Etagenkachel"], dy)
        teil(name + "_Kabel", kabel, FARBE["Kabel"], dy)

    def bm(a, b):
        w = {"A_Etagen": len(a), "B_Etagen": len(b)}
        for s, liste in (("A", a), ("B", b)):
            for i, d in enumerate(liste):
                w["%s_Kabel%d" % (s, i + 1)] = float(d)
        return w

    # gemischte Größen: alle Teile gleich groß, alles passt aneinander
    mix = [("K10", kf.baue_kachel({"Kabeldurchmesser": 10.0}), "Kabelkachel", 0, 0),
           ("D4", kf.baue_etagenkachel(bm([4] * 3, [4] * 3)), "Etagenkachel", W, 0),
           ("E", e, "Etagenkachel", 2 * W, 0),
           ("K4", kf.baue_kachel({"Kabeldurchmesser": 4.0}), "Kabelkachel", 3 * W, 0),
           ("KV", kf.baue_kreisverkehr({"Kabeldurchmesser": 10.0}), "Kreisverkehr", 4 * W, 0),
           ("D8", kf.baue_etagenkachel(bm([8] * 2, [8] * 2)), "Etagenkachel", 0, H),
           ("K6e", kf.baue_kachel({"Kabeldurchmesser": 6.0, "Spuren": 1}), "Kabelkachel", W, H)]
    for name, form, farbe, x, y in mix:
        f = form.copy()
        f.translate(V(x, y, 0))
        teil("Z_Mix_" + name, f, FARBE[farbe], -1400)
    doc.recompute()
    return neu


AUFNAHMEN = [
    # Name, sichtbare Objekte (Präfixe), Blickrichtung, oben, Zoom
    ("kachel_2spur_wie_foto", ("Kabelkachel", "Kabel_Probe"), (0.18, -0.42, 1.0), (0, 1, 0), 0.72),
    ("kachel_1spur_wie_foto", ("Z_Einspur", "Z_Kabel_Einspur"), (0.18, -0.42, 1.0), (0, 1, 0), 0.72),
    ("kachel_1spur_leer", ("Z_Einspur",), (0.55, -1.0, 1.0), (0, 0, 1), 0.72),
    ("schnitt_aussenhaken", ("Z_SchnittA",), (1, 0, 0), (0, 0, 1), 0.62),
    ("schnitt_aussenhaken_schraeg", ("Z_SchnittA",), (1, -0.55, 0.45), (0, 0, 1), 0.66),
    ("schnitt_mittelzunge", ("Z_SchnittM",), (1, 0, 0), (0, 0, 1), 0.62),
    ("verbindung_oben", ("A_Kachel_1", "A_Kachel_2", "B_Kachel_1", "B_Kachel_2"), (0, 0, 1), (0, 1, 0), 0.75),
    ("kreuzung_oben", ("A_Kachel_3", "A_Kreisverkehr", "A_Kachel_4", "V_Kachel_1", "B_Kachel_3", "B_Leerkachel",
                       "B_Kachel_4"), (0, 0, 1), (0, 1, 0), 0.8),
    ("aufbau_iso", ("A_", "B_", "C_", "V_", "Kabel_A", "Kabel_B", "Kabel_C"), (-0.45, -1.0, 1.15), (0, 0, 1), 0.8),
    ("aufbau_oben", ("A_", "B_", "C_", "V_", "Kabel_A", "Kabel_B", "Kabel_C"), (0, 0, 1), (0, 1, 0), 0.88),
    ("aufbau_ohne_kabel", ("A_", "B_", "C_", "V_"), (0.35, -1.0, 1.25), (0, 0, 1), 0.8),
    ("grundformen", ("Kabelkachel", "Kreisverkehr", "Leerkachel", "Etagenkachel"), (0.35, -1.0, 0.9), (0, 0, 1),
     0.85),
    ("etagen_iso", ("Etagenkachel", "Kabel_Etage"), (-0.55, -1.0, 0.8), (0, 0, 1), 0.72),
    ("etagen_leer_iso", ("Etagenkachel",), (-0.55, -1.0, 0.8), (0, 0, 1), 0.72),
    ("etagen_schnitt", ("Z_EtagenSchnitt",), (1, 0, 0), (0, 0, 1), 0.66),
    ("etagen_schnitt_montiert", ("Z_EtagenSchnitt",), (1, 0, 0), (0, 0, -1), 0.66),
    ("etagen_schnitt_schraeg", ("Z_EtagenSchnitt",), (1, -0.55, 0.45), (0, 0, 1), 0.7),
    ("etagen_schnitt_schacht", ("Z_EtagenMitte",), (1, -0.35, 0.55), (0, 0, 1), 0.7),
    ("etagen_oben", ("Etagenkachel",), (0, 0, 1), (0, 1, 0), 0.72),
    ("etagen_reihe", ("C_", "Kabel_C"), (-0.4, -1.0, 0.75), (0, 0, 1), 0.78),
    ("gemischt_oben", ("Z_Mix",), (0, 0, 1), (0, 1, 0), 0.85),
    ("gemischt_iso", ("Z_Mix",), (-0.35, -1.0, 1.0), (0, 0, 1), 0.8),
    ("kachel_iso", ("Kabelkachel", "Kabel_Probe"), (0.55, -1.0, 0.95), (0, 0, 1), 0.72),
    ("kachel_leer_iso", ("Kabelkachel",), (-0.55, -1.0, 1.0), (0, 0, 1), 0.72),
    ("kachel_oben", ("Kabelkachel",), (0, 0, 1), (0, 1, 0), 0.75),
    ("kreisverkehr_iso", ("Kreisverkehr",), (0.6, -1.0, 0.9), (0, 0, 1), 0.72),
    ("unterseite", ("Kabelkachel", "Kreisverkehr", "Leerkachel", "Etagenkachel"), (0.3, -0.7, -1.0), (0, 0, 1),
     0.85),
]


def run():
    try:
        log("Start")
        Gui.getMainWindow().showMaximized()
        doc = baue()
        extra = nur_ansicht(doc)
        Gui.updateGui()
        view = Gui.getDocument(doc.Name).activeView()
        for name, sicht, eye, up, zoom in AUFNAHMEN:
            zeige(doc, sicht)
            cam(view, eye, up, zoom)
            foto(view, name)
        zeige(doc, ("Kabelkachel", "Kreisverkehr", "Leerkachel", "Etagenkachel", "A_", "B_", "C_", "V_", "Kabel_A",
                    "Kabel_B", "Kabel_C"))
        for o in extra:
            doc.removeObject(o.Name)
        doc.recompute()
        view.viewIsometric()
        view.fitAll()
        doc.save()
        log("FERTIG", FCSTD)
    except Exception as e:  # noqa: BLE001
        import traceback
        log("FEHLER", repr(e), traceback.format_exc())
    finally:
        os._exit(0)


from PySide import QtCore  # noqa: E402

QtCore.QTimer.singleShot(3000, run)
