from bno08x_spi import BNO08X_SPI
from ds3231 import DS3231
from machine import I2C, SPI, Pin
import time
import os
import sdcard

led = Pin(25, Pin.OUT) # builtin led

# --- CONFIG ---
SD_SPI_BUS = 1
SD_SCK_PIN = 10
SD_MOSI_PIN = 11
SD_MISO_PIN = 8
SD_CS_PIN = 9

BNO_SPI_BUS = 0
BNO_SCK_PIN = 2
BNO_MOSI_PIN = 3
BNO_MISO_PIN = 16
BNO_CS_PIN = 17
BNO_INT_PIN = 20
BNO_RST_PIN = 21
BNO_WAKE_PIN = 22

# Sensor & Datalogging
BATCH_SIZE = 10
# HEADER values should not contain commas
HEADER = ["Timestamp", "ax", "ay", "az", "qr", "qi", "qj", "qk"]
SAMPLE_RATE_HZ = 100  # BNO085 report rate

# --- Global/Shared Objects (will be initialized in __main__) ---
rtc = None
imu = None
sd_mounted = False
current_filepath = None

# --- RTC Functions ---
def set_rtc_time(year, month, mday, hour, minute, second=0, weekday=0):
	"""
	Sets the RTC time.
	year (yyyy), month (1-12), mday (1-31), hour (0-23), minute (0-59), second (0-59), weekday (0-6)
	"""
	global rtc
	if rtc:
		try:
			rtc.datetime((year, month, mday, hour, minute, second, weekday))
			print(f"RTC time set to: {rtc.datetime()}")
		except Exception as e:
			print(f"Error setting RTC time: {e}")
	else:
		print("RTC not initialized.")

def get_formatted_timestamp():
	"""
	Retrieves current time from RTC and formats it for CSV.
	Returns: A string like "2025-11-15 13:30:00"
	"""
	global rtc
	if rtc:
		year, month, mday, weekday, hour, minute, second, _ = rtc.datetime()
		return f"{year:04d}-{month:02d}-{mday:02d} {hour:02d}:{minute:02d}:{second:02d}"
	else:
		# Fallback if RTC isn't ready, useful for debugging
		print("RTC not initialized. Returning generic timestamp.")
		return f"NO_RTC_{time.time():.0f}"


# --- Sensor Data Acquisition ---
def get_sensor_data_row():
	"""
	Reads data from IMU and RTC, returning a single row as a list of strings/numbers.
	Blocks until both accelerometer and game_quaternion reports are updated (max 100ms).
	"""
	global imu, rtc
	if not imu:
		print("IMU not initialized. Returning dummy data.")
		return [get_formatted_timestamp(), "0.0", "0.0", "0.0", "0.0", "0.0", "0.0", "0.0"]

	deadline = time.ticks_add(time.ticks_ms(), 100)
	while not (imu.acceleration.updated and imu.game_quaternion.updated):
		imu.update_sensors()
		if time.ticks_diff(deadline, time.ticks_ms()) <= 0:
			break

	timestamp = get_formatted_timestamp()
	ax, ay, az = imu.acceleration
	qr, qi, qj, qk = imu.game_quaternion

	return [timestamp, f"{ax:.4f}", f"{ay:.4f}", f"{az:.4f}", f"{qr:.6f}", f"{qi:.6f}", f"{qj:.6f}", f"{qk:.6f}"]

# --- SD Card & File Operations ---
def init_sd_card():
	"""Initializes and mounts the SD card."""
	global sd_mounted
	try:
		spi = SPI(
			SD_SPI_BUS,
			baudrate=1000000, # Start with a lower baudrate, can increase if stable
			sck=Pin(SD_SCK_PIN),
			mosi=Pin(SD_MOSI_PIN),
			miso=Pin(SD_MISO_PIN)
		)
		cs = Pin(SD_CS_PIN, Pin.OUT)

		time.sleep_ms(500)

		sd = sdcard.SDCard(spi, cs)
		os.mount(sd, "/sd")
		sd_mounted = True
		print("[SD] mounted to /sd")
		return True
	except Exception as e:
		print(f"Error initializing or mounting SD card: {e}")
		sd_mounted = False
		return False

def unmount_sd_card():
	"""Unmounts the SD card."""
	global sd_mounted
	if sd_mounted:
		try:
			os.umount("/sd")
			sd_mounted = False
			print("SD card unmounted.")
		except Exception as e:
			print(f"Error unmounting SD card: {e}")
	else:
		print("SD card not mounted.")

