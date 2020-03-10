import pygame
from pygame.locals import *
import math
import csv
from os import listdir
from os.path import isfile
from constants import *
import sys
import datetime
import time

msgHeader = "[DISPLAY]: "


class Display():
    def __init__(self):
        self.DEBUG = False

        pygame.init()
        self.screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT), pygame.FULLSCREEN)
        self.background_image = None
        self.default_text_position = (DISPLAY_WIDTH / 1.5, DISPLAY_HEIGHT / 1.2)
        self.font_general = pygame.font.SysFont('Arial', int(DISPLAY_WIDTH / 50)) # Font for general text
        self.font_timer = pygame.font.SysFont('Arial', int(DISPLAY_WIDTH / 30), True) # Font for timer text
        self.font_timer2 = pygame.font.SysFont('Arial', int(DISPLAY_WIDTH / 50), True) # Font for secondary timer text
        self.font_countdown = pygame.font.SysFont('Arial', int(DISPLAY_WIDTH / 2), True) # Font for countdown text
        self.race_started = False
        self.lap = False
        self.race_complete = False
        self.finish_time = None
        self.manual_mode = False
        self.gamepad = False
        self.user_defined = False
        self.blank_image = None
        self.agents = None # Enable stopping of agents on exit
        self.vision = None # Enable stopping of vision system on exit

        # Hide mouse.
        pygame.mouse.set_visible(False)

        # Initialise controller.
        pygame.joystick.init()
        if (pygame.joystick.get_count() < 1):
            print(msgHeader + "No gamepad detected.")
        else:
            self.gamepad = True
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            print(msgHeader + "Gamepad initialised.")
            self.debug_button_last = 0
            self.exit_button_last = 0

            self.done = False

        print(msgHeader + "Initialisation complete.")

    def splash_screen(self):
        self.screen.fill((0, 0, 0))
        text = self.font_general.render("AUTONOMOUS VEHICLE TESTBED", True, (255, 255, 255))
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
            text = self.font_general.render("Calibrated successfully.", True, (0, 0, 0))
        else:
            text = self.font_general.render("Calibrating camera perspective...", True, (0, 0, 0))
        self.screen.blit(text, self.default_text_position)
        pygame.display.flip()

    def connecting_screen(self):
        self.screen.fill((255, 255, 255))
        text = self.font_general.render("Connecting to cars...", True, (0, 0, 0))
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
            id = self.font_general.render(str(agent.ID), True, (0, 0, 0))
            rect = id.get_rect(center=(xOffset + cellWidth / 2, top - cellHeight / 10))
            self.screen.blit(id, rect)
            xOffset += cellWidth + int(DISPLAY_WIDTH / 14)

        text = self.font_general.render("Place each car in its cell.", True, (0, 0, 0))
        self.screen.blit(text, self.default_text_position)
        pygame.display.flip()

    # Create image from raw world data.
    def generate_image(self, world_data, laps):
        raw_img = world_data["map"]
        scale_factor = DISPLAY_WIDTH / raw_img.get_rect().size[0]
        scaled_img = pygame.transform.rotozoom(raw_img, 0, scale_factor)
        self.background_image = scaled_img
        self.screen.blit(self.background_image, (0, 0))
        dt = datetime.datetime(2019, 1, 1) # Parameters don't matter, just used to get current date/time
        dt = dt.now().time() # Get current time
        current_time = datetime.timedelta(seconds=dt.second, milliseconds=dt.microsecond/1000, 
                                        minutes=dt.minute, hours=dt.hour)
        time_elapsed = current_time - laps[0]
        if self.race_complete and self.finish_time == None:
            self.finish_time = time_elapsed # Store finish time
            time_text = self.font_timer.render(str(self.finish_time), True, (255, 0, 0))
            self.screen.blit(time_text, (800, 50))
        elif self.race_complete:
            time_text = self.font_timer.render(str(self.finish_time), True, (255, 0, 0))
            self.screen.blit(time_text, (800, 50))
        else:
            time_text = self.font_timer.render(str(time_elapsed), True, (255, 0, 0)) # Render elapsed time on screen
            self.screen.blit(time_text, (800, 50))
        lap_y = 90 # Y coordinate for lap time text placement
        lap_count = 1
        for lap in laps[1:]:
            lap_text = self.font_timer2.render('Lap '+str(lap_count)+' - '+str(lap), True, (255, 0, 0))
            self.screen.blit(lap_text, (825, lap_y))
            lap_y += 25
            lap_count += 1
            
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
                    text = self.font_general.render(str(vehicle.owner.ID) + ": " + str(pos) + ", " + str(angle), True,
                                            (0, 0, 0))
                    self.screen.blit(text, (50, yOffset))
                    yOffset += 30
                    marker = self.font_general.render(str(vehicle.owner.ID), True, (0, 0, 0))
                    self.screen.blit(marker, pos)
                except Exception as e:
                    print(str(e))
            for wp in world_data['waypoints']:
                try:
                    if wp is None:
                        continue
                    pygame.draw.circle(self.screen, (255,0,0), wp, 10, 1)
                except Exception as e:
                    print(str(e))

    # Draw the cones and waypoints
    def draw_track(self, conePairs):
        for pair in conePairs:
            try:
                if pair is None:
                    continue
                pygame.draw.circle(self.screen, (0, 255, 0), pair[0], 10, 1)
                pygame.draw.circle(self.screen, (0, 255, 0), pair[1], 10, 1)
                pygame.draw.line(self.screen, (255, 0, 0), pair[0], pair[1], 1)
                pygame.draw.circle(self.screen, (0, 0, 0), (pair[0] + pair[1])/2, 10, 1)
            except Exception as e:
                print(str(e))

    def error_message(self, message):
        self.screen.fill((0, 0, 0))
        text = self.font_general.render(message, True, (255, 0, 0))
        self.screen.blit(text, self.default_text_position)
        pygame.display.flip()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.done = True
            elif event.type == pygame.KEYDOWN and event.key == K_ESCAPE:
                if (event.mod & pygame.KMOD_SHIFT):
                    pygame.quit()
                    print(msgHeader+"Keyboard interrupt, exiting program")
                    if self.agents is not None:
                        print(msgHeader + "Stopping agents.")
                        for agent in self.agents:
                            agent.stop()
                    if self.vision is not None:
                        print(msgHeader + "Stopping tracking.")
                        self.vision.stop_tracking()
                        print(msgHeader + "Stopping camera.")
                        self.vision.cam.stop_camera()
                    sys.exit()
                else: self.done = True
            elif self.race_started and event.type == KEYDOWN and event.key == K_SPACE:
                if (event.mod & pygame.KMOD_SHIFT):
                    self.race_complete = True
                else: self.lap = True
        if self.gamepad:
            if self.joystick.get_button(8) and not self.debug_button_last:
                    self.DEBUG = not self.DEBUG
            self.debug_button_last = self.joystick.get_button(8)
            if not self.manual_mode: # If in manual mode, disable controller exit input
                if self.joystick.get_button(1) and not self.exit_button_last:
                    self.done = True
                self.exit_button_last = self.joystick.get_button(1)
    
    def wait_for_confirmation(self):
        print(msgHeader+"Waiting for confirmation.")
        time.sleep(0.5)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == K_RETURN:
                    return True
                elif event.type == pygame.KEYDOWN and event.key == K_ESCAPE: # Allow program exit using SHIFT+ESCAPE
                    if (event.mod & pygame.KMOD_SHIFT):
                        pygame.quit()
                        print(msgHeader+"Keyboard interrupt, exiting program")
                        if self.agents is not None:
                            print(msgHeader + "Stopping agents.")
                            for agent in self.agents:
                                agent.stop()
                        if self.vision is not None:
                            print(msgHeader + "Stopping tracking.")
                            self.vision.stop_tracking()
                            print(msgHeader + "Stopping camera.")
                            self.vision.cam.stop_camera()
                        sys.exit() 
                    else:
                        return False
            if self.gamepad:
                if self.joystick.get_button(0):
                    return True
                elif self.joystick.get_button(1):
                    return False

    # Update the world display.
    def update(self, world_data, laps):
        self.handle_input()
        if self.done:
            return
        self.generate_image(world_data, laps)
        pygame.display.flip()
        
    # Clear the event queue to stop input buffering
    def clear_events(self):
        pygame.event.clear()

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
                        # Store blank image for use later
                        if map["Name"] == "map_blank":
                            self.blank_image = map["Image"]
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
        if self.gamepad:
            strategies.append("Manual") # Add Manual option to strategy files if a gamepad is connected

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
        UI = False
        while not start and not exit:
            self.screen.fill((0, 0, 0))
            for event in pygame.event.get():
                if event.type == QUIT or event.type == KEYDOWN:
                    if (event.mod & pygame.KMOD_SHIFT) and event.key == K_ESCAPE: # SHIFT+ESCAPE quits program
                        pygame.quit()
                        print(msgHeader+"Keyboard interrupt, exiting program")
                        if self.agents is not None:
                            print(msgHeader + "Stopping agents.")
                            for agent in self.agents:
                                agent.stop()
                        if self.vision is not None:
                            print(msgHeader + "Stopping tracking.")
                            self.vision.stop_tracking()
                            print(msgHeader + "Stopping camera.")
                            self.vision.cam.stop_camera()
                        sys.exit() 
                        return False
                        
                    if event.key == K_RETURN: # ENTER functions the same as gamepad A
                        buttons[hovering_on].A()
                        if buttons[hovering_on].is_start:
                            start = True
                        elif buttons[hovering_on].is_exit:
                            exit = True
                    elif event.key == K_ESCAPE: # ESC functions the same as gamepad B
                        buttons[hovering_on].B()
                        
                    elif event.key == K_BACKSPACE: # BACKSPACE functions the same as gamepad X
                        buttons[hovering_on].X()
                        
                    elif event.key == K_SPACE: # SPACE functions the same as gamepad Y
                        buttons[hovering_on].Y()
                    # Enable arrow keys as directional inputs
                    elif event.key == K_DOWN and hovering_on < len(buttons) - 1:
                        if buttons[hovering_on].is_start:
                            pass
                        else:
                            hovering_on += 1
                    
                    elif event.key == K_UP and hovering_on > 0:
                        if buttons[hovering_on].is_exit:
                            pass
                        else:
                            hovering_on -= 1
                    
                    elif event.key == K_LEFT:
                        if buttons[hovering_on].is_exit:
                            hovering_on -= 1
                        else:
                            buttons[hovering_on].previous()
                    
                    elif event.key == K_RIGHT:
                        if buttons[hovering_on].is_start:
                            hovering_on += 1
                        buttons[hovering_on].next()

            if self.gamepad:
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
                text_render = self.font_general.render("Enabled Cars:", True, (255,255,255))
                text_rect = text_render.get_rect(center=(DISPLAY_WIDTH / 6, DISPLAY_HEIGHT / 2))
                self.screen.blit(text_render, text_rect)
                yOffset = DISPLAY_HEIGHT / 30
                for ID in enabled_cars:
                    car_text_render = self.font_general.render(ID, True, (100,120,255))
                    car_text_rect = car_text_render.get_rect(center=(DISPLAY_WIDTH / 6, (DISPLAY_HEIGHT / 2) + yOffset))
                    self.screen.blit(car_text_render, car_text_rect)
                    yOffset += DISPLAY_HEIGHT / 30

            pygame.display.flip()

        if start:
            if maps[map_button.current]["Name"] == "map_user": # If the user-defined option has been selected
                self.user_defined = True
                new_map = {} # Build new map
                new_map["Name"] = "map_user"
                new_map["Image"] = self.blank_image
                scenario_config = {}
                scenario_config["Map"] = new_map
                scenario_config["Active Cars"] = []
                for car in cars:
                    if car["Enabled"]:
                        scenario_config["Active Cars"].append(car)
                        if car["Strategy"] == "Manual":
                            self.manual_mode = True # If any enabled car is in manual mode, set manual_mode to true
                return scenario_config
            else:
                self.user_defined = False # Reset user_defined indicator if a preset map is chosen
                print(msgHeader+"Rebuilding scenario_config")
                scenario_config = {}
                scenario_config["Map"] = maps[map_button.current]
                print(msgHeader+"scenario_config map = "+scenario_config["Map"]["Name"])
                scenario_config["Active Cars"] = []
                for car in cars:
                    if car["Enabled"]:
                        scenario_config["Active Cars"].append(car)
                        if car["Strategy"] == "Manual":
                            self.manual_mode = True # If any enabled car is in manual mode, set manual_mode to true
                return scenario_config
        if exit:
            self.done = True
            pygame.quit()
            return False
        else:
            self.done = True
            pygame.quit()
            return False
            
    def add_waypoints(self, waypoints, scenario_config):
        print(msgHeader+"Adding user-defined waypoints to scenario_config.")
        scenario_config["Map"]["Waypoints"] = waypoints
        return scenario_config
        
    def cone_recognition_screen(self, option = False):
        raw_img = self.blank_image
        scale_factor = DISPLAY_WIDTH / raw_img.get_rect().size[0]
        scaled_img = pygame.transform.rotozoom(raw_img, 0, scale_factor)
        self.background_image = scaled_img
        self.screen.blit(self.background_image, (0, 0))
        if option == True:
            msg_text = self.font_general.render('Press A (controller) or ENTER (keyboard) when cones have been placed.', True, (0, 0, 0))
            self.screen.blit(msg_text, (DISPLAY_WIDTH/4, DISPLAY_HEIGHT/1.2))
        pygame.display.flip()
        
    def countdown(self, world_data):
        raw_img = world_data["map"]
        scale_factor = DISPLAY_WIDTH / raw_img.get_rect().size[0]
        scaled_img = pygame.transform.rotozoom(raw_img, 0, scale_factor)
        self.background_image = scaled_img
        self.screen.blit(self.background_image, (0, 0))
        countdown_text = self.font_countdown.render('3', True, (255, 0, 0))
        self.screen.blit(countdown_text, (DISPLAY_WIDTH/2.5, DISPLAY_HEIGHT/9))
        pygame.display.flip()
        time.sleep(1)
        self.screen.blit(self.background_image, (0, 0))
        countdown_text = self.font_countdown.render('2', True, (255, 0, 0))
        self.screen.blit(countdown_text, (DISPLAY_WIDTH/2.5, DISPLAY_HEIGHT/9))
        pygame.display.flip()
        time.sleep(1)
        self.screen.blit(self.background_image, (0, 0))
        countdown_text = self.font_countdown.render('1', True, (255, 0, 0))
        self.screen.blit(countdown_text, (DISPLAY_WIDTH/2.5, DISPLAY_HEIGHT/9))
        pygame.display.flip()
        time.sleep(1)
        self.screen.blit(self.background_image, (0, 0))
        countdown_text = self.font_countdown.render('GO!', True, (0, 255, 0))
        self.screen.blit(countdown_text, (DISPLAY_WIDTH/6, DISPLAY_HEIGHT/9))
        pygame.display.flip()
        time.sleep(1)
        self.clear_events()


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
        
        self.UI_button = pygame.transform.scale(pygame.image.load("media/UI.png"),
                                             (int(self.w), int(self.h)))

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
            screen.blit(self.UI_button, (self.x  - self.w, (self.y + 150)+ self.h))
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
                
                if(car["Strategy"] == "Manual"): # Check for manual option and display it differently
                    file_text_render = self.font.render("Manual", True, (0,255,0))
                    file_text_rect = file_text_render.get_rect(center=(self.x + self.w *2.5, self.y + self.h / 1.2))
                    screen.blit(file_text_render, file_text_rect)

                else:
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
