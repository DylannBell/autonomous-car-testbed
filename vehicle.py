import time
from zenwheels.protocol import *

msgHeader = " [VEHICLE]: "

class Vehicle:
	def __init__(self, owner):
		# Vehicle properties.
		self.owner = owner
		self.position = None  # World coordinates (x, y).
		self.orientation = None  # Degrees clockwise from north.
		self.dimensions = None  # Size and shape (width, length).
		self.max_speed = None
		self.max_acceleration = None
		self.max_deceleration = None
		self.max_turn = None
		self.max_turn_change = None

		# Vehicle state.
		self.current_speed = None
		self.current_angle = None
		self.horn_active = False
		self.headlights_active = False
		self.left_signal_active = False
		self.right_signal_active = False
		self.police_siren_active = False

		# List of commands to be sent to the corresponding ZenWheels car.
		self.command_queue = {}

	def get_orientation(self):
		return self.orientation

	def get_speed(self):
		return self.current_speed

	def set_speed(self, speed):
		if speed >= 0:  # Forwards.
			if speed > 63:  # Maximum.
				speed = 63
			self.queueCommand(bytes([THROTTLE, speed]))
		else:  # Backwards.
			if speed < -64:  # Maximum.
				speed = 64
			else:
				speed = 128 + speed
			self.queueCommand(bytes([THROTTLE, speed]))

	def set_angle(self, angle):
		if angle >= 0:  # Steering right.
			if angle > 63:  # Maximum.
				angle = 63
			self.queueCommand(bytes([STEERING, angle]))
		else:  # Steering left.
			if angle < -64:  # Maximum.
				angle = 64
			else:
				angle = 128 + angle
			self.queueCommand(bytes([STEERING, angle]))

	def stop(self):
		self.queueCommand(bytes([THROTTLE, 0]))

	def horn_on(self):
		if self.horn_active == False:
			self.queueCommand(bytes([HORN, HORN_ON]))
			self.horn_active = True

	def horn_off(self):
		if self.horn_active == True:
			self.queueCommand(bytes([HORN, HORN_OFF]))
			self.horn_active = False

	def headlights_on(self):
		if self.headlights_active == False:
			self.queueCommand(bytes([HEADLIGHT, HEADLIGHT_BRIGHT]))
			self.headlights_active = True

	def headlights_off(self):
		if self.headlights_active == True:
			self.queueCommand(bytes([HEADLIGHT, HEADLIGHT_OFF]))
			self.headlights_active = False

	def left_signal_on(self):
		if self.left_signal_active == False:
			self.queueCommand(bytes([LEFT_SIGNAL, SIGNAL_FRONT_BRIGHT]))
			self.left_signal_active = True

	def left_signal_off(self):
		if self.left_signal_active == True:
			self.queueCommand(bytes([LEFT_SIGNAL, SIGNAL_OFF]))
			self.left_signal_active = False

	def right_signal_on(self):
		if self.right_signal_active == False:
			self.queueCommand(bytes([RIGHT_SIGNAL, SIGNAL_FRONT_BRIGHT]))
			self.right_signal_active = True

	def right_signal_off(self):
		if self.right_signal_active == True:
			self.queueCommand(bytes([RIGHT_SIGNAL, SIGNAL_OFF]))
			self.right_signal_active = False
			
	def police_siren_on(self):
		if self.police_siren_active == False:
			self.queueCommand(bytes([EFFECTS, EFFECTS_POLICE_HILO]))
			self.police_siren_active = True
			
	def police_siren_off(self):
		if self.police_siren_active == True:
			self.queueCommand(bytes([EFFECTS, EFFECTS_OFF]))
			self.police_siren_active = False

	def queueCommand(self, command):
		self.command_queue[command] = int(round(time.time() * 1000))  # Append time of queueing in milliseconds.


class Car(Vehicle):
	def __init__(self, owner):
		Vehicle.__init__(self, owner)
		self.max_speed = 50
		self.dimensions = (35, 60)
		self.max_acceleration = 2
		self.max_deceleration = 1


class Truck(Vehicle):
	def __init__(self, owner):
		Vehicle.__init__(self, owner)
		self.max_speed = 40
		self.dimensions = (40, 90)
		self.max_acceleration = 0.5
		self.max_deceleration = 0.25


class Motorcycle(Vehicle):
	def __init__(self, owner):
		Vehicle.__init__(self, owner)
		self.max_speed = 60
		self.dimensions = (15, 30)
		self.max_acceleration = 3
		self.max_deceleration = 2


class Bicycle(Vehicle):
	def __init__(self, owner):
		Vehicle.__init__(self, owner)
		self.max_speed = 20
		self.dimensions = (8, 25)
		self.max_acceleration = 1
		self.max_deceleration = 1
