from tracker.core import *
from constants import *

msgHeader = "[CALIBRATOR]: "




class Calibrator:
	def get_transform(self, inputImage):
		print(msgHeader + "Attempting to calibrate...")

		img1 = cv2.resize(cv2.imread(CALIBRATION_IMG_PATH),
						  (DISPLAY_WIDTH, DISPLAY_HEIGHT))
		img2 = cv2.cvtColor(inputImage, cv2.COLOR_BGR2GRAY)

		patternSize = (10, 7)
		_, reference_corners = cv2.findChessboardCorners(img1, patternSize)
		found, projected_corners = cv2.findChessboardCorners(img2, patternSize)

		if found:
			rc = np.array(reference_corners).reshape(len(reference_corners), 2)
			pc = np.array(projected_corners).reshape(len(projected_corners), 2)

			homo = cv2.findHomography(pc, rc)
			corners = self.calculate_corners(pc, homo[0])

			print(msgHeader + "Successfully calibrated.")
			return homo[0], corners
		else:
			print(msgHeader + "Could not calibrate.")
			return None, None

	def calculate_corners(self, pc, mat):
		xMin = None
		xMax = None
		yMin = None
		yMax = None
		for p in pc:
			point = np.matrix([p[0], p[1], 1]).T
			hPoint = np.dot(mat, point)
			x = hPoint[0]
			y = hPoint[1]
			if xMin is None or x < xMin:
				xMin = int(x)
			if xMax is None or x > xMax:
				xMax = int(x)
			if yMin is None or y < yMin:
				yMin = int(y)
			if yMax is None or y > yMax:
				yMax = int(y)

		sw = int((xMin - xMax) / 9)

		tl = [xMin + sw, yMin + sw]
		tr = [xMax - sw, yMin + sw]
		bl = [xMin + sw, yMax - sw]
		br = [xMax - sw, yMax - sw]

		return [tl, tr, bl, br]
