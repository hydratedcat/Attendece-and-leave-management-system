from django.db import models
from django.conf import settings
from django_fsm import FSMField, transition


class LeaveRequest(models.Model):
    LEAVE_TYPES = [
        ('SICK', 'Sick'),
        ('CASUAL', 'Casual'),
        ('EARNED', 'Earned'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    employee = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='leave_requests', on_delete=models.CASCADE)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='managed_leaves', on_delete=models.SET_NULL, null=True, blank=True)
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = FSMField(default='PENDING', choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['employee', 'status']),
            models.Index(fields=['manager', 'status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['start_date', 'end_date']),
        ]

    @transition(field=status, source='PENDING', target='APPROVED')
    def approve(self):
        return

    @transition(field=status, source='PENDING', target='REJECTED')
    def reject(self):
        return

    def __str__(self):
        return f"LeaveRequest({self.employee.username}, {self.leave_type}, {self.status})"


class AuditLog(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=100)
    target_id = models.IntegerField(null=True, blank=True)
    target_model = models.CharField(max_length=100)
    from_state = models.CharField(max_length=50, null=True, blank=True)
    to_state = models.CharField(max_length=50, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['actor', 'timestamp']),
            models.Index(fields=['target_model', 'target_id']),
            models.Index(fields=['timestamp']),
        ]

    class Meta:
        ordering = ['-timestamp']

    def save(self, *args, **kwargs):
        if self.pk is not None:
            raise ValueError('AuditLog entries are immutable and cannot be updated')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"AuditLog({self.action} on {self.target_model}:{self.target_id})"
