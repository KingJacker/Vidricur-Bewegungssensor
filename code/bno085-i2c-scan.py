"""
Scan I2C1 (GP26/GP27) for BNO085.
BNO085 I2C addresses: 0x4A (ADDR=GND) or 0x4B (ADDR=VCC)
"""
from machine import I2C, Pin

i2c = I2C(1, scl=Pin(27), sda=Pin(26), freq=400_000)
found = i2c.scan()

print(f"I2C scan: {[hex(a) for a in found]}")
if 0x4A in found:
    print("BNO085 found at 0x4A — module is in I2C mode (ADDR=GND)")
elif 0x4B in found:
    print("BNO085 found at 0x4B — module is in I2C mode (ADDR=VCC)")
else:
    print("BNO085 not found on I2C.")
    print("Check: SCL/SCK → GP27, SDA/MISO → GP26")
