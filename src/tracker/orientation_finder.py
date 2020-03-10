from tracker.core import *



class OrientationFinder():
	def __init__(self):
		# For dynamic.
		self.last_locations = {}
		self.last_angles = {}
		self.last_times = {}
		self.last_velocities = {}

		# For static.
		self.kernel = np.ones((9,9), np.uint8)
		self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(6,6))


	"""
		This isn't very robust. Definitely needs some kind of filtering. - Michael
	"""
	def dynamic_determine(self, entity):
		car_id = entity.ID
		car_position = entity.position

		current_time = time.time()
		if not car_id in self.last_locations.keys():
			self.last_locations[car_id] = car_position
			self.last_angles[car_id] = 0
			self.last_times[car_id] = time.time()
			self.last_velocities[car_id] = 0

		if self.last_velocities[car_id] > 70:
			timestep = 100
		elif self.last_velocities[car_id] > 50:
			timestep = 200
		else:
			timestep = 500
		time_taken = (current_time - self.last_times[car_id]) * 1000
		if (time_taken > timestep):
			dx = car_position[0] - self.last_locations[car_id][0]
			dy = car_position[1] - self.last_locations[car_id][1]

			velocity = hypot(dx, dy) / (timestep / 1000)

			# Filter out small dy, dx values.
			if abs(dx) < 5 and abs(dy) < 5:
				theta = self.last_angles[car_id]
			else:
				theta = 0
				if (dx != 0):
					theta = atan(dy / dx) * (180 / pi)
				if (dx == 0):
					if (dy <= 0):
						theta = 0
					else:
						theta = 180
				elif (dy == 0):
					if (dx < 0):
						theta = 90
					else:
						theta = 270
				elif (dx > 0 and dy > 0):
					theta = theta + 90
				elif (dx > 0 and dy < 0):
					theta = theta + 90
				elif (dx < 0 and dy > 0):
					theta = theta + 270
				elif (dx < 0 and dy < 0):
					theta = theta + 270

				# Handle reversing.
				if self.last_angles[car_id] is not None:
					diff = abs(theta - self.last_angles[car_id])
					if diff > 120 and diff < 240:
						theta = self.last_angles[car_id] + 180 - diff

			self.last_times[car_id] = current_time
			self.last_angles[car_id] = int(theta)
			self.last_locations[car_id] = car_position
			self.last_velocities[car_id] = velocity

			return self.last_angles[car_id]

	def static_determine(self, roi):
		image = self._apply_border(roi)
		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		_, thresh = cv2.threshold(gray, 110, 255, cv2.THRESH_BINARY_INV)
		dilated = cv2.dilate(thresh, self.kernel)
		eroded = cv2.erode(dilated, self.kernel)
		canny = cv2.Canny(eroded, 100, 200)

		_, contours, _ = cv2.findContours(canny, 1, 2)
		if not contours:
			return None
		c = max(contours, key=cv2.contourArea)
		rect = cv2.minAreaRect(c)
		box = np.int0(cv2.boxPoints(rect))

		(x, y), (h, w), angle = rect
		if h > w:
			temp = w
			w = h
			h = temp
			angle -= 90

		x1 = int(x - ((w / 8) * cos(radians(90 + angle))))
		y1 = int(y - ((h / 8) * sin(radians(90 + angle))))
		rect_upper = ( (x1, y1), (h, w / 4), angle )
		box_upper = np.int0(cv2.boxPoints(rect_upper))

		x2 = int(x + ((w / 8) * cos(radians(90 + angle))))
		y2 = int(y + ((h / 8) * sin(radians(90 + angle))))
		rect_lower = ( (x2, y2), (h, w / 4), angle )
		box_lower = np.int0(cv2.boxPoints(rect_lower))

		# (Contrast Limited Adaptive Histogram Equalization)
		cl1 = self.clahe.apply(gray)
		_, windscreen = cv2.threshold(cl1, 50, 255, cv2.THRESH_BINARY)

		mask_upper = np.zeros((image.shape[0], image.shape[1], 1), np.uint8)
		cv2.fillConvexPoly(mask_upper, box_upper, [255])
		count_upper = cv2.countNonZero(cv2.bitwise_and(mask_upper, windscreen))

		mask_lower = np.zeros((image.shape[0], image.shape[1], 1), np.uint8)
		cv2.fillConvexPoly(mask_lower, box_lower, [255])
		count_lower = cv2.countNonZero(cv2.bitwise_and(mask_lower, windscreen))

		if count_upper > count_lower:
			orientation = degrees(atan2(y2 - y1, x2 - x1))
		else:
			orientation = degrees(atan2(y1 - y2, x1 - x2))

		return orientation

	def _apply_border(self, image, borderSize=0):
		row, col = image.shape[:2]
		bordered_image = image.copy()
		bordered_image[row - borderSize:row, 0:col] = 255
		bordered_image[0:borderSize, 0:col] = 255
		bordered_image[0:row, col - borderSize:col] = 255
		bordered_image[0:row, 0:borderSize] = 255
		return bordered_image
