#!/usr/bin/env python
import sys
import os
import time
from threading import Thread, Lock

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../bindings/python'))
from rgbmatrix import RGBMatrix, RGBMatrixOptions

class Controller:
    def __init__(self, matrix):
        self.exit_thread = True
        self.image_mutex = Lock()
        self.bpm_mutex = Lock()
        self.thread = None

        self.matrix = matrix
        self.blank_canvas = self.matrix.CreateFrameCanvas()
        self.blank_canvas.Clear()
        self.image = self.matrix.SwapOnVSync(self.blank_canvas)
        self.blank = True

    def SetBpm(self, bpm):
        with self.bpm_mutex:
            self.bpm = bpm
            self.interval_secs = 60 / int(bpm)

    def SetImage(self, image):
        old_image = None
        while True:
            if self.blank == True or self.exit_thread == True:
                with self.image_mutex:
                    old_image = self.image
                    self.image = image
                    break
            else:
                time.sleep(0.001)

        return old_image

    def SetStrobeMode(self, mode):
        self.strobe_mode = mode

    def StrobeWorkFunc(self):
        start_time = time.monotonic()
        while self.exit_thread == False:
            with self.bpm_mutex:
                if time.monotonic() - start_time > self.interval_secs:
                    start_time = time.monotonic()
                    with self.image_mutex:
                        if self.blank:
                            self.blank_canvas = self.matrix.SwapOnVSync(self.image)
                            self.blank = False
                        else:
                            self.image = self.matrix.SwapOnVSync(self.blank_canvas)
                            self.blank = True
                else:
                    time.sleep(0.001)

    def StartStrobeWorker(self):
        self.exit_thread = False
        self.thread = Thread(target=self.StrobeWorkFunc)
        self.thread.start()

    def StopStrobeWorker(self):
        self.exit_thread = True
        self.thread.join()