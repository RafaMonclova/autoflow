import logging
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)


def send_web_notification(user_id, title, body):
    """
    Envía una notificación en tiempo real al navegador del usuario
    a través del WebSocket (NotificacionConsumer).
    """
    channel_layer = get_channel_layer()

    if not channel_layer:
        logger.error("Channel layer no disponible. ¿Está configurado CHANNEL_LAYERS?")
        return False

    group_name = f"notifications_{user_id}"

    try:
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "send_notification",
                "notification": title,
                "text": body,
                "message": {
                    "title": title,
                    "body": body,
                    "source": "workflow",
                },
            },
        )
        logger.info(f"Notificación web enviada al usuario {user_id}: {title}")
        return True
    except Exception as e:
        logger.error(f"Error enviando notificación web al usuario {user_id}: {e}")
        return False
