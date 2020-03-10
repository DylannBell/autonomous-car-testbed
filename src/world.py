from constants import *


msgHeader = "[WORLD]: "


class World():
	def __init__(self, agents, vehicles, map, waypoints):
		self.world_data = {'agents': agents,
						   'vehicles': vehicles,
						   'dimensions': (DISPLAY_WIDTH, DISPLAY_HEIGHT),
						   'map': map,
						   'waypoints': waypoints}
		print(msgHeader + "Initialisation complete.")

	# Update the world state.
	def update(self, car_locations):
		for known_vehicle in self.world_data['vehicles']:
			updated = False
			for observed_car in car_locations:
				if observed_car['ID'] == known_vehicle.owner.ID:
					known_vehicle.position = observed_car['position']
					known_vehicle.orientation = observed_car['orientation']
					updated = True
					break
			if not updated:
				known_vehicle.position = None
				known_vehicle.orientation = None
		print(self.world_data)

	def get_world_data(self):
		return dict(self.world_data)
