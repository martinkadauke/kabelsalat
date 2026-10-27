# -*- coding: utf-8 -*-
"""Kabelführung zum Unter-den-Tisch-Schrauben – parametrisch, zwei Grundformen, puzzle-kompatibel.

Nach Fotos modularer Kabel-Kacheln mit Schnappklammern und "Kreisverkehr"-Poller.

Kabelkachel    gerade Spuren. Je Spur: zwei kurze Haken außen, ein langer Haken in der Mitte von der Gegenseite.
               Gegenüber jedem Haken steht ein niedriger Bord: zwischen Lippenspitze und Bord bleibt ein Fenster,
               etwas schmaler als das Kabel (Klemmung) -> das Kabel klickt hinein und lässt sich wieder ziehen.
               Bei zwei Spuren teilen sich die Haken einen Steg in der Mitte (T-Form).
               Schraube in Kachelmitte; ihr Schacht trennt den Mittelhaken in zwei Zungen.
Kreisverkehr   quadratische Kachel (Kante = Kachelbreite) mit Poller zum Umlenken; die Schraube sitzt
               unten im Poller. Ohne Poller ist es die Leerkachel für Kreuzungen.
Etagenkachel   zwei "Bäume" Rücken an Rücken auf einem vollen Kiel in der Kachelmitte, je bis zu drei Kabel
               übereinander, jede Etage mit eigenem Kabeldurchmesser. Die Kabel klicken von außen ein; jede Etage
               steht weiter innen als die darunter, damit ihr Fenster frei bleibt (stützenfrei). Schraube mittig
               im Kiel.

Alle Teile sind gleich groß (Laenge x Breite, 72 x 72 mm), unabhängig vom Kabel: alles passt an alles.
Koordinaten: X = Kabelrichtung, Y = quer, Z = vom Tisch weg; z = 0 liegt am Tisch und auf dem Druckbett.
Verbinder: Schnappklammer = Zinke mit Widerhaken, Schlitz, fester Körper; Gegenstück = Tasche mit Aussparung für
den Widerhaken. Klammer an +X (mittig) und +Y (zwei, gespiegelt, Haken nach außen), Taschen an -X und -Y.
Die X-Klammer sitzt mittig auf der Kante, darum passt eine um 90° gedrehte Kabelkachel an jede Kante des
Kreisverkehrs. Kacheln von vorn aufsetzen (Richtung Tisch drücken) - der Widerhaken fällt in seine Aussparung.

In FreeCAD (Datei liegt im Makro-Ordner): Makro "Kabelfuehrung" ausführen oder
    import kabelfuehrung as kf; kf.neues_set()
Gespeicherte Objekte lassen sich nur neu berechnen, wenn diese Datei im Makro-Ordner liegt.
"""
import math

import FreeCAD as App
import Part

V = App.Vector
SQ2 = math.sqrt(2.0)

# Name, Gruppe, Typ, Standard, Erklärung
PARAMETER = [
    ("Kabeldurchmesser", "Kabel", "Length", 6.0, "Außendurchmesser des Kabels (nachmessen)"),
    ("Spiel", "Kabel", "Length", 0.4, "Luft rund ums Kabel im Kanal"),
    ("Spuren", "Kabel", "Integer", 2, "Kabel nebeneinander auf der Kabelkachel"),
    ("Ueberdeckung", "Kabel", "Float", 0.6, "Hakenlippe reicht so viele Kabelradien über die Kabelmitte"),
    ("Klemmung", "Kabel", "Length", 0.4, "Fenster zwischen Lippe und Bord ist um so viel enger als das Kabel"),
    ("Laenge", "Kachel", "Length", 72.0, "Kachellänge in Kabelrichtung"),
    ("Breite", "Kachel", "Length", 72.0, "Kachelbreite quer zum Kabel; für alle Teile gleich, damit alles passt"),
    ("Dicke", "Kachel", "Length", 3.0, "Plattendicke"),
    ("Hakenbreite", "Kachel", "Length", 10.0, "Breite der kurzen Haken in Kabelrichtung"),
    ("Steg", "Kachel", "Length", 2.4, "Wandstärke des Hakenstegs"),
    ("Lippe", "Kachel", "Length", 1.8, "Dicke der Hakenlippe und des Pollerrands"),
    ("Bordbreite", "Kachel", "Length", 2.4, "Breite des Bords gegenüber den Haken"),
    ("Bordabstand", "Kachel", "Length", 0.0, "Luft zwischen Kanal und Bord; 0 = automatisch (0,25 x Kabel)"),
    ("Bordhoehe", "Kachel", "Length", 0.0, "Höhe des Bords; 0 = automatisch aus Kabel und Klemmung"),
    ("KlammerLaenge", "Klammer", "Length", 8.0, "So weit steht die Schnappklammer über die Kante"),
    ("KlammerBreite", "Klammer", "Length", 8.5, "Breite der Schnappklammer ohne Widerhaken"),
    ("Zinke", "Klammer", "Length", 2.0, "Breite der federnden Zinke mit Widerhaken"),
    ("Schlitz", "Klammer", "Length", 1.2, "Schlitz zwischen Zinke und Klammerkörper"),
    ("Widerhaken", "Klammer", "Length", 0.8, "Überstand des Widerhakens"),
    ("PuzzleSpiel", "Klammer", "Length", 0.2, "Luft je Seite in der Tasche"),
    ("Schraube", "Schraube", "Length", 3.5, "Gewinde der Senkkopf-Holzschraube"),
    ("Kopf", "Schraube", "Length", 7.0, "Kopfdurchmesser der Schraube"),
    ("PollerD", "Poller", "Length", 0.0, "Pollerdurchmesser; 0 = automatisch (3 x Kabel + 2 mm)"),
    ("PollerLagen", "Poller", "Integer", 1, "Kabellagen übereinander unter dem Pollerrand"),
    ("Pollerrand", "Poller", "Length", 0.0, "Überstand des Rands oben am Poller; 0 = automatisch"),
    ("A_Etagen", "Etagenkachel", "Integer", 3, "Baum auf Seite A (Seite mit den Taschen): Etagen, 0 bis 3"),
    ("A_Kabel1", "Etagenkachel", "Length", 4.0, "Seite A, Etage 1 (am Tisch): Kabeldurchmesser"),
    ("A_Kabel2", "Etagenkachel", "Length", 6.0, "Seite A, Etage 2: Kabeldurchmesser"),
    ("A_Kabel3", "Etagenkachel", "Length", 4.0, "Seite A, Etage 3 (am weitesten vom Tisch): Kabeldurchmesser"),
    ("B_Etagen", "Etagenkachel", "Integer", 3, "Baum auf Seite B (Seite mit den Klammern): Etagen, 0 bis 3"),
    ("B_Kabel1", "Etagenkachel", "Length", 10.0, "Seite B, Etage 1 (am Tisch): Kabeldurchmesser"),
    ("B_Kabel2", "Etagenkachel", "Length", 10.0, "Seite B, Etage 2: Kabeldurchmesser"),
    ("B_Kabel3", "Etagenkachel", "Length", 10.0, "Seite B, Etage 3 (am weitesten vom Tisch): Kabeldurchmesser"),
    ("EtagenBordabstand", "Etagenkachel", "Length", 0.0, "Luft zwischen Kanal und Bord in den Bäumen; 0 = kompakt"),
]
STANDARD = {n: w for n, _, _, w, _ in PARAMETER}
NUR_KACHEL = {"Ueberdeckung", "Klemmung", "Laenge", "Hakenbreite", "Bordhoehe"}
NUR_POLLER = {"PollerD", "PollerLagen", "Pollerrand"}
NUR_ETAGE = {"A_Etagen", "A_Kabel1", "A_Kabel2", "A_Kabel3", "B_Etagen", "B_Kabel1", "B_Kabel2", "B_Kabel3",
             "EtagenBordabstand"}
