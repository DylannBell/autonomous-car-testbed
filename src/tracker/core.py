"""

CORE.PY
Contains project imports, constants, helper functions etc.

"""

import time
import os
import cv2
import numpy as np
import json
from math import cos, sin, sqrt, hypot, radians, degrees, atan2, atan, pi
from threading import Thread



RESOLUTION = (640, 480)


class Entity():
	def __init__(self, ID):
		self.ID = str(ID)
		self.position = None
		self.orientation = None

		self.tracker = None
		self.measurement = None


class Timer():
	def __init__(self):
		self.startTime = time.time()
		self.lastTick = self.startTime
		self.fps_history = []

	def tick_ms(self):
		t = time.time()
		tickTime = t - self.lastTick
		self.lastTick = t
		return "{:.2f}".format(tickTime * 1000) + " ms"

	def tick_fps(self):
		t = time.time()
		tickTime = t - self.lastTick
		if tickTime == 0:
			return "inf fps"
		self.lastTick = t
		self.fps_history.append(1/tickTime)
		return "{:.2f}".format(1/tickTime) + " fps"

	def total_time(self):
		t = time.time()
		totalTime = t - self.startTime
		return "{:.2f}".format(totalTime) + " seconds"

	def average_fps(self):
		return "{:.2f}".format(np.mean(self.fps_history)) + " fps"