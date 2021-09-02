from kivy.app import App
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.gridlayout import GridLayout
from kivy.uix.slider import Slider
from kivy.uix.label import Label


from worker import Gauge


class KivyCamera(Image):
    def __init__(self, fps, **kwargs):
        super(KivyCamera, self).__init__(**kwargs)
        self.gauge = Gauge()
        Clock.schedule_interval(self.result, 1.0 / fps)
    
    def result(self, dt):
        if self.gauge.update() is not None:
            image = self.gauge.update()
            buf = image.tostring()
            image_texture = Texture.create(
                size=(self.gauge.img.shape[1], self.gauge.img.shape[0]), colorfmt='rgb')
            image_texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
            # display image from the texture            
            self.texture = image_texture



class SlidersLayout(GridLayout):
    def __init__(self):
        super().__init__()
        self.rows = 10
        self.size_hint = (.4,.5)
        self.label1 = Label(text="First Canny Threshold")
        self.ct1 = Slider(min = 50,max=500)
        
        self.label2 = Label(text="Second Canny Threshold")
        self.ct2 = Slider(min = 50,max=500)

        self.label3 = Label(text="min Line Length")
        self.mnLL = Slider(min=0,max=100)

        self.label4 = Label(text="max Line Gap")
        self.mxLG = Slider(min=0,max=100)

        self.label5 = Label(text="hough Lines Threshold")
        self.hlt = Slider(min=0,max=100)

        self.add_widget(self.label1)
        self.add_widget(self.ct1)
        self.add_widget(self.label2)
        self.add_widget(self.ct2)
        self.add_widget(self.label3)
        self.add_widget(self.mnLL)
        self.add_widget(self.label4)
        self.add_widget(self.mxLG)
        self.add_widget(self.label5)
        self.add_widget(self.hlt)



class ChildLayout(GridLayout):
    def __init__(self,capture):
        super().__init__()
        self.cols=2
        self.size_hint=(.9,.9)
        sliders = SlidersLayout()
        self.add_widget(capture)
        self.add_widget(sliders)



class ParentLayout(GridLayout):
    def __init__(self,capture):
        super().__init__()
        
        self.rows = 2 
        self.text = "pressure is: "
        self.label = Label(text = self.text,size_hint_y=.1)
        child = ChildLayout(capture)
        self.add_widget(child)
        self.add_widget(self.label)
        

class GUI(App):
    def build(self):       
        camera_image = KivyCamera(fps=30)
        return  ParentLayout(camera_image)



if __name__ == '__main__':
    GUI().run()