MAX_ETAGEN = 3
SEITEN = (("A", -1), ("B", 1))           # Seite A Richtung -y (Taschen), B Richtung +y (Klammern)


# ---------------------------------------------------------------- Maße

def masse(p):
    """Kabelradius r, Kanalradius R, Spurmitten ys, Kachelbreite H, Lücke zwischen Kanälen G, außen Go.
    Die Breite ist fest (alle Teile gleich groß), die Spuren liegen mittig."""
    r = p["Kabeldurchmesser"] / 2.0
    R = r + p["Spiel"]
    n = max(1, int(p["Spuren"]))
    G = max(p["Steg"], p["Bordbreite"] + 2 * bordabstand(p))      # zwischen zwei Spuren: T-Steg oder Bord
    Go = max(p["Steg"], p["Bordbreite"] + bordabstand(p))         # außen: Steg oder Bord
    H = p["Breite"]
    rand = (H - 2 * Go - n * 2 * R - (n - 1) * G) / 2.0
    ys = [rand + Go + R + i * (2 * R + G) for i in range(n)]
    return r, R, ys, H, G, Go


def bordabstand(p):
    if p.get("_bordabstand") is not None:                # Etage eines Baums (EtagenBordabstand, 0 erlaubt)
        return p["_bordabstand"]
    return p["Bordabstand"] if p["Bordabstand"] > 0 else 0.25 * p["Kabeldurchmesser"]


def taschentiefe(p):
    return p["KlammerLaenge"] + p["PuzzleSpiel"]


def senkkopf(p):
    """Bohrung, Senkungsdurchmesser oben, Senktiefe (90°)."""
    d = p["Schraube"] + 0.4
    tiefe = min((p["Kopf"] + 0.6 - d) / 2.0, p["Dicke"] - 0.6)
    return d, d + 2 * tiefe, tiefe


def schacht(p):
    """Durchmesser des Schachts für Schraubenkopf und Bit."""
    return p["Kopf"] + 1.0


def lippen_rundung(p):
    return min(0.6, 0.3 * p["Lippe"])


def bord_rundung(p):
    return min(0.8, 0.4 * p["Bordbreite"])


def bordhoehe(p):
    """Bordhöhe über der Platte. Automatisch so, dass das Fenster zwischen gerundeter Lippenspitze und gerundeter
    Bordkante = Kabel - Klemmung ist (Abstand der Rundungsmittelpunkte minus beide Radien)."""
    if p["Bordhoehe"] > 0:
        return p["Bordhoehe"]
    d, c = p["Kabeldurchmesser"], p["Spiel"]
    r, R = d / 2.0, d / 2.0 + c
    ut = -p["Ueberdeckung"] * r
    r1, r2 = lippen_rundung(p), bord_rundung(p)
    fenster = d - p["Klemmung"]
    du = ut + R + bordabstand(p) + r1 + r2
    dz = math.sqrt(max(0.0, (fenster + r1 + r2) ** 2 - du ** 2))
    h = (d + c) + r1 + r2 - dz
    return max(r2 + 0.4, min(h, 0.6 * d))


def fenster(p):
    """Tatsächliches Fenster zwischen Lippenspitze und Bord (für den Prüfbericht)."""
    d, c = p["Kabeldurchmesser"], p["Spiel"]
    r, R = d / 2.0, d / 2.0 + c
    ut = -p["Ueberdeckung"] * r
    r1, r2 = lippen_rundung(p), bord_rundung(p)
    du = ut + R + bordabstand(p) + r1 + r2
    dz = (d + c) + r1 + r2 - bordhoehe(p)
    return math.hypot(du, dz) - r1 - r2


def kachel_lagen(p):
    """x-Lagen: kurze Haken außen, langer Haken in der Mitte."""
    W, b = p["Laenge"], p["Hakenbreite"]
    xa = taschentiefe(p) + 1.0 + b / 2
    lm = schacht(p) + 2 * 0.7 * b
    return xa, W - xa, W / 2, lm


