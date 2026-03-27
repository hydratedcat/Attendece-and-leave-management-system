from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import LeaveRequest, AuditLog
from notifications.tasks import send_leave_status_email


@receiver(post_save, sender=LeaveRequest)
def create_audit_log(sender, instance, created, **kwargs):
    if created:
        return

    metadata = {'employee_id': instance.employee_id, 'manager_id': instance.manager_id}
    AuditLog.objects.create(
        actor=instance.manager,
        action=f'leave_{instance.status.lower()}',
        target_id=instance.id,
        target_model='LeaveRequest',
        to_state=instance.status,
        metadata=metadata,
    )

    # Send WebSocket notification to employee
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'user_{instance.employee.id}',
        {
            'type': 'leave_update',
            'data': {
                'type': 'leave_status_update',
                'leave_id': instance.id,
                'status': instance.status,
                'message': f'Your leave request has been {instance.status.lower()}'
            }
        }
    )

    # Send notification to manager if status changed
    if instance.manager:
        async_to_sync(channel_layer.group_send)(
            f'notifications_{instance.manager.id}',
            {
                'type': 'notification_message',
                'data': {
                    'type': 'leave_processed',
                    'leave_id': instance.id,
                    'employee_name': instance.employee.username,
                    'status': instance.status,
                    'message': f'Leave request from {instance.employee.username} has been {instance.status.lower()}'
                }
            }
        )

    # Send email notification to employee
    send_leave_status_email.delay(instance.employee.email, instance.status.lower(), instance.id)
