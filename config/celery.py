import os
import django
from celery import Celery
from celery.signals import task_prerun, task_postrun, task_failure

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

app = Celery('autoflow')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()



@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **extra_kwargs):
    print(f"[CELERY] Tarea iniciada: {task.name} (ID: {task_id}) con args={args}, kwargs={kwargs}")


@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, retval=None, **extra_kwargs):
    print(f"[CELERY] Tarea completada: {task.name} (ID: {task_id}) con resultado: {retval}")


@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, args=None, kwargs=None, traceback=None, einfo=None, **extra_kwargs):
    print(f"[CELERY] ERROR en tarea {sender.name} (ID: {task_id}): {exception}")
    print(f"[CELERY] Traceback: {traceback}")
