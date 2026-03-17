import logging
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token

from rest_framework.exceptions import AuthenticationFailed


from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from apps.users.models import User

logger = logging.getLogger(__name__)


class TokenAuthMiddleware(BaseMiddleware):

    def decode_token(self, token):
        from rest_framework_simplejwt.tokens import UntypedToken
        from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

        try:
            return UntypedToken(token).payload
        except (InvalidToken, TokenError) as e:
            logger.warning(f"Token inválido: {e}")
            return None

    @database_sync_to_async
    def get_user(self, token_key):
        if not token_key:
            logger.warning("No se proporcionó token")
            return AnonymousUser()
        
        try:
            payload = self.decode_token(token_key)
            
            if not payload:
                logger.warning("Payload del token vacío o inválido")
                return AnonymousUser()

            user_id = payload.get("user_id")
            
            if not user_id:
                logger.warning("No se encontró user_id en el token")
                return AnonymousUser()

            user = User.objects.get(id=user_id)
            logger.info(f"Usuario autenticado: {user.id}")
            return user
            
        except User.DoesNotExist:
            logger.warning(f"Usuario no encontrado: {user_id}")
            return AnonymousUser()
        except Exception as e:
            logger.error(f"Error al autenticar usuario: {e}")
            return AnonymousUser()

    async def __call__(self, scope, receive, send):
        # Obtener el token desde la query string
        query_string = scope.get('query_string', b'').decode('utf-8')
        
        # Parse query params de forma segura
        query_params = {}
        if query_string:
            for param in query_string.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    query_params[key] = value
        
        token_key = query_params.get('token', None)
        
        logger.info(f"Token recibido: {token_key[:20]}..." if token_key else "Sin token")
        
        # Autenticar al usuario (nunca lanzar excepción, devolver AnonymousUser si falla)
        try:
            scope['user'] = await self.get_user(token_key)
        except Exception as e:
            logger.error(f"Error inesperado en autenticación: {e}")
            scope['user'] = AnonymousUser()

        # Continuar el flujo del middleware
        return await super().__call__(scope, receive, send)
