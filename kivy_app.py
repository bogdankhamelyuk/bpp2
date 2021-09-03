from kivy.app import App
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.gridlayout import GridLayout
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager
from worker import Gauge



        
class MainScreen(Screen):
    pass 
        


class GUI(App):
    def build(self):       
        
        self.gauge = Gauge()
        fps = 30
        Clock.schedule_interval(self.cameraRecord, 1.0 / fps)

        sm = ScreenManager()
        self.main_screen = MainScreen()
        sm.add_widget(self.main_screen)
        
        return sm
    
    def cameraRecord(self,dt):
        if self.gauge.update() is not None:
            image = self.gauge.update()
            buf = image.tobytes(order=None)
            image_texture = Texture.create(
                size=(self.gauge.img.shape[1], self.gauge.img.shape[0]), colorfmt='rgb')
            image_texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
            self.main_screen.ids.pressure_output.text = f'Pressure is: {round(self.gauge.pressure,1)}'
            self.main_screen.ids.vid.texture = image_texture




if __name__ == '__main__':
    GUI().run()
