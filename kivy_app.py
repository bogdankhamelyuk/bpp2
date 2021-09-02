from kivy.app import App
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import threading 
from worker import Gauge
import cv2
import time

class KivyCamera(Image):
    def __init__(self, fps, **kwargs):
        super(KivyCamera, self).__init__(**kwargs)
        self.event = threading.Event()

        self.gauge = Gauge(self.event)
        Clock.schedule_interval(self.result, 1.0 / fps)
    
    def result(self, dt):
        
        if self.gauge.update() is not None:
            image = self.gauge.update()
            buf1 = cv2.flip(image, 0)
            buf = buf1.tostring()
            image_texture = Texture.create(
                size=(self.gauge.img.shape[1], self.gauge.img.shape[0]), colorfmt='rgb')
            image_texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
            # display image from the texture            
            self.texture = image_texture

class CamApp(App):
    def build(self):       
        self.pressure = KivyCamera(fps=20)
        return self.pressure


if __name__ == '__main__':
    CamApp().run()
