import os

DISPLAY_WIDTH = 1024
DISPLAY_HEIGHT = 728

MAPS_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "maps")
STRATEGIES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "strategies")
MEDIA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "media")
ZENWHEELS_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "zenwheels")

CALIBRATION_IMG_PATH = os.path.join(MEDIA_DIR, 'checkerboard.png')