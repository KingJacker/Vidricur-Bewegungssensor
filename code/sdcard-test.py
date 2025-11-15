from machine import SPI, Pin
import os
from sdcard import SDCard
import time # Import time for delays

SPI_BUS = 1
SCK_PIN = 10
MOSI_PIN = 11
MISO_PIN = 8
CS_PIN = 9
SD_MOUNT_PATH = '/sd'

try:
    # Init SPI communication
    spi = SPI(SPI_BUS,sck=Pin(SCK_PIN), mosi=Pin(MOSI_PIN), miso=Pin(MISO_PIN))
    cs = Pin(CS_PIN, Pin.OUT) # Explicitly set CS pin as output
    
    # Optional: Add a small delay after SPI and CS setup
    time.sleep_ms(50) 
    
    sd = SDCard(spi, cs)
    # Mount microSD card
    os.mount(sd, SD_MOUNT_PATH)
    # List files on the microSD card
    print(os.listdir(SD_MOUNT_PATH))
    
except Exception as e:
    print('An error occurred:', e)