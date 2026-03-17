import os
import requests
import logging

logger = logging.getLogger(__name__)

def send_telegram_message(chat_id, text):
    """
    Envía un mensaje HTTP POST a la API de Telegram.
    El token del bot debe estar en las variables de entorno como TELEGRAM_BOT_TOKEN.
    """
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN no configurado en entorno.")
        return False
        
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        # Lanza excepción si el código de estado no es 2xx
        response.raise_for_status() 
        logger.info(f"Mensaje de Telegram enviado con éxito a {chat_id}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Error enviando mensaje de Telegram: {e}")
        return False
