# kabelsalat

Parametric, 3D-printable cable management tiles for the underside of a desk, modelled in FreeCAD (Python).
The tiles snap together like a puzzle, each one is held by a single screw, and the cables click into hooks and
can be pulled out again. Every part has the same 72 × 72 mm footprint, so any tile connects to any other,
also rotated by 90°.

![Example layout with a roundabout, a crossing and a row of triple deckers](bilder/aufbau_iso.png)

## Parts

| Part | What it does |
|------|--------------|
| **Kabelkachel** (flat tile) | Two cable lanes. Short hooks at the ends, a long hook from the other side in the middle, so the cable is held from both sides. |
| **Etagenkachel** (double/triple decker) | Two "trees" with up to three cables stacked on each side. Every level has its own cable diameter. Like on the flat tile, the hooks alternate: at both ends they come from solid keel blocks in the middle, the middle hook comes from an outer wall. |
| **Kreisverkehr** (roundabout) | A post with a rim to lead cables around corners and into branches. |
| **Leerkachel** (blank tile) | Plain plate for crossings and gaps. |

The screw always sits in the middle of the tile. On the decker it sits in the open gap between the two trees.

![Decker cut through an end hook (left) and through the middle hook (right), as mounted with the desk on top: 4/6/4 mm and 10/10/10 mm](bilder/etagen_vergleich_montiert.png)

## Printing

Ready-made STLs for 4, 6, 8 and 10 mm cables (flat, double and triple decker), plus roundabout and blank tile,
are in [`druck/v4`](druck/v4). The print guide with the full parts list, a test print, how to lay the cables in
and mounting notes is in German: [`druck/v4/DRUCKEN.md`](druck/v4/DRUCKEN.md).

Short version:
- print as the STL comes, plate on the bed, **no supports**
- 0.2 mm layers, 3 walls, 15 % infill, PLA
- elephant-foot compensation 0.15 mm, otherwise the clips jam
- one 3.5 × 12 mm countersunk wood screw per tile, desk at least 15 mm thick

## Your own sizes

**Generator (Windows):** double-click `Kabel-Generator.bat`. It needs FreeCAD 1.1, nothing else. Choose the
part and the cable diameters, for a decker per side and per level. The window builds the part with the same
model, checks every level, writes the STL to `generiert/` and opens it in Bambu Studio.

**FreeCAD:** copy `kabelfuehrung.py` and `Kabelfuehrung.FCMacro` into the FreeCAD macro folder, open
`kabelfuehrung.FCStd` and change the values in the spreadsheet `Parameter`. All parts recompute. The most
useful ones:

| Parameter | Meaning |
|-----------|---------|
| `Kabeldurchmesser`, `Spuren` | cable diameter and lanes (1 or 2) of the flat tile; poller size of the roundabout |
| `A_Etagen`, `A_Kabel1..3` | decker, side A (the side with the pockets): number of levels 0–3, diameter per level from the desk outwards |
| `B_Etagen`, `B_Kabel1..3` | the same for side B (the side with the clips) |
| `Klemmung` | the click window is this much narrower than the cable (0.4 mm) |
| `PuzzleSpiel` | clearance of the snap clips per side (0.2 mm) |
| `Breite` | 72 mm. Changing it breaks compatibility with all other tiles. |

## How it works

- **Click fit (flat tile):** between the hook lip and a low rail opposite it there is a window 0.4 mm narrower than the
  cable. The cable is pushed through it and stays in.
- **No supports:** the lip has a 45° wedge under it and only 3 to 5 mm of horizontal overhang.
- **Holding the cable:** what really keeps a cable in is that the hooks alternate. The end hooks wrap around it
  from one side and the middle hook from the other, so it cannot leave in any direction without bending.
  A version of the decker with all hooks on one side was printed and did not hold.
- **Decker:** the cables of a tree lie straight above each other, each level rests on the lips of the level
  below. A cable is slid in from outside at the end hooks and from the middle gap at the middle hook. For that
  it has to bend inwards briefly, about 0.8 × its diameter (8 mm for a 10 mm cable). The decker has no click
  rail, the cable is held by the alternating hooks alone.
- **Snap clips:** a springy prong with a barb and a slit on +X and +Y, matching pockets on −X and −Y. Tiles
  are pressed together from the front (towards the desk).

`build.py` (run with `freecadcmd`) builds every part of the print set and checks it: the part is one valid
solid, the cable lies free in its channel and cannot be lifted straight out, the click window of the flat tile
has the target size, every decker cable is captured on both sides and can be laid in at the end and middle
hooks, and all connector pairings have 0.2 mm clearance and lock.
The results are in [`pruefbericht.txt`](pruefbericht.txt). `ansicht.sh` takes the screenshots in `bilder/` and
saves the FCStd.

## Status

- The first version of the flat tile and the roundabout (6 mm) has been printed: clips and click fit work.
- A v3 triple decker was printed. Its one-sided hooks did not hold the cable.
- The v4 decker with alternating hooks has not been test-printed yet. The open question is whether a stiff
  10 mm cable makes the bend at the middle hook.

The design started from photos of modular snap-together cable guides and was then modelled from scratch and
extended (deckers, generator). Built with [Claude Code](https://claude.com/claude-code).

## License

- Code (`*.py`, `*.pyw`, `*.bat`, `*.sh`, `*.FCMacro`): [MIT](LICENSE)
- Models (`*.FCStd`, `*.stl`): [CERN-OHL-P-2.0](LICENSES/CERN-OHL-P-2.0.txt)
- Documentation and images: [CC BY 4.0](LICENSES/CC-BY-4.0.txt)
