from apps.users.models import User
import uuid
from django.db import models


class Workflow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workflows')
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"

class Trigger(models.Model):
    TRIGGER_TYPES = (
        ('WEBHOOK', 'Webhook'),
        ('CRON', 'Cron'),
    )
    workflow = models.OneToOneField(Workflow, on_delete=models.CASCADE, related_name='trigger')
    trigger_type = models.CharField(max_length=50, choices=TRIGGER_TYPES)
    webhook_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, null=True, blank=True)
    cron_expression = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.get_trigger_type_display()} - {self.workflow.name}"

class Action(models.Model):
    ACTION_TYPES = (
        ('TELEGRAM', 'Telegram'),
        ('EMAIL', 'Email'),
        ('HTTP_FETCH', 'HTTP Fetch'),
    )
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='actions')
    order = models.PositiveIntegerField(default=0)
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    config_template = models.JSONField(default=dict, blank=True)
    sample_payload = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.order}. {self.get_action_type_display()} - {self.workflow.name}"
