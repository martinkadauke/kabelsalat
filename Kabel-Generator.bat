@echo off
rem Kabelfuehrung-Generator: Fenster mit FreeCADs Python starten (FreeCAD 1.1 muss installiert sein).
set "FC=C:\Program Files\FreeCAD 1.1\bin\pythonw.exe"
if not exist "%FC%" (
  echo FreeCAD 1.1 nicht gefunden: %FC%
  pause
  exit /b 1
)
start "" "%FC%" "%~dp0kabel_generator.pyw"
