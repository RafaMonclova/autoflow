import os
import random
import string
import secrets
import urllib.parse
from django.shortcuts import render, redirect
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from datetime import datetime as dt
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from apps.users.models import User
from rest_framework_simplejwt.views import TokenObtainPairView
from apps.users.serializers import CustomTokenObtainPairSerializer, CustomTokenRefreshSerializer, RegisterSerializer, UserSerializer, UserUpdateSerializer
from django_filters.rest_framework import DjangoFilterBackend
from apps.users.filters import UserFilter
from apps.users.permission import IsSelfOrSuperUser
from rest_framework.decorators import action
from django.contrib.auth.hashers import make_password
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.renderers import JSONRenderer
from django.core.cache import cache
from rest_framework_simplejwt.tokens import RefreshToken
import requests
from rest_framework.parsers import JSONParser
from apps.users.throttles import LoginThrottle


import jwt
import json
from jwt.algorithms import RSAAlgorithm
from django.conf import settings


# Create your views here.

class CustomLoginView(APIView):
    serializer_class = CustomTokenObtainPairSerializer
    throttle_classes = [LoginThrottle]

    @extend_schema(request=CustomTokenObtainPairSerializer)
    def post(self, request, *args, **kwargs):
        serializer = CustomTokenObtainPairSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CustomTokenRefreshView(APIView):
    serializer_class = CustomTokenRefreshSerializer

    @extend_schema(request=CustomTokenRefreshSerializer)
    def post(self, request, *args, **kwargs):
        serializer = CustomTokenRefreshSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class UserView(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsSelfOrSuperUser]
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserFilter
    parser_classes = (MultiPartParser, FormParser)
    
   
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    # override delete to disable it
    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = False if user.is_active else True
        user.save()
        return Response(status=status.HTTP_200_OK)
    
    
    @extend_schema(
        parameters=[
            OpenApiParameter("name", str, OpenApiParameter.QUERY, description="Search in username, first_name, or last_name"),
            OpenApiParameter("is_active", bool, OpenApiParameter.QUERY, description="Filter by active status (true/false)"),
        ]
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='export-excel')
    def export_excel(self, request):
        """Export users to Excel with applied filters (same as list endpoint)"""
        # Apply the same filters used in the list view
        queryset = self.filter_queryset(self.get_queryset())
        
        # Create workbook and worksheet
        wb = Workbook()
        ws = wb.active
        ws.title = "Usuarios"
        
        # Define headers
        headers = ['ID', 'Username', 'Nombre', 'Apellido', 'Email', 'Teléfono', 'Activo', 'Es Superuser', 'Fecha de Registro']
        ws.append(headers)
        
        # Style headers
        for cell in ws[1]:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal='center')
        
        # Add data
        for user in queryset:
            ws.append([
                user.id,
                user.username,
                user.first_name,
                user.last_name,
                user.email,
                user.phone_number if hasattr(user, 'phone_number') else '',
                'Sí' if user.is_active else 'No',
                'Sí' if user.is_superuser else 'No',
                user.date_joined.strftime('%Y-%m-%d %H:%M:%S') if user.date_joined else ''
            ])
        
        # Adjust column widths
        for column in ws.columns:
            max_length = 0
            column = list(column)
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 2)
            ws.column_dimensions[column[0].column_letter].width = adjusted_width
        
        # Prepare response
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        filename = f'usuarios_{dt.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        response['Content-Disposition'] = f'attachment; filename={filename}'
        
        wb.save(response)
        return response



class RegisterView(APIView):
    permission_classes = []
    serializer_class = RegisterSerializer

    @extend_schema(request=RegisterSerializer)
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'A one time password has sended to user phone number.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
