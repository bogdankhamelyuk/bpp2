from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from graph_app.consumers import Consumer

import os 
os.environ.setdefault('DJANGO_SETTINGS_MODULE','realtime_graph.settings')


application = ProtocolTypeRouter({   #3
    'websocket' : 
        AuthMiddlewareStack(
            URLRouter(
                [
                    path('graph/upload/',Consumer.as_asgi()),#4
                ]
            )
        ),
})