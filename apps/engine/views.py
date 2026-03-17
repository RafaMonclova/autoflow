import json
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from apps.workflows.models import Trigger
from apps.engine.tasks import execute_workflow_task

@method_decorator(csrf_exempt, name='dispatch')
class WebhookReceiveView(View):
    def post(self, request, uuid, *args, **kwargs):
        # 1. Validar que el UUID existe y es de un trigger tipo WEBHOOK
        try:
            trigger = Trigger.objects.select_related('workflow').get(
                webhook_uuid=uuid, 
                trigger_type='WEBHOOK'
            )
        except Trigger.DoesNotExist:
            return JsonResponse({'error': 'Webhook not found or invalid'}, status=404)
        
        # 2. Verificar que el flujo está activo
        if not trigger.workflow.is_active:
            return JsonResponse({'error': 'Workflow is not active'}, status=400)
            
        # 3. Extraer el payload (JSON) de la request
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            # Si no es JSON válido, usamos un diccionario vacío o podríamos devolver error 400
            payload = {}

        # 4. Enviar a Celery (ejecución asíncrona)
        # Pasamos el trigger.id y el payload
        execute_workflow_task.delay(trigger.id, payload)
        
        # 5. Responder inmediatamente HTTP 202 Accepted
        return JsonResponse(
            {'status': 'Accepted', 'message': 'Webhook received and processing started'}, 
            status=202
        )
