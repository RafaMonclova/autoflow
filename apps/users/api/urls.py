from django.urls import path
from rest_framework.routers import DefaultRouter
from apps.users.api.views import CustomLoginView, CustomTokenRefreshView, RegisterView, UserView

router = DefaultRouter()
router.register(r'users', UserView)

urlpatterns = [
    path('auth/login/', CustomLoginView.as_view(), name='login'),  # Login
    path('auth/refresh/', CustomTokenRefreshView.as_view(), name='refresh'),  # Refresh
    path('register/', RegisterView.as_view(), name='register'), # Register
]

urlpatterns += router.urls
