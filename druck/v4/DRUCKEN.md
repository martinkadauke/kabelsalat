# Kabelführung v4 – Drucken

Neu in v4: die **Etagenkachel hält die Kabel wieder wie die flache Kabelkachel**. Die Haken kommen abwechselnd
von beiden Seiten. An den beiden Enden kommt der Haken vom Kiel in der Mitte und geht außen um das Kabel herum,
am Mittelhaken kommt er von einer Außenwand und geht innen herum. So kann das Kabel nach keiner Seite heraus,
ohne sich zu biegen.

Die Kabel eines Baums liegen jetzt genau übereinander. Die Schraube sitzt frei im Gang in der Mitte, einen
Schacht braucht es nicht mehr. Die Teile sind dadurch leichter als in v3.

Alle Teile sind 72 × 72 mm groß, egal für welches Kabel. Jedes Teil passt an jedes, auch um 90° gedreht.
v3-Teile passen weiterhin an v4-Teile, nur die Etagenkachel ist neu.

## Dateien

| Nr | Teil | Kabel | Höhe | Kabel pro Teil | ca. g |
|----|------|-------|------|----------------|-------|
| 01 | Einfach (Kabelkachel) | 4 mm | 9,2 mm | 2 | 21 |
| 02 | Doppeldecker | 4 mm | 15,4 mm | 4 | 23 |
| 03 | Dreidecker | 4 mm | 21,6 mm | 6 | 25 |
| 04 | Einfach (Kabelkachel) | 6 mm | 11,2 mm | 2 | 22 |
| 05 | Doppeldecker | 6 mm | 19,4 mm | 4 | 24 |
| 06 | Dreidecker | 6 mm | 27,6 mm | 6 | 27 |
| 07 | Einfach (Kabelkachel) | 8 mm | 13,2 mm | 2 | 23 |
| 08 | Doppeldecker | 8 mm | 23,4 mm | 4 | 26 |
| 09 | Dreidecker | 8 mm | 33,6 mm | 6 | 30 |
| 10 | Einfach (Kabelkachel) | 10 mm | 15,2 mm | 2 | 24 |
| 11 | Doppeldecker | 10 mm | 27,4 mm | 4 | 28 |
| 12 | Dreidecker | 10 mm | 39,6 mm | 6 | 33 |
| 13 | Kreisverkehr (Poller Ø 32) | bis 10 mm | 15,2 mm | – | 31 |
| 14 | Leerkachel | – | 3 mm | – | 19 |

Alle Teile 72 × 72 mm ohne die überstehenden Klammern. Die Höhe zählt von der Tischplatte aus.
„Einfach“ ist die flache Kabelkachel mit zwei Spuren. Doppel- und Dreidecker haben zwei Bäume mit je 2 bzw. 3
Kabeln übereinander. Die Gramm sind voll gerechnet, gedruckt mit 15 % Füllung wird es etwas weniger.

## Zuerst eine Probe: 06 + 12

1. **06 (Dreidecker 6 mm)** und **12 (Dreidecker 10 mm)** an der Stirnseite von vorn zusammendrücken.
2. Schraube in der Mitte festdrehen. Sie liegt frei im Gang zwischen den Bäumen.
3. Kabel einlegen, **auf jeder Seite zuerst die Etage am Tisch**:
   - An den **beiden Enden** das Kabel von außen unter seine Lippe schieben.
   - In der **Mitte** das Kabel ein Stück nach innen in den Gang biegen, an den Lippen der unteren Etagen
     vorbei hochführen und dann nach außen unter seine Lippe ziehen. Bei 10-mm-Kabeln muss es dafür etwa 8 mm
     zur Seite, bei 6 mm etwa 5 mm, bei 4 mm etwa 3 mm.
4. Prüfen: Liegt jedes Kabel fest, auch wenn man seitlich daran zieht? Lässt sich das 10-mm-Kabel in der Mitte
   einlegen, oder ist es zu steif?

Die Etagenkachel klickt nicht, sie hat keinen Bord. Das Kabel ist durch die abwechselnden Haken gefangen.
Die flache Kabelkachel klickt weiter wie bisher.

Danach anpassen, falls nötig (im Generator unter „Passung“ oder in der Tabelle `Parameter`):
- Flache Kachel, Kabel klickt zu schwer oder fällt raus: `Klemmung` 0,3 / 0,5 (Standard 0,4)
- Klammer zu stramm oder zu locker: `PuzzleSpiel` 0,15 / 0,25 (Standard 0,2)
- Kabel liegt zu locker in der Etagenkachel: `Spiel` kleiner (Standard 0,4)

## Eigene Teile: Generator

1. **`Kabel-Generator.bat`** im Hauptordner doppelklicken (Windows, FreeCAD 1.1 muss installiert sein).
2. Teil wählen. Bei der Etagenkachel je Seite die Zahl der Etagen (0 bis 3) und je Etage den Kabeldurchmesser
   eintragen. Komma oder Punkt gehen beide.
3. **„STL erzeugen und in Bambu Studio öffnen“**. Das Rechnen dauert 5 bis 30 Sekunden.
4. Das Fenster zeigt je Etage, ob das Kabel gefangen ist und sich einlegen lässt, und wie weit es dafür in der
   Mitte zur Seite muss. Unsinnige Werte meldet es im Klartext, zum Beispiel „Baum A zu breit“.

Die STL landet im Ordner `generiert`, der Name sagt, was drin ist (z. B. `Etagen_A4-6-4_B10-10-10.stl`).

- **Seite A** ist die Seite mit den Taschen, **Seite B** die mit den Klammern. Etage 1 liegt am Tisch.
- 0 Etagen auf einer Seite ergibt ein Teil mit nur einem Baum.
- Platz ist jetzt genug: auch 3 × 12 mm passt auf beiden Seiten.

## Einstellungen (Bambu A1)

- Lage: so wie die STL kommt, Rückseite aufs Bett. **Keine Stützen.**
  Nur die Hakenlippen haben 3 bis 5 mm waagrechten Überhang, das geht ohne.
- 0,2 mm Schicht, 3 Wände, 15 % Füllung
- PLA reicht. PETG nehmen, wenn die Kacheln seitlich eingeschoben werden sollen.
- Elefantenfuß-Ausgleich an (0,15 mm), sonst klemmen die Klammern unten

## Montage

- Schrauben: **Senkkopf-Spanplattenschraube 3,5 × 12**, eine pro Teil, immer in der Mitte
  - Kabelkachel: zwischen den Mittelzungen
  - Etagenkachel: frei im Gang zwischen den Bäumen
  - Kreisverkehr: durch den Poller
- Tischplatte mindestens 15 mm dick
- Reihenfolge: erste Kachel festschrauben, nächste von vorn auf ihre Klammer drücken, dann schrauben.
  Erst schrauben, dann Kabel einlegen.
- Reihen stapeln geht mit allen Teilen, auch gemischt. Versetzt um eine halbe Kachel geht es **nicht**, weil die
  Widerhaken nach außen zeigen.
- Kreisverkehr: Der Poller reicht für Kabel bis 10 mm und sitzt auf Tischhöhe.
