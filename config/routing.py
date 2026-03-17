from django.urls import re_path
from . import consumer

websocket_urlpatterns = [
    #re_path(r'ws/chat/(?P<ticket_type>pedido|plataforma|otros)/(?P<ticket_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
    #re_path(r'ws/notificaciones/global/$', consumer.NotificacionConsumer.as_asgi()),
    re_path(r'ws/notifications/(?P<user_id>\d+)/$', consumer.NotificacionConsumer.as_asgi()),
    re_path(r'wss/notifications/(?P<user_id>\d+)/$', consumer.NotificacionConsumer.as_asgi()),
]
