# -*- coding: utf-8 -*-
"""Headless: baut die Druckteile, prüft sie und schreibt STLs + Prüfbericht, kopiert Modul + Makro in FreeCADs
Makro-Ordner (sonst lassen sich die parametrischen Objekte der FCStd in FreeCAD nicht neu berechnen).

    "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" build.py
"""
import json
import math
import os
import shutil
import sys

# Ordner dieses Skripts (freecadcmd setzt kein __file__, darum über die Kommandozeile)
HERE = os.path.dirname(os.path.abspath(next((a for a in sys.argv if os.path.basename(a) == "build.py"), "build.py")))
sys.path.insert(0, HERE)

import FreeCAD as App  # noqa: E402
import MeshPart  # noqa: E402
import Part  # noqa: E402

import kabelfuehrung as kf  # noqa: E402

V = App.Vector
STAND = "v3"
DRUCK = os.path.join(HERE, "druck", STAND)
MAKRO = App.getUserMacroDir(True)


def baeume(a, b):
    """Werte für eine Etagenkachel: a, b = Kabeldurchmesser je Etage (vom Tisch aus) auf Seite A und B."""
    w = {"A_Etagen": len(a), "B_Etagen": len(b)}
    for seite, liste in (("A", a), ("B", b)):
        for i, d in enumerate(liste):
            w["%s_Kabel%d" % (seite, i + 1)] = float(d)
    return w


# Druckset: je Kabelgröße einfach (Kabelkachel, 2 Spuren), Doppel- und Dreidecker (2 Bäume); dann Kreisverkehr
DRUCKSET = []
for _d in (4.0, 6.0, 8.0, 10.0):
    DRUCKSET += [("kachel", {"Kabeldurchmesser": _d}), ("etagen", baeume([_d] * 2, [_d] * 2)),
                 ("etagen", baeume([_d] * 3, [_d] * 3))]
DRUCKSET += [("kreisverkehr", {"Kabeldurchmesser": 10.0}), ("leer", {"Kabeldurchmesser": 10.0})]
# nur prüfen (gemischte Bäume, einseitige Bäume, Grenzfälle)
NUR_PRUEFEN = [
    ("etagen", baeume([4, 6, 4], [10, 10, 10])), ("etagen", baeume([4, 10], [10])),
    ("etagen", baeume([], [8, 8])), ("etagen", baeume([10], [])),
]
bericht = []


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    bericht.append(s)


def stl(form, pfad):
    m = MeshPart.meshFromShape(Shape=form, LinearDeflection=0.01, AngularDeflection=0.1, Relative=False)
    m.write(pfad)
    return m


def ueberhaenge(mesh, grenze=-0.72):
    """Fläche der Facetten, die steiler als ~46° nach unten zeigen (ohne Druckbett), nach Höhe gruppiert."""
    z = {}
    for f in mesh.Facets:
        n = f.Normal
        if n.z < grenze:
            hz = sum(p[2] for p in f.Points) / 3
            if hz > 0.05:
                k = round(hz, 1)
                z[k] = z.get(k, 0.0) + f.Area
    return z


def bewegt(form, dx=0.0, dy=0.0, winkel=0.0):
    s = form.copy()
    if winkel:
        s.rotate(V(0, 0, 0), V(0, 0, 1), winkel)
    s.translate(V(dx, dy, 0))
    return s


def ueberlapp(a, b):
    return a.common(b).Volume


def baue(art, w):
    if art == "kachel":
        return kf.baue_kachel(w)
    if art == "etagen":
        return kf.baue_etagenkachel(w)
    return kf.baue_kreisverkehr(w, art == "kreisverkehr")


def name_von(art, w):
    p = dict(kf.STANDARD, **w)
    if art == "kachel":
        return "Kabelkachel_%gmm_%dspur" % (p["Kabeldurchmesser"], p["Spuren"])
    if art == "etagen":
        return etagen_name(p)
    if art == "kreisverkehr":
        return "Kreisverkehr_bis%gmm" % p["Kabeldurchmesser"]
    return "Leerkachel"


def etagen_name(p):
    """Doppeldecker_6mm, Dreidecker_A4-6-4_B10-10-10mm ..."""
    n = [int(p["A_Etagen"]), int(p["B_Etagen"])]
    seiten = ["-".join("%g" % p["%s_Kabel%d" % (s, i + 1)] for i in range(k)) for s, k in zip("AB", n)]
    art = {1: "Einfach", 2: "Doppeldecker", 3: "Dreidecker"}[max(n)]
    if n[0] == n[1] and seiten[0] == seiten[1] and len(set(seiten[0].split("-"))) == 1:
        return "%s_%smm" % (art, seiten[0].split("-")[0])
    return "%s_A%s_B%smm" % (art, seiten[0] or "0", seiten[1] or "0")


