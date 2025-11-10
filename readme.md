# Vidricur Bewegungssensor

Es wird ein Accelerationssensor verwendet, dessen Daten auf einer SD-Karte gespeichert werden, welche im Anschluss auf dem PC mit ausgewertet und dargestellt werden.


## Komponenten
- Real Time Clock (RTC)
- SD-Karten Modul
- Accelerometer
- Pi Pico
- Status Led
- 18650 Li-Ion Battery
- Charging Module
- Button (Reset)
- On/Off Switch

## Software Konzept
Nach Initialisierung, wird der Sensor Kalibiriert.

Es wird eine neue CSV-Datei erstellt, mit dem Momentanen Datetime als Name.

Solange der Knopf nicht gedrückt ist: 

Ein Batch Messungen wird aufgenommen und auf die SD Karte, in die erstellte Datei geschrieben.

Wenn der Knopf gedrückt wird (wurde die letzte Batch bereits geschrieben):
    
Reset

### Initialize
- Led Pin
- Button Pin
- I2C
    - RTC
    - SD-Card Module
    - Accelerometer

- Calibrate

#### Functions
- get_data()
    - returns: [datetime, sensor values] 
- get_batch(num)
    - returns: num of sensor values
- write_batch()
- calibrate()



## Diagramme
| Hardware | Software |
| -------- | -------- |
| <img src="diagrams/hardware_diagram.svg"> | <img src="diagrams/software_diagram.svg">  |