def poller_masse(p):
    """Durchmesser, Randüberstand, Unterkante Rand, Oberkante."""
    S = masse(p)[3]
    d = p["Kabeldurchmesser"]
    dp = p["PollerD"] if p["PollerD"] > 0 else max(14.0, 3 * d + 2.0)
    dp = min(dp, S - 2 * taschentiefe(p) - 2.0)          # Fuß steht ganz auf der Platte, nicht über einer Tasche
    ue = p["Pollerrand"] if p["Pollerrand"] > 0 else max(1.0, 0.2 * d)
    zr = p["Dicke"] + max(1, int(p["PollerLagen"])) * (d + p["Spiel"])
    return dp, ue, zr, zr + p["Lippe"]


def pruefe(p, art="kachel"):
    """Unsinnige Kombinationen mit verständlicher Meldung abfangen (FreeCAD zeigt sie beim Neuberechnen).
    art: "kachel", "kreisverkehr" oder "etagen"."""
    f = []
    if art == "etagen":
        for seite, _ in SEITEN:
            n = int(p["%s_Etagen" % seite])
            if not 0 <= n <= MAX_ETAGEN:
                f.append("%s_Etagen: 0 bis %d" % (seite, MAX_ETAGEN))
            for i in range(max(0, min(n, MAX_ETAGEN))):
                if p["%s_Kabel%d" % (seite, i + 1)] < 1.0:
                    f.append("%s_Kabel%d: Kabeldurchmesser unter 1 mm" % (seite, i + 1))
        if int(p["A_Etagen"]) <= 0 and int(p["B_Etagen"]) <= 0:
            f.append("Keine Etagen: mindestens eine Seite braucht 1 bis 3 Etagen")
        if not f:
            for seite, r in SEITEN:
                et = baum(p, seite)
                if et:
                    aussen = baum_aussen(p, et[0])
                    # Seite A: Bord muss vor den Klammertaschen bleiben; Seite B hat außen nur Klammern
                    platz = p["Breite"] / 2.0 - (taschentiefe(p) + 1.0 if r < 0 else 1.0)
                    if aussen > platz + 1e-9:
                        f.append("Baum %s zu breit: %.1f mm von der Mitte, Platz %.1f mm (dicke Kabel weiter oben "
                                 "oder auf Seite B)" % (seite, aussen, platz))
    elif p["Kabeldurchmesser"] < 1.0:
        f.append("Kabeldurchmesser unter 1 mm")
    if p["Zinke"] + p["Schlitz"] > p["KlammerBreite"] - 2.0:
        f.append("Klammer zu schmal für Zinke + Schlitz (Körper braucht 2 mm)")
    if p["Widerhaken"] >= p["Zinke"]:
        f.append("Widerhaken muss kleiner als die Zinke sein")
    _, R, ys, H, _, Go = masse(p)
    if p["KlammerBreite"] + 2 * p["Widerhaken"] + 2 > H:
        f.append("Kachel zu schmal für die Schnappklammer")
    if art == "kachel":
        rand = ys[0] - R - Go
        if rand < taschentiefe(p) + 1.0 - 1e-9:
            f.append("Breite zu klein für %d Spuren à %g mm: mindestens %.1f mm" %
                     (len(ys), p["Kabeldurchmesser"], H + 2 * (taschentiefe(p) + 1.0 - rand)))
    if art in ("kachel", "etagen"):
        W, b = p["Laenge"], p["Hakenbreite"]
        xa, _, xm, lm = kachel_lagen(p)
        if xa + b / 2 + 2.0 > xm - lm / 2:
            f.append("Kachel zu kurz: mindestens %.1f mm Länge" % (2 * (xa + b / 2 + 2.0) + lm))
        if W / 4 < p["KlammerBreite"] / 2 + p["Widerhaken"] + p["PuzzleSpiel"] + 1.0:
            f.append("Kachel zu kurz für die Klammern oben/unten")
        if p["Ueberdeckung"] < 0:
            f.append("Ueberdeckung negativ: die Lippe reicht nicht bis zur Kabelmitte")
    else:
        if poller_masse(p)[0] < schacht(p) + 3.2:
            f.append("Poller zu dünn für den Schraubenkopf: mehr Spuren/Rand (größere Kachel) oder kleinere Schraube")
    if f:
        raise ValueError("; ".join(f))


# ---------------------------------------------------------------- Boolesche Schritte mit Wächter

def _sauber(s):
    """removeSplitter auf einer KOPIE (beschädigt sonst das Original) - nur übernehmen, wenn gültig und volumengleich."""
    try:
        k = s.copy().removeSplitter()
        if k.isValid() and len(k.Solids) == 1 and abs(k.Volume - s.Volume) < 1e-4 * max(1.0, s.Volume):
            return k.Solids[0]
    except Exception:  # noqa: BLE001
        pass
    return s


def _dazu(a, teile, was):
    for i, t in enumerate(teile):
        v0 = a.Volume
        r = a.fuse(t).Solids
        if len(r) != 1 or not r[0].isValid() or not (v0 + 1e-6 < r[0].Volume <= v0 + t.Volume + 1e-3):
            raise RuntimeError("%s: Vereinigung %d fehlgeschlagen (%d Körper)" % (was, i, len(r)))
        a = r[0]
    return _sauber(a)


def _weg(a, werkzeuge, was):
    for i, t in enumerate(werkzeuge):
        v0 = a.Volume
        r = a.cut(t).Solids
        if len(r) != 1 or not r[0].isValid() or not (v0 - t.Volume - 1e-3 <= r[0].Volume < v0 - 1e-6):
            raise RuntimeError("%s: Schnitt %d fehlgeschlagen (%d Körper)" % (was, i, len(r)))
        a = r[0]
    return _sauber(a)


def _setze(form, x, y, winkel=0.0):
    s = form.copy()
    if winkel:
        s.rotate(V(0, 0, 0), V(0, 0, 1), winkel)
    s.translate(V(x, y, 0))
    return s


def _gespiegelt(form):
    """Spiegeln an der xz-Ebene (y -> -y)."""
    return form.mirror(V(0, 0, 0), V(0, 1, 0))


