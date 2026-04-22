"""
BNO085 wiring diagnostic — run before the full driver test.
Checks INT, RST, and raw SPI response without the driver.
"""
from machine import SPI, Pin
import time

INT_PIN  = 20
RST_PIN  = 21
CS_PIN   = 17
WAKE_PIN = 22

int_pin  = Pin(INT_PIN,  Pin.IN,  Pin.PULL_UP)
rst_pin  = Pin(RST_PIN,  Pin.OUT, value=1)
cs_pin   = Pin(CS_PIN,   Pin.OUT, value=1)
wake_pin = Pin(WAKE_PIN, Pin.OUT, value=1)

spi = SPI(0, baudrate=1_000_000, sck=Pin(2), mosi=Pin(3), miso=Pin(16), polarity=1, phase=1)

print("=== BNO085 Wiring Check ===\n")

# 1. INT idle state
print(f"[1] INT pin (GP{INT_PIN}) idle: {int_pin.value()}  (expect 1 = HIGH when idle)")

# 2. Pulse RST and watch INT
print(f"\n[2] Pulsing RST (GP{RST_PIN}) LOW for 10ms...")
rst_pin.value(0)
time.sleep_ms(10)
rst_pin.value(1)
print("    RST released HIGH. Watching INT for 1000ms...")

deadline = time.ticks_add(time.ticks_ms(), 1000)
int_fired = False
while time.ticks_diff(deadline, time.ticks_ms()) > 0:
    if int_pin.value() == 0:
        int_fired = True
        break

if int_fired:
    print("    INT went LOW — sensor alive and signalling.")
else:
    print("    INT never went LOW — sensor not responding.")
    print("    CHECK: INT module pin → GP20, PS1 → 3.3V, VCC → 3.3V, wiring")

# 3. Try raw SPI read (4-byte SHTP header)
print(f"\n[3] Raw SPI read (4 bytes) after INT...")
cs_pin.value(0)
time.sleep_us(10)
buf = bytearray(4)
spi.readinto(buf, 0x00)
cs_pin.value(1)
print(f"    Raw bytes: {[hex(b) for b in buf]}")
print(f"    Packet len (little-endian): {buf[0] | (buf[1] << 8)}")
print(f"    Channel: {buf[2]}  (expect 0 = SHTP advertisement)")
if buf[0] == 0xFF and buf[1] == 0xFF:
    print("    All 0xFF — MISO floating or not connected.")
    print("    CHECK: SDA module pin → GP16 (MISO)")
elif buf[0] == 0 and buf[1] == 0:
    print("    All zeros — sensor not driving MISO. Check PS1 → 3.3V (SPI mode select).")
elif buf[2] == 0:
    pkt_len = buf[0] | (buf[1] << 8)
    print(f"    Channel 0, packet len {pkt_len} — looks like advertisement. MISO OK.")
else:
    print(f"    Unexpected channel {buf[2]} — partial connection or noise.")

print("\n=== Done ===")
