# Vidricur Bewegungssensor

Ein Raspberry Pi Pico basiertes Datenerfassungssystem für Beschleunigungsdaten mit automatischer Speicherung auf SD-Karte.

## Übersicht

Dieses Projekt implementiert einen autonomen Bewegungssensor, der kontinuierlich Beschleunigungsdaten aufzeichnet. Ein BMI160 Accelerometer erfasst die Bewegungsdaten, die zusammen mit präzisen Zeitstempeln von einem DS3231 RTC-Modul auf einer SD-Karte im CSV-Format gespeichert werden. Die gespeicherten Daten können anschließend auf einem PC analysiert und visualisiert werden.

### Hauptmerkmale

- 📊 Kontinuierliche Datenerfassung mit konfigurierbarer Abtastrate
- 💾 Automatische Speicherung auf SD-Karte im CSV-Format
- ⏰ Präzise Zeitstempel durch RTC-Modul
- 🔋 Batteriebetrieb mit 18650 Li-Ion Akku
- 📈 Erfassung von Beschleunigung (ax, ay, az) und Neigungswinkeln (Roll, Pitch)
- 🔄 Batch-basiertes Schreiben für Effizienz

## Komponenten

### Hardware
| Komponente | Modell/Typ | Funktion |
|-----------|-----------|----------|
| Mikrocontroller | Raspberry Pi Pico | Hauptsteuerung |
| Beschleunigungssensor | BMI160 | 3-Achsen Beschleunigungsmessung |
| Real Time Clock | DS3231 | Präzise Zeitstempel |
| SD-Karten Modul | - | Datenspeicherung |
| Status LED | Eingebaut (Pin 25) | Betriebsanzeige |
| Batterie | 18650 Li-Ion | Stromversorgung |
| Lademodul | - | Batterieaufladung |
| Taster | Reset Button | System-Reset |
| Schalter | On/Off | Ein/Aus-Schaltung |

### Pin-Belegung

#### I2C Verbindungen
- **I2C0 (RTC DS3231)**
  - SDA: GPIO 4
  - SCL: GPIO 5
  
- **I2C1 (BMI160 Sensor)**
  - SDA: GPIO 26
  - SCL: GPIO 27

#### SPI Verbindungen (SD-Karte)
- SCK: GPIO 10
- MOSI: GPIO 11
- MISO: GPIO 8
- CS: GPIO 9

#### Sonstige
- Status LED: GPIO 25 (eingebaut)

## Software Konzept

### Ablaufdiagramm

Das System folgt diesem Ablauf:

1. **Initialisierung**
   - LED Pin konfigurieren
   - Button Pin konfigurieren
   - I2C-Busse einrichten
     - I2C0: RTC (DS3231)
     - I2C1: Accelerometer (BMI160)
   - SD-Karte über SPI initialisieren und mounten
   - Sensor kalibrieren (optional)

2. **Dateimanagement**
   - Neue CSV-Datei mit aktuellem Datum/Uhrzeit als Namen erstellen
   - Header schreiben: `Timestamp, ax, ay, az, roll, pitch`

3. **Hauptschleife**
   - Solange System aktiv:
     - LED aus (zeigt Datenerfassung an)
     - Batch von Messungen aufnehmen (Standard: 10 Messungen)
     - LED an (zeigt Schreibvorgang an)
     - Batch auf SD-Karte schreiben
     - Vorgang wiederholen

4. **Beenden**
   - Bei Tasterdruck oder Keyboard Interrupt (Ctrl+C)
   - SD-Karte ordnungsgemäß unmounten
   - System zurücksetzen

### Konfigurierbare Parameter

```python
BATCH_SIZE = 10           # Anzahl Messungen pro Batch
SAMPLE_RATE_MS = 100      # Millisekunden zwischen Messungen (10 Hz)
```

### Hauptfunktionen