def _flaeche(pts):
    return Part.Face(Part.makePolygon([V(a, b, 0) for a, b in pts] + [V(pts[0][0], pts[0][1], 0)]))


def _stadion(laenge, breite):
    """Langloch-Fläche (runde Enden) längs x, mittig um 0."""
    r = breite / 2.0
    a = max(0.0, (laenge - breite) / 2.0)
    if a < 1e-6:
        return Part.Face(Part.Wire(Part.makeCircle(r)))
    kanten = [Part.LineSegment(V(-a, -r, 0), V(a, -r, 0)).toShape(),
              Part.Arc(V(a, -r, 0), V(a + r, 0, 0), V(a, r, 0)).toShape(),
              Part.LineSegment(V(a, r, 0), V(-a, r, 0)).toShape(),
              Part.Arc(V(-a, r, 0), V(-a - r, 0, 0), V(-a, -r, 0)).toShape()]
    return Part.Face(Part.Wire(kanten))


# ---------------------------------------------------------------- Bauteile

def _klammer_umriss(p, a0):
    """Umriss der Schnappklammer im Kantenrahmen: Kante bei a = 0, a nach außen, b längs der Kante (Mitte 0).
    Zinke mit Widerhaken auf der -b-Seite; Widerhaken mit Rastkante zur Kachel hin und Anlaufschräge an der Spitze."""
    L, w, bh = p["KlammerLaenge"], p["KlammerBreite"], p["Widerhaken"]
    bl = min(2.6, 0.35 * L)
    rampe = min(1.2, 0.5 * bl)
    return [(a0, -w / 2), (L - bl, -w / 2), (L - bl, -w / 2 - bh), (L - rampe, -w / 2 - bh), (L, -w / 2),
            (L, w / 2), (a0, w / 2)]


def klammer(p):
    """Schnappklammer (steht über die Kante), Kantenrahmen wie _klammer_umriss."""
    t, L, w = p["Dicke"], p["KlammerLaenge"], p["KlammerBreite"]
    k = _flaeche(_klammer_umriss(p, -0.5)).extrude(V(0, 0, t))
    schlitz = Part.makeBox(L + 1.0, p["Schlitz"], t + 2.0, V(0.0, -w / 2 + p["Zinke"], -1.0))
    return k.cut(schlitz).Solids[0]


def tasche(p):
    """Tasche für die Schnappklammer: Umriss ohne Schlitz, rundum um PuzzleSpiel größer."""
    f = _flaeche(_klammer_umriss(p, -1.5)).makeOffset2D(p["PuzzleSpiel"], 0)
    f.translate(V(0, 0, -1.0))
    return f.extrude(V(0, 0, p["Dicke"] + 2.0)).Solids[0]


def _senkloch(p, x, y):
    d, k, tiefe = senkkopf(p)
    t = p["Dicke"]
    loch = Part.makeCylinder(d / 2, t + 2, V(x, y, -1))
    senk = Part.makeCone(d / 2, k / 2, tiefe, V(x, y, t - tiefe))
    oben = Part.makeCylinder(k / 2, 1.0, V(x, y, t))
    return loch.fuse(senk).fuse(oben).Solids[0]


def _kante_runden(form, y, z, radius):
    """Kante parallel zu x bei (y, z) runden."""
    for e in form.Edges:
        a, b = e.Vertexes[0].Point, e.Vertexes[-1].Point
        if (abs(a.y - y) < 1e-6 and abs(b.y - y) < 1e-6 and abs(a.z - z) < 1e-6 and abs(b.z - z) < 1e-6
                and abs(a.x - b.x) > 1e-3):
            return form.makeFillet(radius, [e])
    raise RuntimeError("Kante bei y=%.2f z=%.2f nicht gefunden" % (y, z))


def spitzen_rundung(p):
    return min(1.0, 0.55 * p["Lippe"])


def haken(p, laenge, steg=None, ausladung=0.0, oben=True, kappe=None):
    """Haken für eine Spur mit Mitte y = 0: Steg auf +y, Lippe über dem Kabel nach -y, mittig um x = 0.
    steg: Stegbreite (zwischen zwei Spuren die ganze Lücke, dann decken sich die Stege beider Spuren = T-Haken).
    ausladung: Steg oben um so viel nach +y verbreitert, mit 45° darunter.
    oben=False: flache Oberseite bis zur Lippenspitze ohne Rundungen und Zungenform, weil darauf die nächste
    Etage steht (ihr Bord bündig an der Spitze).
    kappe: Außenkante des Stegs oben rund (Standard wie oben; aus, wenn der Steg am Kiel anliegt).

    Unterseite der Lippe: 45°-Keil am Steg (tangential zum runden Kanal, der die Ecke nicht braucht), dann
    waagrecht bis zur Spitze -> druckt ohne Stützen, waagrecht frei sind nur ~3 mm.
    """
    t = p["Dicke"]
    r = p["Kabeldurchmesser"] / 2.0
    c = p["Spiel"]
    R = r + c
    s, l, b = steg or p["Steg"], p["Lippe"], laenge
    zl = t + 2 * r + c                    # Unterkante Lippe = Kabeloberkante + Spiel
    zt = zl + l
    ug = (SQ2 - 1) * R                    # Keil endet hier an der Lippe ...
    zg = t + r + (SQ2 - 1) * R            # ... und beginnt hier am Steg
    ut = -p["Ueberdeckung"] * r           # Lippenspitze (negativ = über die Kabelmitte hinaus)
    a, zb = ausladung, t - 0.5
    if a <= 1e-6:
        aussen = [(R + s, zb), (R + s, zt)]
    elif zt - a > zb:
        aussen = [(R + s, zb), (R + s, zt - a), (R + s + a, zt)]
    else:                                 # Ausladung höher als der Haken: Fuß gleich breiter
        aussen = [(R + s + a - (zt - zb), zb), (R + s + a, zt)]
    pts = aussen + [(ut, zt), (ut, zl), (ug, zl), (R, zg), (R, zb)]
    poly = Part.makePolygon([V(-b / 2, u, z) for u, z in pts] + [V(-b / 2, pts[0][0], pts[0][1])])
    form = Part.Face(poly).extrude(V(b, 0, 0))
    if oben if kappe is None else kappe:
        form = _kante_runden(form, R + s + a, zt, min(2.0, 0.8 * s))     # Kappe außen rund (C-Form wie im Foto)
    if oben:
        form = _kante_runden(form, ut, zt, spitzen_rundung(p))
    form = _kante_runden(form, ut, zl, lippen_rundung(p))
    if not oben:
        return form.Solids[0]
    # Draufsicht: Lippe als Zunge mit runden Ecken
    rho = min(0.4 * b, 0.8 * (R - ut))
    z0, h = t - 1.0, zt - t + 2.0
    u0, u1 = ut - 1.0, R + s + a + 1.0
    zunge = Part.makeBox(b, u1 - ut - rho, h, V(-b / 2, ut + rho, z0))
    for teil in (Part.makeBox(b - 2 * rho, ut + rho - u0, h, V(-b / 2 + rho, u0, z0)),
                 Part.makeCylinder(rho, h, V(-b / 2 + rho, ut + rho, z0)),
                 Part.makeCylinder(rho, h, V(b / 2 - rho, ut + rho, z0))):
        zunge = zunge.fuse(teil)
    erg = form.common(zunge).Solids
    if len(erg) != 1 or not erg[0].isValid():
        raise RuntimeError("Haken: Zungenform fehlgeschlagen")
    return erg[0]


