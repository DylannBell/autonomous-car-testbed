from tracker.core import *



class ConeDetector():
	def __init__(self):
		# Setup SimpleBlobDetector parameters.
		params = cv2.SimpleBlobDetector_Params()

		# Filter by Area.
		params.filterByArea = True
		params.minArea = 400
		params.maxArea = 1500

		# Filter by Circularity
		params.filterByCircularity = True
		params.minCircularity = 0.6
		params.maxCircularity = 0.99

		# Filter by Convexity
		params.filterByConvexity = False
		params.minConvexity = 0.87

		# Filter by Inertia
		params.filterByInertia = False
		params.minInertiaRatio = 0.3
		params.maxInertiaRatio = 0.99

		self.detector = cv2.SimpleBlobDetector_create(params)

		self.thresholdVal = 110
		self.kernel = np.ones((3, 3), np.uint8)

		self.border_mask = cv2.imread("media/woodmask.jpg", 0)


	def _superblob_divider(self, fg_img):
		img = fg_img.copy()
		_, contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		superblobs = []
		for c in contours:
			area = cv2.contourArea(c)
			perimeter = cv2.arcLength(c, True)
			if perimeter == 0:
				continue
			ratio = area / perimeter
			if area > 1000 and area < 2000 and ratio > 2.6:
				superblobs.append(c)

		for c in superblobs:
			x, y, w, h = cv2.boundingRect(c)
			mask = np.zeros(img.shape, np.uint8)
			mask[y:y + h, x:x + w] = img[y:y + h, x:x + w]

			[vx, vy, x0, y0] = cv2.fitLine(c, cv2.DIST_L2, 0, 0.01, 0.01)
			nx, ny = 1, -vx / vy
			mag = np.sqrt((1 + ny ** 2))
			vx, vy = nx / mag, ny / mag
			lefty = int((-x0 * vy / vx) + y0)
			righty = int(((mask.shape[1] - x0) * vy / vx) + y0)
			cv2.line(mask, (mask.shape[1] - 1, righty), (0, lefty), 0, 2)
			img[y:y + h, x:x + w] = mask[y:y + h, x:x + w]

		return img


	def findCones(self, image):
		# Convert to grayscale.
		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

		# Find non-projected objects.
		_, thresh = cv2.threshold(gray, self.thresholdVal, 255, cv2.THRESH_BINARY_INV)
		masked = cv2.bitwise_and(thresh, thresh, mask=self.border_mask)


		# Fill holes in cars.
		dilated = cv2.dilate(masked, self.kernel, iterations=3)
		dilated = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, self.kernel, iterations=3)

		# Separate superblobs.
		divided = self._superblob_divider(dilated)

		#cv2.imshow("divided", divided)
		#cv2.waitKey(100)

		# Detect blobs.
		inv = cv2.bitwise_not(divided)
		keypoints = self.detector.detect(inv)

		return keypoints
