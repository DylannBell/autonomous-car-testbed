import pygame
from pygame.locals import *
import math
import csv
from os import listdir
from os.path import isfile
from constants import *

msgHeader = "[DISPLAY]: "


class Display():
	def __init__(self):
		self.DEBUG = False

		pygame.init()
		self.screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT), pygame.FULLSCREEN)
		self.font = pygame.font.SysFont('Arial', int(DISPLAY_WIDTH / 50))
		self.background_image = None
		self.default_text_position = (DISPLAY_WIDTH / 1.5, DISPLAY_HEIGHT / 1.2)

		# Hide mouse.
		pygame.mouse.set_visible(False)

		# Initialise controller.
		pygame.joystick.init()
		if (pygame.joystick.get_count() < 1):
			print(msgHeader + "No gamepad detected.")
			exit()
		self.joystick = pygame.joystick.Joystick(0)
		self.joystick.init()
		self.debug_button_last = 0
		self.exit_button_last = 0

		self.done = False

		print(msgHeader + "Initialisation complete.")

	def splash_screen(self):
		self.screen.fill((0, 0, 0))
		text = self.font.render("AUTONOMOUS VEHICLE TESTBED", True, (255, 255, 255))
		self.screen.blit(text, self.default_text_position)
		pygame.display.flip()

	def calibration_screen(self, corners=None):
		raw_img = pygame.image.load(CALIBRATION_IMG_PATH)
		scale_factor = DISPLAY_WIDTH / raw_img.get_rect().size[0]
		scaled_img = pygame.transform.rotozoom(raw_img, 0, scale_factor)
		self.screen.blit(scaled_img, (0, 0))
		if corners is not None:
			#tl = corners[0][0]
			#tr = corners[0][1]
			#bl = corners[0][2]
			#br = corners[0][3]
			#pygame.draw.line(self.screen, (255, 0, 0), tl, tr, 5)
			#pygame.draw.line(self.screen, (255, 0, 0), tl, bl, 5)
			#pygame.draw.line(self.screen, (255, 0, 0), bl, br, 5)
			#pygame.draw.line(self.screen, (255, 0, 0), br, tr, 5)

			tl = corners[0]
			tr = corners[1]
			bl = corners[2]
			br = corners[3]
			pygame.draw.line(self.screen, (0, 255, 0), tl, tr, 5)
			pygame.draw.line(self.screen, (0, 255, 0), tl, bl, 5)
			pygame.draw.line(self.screen, (0, 255, 0), bl, br, 5)
			pygame.draw.line(self.screen, (0, 255, 0), br, tr, 5)
			text = self.font.render("Calibrated successfully.", True, (0, 0, 0))
		else:
			text = self.font.render("Calibrating camera perspective...", True, (0, 0, 0))
		self.screen.blit(text, self.default_text_position)
		pygame.display.flip()

	def connecting_screen(self):
		self.screen.fill((255, 255, 255))
		text = self.font.render("Connecting to cars...", True, (0, 0, 0))
		self.screen.blit(text, self.default_text_position)
		pygame.display.flip()

	def identifying_screen(self, agents):
		self.screen.fill((255, 255, 255))
		cellWidth = int(DISPLAY_WIDTH / 12)
		cellHeight = int(DISPLAY_HEIGHT / 8)
		xOffset = int(DISPLAY_WIDTH / 8)
		top = int(DISPLAY_HEIGHT / 1.3)
		for agent in agents:
			pygame.draw.rect(self.screen, (0, 0, 0),
							 Rect(xOffset, top, cellWidth, cellHeight), 4)
			id = self.font.render(str(agent.ID), True, (0, 0, 0))
			rect = id.get_rect(center=(xOffset + cellWidth / 2, top - cellHeight / 10))
			self.screen.blit(id, rect)
			xOffset += cellWidth + int(DISPLAY_WIDTH / 14)

		text = self.font.render("Place each car in its cell.", True, (0, 0, 0))
		self.screen.blit(text, self.default_text_position)
		pygame.display.flip()

	# Create image from raw world data.
	def generate_image(self, world_data):
		if self.background_image is None:
			raw_img = world_data["map"]
			scale_factor = DISPLAY_WIDTH / raw_img.get_rect().size[0]
			scaled_img = pygame.transform.rotozoom(raw_img, 0, scale_factor)
			self.background_image = scaled_img
		self.screen.blit(self.background_image, (0, 0))
		if self.DEBUG:
			yOffset = 0
			for vehicle in world_data['vehicles']:
				try:
					if vehicle.position is None or vehicle.orientation is None:
						continue
					pos = vehicle.position
					angle = vehicle.orientation - 90
					pygame.draw.circle(self.screen, (0, 0, 0), pos, 50, 1)
					angleLine = (
					pos[0] + 200 * math.cos(math.radians(angle)), pos[1] + 200 * math.sin(math.radians(angle)))
					pygame.draw.line(self.screen, (0, 0, 0), pos, angleLine, 5)
					text = self.font.render(str(vehicle.owner.ID) + ": " + str(pos) + ", " + str(angle), True,
											(0, 0, 0))
					self.screen.blit(text, (50, yOffset))
					yOffset += 30
					marker = self.font.render(str(vehicle.owner.ID), True, (0, 0, 0))
					self.screen.blit(marker, pos)
				except Exception as e:
					print(str(e))
					
			for waypoint in world_data['waypoints']:
				pygame.draw.circle(self.screen, (256, 0, 0), waypoint, 10, 1)
				

	def error_message(self, message):
		self.screen.fill((0, 0, 0))
		text = self.font.render(message, True, (255, 0, 0))
		self.screen.blit(text, self.default_text_position)
		pygame.display.flip()

	def handle_input(self):
		for event in pygame.event.get():
			if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
				self.done = True
		if self.joystick.get_button(8) and not self.debug_button_last:
			self.DEBUG = not self.DEBUG
		if self.joystick.get_button(1) and not self.exit_button_last:
			self.done = True
		self.debug_button_last = self.joystick.get_button(8)
		self.exit_button_last = self.joystick.get_button(1)

	# Update the world display.
	def update(self, world_data):
		self.handle_input()
		if self.done: return
		self.generate_image(world_data)
		pygame.display.flip()


	"""
	My apologies for the following code! It was done in a hurry post-exams to try to
	tie everything together for you guys. I definitely advise doing a proper menu if
	you get the time.
	-- Michael Finn :)
	"""

	def menu(self):
		# Get maps from folder.
		maps = []
		for folder in listdir(MAPS_DIR):
			if not isfile(folder):
				map = {}
				width, height = None, None
				for file in listdir(os.path.join(MAPS_DIR, folder)):
					if ".png" in file:
						path = os.path.join(MAPS_DIR, folder, file).replace("\\", "/")
						map["Name"] = path.split("/")[-1].split(".")[0]
						map["Image"] = pygame.image.load(path)
						width, height = map["Image"].get_rect().size
				for file in listdir(os.path.join(MAPS_DIR, folder)):
					if ".txt" in file:
						waypoints_file = os.path.join(MAPS_DIR, folder, file).replace("\\", "/")
						waypoints = []
						xScale = DISPLAY_WIDTH / width
						yScale = DISPLAY_HEIGHT / height
						with open(waypoints_file, "r") as f:
							for line in f:
								x_str, y_str = line.split(" ")[:2]
								x = int(int(x_str) * xScale)
								y = int(int(y_str) * yScale)
								waypoints.append((x, y))
						map["Waypoints"] = waypoints
				if len(map) == 3:
					maps.append(map)
		if not maps:
			print(msgHeader + "Error: No maps in the map folder.")
			return False

		# Get strategies from folder.
		strategies = []
		for file in listdir(STRATEGIES_DIR):
			if ".py" in file:
				strategy = os.path.join(STRATEGIES_DIR, file).replace("\\", "/")
				strategies.append(strategy)
		if not strategies:
			print(msgHeader + "Error: No strategies in the strategy folder.")
			return False

		# Get cars.
		cars = []
		file = csv.DictReader(open(os.path.join(ZENWHEELS_DIR, 'cars.csv')))
		for car in file:
			cars.append({"ID": car["Bluetooth SSID"],
						 "Colour": car["Colour"],
						 "Type": "Robot",
						 "Vehicle": "Car",
						 "Strategy": strategies[0],
						 "Enabled": False})

		# Initialise menu.
		buttons = []
		map_button = Button(DISPLAY_WIDTH / 2 - DISPLAY_WIDTH / 6,
							DISPLAY_HEIGHT / 4 - DISPLAY_HEIGHT / 6,
							DISPLAY_WIDTH / 3,
							DISPLAY_HEIGHT / 3,
							maps=maps)
		buttons.append(map_button)
		car_button = Button(DISPLAY_WIDTH / 2 - DISPLAY_HEIGHT / 10,
							DISPLAY_HEIGHT / 1.6 - DISPLAY_HEIGHT / 10,
							DISPLAY_HEIGHT / 5,
							DISPLAY_HEIGHT / 5,
							cars=cars, strategies=strategies)
		buttons.append(car_button)
		start_button = Button(DISPLAY_WIDTH / 2 - DISPLAY_WIDTH / 12,
							DISPLAY_HEIGHT / 1.1 - DISPLAY_HEIGHT / 16,
							DISPLAY_WIDTH / 6,
							DISPLAY_HEIGHT / 8)
		start_button.is_start = True
		buttons.append(start_button)
		exit_button = Button(DISPLAY_WIDTH / 1.1 - DISPLAY_WIDTH / 16,
							DISPLAY_HEIGHT / 1.1 - DISPLAY_HEIGHT / 16,
							DISPLAY_HEIGHT / 8,
							DISPLAY_HEIGHT / 8)
		exit_button.is_exit = True
		buttons.append(exit_button)


		# Menu navigation.
		hovering_on = 0 # Make first button hovered over by default.
		prev_direction = (0, 0)
		prev_abxy = [0, 0, 0, 0]
		start = False
		exit = False
		while not start and not exit:
			self.screen.fill((0, 0, 0))
			for event in pygame.event.get():
				if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
					return False

			direction = self.joystick.get_hat(0)
			A = self.joystick.get_button(0)
			B = self.joystick.get_button(1)
			X = self.joystick.get_button(2)
			Y = self.joystick.get_button(3)
			abxy = [A, B, X, Y]

			if direction == prev_direction:
				pass
			elif direction == (0, -1) and hovering_on < len(buttons) - 1:
				if buttons[hovering_on].is_start:
					pass
				else:
					hovering_on += 1
			elif direction == (0, 1) and hovering_on > 0:
				if buttons[hovering_on].is_exit:
					pass
				else:
					hovering_on -= 1
			elif direction == (-1, 0):
				if buttons[hovering_on].is_exit:
					hovering_on -= 1
				else:
					buttons[hovering_on].previous()
			elif direction == (1, 0):
				if buttons[hovering_on].is_start:
					hovering_on += 1
				buttons[hovering_on].next()
			prev_direction = direction

			if prev_abxy != [0,0,0,0]:
				pass
			elif A:
				buttons[hovering_on].A()
				if buttons[hovering_on].is_start:
					start = True
				elif buttons[hovering_on].is_exit:
					exit = True
			elif B:
				buttons[hovering_on].B()
			elif X:
				buttons[hovering_on].X()
			elif Y:
				buttons[hovering_on].Y()
			prev_abxy = abxy

			for i, button in enumerate(buttons):
				if i == hovering_on:
					button.hover = True
				else:
					button.hover = False
				button.render(self.screen)

			enabled_cars = []
			for car in cars:
				if car["Enabled"]:
					enabled_cars.append(car["ID"])
			if enabled_cars:
				text_render = self.font.render("Enabled Cars:", True, (255,255,255))
				text_rect = text_render.get_rect(center=(DISPLAY_WIDTH / 6, DISPLAY_HEIGHT / 2))
				self.screen.blit(text_render, text_rect)
				yOffset = DISPLAY_HEIGHT / 30
				for ID in enabled_cars:
					car_text_render = self.font.render(ID, True, (100,120,255))
					car_text_rect = car_text_render.get_rect(center=(DISPLAY_WIDTH / 6, (DISPLAY_HEIGHT / 2) + yOffset))
					self.screen.blit(car_text_render, car_text_rect)
					yOffset += DISPLAY_HEIGHT / 30

			pygame.display.flip()

		if start:
			scenario_config = {}
			scenario_config["Map"] = maps[map_button.current]
			scenario_config["Active Cars"] = []
			for car in cars:
				if car["Enabled"]:
					scenario_config["Active Cars"].append(car)
			return scenario_config
		else:
			pygame.quit()
			return False


