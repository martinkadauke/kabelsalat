# Kabelführung v3 – Drucken

Alle Teile sind 72 × 72 mm groß (quadratisch), egal für welches Kabel. Jedes Teil passt an jedes, auch um 90°
gedreht. `kabelfuehrung.FCStd` im Hauptordner zeigt alles in FreeCAD.

## Dateien

| Nr | Teil | Kabel | Höhe | Kabel pro Teil | ca. g |
|----|------|-------|------|----------------|-------|
| 01 | Einfach (Kabelkachel) | 4 mm | 9,2 mm | 2 | 21 |
| 02 | Doppeldecker | 4 mm | 15,4 mm | 4 | 27 |
| 03 | Dreidecker | 4 mm | 21,6 mm | 6 | 35 |
| 04 | Einfach (Kabelkachel) | 6 mm | 11,2 mm | 2 | 22 |
| 05 | Doppeldecker | 6 mm | 19,4 mm | 4 | 30 |
| 06 | Dreidecker | 6 mm | 27,6 mm | 6 | 42 |
| 07 | Einfach (Kabelkachel) | 8 mm | 13,2 mm | 2 | 23 |
| 08 | Doppeldecker | 8 mm | 23,4 mm | 4 | 33 |
| 09 | Dreidecker | 8 mm | 33,6 mm | 6 | 50 |
| 10 | Einfach (Kabelkachel) | 10 mm | 15,2 mm | 2 | 24 |
| 11 | Doppeldecker | 10 mm | 27,4 mm | 4 | 37 |
| 12 | Dreidecker | 10 mm | 39,6 mm | 6 | 58 |
| 13 | Kreisverkehr (Poller Ø 32) | bis 10 mm | 15,2 mm | – | 31 |
| 14 | Leerkachel | – | 3 mm | – | 19 |

Alle Teile 72 × 72 mm ohne die überstehenden Klammern. Die Höhe zählt von der Tischplatte aus.
„Einfach“ ist die flache Kabelkachel mit zwei Spuren, die Haken kommen abwechselnd von beiden Seiten.
Doppel- und Dreidecker haben zwei Bäume mit je 2 bzw. 3 Kabeln übereinander, also 4 bzw. 6 Kabel pro Teil.
Die Gramm sind voll gerechnet. Gedruckt mit 15 % Füllung wiegen vor allem die Dreidecker deutlich weniger, weil
der Kiel innen nur zu 15 % gefüllt wird.

## Zuerst eine Probe: 03 + 12

1. **03 (Dreidecker 4 mm)** und **12 (Dreidecker 10 mm)** an der Stirnseite von vorn zusammendrücken.
2. Schraube in der Mitte durch den Schacht im Kiel drehen (3,5 × 12 Senkkopf). Der Schacht ist 8 mm weit,
   ein normaler Kreuzschlitz-Schraubendreher passt durch.
3. Kabel einklicken: **auf jeder Seite zuerst die Etage am Tisch, dann die nächste**. Jedes Kabel kommt von
   außen, fast waagrecht, und klickt unter die Lippe.
4. Prüfen: Klickt jedes Kabel ein und hält es? Sitzen die Klammern fest?

Danach anpassen, falls nötig (im Generator unter „Passung“ oder in der Tabelle `Parameter`):
- Kabel klickt zu schwer oder fällt raus: `Klemmung` 0,3 / 0,5 (Standard 0,4)
- Klammer zu stramm oder zu locker: `PuzzleSpiel` 0,15 / 0,25 (Standard 0,2)

Erfahrung aus dem ersten Probedruck: Ein 5,4-mm-Kabel klickt in der 6-mm-Kachel, obwohl das Fenster mit 5,6 mm
gezeichnet ist. Gedruckt ist es also etwas enger. Ist ein echtes 6-mm-Kabel zu stramm, das Teil mit 6,4 mm
erzeugen.

## Eigene Teile: Generator

1. **`Kabel-Generator.bat`** im Hauptordner doppelklicken (Windows, FreeCAD 1.1 muss installiert sein).
2. Teil wählen. Bei der Etagenkachel je Seite die Zahl der Etagen (0 bis 3) und je Etage den Kabeldurchmesser
   eintragen. Komma oder Punkt gehen beide.
3. **„STL erzeugen und in Bambu Studio öffnen“**. Das Rechnen dauert 5 bis 30 Sekunden.
4. Das Fenster zeigt für jede Etage das Klickfenster und ob alles passt (Kabel liegt frei, hält, Einklickweg frei).
   Unsinnige Werte meldet es im Klartext, zum Beispiel „Baum A zu breit“.

Die STL landet im Ordner `generiert`, der Name sagt, was drin ist (z. B. `Etagen_A4-6-4_B10-10-10.stl`, dieses
Beispiel liegt schon dort).

- **Seite A** ist die Seite mit den Taschen, **Seite B** die mit den Klammern. Etage 1 liegt am Tisch.
- Seite A hat etwas weniger Platz, weil am Rand die Taschen sitzen. 3 × 10 mm passt auf beiden Seiten.
  Für noch dickere Kabel: auf Seite B legen oder in die oberen Etagen.
- 0 Etagen auf einer Seite ergibt ein Teil mit nur einem Baum.

## Einstellungen (Bambu A1)

- Lage: so wie die STL kommt, Rückseite aufs Bett. **Keine Stützen.**
  Nur die Hakenlippen haben 3 bis 5 mm waagrechten Überhang, das geht ohne.
- 0,2 mm Schicht, 3 Wände, 15 % Füllung
- PLA reicht. PETG nehmen, wenn die Kacheln seitlich eingeschoben werden sollen.
- Elefantenfuß-Ausgleich an (0,15 mm), sonst klemmen die Klammern unten

## Montage

- Schrauben: **Senkkopf-Spanplattenschraube 3,5 × 12**, eine pro Teil, immer in der Mitte
  - Kabelkachel: zwischen den Mittelzungen
  - Etagenkachel: durch den Schacht im Kiel
  - Kreisverkehr: durch den Poller
- Tischplatte mindestens 15 mm dick
- Reihenfolge: erste Kachel festschrauben, nächste von vorn auf ihre Klammer drücken, dann schrauben.
  Erst schrauben, dann Kabel einklicken.
- Reihen stapeln geht mit allen Teilen, auch gemischt. Versetzt um eine halbe Kachel geht es **nicht**, weil die
  Widerhaken nach außen zeigen.
- Kreisverkehr: Der Poller reicht für Kabel bis 10 mm und sitzt auf Tischhöhe.
