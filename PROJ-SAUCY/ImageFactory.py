#!/usr/bin/env python
import sys
import os
import time
from threading import Thread, Lock

from PIL import Image

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

        self.image_buffer = matrix.CreateFrameCanvas()

    def FormatAndSendImage(self, path):
        image = Image.open(path)
        image.thumbnail((self.matrix.width, self.matrix.height), Image.LANCZOS)
        self.image_buffer.SetImage(image.convert('RGB'))
        self.image_buffer = self.controller.SetImage(self.image_buffer)

    def SetImage(self, id):
        if id in self.image_dict:
            with self.id_mutex:
                self.old_id = self.id
                self.id = id

    def ImageWorkFunc(self):
        while self.exit_thread == False:
            with self.id_mutex:
                if self.id != self.old_id:
                    self.FormatAndSendImage(os.path.dirname(__file__) + "/img/" + self.image_dict[self.id])
                    self.old_id = self.id
                else:
                    time.sleep(0.001)


    def StartImageWorker(self):
        self.exit_thread = False
        self.thread = Thread(target=self.ImageWorkFunc)
        self.thread.start()

        