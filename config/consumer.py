import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async

# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         # Obtener el ticket_id desde la URL
#         ticket_id = self.scope['url_route']['kwargs']['ticket_id']
#         ticket_type = self.scope['url_route']['kwargs']['ticket_type']

#         # Asignar el grupo de WebSocket según el tipo de ticket
#         self.room_group_name = f'ticket_{ticket_type}_{ticket_id}'

#         # Unirse a un grupo basado en el tipo de ticket y el ticket_id
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )

#         await self.accept()

#     async def disconnect(self, close_code):
#         # Dejar el grupo cuando se desconecta
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )

#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         mensaje = text_data_json['mensaje']
#         user_id = text_data_json['user_id']
#         ticket_id = text_data_json['ticket_id']
#         ticket_type = text_data_json['ticket_type']

#         # Obtener el usuario desde la base de datos
#         user = await sync_to_async(User.objects.get)(id=user_id)

#         # Determinar el tipo de ticket y asociar el mensaje con el ticket correcto
#         if ticket_type == 'pedido':
#             ticket = await sync_to_async(TicketPedido.objects.get)(id=ticket_id)
#         elif ticket_type == 'plataforma':
#             ticket = await sync_to_async(TicketPlataforma.objects.get)(id=ticket_id)
#         elif ticket_type == 'otros':
#             ticket = await sync_to_async(TicketOtros.objects.get)(id=ticket_id)
#         else:
#             return  # Si el tipo de ticket no es válido, no hacemos nada

#         # Crear el mensaje en la base de datos
#         chat = await sync_to_async(Chat.objects.create)(
#             mensaje=mensaje,
#             afiliado=user if user.is_authenticated else None,
#             proveedor=user if user.is_authenticated else None,
#             ticket_pedido=ticket if isinstance(ticket, TicketPedido) else None,
#             ticket_plataforma=ticket if isinstance(ticket, TicketPlataforma) else None,
#             ticket_otros=ticket if isinstance(ticket, TicketOtros) else None,
#             is_admin=False  # O True, dependiendo de la lógica de tu sistema
#         )

#         # Enviar el mensaje a todos los clientes conectados a este ticket
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'mensaje': mensaje,
#                 'user_id': user.id,
#                 'username': user.username,
#             }
#         )

#     async def chat_message(self, event):
#         mensaje = event['mensaje']
#         user_id = event['user_id']
#         username = event['username']

#         # Enviar el mensaje a WebSocket
#         await self.send(text_data=json.dumps({
#             'mensaje': mensaje,
#             'user_id': user_id,
#             'username': username,
#         }))
class NotificacionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            self.user = self.scope['user']  # Usuario autenticado
            self.user_id = self.scope['url_route']['kwargs']['user_id']

            logger.info(f"Intento de conexión WebSocket - User: {self.user}, User ID solicitado: {self.user_id}")

            # Verificar si el usuario está autenticado
            if self.user.is_anonymous:
                logger.warning(f"Usuario anónimo intentó conectarse al WebSocket para user_id: {self.user_id}")
                await self.close(code=4001)  # Código personalizado para "no autenticado"
                return

            # Verificar si el usuario tiene permiso para conectarse
            if int(self.user.id) != int(self.user_id):
                logger.warning(f"Usuario {self.user.id} intentó conectarse al WebSocket del usuario {self.user_id}")
                await self.close(code=4003)  # Código personalizado para "sin permiso"
                return

            # Crear un grupo único para el usuario
            self.room_group_name = f'notifications_{self.user.id}'

            # Agregar al usuario a su grupo
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            logger.info(f"Usuario {self.user.id} conectado exitosamente al WebSocket")
            await self.accept()
            
        except Exception as e:
            logger.error(f"Error en connect de NotificacionConsumer: {e}")
            await self.close(code=4000)  # Código personalizado para "error del servidor"

    async def disconnect(self, close_code):
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"WebSocket desconectado - Code: {close_code}, User: {getattr(self, 'user', 'unknown')}")
        
        # Eliminar al usuario del grupo al desconectarse
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def send_notification(self, event):
        # Enviar el mensaje al cliente
        notificacion = event['notification']
        texto = event['text']
        message = event.get('message', {})  # Diccionario con varios campos
        await self.send(text_data=json.dumps({
            'notification': notificacion,
            'text': texto,
            'message': message,
        }))
