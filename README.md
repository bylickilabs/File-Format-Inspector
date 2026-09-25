# BYLICKILABS File Format Inspector

> [!IMPORTANT]
> **Version:** 1.0.0  
> **Plattform / Platform:** Windows Desktop  
> **Programmiersprache / Language:** Python 3.11+  
> **Oberfläche / Interface:** Deutsch (DE) · English (EN)  
> **Autor / Author:** Thorsten Bylicki / BYLICKILABS  
> **Technologien / Technologies:** Python · PySide6 / Qt · NumPy · SciPy

> **BYLICKILABS File Format Inspector** ist eine lokal arbeitende Windows-Anwendung zur Erkennung von Dateiformaten und zur Untersuchung binärer Dateiinhalte.
  - Die Anwendung verbindet Dateisignaturprüfung, einen farbigen Hex-Viewer, einen separaten Hex-Editor, statistische Datenanalyse und einen strukturierten Berichtsexport.

> **BYLICKILABS File Format Inspector** is a local Windows desktop application for file format identification and binary data inspection.
  - It combines file signature detection, a color-coded hex viewer, a separate hex editor, statistical data analysis, and structured report exports.

> [!CAUTION]
> **DE:** Der File Format Inspector ist **kein Antivirenprogramm**.
> - Erkannte Dateiformate, auffällige Muster und Entropiewerte sind Untersuchungsergebnisse, keine Aussage über die Sicherheit einer Datei.
> - Die analysierten Dateien werden nicht ausgeführt.  
> **EN:** File Format Inspector is **not an antivirus scanner**.
> - Identified formats, unusual patterns, and entropy values are analysis results, not a determination that a file is safe or malicious.
> - Analyzed files are not executed.

## Inhaltsverzeichnis / Table of Contents

