# Vidricur Bewegungssensor

Accelerometer data logger: sensor data is written to a CSV on an SD card, then analyzed and visualized on PC.

## Components

- Raspberry Pi Pico
- GY-BNO085 IMU (accelerometer + gyroscope + fusion)
- Real Time Clock (DS3231 RTC)
- SD card module
- Status LED (built-in, GP25)
- 18650 Li-Ion battery + charging module
- On/Off switch

## Wiring

See [accelerometer.md](accelerometer.md) for full BNO085 pin connections.

**SD card (SPI1):**

| SD Module | Pico Pin |
|-----------|----------|
| VCC | 3.3V |
| GND | GND |
| SCK | GP10 |
| MOSI | GP11 |
| MISO | GP8 |
| CS | GP9 |

**RTC DS3231 (I2C0):**

| RTC Module | Pico Pin |
|------------|----------|
| VCC | 3.3V |
| GND | GND |
| SCL | GP5 |
| SDA | GP4 |

## Use Case

Mounted on an RC vehicle to log orientation continuously. Tilt angle is computed post-recording from the quaternion data to verify the vehicle never exceeded 10°.

## Software Concept

On startup the Pico initializes the RTC, BNO085, and SD card. A new CSV file is created named after the current datetime. The logger then continuously collects batches of sensor readings and writes them to the file.

Each row contains: `Timestamp, ax, ay, az, qr, qi, qj, qk`

- `ax/ay/az` — calibrated acceleration in m/s² (gravity included)
- `qr/qi/qj/qk` — Game Rotation Vector quaternion (onboard fusion, no magnetometer needed)

The BNO085 runs at **100 Hz**. Data is written in batches of 10 rows.

## Calibration

The BNO085 automatically saves calibration data to its own internal flash. On every boot it loads the previous calibration — no user action needed. On first-ever boot, calibration starts from scratch and improves automatically in the background during use.

## CSV Output Format

```
Timestamp,ax,ay,az,qr,qi,qj,qk
2025-11-15 13:30:00,0.1234,-0.0521,9.8102,0.999812,0.001234,-0.005678,0.012345
...
```

## Libraries

| Library | File | Source |
|---------|------|--------|
| BNO08X base driver | `bno08x.py` | [bradcar/bno08x_i2c_spi_MicroPython](https://github.com/bradcar/bno08x_i2c_spi_MicroPython) |
| BNO08X SPI driver | `bno08x_spi.py` | same |
| DS3231 RTC | `ds3231.py` | [pangopi/micropython-DS3231-AT24C32](https://github.com/pangopi/micropython-DS3231-AT24C32) |
| SD card | `sdcard.py` | [RuiSantosdotme/Random-Nerd-Tutorials](https://raw.githubusercontent.com/RuiSantosdotme/Random-Nerd-Tutorials/refs/heads/master/Projects/Raspberry-Pi-Pico/MicroPython/sd_card/sdcard.py) |

## Usage

### Setup

Install `mpremote` via `uv`:

```bash
uv init
uv add mpremote
```

### Set RTC time (first time only)

Uncomment and adjust this line in `main.py`, then flash and run once:

```python
# set_rtc_time(2025, 11, 15, 13, 1, 0, 5)  # Y, M, D, H, M, S, Weekday
```

Re-comment it before deploying.

### Copy files to Pico

```bash
cd code
uv run mpremote fs cp bno08x.py     :bno08x.py
uv run mpremote fs cp bno08x_spi.py :bno08x_spi.py
uv run mpremote fs cp ds3231.py     :ds3231.py
uv run mpremote fs cp sdcard.py     :sdcard.py
uv run mpremote fs cp main.py       :main.py
```

### Run

```bash
uv run mpremote run main.py
```

Or copy `main.py` as `main.py` on the Pico — it will auto-run on boot.

### Retrieve CSV from SD card

Remove the SD card and read on PC, or use mpremote:

```bash
uv run mpremote fs ls /sd
uv run mpremote fs cp :/sd/2025-11-15_13-30-00.csv ./data.csv
```

## Diagrams

| Hardware | Software |
| -------- | -------- |
| <img src="diagrams/hardware_diagram.svg"> | <img src="diagrams/software_diagram.svg"> |
