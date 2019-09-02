from tracker.core import *
from tracker.blob_detector import BlobDetector
from tracker.orientation_finder import OrientationFinder


class MOSSETracker():
	def __init__(self, entities, initFrame):
		self.detector = BlobDetector()
		self.entities = entities
		for entity in self.entities:
			entity.tracker = cv2.TrackerMOSSE_create()
			bb = (entity.position[0] - 20, entity.position[1] - 20, 40, 40)
			entity.tracker.init(initFrame, bb)

		self.orientationFinder = OrientationFinder()

	def process(self, image):
		copy = image.copy()

		# Track BBs.
		lostEntities = []
		for entity in self.entities:
			success, box = entity.tracker.update(image)
			if success:
				(x, y, w, h) = [int(v) for v in box]
				entity.position = (int(x + w / 2), int(y + h / 2))

				orientation = self.orientationFinder.dynamic_determine(entity)
				if orientation is not None:
					entity.orientation = orientation

				#roi = copy[y:y + h, x:x + w]
				#orientation = self.orientationFinder.static_determine(roi)

			else:
				print("\nLost " + entity.ID + ".")
				lostEntities.append(entity)

		# Re-detect any lost entities.
		if lostEntities:
			# Find keypoints in image.
			keypoints = self.detector.findCars(image)

			# Match keypoints with last known entity positions.
			pool = []
			owned = []

			for keypoint in keypoints:
				pos = (int(keypoint.pt[0]), int(keypoint.pt[1]))

				for entity in self.entities:
					dist = hypot(entity.position[0] - pos[0], entity.position[1] - pos[1])
					if entity in lostEntities:
						if dist < 40 or len(lostEntities) == 1: # If there's only one missing, give special treatment.
							pool.append((pos, entity, dist))
					elif dist < 8:
						owned.append(pos)
						break

			pool.sort(key=lambda t: t[2])

			for pair in pool:
				pos = pair[0]
				entity = pair[1]
				if pos in owned or entity in owned:
					continue
				else:
					owned.append(pos)
					owned.append(entity)
					entity.position = pos
					bb = (pos[0] - 20, pos[1] - 20, 40, 40)
					entity.tracker = cv2.TrackerMOSSE_create()
					entity.tracker.init(image, bb)
					print("Re-detected " + pair[1].ID)

		return self.entities