| Deutsch | English |
|---|---|
| [01 · Überblick](#de-overview) | [01 · Overview](#en-overview) |
| [02 · Funktionen](#de-features) | [02 · Features](#en-features) |
| [03 · Systemanforderungen und Technologien](#de-requirements) | [03 · Requirements and technologies](#en-requirements) |
| [04 · Installation mit install.bat](#de-automatic-install) | [04 · Installation with install.bat](#en-automatic-install) |
| [05 · Virtuelle Umgebung manuell einrichten](#de-manual-install) | [05 · Set up a virtual environment manually](#en-manual-install) |
| [06 · Anwendung starten](#de-start) | [06 · Start the application](#en-start) |
| [07 · Dateianalyse und Statusmeldungen](#de-scan) | [07 · File analysis and statuses](#en-scan) |
| [08 · Unterstützte Formate](#de-formats) | [08 · Supported formats](#en-formats) |
| [09 · Hex-Vorschau, Ausdocken und Hex-Editor](#de-hex) | [09 · Hex preview, undocking, and hex editor](#en-hex) |
| [10 · DATA INFO](#de-data-info) | [10 · DATA INFO](#en-data-info) |
| [11 · PATTERN DATA und Mustersuche](#de-pattern) | [11 · PATTERN DATA and pattern search](#en-pattern) |
| [12 · Berichte und Export](#de-reports) | [12 · Reports and exports](#en-reports) |
| [13 · Sprache, INFO und Social Media](#de-interface) | [13 · Language, INFO, and social media](#en-interface) |
| [14 · Projektstruktur](#de-project) | [14 · Project structure](#en-project) |
| [15 · Datenschutz, Sicherheit und Grenzen](#de-safety) | [15 · Privacy, safety, and limitations](#en-safety) |
| [16 · Fehlerbehebung](#de-troubleshooting) | [16 · Troubleshooting](#en-troubleshooting) |
| [17 · GitHub-Repository und Projektintegration](#de-integration) | [17 · GitHub repository and project integration](#en-integration) |

# Deutsche Dokumentation

<a id="de-overview"></a>
## 01 · Überblick

> Der **BYLICKILABS File Format Inspector** untersucht Dateien anhand ihres tatsächlichen Inhalts, statt sich ausschließlich auf die Dateiendung zu verlassen.
  - Beispielsweise kann eine Datei mit der Endung `.jpg` anhand ihrer Signatur als PNG erkannt werden.
  - Bei uneindeutigen Containerformaten meldet die Anwendung eine eingeschränkte Identifikation, statt ein Format unbegründet zu behaupten.

| Bereich | Information |
|---|---|
| Anwendung | BYLICKILABS File Format Inspector |
| Version | 1.0.0 |
| System | Windows Desktop |
| Ausführung | Lokal, mit Python und virtueller Umgebung |
| Oberfläche | PySide6 / Qt |
| Sprachen | Deutsch und Englisch |
| Analyse | Dateisignaturen, Hex-Daten, Statistik, Muster und SHA-256 |
| Export | JSON und HTML |
| Autor | Thorsten Bylicki / BYLICKILABS |

> [!NOTE]
> Das bereitgestellte Python-Projekt ist **keine vorkompilierte EXE-Datei**.
> - Für die Ausführung wird eine passende Python-Installation benötigt.

<br>

---

<br>

<a id="de-features"></a>
## 02 · Funktionen

| Funktion | Beschreibung |
|---|---|
| Signaturerkennung | Identifiziert unterstützte Formate anhand von Dateiheadern und ausgewählten Strukturmerkmalen. |
| Endungsvergleich | Vergleicht erkanntes Format und vorhandene Dateiendung. |
| Datei- und Ordnerscan | Erfasst ausgewählte Dateien sowie reguläre Dateien in gewählten Ordnern und Unterordnern. |
| Hintergrundverarbeitung | Analysiert die Dateien in einem Qt-Arbeitsthread; Fortschritt und Abbruch sind vorgesehen. |
| SHA-256 | Berechnet den SHA-256-Hash über den vollständigen Dateiinhalt. |
| Hex-Vorschau | Farbcodierte Ansicht mit 256 Byte pro Seite, Offset und ASCII-Spalte im Hauptfenster. |
| Ausdockbare Hex-Ansicht | Zeigt die vollständige Datei in einem separaten, maximierbaren Fenster mit virtuellem Scrollen und direkter Offset-Navigation. |
| Hex-Editor | Öffnet eine unabhängig bearbeitbare Ansicht mit 512 Byte pro Seite, Hex-Mustersuche und „Kopie speichern unter“. |
| DATA INFO | Zeigt Entropie, Byte-Histogramm, Bytehäufigkeiten und weitere statistische Kennzahlen. |
| PATTERN DATA | Untersucht begrenzte Anfangsbereiche auf Muster, lesbare ASCII-Zeichenketten und Nullbyte-Sequenzen. |
| Berichte | Exportiert die vorhandenen Scanergebnisse im JSON- oder HTML-Format. |
| DE/EN | Wechsel der Oberflächensprache über `LANG`; ausführlicher `INFO`-Dialog. |

> [!IMPORTANT]
> **Alle regulären Dateien** innerhalb der gewählten Verzeichnisse werden ohne Filter auf bekannte Dateiendungen zur Analyse herangezogen.
> - Auch bei unbekannten Formaten wird ein Untersuchungsergebnis erstellt.
> - Symbolische Links und nicht lesbare Verzeichnisse werden übersprungen; ein abgebrochener Scan verarbeitet nur den bereits erreichten Teil der Auswahl.

<br>

---

<br>

<a id="de-requirements"></a>
## 03 · Systemanforderungen und Technologien

> **Voraussetzungen:** Windows, Python **3.11 oder neuer**, eine funktionierende `pip`- und `venv`-Installation sowie ausreichend freier Speicherplatz für Python-Pakete und gegebenenfalls bearbeitete Dateikopien.
  - Für den ersten Paketdownload kann eine Internetverbindung erforderlich sein.

> Die tatsächlichen Abhängigkeiten aus `requirements.txt` lauten:

```text
PySide6>=6.8,<7
numpy>=1.26,<3
scipy>=1.13,<2
```

| Technologie | Aufgabe |
|---|---|
| Python | Anwendungslogik, Dateiverarbeitung und Standardbibliothek |
| PySide6 / Qt | Benutzeroberfläche, zusätzliche Fenster und Hintergrundverarbeitung mit `QThread` |
| NumPy | Inkrementelle Bytehäufigkeiten, Histogramme und Array-Auswertungen |
| SciPy | Shannon-Entropie, Chi-Quadrat-Test und explorative Peaksuche |
| `hashlib` | SHA-256-Berechnung |
| `struct` / `zipfile` | Binärstrukturen und ausgewählte Containermerkmale |
| JSON / HTML | Ausgabe technischer Analyseberichte |

<br>

---

<br>

<a id="de-automatic-install"></a>
## 04 · Installation mit install.bat

> [!IMPORTANT]
> **Das Archiv zuerst vollständig entpacken.** `install.bat`, `start.bat`, `requirements.txt` und die Python-Module müssen gemeinsam im selben Projektordner liegen.
> - Die Batchdateien nicht direkt aus der ZIP-Vorschau starten.

1. Python 3.11 oder neuer installieren. Prüfen, ob Python über den Windows-Launcher `py` oder über `python` verfügbar ist.
2. Den Projektordner vollständig entpacken und öffnen.
3. `install.bat` per Doppelklick ausführen. Das Skript prüft die Python-Version, legt `.venv` an, aktualisiert nach Möglichkeit `pip`, installiert die Abhängigkeiten und prüft deren Import.
4. Nach erfolgreicher Installation `start.bat` ausführen.

> **Prüfung der Python-Version in der Eingabeaufforderung:**

```bat
py -3 --version
```

> Falls der Python-Launcher nicht verfügbar ist:

```bat
python --version
```

> **Die automatische Installation erzeugt diese lokale Struktur:**

```text
File_Format_Inspector/
├── .venv/
│   └── Scripts/
│       └── python.exe
├── install.bat
├── start.bat
├── requirements.txt
└── file_format_inspector.py
```

> [!NOTE]
> Die virtuelle Umgebung trennt die Projektpakete von anderen Python-Projekten. 
> - Die Abhängigkeiten müssen nicht global installiert werden.
> - Wenn `.venv` bereits vollständig eingerichtet ist, genügt für spätere Starts normalerweise `start.bat`.

<br>

---

<br>

<a id="de-manual-install"></a>
## 05 · Virtuelle Umgebung manuell einrichten

> **Alternative über die Windows-Eingabeaufforderung (`cmd`):** Im vollständig entpackten Projektordner die Adressleiste des Explorers anklicken, `cmd` eingeben und die folgenden Befehle nacheinander ausführen:

```bat
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -c "import PySide6, numpy, scipy; print('Dependencies OK')"
.venv\Scripts\python.exe file_format_inspector.py
```

> Wenn `py` nicht vorhanden ist, kann bei installiertem Python stattdessen `python -m venv .venv` verwendet werden.

> **Optionale Aktivierung der Umgebung in `cmd`:**

```bat
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python file_format_inspector.py
deactivate
```

> Die Aktivierung ist **nicht erforderlich**, wenn die Befehle direkt mit `.venv\Scripts\python.exe` aufgerufen werden.
  - Für PowerShell gelten andere Aktivierungsbefehle und gegebenenfalls Ausführungsrichtlinien; der direkte Aufruf von `python.exe` umgeht dieses Aktivierungsproblem.

<br>

---

<br>

<a id="de-start"></a>
## 06 · Anwendung starten

> Nach der Einrichtung:

```bat
start.bat
```

> Oder direkt über die virtuelle Umgebung:

```bat
.venv\Scripts\python.exe file_format_inspector.py
```

> `start.bat` wechselt in den eigenen Projektordner, prüft `.venv`, die Hauptdatei und die erforderlichen Pakete und startet dann die grafische Anwendung.
  - Bei einem Startfehler bleibt die Konsolenmeldung zur Diagnose sichtbar.

<br>

---

<br>

<a id="de-scan"></a>
## 07 · Dateianalyse und Statusmeldungen

1. Über **Dateien hinzufügen**, **Ordner hinzufügen** oder Drag & Drop die gewünschten Quellen auswählen.
2. **Analyse starten** anklicken und den Fortschritt abwarten. Der Scan kann über **Abbrechen** beendet werden.
3. Eine Ergebniszeile markieren, um Dateiinformationen, Hex-Daten, DATA INFO und PATTERN DATA für diese Datei anzuzeigen.
4. Die Ergebnisse bei Bedarf als JSON oder HTML exportieren.

> Erfasste Dateien werden anhand ihrer Inhalte untersucht.
  - Dabei werden Dateipfad, Dateigröße, Änderungszeitpunkt (UTC), Dateiendung, Erkennungsmerkmale, SHA-256 und statistische Werte ermittelt, soweit die Datei lesbar ist.
  - Eine Datei mit unbekannter Signatur wird nicht allein deshalb vom Scan ausgeschlossen.

| Status | Bedeutung |
|---|---|
| Passend | Die erkannte Dateifamilie ist mit der Endung vereinbar. |
| Abweichung | Die erkannte Dateifamilie passt nicht zur angegebenen Endung. |
| Unbekannt | Es wurde keine unterstützte Dateisignatur erkannt. |
| Ohne Endung | Ein Format wurde erkannt; die Datei hat keine Endung. |
| Nicht eindeutig | Eine Containerstruktur oder heuristische Erkennung reicht für eine eindeutige Zuordnung nicht aus. |
| Lesefehler | Die betreffende Datei konnte nicht vollständig verarbeitet werden. |

> [!NOTE]
> Verzeichnisse werden rekursiv erfasst.
> - Symbolische Links werden nicht verfolgt, um Schleifen und unbeabsichtigte Zugriffe außerhalb der Auswahl zu vermeiden.
> - Nicht lesbare Ordner können übersprungen werden; bei einzelnen Dateifehlern wird nach Möglichkeit ein Fehlerdatensatz ausgegeben. „Alle Dateien“ bedeutet daher **alle zugänglichen, regulären Dateien der ausgewählten Quellen**, nicht jede technisch denkbare Datei im Dateisystem.

<br>

---

<br>

<a id="de-formats"></a>
## 08 · Unterstützte Formate

| Kategorie | Erkennung |
|---|---|
| Bilder | JPEG, PNG, GIF, WebP, BMP, TIFF |
| Dokumente | PDF, RTF, DOCX, XLSX, PPTX, ODT, ODS, ODP |
| Archive | ZIP, RAR, 7z, GZIP, TAR |
| Audio | MP3, WAV, FLAC, Ogg |
| Video / Container | MP4 / ISO BMFF, AVI, WebM, Matroska |
| Windows-Binärdateien | PE-basierte EXE- und DLL-Varianten |
| Weitere Formate | SQLite 3, TrueType (TTF), OpenType (OTF) |

> **Beispiele für Dateisignaturen:**

```text
PNG       89 50 4E 47 0D 0A 1A 0A
JPEG      FF D8 FF
PDF       25 50 44 46 2D
ZIP       50 4B 03 04
Windows   4D 5A ... + PE-Header-Prüfung
SQLite    SQLite format 3\0
```

> DOCX, XLSX, PPTX und OpenDocument-Formate werden anhand ausgewählter ZIP-Containermerkmale genauer zugeordnet.
  - Andere ZIP-basierte Formate können als generischer ZIP-Container erscheinen.
  - Bei EXE und DLL überprüft die Anwendung MZ- und PE-Merkmale; es handelt sich **nicht** um eine vollständige PE-Strukturanalyse, Disassemblierung oder Authenticode-Prüfung.

<br>

---

<br>

<a id="de-hex"></a>
## 09 · Hex-Vorschau, Ausdocken und Hex-Editor

### Hex-Vorschau im Hauptfenster

> Die farbige Vorschau zeigt **256 Byte pro Seite** mit absoluten Offsets und einer ASCII-Spalte.
  - Über die Vorwärts- und Rückwärtsnavigation lassen sich weitere Vorschauseiten aufrufen.
  - Dieses Fenster ist schreibgeschützt.

### Vollständige Hex-Ansicht ausdocken

> Über **Hex-Vorschau ausdocken** wird die bestehende Vorschau in ein separates, verschiebbares und maximierbares Fenster übertragen.
  - Dort ist die **gesamte Datei** über eine virtuelle Bildlaufleiste zugänglich; angezeigt werden die gerade sichtbaren Hex- und ASCII-Werte, der Dateipfad und der beim Scan berechnete SHA-256-Hash.
  - Eine Eingabe wie `4096` oder `0x1000` springt zu einem absoluten Offset.
  - Beim Andocken oder Schließen kehrt die Vorschau in das Hauptfenster zurück.

> [!NOTE]
> Die Grenze von 256 Byte gilt **nur für die angedockte Vorschau**.
> - In der ausgedockten Ansicht werden jeweils die benötigten Bildschirmzeilen nachgeladen, nicht die gesamte Datei gleichzeitig in den Arbeitsspeicher eingelesen.
> - Die ausgedockte Ansicht bleibt schreibgeschützt.

### Hex-Editor in einem eigenen Fenster

> Über **Hex-Editor im eigenen Fenster** wird ein gesondertes Bearbeitungsfenster geöffnet.
  - Ist keine analysierte Datei ausgewählt, kann die zu bearbeitende Datei über einen Dateidialog geöffnet werden.

1. Mit den Seitenschaltflächen navigieren oder einen absoluten Offset (dezimal beziehungsweise mit `0x`) eingeben.
2. Das gewünschte Byte in der **512-Byte-Seite** doppelt anklicken und zwei Hex-Ziffern von `00` bis `FF` eingeben.
3. Änderungen werden farbig hervorgehoben und zunächst nur vorgemerkt.
4. Über **Kopie speichern unter** einen **anderen Dateipfad** auswählen. Die Quelldatei wird nicht überschrieben. Wird als Ziel eine bereits vorhandene *andere* Datei gewählt, fragt die Anwendung vor dem Ersetzen nach.

> Vor dem Speichern kontrolliert die Anwendung bei den geänderten Bytepositionen, ob die Quelldaten noch den zuvor gelesenen Originalwerten entsprechen.
  - Ein nachträglich veränderter Ausgangsbestand kann den Speichervorgang deshalb abbrechen.

> [!WARNING]
> Eine Byteänderung kann Programme, Archive oder Dokumente unbrauchbar machen.
> - Die Anwendung repariert dabei **keine** formatabhängigen Checksummen, Header, Signaturen oder internen Offsets.
> - Vor dem Bearbeiten wichtige Originale separat sichern.

<br>

---

<br>

<a id="de-data-info"></a>
## 10 · DATA INFO

> Die Statistik basiert auf den Bytehäufigkeiten der vollständig gelesenen Datei; die Daten werden blockweise verarbeitet.

| Kennzahl | Erläuterung |
|---|---|
| Shannon-Entropie | Verteilungsbasierte Entropie in Bit pro Byte, im Wertebereich von 0 bis 8. |
| Byte-Histogramm | Absolute Häufigkeit sämtlicher 256 möglichen Bytewerte, skaliert auf den häufigsten Wert. |
| Unterschiedliche Bytewerte | Anzahl der tatsächlich vorkommenden Werte zwischen `00` und `FF`. |
| Druckbare ASCII-Zeichen | Anteil der Bytewerte `20` bis `7E`. |
| Nullbyte-Anteil | Anteil des Bytewerts `00`. |
| Mittelwert / Standardabweichung | Deskriptive Statistik der Bytewerte. |
| Chi-Quadrat-p-Wert | Statistischer Vergleich mit einer hypothetisch gleichmäßigen Byteverteilung. |
| Fensterentropie | Entropiewerte in 4096-Byte-Fenstern **nur aus der begrenzten Anfangsstichprobe**. |

> **Farblegende direkt unter dem Byte-Histogramm:**

| Farbe | Bytekategorie |
|---|---|
| Grau `#7e96ad` | Nullbyte `00` |
| Grün `#75e0b1` | Druckbare ASCII-Zeichen `20`–`7E` |
| Blau `#73b5ed` | Übrige Bytewerte außerhalb der anderen Gruppen |
| Orange `#ffba80` | Bytewert `FF` |

> [!IMPORTANT]
> Die Farben kennzeichnen **Bytekategorien**, keine Entropiestufen.
> - Eine hohe Entropie kann unter anderem bei komprimierten, verschlüsselten oder andersartig verteilten Daten vorkommen; sie beweist weder Verschlüsselung noch Schadsoftware.
> - Der Chi-Quadrat-p-Wert ist **kein Sicherheitswert**.

<br>

---

<br>

<a id="de-pattern"></a>
## 11 · PATTERN DATA und Mustersuche

> **Die automatische Musteranalyse ist stichprobenbasiert:**

| Untersuchung | Analysierter Bereich |
|---|---|
| ASCII-Zeichenketten und Nullbyte-Sequenzen | Anfangsbereich der Datei, maximal **128 KiB** |
| Häufige Vier-Byte-Muster | Anfangsbereich, maximal **64 KiB** |
| Explorative Byte-Periodizität | Anfangsbereich, maximal **8 KiB** |
| Fensterentropie | Anfangsstichprobe, maximal **128 KiB**, Fenstergröße **4096 Byte** |

> Ein Klick auf ein erkanntes Vier-Byte-Muster kann dieses in der Hex-Vorschau hervorheben.
  - Die automatische Suche beschreibt **nicht die gesamte Datei**, sofern diese größer als die jeweilige Stichprobe ist.

> **Gezielte Suche über die vollständige Datei:** Im separaten Hex-Editor können Hex-Muster wie `4D 5A ?? 00` gesucht werden.
  - `??` steht für **genau ein beliebiges Byte**.
  - Ein Suchmuster umfasst 1 bis 256 Bytes und muss mindestens ein festgelegtes Byte enthalten.
  - Die Suche berücksichtigt auch Treffer über Lese-Blockgrenzen hinweg; sie gibt **maximal 200 Treffer** pro Suchlauf aus.
  - Treffer lassen sich zur Offset-Navigation auswählen.

<br>

---

<br>

<a id="de-reports"></a>
## 12 · Berichte und Export

> Nach der Analyse stehen zwei Ausgabeformate bereit:

| Format | Inhalt und Einsatz |
|---|---|
| JSON | Maschinenlesbare Scanergebnisse einschließlich Dateipfad, Format, Status, SHA-256 sowie umfangreicher `data_info`-Statistik und Musterinformationen. |
| HTML | Lesbarer Tabellenbericht mit Dateiinformationen, erkannten Formaten, SHA-256 und ausgewählten Statistikfeldern (Entropie, Anzahl unterschiedlicher Bytewerte, ASCII-/Nullbyte-Anteil, Stichprobengröße). |

> Die Berichte werden über den jeweiligen Exportbutton an einem lokal gewählten Speicherort erstellt.
  - Sie können absolute Dateipfade, Dateinamen und technische Metadaten enthalten und sollten vor einer öffentlichen Weitergabe geprüft werden.

<br>

---

<br>

<a id="de-interface"></a>
## 13 · Sprache, INFO und Social Media

> **`LANG`** öffnet die Sprachauswahl **Deutsch (DE) / English (EN)** und aktualisiert die Benutzeroberfläche sowie die Bezeichnungen neuer Analyseansichten.
  - **`INFO`** öffnet einen Dialog mit Informationen zu Funktionen, technischen Verfahren, Formaten, Einschränkungen und Datenschutz.

> Die Schaltflächen **GitHub**, **Facebook** und **LinkedIn** öffnen bei Betätigung die hinterlegten BYLICKILABS-Profile beziehungsweise das GitHub-Repository im Standardbrowser.
  - Die URLs und die zentralen Anwendungsdaten stehen am Anfang von `file_format_inspector.py`:

```python
APP_NAME = "BYLICKILABS File Format Inspector"
APP_TITLE = "BYLICKILABS | FILE FORMAT INSPECTOR"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Thorsten Bylicki / BYLICKILABS"
GITHUB_URL = "https://github.com/bylickilabs/Desktop-Utility-Toolkit"
FACEBOOK_URL = "https://www.facebook.com/BylickiLabs"
LINKEDIN_URL = "https://www.linkedin.com/in/bylicki/"
```

<br>

---

<br>

<a id="de-project"></a>
## 14 · Projektstruktur

```text
File_Format_Inspector/
├── file_format_inspector.py  # Hauptfenster, Scansteuerung, INFO, LANG, Links
├── file_analyzer.py          # Dateierfassung, SHA-256 und Analyseergebnisse
├── signature_database.py     # Dateisignaturen und ausgewählte Strukturmerkmale
├── data_analysis.py          # NumPy/SciPy, Statistik und Mustersuche
├── data_panels.py            # DATA INFO, PATTERN DATA und Histogrammlegende
├── hex_viewer.py             # Hex-Vorschau und Wechsel in Vollansicht
├── hex_full_view.py          # Virtuelles Scrollen durch die gesamte Datei
├── hex_navigation.py         # Offset- und Fenster-Navigation
├── hex_editor.py             # Separater Hex-Editor und Suchfenster
├── hex_patch.py              # Kopie mit vorgemerkten Byteänderungen speichern
├── report_generator.py       # JSON- und HTML-Export
├── translations.py           # DE/EN-Übersetzungen
├── requirements.txt          # Python-Abhängigkeiten
├── install.bat               # Einrichtung der virtuellen Umgebung
├── start.bat                 # Start mit lokaler Python-Umgebung
└── README.md                 # Diese Dokumentation
```

> Die virtuelle Umgebung `.venv/` wird bei der Installation lokal erzeugt und gehört nicht zum eigentlichen Quellcode.

<br>

---

<br>

<a id="de-safety"></a>
## 15 · Datenschutz, Sicherheit und Grenzen

> Die eigentliche Dateianalyse, Hashberechnung, Statistik und Bearbeitung erfolgen **lokal**; die untersuchten Dateien werden dafür nicht an einen externen Dienst hochgeladen.
  - Externe Webseiten werden erst durch die entsprechenden Social-Media-Buttons geöffnet. Zum erstmaligen Installieren der Pakete kann ein Internetzugang nötig sein.
  - Die Signaturerkennung klassifiziert nur unterstützte Formate und bestimmte Strukturmerkmale. **Unbekannt** bedeutet nicht **gefährlich**, und **passend** bedeutet nicht **sicher**.
  - SHA-256 ermöglicht den Vergleich von Dateiinhalten. Ein einzelner Hashwert beweist ohne vertrauenswürdigen Referenzwert keine Herkunft oder Unbedenklichkeit.
  - Die vollständige Datei fließt in Hashberechnung und globale Byte-Statistik ein. Die automatische Musteranalyse bleibt auf die unter [PATTERN DATA](#de-pattern) angegebenen Bereiche begrenzt.
  - Im separaten Hex-Editor werden Änderungen auf eine **andere Ausgabedatei** angewendet; die analysierte Originaldatei wird nicht absichtlich überschrieben. Andere bestehende Zieldateien können nach Bestätigung ersetzt werden.
  - Der Inspector führt keine Datei aus und ist kein Malware-Scanner, keine vollständige Dateiformatvalidierung und kein Ersatz für Backups.

<br>

---

<br>

<a id="de-troubleshooting"></a>
## 16 · Fehlerbehebung

| Problem | Mögliche Abhilfe |
|---|---|
| `Python` wurde nicht gefunden | Python 3.11+ installieren und `py -3 --version` oder `python --version` prüfen. |
| `.venv` fehlt | Im entpackten Ordner `install.bat` ausführen. |
| Paketimport schlägt fehl | `install.bat` erneut ausführen und die angezeigte `pip`-Fehlermeldung prüfen. |
| Anwendung schließt sich sofort | `start.bat` in `cmd` starten, damit die genaue Fehlermeldung sichtbar bleibt. |
| Hex-Editor öffnet sich nicht | Prüfen, ob alle Projektdateien aus derselben Fassung stammen, insbesondere `hex_editor.py`; eventuelle Fehlermeldung notieren. |
| Die Hex-Vorschau zeigt nur 256 Byte | Die **Vorschau ausdocken**, um die vollständige Datei zu scrollen; für Änderungen den **separaten Hex-Editor** öffnen. |
| Format unbekannt / nicht eindeutig | Die Datei kann trotzdem untersucht werden; die Signaturdatenbank deckt nicht alle Dateiformate ab. |
| Verzeichnis enthält weniger Ergebnisse als erwartet | Berechtigungen, symbolische Links, abgebrochenen Scan und übersprungene nicht lesbare Unterordner prüfen. |

> **Start mit sichtbarer Konsole:**

```bat
cd /d "C:\Pfad\zum\File_Format_Inspector"
start.bat
```

> Den Beispielpfad durch den tatsächlichen Projektordner ersetzen.
  - Alternativ im Explorer den Ordner öffnen, `cmd` in die Adressleiste eingeben und anschließend `start.bat` ausführen.

<br>

---

<br>

<a id="de-integration"></a>
## 17 · GitHub-Repository und Projektintegration

> Der File Format Inspector ist als Anwendungsordner innerhalb des [BYLICKILABS Desktop Utility Toolkit](https://github.com/bylickilabs/Desktop-Utility-Toolkit) vorgesehen.
  - Die Python-Abhängigkeiten und die lokal erzeugte `.venv` werden innerhalb des Anwendungsordners verwaltet.

<br>

---

<br>

# English Documentation

<a id="en-overview"></a>
## 01 · Overview

> **BYLICKILABS File Format Inspector** examines file content rather than relying solely on filename extensions.
  - A file named `.jpg`, for example, may be identified as PNG from its signature.
  - Ambiguous container formats are reported as such instead of being assigned an unsupported definitive format.

| Item | Details |
|---|---|
| Application | BYLICKILABS File Format Inspector |
| Version | 1.0.0 |
| Platform | Windows Desktop |
| Runtime | Local Python environment |
| Interface | PySide6 / Qt |
| Languages | German and English |
| Analysis | File signatures, hex data, statistics, patterns, and SHA-256 |
| Export | JSON and HTML |
| Author | Thorsten Bylicki / BYLICKILABS |

> [!NOTE]
> The distributed Python project is **not a precompiled `.exe` file**.
> - A compatible Python installation is required.

<br>

---

<br>

<a id="en-features"></a>
## 02 · Features

| Feature | Description |
|---|---|
| File signature detection | Identifies supported formats using headers and selected structural indicators. |
| Extension comparison | Compares the detected format with the filename extension. |
| Files and folders | Scans selected files and regular files in selected folders and subfolders. |
| Background scan | Runs analysis in a Qt worker thread, with progress and cancellation support. |
| SHA-256 | Calculates the SHA-256 digest of the full file. |
| Hex preview | Color-coded, read-only preview of 256 bytes per page, with offsets and ASCII. |
| Undocked hex view | Scrolls through the entire file in an independent, resizable window, with direct offset navigation. |
| Hex editor | Opens a separate editable window with 512-byte pages, full-file pattern search, and Save Copy As. |
| DATA INFO | Shows entropy, byte histogram, frequencies, and additional statistical measures. |
| PATTERN DATA | Examines bounded initial samples for byte patterns, ASCII strings, and zero runs. |
| Reporting | Exports available scan results to JSON or HTML. |
| DE/EN | Language selection using `LANG` and a detailed `INFO` dialog. |

> [!IMPORTANT]
> **All regular files** in selected directories are considered for scanning, regardless of whether their extensions are recognized.
> - Unknown formats are still represented in the results.
> - Symbolic links and unreadable directories are skipped; a canceled scan only covers the files processed before cancellation.

<br>

---

<br>

<a id="en-requirements"></a>
## 03 · Requirements and technologies

> **Requirements:** Windows, Python **3.11 or newer**, working `pip` and `venv` support, and sufficient disk space for dependencies and any edited output copies.
  - Downloading missing packages may require an internet connection.

> Actual dependencies listed in `requirements.txt`:

```text
PySide6>=6.8,<7
numpy>=1.26,<3
scipy>=1.13,<2
```

| Technology | Purpose |
|---|---|
| Python | Core application, file I/O, and standard library |
| PySide6 / Qt | Graphical interface, floating windows, and `QThread` workers |
| NumPy | Incremental byte frequencies, histograms, and array operations |
| SciPy | Shannon entropy, chi-square test, and exploratory peak detection |
| `hashlib` | SHA-256 hashing |
| `struct` / `zipfile` | Binary structures and selected container indicators |
| JSON / HTML | Structured analysis reports |

<br>

---

<br>

<a id="en-automatic-install"></a>
## 04 · Installation with install.bat

> [!IMPORTANT]
> **Extract the entire archive first.** Keep `install.bat`, `start.bat`, `requirements.txt`, and the Python modules together in the same project directory.
> - Do not run the batch files directly from the ZIP preview.

1. Install Python 3.11 or newer. Make sure the Windows `py` launcher or `python` command is available.
2. Extract and open the project directory.
3. Double-click `install.bat`. The script checks the Python version, creates `.venv`, attempts to update `pip`, installs the declared packages, and checks that they can be imported.
4. When installation succeeds, run `start.bat`.

> Check Python from Command Prompt:

```bat
py -3 --version
```

> If the launcher is unavailable:

```bat
python --version
```

> The automatic installation creates the following local structure:

```text
File_Format_Inspector/
├── .venv/
│   └── Scripts/
│       └── python.exe
├── install.bat
├── start.bat
├── requirements.txt
└── file_format_inspector.py
```

> [!NOTE]
> The virtual environment isolates this project's dependencies from other Python installations.
> - Global package installation is unnecessary.
> - Once `.venv` has been set up successfully, `start.bat` is normally sufficient for subsequent launches.

<br>

---

<br>

<a id="en-manual-install"></a>
## 05 · Set up a virtual environment manually

> **Alternative using Windows Command Prompt (`cmd`):** Open the fully extracted project directory, type `cmd` in the File Explorer address bar, and execute:

```bat
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -c "import PySide6, numpy, scipy; print('Dependencies OK')"
.venv\Scripts\python.exe file_format_inspector.py
```

> If `py` is unavailable, use `python -m venv .venv` with a compatible installed version of Python.

> **Optional activation in `cmd`:**

```bat
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python file_format_inspector.py
deactivate
```

> Activation is **not necessary** if you invoke `.venv\Scripts\python.exe` directly.
  - PowerShell uses a different activation command and may enforce script execution policies; using the environment's `python.exe` directly avoids that activation issue.

<br>

---

<br>

<a id="en-start"></a>
## 06 · Start the application

> After setup:

```bat
start.bat
```

> Or run Python directly from the virtual environment:

```bat
.venv\Scripts\python.exe file_format_inspector.py
```

> `start.bat` changes to its own directory, verifies that `.venv`, the main module, and required packages are present, then launches the graphical application.
  - If launch fails, its console displays the error for diagnosis.

<br>

---

<br>

<a id="en-scan"></a>
## 07 · File analysis and statuses

1. Use **Add Files**, **Add Folder**, or drag and drop to select sources.
2. Click **Start Analysis** and monitor the progress. Use **Cancel** to stop the scan.
3. Select a result row to display file details, hex data, DATA INFO, and PATTERN DATA for that file.
4. Export the results to JSON or HTML if needed.

> The application inspects actual file content and collects path, size, UTC modification time, extension, evidence, SHA-256, and statistics where reading succeeds.
  - A file with an unknown signature is not excluded merely for being unknown.

| Status | Meaning |
|---|---|
| Matched | The identified format is compatible with the file extension. |
| Mismatch | The identified file family does not match the declared extension. |
| Unknown | No supported signature has been identified. |
| No extension | A format was found, but the file has no extension. |
| Ambiguous | A container structure or heuristic signal does not justify a definitive identification. |
| Read error | The file could not be fully processed. |

> [!NOTE]
> Directory enumeration is recursive.
> - Symbolic links are not followed, avoiding cycles and unexpected traversal outside selected folders.
> - Unreadable directories may be skipped; individual file errors are recorded where possible.
> - Accordingly, “all files” means **accessible regular files from the selected sources**, not every possible file on the system.

<br>

---

<br>

<a id="en-formats"></a>
## 08 · Supported formats

| Category | Detection |
|---|---|
| Images | JPEG, PNG, GIF, WebP, BMP, TIFF |
| Documents | PDF, RTF, DOCX, XLSX, PPTX, ODT, ODS, ODP |
| Archives | ZIP, RAR, 7z, GZIP, TAR |
| Audio | MP3, WAV, FLAC, Ogg |
| Video / containers | MP4 / ISO BMFF, AVI, WebM, Matroska |
| Windows binaries | PE-based EXE and DLL variants |
| Other formats | SQLite 3, TrueType (TTF), OpenType (OTF) |

> Example signatures:

```text
PNG       89 50 4E 47 0D 0A 1A 0A
JPEG      FF D8 FF
PDF       25 50 44 46 2D
ZIP       50 4B 03 04
Windows   4D 5A ... + PE header validation
SQLite    SQLite format 3\0
```

> DOCX, XLSX, PPTX, and OpenDocument formats are differentiated using selected ZIP container indicators.
  - Other ZIP-based files can remain generic ZIP containers.
  - EXE/DLL detection examines MZ and PE indicators; it is **not** a full PE-structure analysis, disassembler, or Authenticode signature verification tool.

<br>

---

<br>

<a id="en-hex"></a>
## 09 · Hex preview, undocking, and hex editor

### Docked hex preview

> The read-only, color-coded preview displays **256 bytes per page** with absolute offsets and an ASCII column.
  - Previous/Next navigates between preview pages.

### Undock the complete hex view

> Click **Undock Hex Preview** to move the existing viewer into a separate, movable, maximizable window.
  - Its virtual scrollbar provides access to the **entire file**; the viewer shows the currently visible hex and ASCII values, file path, and SHA-256 hash calculated during the scan.
  - Enter `4096` or `0x1000` to jump to an absolute offset.
  - Docking or closing the floating window returns the preview to the main interface.

> [!NOTE]
> The **256-byte limit only applies to the docked preview**.
> - The undocked view reads just the visible rows as needed instead of loading the whole file into memory.
> - It remains read-only.

### Hex editor in a separate window

> Click **Open Hex Editor in Separate Window** to open the editable view.
  - If no analyzed result is selected, a file chooser allows a file to be opened directly.

1. Navigate using the page controls or enter an absolute offset in decimal or `0x` notation.
2. Double-click a byte in the **512-byte page**, then enter two hexadecimal digits from `00` to `FF`.
3. Modified bytes are highlighted and staged in memory.
4. Use **Save Copy As** to choose a **different output path**. The source file is not overwritten. If a separate destination file already exists, replacement requires confirmation.

> Before writing a modified copy, the application checks that the original values at edited offsets still match the values observed while editing.
  - If the source data has changed, saving may be aborted.

> [!WARNING]
> Editing bytes can render programs, archives, or documents unusable.
> - The editor does **not** repair format-specific checksums, headers, signatures, or internal offsets.
> - Keep an independent backup of important source files.

<br>

---

<br>

<a id="en-data-info"></a>
## 10 · DATA INFO

> Whole-file statistics are derived from byte frequencies accumulated while reading the file incrementally.

| Metric | Description |
|---|---|
| Shannon entropy | Distribution-based entropy in bits per byte, from 0 to 8. |
| Byte histogram | Absolute frequency of all 256 possible byte values, scaled relative to the highest count. |
| Unique byte values | Number of values between `00` and `FF` observed in the file. |
| Printable ASCII | Percentage of bytes between `20` and `7E`. |
| Zero bytes | Percentage of bytes equal to `00`. |
| Mean / standard deviation | Descriptive statistics of byte values. |
| Chi-square p-value | Statistical comparison against a hypothetical uniform byte distribution. |
| Window entropy | Entropy in 4096-byte windows **from the bounded initial sample only**. |

> **Color legend displayed directly below the byte histogram:**

| Color | Byte category |
|---|---|
| Gray `#7e96ad` | Zero byte `00` |
| Green `#75e0b1` | Printable ASCII `20`–`7E` |
| Blue `#73b5ed` | Remaining byte values outside the other groups |
| Orange `#ffba80` | Byte value `FF` |

> [!IMPORTANT]
> The colors represent **byte categories**, not entropy bands.
> - High entropy may occur in compressed, encrypted, or otherwise distributed data; it proves neither encryption nor malware.
> - The chi-square p-value is **not a security score**.

<br>

---

<br>

<a id="en-pattern"></a>
## 11 · PATTERN DATA and pattern search

> **Automatic pattern inspection uses bounded samples:**

| Analysis | Coverage |
|---|---|
| ASCII strings and zero runs | Initial sample, at most **128 KiB** |
| Frequent four-byte patterns | Initial sample, at most **64 KiB** |
| Exploratory byte periodicity | Initial sample, at most **8 KiB** |
| Window entropy | Initial sample, at most **128 KiB**, **4096-byte** windows |

> Clicking a recognized four-byte pattern can highlight it in the hex preview.
  - Automatic pattern results do **not represent the whole file** when the file exceeds the respective sample size.

> **Explicit full-file search:** Use the separate hex editor to search for hexadecimal sequences such as `4D 5A ?? 00`.
  - `??` matches **exactly one arbitrary byte**.
  - A pattern contains 1–256 bytes and must specify at least one concrete byte.
  - Search handles matches across read-chunk boundaries and reports **up to 200 matches** per run.
  - Select a hit to navigate to its offset.

<br>

---

<br>

<a id="en-reports"></a>
## 12 · Reports and exports

> After analysis, the application offers two output formats:

| Format | Content and use |
|---|---|
| JSON | Machine-readable scan records including file paths, formats, statuses, SHA-256, and detailed `data_info` statistics and pattern findings. |
| HTML | Readable tabular report with file metadata, detected formats, SHA-256, and selected statistics (entropy, unique-byte count, ASCII/zero percentages, sample size). |

> The export buttons save reports to a locally selected destination.
  - Reports can include absolute paths, filenames, and technical metadata; review them before publishing or sharing.

<br>

---

<br>

<a id="en-interface"></a>
## 13 · Language, INFO, and social media

> **`LANG`** offers **Deutsch (DE) / English (EN)** and updates the interface and newly added analysis view labels.
  - **`INFO`** opens a dialog covering the application's functions, technical methods, formats, limitations, and privacy information.

> The **GitHub**, **Facebook**, and **LinkedIn** buttons open the configured BYLICKILABS pages or repository in the default browser when clicked.
  - Application metadata and URLs are defined near the top of `file_format_inspector.py`:

```python
APP_NAME = "BYLICKILABS File Format Inspector"
APP_TITLE = "BYLICKILABS | FILE FORMAT INSPECTOR"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Thorsten Bylicki / BYLICKILABS"
GITHUB_URL = "https://github.com/bylickilabs/Desktop-Utility-Toolkit"
FACEBOOK_URL = "https://www.facebook.com/BylickiLabs"
LINKEDIN_URL = "https://www.linkedin.com/in/bylicki/"
```

<br>

---

<br>

<a id="en-project"></a>
## 14 · Project structure

```text
File_Format_Inspector/
├── file_format_inspector.py  # Main window, scan orchestration, INFO, LANG, links
├── file_analyzer.py          # File enumeration, SHA-256, result records
├── signature_database.py     # File signatures and selected structural evidence
├── data_analysis.py          # NumPy/SciPy, statistics, and pattern search
├── data_panels.py            # DATA INFO, PATTERN DATA, histogram legend
├── hex_viewer.py             # Docked hex preview and full-view transition
├── hex_full_view.py          # Virtual scrolling through the entire file
├── hex_navigation.py         # Offset and byte-window navigation
├── hex_editor.py             # Separate editable hex window and pattern search
├── hex_patch.py              # Write a copy with staged byte changes
├── report_generator.py       # JSON and HTML export
├── translations.py           # German and English strings
├── requirements.txt          # Python dependencies
├── install.bat               # Virtual environment setup
├── start.bat                 # Launch with local Python environment
└── README.md                 # This documentation
```

> The virtual environment `.venv/` is created locally during setup and is not part of the source code.

<br>

---

<br>

<a id="en-safety"></a>
## 15 · Privacy, safety, and limitations

> File analysis, hashing, statistics, and editing are performed **locally**; analyzed files are not uploaded to an external service for these operations.
  - External websites open only when their social media buttons are used. Installing missing Python packages may require internet access.
  - Signature detection classifies supported formats and selected structural indicators only. **Unknown** does not mean **dangerous**, and **matched** does not mean **safe**.
  - SHA-256 can be used to compare file content. Without a trusted reference hash, a digest alone does not establish origin or safety.
  - Full-file hashing and global byte statistics process the whole file. Automatic pattern analysis remains limited to the sample ranges described in [PATTERN DATA](#en-pattern).
  - Separate hex-editor modifications are written to a **different output path**; the analyzed source file is not intentionally overwritten. An existing *other* destination file can be replaced after confirmation.
  - The inspector does not execute analyzed files and is neither an antivirus program, a comprehensive format validator, nor a substitute for backups.

<br>

---

<br>

<a id="en-troubleshooting"></a>
## 16 · Troubleshooting

| Problem | Suggested action |
|---|---|
| Python not found | Install Python 3.11+ and check `py -3 --version` or `python --version`. |
| `.venv` missing | Run `install.bat` from the extracted project folder. |
| Dependency import fails | Run `install.bat` again and inspect the displayed `pip` error. |
| App closes immediately | Launch `start.bat` from `cmd` so the actual error stays visible. |
| Hex editor does not open | Ensure all modules are from the same application revision, especially `hex_editor.py`; capture the displayed error. |
| Hex preview shows only 256 bytes | **Undock the preview** to scroll the whole file; use the **separate hex editor** for modifications. |
| Format is unknown / ambiguous | The file can still be inspected; the signature database does not cover every format. |
| Fewer files than expected | Check permissions, symbolic links, canceled runs, and unreadable subdirectories. |

> **Launch with a visible console:**

```bat
cd /d "C:\Path\To\File_Format_Inspector"
start.bat
```

> Replace the example path with the actual project directory.
  - Alternatively, open the folder in File Explorer, type `cmd` in its address bar, and run `start.bat`.

<br>

---

<br>

<a id="en-integration"></a>
## 17 · GitHub repository and project integration

> File Format Inspector is intended to reside in its own application folder within the [BYLICKILABS Desktop Utility Toolkit](https://github.com/bylickilabs/Desktop-Utility-Toolkit).
  - Python dependencies and the locally created `.venv` are managed within the application folder.

**BYLICKILABS · File Format Inspector · v1.0.0**  
**Thorsten Bylicki / BYLICKILABS**