class Button:
	def __init__(self, x, y, w, h, maps=[], cars=[], strategies=[]):
		self.text = ""
		self.font = pygame.font.SysFont("Arial", int(DISPLAY_WIDTH / 50))

		self.maps = maps
		self.cars = cars
		self.current = 0

		self.strategies = strategies

		self.is_start = False
		self.is_exit = False

		self.x = int(x)
		self.y = int(y)
		self.w = int(w)
		self.h = int(h)

		self.left_arrow = pygame.transform.scale(pygame.image.load("media/left-arrow.png"),
											(int(self.w / 2), int(self.h / 2)))
		self.right_arrow = pygame.transform.scale(pygame.image.load("media/right-arrow.png"),
											 (int(self.w / 2), int(self.h / 2)))

		self.hover = False

	def next(self):
		self.current += 1
		if self.maps: length = len(self.maps) - 1
		else: length = len(self.cars) - 1
		if self.current > length:
			self.current = 0

	def previous(self):
		self.current -= 1
		if self.maps: length = len(self.maps) - 1
		else: length = len(self.cars) - 1
		if self.current < 0:
			self.current = length

	def A(self):
		if self.is_start:
			pass
		elif self.is_exit:
			pass
		elif self.cars:
			self.cars[self.current]["Enabled"] = True

	def B(self):
		if self.cars:
			self.cars[self.current]["Enabled"] = False

	def X(self):
		if self.cars:
			num = self.strategies.index(self.cars[self.current]["Strategy"]) - 1
			if num < 0:
				num = len(self.strategies) - 1
			self.cars[self.current]["Strategy"] = self.strategies[num]

	def Y(self):
		if self.cars:
			num = self.strategies.index(self.cars[self.current]["Strategy"]) + 1
			if num > len(self.strategies) - 1:
				num = 0
			self.cars[self.current]["Strategy"] = self.strategies[num]

	def render(self, screen):
		if self.hover:
			b_factor = int(self.w / 20)
			pygame.draw.rect(screen, (255,200,0), (self.x - int(b_factor/2), self.y - int(b_factor/2), self.w + b_factor, self.h + b_factor), 0)
			if not self.is_start and not self.is_exit:
				screen.blit(self.left_arrow, (self.x - self.w / 2, self.y + self.h / 4))
				screen.blit(self.right_arrow, (self.x + self.w, self.y + self.h / 4))

		if self.maps:
			button_img = pygame.transform.scale(self.maps[self.current]["Image"], (self.w, self.h))
			screen.blit(button_img, (self.x, self.y))
			if self.hover:
				map_text_render = self.font.render("Map:", True, (255,255,255))
				map_text_rect = map_text_render.get_rect(center=(self.x + self.w * 1.6, self.y + self.h / 3))
				screen.blit(map_text_render, map_text_rect)

				file_text_render = self.font.render(self.maps[self.current]["Name"], True, (255,0,255))
				file_text_rect = file_text_render.get_rect(center=(self.x + self.w * 1.6, self.y + self.h / 2))
				screen.blit(file_text_render, file_text_rect)

		elif self.cars:
			car = self.cars[self.current]
			colour = car["Colour"]
			if colour == "blue": c = (100,150,255)
			elif colour == "pink": c = (255,50,150)
			elif colour == "orange": c = (255,150,50)
			elif colour == "yellow": c = (255,255,0)
			elif colour == "green": c = (0,255,0)
			elif colour == "black": c = (0,0,0)
			elif colour == "red": c = (255,0,0)
			elif colour == "white": c = (255,255,255)
			else: c = (180,180,180)
			pygame.draw.rect(screen, c, (self.x, self.y, self.w, self.h), 0)
			self.text = car["ID"]

			if self.hover:
				status_text_render = self.font.render("Status:", True, (255,255,255))
				status_text_rect = status_text_render.get_rect(center=(self.x + self.w * 2.5, self.y + self.h / 12))
				screen.blit(status_text_render, status_text_rect)

				en_text_render = self.font.render("Enabled" if car["Enabled"] else "Not Enabled", True, (0,255,0) if car["Enabled"] else (255,0,0))
				en_text_rect = en_text_render.get_rect(center=(self.x + self.w *2.5, self.y + self.h / 4))
				screen.blit(en_text_render, en_text_rect)

				strat_text_render = self.font.render("Strategy File:", True, (255,255,255))
				strat_text_rect = strat_text_render.get_rect(center=(self.x + self.w *2.5, self.y + self.h / 1.5))
				screen.blit(strat_text_render, strat_text_rect)

				file_text_render = self.font.render(car["Strategy"].split("/")[-1], True, (0,0,255))
				file_text_rect = file_text_render.get_rect(center=(self.x + self.w *2.5, self.y + self.h / 1.2))
				screen.blit(file_text_render, file_text_rect)
		elif self.is_start:
			pygame.draw.rect(screen, (0,255,0), (self.x, self.y, self.w, self.h), 0)
			self.text = "Start"
		elif self.is_exit:
			pygame.draw.rect(screen, (255,0,0), (self.x, self.y, self.w, self.h), 0)
			self.text = "Exit"

		if (self.text != ""):
			if self.cars and self.cars[self.current]["Colour"] == "white":
				colour = (0, 0, 0)
			else:
				colour = (255, 255, 255)
			text_render = self.font.render(self.text, True, colour)
			text_rect = text_render.get_rect(center=(self.x + self.w / 2, self.y + self.h / 2))
			screen.blit(text_render, text_rect)
