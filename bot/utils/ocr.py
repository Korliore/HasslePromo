import os

os.environ["OMP_NUM_THREADS"] = "1"
import cv2
import numpy as np
import logging

# Инициализация логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("[OCR]")

