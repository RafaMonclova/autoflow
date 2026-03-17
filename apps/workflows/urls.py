from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('login/', LoginView.as_view(template_name='workflows/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

    # Vistas principales
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('create/', views.create_workflow, name='create_workflow'),
    path('builder/<int:pk>/', views.WorkflowBuilderView.as_view(), name='workflow_builder'),
    
    # Endpoints HTMX y acciones backend
    path('delete/<int:pk>/', views.delete_workflow, name='delete_workflow'),
    path('htmx/toggle/<int:pk>/', views.toggle_workflow_status, name='toggle_workflow_status'),
    path('htmx/trigger/save/<int:trigger_id>/', views.save_trigger_config, name='save_trigger_config'),
    path('htmx/action/add/<int:pk>/', views.add_action_fragment, name='add_action_fragment'),
    path('htmx/action/save/<int:action_id>/', views.save_action_config, name='save_action_config'),
    path('htmx/action/delete/<int:action_id>/', views.delete_action, name='delete_action'),
    path('htmx/action/test-fetch/<int:action_id>/', views.test_action_fetch, name='test_action_fetch'),
    path('htmx/workflow/<int:pk>/variables/', views.available_variables, name='available_variables'),
]
