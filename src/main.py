import time
from display import Display
from vision import Vision
from agent import Agent
from world import World
from zenwheels.comms import CarCommunicator
import datetime
from tracker.cone_detector import ConeDetector
import sys
import math


if __name__ == "__main__":
	msgHeader = "[MAIN]: "

	print("")
	print("========================================")
	print("         TABLETOP CAR SIMULATOR         ")
	print("========================================")
	print("")

	## SETUP USING ARGS
	timing = False
	args = sys.argv
	if len(args) > 1:

		# Run timing
		if args[1] == "timing":
            timing = True
            timeNow = datetime.datetime.now()
            filename = "logs/timing" + str(timeNow) + ".txt"
		
		if args[1] == "nogui":
			assert(len(args) == 3), "Please add a single car number!"


	# Initialise display.
	display = Display()
	# Display splash screen.
	display.splash_screen()

	# Initialise vision.
	vision = Vision()
	display.vision = vision # Pass vision to display so that it can be stopped on exit

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
				continue # Go back to main menu after 2 seconds
			display.agents = agents # Pass agent list to display so that agents can be stopped if the program exits
				
			manual_cars = 0 # Check how many manual cars are enabled, show error if more than 1 has been enabled
			for agent in agents:
				if agent.strategy == "Manual":
					manual_cars += 1
			if manual_cars > 1:
				errorMsg = msgHeader + ">1 manual cars enabled."
				print(errorMsg)
				display.error_message(errorMsg)
				time.sleep(2)
				continue
			
			if display.user_defined:
				print(msgHeader+"Detecting cones.")
				display.cone_recognition_screen(True)
				cone_detector = ConeDetector()
				if display.wait_for_confirmation():
					display.cone_recognition_screen()
					cones = vision.getCones()
					newWaypoints = []
					conePairs = []
					# Track-Building Algorithm
					while cones:
						currentCone = cones.pop(0)
						minDist = 99999				# Arbitrarily large number
						pairedIndex = 1
						for posPair in cones:
							currentDist = math.sqrt((currentCone[0] - posPair[0])**2 + (currentCone[1] - posPair[1])**2)
							if minDist > currentDist:
								minDist = currentDist
								pairedIndex = cones.index(posPair)
						conePairs.append((currentCone, cones[pairedIndex]))
						newWaypoints.append((round((currentCone[0] + cones[pairedIndex][0])/2*1.6), round((currentCone[1] + cones[pairedIndex][1])/2*1.6)))
						cones.pop(pairedIndex)
					newWaypoints.sort(key=lambda x: x[0])
					new_newWaypoints = []  # 新list

					while newWaypoints:  # newWaypoints不为空
						if len(new_newWaypoints) == 0:
							# 从第一个坐标A开始，放进新list
							point = newWaypoints.pop(0)
							new_newWaypoints.append(point)
						else:
							last_point = new_newWaypoints[-1]  # 上一个点A

							min_distance, min_point = 1e10, None
							for point in newWaypoints:  # 遍历newWaypoints，找到和上一个点A距离最小的点B min_point
								this_distance = (point[0] - last_point[0]) ** 2 + (point[1] - last_point[1]) ** 2
								if this_distance < min_distance:
									min_distance = this_distance
									min_point = point

							new_newWaypoints.append(min_point)  # 找到与A最近的坐标B，放进新list
							newWaypoints.remove(min_point)  # 从Newwaypoints里删除坐标B
					display.add_waypoints(new_newWaypoints, scenario_config) # Add new waypoints to scenario_config
					world = World(agents, vehicles, scenario_config["Map"]["Image"], scenario_config["Map"]["Waypoints"]) # Update world
				else:
					continue
				
			else:
				world = World(agents, vehicles, scenario_config["Map"]["Image"], scenario_config["Map"]["Waypoints"])

			# Connect to selected cars.
			display.connecting_screen()
			success = comms.connectToCars(vehicles)
			if not success:
				errorMsg = msgHeader + "Could not connect to cars."
				print(errorMsg)
				display.error_message(errorMsg)
				time.sleep(2)
				continue # Go back to main menu after 2 seconds
			
			# Identify car locations.
			display.identifying_screen(agents)
			success = vision.identify(agents)
			if not success:
				errorMsg = msgHeader + "Could not locate all of the specified cars."
				print(errorMsg)
				display.error_message(errorMsg)
				time.sleep(2)
				continue # Go back to main menu after 2 seconds

			# Start tracking.
			print(msgHeader + "Starting tracking.")
			vision.start_tracking()


			# Main loop.
			print(msgHeader + "Entering main loop.")
			display.countdown(world.get_world_data())
			# Start agents.
			print(msgHeader + "Starting agents.")
			for agent in agents:
				agent.start()
			dt = datetime.datetime(2019, 1, 1)
			dt_time = dt.now().time() # Get current time
			start_time = datetime.timedelta(seconds=dt_time.second, milliseconds=dt_time.microsecond/1000, 
																			minutes=dt_time.minute, hours=dt_time.hour) 
			laps = []
			laps.append(start_time) # Store current time as lap 0
			display.race_started = True

			updates = 0
			# Total 100 frames time
			start = datetime.datetime.now()
			while True:
				s = ''

				# Time get car locations
				startTimeCarLocations = datetime.datetime.now()
				car_locations = vision.get_car_locations()
				world.update(car_locations)
				now = datetime.datetime.now()
				s += "\nCar locations time : "
				s += str((now - startTimeCarLocations).total_seconds())

				# Time lap
				startTimeLap = datetime.datetime.now()
				if display.lap:
					# If a lap has been completed, get the current time and store it as the next lap
					dt_time = dt.now().time()
					current_time = datetime.timedelta(seconds=dt_time.second, milliseconds=dt_time.microsecond/1000,                                                                                          minutes=dt_time.minute, hours=dt_time.hour)
					laps.append(current_time - start_time)
				now = datetime.datetime.now()
				s += "\nLap time : "
				s += str((now - startTimeLap).total_seconds())

				# Time display
				startTimeDisplay = datetime.datetime.now()
				display.lap = False # Reset lap trigger
				display.update(world.get_world_data(), laps)
				now = datetime.datetime.now()
				s += "\nDisplay time : "
				s += str((now - startTimeDisplay).total_seconds())

				if display.done:
					break

				if display.race_complete:
					######## Do something when the race is finished - e.g. splash screen showing lap times, leaderboard, etc. #########
					display.race_complete = False
					display.race_started = False
					time.sleep(3)
					break

				# Time update agents
				startTimeAgent = datetime.datetime.now()
				for agent in agents:
					agent.update_world_knowledge(world.get_world_data())
				now = datetime.datetime.now()
				s += "\nAgent time : "
				s += str((now - startTimeAgent).total_seconds())

				# Do timing
                updates += 1
				if timing:
					print (s)
					endTime = datetime.datetime.now()
					timingFile = open(filename, "a+")
					s += "Timing update lap " + str(updates) + " complete."
					timingFile.write(s)
					s= ""
					if updates == 100:
                        now = datetime.datetime.now()
                        s += "\nTiming Finish: 100 Laps : "
                        totalTime = (now - start).total_seconds()
                        s += str(totalTime)
                        averageTime = totalTime / 100
                        s += "\nAverage Frame Time: "
                        s += str(averageTime)
                        timingFile.write(s)
                        timing = False							
				
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
	print(msgHeader + "Stopping camera.")
	vision.cam.stop_camera()
	print(msgHeader + "Camera stopped.")

	print(msgHeader + "Exiting simulator.")
	sys.exit(0)

