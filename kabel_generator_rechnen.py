# -*- coding: utf-8 -*-
"""Rechenteil des Generators: läuft in freecadcmd, baut ein Teil aus kabelfuehrung.py und schreibt die STL.

Auftrag als JSON (Pfad in KF_AUFTRAG): {"ordner", "art", "werte", "datei", "ergebnis"}.
Ergebnis als JSON: {"ok", "datei", "masse", "gramm", "pruefung"} oder {"ok": false, "fehler"}.
"""
import json
import os
import sys
import traceback

auftrag = json.load(open(os.environ["KF_AUFTRAG"], encoding="utf-8"))
sys.path.insert(0, auftrag["ordner"])
erg = {"ok": False}
try:
    import MeshPart
    import kabelfuehrung as kf

    art, werte = auftrag["art"], auftrag["werte"]
    if art == "kachel":
        form = kf.baue_kachel(werte)
    elif art == "etagen":
        form = kf.baue_etagenkachel(werte)
    else:
        form = kf.baue_kreisverkehr(werte, art == "kreisverkehr")
    if not (form.isValid() and len(form.Solids) == 1):
        raise RuntimeError("Das Teil ist kein sauberer Körper geworden")
    pruefung = []
    if art == "etagen":
        for zeile in kf.pruefe_etagen_kabel(form, dict(kf.STANDARD, **werte)):
            pruefung.append(zeile)
    mesh = MeshPart.meshFromShape(Shape=form, LinearDeflection=0.01, AngularDeflection=0.1, Relative=False)
    mesh.write(auftrag["datei"])
    bb = form.BoundBox
    erg = {"ok": all(z["ok"] for z in pruefung), "datei": auftrag["datei"],
           "masse": [round(bb.XLength, 1), round(bb.YLength, 1), round(bb.ZLength, 1)],
           "gramm": round(form.Volume * 1.24e-3, 1), "pruefung": pruefung}
    if not erg["ok"]:
        erg["fehler"] = "Prüfung nicht bestanden (siehe Liste)"
except ValueError as e:                       # verständliche Meldung aus kabelfuehrung.pruefe
    erg["fehler"] = str(e)
except Exception as e:  # noqa: BLE001
    erg["fehler"] = "%s: %s" % (type(e).__name__, e)
    erg["details"] = traceback.format_exc()
with open(auftrag["ergebnis"], "w", encoding="utf-8") as fh:
    json.dump(erg, fh, ensure_ascii=False, indent=1)
