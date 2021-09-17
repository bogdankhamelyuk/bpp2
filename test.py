import json
import websocket
import time
ws = websocket.WebSocket()
ws.connect("ws://127.0.0.1:8000/graph/upload/")
i=0
for i in range(1000):
    print(i)
    
    a = {'pressure': i}
    b = json.dumps(a).encode('utf-8')
    ws.send(b)
    time.sleep(1)
    

ws.close()