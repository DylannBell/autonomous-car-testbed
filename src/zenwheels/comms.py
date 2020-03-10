import select
import threading
import time
import csv
from bluetooth import *

from constants import *

msgHeader = "[CAR COMMS]: "

BT_LOOP_SLEEP = 25


def read_cars_csv():
	file = csv.DictReader(open(os.path.join(ZENWHEELS_DIR, 'cars.csv')))
	cars = []
	for row in file:
		cars.append(row)
	return cars


class CarCommunicator():
	def __init__(self):
		self.cars_info = read_cars_csv()
		self.active_vehicles = None
		self.car_sockets = {}

	def connectToCars(self, vehicles):
		print(msgHeader + "Connecting to the ZenWheels cars...")
		self.active_vehicles = vehicles

		for vehicle in self.active_vehicles:
			car_id = vehicle.owner.ID
			if car_id in self.car_sockets.keys() and self.car_sockets[car_id] != None:
				print(msgHeader + "Already connected to " + car_id + ".")
				continue
			mac_address = None
			for car in self.cars_info:
				if car["Bluetooth SSID"] == car_id:
					mac_address = car["MAC Address"]
					break
			if mac_address is None:
				print(msgHeader + "Could not find a record for " + car_id + ".")
				return False

			# Try to connect to each car three times
			connected = False
			for attempt in range(1, 4):
				try:
					print(msgHeader + "Connecting to %s (Attempt %d)." % (car_id, attempt))
					socket = BluetoothSocket(RFCOMM)
					socket.connect((mac_address, 1))
					self.car_sockets[car_id] = socket
					print(msgHeader + "Connected to %s." % car_id)
					connected = True
					break
				except (BluetoothError, OSError) as e:
					print(msgHeader + "Could not connect to %s because %s." % (car_id, e))
			if connected == False:
				print(msgHeader + "All connection attempts to %s failed." % (car_id))
				return False

		self.startCarComms()
		return True


	def startCarComms(self):
		t_process = threading.Thread(target=self.bt_send)
		t_process.daemon = True
		t_process.start()

	def bt_send(self):
		while True:
			for vehicle in self.active_vehicles:
				socket = self.car_sockets[vehicle.owner.ID]
				if socket is None: continue # Connection to this car was lost.
				try:
					can_read, can_write, has_error = select.select([], [socket], [], 0)
					if socket in can_write:
						try:
							if not vehicle.command_queue:
								continue
							command = vehicle.command_queue.popitem()
							socket.send(command[0])
						except Exception as e:
							print(msgHeader + str(e))
							pass
				except (BluetoothError, OSError, ValueError) as e:
					print(msgHeader + str(e))
					socket.close()
					self.car_sockets[vehicle.owner.ID] = None

			# Ray: Sleep is essential otherwise all system resources are taken and total system delay skyrockets.
			time.sleep(BT_LOOP_SLEEP / 1000)
