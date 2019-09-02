import time
from display import Display
from vision import Vision
from agent import Agent
from world import World
from zenwheels.comms import CarCommunicator


if __name__ == "__main__":
	msgHeader = "[MAIN]: "

	print("")
	print("========================================")
	print("         TABLETOP CAR SIMULATOR         ")
	print("========================================")
	print("")

	# Initialise display.
	display = Display()
	# Display splash screen.
	display.splash_screen()

	# Initialise vision.
	vision = Vision()

	# Initialise car comms.
	comms = CarCommunicator()

	# Calibrate once at the beginning.
	display.calibration_screen()
	tries = 5
	corners = None
	for i in range(tries):
		corners = vision.calibrate()
		if corners is not None:
			break
	if corners is None:
		errorMsg = msgHeader + "Could not calibrate."
		print(errorMsg)
		display.error_message(errorMsg)
		time.sleep(2)
	else:
		display.calibration_screen(corners=corners)
		time.sleep(2)

		while True:
			display.done = False

			# Menu.
			scenario_config = display.menu()
			if not scenario_config:
				break

			# Scenario initialisation.
			agents = []
			vehicles = []
			for car_parameters in scenario_config["Active Cars"]:
				agent = Agent(car_parameters["ID"], agentType=car_parameters["Type"],
							  vehicleType=car_parameters["Vehicle"], strategyFile=car_parameters["Strategy"])
				agents.append(agent)
				vehicles.append(agent.vehicle)
			if not agents:
				errorMsg = msgHeader + "No cars enabled."
				print(errorMsg)
				display.error_message(errorMsg)
				time.sleep(2)
				break

			world = World(agents, vehicles, scenario_config["Map"]["Image"], scenario_config["Map"]["Waypoints"])

			# Connect to selected cars.
			display.connecting_screen()
			success = comms.connectToCars(vehicles)
			if not success:
				break

			# Identify car locations.
			display.identifying_screen(agents)
			success = vision.identify(agents)
			if not success:
				errorMsg = msgHeader + "Could not locate all of the specified cars."
				print(errorMsg)
				display.error_message(errorMsg)
				time.sleep(2)
				break

			# Start tracking.
			print(msgHeader + "Starting tracking.")
			vision.start_tracking()

			# Start agents.
			print(msgHeader + "Starting agents.")
			for agent in agents:
				agent.start()

			# Main loop.
			print(msgHeader + "Entering main loop.")
			while True:
				car_locations = vision.get_car_locations()
				world.update(car_locations)
				display.update(world.get_world_data())
				if display.done:
					break

				for agent in agents:
					agent.update_world_knowledge(world.get_world_data())
			print(msgHeader + "Exited main loop.")

			# Stop agents.
			print(msgHeader + "Stopping agents.")
			for agent in agents:
				agent.stop()

			# Stop tracking.
			print(msgHeader + "Stopping tracking.")
			vision.stop_tracking()

			print(msgHeader + "Exiting scenario.")

	# Stop camera.
	vision.cam.stop_camera()

	print(msgHeader + "Exiting simulator.")

