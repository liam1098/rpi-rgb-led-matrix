#!/usr/bin/env python
import sys
import os
import time
from threading import Thread, Lock

from PIL import Image, ImageSequence

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../bindings/python'))
from rgbmatrix import RGBMatrix, RGBMatrixOptions


class ImageFactory:
    def __init__(self, matrix, controller, image_dict):
        self.matrix = matrix
        self.controller = controller
        self.exit_thread = True
        self.thread = None
        self.id_mutex = Lock()
        self.id = "INIT"
        self.old_id = "INIT"
        self.image_dict = image_dict

        self.fr_mutex = Lock()
        self.fr_multiplier = 1

        self.image_buffer = matrix.CreateFrameCanvas()

    def FormatAndSendImage(self, path):
        image = Image.open(path)
        if hasattr(image, 'is_animated') and image.is_animated:  # Safely check if the image is a GIF
            while not self.exit_thread:
                for frame in ImageSequence.Iterator(image):
                    self.DisplayFrame(frame)
                    time.sleep(60 / self.fr)  # Use GIF's own frame duration
        else:
            self.DisplayFrame(image)

    def SetGifFrameRate(self, frame_rate):
        with self.fr_mutex:
            self.fr_multiplier = 1

            self.fr = frame_rate

    def SetImage(self, id):
        if id in self.image_dict:
            with self.id_mutex:
                self.old_id = self.id
                self.id = id

    def ImageInputWorkFunc(self):
        while self.exit_thread == False:
            with self.id_mutex:
                current_id = self.id
            if current_id.endswith("-gif"):  # Only process GIFs if ID ends with "-gif"
                self.FormatAndSendImage(os.path.dirname(__file__) + "/img/" + self.image_dict[current_id])
            elif current_id != self.old_id:  # Process static images
                with self.id_mutex:
                    self.FormatAndSendImage(os.path.dirname(__file__) + "/img/" + self.image_dict[self.id])
                    self.old_id = self.id
                time.sleep(0.001)

    def StartImageWorker(self):
        self.exit_thread = False
        self.thread = Thread(target=self.ImageInputWorkFunc)
        self.thread.start()

    def DisplayFrame(self, frame):
        frame.thumbnail((self.matrix.width, self.matrix.height), Image.LANCZOS)
        self.image_buffer.SetImage(frame.convert('RGB'))
        self.controller.SetImage(self.image_buffer)
        
    def DoubleFRMultiplier(self):
        with self.fr_mutex:
            self.fr_multiplier = self.fr_multiplier * 2

    def HalfFRMultiplier(self):
        with self.fr_mutex:
            self.fr_multiplier = self.fr_multiplier / 2