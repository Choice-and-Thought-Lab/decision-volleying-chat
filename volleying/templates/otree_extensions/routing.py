from django.conf.urls import url
from ..consumers import VolleyingConsumer
from otree.channels.routing import websocket_routes


websocket_routes += [
    url(r'^volleying/(?P<params>[\w,]+)/$',
        VolleyingConsumer),
]


# Uncomment this line to print websocket_routes for troubleshooting
print("websocket_routes="+str(websocket_routes))