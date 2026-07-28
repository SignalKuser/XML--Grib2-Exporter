# NLCurrent2GRIB V0.2.1

Windows-Konverter für amtliche niederländische XML-Strömungsvorhersagen.
Die Anwendung erzeugt regionale GRIB2-Dateien zur Darstellung der
Oberflächenströmung in QtVlm und OpenCPN.

## Funktionen

- grafische Oberfläche mit Drag-and-drop
- frei wählbarer Ausgabeordner
- strikte Verarbeitung der UTC-Zeitstempel
- automatische regionale Gruppierung
- getrennte GRIB2-Dateien je Region
- Umrechnung von Geschwindigkeit in Knoten und Richtung in U/V-Komponenten
- Missing-Value-Maske gegen großflächige Extrapolation
- Kommandozeilenbetrieb über `convert_cli.py`

## Build unter Windows

Python muss installiert und über den in den Skripten angegebenen Befehl
erreichbar sein.

```powershell
.\Install-Dependencies.ps1
.\Build-Portable-EXE.ps1
```

Die portable Ausgabe wird unter `dist\NLCurrent2GRIB_v021` erzeugt.
Der Ordner `vendor` enthält nur lokal installierte Build-Abhängigkeiten und
wird nicht auf GitHub hochgeladen.

Nach dem Build erzeugt `Prepare-GitHub-Upload.ps1` einen neuen, sauberen
Uploadordner ohne Laufzeitbibliotheken, EXE, Buildreste und Testausgaben:

```powershell
.\Prepare-GitHub-Upload.ps1
```

## Lizenz

Der eigene Quellcode steht unter der GNU General Public License Version 3.
Die verwendeten Drittanbieterkomponenten behalten ihre jeweiligen Lizenzen.
Siehe `THIRD_PARTY_NOTICES.txt` und den Ordner `licenses`.

## Hinweis

Experimenteller Entwicklungsstand. Nicht als alleinige Grundlage für die
Navigation verwenden.
