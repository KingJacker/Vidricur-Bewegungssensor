"""
Try all 4 SPI modes after reset. One should give a valid SHTP advertisement header.
"""
from machine import SPI, Pin
import time

RST_PIN  = 21
INT_PIN  = 20
CS_PIN   = 17
WAKE_PIN = 22

def reset_and_read(polarity, phase):
    int_pin  = Pin(INT_PIN,  Pin.IN)
    rst_pin  = Pin(RST_PIN,  Pin.OUT, value=1)
    cs_pin   = Pin(CS_PIN,   Pin.OUT, value=1)
    wake_pin = Pin(WAKE_PIN, Pin.OUT, value=1)

    spi = SPI(0, baudrate=500_000, sck=Pin(2), mosi=Pin(3), miso=Pin(16),
              polarity=polarity, phase=phase)

    # Reset
    rst_pin.value(0)
    time.sleep_ms(10)
    rst_pin.value(1)

    # Wait for INT
    deadline = time.ticks_add(time.ticks_ms(), 2000)
    while int_pin.value() == 1:
        if time.ticks_diff(deadline, time.ticks_ms()) <= 0:
            return None, "INT timeout"

    # Read header immediately
    cs_pin.value(0)
    time.sleep_us(10)
    h = bytearray(4)
    spi.readinto(h, 0x00)
    pkt_len = (h[0] | (h[1] << 8)) & 0x7FFF
    channel = h[2]

    # Read 8 payload bytes
    payload = bytearray(min(pkt_len - 4, 8)) if pkt_len > 4 else bytearray(0)
    if len(payload):
        spi.readinto(payload, 0x00)
    cs_pin.value(1)

    spi.deinit()
    return h, f"len={pkt_len} ch={channel} pay={[hex(b) for b in payload[:4]]}"

modes = [(0,0), (0,1), (1,0), (1,1)]
for pol, pha in modes:
    time.sleep_ms(200)  # let sensor settle between tests
    header, info = reset_and_read(pol, pha)
    h_str = [hex(b) for b in header] if header else "N/A"
    print(f"Mode pol={pol} pha={pha}: header={h_str}  {info}")
