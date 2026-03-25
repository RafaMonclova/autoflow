import traceback
import requests
from celery import shared_task
from apps.workflows.models import Trigger
from apps.engine.models import ExecutionHistory
from apps.engine.parser import parse_template_with_payload, get_nested_value, extract_wildcard_path, replace_wildcard_with_index

# Importamos las integraciones
from apps.integrations.telegram import send_telegram_message
from apps.integrations.email import send_custom_email
from apps.integrations.notification import send_web_notification

def _execute_single_action(action_type, parsed_config, current_payload, step_key, user_id=None):
    """
    Ejecuta una acción individual. Si es HTTP_FETCH, inyecta su resultado en current_payload.
    """
    if action_type == 'TELEGRAM':
        chat_id = parsed_config.get('chat_id')
        text = parsed_config.get('text')
        
        if chat_id and text:
            success = send_telegram_message(chat_id, text)
            if not success:
                raise Exception("Fallo en la API de Telegram al enviar el mensaje.")
        else:
            raise ValueError("Faltan 'chat_id' o 'text' en el config parseado de TELEGRAM.")
            
    elif action_type == 'EMAIL':
        to_email = parsed_config.get('to_email')
        subject = parsed_config.get('subject')
        body = parsed_config.get('body')
        
        if to_email and subject and body:
            success = send_custom_email(to_email, subject, body)
            if not success:
                raise Exception("Fallo en el servicio SMTP al enviar el correo.")
        else:
            raise ValueError("Faltan 'to_email', 'subject' o 'body' en el config parseado de EMAIL.")
            
    elif action_type == 'HTTP_FETCH':
        url = parsed_config.get('url')
        if url:
            # Ejecutamos la petición HTTP en tiempo real para el motor
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            # Inyectamos el resultado en el payload global para las siguientes acciones
            current_payload[step_key] = response.json()
        else:
            raise ValueError("Falta 'url' en el config parseado de HTTP_FETCH.")

    elif action_type == 'WEB_NOTIFICATION':
        title = parsed_config.get('title')
        body = parsed_config.get('body')

        if title and body:
            if not user_id:
                raise ValueError("No se pudo determinar el user_id del propietario del workflow.")
            success = send_web_notification(user_id, title, body)
            if not success:
                raise Exception("Fallo al enviar la notificación web por WebSocket.")
        else:
            raise ValueError("Faltan 'title' o 'body' en el config parseado de WEB_NOTIFICATION.")
            
    else:
        raise ValueError(f"Tipo de acción desconocido o no implementado: '{action_type}'")

@shared_task
def execute_workflow_task(trigger_id, payload):
    """
    Tarea central de Celery que procesa un webhook entrante ejecutando todas las acciones de su flujo.
    Soporta iteración de listas si alguna acción está configurada con rutas comodín [*].
    """
    
    # 1. Obtener el Trigger y su Workflow asociado
    try:
        trigger = Trigger.objects.select_related('workflow').get(id=trigger_id)
    except Trigger.DoesNotExist:
        # El webhook puede haber sido procesado por un trigger que luego fue borrado
        return f"Trigger ID {trigger_id} no encontrado."

    workflow = trigger.workflow
    
    # 2. Crear un registro en ExecutionHistory con estado "PENDING"
    execution = ExecutionHistory.objects.create(
        workflow=workflow,
        status='PENDING',
        payload_received=payload
    )

    try:
        # 3. Iterar sobre todas las Action asociadas, ordenadas por el campo 'order'
        actions = workflow.actions.all().order_by('order')
        
        # El payload irá mutando: inyectaremos step1, step2, etc. a medida que vengan Fetch
        # Clona el payload inicial (del Webhook) por seguridad
        current_payload = dict(payload) if payload else {}
        
        for action in actions:
            step_key = f"step{action.order}"
            
            # 4. Comprobar si hay comodines de iteración [*] en la configuración
            wildcard_base = extract_wildcard_path(action.config_template)
            
            if wildcard_base:
                # La acción necesita iterarse. Extraemos la lista original iteradora.
                lista_datos = get_nested_value(current_payload, wildcard_base, default=None)
                
                if isinstance(lista_datos, list):
                    # Iteramos ejecutando la acción N veces, una por cada elemento de la lista
                    for i in range(len(lista_datos)):
                        # Reemplazamos [*] por el índice actual numérico (.0, .1)
                        indexed_config = replace_wildcard_with_index(action.config_template, i)
                        parsed_config = parse_template_with_payload(indexed_config, current_payload)
                        _execute_single_action(action.action_type, parsed_config, current_payload, f"{step_key}_{i}", user_id=workflow.user_id)
                else:
                    raise ValueError(f"La variable comodín '{wildcard_base}' no devuelve una lista válida para iterar.")
            else:
                # Flujo normal para acciones que no sean bucles o en caso de diccionarios planos
                parsed_config = parse_template_with_payload(action.config_template, current_payload)
                _execute_single_action(action.action_type, parsed_config, current_payload, step_key, user_id=workflow.user_id)

        # 5. Actualizar el ExecutionHistory a "SUCCESS"
        execution.status = 'SUCCESS'
        execution.save()
        
        return f"Workflow '{workflow.name}' ejecutado EXITOSAMENTE (Execution ID: {execution.id})."

    except Exception as e:
        # Si hubo una excepción guardamos el error en el historial
        execution.status = 'FAILED'
        # Guardamos el mensaje de error de la excepción y el traceback detallado
        execution.error_log = f"Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        execution.save()
        
        return f"Workflow '{workflow.name}' FALLÓ (Execution ID: {execution.id}). Error capturado."
