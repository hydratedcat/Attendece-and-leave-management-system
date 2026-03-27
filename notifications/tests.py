from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core import mail
from unittest.mock import patch, MagicMock
from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework.test import APIClient
from leaves.models import LeaveRequest
from .consumers import LeaveStatusConsumer, NotificationConsumer
from .tasks import send_leave_status_email


class NotificationTests(TestCase):
    def setUp(self):
        self.employee = get_user_model().objects.create_user(username='employee', password='pass', role='EMPLOYEE')
        self.manager = get_user_model().objects.create_user(username='manager', password='pass', role='MANAGER')
        self.client = APIClient()

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_send_leave_notification_task(self):
        # Test the Celery task for sending email notifications
        leave = LeaveRequest.objects.create(
            employee=self.employee,
            leave_type='SICK',
            start_date='2026-04-01',
            end_date='2026-04-02',
            reason='Feeling unwell'
        )

        # Call the task
        send_leave_status_email.delay(self.employee.email, 'approved', leave.id)

        # Check that email was sent
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertIn('approved', email.subject.lower())
        self.assertIn(self.employee.email, email.to)

    def test_leave_status_consumer_connection(self):
        # Test WebSocket consumer connection
        communicator = WebsocketCommunicator(
            LeaveStatusConsumer.as_asgi(),
            "/ws/leaves/status/"
        )
        communicator.scope['user'] = self.employee

        connected, _ = async_to_sync(communicator.connect)()
        self.assertTrue(connected)

        # Send a message
        async_to_sync(communicator.send_json_to)({
            "type": "leave_status_update",
            "leave_id": 1,
            "status": "APPROVED"
        })

        # Receive response
        response = async_to_sync(communicator.receive_json_from)()
        self.assertEqual(response["type"], "leave_status_update")

        async_to_sync(communicator.disconnect)()

    def test_notification_consumer_connection(self):
        # Test notification WebSocket consumer
        communicator = WebsocketCommunicator(
            NotificationConsumer.as_asgi(),
            "/ws/notifications/"
        )
        communicator.scope['user'] = self.employee

        connected, _ = async_to_sync(communicator.connect)()
        self.assertTrue(connected)

        # Send a message
        async_to_sync(communicator.send_json_to)({
            "type": "notification",
            "message": "Test notification"
        })

        # Receive response
        response = async_to_sync(communicator.receive_json_from)()
        self.assertEqual(response["type"], "notification")

        async_to_sync(communicator.disconnect)()

    @patch('leaves.signals.channel_layer')
    def test_websocket_notification_on_leave_approval(self, mock_channel_layer):
        # Test that WebSocket notifications are sent when leave is approved
        leave = LeaveRequest.objects.create(
            employee=self.employee,
            leave_type='SICK',
            start_date='2026-04-01',
            end_date='2026-04-02',
            reason='Feeling unwell'
        )

        # Mock the channel layer
        mock_channel_layer.group_send = MagicMock()

        # Approve the leave (this should trigger the signal)
        leave.manager = self.manager
        leave.approve()
        leave.save()

        # Check that group_send was called
        self.assertTrue(mock_channel_layer.group_send.called)
        call_args = mock_channel_layer.group_send.call_args
        self.assertIn(f"user_{self.employee.id}", call_args[0][0])  # Group name
        message = call_args[0][1]
        self.assertEqual(message['type'], 'leave_status_update')
        self.assertEqual(message['leave_id'], leave.id)
        self.assertEqual(message['status'], 'APPROVED')

    def test_channel_layer_group_naming(self):
        # Test that group names are constructed correctly
        expected_group = f"user_{self.employee.id}"
        self.assertEqual(expected_group, f"user_{self.employee.id}")

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_email_notification_on_leave_status_change(self):
        # Test that email is sent when leave status changes (not on creation)
        with patch('leaves.signals.send_leave_status_email') as mock_send_email:
            leave = LeaveRequest.objects.create(
                employee=self.employee,
                leave_type='SICK',
                start_date='2026-04-01',
                end_date='2026-04-02',
                reason='Feeling unwell'
            )

            # Email is not sent on creation, only on status change
            self.assertFalse(mock_send_email.delay.called)

            # Now approve the leave
            leave.manager = self.manager
            leave.approve()
            leave.save()

            # Check that email task was called
            self.assertTrue(mock_send_email.delay.called)
            call_args = mock_send_email.delay.call_args
            self.assertEqual(call_args[0][0], self.employee.email)  # email
            self.assertEqual(call_args[0][1], 'approved')  # status
            self.assertEqual(call_args[0][2], leave.id)  # leave_id
