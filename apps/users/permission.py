from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsSelfOrSuperUser(BasePermission):
    """
    Permite edición solo si el usuario es superusuario o está editando su propio perfil.
    """

    def has_object_permission(self, request, view, obj):
        # Permitir métodos seguros (GET, HEAD, OPTIONS) a cualquier autenticado
        if request.method in SAFE_METHODS:
            return True

        # Permitir PUT/PATCH/DELETE solo si es superusuario o si el usuario está editando su propio perfil
        return request.user.is_superuser or request.user.id == obj.id
