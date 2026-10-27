#!/usr/bin/env bash
# Echte FreeCAD-Screenshots + FCStd in EIGENER GUI-Instanz (eigenes Profil, keine Addons, das normale FreeCAD-Profil
# bleibt unberührt). Läuft in Git Bash unter Windows.
set -e
HIER="$(cd "$(dirname "$0")" && pwd -W)"
FREECAD="${FREECAD:-/c/Program Files/FreeCAD 1.1/bin/freecad.exe}"
PROFIL="$HIER/.fc_profil"
mkdir -p "$PROFIL/home" "$PROFIL/data" "$PROFIL/temp"
export FREECAD_USER_HOME="$PROFIL/home" FREECAD_USER_DATA="$PROFIL/data" FREECAD_USER_TEMP="$PROFIL/temp"
rm -f "$HIER/bilder/log.txt"
timeout 600 "$FREECAD" "$HIER/ansicht.py" >/dev/null 2>&1 || true
cat "$HIER/bilder/log.txt"
