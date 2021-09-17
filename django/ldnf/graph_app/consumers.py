from asgiref.sync import async_to_sync
import json 
from channels.exceptions import StopConsumer 
from channels.generic.websocket import JsonWebsocketConsumer
from .models import Message

class Consumer(JsonWebsocketConsumer):#5
    def __init__(self, *args, **kwargs):
        super(Consumer, self).__init__(*args, **kwargs)

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
        #msg = Message(pressure=pressure)
        #msg.save()
        print("receive. Pressure is: ", pressure)
        
        async_to_sync(self.channel_layer.group_send)(
            self.room_name,{
                "type": 'send_message_to_frontend',
                "pressure": pressure
            }
        )
    
    def send_message_to_frontend(self,event):
        print("EVENT TRIGERED")
        # Receive message from room group
        message = event['pressure']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'pressure': message
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

        raise StopConsumer()