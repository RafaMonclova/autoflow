import json
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .models import Workflow, Trigger, Action
from .services.cron_scheduler import sync_cron_to_beat, delete_cron_beat_task, set_cron_beat_active

class DashboardView(LoginRequiredMixin, ListView):
    model = Workflow
    template_name = 'workflows/dashboard.html'
    context_object_name = 'workflows'
    
    def get_queryset(self):
        return Workflow.objects.filter(user=self.request.user).order_by('-created_at')

class WorkflowBuilderView(LoginRequiredMixin, DetailView):
    model = Workflow
    template_name = 'workflows/builder.html'
    context_object_name = 'workflow'
    
    def get_queryset(self):
        return Workflow.objects.filter(user=self.request.user)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        workflow = self.get_object()
        trigger, created = Trigger.objects.get_or_create(
            workflow=workflow,
            defaults={'trigger_type': 'WEBHOOK'}
        )
        context['trigger'] = trigger
        context['actions'] = workflow.actions.all().order_by('order')
        return context

@login_required
@require_POST
def create_workflow(request):
    workflow = Workflow.objects.create(
        user=request.user,
        name=f"Nuevo Flujo {Workflow.objects.filter(user=request.user).count() + 1}"
    )
    Trigger.objects.create(workflow=workflow, trigger_type='WEBHOOK')
    return redirect('workflow_builder', pk=workflow.pk)

@login_required
@require_POST
def toggle_workflow_status(request, pk):
    workflow = get_object_or_404(Workflow, pk=pk, user=request.user)
    workflow.is_active = not workflow.is_active
    workflow.save()
    
    # Sincronizar estado con Celery Beat si es CRON
    if hasattr(workflow, 'trigger') and workflow.trigger.trigger_type == 'CRON':
        set_cron_beat_active(workflow.trigger, workflow.is_active)
    
    return render(request, 'workflows/partials/toggle_button.html', {'workflow': workflow})

@login_required
@require_POST
def delete_workflow(request, pk):
    workflow = get_object_or_404(Workflow, pk=pk, user=request.user)
    
    # Limpiar PeriodicTask de Celery Beat si es CRON
    if hasattr(workflow, 'trigger') and workflow.trigger.trigger_type == 'CRON':
        delete_cron_beat_task(workflow.trigger)
    
    workflow.delete()
    return redirect('dashboard')

@login_required
@require_POST
def save_trigger_config(request, trigger_id):
    trigger = get_object_or_404(Trigger, pk=trigger_id, workflow__user=request.user)
    old_type = trigger.trigger_type
    trigger_type = request.POST.get('trigger_type')
    
    if trigger_type in dict(Trigger.TRIGGER_TYPES):
        trigger.trigger_type = trigger_type
        if trigger_type == 'CRON':
            trigger.cron_expression = request.POST.get('cron_expression', '* * * * *')
        trigger.save()
        
        # Sincronizar con Celery Beat
        if trigger_type == 'CRON':
            sync_cron_to_beat(trigger)
        elif old_type == 'CRON' and trigger_type != 'CRON':
            # Si cambió de CRON a otro tipo, eliminar la tarea periódica
            delete_cron_beat_task(trigger)
        
    return render(request, 'workflows/partials/trigger_block.html', {'trigger': trigger})

@login_required
@require_POST
def rename_workflow(request, pk):
    workflow = get_object_or_404(Workflow, pk=pk, user=request.user)
    new_name = request.POST.get('name', '').strip()
    if new_name:
        workflow.name = new_name
        workflow.save()
    return render(request, 'workflows/partials/workflow_name.html', {'workflow': workflow})

@login_required
def add_action_fragment(request, pk):
    workflow = get_object_or_404(Workflow, pk=pk, user=request.user)
    last_action = workflow.actions.order_by('order').last()
    next_order = last_action.order + 1 if last_action else 0
    action = Action.objects.create(
        workflow=workflow,
        order=next_order,
        action_type='TELEGRAM',
        config_template={"chat_id": "", "text": ""}
    )
    return render(request, 'workflows/partials/action_card.html', {'action': action, 'workflow': workflow})

@login_required
@require_POST
def save_action_config(request, action_id):
    action = get_object_or_404(Action, pk=action_id, workflow__user=request.user)
    action_type = request.POST.get('action_type')
    config_data = {}
    
    if action_type == 'TELEGRAM':
        config_data = {
            'chat_id': request.POST.get('telegram_chat_id', ''),
            'text': request.POST.get('telegram_text', '')
        }
    elif action_type == 'EMAIL':
        config_data = {
            'to_email': request.POST.get('email_to', ''),
            'subject': request.POST.get('email_subject', ''),
            'body': request.POST.get('email_body', '')
        }
    elif action_type == 'HTTP_FETCH':
        config_data = {
            'url': request.POST.get('fetch_url', '')
        }
        
    action.action_type = action_type
    action.config_template = config_data
    action.save()
    return HttpResponse('<span class="text-emerald-600 text-sm font-medium mr-4 flex items-center"><svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>¡Guardado!</span>')

@login_required
@require_POST
def delete_action(request, action_id):
    action = get_object_or_404(Action, pk=action_id, workflow__user=request.user)
    action.delete()
    return HttpResponse('')

import requests
from apps.engine.utils import flatten_json

@login_required
@require_POST
def test_action_fetch(request, action_id):
    action = get_object_or_404(Action, pk=action_id, workflow__user=request.user)
    
    if action.action_type != 'HTTP_FETCH':
        return HttpResponse('<span class="text-red-600 text-sm">Acción no es HTTP Fetch</span>')
        
    url = action.config_template.get('url')
    if not url:
        return HttpResponse('<span class="text-red-600 text-sm">URL no configurada. Guárdala primero.</span>')
        
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        action.sample_payload = data
        action.save()
        
        message = f"✅ Datos obtenidos"
        return HttpResponse(f'<span class="text-emerald-600 text-sm font-medium">{message}</span>')
    except Exception as e:
        return HttpResponse(f'<span class="text-red-600 text-sm">❌ Error: {str(e)}</span>')

@login_required
def available_variables(request, pk):
    """Devuelve las píldoras de las variables disponibles en un workflow (de webhooks o fetch previos)."""
    workflow = get_object_or_404(Workflow, pk=pk, user=request.user)
    variables = {}
    
    # Payload general desde acciones HTTP_FETCH
    for action in workflow.actions.filter(action_type='HTTP_FETCH').order_by('order'):
        if action.sample_payload:
            flat = flatten_json(action.sample_payload)
            for k, v in flat.items():
                variables[f"step{action.order}.{k}"] = v
                
    return render(request, 'workflows/partials/variables_pills.html', {'variables': variables})
