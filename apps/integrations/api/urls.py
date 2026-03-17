from django.urls import path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# router.register(r'endpoint', YourViewSet)

urlpatterns = [
    # Add your custom paths here
]

urlpatterns += router.urls
