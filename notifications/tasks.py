from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_leave_status_email(employee_email, status, leave_id):
    send_mail(
        subject=f'Leave Request {status}',
        message=f'Your leave request #{leave_id} has been {status}.',
        from_email='hr@company.com',
        recipient_list=[employee_email],
    )