def grunddaten(name, f):
    bb = f.optimalBoundingBox()
    ok = f.isValid() and len(f.Solids) == 1
    log("  %-28s gueltig=%s  V=%.0f mm3  (~%.1f g PLA)  %.1f x %.1f x %.1f mm" %
        (name, ok, f.Volume, f.Volume * 1.24e-3, bb.XLength, bb.YLength, bb.ZLength))
    assert ok, name


def kanal(f, p, y, z, W, txt):
    """Kabel liegt frei im Kanal und kann nicht senkrecht heraus."""
    r = p["Kabeldurchmesser"] / 2.0
    frei = ueberlapp(f, Part.makeCylinder(r - 0.01, W + 30, V(-15, y, z + r), V(1, 0, 0)))
    hoch = ueberlapp(f, Part.makeCylinder(r - 0.01, W + 30, V(-15, y, z + r + p["Spiel"] + 0.5), V(1, 0, 0)))
    log("  %s: Kabel %g mm frei=%s (%.3f mm3), senkrecht raus blockiert=%s (%.1f mm3)" %
        (txt, p["Kabeldurchmesser"], frei < 1e-3, frei, hoch > 1.0, hoch))
    assert frei < 1e-3 and hoch > 1.0


def fenster_messen(p, oben=True):
    """Fenster am echten Haken/Bord nachmessen (lokal, Spurmitte 0, Boden = Platte)."""
    R = p["Kabeldurchmesser"] / 2.0 + p["Spiel"]
    hk = kf.haken(p, p["Hakenbreite"], oben=oben)
    bd = kf.bord(p, p["Hakenbreite"])
    bd.translate(V(0, -(R + kf.bordabstand(p) + p["Bordbreite"] / 2), 0))
    fe = hk.distToShape(bd)[0]
    ziel = p["Kabeldurchmesser"] - p["Klemmung"]
    log("  Fenster gemessen %.2f mm (Ziel %.2f) -> Kabel muss %.2f mm nachgeben" %
        (fe, ziel, p["Kabeldurchmesser"] - fe))
    assert abs(fe - ziel) < 0.05


def prisma(a, b, rho, x0, x1):
    """Raum, den ein Kabel (Radius rho, längs x) überstreicht, wenn es in der yz-Ebene von a nach b wandert."""
    uy, uz = b[0] - a[0], b[1] - a[1]
    L = math.hypot(uy, uz)
    vy, vz = -uz / L * rho, uy / L * rho
    pts = [(a[0] + vy, a[1] + vz), (b[0] + vy, b[1] + vz), (b[0] - vy, b[1] - vz), (a[0] - vy, a[1] - vz)]
    f = Part.Face(Part.makePolygon([V(x0, u, w) for u, w in pts] + [V(x0, pts[0][0], pts[0][1])]))
    s = f.extrude(V(x1 - x0, 0, 0))
    for q in (a, b):
        s = s.fuse(Part.makeCylinder(rho, x1 - x0, V(x0, q[0], q[1]), V(1, 0, 0)))
    return s


def einfuehrweg(f, p, y, z, W, txt, aussen=-1, laenge=30.0):
    """Kabel, auf Fenstermaß gestaucht, vom Fenster senkrecht dazu 30 mm nach außen schieben: nichts darf im
    Weg sein (vor allem nicht die Etagen darüber). aussen: Richtung der Bordseite (-1 = -y, +1 = +y)."""
    d, c = p["Kabeldurchmesser"], p["Spiel"]
    r, R = d / 2.0, d / 2.0 + c
    r1, h = kf.lippen_rundung(p), kf.bordhoehe(p)
    rr = min(kf.bord_rundung(p), h - 0.2)
    c1 = (y + aussen * (p["Ueberdeckung"] * r - r1), z + 2 * r + c + r1)    # Rundung Lippenspitze
    c2 = (y + aussen * (R + kf.bordabstand(p) + rr), z + h - rr)           # Rundung Bordkante innen
    dy, dz = c1[0] - c2[0], c1[1] - c2[1]
    L = math.hypot(dy, dz)
    w = L - r1 - rr
    m = (c2[0] + dy / L * (rr + w / 2), c2[1] + dz / L * (rr + w / 2))
    n = (-dz / L, dy / L)
    if n[0] * aussen < 0:                                                  # nach außen: Bordseite, vom Tisch weg
        n = (-n[0], -n[1])
    ziel = (m[0] + n[0] * laenge, m[1] + n[1] * laenge)
    ue = ueberlapp(f, prisma(m, ziel, w / 2 - 0.1, -15, W + 15))
    log("  %s: Einfuehrweg frei=%s (%.3f mm3), %.0f Grad gegen die Platte geneigt" %
        (txt, ue < 1e-2, ue, math.degrees(math.atan2(n[1], abs(n[0])))))
    assert ue < 1e-2


