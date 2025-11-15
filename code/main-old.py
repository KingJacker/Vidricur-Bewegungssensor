from bmi160 import BMI160
from ds3231 import DS3231
from machine import I2C, Pin
import time



### CONFIG
BATCH_SIZE = 10
HEADER = ["Timestamp", "ax", "ay", "az", "roll", "pitch"]
SAMPLE_RATE = 0.1 # seconds



def set_time(datetime):
	year = 2025 # Can be yyyy or yy format
	month = 11
	mday = 14
	hour = 13 # 24 hour format only
	minute = 14
	second = 0 # Optional
	weekday = 4 # Optional
	datetime = (year, month, mday, hour, minute, second, weekday)
	rtc.datetime(datetime)

def get_time():
	return rtc.datetime()

def get_data():
	datetime = rtc.datetime()
	ax, ay, az = imu.read_acceleration()
	pitch, roll = imu.calculate_tilt_angles(ax, ay, az)
	return [datetime, ax, ay, az, pitch, roll]


def create_new_file(datetime):
	year, month, mday, hour, minute, second, weekday = datetime
	filename = f"{year}-{month}-{mday}_{hour}-{minute}-{second}.csv" # 2025-11-15_13-11-30
	filepath = "/sd/" + filename

	if filename not in os.listdir("/sd"):
		try:
			with open(filepath, "w", newline="") as csvfile:
				writer = csv.writer(csvfile)
				writer.writerow(HEADER)
			print(f"Created CSV file: {filename}")
			return filepath

		except Exception as e:
			print(f"Error creating CSV file: {e}")
			return false
	else:
		print(f"File already exists: {filename}")



def write_batch(filepath, data_batch):
	try:
		with open(filepath, "a", newline="") as csvfile:
			writer = csv.writer(csvfile)
			writer.writerow(data_batch)
		print(f"Appended {len(data_batch)} entries")
		return True
	
	except Exception as e:
			print(f"Error creating CSV file: {e}")
			return false



def logger_loop(filepath):
	
	print("Starting logger...")

	while True:
		data_buffer = []

		for i in range(BATCH_SIZE):
			data_buffer.append(get_data())
	
		write_batch(filepath, data_buffer)
		time.sleep(SAMPLE_RATE)


if __name__ == "__main__":
	### SETUP IO
	try: 
		i2c1 = I2C(1, scl=Pin(27), sda=Pin(26), freq=400000) # BMI160
		i2c0 = I2C(0, scl=Pin(5), sda=Pin(4), freq=400000) # RTC

		spi = SPI(SPI_BUS,sck=Pin(SCK_PIN), mosi=Pin(MOSI_PIN), miso=Pin(MISO_PIN)) # sdcard
		cs = Pin(CS_PIN, Pin.OUT) # Explicitly set CS pin as output
		time.sleep_ms(50)

	except Exception as e:
		print(f"Error i2c/spi setup: {e}")


	### INIT
	try:
		rtc = DS3231(i2c0)
		imu = BMI160(i2c1)

		sd = SDCard(spi, cs)
		os.mount(sd, "/sd")
		print("SD card mounted")
		# print(os.listdir(SD_MOUNT_PATH))

	except Exception as e:
		print(f"Error initializing classes: {e}")

	try:
		filepath = create_new_file(get_time())
		logger_loop(filepath)

	except Exception as e:
		print(f"Error: {e}")

