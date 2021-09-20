import json
import websocket
import time
import datetime
from random import randint

ws = websocket.WebSocket()
ws.connect("ws://127.0.0.1:8000/graph/upload/")
i=0
for i in range(1000):
    print(i)
    value = randint(0, 10)
    now = datetime.datetime.now()
    timestamp = datetime.datetime.timestamp(now)
    if i == 0:
        a = {'pressure': value,'time' : 0}
        first_time=timestamp
    else:
        time_diff = timestamp - first_time
        time_diff = round(time_diff,1)
        a = {'pressure': value,'time' : time_diff}
    b = json.dumps(a).encode('utf-8')
    ws.send(b)
    time.sleep(1)
    

ws.close()
