# Betriebspraxisphase 2
Repo for Company practice phase #2 at System Industrie Electronic as a Dual Student. The repo includes kivy-app and django server. 

## Kivy App
Source code for kivy app is located under ```gui/kivy_app.py```. This little UI consists of two slides: main and settings. 
At the main slide user sees live picture from the webcam directed onto pressure gauge of the steam machine model.
Circle together with arrow are also displayed, so that user can observe the recogniton process. The digital pressure value is located at the bottom left. 
<img width="700" alt="image" src="https://user-images.githubusercontent.com/71139952/181781776-7114d34c-5d09-4848-a278-f17e41169b8b.png">

Optionally user may change recogniton parameters in real time mode, so "settings" button is to be clicked. In this slide user sees solely contours 
of the recognized shapes. By adjusting the sliders at the right, the resulting picture can become more noisy and detailed, what may result in the undesired
recogniton of other other objects and lead therefore to the disturbances. 
<img width="700" alt="image" src="https://user-images.githubusercontent.com/71139952/181783024-e6dbd33a-9e22-4625-9e19-cc42f6fea8c1.png">

As soon as user clicks on "save changes" the adjusted parameters will be stored in working direction under ```datafile.json```. 
The advantage of that solution is that they canbe used repeatedly, i.e. they are not going to be deleted, as programm is closed or whatsoever.
## Pressure Calculation 

For calculating pressure it was important to find first circle edges, its centre and radius; also it will be necessary to know end coordinates of
the arrow. Pressure is calculated using by multiplying pressure/angle coefficient with the current angle. The coefficient can be found very easily,
since one bar has difference of 90°. Dividing 1 over 90 gives us the value of coefficient. Current angle of the arrow is found using archtangen, where 
perpendicular is divided over base. Both sides are calculated by substracting coordinates of the centre from end points of the arrow on the corresponding axis.
It must be noticed, that pixels at the vertical axis are incresing downwards and the same formula cannot be applied on all quadrants of the circle. 
So the position of the arrow with respect to quadrant must be determined first and corresponding formula is to be apllied than. 
Basically there were following formulae calculated:
<img width="700" alt="image" src="https://user-images.githubusercontent.com/71139952/181789761-a3bd005c-003e-4955-8001-2462c8fc0598.png">


## Django Backend

Django backend was used for transmitting the data on screens within the local network. For the real time data django server was set to be ASGI type. Data was stored using redis. The end result is represented as following:
![ezgif-5-27110f55b9](https://user-images.githubusercontent.com/71139952/181797282-2d81323d-c4b1-465a-b7b9-c321096b6422.gif)

# Personal thoughts

This project was for me completely new area. Although I didn't have any previous experience with Python, Django and Computer Vision with the help of God I could implement not only recogniton of the manometer, but also small user interface and played with web programming. Nevertheless the project doesn't pretend to be professional, since the recogniton suffers from external parameters, such as light, contrast and so on. The possible solution could be CNNs, which are also complicated, but more reliable, than solely geometrical recogniton patterns.
