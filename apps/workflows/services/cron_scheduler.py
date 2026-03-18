import json
import logging
from django_celery_beat.models import PeriodicTask, CrontabSchedule

logger = logging.getLogger(__name__)

TASK_NAME_PREFIX = "autoflow_cron_"


def _get_task_name(trigger):
    """Genera un nombre único para el PeriodicTask basado en el trigger."""
    return f"{TASK_NAME_PREFIX}{trigger.id}"


def _parse_cron_expression(cron_expression):
    """
    Parsea una expresión cron estándar de 5 campos:
    minute hour day_of_month month_of_year day_of_week
    
    Retorna un dict compatible con CrontabSchedule.
    """
    parts = cron_expression.strip().split()
    if len(parts) != 5:
        raise ValueError(
            f"Expresión cron inválida: '{cron_expression}'. "
            f"Se esperan 5 campos (minute hour day_of_month month_of_year day_of_week)."
        )
    
    return {
        'minute': parts[0],
        'hour': parts[1],
        'day_of_month': parts[2],
        'month_of_year': parts[3],
        'day_of_week': parts[4],
    }


def sync_cron_to_beat(trigger):
    """
    Sincroniza un Trigger de tipo CRON con un PeriodicTask de django_celery_beat.
    Crea o actualiza tanto el CrontabSchedule como el PeriodicTask.
    """
    if trigger.trigger_type != 'CRON' or not trigger.cron_expression:
        logger.warning(f"Trigger {trigger.id} no es CRON o no tiene cron_expression.")
        return
    
    # 1. Parsear la expresión cron
    cron_fields = _parse_cron_expression(trigger.cron_expression)
    
    # 2. Crear o reutilizar el CrontabSchedule
    schedule, _ = CrontabSchedule.objects.get_or_create(**cron_fields)
    
    # 3. Crear o actualizar el PeriodicTask
    task_name = _get_task_name(trigger)
    
    PeriodicTask.objects.update_or_create(
        name=task_name,
        defaults={
            'task': 'apps.engine.tasks.execute_workflow_task',
            'crontab': schedule,
            'args': json.dumps([trigger.id, {}]),  # trigger_id, payload vacío
            'enabled': trigger.workflow.is_active,
        }
    )
    
    logger.info(f"PeriodicTask '{task_name}' sincronizado con cron '{trigger.cron_expression}'.")


def delete_cron_beat_task(trigger):
    """
    Elimina el PeriodicTask asociado a un trigger CRON.
    """
    task_name = _get_task_name(trigger)
    deleted_count, _ = PeriodicTask.objects.filter(name=task_name).delete()
    
    if deleted_count:
        logger.info(f"PeriodicTask '{task_name}' eliminado.")


def set_cron_beat_active(trigger, is_active):
    """
    Activa o desactiva el PeriodicTask asociado a un trigger CRON
    sin eliminarlo.
    """
    task_name = _get_task_name(trigger)
    updated = PeriodicTask.objects.filter(name=task_name).update(enabled=is_active)
    
    if updated:
        state = "activado" if is_active else "desactivado"
        logger.info(f"PeriodicTask '{task_name}' {state}.")
