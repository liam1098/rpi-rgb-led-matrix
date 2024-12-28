#!/usr/bin/env python
import sys
import os
import time
from threading import Thread, Lock

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../bindings/python'))
from rgbmatrix import RGBMatrix, RGBMatrixOptions

class Controller:
    def __init__(self, matrix, strobe_dict):
        self.exit_main_thread = True
        self.image_mutex = Lock()
        self.bpm_mutex = Lock()
        self.strobe_mode_mutex = Lock()
        self.main_thread = None
        self.strobe_dict = strobe_dict
        self.strobe_mode = 1
        self.old_strobe_mode = 1
        self.bpm_multiplier = 1

        self.matrix = matrix
        self.blank_canvas = self.matrix.CreateFrameCanvas()
        self.blank_canvas.Clear()
        self.image = self.matrix.SwapOnVSync(self.blank_canvas)
        self.blank = True

    def SetBpm(self, bpm):
        with self.bpm_mutex:
            self.bpm_multiplier = 1

            self.bpm = bpm
            self.interval_secs = 60 / int(bpm)

    def SetImage(self, image):
        old_image = None
        while True:
            if self.blank == True or self.exit_main_thread == True:
                with self.image_mutex:
                    old_image = self.image
                    self.image = image
                    break
            else:
                time.sleep(0.001)

        return old_image

    def SetStrobeMode(self, mode):
        if mode in self.strobe_dict:
            with self.strobe_mode_mutex:
                self.old_strobe_mode = self.strobe_mode
                self.strobe_mode = mode

    def StrobeWorkFunc(self):
        strobe_count = 0
        strobe_arr = [1]
        start_time = time.monotonic()

        # This should loop infinitely or until we shutdown
        while self.exit_main_thread == False:
            
            # Check if we've set a new strobe sequence
            with self.strobe_mode_mutex:
                if self.old_strobe_mode != self.strobe_mode:
                    self.old_strobe_mode = self.strobe_mode
                    strobe_arr = self.strobe_dict[self.strobe_mode]
                    strobe_count = 0

            if strobe_count >= len(strobe_arr):
                strobe_count = 0
            
            # Do the strobing
            self.bpm_mutex.acquire()
            if time.monotonic() - start_time > self.interval_secs * strobe_arr[strobe_count] / self.bpm_multiplier:
                self.bpm_mutex.release()
                with self.image_mutex:
                    if self.blank:
                        self.blank_canvas = self.matrix.SwapOnVSync(self.image)
                        self.blank = False
                    else:
                        self.image = self.matrix.SwapOnVSync(self.blank_canvas)
                        self.blank = True
                strobe_count = strobe_count + 1
                start_time = time.monotonic()
            else:
                self.bpm_mutex.release()
                time.sleep(0.001)

    def StartStrobeWorker(self):
        self.exit_main_thread = False
        self.main_thread = Thread(target=self.StrobeWorkFunc)
        self.main_thread.start()

    def StopStrobeWorkers(self):
        self.exit_main_thread = True
        self.main_thread.join()

    def DoubleBpmMultiplier(self):
        with self.bpm_mutex:
            self.bpm_multiplier = self.bpm_multiplier * 2

    def HalfBpmMultiplier(self):
        with self.bpm_mutex:
            self.bpm_multiplier = self.bpm_multiplier / 2


