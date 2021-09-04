from kivy.app import App
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.gridlayout import GridLayout
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager
from worker import Gauge
from parameters import  Parameters


        
class MainScreen(Screen):
    pass 
        
class SettingsScreen(Screen):
    param = Parameters()
    threshold1 = param.__class__._canny_threshold1
    threshold2 = param.__class__._canny_threshold2
    maxLineGap = param.__class__._maxLineGap
    minLineLength = param.__class__._minLineLength
    houghlines_threshold = param.__class__._houghlines_threshold
    def changeCannyThreshold1(self,*args):
        self.param.__class__._canny_threshold1 = int(args[1])
    def changeCannyThreshold2(self,*args):
        self.param.__class__._canny_threshold2 = int(args[1])
    def changeMinLineLength(self,*args):
        self.param.__class__._minLineLength = int(args[1])
    def changeMaxLineGap(self,*args):
        self.param.__class__._maxLineGap = int(args[1])
    def changeHoughLinesThreshold(self,*args):
        self.param.__class__._houghlines_threshold = int(args[1])    



class GUI(App):
    def build(self):       
        
        self.gauge = Gauge()
        fps = 30
        Clock.schedule_interval(self.cameraRecord, 1.0 / fps)

        sm = ScreenManager()
        self.main_screen = MainScreen()
        self.settings_screen = SettingsScreen()
        sm.add_widget(self.main_screen)
        sm.add_widget(self.settings_screen)
        
        return sm
    
    def cameraRecord(self,dt):
        if self.gauge.update() is not None:
            image = self.gauge.img
            buf = image.tobytes(order=None)
            image_texture = Texture.create(
                size=(image.shape[1], image.shape[0]), colorfmt='rgb')
            image_texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
            self.main_screen.ids.vid.texture = image_texture
           
            edges = self.gauge.edges 
            buf1 = edges.tobytes(order=None)
            edges_texture = Texture.create(
                size=(edges.shape[1], edges.shape[0]), colorfmt='rgb')
            edges_texture.blit_buffer(buf1, colorfmt='rgb', bufferfmt='ubyte')  
            self.settings_screen.ids.vid.texture = edges_texture

            self.main_screen.ids.pressure_output.text = f'  Pressure is: {round(self.gauge.pressure,1)}'




if __name__ == '__main__':
    GUI().run()