def create_or_get_current_file(header):
	"""
	Generates a new filename based on current time and creates the CSV file with header.
	Returns: The full filepath string, or None if creation fails.
	"""
	if not sd_mounted:
		print("SD card not mounted, cannot create file.")
		return None

	timestamp_for_filename = get_formatted_timestamp().replace(" ", "_").replace(":", "-") # "YYYY-MM-DD_HH-MM-SS"
	filename = f"{timestamp_for_filename}.csv"
	filepath = "/sd/" + filename

	try:
		if filename not in os.listdir("/sd"):
			with open(filepath, "w") as f: # No newline='' needed when manually handling newlines
				f.write(",".join(header) + "\n") # Manually join header elements with comma
			print(f"[WRITER] Created new CSV file: {filename}")
		else:
			print(f"File already exists: {filename}. Appending to it.")
		return filepath
	except Exception as e:
		print(f"Error creating/accessing CSV file: {e}")
		return None

def write_data_batch(filepath, data_batch):
    """
    Appends a batch of sensor data to the specified CSV file.
    Each row in data_batch is a list of values.
    """
    if not sd_mounted:
        print("SD card not mounted, cannot write data.")
        return False
    if not filepath:
        print("No valid filepath to write to.")
        return False
    if not data_batch: # Handle empty batch gracefully
        print("Empty data batch, nothing to write.")
        return True

    try:
        with open(filepath, "a") as f: # No newline='' needed
            for row in data_batch:
                f.write(",".join(map(str, row)) + "\n") # Convert all elements to string and join
        
        filename = filepath.split('/')[-1]
        print(f"[LOGGER] Appended {len(data_batch)} entries to {filename}")
        
        return True
    except Exception as e:
        print(f"Error writing batch to CSV file: {e}")
        return False

# --- Main Datalogger Loop ---
def logger_loop():
	"""
	Main loop for collecting and writing batches of sensor data.
	"""
	global current_filepath
	if not sd_mounted:
		print("SD card not mounted. Logger cannot start.")
		return

	current_filepath = create_or_get_current_file(HEADER)
	if not current_filepath:
		print("Failed to get a valid filepath. Logger cannot start.")
		return

	data_buffer = [] # Initialize buffer outside the while loop
	print("[LOGGER] Starting data logging...")

	while True:
		led.off()

		# Collect sensor readings — paced by BNO085 interrupt (100 Hz)
		for _ in range(BATCH_SIZE):
			data_row = get_sensor_data_row()
			data_buffer.append(data_row)

		led.on()
		# Write the collected batch
		if len(data_buffer) > 0:
			if write_data_batch(current_filepath, data_buffer):
				data_buffer = [] # Clear buffer only on successful write
			else:
				print("Write failed, data remains in buffer for next attempt.")
		else:
			print("Buffer empty, this should not happen if BATCH_SIZE > 0.")
		
		


# --- Main Execution ---
if __name__ == "__main__":

	led.on()

	# --- Sensor & RTC Setup ---
	try:
		i2c0 = I2C(0, scl=Pin(5), sda=Pin(4), freq=400000)
		rtc = DS3231(i2c0)
		print("[I2C] RTC Initialized")
	except Exception as e:
		print(f"Error initializing RTC: {e}")

	try:
		bno_spi = SPI(BNO_SPI_BUS, baudrate=3_000_000, sck=Pin(BNO_SCK_PIN), mosi=Pin(BNO_MOSI_PIN), miso=Pin(BNO_MISO_PIN))
		cs_pin   = Pin(BNO_CS_PIN,   Pin.OUT, value=1)
		int_pin  = Pin(BNO_INT_PIN,  Pin.IN)
		rst_pin  = Pin(BNO_RST_PIN,  Pin.OUT, value=1)
		wake_pin = Pin(BNO_WAKE_PIN, Pin.OUT, value=1)
		imu = BNO08X_SPI(bno_spi, cs_pin, rst_pin, int_pin, wake_pin)
		imu.acceleration.enable(SAMPLE_RATE_HZ)
		imu.game_quaternion.enable(SAMPLE_RATE_HZ)
		print("[SPI] BNO085 Initialized")
	except Exception as e:
		print(f"Error initializing BNO085: {e}")

	# --- SD Card Init ---
	if not init_sd_card():
		print("SD card initialization failed. Datalogger will not function properly.")
		# We proceed, but the logger_loop will detect sd_mounted is False.

	# --- Set RTC Time (Optional, uncomment and adjust if you need to set time) ---
	# set_rtc_time(2025, 11, 15, 13, 1, 0, 5) # Y, M, D, H, M, S, Weekday (Friday)
	# print(f"Current RTC time: {get_formatted_timestamp()}")


	led.off()
	# --- Start Logger ---
	try:
		logger_loop()
	except KeyboardInterrupt:
		print("\n--- Datalogger stopped by user (Ctrl+C) ---")
	except Exception as e:
		print(f"--- An unhandled error occurred in the logger loop: {e} ---")
	finally:
		unmount_sd_card() # Always attempt to unmount
		print("Datalogger finished.")