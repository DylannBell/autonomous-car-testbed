from tracker.core import *
from threading import Thread
from multiprocessing import Process, Queue
from sys import argv
from pathlib import Path
from queue import Empty as QueueEmptyException

header = "[CAMERA]: "

if len(argv) > 1:
	filename = argv[1]
else:
	filename = "raw"

CAPTURE_WIDTH = 640
CAPTURE_HEIGHT = 480

camSetupScript = 	"""
					v4l2-ctl \
					-c auto_exposure=1 \
					-c exposure_time_absolute=100 \
					-c white_balance_auto_preset=0 \
					-c red_balance=2000 \
					-c blue_balance=1500
					"""
# G04 values are red=2000, blue=1500
# Clough values are red=2300, blue=1400

class OldCamera:
	def __init__(self, source=None):
		if source is None: # Reading from webcam.
			os.system(camSetupScript)
			self.livestream = True
			self.stream = cv2.VideoCapture(0)
			self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, CAPTURE_WIDTH)
			self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, CAPTURE_HEIGHT)
		else: # Reading from video file.
			self.livestream = False
			self.stream = cv2.VideoCapture(source)
			self.lastTime = time.time()

		_, self.frame = self.stream.read()
		self.deliveredFrame = False
		self.frame_count = 1
		self.stopped = False
		self.start()

	def start(self):
		Thread(target=self.update, args=()).start()
		return self

	def update(self):
		if self.livestream:
			while True:
				if self.stopped:
					return
				_, self.frame = self.stream.read()
				self.frame_count += 1
				self.deliveredFrame = False
		else:
			while True:
				if self.stopped:
					return
				now = time.time()
				if now - self.lastTime > 1 / 30: # Fake 30 fps stream.
					self.lastTime = now
					ret, self.frame = self.stream.read()
					self.frame_count += 1
					self.deliveredFrame = False
					if not ret:
						self.destroy()

	def get_frame(self):
		while True:
			if not self.deliveredFrame:
				self.deliveredFrame = True
				return self.frame


	def stop(self):
		self.stopped = True

	def destroy(self):
		self.stop()
		self.stream.release()
		print("\n" + header + "Frame Count: " + str(self.frame_count))


class Camera():
	def __init__(self, source=None):
		if source is not None:
			# Check if specified source exists.
			if not Path(source).exists():
				print(header + "Error - path '" + str(source) + "' does not exist.")
				return

		self.killQueue = Queue(maxsize=1)
		self.framebuffer = Queue(maxsize=1)
		self.worker = Process(target=self.read_frames, args=(source, self.framebuffer, self.killQueue,))
		self.worker.daemon = True
		self.worker.start()

		while self.framebuffer.empty(): # Wait for camera to activate.
			continue

	def read_frames(self, source, framebuffer, killQueue):
		if source is None: # Reading from webcam.
			os.system(camSetupScript)
			stream = cv2.VideoCapture(0)
			stream.set(cv2.CAP_PROP_FRAME_WIDTH, CAPTURE_WIDTH)
			stream.set(cv2.CAP_PROP_FRAME_HEIGHT, CAPTURE_HEIGHT)
			while True:
				if killQueue.full(): # Flush queues.
					killQueue.get()
					try:
						while True:
							framebuffer.get_nowait()
					except QueueEmptyException:
						framebuffer.close()
						killQueue.close()
						framebuffer.join_thread()
						killQueue.join_thread()
						break
				ret, frame = stream.read()
				if not ret or frame is None: continue
				try:
					if framebuffer.full():
						framebuffer.get_nowait()
				except:
					pass
				framebuffer.put(frame)
		else: # Reading from video file.
			stream = cv2.VideoCapture(source)
			lastTime = time.time()
			while True:
				if killQueue.full(): # Flush queues.
					killQueue.get()
					try:
						while True:
							framebuffer.get_nowait()
					except QueueEmptyException:
						framebuffer.close()
						killQueue.close()
						framebuffer.join_thread()
						killQueue.join_thread()
						break
				now = time.time()
				if now - lastTime > 1 / 30: # Fake 30 fps stream.
					lastTime = now
					ret, frame = stream.read()
					if not ret or frame is None: continue
					try:
						if framebuffer.full():
							framebuffer.get_nowait()
					except:
						pass
					framebuffer.put(frame)
		return

	def get_frame(self):
		start = time.time()
		while self.framebuffer.empty(): # Block until a frame is available.
			timeElapsed = time.time() - start
			if timeElapsed > 0.5: # Timeout.
				print("\n\n\nRan out of frames.\n\n\n")
				return None
		frame = None
		while not self.framebuffer.empty() or frame is None:
			frame = self.framebuffer.get() # Get most up-to-date frame.
		return frame

	def stop_camera(self):
		self.killQueue.put("KILL")
		self.worker.join()


def video_capture():
	os.system(camSetupScript)
	frame_width = 640
	frame_height = 480
	stream = cv2.VideoCapture(0)
	stream.set(cv2.CAP_PROP_FRAME_WIDTH, CAPTURE_WIDTH)
	stream.set(cv2.CAP_PROP_FRAME_HEIGHT, CAPTURE_HEIGHT)

	start = time.time()
	timeElapsed = 0
	frameCount = 0

	def worker(q):
		out = cv2.VideoWriter(filename + ".avi", cv2.VideoWriter_fourcc(*"MJPG"), 30.0, (frame_width, frame_height))
		while q.empty():
			continue
		count = 0
		while not q.empty():
			out.write(q.get())
			count += 1
			if count % 100 == 0:
				print("Wrote ", count, " frames.")
		out.release()
		print("Finished writing.")

	queue = Queue()
	p = Process(target=worker, args=(queue,))
	p.daemon = True
	p.start()

	while timeElapsed < 1000 / 30: # 1000 frames.
			ret, frame = stream.read()
			if ret:
				queue.put(frame)
				frameCount += 1
			if frameCount % 100 == 0:
				print("Read ", frameCount, " frames.")
			timeElapsed = time.time() - start
	print('Total frames: ', frameCount)

	p.join()
	queue.close()
	queue.join_thread()

	print("Shutting down.")
	stream.release()


if __name__ == "__main__":
	video_capture()