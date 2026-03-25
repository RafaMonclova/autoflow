from rest_framework_simplejwt.tokens import AccessToken


def websocket_token(request):
    """
    Context processor que genera un JWT de corta duración
    para autenticar la conexión WebSocket desde el frontend.
    """
    if request.user.is_authenticated:
        token = AccessToken.for_user(request.user)
        return {
            'ws_token': str(token),
            'ws_user_id': request.user.id,
        }
    return {}
