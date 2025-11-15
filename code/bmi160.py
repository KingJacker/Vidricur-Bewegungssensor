from machine import I2C, Pin
import math
import time

class BMI160:
	# Constants
	# BMI160_I2C_ADDR = 0x69
	# ACCEL_SENSITIVITY = 16384.0  # ±2g sensitivity for the accelerometer in LSB/g

	def __init__(self, i2c, i2c_addr=0x69, sensitivity=16384.0):
		self.i2c = i2c
		self.BMI160_I2C_ADDR = i2c_addr
		self.ACCEL_SENSITIVITY = sensitivity

		self.initialize_bmi160()

		# Perform auto-calibration
		self.ax_offset, self.ay_offset, self.az_offset = self.auto_calibrate()


	def write_register(self, addr, reg, data):
		"""Write data to a register."""
		self.i2c.writeto_mem(addr, reg, bytes([data]))

	def read_register(self, addr, reg, length):
		"""Read data from a register."""
		return self.i2c.readfrom_mem(addr, reg, length)

	def initialize_bmi160(self):
		"""Initialize the BMI160 sensor."""
		# Set accelerometer to normal mode
		self.write_register(self.BMI160_I2C_ADDR, 0x7E, 0x11)  # ACC_NORMAL_MODE
		time.sleep(0.1)

	def read_raw_acceleration(self):
		"""Read raw acceleration data."""
		data = self.read_register(self.BMI160_I2C_ADDR, 0x12, 6)  # Read accel data
		ax_raw = int.from_bytes(data[0:2], 'little') - (1 << 16 if data[1] & 0x80 else 0)
		ay_raw = int.from_bytes(data[2:4], 'little') - (1 << 16 if data[3] & 0x80 else 0)
		az_raw = int.from_bytes(data[4:6], 'little') - (1 << 16 if data[5] & 0x80 else 0)
		return ax_raw, ay_raw, az_raw

	def auto_calibrate(self):
		"""Perform auto-calibration to remove noise or error."""
		print("[BMI160] Starting auto-calibration...")
		num_samples = 100
		ax_offset = 0
		ay_offset = 0
		az_offset = 0

		for _ in range(num_samples):
			ax_raw, ay_raw, az_raw = self.read_raw_acceleration()
			ax_offset += ax_raw
			ay_offset += ay_raw
			az_offset += az_raw
			time.sleep(0.01)  # Small delay between readings
			# print(_)

		# Calculate average offsets
		ax_offset //= num_samples
		ay_offset //= num_samples
		az_offset //= num_samples

		# Assuming the sensor is stable, Z-axis should measure 1g (gravity)
		az_offset -= int(self.ACCEL_SENSITIVITY)

		print("[BMI160] Auto-calibration completed.")
		print("[BMI160] Offsets - X: {}, Y: {}, Z: {}".format(ax_offset, ay_offset, az_offset))

		return ax_offset, ay_offset, az_offset

	def read_acceleration(self):
		"""Read raw acceleration data, apply offsets, and convert to m/s²."""
		ax_raw, ay_raw, az_raw = self.read_raw_acceleration()
		ax = ((ax_raw - self.ax_offset) / self.ACCEL_SENSITIVITY) * 9.81  # Convert to m/s²
		ay = ((ay_raw - self.ay_offset) / self.ACCEL_SENSITIVITY) * 9.81  # Convert to m/s²
		az = ((az_raw - self.az_offset) / self.ACCEL_SENSITIVITY) * 9.81  # Convert to m/s²
		return ax, ay, az

	def calculate_tilt_angles(self, ax, ay, az):
		"""Calculate pitch and roll angles from acceleration."""
		pitch = math.atan2(ay, math.sqrt(ax**2 + az**2)) * 180.0 / math.pi
		roll = math.atan2(-ax, az) * 180.0 / math.pi
		return pitch, roll

