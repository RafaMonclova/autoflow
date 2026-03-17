from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_custom_email(to_email, subject, body):
    """
    Envía un correo electrónico utilizando el backend SMTP configurado en Django.
    """
    try:
        # Intenta obtener el correo origen configurado en settings.py, sino usa un por defecto
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@autoflow.local')
        
        send_mail(
            subject=subject,
            message=body,
            from_email=from_email,
            recipient_list=[to_email],
            fail_silently=False,
        )
        logger.info(f"Email enviado con éxito a {to_email}")
        return True
    except Exception as e:
        logger.error(f"Error al intentar enviar el email a {to_email}: {e}")
        return False
