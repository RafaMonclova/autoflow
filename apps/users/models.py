from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

from django.utils.translation import gettext_lazy as _
from enum import Enum

class Gender(Enum):
    masculine = 'M'
    feminine = 'F'
    other = 'O'
    

class User(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True, unique=True)
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(
        max_length=1,
        choices=[(gender.value, gender.name.capitalize()) for gender in Gender],
        blank=True,
        null=True
    )    
    role = models.ForeignKey(
        'Role',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='users'
    )

class Role (models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