| Funktion | Beschreibung | Rückgabewert |
|----------|--------------|--------------|
| `get_sensor_data_row()` | Liest aktuelle Sensordaten und Zeitstempel | Liste: [timestamp, ax, ay, az, roll, pitch] |
| `get_formatted_timestamp()` | Formatiert RTC-Zeit für CSV | String: "YYYY-MM-DD HH:MM:SS" |
| `init_sd_card()` | Initialisiert und mountet SD-Karte | Boolean: Erfolg/Fehler |
| `create_or_get_current_file(header)` | Erstellt CSV-Datei mit Header | String: Dateipfad |
| `write_data_batch(filepath, data_batch)` | Schreibt Batch auf SD-Karte | Boolean: Erfolg/Fehler |
| `logger_loop()` | Haupt-Datenlogger-Schleife | - |
| `set_rtc_time(...)` | Setzt RTC-Zeit manuell | - |

### Datenformat

Die gespeicherten CSV-Dateien haben folgendes Format:

```csv
Timestamp,ax,ay,az,roll,pitch
2025-11-15 13:30:00,0.0234,0.0156,-9.8100,0.89,-0.14
2025-11-15 13:30:00,0.0231,0.0158,-9.8095,0.90,-0.13
...
```

- **Timestamp**: Datum und Uhrzeit im Format `YYYY-MM-DD HH:MM:SS`
- **ax, ay, az**: Beschleunigung in m/s² (4 Dezimalstellen)
- **roll, pitch**: Neigungswinkel in Grad (2 Dezimalstellen)



## Diagramme

Die folgenden Diagramme zeigen die Hardware- und Software-Architektur:

| Hardware | Software |
|----------|----------|
| <img src="diagrams/hardware_diagram.svg" alt="Hardware Diagramm"> | <img src="diagrams/software_diagram.svg" alt="Software Diagramm"> |

## Verwendete Bibliotheken

Dieses Projekt verwendet die folgenden MicroPython-Bibliotheken:

| Komponente | Bibliothek | Quelle |
|-----------|-----------|---------|
| RTC-Modul | DS3231-AT24C32 | [GitHub Repository](https://github.com/pangopi/micropython-DS3231-AT24C32/tree/main) |
| Beschleunigungssensor | BMI160 | [Anleitung & Code](https://how2electronics.com/interface-bmi160-with-raspberry-pi-pico-micropython/) |
| SD-Karte | SDCard | [Direkt-Download](https://raw.githubusercontent.com/RuiSantosdotme/Random-Nerd-Tutorials/refs/heads/master/Projects/Raspberry-Pi-Pico/MicroPython/sd_card/sdcard.py) |

## Installation und Verwendung

### Voraussetzungen

- Raspberry Pi Pico mit MicroPython-Firmware
- Python 3.8 oder höher auf dem PC
- USB-Kabel für Verbindung zum Pico
- Alle erforderlichen Hardwarekomponenten (siehe Komponenten-Liste)

### Setup

1. **Python Virtual Environment einrichten**

   Dieses Projekt verwendet [uv](https://github.com/astral-sh/uv) für die Verwaltung der Python-Umgebung:

   ```bash
   # uv initialisieren
   uv init
   
   # mpremote installieren
   uv add mpremote
   ```

2. **Bibliotheken auf den Pico kopieren**

   Verwenden Sie `mpremote`, um alle erforderlichen Dateien auf den Raspberry Pi Pico zu kopieren:

   ```bash
   # Bibliotheken kopieren
   uv run mpremote fs cp code/bmi160.py :bmi160.py
   uv run mpremote fs cp code/ds3231.py :ds3231.py
   uv run mpremote fs cp code/sdcard.py :sdcard.py
   
   # Hauptprogramm kopieren
   uv run mpremote fs cp code/main.py :main.py
   ```

3. **RTC-Zeit einstellen (optional)**

   Beim ersten Start muss die RTC-Zeit gesetzt werden. Editieren Sie `main.py` und kommentieren Sie diese Zeile aus:

   ```python
   set_rtc_time(2025, 11, 15, 13, 1, 0, 5)  # Jahr, Monat, Tag, Stunde, Minute, Sekunde, Wochentag
   ```

4. **SD-Karte vorbereiten**

   - Formatieren Sie die SD-Karte mit FAT32
   - Setzen Sie die SD-Karte in das SD-Karten-Modul ein

### Ausführung

Nach dem Kopieren aller Dateien startet das Programm automatisch beim Einschalten des Pico:

1. Schalten Sie das Gerät ein
2. Die LED leuchtet während der Initialisierung
3. Die LED blinkt während des Betriebs:
   - **LED aus**: Datenerfassung läuft
   - **LED an**: Daten werden auf SD-Karte geschrieben
4. Die Daten werden in `/sd/YYYY-MM-DD_HH-MM-SS.csv` gespeichert

### Debugging und Tests

Einzelne Komponenten können mit den Test-Skripten überprüft werden:

```bash
# RTC testen
uv run mpremote fs cp code/rtc-test.py :rtc-test.py
uv run mpremote run rtc-test.py

# SD-Karte testen
uv run mpremote fs cp code/sdcard-test.py :sdcard-test.py
uv run mpremote run sdcard-test.py
```

### Daten auslesen

1. Schalten Sie das Gerät aus
2. Entnehmen Sie die SD-Karte
3. Stecken Sie die SD-Karte in Ihren PC
4. Die CSV-Dateien können mit Excel, Python (pandas), oder anderen Analyse-Tools geöffnet werden

## Konfiguration

Die Hauptkonfiguration erfolgt in `main.py` über folgende Konstanten:

```python
# SPI Pin-Konfiguration für SD-Karte
SD_SPI_BUS = 1
SD_SCK_PIN = 10
SD_MOSI_PIN = 11
SD_MISO_PIN = 8
SD_CS_PIN = 9

# Sensor & Datalogging Parameter
BATCH_SIZE = 10          # Anzahl der Messungen pro Batch
SAMPLE_RATE_MS = 100     # Millisekunden zwischen Messungen (10 Hz)
HEADER = ["Timestamp", "ax", "ay", "az", "roll", "pitch"]  # CSV Header
```

## Fehlerbehebung

### Problem: SD-Karte wird nicht erkannt

- Überprüfen Sie die SPI-Verkabelung
- Stellen Sie sicher, dass die SD-Karte mit FAT32 formatiert ist
- Versuchen Sie eine niedrigere SPI-Baudrate (z.B. 500000 statt 1000000)

### Problem: RTC-Zeit ist falsch

- Setzen Sie die Zeit manuell mit `set_rtc_time()` in `main.py`
- Überprüfen Sie die I2C-Verbindung zum RTC-Modul
- Die CR2032-Batterie im RTC-Modul könnte leer sein

### Problem: Keine Sensordaten

- Überprüfen Sie die I2C-Verbindung zum BMI160
- Testen Sie den Sensor einzeln mit dem entsprechenden Test-Skript
- Überprüfen Sie die I2C-Adresse des Sensors

### Problem: LED blinkt nicht

- Das System könnte bei der Initialisierung hängen bleiben
- Verbinden Sie sich über USB und prüfen Sie die Konsolenausgabe:
  ```bash
  uv run mpremote repl
  ```

## Beispiel CSV-Ausgabe

```csv
Timestamp,ax,ay,az,roll,pitch
2025-11-15 13:30:00,0.0234,0.0156,-9.8100,0.89,-0.14
2025-11-15 13:30:00,0.0231,0.0158,-9.8095,0.90,-0.13
2025-11-15 13:30:01,0.0229,0.0160,-9.8098,0.91,-0.13
2025-11-15 13:30:01,0.0233,0.0155,-9.8102,0.88,-0.14
```

## Projektstruktur

```
Vidricur-Bewegungssensor/
├── code/
│   ├── main.py           # Hauptprogramm
│   ├── bmi160.py         # BMI160 Treiber
│   ├── ds3231.py         # DS3231 RTC Treiber
│   ├── sdcard.py         # SD-Karten Treiber
│   ├── rtc-test.py       # RTC Test-Skript
│   └── sdcard-test.py    # SD-Karte Test-Skript
├── diagrams/
│   ├── hardware_diagram.svg
│   └── software_diagram.svg
└── readme.md             # Diese Datei
```

## Lizenz

Dieses Projekt ist Open Source. Bitte beachten Sie die Lizenzen der verwendeten Bibliotheken.

## Mitwirkende

Entwickelt als Teil des Vidricur-Projekts.

## Weiterführende Ressourcen

- [Raspberry Pi Pico Documentation](https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html)
- [MicroPython Documentation](https://docs.micropython.org/)
- [BMI160 Datasheet](https://www.bosch-sensortec.com/products/motion-sensors/imus/bmi160.html)
- [DS3231 RTC Module Guide](https://lastminuteengineers.com/ds3231-rtc-arduino-tutorial/)
