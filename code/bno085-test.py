from bno08x_spi import BNO08X_SPI
from machine import SPI, Pin
import time

int_pin  = Pin(20, Pin.IN)
rst_pin  = Pin(21, Pin.OUT, value=1)
cs_pin   = Pin(17, Pin.OUT, value=1)
wake_pin = Pin(22, Pin.OUT, value=1)

spi = SPI(0, baudrate=3_000_000, sck=Pin(2), mosi=Pin(3), miso=Pin(16))

print("Initializing BNO085...")
bno = BNO08X_SPI(spi, cs_pin, rst_pin, int_pin, wake_pin, debug=True)
print("BNO085 OK")
print(spi)

bno.acceleration.enable(10)
bno.game_quaternion.enable(10)
bno.print_report_period()

print("\nReading sensor (Ctrl+C to stop):")
print("=" * 60)

while True:
    bno.update_sensors()

    if bno.acceleration.updated and bno.game_quaternion.updated:
        ax, ay, az = bno.acceleration
        qr, qi, qj, qk = bno.game_quaternion
        print(f"Accel  X:{ax:+7.3f}  Y:{ay:+7.3f}  Z:{az:+7.3f}  m/s²")
        print(f"Quat  QR:{qr:+7.4f} QI:{qi:+7.4f} QJ:{qj:+7.4f} QK:{qk:+7.4f}")
        print()
        time.sleep_ms(500)
