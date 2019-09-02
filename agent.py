import time
import math
from threading import Thread
import vehicle


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
		if strategyFile is not None:
			try:
				self.strategy = import_file("strategy", strategyFile)
				print(msgHeader + "Successfully loaded the strategy file for Agent " + self.ID + ".")
			except:
				print(msgHeader + "Could not load the strategy file for Agent " + self.ID + ". (Fatal)")
				exit()

		self.stopped = False

	def start(self):
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


def import_file(full_name, path):
	from importlib import util
	spec = util.spec_from_file_location(full_name, path)
	mod = util.module_from_spec(spec)
	spec.loader.exec_module(mod)
	return mod
