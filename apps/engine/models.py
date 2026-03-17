from django.db import models

class ExecutionHistory(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    )
    
    # Resolving via string to avoid circular dependency
    workflow = models.ForeignKey('workflows.Workflow', on_delete=models.CASCADE, related_name='executions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    payload_received = models.JSONField(default=dict, blank=True, null=True)
    error_log = models.TextField(blank=True, null=True)
    executed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-executed_at']

    def __str__(self):
        return f"Execution {self.id} for {self.workflow.name} - {self.status}"
