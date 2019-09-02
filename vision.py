from tracker.core import *
from tracker.camera import Camera
from tracker.blob_detector import BlobDetector
from tracker.calibrator import Calibrator
from tracker.mosse_tracker import MOSSETracker
from multiprocessing import Process, Manager

msgHeader = "[VISION]: "


class Vision():
	def __init__(self):
		self.cam = Camera()

		self.homo_matrix = None

		manager = Manager()
		self.shared_dict = manager.dict()
		self.worker = None

	def identify(self, agents):
		entities_in_scene = []
		for agent in agents:
			entities_in_scene.append(agent.ID)

		bd = BlobDetector()

		start = time.time()
		entities_found = []
		count = 1
		while count != 0:
			image = self.cam.get_frame()

			# Assign list of IDs left to right on horizontal axis
			positions = []
			keypoints = bd.findCars(image)
			for keypoint in keypoints:
				pos = (int(keypoint.pt[0]), int(keypoint.pt[1]))
				positions.append(pos)
			positions.sort(key=lambda x: x[0])

			entities_found = []
			for i in range(len(positions)):
				if len(positions) != len(entities_in_scene):
					count = -20  # Not the right number of objects - reset countdown.
					break
				entity = Entity(entities_in_scene[i])
				entity.position = positions[i]
				entities_found.append(entity)

			if len(entities_found) == len(entities_in_scene) and count > 0:
				count = -20  # Identify for 20 more frames to ensure accuracy.
			count += 1

			if time.time() - start > 20: # Timeout after 20 seconds.
				print(msgHeader + "Identification stage timed out.")
				return False

		entity_str = ""
		for i in range(len(entities_found)):
			if i < len(entities_found) - 2:
				entity_str += entities_found[i].ID + ", "
			elif i == len(entities_found) - 2:
				entity_str += entities_found[i].ID + " and "
			else:
				entity_str += entities_found[i].ID
		print(msgHeader + "Identified entities " + entity_str + ".")

		self.shared_dict["Entities"] = entities_found
		return True

	def calibrate(self):
		frame = self.cam.get_frame()
		self.homo_matrix, corners = Calibrator().get_transform(frame)
		return corners

	def start_tracking(self):
		self.worker = Process(target=self.track, args=(self.shared_dict,))
		self.worker.daemon = True
		self.worker.start()

	def stop_tracking(self):
		self.shared_dict["KILL"] = True
		self.worker.terminate()
		self.worker.join()

	def track(self, shared_dict):
		shared_dict["KILL"] = False

		entities = list(shared_dict["Entities"])
		tracker = MOSSETracker(entities, self.cam.get_frame())

		# Main tracking loop.
		print(msgHeader + "Initialised the MOSSE Tracker.")
		while True:
			if shared_dict["KILL"]:
				break
			image = self.cam.get_frame()
			if image is None:
				break
			entities = tracker.process(image)
			shared_dict["Entities"] = entities
		return

	def get_car_locations(self):
		car_locations = []
		for entity in self.shared_dict["Entities"]:
			point = np.matrix([entity.position[0], entity.position[1], 1]).T
			transformed = np.dot(self.homo_matrix, point)
			position = (int(transformed[0]), int(transformed[1]))
			car_locations.append({"ID": entity.ID,
								  "position": position,
								  "orientation": entity.orientation})
		return car_locations