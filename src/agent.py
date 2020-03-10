import time
import math
from threading import Thread
import vehicle
import pygame


msgHeader = "[AGENT]: "


class Agent():
	def __init__(self, ID, agentType="robot", vehicleType="car", strategyFile=None):
		self.ID = str(ID)

		if vehicleType.lower() == "car":
			self.vehicle = vehicle.Car(self)
		elif vehicleType.lower() == "truck":
			self.vehicle = vehicle.Truck(self)
		elif vehicleType.lower() == "motorcycle":
			self.vehicle = vehicle.Motorcycle(self)
		elif vehicleType.lower() == "bicycle":
			self.vehicle = vehicle.Bicycle(self)
		else:
			print(msgHeader + "Could not initialise Agent " + self.ID + " with vehicle type '" + vehicleType + "'.")
			self.vehicle = vehicle.Car(self)

		self.worldKnowledge = {}

		self.strategy = None
		if strategyFile is not None and strategyFile != "Manual": # Do not look for 'manual' strategy file
			try:
				self.strategy = import_file("strategy", strategyFile)
				print(msgHeader + "Successfully loaded the strategy file for Agent " + self.ID + ".")
			except:
				print(msgHeader + "Could not load the strategy file for Agent " + self.ID + ". (Fatal)")
				exit()
		elif strategyFile is not None and strategyFile == "Manual": # Mark agent as a manual car
			self.strategy = "Manual"
			print(msgHeader + "Manual agent successfully initialised.")

		self.stopped = False

	def start(self):
		if self.strategy == "Manual":
			t_process = Thread(target=self.manual_control)
			t_process.daemon = True
			t_process.start()
			return self
		else:
			t_process = Thread(target=self.update)
			t_process.daemon = True
			t_process.start()
			return self

	def update(self):
		while True:
			if self.stopped or not self.strategy:
				return
			self.strategy.make_decision(self)
			time.sleep(0.2)

	def stop(self):
		self.vehicle.stop()
		self.stopped = True

	def update_world_knowledge(self, worldData):
		for key in self.worldKnowledge:
			if key in worldData:
				self.worldKnowledge[key] = worldData[key]

	def aim_speed(self, speed):
		cspeed = self.vehicle.current_speed
		if (cspeed is None):
			cspeed = 0
		if (speed > cspeed):
			diff = speed - cspeed
			if (diff > self.vehicle.max_acceleration):
				diff = self.vehicle.max_acceleration
			self.vehicle.set_speed(cspeed + diff)
		else:
			diff = cspeed - speed
			if (diff > self.vehicle.max_deceleration):
				diff = self.vehicle.max_deceleration
			self.vehicle.set_speed(cspeed - diff)

	def aim_angle(self, angle):
		cangle = self.vehicle.orientation
		if (cangle is None):
			cangle = 0
		diff = int(math.fabs(angle - cangle))
		if (diff > 180):
			diff = 360 - diff
			if (cangle < angle):
				da = -diff
			else:
				da = diff
		else:
			if (cangle < angle):
				da = diff
			else:
				da = -diff
		self.vehicle.set_angle(da // 3)

	def get_vector_between_points(self, x1, y1, x2, y2):
		if (x1 != None and y1 != None):
			dx = x2 - x1
			dy = y2 - y1
			dist = int(math.sqrt(dx * dx + dy * dy))
			theta = 0
			if (dx != 0):
				theta = math.atan(dy / dx) * (180 / math.pi)
			if (dx == 0):
				if (dy <= 0):
					theta = 0
				else:
					theta = 180
			elif (dy == 0):
				if (dx < 0):
					theta = 270
				else:
					theta = 90
			elif (dx > 0 and dy > 0):
				theta = theta + 90
			elif (dx > 0 and dy < 0):
				theta = theta + 90
			elif (dx < 0 and dy > 0):
				theta = theta + 270
			elif (dx < 0 and dy < 0):
				theta = theta + 270
			return (dist, theta)
		return (None, None)

	# Return Distance and Angle to current waypoint. Angle must be degrees clockwise from north
	def get_vector_to_waypoint(self):
		if (self.vehicle.position[0] != None and self.vehicle.position[1] != None):
			wpi = self.get_waypoint_index()
			if (wpi != None):
				if (self.worldKnowledge['waypoints'] != []):
					x1 = self.vehicle.position[0]
					y1 = self.vehicle.position[1]
					x2 = self.worldKnowledge['waypoints'][wpi][0]
					y2 = self.worldKnowledge['waypoints'][wpi][1]
					return self.get_vector_between_points(x1, y1, x2, y2)
		return (None, None)

	# Return current waypoint index
	def get_waypoint_index(self):
		return self.worldKnowledge['waypoint_index']

	# Set current waypoint index
	def set_waypoint_index(self, wp):
		mmax = len(self.worldKnowledge['waypoints']) - 1
		if (wp > mmax):
			wp = 0
		if (wp < 0):
			wp = mmax
		self.worldKnowledge['waypoint_index'] = wp
		
	def manual_control(self):
		joystick = pygame.joystick.Joystick(0)
		prev_axes = (0, 0) # Use to check if axis input has been made
		prev_buttons =  (0, 0, 0, 0, 0, 0, 0, 0)# Use to check if button has been pressed
		while True:
			if self.stopped:
				return
			else: 
				# Get gamepad button and axis states
				left_stick = joystick.get_axis(0)
				left_trigger = joystick.get_axis(2)
				right_trigger = joystick.get_axis(5)
				left_bumper = joystick.get_button(4)
				right_bumper = joystick.get_button(5)
				A = joystick.get_button(0)
				B = joystick.get_button(1)
				X = joystick.get_button(2)
				Y = joystick.get_button(3)
				L3 = joystick.get_button(8)
				R3 = joystick.get_button(9)
				axes = (left_stick, left_trigger, right_trigger)
				buttons = (left_bumper, right_bumper, A, B, X, Y, L3, R3)
				
				if axes != prev_axes:
					self.vehicle.set_angle(int(64*left_stick)) # Left stick controls left/right steering)
					# If both right trigger and left trigger are pressed simultaneously, right trigger takes precedence
					if right_trigger >= -0.8:
						self.vehicle.set_speed(int(63*((right_trigger+1)/2))) # Set forward speed according to right trigger press
					elif left_trigger >= -0.8:	
						self.vehicle.set_speed(int(-64*((left_trigger+1)/2))) # Set backward speed according to left trigger press
					elif right_trigger < -0.8 and left_trigger < -0.8: # If neither trigger is being pressed, stop the car
						self.vehicle.stop()
					prev_axes = axes
				if buttons != prev_buttons:
					if X and not self.vehicle.horn_active:	# X activates horn
						self.vehicle.horn_on()
					if not X and self.vehicle.horn_active:	# Deactivate horn when X is released
						self.vehicle.horn_off()
					if left_bumper: # Left bumper toggles left indicator
						if self.vehicle.left_signal_active:
							self.vehicle.left_signal_off()
						else:
							self.vehicle.left_signal_on()
					if right_bumper: # Right bumper toggles right indicator
						if self.vehicle.right_signal_active:
							self.vehicle.right_signal_off()
						else:
							self.vehicle.right_signal_on()
					if Y: # Y toggles headlights
						if self.vehicle.headlights_active:
							self.vehicle.headlights_off()
						else:
							self.vehicle.headlights_on()
					if B: # B toggles police siren
						if self.vehicle.police_siren_active:
							self.vehicle.police_siren_off()
						else:
							self.vehicle.police_siren_on()

def import_file(full_name, path):
	from importlib import util
	spec = util.spec_from_file_location(full_name, path)
	mod = util.module_from_spec(spec)
	spec.loader.exec_module(mod)
	return mod