def verbinder(faelle):
    for name, a, b, klammer, b_weg in faelle:
        ue = ueberlapp(a, b)
        luft = klammer.distToShape(b)[0]
        rast = ueberlapp(a, b_weg)
        log("  %-40s Ueberschneidung %.3f mm3, Luft Klammer %.2f mm, rastet (0,5 mm auseinander -> %.1f mm3)" %
            (name, ue, luft, rast))
        assert ue < 1e-3 and rast > 0.05, name


def paare(a, b, p, na, nb):
    """a links/unten, b rechts/oben: an der Stirnseite (x) und gestapelt (y)."""
    W, H = p["Laenge"], p["Breite"]
    kl = kf.klammer(p)
    return [("%s | %s (x)" % (na, nb), a, bewegt(b, W, 0), bewegt(kl, W, H / 2), bewegt(b, W + 0.5, 0)),
            ("%s / %s (y)" % (na, nb), a, bewegt(b, 0, H), bewegt(kl, 3 * W / 4, H, 90), bewegt(b, 0, H + 0.5))]


def pruefe_kachel(w, kv, lk):
    p = dict(kf.STANDARD, **w)
    r, R, ys, H, G, Go = kf.masse(p)
    W = p["Laenge"]
    k = kf.baue_kachel(w)
    grunddaten("Kabelkachel", k)
    log("  Kachel %.1f x %.1f mm (ohne Klammern), Bauhoehe %.1f, Bord %.2f mm, Rand %.1f mm" %
        (W, H, kf.bauhoehe(p, "kachel"), kf.bordhoehe(p), ys[0] - R - Go))
    for i, y in enumerate(ys):
        kanal(k, p, y, p["Dicke"], W, "Spur %d" % (i + 1))
    fenster_messen(p)
    kl = kf.klammer(p)
    faelle = paare(k, k, p, "Kachel", "Kachel") + [
        ("Kachel | Kreisverkehr", k, bewegt(kv, W, 0), bewegt(kl, W, H / 2), bewegt(kv, W + 0.5, 0)),
        ("Kreisverkehr | Kachel", kv, bewegt(k, H, 0), bewegt(kl, H, H / 2), bewegt(k, H + 0.5, 0)),
        ("Kreisverkehr / Kachel 90 Grad oben", kv, bewegt(k, H, H, 90), bewegt(kl, H / 2, H, 90),
         bewegt(k, H, H + 0.5, 90)),
        ("Kachel 90 Grad unten / Kreisverkehr", bewegt(k, H, -W, 90), kv, bewegt(kl, H / 2, 0, 90),
         bewegt(kv, 0, 0.5)),
    ]
    verbinder(faelle)
    return k


def pruefe_etagen(w, k6, kv):
    p = dict(kf.STANDARD, **w)
    W, H = p["Laenge"], p["Breite"]
    e = kf.baue_etagenkachel(w)
    grunddaten("Etagenkachel", e)
    bm, zo = kf.baeume(p)
    log("  Kachel %.1f x %.1f mm, Bauhoehe %.1f, Schraube mittig" % (W, H, zo))
    for seite, (r, et) in bm.items():
        if et:
            log("  Baum %s: %.1f mm von der Mitte bis zum aeusseren Bord" % (seite, kf.baum_aussen(p, et[0])))
        for i, (pe, a, z) in enumerate(et):
            y = H / 2.0 + r * a
            log("  %s%d: Kabel %g mm, Spurmitte y=%.1f, Boden z=%.1f, Bord %.2f mm" %
                (seite, i + 1, pe["Kabeldurchmesser"], y, z, kf.bordhoehe(pe)))
            kanal(e, pe, y, z, W, "  %s%d" % (seite, i + 1))
            fenster_messen(pe, i == len(et) - 1)
            einfuehrweg(e, pe, y, z, W, "  %s%d" % (seite, i + 1), r)
    kl = kf.klammer(p)
    faelle = paare(e, k6, p, "Etagen", "Kachel6") + paare(k6, e, p, "Kachel6", "Etagen") + [
        ("Etagen | Kreisverkehr", e, bewegt(kv, W, 0), bewegt(kl, W, H / 2), bewegt(kv, W + 0.5, 0)),
        ("Kreisverkehr | Etagen", kv, bewegt(e, H, 0), bewegt(kl, H, H / 2), bewegt(e, H + 0.5, 0)),
    ]
    verbinder(faelle)
    return e