def bord(p, laenge):
    """Bord gegenüber einem Haken: Langloch-Grundriss, oben rundum gerundet, mittig um (0, 0)."""
    t = p["Dicke"]
    h = bordhoehe(p)
    form = _stadion(laenge, p["Bordbreite"]).extrude(V(0, 0, h + 0.5))
    form.translate(V(0, 0, t - 0.5))
    oben = [e for e in form.Edges if all(abs(v.Point.z - (t + h)) < 1e-6 for v in e.Vertexes)]
    return form.makeFillet(min(bord_rundung(p), h - 0.2), oben).Solids[0]


def poller(p):
    """Poller um die z-Achse: Fuß ab Plattenoberkante, Rand oben mit 45°-Unterseite (stützenfrei)."""
    t, l = p["Dicke"], p["Lippe"]
    dp, ue, zr, zt = poller_masse(p)
    rp, f = dp / 2.0, min(0.6, 0.4 * l)
    prof = [(0, t - 0.5), (rp, t - 0.5), (rp, zr - ue), (rp + ue, zr), (rp + ue, zt - f), (rp + ue - f, zt), (0, zt)]
    poly = Part.makePolygon([V(x, 0, z) for x, z in prof] + [V(prof[0][0], 0, prof[0][1])])
    return Part.Face(poly).revolve(V(0, 0, 0), V(0, 0, 1), 360).Solids[0]


# ---------------------------------------------------------------- Grundformen

