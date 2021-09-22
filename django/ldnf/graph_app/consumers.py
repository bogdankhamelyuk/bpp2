from asgiref.sync import async_to_sync
import json 
from channels.exceptions import StopConsumer 
from channels.generic.websocket import JsonWebsocketConsumer
from .models import Pressure
from datetime import datetime

class Consumer(JsonWebsocketConsumer):#5
    def __init__(self, *args, **kwargs):
        super(Consumer, self).__init__(*args, **kwargs)
        self.i=0
    def websocket_connect(self,event):
        self.room_name = 'event'
        async_to_sync(self.channel_layer.group_add)(
            self.room_name,
            self.channel_name
        ) 
        self.accept()
        #self.send(json.dumps({'value': 10}))
        print("''''''''''''''''CONNECTED''''''''''''''''")
        
    def websocket_receive(self, content):
        text = content["text"]
        data = json.loads(text) 
        pressure = data["pressure"]
        time_of_measure = data["time"]
        print("receive. Pressure is: ", pressure)
        pressure_db = Pressure(pressure=pressure,timestamp=time_of_measure)
        pressure_db.save()#,timestamp=time_of_measure,number_of_measure=self.i).save()
       
        async_to_sync(self.channel_layer.group_send)(
            self.room_name,{
                "type": 'send_message_to_frontend',
                "message": "ok"
            }
        )
    
    def send_message_to_frontend(self,event):
        #print("EVENT TRIGERED")
        # Receive message from room group
        message = event['message']
        self.send(text_data=json.dumps({
            'message': message,
        }))

    def websocket_disconnect(self, code):
        print("'''''''''''''''disconnected'''''''''''''''")
        #await self.close()
        #Message.objects.all().delete()
        async_to_sync(self.channel_layer.group_discard)(
            self.room_name,
            self.channel_name
        )
        print("DISCONNECTED CODE: ",code)
        Pressure.objects.all().delete()
        
        raise StopConsumer()