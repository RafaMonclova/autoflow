# Script para crear una nueva app con la estructura recomendada
# Uso: .\create_app.ps1 -AppName "nombre_app"

param(
    [Parameter(Mandatory=$true)]
    [string]$AppName
)

Write-Host "=" -ForegroundColor Cyan
Write-Host "Creando nueva app: $AppName" -ForegroundColor Cyan
Write-Host "=" -ForegroundColor Cyan
Write-Host ""

$projectRoot = $PSScriptRoot
$appPath = "$projectRoot\apps\$AppName"

# Verificar que estamos en el directorio correcto
if (-not (Test-Path "$projectRoot\manage.py")) {
    Write-Host "Error: No se encuentra manage.py en el directorio actual" -ForegroundColor Red
    exit 1
}

# Verificar que la app no existe
if (Test-Path $appPath) {
    Write-Host "Error: La app '$AppName' ya existe en apps/" -ForegroundColor Red
    exit 1
}

# Crear estructura de carpetas
Write-Host "Creando estructura de carpetas..." -ForegroundColor Cyan
New-Item -ItemType Directory -Path "$appPath" -Force | Out-Null
New-Item -ItemType Directory -Path "$appPath\api" -Force | Out-Null
New-Item -ItemType Directory -Path "$appPath\services" -Force | Out-Null
New-Item -ItemType Directory -Path "$appPath\migrations" -Force | Out-Null

# Crear __init__.py principal
@"
# $AppName app
"@ | Out-File -FilePath "$appPath\__init__.py" -Encoding utf8

# Crear apps.py
$appNameCapitalized = (Get-Culture).TextInfo.ToTitleCase($AppName)
@"
from django.apps import AppConfig


class ${appNameCapitalized}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.$AppName'
"@ | Out-File -FilePath "$appPath\apps.py" -Encoding utf8

# Crear models.py
@"
from django.db import models

# Create your models here.
"@ | Out-File -FilePath "$appPath\models.py" -Encoding utf8

# Crear serializers.py
@"
from rest_framework import serializers

# Create your serializers here.
"@ | Out-File -FilePath "$appPath\serializers.py" -Encoding utf8

# Crear filters.py
@"
from django_filters import rest_framework as filters

# Create your filters here.
"@ | Out-File -FilePath "$appPath\filters.py" -Encoding utf8

# Crear permission.py
@"
from rest_framework.permissions import BasePermission

# Create your custom permissions here.
"@ | Out-File -FilePath "$appPath\permission.py" -Encoding utf8

# Crear admin.py
@"
from django.contrib import admin

# Register your models here.
"@ | Out-File -FilePath "$appPath\admin.py" -Encoding utf8

# Crear tests.py
@"
from django.test import TestCase

# Create your tests here.
"@ | Out-File -FilePath "$appPath\tests.py" -Encoding utf8

# Crear api/__init__.py
@"
# API package
"@ | Out-File -FilePath "$appPath\api\__init__.py" -Encoding utf8

# Crear api/views.py
@"
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Create your views here.
"@ | Out-File -FilePath "$appPath\api\views.py" -Encoding utf8

# Crear api/urls.py
@"
from django.urls import path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# router.register(r'endpoint', YourViewSet)

urlpatterns = [
    # Add your custom paths here
]

urlpatterns += router.urls
"@ | Out-File -FilePath "$appPath\api\urls.py" -Encoding utf8

# Crear services/__init__.py
@"
# Services package for complex business logic
"@ | Out-File -FilePath "$appPath\services\__init__.py" -Encoding utf8

# Crear migrations/__init__.py
@"
# Migrations
"@ | Out-File -FilePath "$appPath\migrations\__init__.py" -Encoding utf8

Write-Host ""
Write-Host "App '$AppName' creada exitosamente!" -ForegroundColor Green
Write-Host ""
Write-Host "Estructura creada:" -ForegroundColor Cyan
Write-Host "apps/$AppName/" -ForegroundColor White
Write-Host "  __init__.py" -ForegroundColor Gray
Write-Host "  apps.py" -ForegroundColor Gray
Write-Host "  models.py" -ForegroundColor Gray
Write-Host "  serializers.py" -ForegroundColor Gray
Write-Host "  filters.py" -ForegroundColor Gray
Write-Host "  permission.py" -ForegroundColor Gray
Write-Host "  admin.py" -ForegroundColor Gray
Write-Host "  tests.py" -ForegroundColor Gray
Write-Host "  api/" -ForegroundColor White
Write-Host "    __init__.py" -ForegroundColor Gray
Write-Host "    views.py" -ForegroundColor Gray
Write-Host "    urls.py" -ForegroundColor Gray
Write-Host "  services/" -ForegroundColor White
Write-Host "    __init__.py" -ForegroundColor Gray
Write-Host "  migrations/" -ForegroundColor White
Write-Host "    __init__.py" -ForegroundColor Gray
Write-Host ""
Write-Host "Próximos pasos:" -ForegroundColor Cyan
Write-Host "1. Agrega 'apps.$AppName' a INSTALLED_APPS en config/settings.py" -ForegroundColor Yellow
Write-Host "2. Incluye las URLs en config/urls.py:" -ForegroundColor Yellow
Write-Host "   path('apiweb/', include('apps.$AppName.api.urls'))," -ForegroundColor White
Write-Host "3. Crea tus modelos en apps/$AppName/models.py" -ForegroundColor Yellow
Write-Host "4. Ejecuta: python manage.py makemigrations" -ForegroundColor Yellow
Write-Host "5. Ejecuta: python manage.py migrate" -ForegroundColor Yellow
Write-Host ""
