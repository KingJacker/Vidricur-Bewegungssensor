# Accelerometer: GY-BNO085

Interface: **SPI** (PS1=high, PS0=WAKE)

## Wiring — Pi Pico

| GY-BNO085 Pin | Pico Pin | Note |
|---------------|----------|------|
| VCC | 3.3V | power |
| GND | GND | ground |
| SCL/SCK/RX | GP2 | SPI0 SCK |
| ADDR/MOSI | GP3 | SPI0 MOSI |
| SDA/MISO/TX | GP16 | SPI0 MISO |
| CS | GP17 | chip select |
| INT | GP20 | data-ready interrupt |
| RST | GP21 | reset |
| PS1 | 3.3V | SPI mode select (permanent) |
| PS0 | GP22 | WAKE (also SPI mode select at reset) |


> **Note:** PS1 must be tied HIGH before reset so the BNO085 boots into SPI mode.
> PS0 is driven HIGH by the Pico at boot (wake_pin), then used as the WAKE signal during operation.
