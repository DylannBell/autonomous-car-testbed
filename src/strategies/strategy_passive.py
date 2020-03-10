"""
PASSIVE

Agent will navigate waypoints slowly,
stopping if a collision is imminent.
"""

import math, time

def make_decision(self):
	# Set up the agent's memory.
	if "vehicles" not in self.worldKnowledge.keys() \
			or "waypoints" not in self.worldKnowledge.keys() \
			or "current_waypoint" not in self.worldKnowledge.keys():
		self.worldKnowledge['vehicles'] = [] # Grab vehicles from World
		self.worldKnowledge['waypoints'] = []  # Grab waypoints from World
		self.worldKnowledge['dimensions'] = []  # Grab dimensions from World
		self.worldKnowledge['current_waypoint'] = None # New memory slot.
		return

	# If there are no waypoints, stop.
	if not self.worldKnowledge['waypoints']:
		self.vehicle.stop()
		return

	# If we don't know where we are, stop.
	if self.vehicle.position == None or self.vehicle.orientation == None:
		self.vehicle.stop()
		return

	# Get the closest waypoint if we don't have one yet.
	if self.worldKnowledge['current_waypoint'] == None:
		self.worldKnowledge['current_waypoint'] = get_next_waypoint(self)

	# Check positions of other cars.
	for vehicle in self.worldKnowledge['vehicles']:
		if vehicle.owner.ID == self.vehicle.owner.ID or vehicle.position == (None, None):
			continue
		# Get vectors to other cars.
		x1 = self.vehicle.position[0]
		y1 = self.vehicle.position[1]
		x2 = vehicle.position[0]
		y2 = vehicle.position[1]
		dist, angle = get_vector_between_points(x1, y1, x2, y2)
		cangle = self.vehicle.orientation
		diff = int(math.fabs(angle - cangle))
		if (diff > 180):
			diff = 360 - diff
		# If our nose is too close to another car, stop and complain.
		if dist < 50 and diff < 90:
			self.vehicle.stop()
			self.vehicle.horn_on()
			self.vehicle.headlights_on()
			time.sleep(1)
			self.vehicle.horn_off()
			self.vehicle.headlights_off()
			return

	# Find waypoint vector info
	wp_current = self.worldKnowledge['current_waypoint']
	wp_dist, wp_angle = get_vector_between_points(self.vehicle.position[0],
												  self.vehicle.position[1],
												  self.worldKnowledge['waypoints'][wp_current][0],
												  self.worldKnowledge['waypoints'][wp_current][1])
	if (wp_dist < 50): # If we are close enough to our waypoint, set our sights on the next one
		self.worldKnowledge['current_waypoint'] = get_next_waypoint(self)
	else: # Drive slowly towards current waypoint. Slow down drastically if we are not directed towards the waypoint.
		speed = 8
		car_angle = self.vehicle.get_orientation()
		a = int(math.fabs(car_angle - wp_angle))
		if (a > 180):
			a = 360 - a
			if (car_angle < wp_angle):
				da = -a
			else:
				da = a
		else:
			if (car_angle < wp_angle):
				da = a
			else:
				da = -a
		self.vehicle.set_angle(da // 2)
		self.vehicle.set_speed(speed)


def get_next_waypoint(self):
	current = self.worldKnowledge['current_waypoint']
	if current == None:
		closest = (0, 9999)
		for index, waypoint in enumerate(self.worldKnowledge['waypoints']):
			x1 = self.vehicle.position[0]
			y1 = self.vehicle.position[1]
			x2 = waypoint[0]
			y2 = waypoint[1]
			dist, theta = get_vector_between_points(x1, y1, x2, y2)
			if dist < closest[1]:
				closest = (index, dist)
		return closest[0]
	else:
		num_points = len(self.worldKnowledge['waypoints'])
		next = current + 1
		if next > num_points - 1:
			next = 0
		return next


def get_vector_between_points(x1, y1, x2, y2):
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
	return dist, theta
