"""
Custom management command to create apps in the apps/ directory
Usage: python manage.py startapp_custom <app_name>

This command creates a new Django app in the apps/ directory with the following structure:
apps/
  <app_name>/
    __init__.py
    admin.py
    apps.py
    models.py
    serializers.py
    filters.py
    permission.py
    tests.py
    api/
      __init__.py
      views.py
      urls.py
    services/
      __init__.py
    migrations/
      __init__.py
"""
import os
from django.core.management.base import BaseCommand, CommandError
from pathlib import Path


class Command(BaseCommand):
    help = 'Creates a new Django app in the apps/ directory with the recommended structure'

    def add_arguments(self, parser):
        parser.add_argument('app_name', type=str, help='Name of the app to create')

    def handle(self, *args, **options):
        app_name = options['app_name']
        base_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
        apps_dir = base_dir / 'apps'
        app_path = apps_dir / app_name

        if app_path.exists():
            raise CommandError(f"La app '{app_name}' ya existe en apps/")

        self.stdout.write(f'Creating app {app_name} in apps/ directory...')

        # Create directory structure
        (app_path / 'api').mkdir(parents=True)
        (app_path / 'services').mkdir()
        (app_path / 'migrations').mkdir()

        app_name_cap = app_name.capitalize()

        # Root files
        (app_path / '__init__.py').write_text('')
        (app_path / 'admin.py').write_text('from django.contrib import admin\n\n# Register your models here.\n')
        (app_path / 'apps.py').write_text(
            f'from django.apps import AppConfig\n\n\nclass {app_name_cap}Config(AppConfig):\n'
            f"    default_auto_field = 'django.db.models.BigAutoField'\n"
            f"    name = 'apps.{app_name}'\n"
        )
        (app_path / 'models.py').write_text('from django.db import models\n\n# Create your models here.\n')
        (app_path / 'serializers.py').write_text('from rest_framework import serializers\n\n# Create your serializers here.\n')
        (app_path / 'filters.py').write_text('from django_filters import rest_framework as filters\n\n# Create your filters here.\n')
        (app_path / 'permission.py').write_text('from rest_framework.permissions import BasePermission\n\n# Create your custom permissions here.\n')
        (app_path / 'tests.py').write_text('from django.test import TestCase\n\n# Create your tests here.\n')

        # api/
        (app_path / 'api' / '__init__.py').write_text('')
        (app_path / 'api' / 'views.py').write_text(
            'from rest_framework.viewsets import ModelViewSet\n'
            'from rest_framework.permissions import IsAuthenticated\n\n'
            '# Create your views here.\n'
        )
        (app_path / 'api' / 'urls.py').write_text(
            'from django.urls import path\n'
            'from rest_framework.routers import DefaultRouter\n\n'
            'router = DefaultRouter()\n'
            '# router.register(r\'endpoint\', YourViewSet)\n\n'
            'urlpatterns = [\n'
            '    # Add your custom paths here\n'
            ']\n\n'
            'urlpatterns += router.urls\n'
        )

        # services/
        (app_path / 'services' / '__init__.py').write_text('')

        # migrations/
        (app_path / 'migrations' / '__init__.py').write_text('')

        self.stdout.write(self.style.SUCCESS(f'App "{app_name}" creada en apps/{app_name}/'))
        self.stdout.write(self.style.WARNING(f"Agrega 'apps.{app_name}' a INSTALLED_APPS en config/settings.py"))
        self.stdout.write(self.style.SUCCESS(f'Don\'t forget to add "apps.{app_name}" to INSTALLED_APPS in settings.py'))
