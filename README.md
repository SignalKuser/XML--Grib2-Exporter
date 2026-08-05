# NLCurrent2GRIB V0.2.1

Windows-Konverter für niederländische XML-Strömungsvorhersagen.
Die Anwendung erzeugt regionale GRIB2-Dateien zur Darstellung der
Oberflächenströmung in QtVlm und OpenCPN.
.
.
.
<img width="845" height="548" alt="Screenshot 2026-07-28 212238" src="https://github.com/user-attachments/assets/204b4674-45e0-4aa1-9802-9e870739a4d6" />

## Funktionen

- grafische Oberfläche mit Drag-and-drop
- frei wählbarer Ausgabeordner
- strikte Verarbeitung der UTC-Zeitstempel
- automatische regionale Gruppierung
- getrennte GRIB2-Dateien je Region
- Umrechnung von Geschwindigkeit in Knoten und Richtung in U/V-Komponenten
- Missing-Value-Maske gegen großflächige Extrapolation
- Kommandozeilenbetrieb über `convert_cli.py`
# NLCurrent2GRIB V0.2.5

<img width="842" height="727" alt="Screenshot 2026-07-29 203906" src="https://github.com/user-attachments/assets/db66ad3a-6145-44eb-b135-0f9ac1978d2f" />

# NLCurrent2GRIB__multi_v.026


<img width="839" height="724" alt="Screenshot 2026-08-05 124524" src="https://github.com/user-attachments/assets/79b3de10-20ae-43c4-b0cc-d45f34c2523e" />

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
