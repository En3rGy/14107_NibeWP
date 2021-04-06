# 14107 NibeWP

## Beschreibung 

Der Baustein dient zur Kommunikation mit einer Nibe Wärmepumpe. Der Baustein nutzt hierbei das [NibeUPD Gateway](https://github.com/fablable/NibeGW-ProdinoMKR)

### Vorbereitung

1. NIBE UDP Gateway läuft, s. z.B. das [NIBE UDP Gateway auf Prodino MKR](https://github.com/fablable/NibeGW-ProdinoMKR)
2. Mit NIBE Modbus Manager:
    - In NIBE Modbus Manager Modell der Wärmepumpe auswählen
    - Mit File - Export, Datei *export.csv* generieren
3. *export.csv* mittels *hsupload* auf den HS laden:
    - *hsupload* ist normalerweise unter folgendem Pfad zu finden:
        "c:\users\user_name\Documents\Gira\HS+FS Experte 4.11\Projekte\project_name\project_name\hsupload"
    - In *hsupload* die Unterverzeichnisse *\_logic\14107* anlegen
    - *export.csv* in das neue Unterverzeichnis kopieren. Der Komplette Pfad zur Datei könnte dann so aussehen:
        *c:\users\user_name\Documents\Gira\HS+FS Experte 4.11\Projekte\project_name\project_name\hsupload\_logic\14107\export.csv*
	- In Experte, ggf. Haken unter Projekt - Oberfläche für den Ordner setzen.
	- Projekt übertragen.

## Eingänge

| Nr. | Name | Initialisierung | Beschreibung |
| --- | --- | --- | --- |
| 1 | Nibe UDP GW IP | | IP des UDP-Gateways |
| 2 | Nibe UDP GW get Port | 9999 | Port des UDP-Gateways |
| 3 | Nibe UDP GW set Port | 1000 |  |
| 4 | HS-Port | 9999 |  |
| 5 | Set (json) | | Register mit einem bestimmten wert schreiben: *Register:Wert*, z.B. *48043:1* |
| 6 | Get Register | | Nummer des abzufragenden Registers |

## Ausgänge

| Nr. | Name | Initialisierung | Beschreibung |
| --- | --- | --- | --- |
| 1 | Werte (json) | | Json Objekt der Form *{'48043': {'value': 0.0, 'Title': 'Holiday - Activated'}, ...*. Die weite Auswertung kann dann z.B. mit dem Baustein 11087 erfolgen. |
| 2 | Modell | | Nibe Modell / Produkt |
| 3 | SW Version | 0 | SW-Version des Nibe Geräts |


## Beispielwerte

| Eingang | Ausgang |
| --- | --- |
| - | - |


## Sonstiges

- Neuberechnug beim Start: Nein
- Baustein ist remanent: nein
- Interne Bezeichnung: 14107
- Kategorie: Datenaustausch

### Change Log

- v1.2
	- Impr.: Improved logging
	- Impr.: Update to hsl 20.4
- v1.1
    - Fix: 1st value received not provided at output
- v1.0
    - Initial

### Open Issues / Know Bugs

Bekannte Fehler werden auf [github](https://github.com/En3rGy/14107_NibeWP) verfolgt.

### Support

Please use [github issue feature](https://github.com/En3rGy/14107_NibeWP/issues) to report bugs or rise feature requests.
Questions can be addressed as new threads at the [knx-user-forum.de](https://knx-user-forum.de) also. There might be discussions and solutions already.


### Code

Der Code des Bausteins befindet sich in der hslz Datei oder auf [github](https://github.com/En3rGy/14107_NibeWP).

### Devleopment Environment

- [Python 2.7.18](https://www.python.org/download/releases/2.7/)
    - Install python markdown module (for generating the documentation) `python -m pip install markdown`
- Python editor [PyCharm](https://www.jetbrains.com/pycharm/)
- [Gira Homeserver Interface Information](http://www.hs-help.net/hshelp/gira/other_documentation/Schnittstelleninformationen.zip)


## Anforderungen

-

## Software Design Description

-

## Validierung & Verifikation

- Teilweise Abdeckung durch Unit Tests 

## Licence

Copyright 2021 T. Paul

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
