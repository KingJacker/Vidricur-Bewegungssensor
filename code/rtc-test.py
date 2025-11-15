from machine import Pin, I2C
from ds3231 import DS3231
import time

i2c = I2C(1, sda=Pin(2), scl=Pin(3))

ds = DS3231(i2c)


### SET TIME
# year = 2025 # Can be yyyy or yy format
# month = 11
# mday = 14
# hour = 13 # 24 hour format only
# minute = 14
# second = 0 # Optional
# weekday = 4 # Optional

# datetime = (year, month, mday, hour, minute, second, weekday)
# ds.datetime(datetime)


### GET TIME
print(ds.datetime())