def installiere():
    os.makedirs(MAKRO, exist_ok=True)
    shutil.copy2(os.path.join(HERE, "kabelfuehrung.py"), os.path.join(MAKRO, "kabelfuehrung.py"))
    shutil.copy2(os.path.join(HERE, "Kabelfuehrung.FCMacro"), os.path.join(MAKRO, "Kabelfuehrung.FCMacro"))
    log("Modul + Makro -> FreeCAD-Makro-Ordner")


def main():
    os.makedirs(DRUCK, exist_ok=True)
    w10 = {"Kabeldurchmesser": 10.0}
    log("== Kreisverkehr + Leerkachel (Poller fuer Kabel bis 10 mm) ==")
    kv, lk = kf.baue_kreisverkehr(w10, True), kf.baue_kreisverkehr(w10, False)
    grunddaten("Kreisverkehr", kv)
    grunddaten("Leerkachel", lk)
    p10 = dict(kf.STANDARD, **w10)
    dp, ue, _, zt = kf.poller_masse(p10)
    log("  Poller %.1f mm, Rand %.1f mm, Hoehe %.1f mm" % (dp, ue, zt))
    verbinder([("Leerkachel / Kreisverkehr", lk, bewegt(kv, 0, p10["Breite"]),
                bewegt(kf.klammer(p10), p10["Breite"] / 2, p10["Breite"], 90), bewegt(kv, 0, p10["Breite"] + 0.5))])
    formen = {}
    k6 = kf.baue_kachel({"Kabeldurchmesser": 6.0})
    for art, w in DRUCKSET + NUR_PRUEFEN:
        if art not in ("kachel", "etagen"):
            continue
        log("== %s ==" % name_von(art, w))
        if art == "kachel":
            formen[name_von(art, w)] = pruefe_kachel(w, kv, lk)
        else:
            formen[name_von(art, w)] = pruefe_etagen(w, k6, kv)
    log("== gemischte Groessen ==")
    p = kf.STANDARD
    verbinder(paare(formen["Kabelkachel_4mm_2spur"], formen["Kabelkachel_10mm_2spur"], p, "Kachel4", "Kachel10")
              + paare(formen["Dreidecker_4mm"], formen["Dreidecker_10mm"], p, "Dreidecker4", "Dreidecker10")
              + paare(formen["Doppeldecker_6mm"], formen["Kabelkachel_8mm_2spur"], p, "Doppeldecker6", "Kachel8")
              + paare(formen["Dreidecker_A4-6-4_B10-10-10mm"], formen["Dreidecker_10mm"], p, "Dreidecker464|10",
                      "Dreidecker10"))
    formen["Kreisverkehr_bis10mm"], formen["Leerkachel"] = kv, lk

    log("== STL ==")
    manifest = []
    for nr, (art, w) in enumerate(DRUCKSET, start=1):
        name = name_von(art, w)
        datei = "%02d_%s_print.stl" % (nr, name)
        m = stl(formen[name], os.path.join(DRUCK, datei))
        ue = {z: a for z, a in ueberhaenge(m).items() if a > 0.5}
        log("  %s: %d Facetten, %.0f g, Ueberhang >46 Grad: %s" %
            (datei, m.CountFacets, formen[name].Volume * 1.24e-3,
             ", ".join("z=%.1f: %.0f mm2" % kv_ for kv_ in sorted(ue.items())) or "keiner"))
        manifest.append({"datei": datei, "form": art, "werte": w})
    with open(os.path.join(DRUCK, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=1, ensure_ascii=False)
    installiere()
    with open(os.path.join(HERE, "pruefbericht.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(bericht) + "\n")
    log("FERTIG")


if any(os.path.basename(a) == "build.py" for a in sys.argv):
    main()
