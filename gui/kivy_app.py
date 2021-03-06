from kivy.app import App

from kivy.clock import Clock
from kivy.graphics.texture import Texture
from threading import Event
from kivy.uix.screenmanager import Screen, ScreenManager
from worker import Gauge
from parameters import Parameters
import json


class MainScreen(Screen):
    param = Parameters()

    def changeCamera(self):
        if self.param.__class__._camera == 0:
            self.param.__class__._camera = 2
        else:
            self.param.__class__._camera = 0
        SettingsScreen().updateJson()

    def mirrorCamera(self):
        GUI().mirrorEventSet()


class SettingsScreen(Screen):
    param = Parameters()
    threshold1 = param.__class__._canny_threshold1
    threshold2 = param.__class__._canny_threshold2
    maxLineGap = param.__class__._maxLineGap
    minLineLength = param.__class__._minLineLength
    houghlines_threshold = param.__class__._houghlines_threshold

    minDist = param.__class__._minDist
    param1 = param.__class__._param1
    param2 = param.__class__._param2
    minRadius = param.__class__._minRadius
    maxRadius = param.__class__._maxRadius

    def changeCannyThreshold1(self, *args):
        self.param.__class__._canny_threshold1 = int(args[1])
        #self.updateJson()

    def changeCannyThreshold2(self, *args):
        self.param.__class__._canny_threshold2 = int(args[1])
        #self.updateJson()

    def changeMinLineLength(self, *args):
        self.param.__class__._minLineLength = int(args[1])
        #self.updateJson()

    def changeMaxLineGap(self, *args):
        self.param.__class__._maxLineGap = int(args[1])
        #self.updateJson()

    def changeHoughLinesThreshold(self, *args):
        self.param.__class__._houghlines_threshold = int(args[1])

    def changeMinDist(self, *args):
        self.param.__class__._minDist = int(args[1])
        #self.updateJson()

    def changeParam1(self, *args):
        self.param.__class__._param1 = int(args[1])

    def changeParam2(self, *args):
        self.param.__class__._param2 = int(args[1])/1000

    def changeMinRadius(self, *args):
        self.param.__class__._minRadius = int(args[1])

    def changeMaxRadius(self, *args):
        self.param.__class__._maxRadius = int(args[1])

    def updateJson(self):
        file = open(
            "/home/bogdan/Vs-code-workspace/python/lndf_video/gui/datafile.json", "w")
        print("saved values")
        data = {
            "threshold1": self.param.__class__._canny_threshold1,
            "threshold2": self.param.__class__._canny_threshold2,
            "maxLineGap": self.param.__class__._maxLineGap,
            "minLineLength": self.param.__class__._minLineLength,
            "houghlines_threshold": self.param.__class__._houghlines_threshold,
            "camera": self.param.__class__._camera,
            "minDist": self.param.__class__._minDist,
            "param1": self.param.__class__._param1,
            "param2": self.param.__class__._param2,
            "minRadius": self.param.__class__._minRadius,
            "maxRadius": self.param.__class__._maxRadius,
            "angle": self.param.__class__._angle
        }
        json.dump(data, file, sort_keys=False, indent=4, separators=(',', ':'))


class GUI(App):
    mirrorEvent = Event()

    def build(self):
        self.param = Parameters()
        self.gauge = Gauge(self.mirrorEvent)

        fps = 20
        Clock.schedule_interval(self.cameraRecord, 1.0 / fps)

        sm = ScreenManager()
        self.main_screen = MainScreen()
        self.settings_screen = SettingsScreen()
        sm.add_widget(self.main_screen)
        sm.add_widget(self.settings_screen)

        return sm

    def cameraRecord(self, dt):
        image = self.gauge.update()
        if image is not None:
            #image = self.gauge.img
            buf = image.tobytes(order=None)
            image_texture = Texture.create(
                size=(image.shape[1], image.shape[0]), colorfmt='rgb')
            image_texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
            self.main_screen.ids.vid.texture = image_texture

            try:
                edges = self.gauge.edges
                buf1 = edges.tobytes(order=None)
                edges_texture = Texture.create(
                    size=(edges.shape[1], edges.shape[0]), colorfmt='rgb')
                edges_texture.blit_buffer(
                    buf1, colorfmt='rgb', bufferfmt='ubyte')
                self.settings_screen.ids.vid.texture = edges_texture
            except:
                self.settings_screen.ids.vid.texture = image_texture
        self.main_screen.ids.pressure_output.text = f'  Pressure is: {round(self.gauge.pressure,1)}'

    def mirrorEventSet(self):
        self.mirrorEvent.set()


if __name__ == '__main__':
    GUI().run()