def baue_kachel(werte=None):
    p = dict(STANDARD, **(werte or {}))
    pruefe(p, "kachel")
    r, R, ys, H, G, _ = masse(p)
    W, t = p["Laenge"], p["Dicke"]
    n = len(ys)
    kl, ta = klammer(p), tasche(p)
    # Klammern: +X mittig, +Y zwei Stück (links gespiegelt -> Widerhaken zeigen nach außen)
    plus = [_setze(kl, W, H / 2), _setze(_gespiegelt(kl), W / 4, H, 90), _setze(kl, 3 * W / 4, H, 90)]
    minus = [_setze(ta, 0, H / 2), _setze(_gespiegelt(ta), W / 4, 0, 90), _setze(ta, 3 * W / 4, 0, 90)]
    # Haken + Borde. Seite s = +1: Steg auf +y. Mitte von der Gegenseite der Außenhaken; benachbarte Spuren
    # wechseln -> zwischen zwei Spuren treffen sich die Stege (T-Haken) bzw. die Borde (ein gemeinsamer Bord).
    xa, xe, xm, lm = kachel_lagen(p)
    b = p["Hakenbreite"]
    g, wb = bordabstand(p), p["Bordbreite"]
    formen = {}

    def hk(laenge, seite, innen):
        key = ("h", laenge, seite, innen)
        if key not in formen:
            h = haken(p, laenge, G if innen else None)
            formen[key] = h if seite > 0 else _gespiegelt(h)
        return formen[key]

    def bd(laenge):
        key = ("b", laenge)
        if key not in formen:
            formen[key] = bord(p, laenge)
        return formen[key]

    borde = {}
    for i, y in enumerate(ys):
        s_mitte = -1 if (n - 1 - i) % 2 == 0 else 1
        for x, laenge, s in ((xa, b, -s_mitte), (xm, lm, s_mitte), (xe, b, -s_mitte)):
            innen = (s > 0 and i < n - 1) or (s < 0 and i > 0)
            plus.append(_setze(hk(laenge, s, innen), x, y))
            yb = round(y - s * (R + g + wb / 2), 6)
            borde[(round(x, 6), yb)] = laenge + (1.0 if laenge == b else 2.0)
    for (x, yb), laenge in sorted(borde.items()):
        plus.append(_setze(bd(laenge), x, yb))
    form = _dazu(Part.makeBox(W, H, t), plus, "Kabelkachel")
    zt = bauhoehe(p, "kachel")
    minus += [_senkloch(p, W / 2, H / 2),
              Part.makeCylinder(schacht(p) / 2, zt + 1.0 - t, V(W / 2, H / 2, t))]
    if n % 2 == 0:
        # Schraube zwischen zwei Spuren: der T-Mittelhaken wird quer ganz durchgetrennt -> zwei Zungen (Foto)
        ut = -p["Ueberdeckung"] * r
        y0, y1 = ys[n // 2 - 1] + ut - 1.0, ys[n // 2] - ut + 1.0
        minus.append(Part.makeBox(schacht(p), y1 - y0, zt + 1.0 - t, V(W / 2 - schacht(p) / 2, y0, t)))
    return _weg(form, minus, "Kabelkachel")


def baue_kreisverkehr(werte=None, mit_poller=True):
    p = dict(STANDARD, **(werte or {}))
    pruefe(p, "kreisverkehr")
    S = masse(p)[3]
    t, m = p["Dicke"], S / 2
    kl, ta = klammer(p), tasche(p)
    # gleiche Klammer wie an der Stirnseite der Kabelkachel, auf allen vier Kanten mittig (Rahmen um 90° gedreht)
    plus = [_setze(kl, S, m), _setze(kl, m, S, 90)]
    if mit_poller:
        plus.append(_setze(poller(p), m, m))
    form = _dazu(Part.makeBox(S, S, t), plus, "Kreisverkehr")
    minus = [_setze(ta, 0, m), _setze(ta, m, 0, 90), _senkloch(p, m, m)]
    if mit_poller:   # Schacht für Schraubenkopf und Bit bis auf die Platte
        zt = poller_masse(p)[3]
        minus.append(Part.makeCylinder(schacht(p) / 2, zt + 1.0 - t, V(m, m, t)))
    return _weg(form, minus, "Kreisverkehr" if mit_poller else "Leerkachel")


def baum(p, seite):
    """Baum einer Seite ("A" oder "B"): Etagen vom Tisch aus als (Parameter der Etage, Abstand der Spurmitte von
    der Kachelmitte, Boden z).

    Die oberste Etage liegt mit ihrem Steg am Kiel. Jede tiefere Etage liegt so weit außen, dass der Bord der
    Etage darüber bündig auf ihrer Lippenspitze steht. So ist das Fenster jeder Etage nach außen frei: das Kabel
    kommt von der Seite und klickt unter die Lippe. Alles steht auf dem Kiel oder auf der Lippe darunter."""
    n = min(MAX_ETAGEN, max(0, int(p["%s_Etagen" % seite])))
    c, l, s, wb = p["Spiel"], p["Lippe"], p["Steg"], p["Bordbreite"]
    pes = [dict(p, Kabeldurchmesser=p["%s_Kabel%d" % (seite, i + 1)], _bordabstand=p["EtagenBordabstand"])
           for i in range(n)]
    R = [pe["Kabeldurchmesser"] / 2.0 + c for pe in pes]
    a = [0.0] * n
    for i in range(n - 1, -1, -1):
        a[i] = s + R[i]                                              # Steg liegt am Kiel
        if i + 1 < n:                                                # Bord darüber auf der Lippenspitze
            a[i] = max(a[i], a[i + 1] + R[i + 1] + bordabstand(pes[i + 1]) + wb
                       - p["Ueberdeckung"] * pes[i]["Kabeldurchmesser"] / 2.0)
    liste, z = [], p["Dicke"]
    for i in range(n):
        liste.append((pes[i], a[i], z))
        z += pes[i]["Kabeldurchmesser"] + c + l
    return liste


def baeume(p):
    """Beide Bäume {seite: (richtung, etagen)} und Oberkante des Kiels (= höchste Etage)."""
    bm = {seite: (r, baum(p, seite)) for seite, r in SEITEN}
    oben = max([z + pe["Kabeldurchmesser"] + p["Spiel"] + p["Lippe"] for _, et in bm.values() for pe, _, z in et]
               + [p["Dicke"]])
    return bm, oben


def baum_aussen(p, etage):
    """Abstand der Bord-Außenkante der untersten Etage von der Kachelmitte."""
    pe, a, _ = etage
    return a + pe["Kabeldurchmesser"] / 2.0 + p["Spiel"] + bordabstand(pe) + p["Bordbreite"]


def etagen_kabel(p):
    """Alle Kabel der Etagenkachel: (Seite, Etage, Durchmesser, y, z der Kabelmitte, wenn es auf dem Boden liegt)."""
    m = p["Breite"] / 2.0
    bm, _ = baeume(p)
    return [(seite, i + 1, pe["Kabeldurchmesser"], m + r * a, z + pe["Kabeldurchmesser"] / 2.0)
            for seite, (r, et) in bm.items() for i, (pe, a, z) in enumerate(et)]


def baue_etagenkachel(werte=None):
    p = dict(STANDARD, **(werte or {}))
    pruefe(p, "etagen")
    W, H, t, s, wb = p["Laenge"], p["Breite"], p["Dicke"], p["Steg"], p["Bordbreite"]
    c, l, m = p["Spiel"], p["Lippe"], H / 2.0
    bm, zo = baeume(p)
    kl, ta = klammer(p), tasche(p)
    plus = [_setze(kl, W, H / 2), _setze(_gespiegelt(kl), W / 4, H, 90), _setze(kl, 3 * W / 4, H, 90)]
    minus = [_setze(ta, 0, H / 2), _setze(_gespiegelt(ta), W / 4, 0, 90), _setze(ta, 3 * W / 4, 0, 90)]
    xa, xe, xm, lm = kachel_lagen(p)
    b, sch = p["Hakenbreite"], schacht(p)
    tm = (lm - sch) / 2.0                       # Mittelhaken als zwei Zungen, dazwischen der Schraubenschacht
    lagen = ((xa, b), (xm - (sch + tm) / 2.0, tm), (xm + (sch + tm) / 2.0, tm), (xe, b))
    x0, x1 = xa - b / 2.0, xe + b / 2.0
    schlitze = []
    for seite, (r, et) in bm.items():
        # Kiel: treppenförmig bis an die Stege jeder Etage, über dem eigenen Baum in Stegbreite bis ganz oben.
        # Er läuft über die ganze Kachel und trägt alles; zur Mitte hin stößt er an den Kiel der anderen Seite.
        stufen, zu = [], t - 0.5
        for pe, a, z in et:
            zt = z + pe["Kabeldurchmesser"] + c + l
            stufen.append((a - pe["Kabeldurchmesser"] / 2.0 - c, zu, zt))
            zu = zt
        stufen.append((stufen[-1][0] if stufen else s, zu, zo))
        pts = [(0.0, t - 0.5)]
        for u, z_von, z_bis in stufen:
            pts += [(u, z_von), (u, z_bis)]
        pts.append((0.0, zo))
        rein = [q for i, q in enumerate(pts) if i == 0 or abs(q[0] - pts[i - 1][0]) + abs(q[1] - pts[i - 1][1]) > 1e-6]
        rein = [q for i, q in enumerate(rein) if i == 0 or i == len(rein) - 1 or
                abs((q[0] - rein[i - 1][0]) * (rein[i + 1][1] - q[1]) - (q[1] - rein[i - 1][1]) * (rein[i + 1][0] - q[0])) > 1e-9]
        poly = Part.makePolygon([V(x0, m + r * u, z) for u, z in rein] + [V(x0, m + r * rein[0][0], rein[0][1])])
        plus.append(Part.Face(poly).extrude(V(x1 - x0, 0, 0)))
        schlitz = None                          # zu dünn neben dem Schacht: dort den Kiel ganz ausschneiden
        for u, z_von, z_bis in stufen:
            z_von = max(z_von, t)
            if u < sch / 2.0 + 1.2 and z_bis - z_von > 1e-6:
                kasten = Part.makeBox(sch, u + 0.5, z_bis - z_von + (1.0 if z_bis >= zo else 0.0),
                                      V(xm - sch / 2.0, min(m, m + r * (u + 0.5)), z_von))
                schlitz = kasten if schlitz is None else schlitz.fuse(kasten)
        if schlitz is not None:
            schlitze.append(schlitz)
        # Haken (Steg zur Mitte) und Borde (außen); Bord der unteren Etage auf der Platte, darüber auf der Lippe
        for i, (pe, a, z) in enumerate(et):
            R = pe["Kabeldurchmesser"] / 2.0 + c
            formen = {}
            for laenge in (b, tm):
                hk = haken(pe, laenge, oben=(i == len(et) - 1), kappe=False)
                if r > 0:
                    hk = _gespiegelt(hk)
                bd = bord(pe, laenge + (1.0 if i == 0 else 0.0))
                hk.translate(V(0, 0, z - t))
                bd.translate(V(0, 0, z - t))
                formen[laenge] = hk, bd
            for x, laenge in lagen:
                hk, bd = formen[laenge]
                plus += [_setze(hk, x, m + r * a), _setze(bd, x, m + r * (a + R + bordabstand(pe) + wb / 2.0))]
    form = _dazu(Part.makeBox(W, H, t), plus, "Etagenkachel")
    minus += [_senkloch(p, xm, m), Part.makeCylinder(sch / 2.0, zo + 1.0 - t, V(xm, m, t))] + schlitze
    return _weg(form, minus, "Etagenkachel")


def _wanderndes_kabel(a, b, rho, x0, x1):
    """Raum, den ein Kabel (Radius rho, längs x) überstreicht, wenn es in der yz-Ebene von a nach b wandert."""
    uy, uz = b[0] - a[0], b[1] - a[1]
    L = math.hypot(uy, uz)
    vy, vz = -uz / L * rho, uy / L * rho
    pts = [(a[0] + vy, a[1] + vz), (b[0] + vy, b[1] + vz), (b[0] - vy, b[1] - vz), (a[0] - vy, a[1] - vz)]
    s = Part.Face(Part.makePolygon([V(x0, u, w) for u, w in pts] + [V(x0, pts[0][0], pts[0][1])])).extrude(
        V(x1 - x0, 0, 0))
    for q in (a, b):
        s = s.fuse(Part.makeCylinder(rho, x1 - x0, V(x0, q[0], q[1]), V(1, 0, 0)))
    return s


def einfuehrweg(p, y, z, aussen, laenge=30.0):
    """Weg beim Einklicken, rückwärts: Kabel, auf Fenstermaß gestaucht, vom Fenster senkrecht dazu `laenge` mm
    nach außen (aussen = -1: Bord auf -y, +1: Bord auf +y). Gibt (überstrichener Körper, Fenster, Neigung °)."""
    d, c = p["Kabeldurchmesser"], p["Spiel"]
    r, R = d / 2.0, d / 2.0 + c
    r1, h = lippen_rundung(p), bordhoehe(p)
    rr = min(bord_rundung(p), h - 0.2)
    c1 = (y + aussen * (p["Ueberdeckung"] * r - r1), z + 2 * r + c + r1)   # Rundung Lippenspitze
    c2 = (y + aussen * (R + bordabstand(p) + rr), z + h - rr)             # Rundung Bordkante innen
    dy, dz = c1[0] - c2[0], c1[1] - c2[1]
    L = math.hypot(dy, dz)
    w = L - r1 - rr
    m = (c2[0] + dy / L * (rr + w / 2), c2[1] + dz / L * (rr + w / 2))
    n = (-dz / L, dy / L)
    if n[0] * aussen < 0:
        n = (-n[0], -n[1])
    weg = _wanderndes_kabel(m, (m[0] + n[0] * laenge, m[1] + n[1] * laenge), w / 2 - 0.1, -15,
                            p["Laenge"] + 15)
    return weg, w, math.degrees(math.atan2(n[1], abs(n[0])))


def pruefe_etagen_kabel(form, p):
    """Je Etage: Kabel liegt frei, kann nicht senkrecht heraus, Einklickweg frei, Fenster. Liste von dicts."""
    W, m = p["Laenge"], p["Breite"] / 2.0
    bm, _ = baeume(p)
    zeilen = []
    for seite, (r, et) in bm.items():
        for i, (pe, a, z) in enumerate(et):
            y, rk = m + r * a, pe["Kabeldurchmesser"] / 2.0
            frei = form.common(Part.makeCylinder(rk - 0.01, W + 30, V(-15, y, z + rk), V(1, 0, 0))).Volume
            hoch = form.common(Part.makeCylinder(rk - 0.01, W + 30, V(-15, y, z + rk + p["Spiel"] + 0.5),
                                                 V(1, 0, 0))).Volume
            weg, w, neigung = einfuehrweg(pe, y, z, r)
            stoss = form.common(weg).Volume
            zeilen.append({"etage": "%s%d" % (seite, i + 1), "kabel": pe["Kabeldurchmesser"], "fenster": round(w, 2),
                           "kanal_frei": frei < 1e-3, "haelt": hoch > 1.0, "weg_frei": stoss < 1e-2,
                           "ok": frei < 1e-3 and hoch > 1.0 and stoss < 1e-2, "y": round(y, 2), "z": round(z, 2),
                           "neigung": round(neigung)})
    return zeilen


def bauhoehe(p, form):
    p = dict(STANDARD, **p)
    if form == "kachel":
        return p["Dicke"] + p["Kabeldurchmesser"] + p["Spiel"] + p["Lippe"]
    if form == "kreisverkehr":
        return poller_masse(p)[3]
    if form == "etagen":
        return baeume(p)[1]
    return p["Dicke"]


# ---------------------------------------------------------------- FreeCAD-Objekte (parametrisch)

def _wert(obj, name):
    v = getattr(obj, name)
    return float(v.Value) if hasattr(v, "Value") else v


class _Form:
    NAMEN = ()

    def __init__(self, obj):
        obj.Proxy = self
        self._eigenschaften(obj)

    def _eigenschaften(self, obj):
        for name, gruppe, typ, std, hilfe in PARAMETER:
            if name in self.NAMEN and name not in obj.PropertiesList:
                obj.addProperty("App::Property" + typ, name, gruppe, hilfe)
                setattr(obj, name, std)
        for name, hilfe in (("Bauhoehe", "Höchster Punkt über dem Tisch"),):
            if name not in obj.PropertiesList:
                obj.addProperty("App::PropertyLength", name, "Ergebnis", hilfe)
                obj.setEditorMode(name, 1)

    def onDocumentRestored(self, obj):
        self._eigenschaften(obj)

    def parameter(self, obj):
        return {n: _wert(obj, n) for n in self.NAMEN}

    def execute(self, obj):
        p = self.parameter(obj)
        form, art = self.baue(obj, p)
        pl = obj.Placement
        obj.Shape = form
        obj.Placement = pl
        bh = bauhoehe(p, art)
        if abs(_wert(obj, "Bauhoehe") - bh) > 1e-9:
            obj.Bauhoehe = bh

    def dumps(self):
        return None

    def loads(self, state):
        return None


class Kabelkachel(_Form):
    NAMEN = tuple(n for n, *_ in PARAMETER if n not in NUR_POLLER | NUR_ETAGE)

    def baue(self, obj, p):
        return baue_kachel(p), "kachel"


class Etagenkachel(_Form):
    NAMEN = tuple(n for n, *_ in PARAMETER if n not in NUR_POLLER | {"Kabeldurchmesser", "Spuren"})

    def baue(self, obj, p):
        return baue_etagenkachel(p), "etagen"


class Kreisverkehr(_Form):
    NAMEN = tuple(n for n, *_ in PARAMETER if n not in NUR_KACHEL | NUR_ETAGE | {"Spuren"})

    def _eigenschaften(self, obj):
        super()._eigenschaften(obj)
        if "Poller" not in obj.PropertiesList:
            obj.addProperty("App::PropertyBool", "Poller", "Poller", "Aus = Leerkachel (z. B. für Kreuzungen)")
            obj.Poller = True

    def baue(self, obj, p):
        return baue_kreisverkehr(p, obj.Poller), ("kreisverkehr" if obj.Poller else "leer")


def _neu(doc, klasse, name):
    obj = doc.addObject("Part::FeaturePython", name)
    klasse(obj)
    if App.GuiUp:
        obj.ViewObject.Proxy = 0
    return obj


def neues_set(doc=None, werte=None):
    """Tabelle "Parameter" + Kabelkachel, Kreisverkehr, Leerkachel und Etagenkachel, alle an die Tabelle gebunden.
    Wert in der Tabelle ändern -> alle Teile passen sich an. Einzelnes Teil abweichend: Ausdruck am Teil löschen."""
    doc = doc or App.ActiveDocument or App.newDocument("Kabelfuehrung")
    werte = dict(STANDARD, **(werte or {}))
    tab = doc.getObject("Parameter")
    if tab is None:
        tab = doc.addObject("Spreadsheet::Sheet", "Parameter")
        tab.set("A1", "'Parameter")
        tab.set("B1", "'Wert")
        tab.set("C1", "'Erklärung")
        for j, (name, _, typ, _, hilfe) in enumerate(PARAMETER, start=2):
            w = werte[name]
            tab.set("A%d" % j, "'" + name)
            tab.set("B%d" % j, ("%g mm" % w) if typ == "Length" else ("%d" % w if typ == "Integer" else "%g" % w))
            tab.setAlias("B%d" % j, name)
            tab.set("C%d" % j, "'" + hilfe)
        tab.setColumnWidth("A", 140)
        tab.setColumnWidth("C", 560)
    k = _neu(doc, Kabelkachel, "Kabelkachel")
    kv = _neu(doc, Kreisverkehr, "Kreisverkehr")
    lk = _neu(doc, Kreisverkehr, "Leerkachel")
    lk.Poller = False
    ek = _neu(doc, Etagenkachel, "Etagenkachel")
    for obj in (k, kv, lk, ek):
        for name in obj.Proxy.NAMEN:
            obj.setExpression(name, "%s.%s" % (tab.Name, name))
    kv.setExpression("Placement.Base.x", "%s.Laenge + 20 mm" % tab.Name)
    lk.setExpression("Placement.Base.x", "%s.Laenge + %s.Breite + 40 mm" % (tab.Name, tab.Name))
    ek.setExpression("Placement.Base.x", "%s.Laenge + 2 * %s.Breite + 60 mm" % (tab.Name, tab.Name))
    doc.recompute()
    return {"Parameter": tab, "Kabelkachel": k, "Kreisverkehr": kv, "Leerkachel": lk, "Etagenkachel": ek}
