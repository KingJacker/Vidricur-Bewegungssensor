"""
Raw SHTP read test — bypasses driver, reads advertisement directly.
If this works, the hardware is fine and the issue is driver timing.
"""
from machine import SPI, Pin
import time

int_pin  = Pin(20, Pin.IN)
rst_pin  = Pin(21, Pin.OUT, value=1)
cs_pin   = Pin(17, Pin.OUT, value=1)
wake_pin = Pin(22, Pin.OUT, value=1)  # PS0/WAKE, keep HIGH for SPI mode

spi = SPI(0, baudrate=1_000_000, sck=Pin(2), mosi=Pin(3), miso=Pin(16),
          polarity=1, phase=1)

print(f"SPI config: {spi}")
print("Resetting sensor...")

# Hard reset
rst_pin.value(0)
time.sleep_ms(10)
rst_pin.value(1)

# Wait for INT to go LOW (sensor ready to send advertisement)
print("Waiting for INT (up to 2000ms)...")
deadline = time.ticks_add(time.ticks_ms(), 2000)
while int_pin.value() == 1:
    if time.ticks_diff(deadline, time.ticks_ms()) <= 0:
        print("TIMEOUT: INT never went LOW. Check wiring.")
        raise SystemExit

elapsed = time.ticks_diff(time.ticks_ms(), time.ticks_add(deadline, -2000))
print(f"INT went LOW after ~{elapsed}ms")

# Assert CS and read SHTP header (4 bytes)
cs_pin.value(0)
time.sleep_us(5)
header = bytearray(4)
spi.readinto(header, 0x00)

raw_len = header[0] | (header[1] << 8)
channel = header[2]
seq     = header[3]
cont    = bool(raw_len & 0x8000)
pkt_len = raw_len & 0x7FFF

print(f"\nHeader: {[hex(b) for b in header]}")
print(f"  Packet length : {pkt_len} (continuation={cont})")
print(f"  Channel       : {channel}  (expect 0 = advertisement)")
print(f"  Sequence      : {seq}")

if pkt_len == 0 or pkt_len > 300:
    cs_pin.value(1)
    print(f"\nBad packet length {pkt_len}. SPI data wrong — check MODE (need polarity=1 phase=1).")
    raise SystemExit

# Read payload
payload_len = pkt_len - 4
payload = bytearray(payload_len)
spi.readinto(payload, 0x00)
cs_pin.value(1)

print(f"\nPayload ({payload_len} bytes), first 16: {[hex(b) for b in payload[:16]]}")
print(f"  Report ID [0]: {hex(payload[0])}  (expect 0x00 = SHTP advertisement)")

if channel == 0 and payload[0] == 0x00:
    print("\nSUCCESS: Advertisement received correctly.")
    print("Issue is in driver timing — not hardware.")
else:
    print(f"\nUnexpected channel={channel} reportId={hex(payload[0])}.")
