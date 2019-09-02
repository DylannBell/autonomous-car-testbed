"""
STRATEGY_KEEPAWAY

Agent tries to keep away from the walls.
"""

def make_decision(self):
	if "dimensions" not in self.worldKnowledge.keys():
		self.worldKnowledge['dimensions'] = None
		return

	self.vehicle.set_speed(10)

	width, height = self.worldKnowledge['dimensions']

	TOO_FAR_NORTH = self.vehicle.position[1] - (height / 4) < 0
	TOO_FAR_EAST = self.vehicle.position[0] + (width / 4) > width
	TOO_FAR_SOUTH = self.vehicle.position[1] + (height / 4) > height
	TOO_FAR_WEST = self.vehicle.position[0] - (width / 4) < 0

	if TOO_FAR_NORTH or TOO_FAR_EAST or TOO_FAR_SOUTH or TOO_FAR_WEST:
		self.vehicle.set_angle(40)
		self.vehicle.headlights_on()
	else:
		self.vehicle.set_angle(0)
		self.vehicle.headlights_off()