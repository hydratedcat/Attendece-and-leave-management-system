from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from .models import AuditLog, LeaveRequest


class LeaveTests(TestCase):
    def setUp(self):
        self.employee = get_user_model().objects.create_user(
            username="employee", password="pass", role="EMPLOYEE"
        )
        self.manager = get_user_model().objects.create_user(
            username="manager", password="pass", role="MANAGER"
        )
        self.hr_admin = get_user_model().objects.create_user(
            username="hr", password="pass", role="HR_ADMIN"
        )
        self.client = APIClient()

    def test_employee_can_apply_leave(self):
        self.client.force_authenticate(user=self.employee)
        resp = self.client.post(
            "/api/leaves/apply/",
            {
                "leave_type": "SICK",
                "start_date": "2026-04-01",
                "end_date": "2026-04-02",
                "reason": "Feeling unwell",
            },
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(LeaveRequest.objects.count(), 1)
        leave = LeaveRequest.objects.first()
        self.assertEqual(leave.status, "PENDING")
        self.assertEqual(leave.employee, self.employee)

    def test_manager_can_approve_leave(self):
        # Create leave request
        self.client.force_authenticate(user=self.employee)
        resp = self.client.post(
            "/api/leaves/apply/",
            {
                "leave_type": "SICK",
                "start_date": "2026-04-01",
                "end_date": "2026-04-02",
                "reason": "Feeling unwell",
            },
        )
        leave_id = resp.data["id"]

        # Approve as manager
        self.client.force_authenticate(user=self.manager)
        resp = self.client.patch(f"/api/leaves/{leave_id}/approve/", {})
        self.assertEqual(resp.status_code, 200)
        leave = LeaveRequest.objects.get(id=leave_id)
        self.assertEqual(leave.status, "APPROVED")
        self.assertEqual(leave.manager, self.manager)

    def test_manager_can_reject_leave(self):
        # Create leave request
        self.client.force_authenticate(user=self.employee)
        resp = self.client.post(
            "/api/leaves/apply/",
            {
                "leave_type": "SICK",
                "start_date": "2026-04-01",
                "end_date": "2026-04-02",
                "reason": "Feeling unwell",
            },
        )
        leave_id = resp.data["id"]

        # Reject as manager
        self.client.force_authenticate(user=self.manager)
        resp = self.client.patch(f"/api/leaves/{leave_id}/reject/", {})
        self.assertEqual(resp.status_code, 200)
        leave = LeaveRequest.objects.get(id=leave_id)
        self.assertEqual(leave.status, "REJECTED")
        self.assertEqual(leave.manager, self.manager)

    def test_invalid_state_transition_rejected(self):
        # Create and approve leave
        self.client.force_authenticate(user=self.employee)
        resp = self.client.post(
            "/api/leaves/apply/",
            {
                "leave_type": "SICK",
                "start_date": "2026-04-01",
                "end_date": "2026-04-02",
                "reason": "Feeling unwell",
            },
        )
        leave_id = resp.data["id"]

        self.client.force_authenticate(user=self.manager)
        self.client.patch(f"/api/leaves/{leave_id}/approve/", {})

        # Try to approve again - should fail
        resp = self.client.patch(f"/api/leaves/{leave_id}/approve/", {})
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Invalid transition", resp.data["detail"])

    def test_employee_can_view_own_leaves(self):
        self.client.force_authenticate(user=self.employee)
        LeaveRequest.objects.create(
            employee=self.employee,
            leave_type="SICK",
            start_date="2026-04-01",
            end_date="2026-04-02",
            reason="Feeling unwell",
        )
        resp = self.client.get("/api/leaves/my/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)

    def test_manager_can_view_pending_leaves(self):
        self.client.force_authenticate(user=self.employee)
        self.client.post(
            "/api/leaves/apply/",
            {
                "leave_type": "SICK",
                "start_date": "2026-04-01",
                "end_date": "2026-04-02",
                "reason": "Feeling unwell",
            },
        )

        self.client.force_authenticate(user=self.manager)
        resp = self.client.get("/api/leaves/pending/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)

    def test_employee_cannot_approve_leaves(self):
        self.client.force_authenticate(user=self.employee)
        resp = self.client.post(
            "/api/leaves/apply/",
            {
                "leave_type": "SICK",
                "start_date": "2026-04-01",
                "end_date": "2026-04-02",
                "reason": "Feeling unwell",
            },
        )
        leave_id = resp.data["id"]

        # Try to approve own leave - should fail
        resp = self.client.patch(f"/api/leaves/{leave_id}/approve/", {})
        self.assertEqual(resp.status_code, 403)

    def test_leave_summary_report(self):
        # Create multiple leave requests
        LeaveRequest.objects.create(
            employee=self.employee,
            leave_type="SICK",
            start_date="2026-04-01",
            end_date="2026-04-02",
            reason="Feeling unwell",
            status="PENDING",
        )
        LeaveRequest.objects.create(
            employee=self.employee,
            leave_type="CASUAL",
            start_date="2026-05-01",
            end_date="2026-05-05",
            reason="Holiday",
            status="APPROVED",
        )

        self.client.force_authenticate(user=self.manager)
        resp = self.client.get("/api/leaves/reports/summary/")
        self.assertEqual(resp.status_code, 200)
        self.assertGreater(len(resp.data), 0)

    def test_audit_log_creation(self):
        # Create and approve leave
        self.client.force_authenticate(user=self.employee)
        resp = self.client.post(
            "/api/leaves/apply/",
            {
                "leave_type": "SICK",
                "start_date": "2026-04-01",
                "end_date": "2026-04-02",
                "reason": "Feeling unwell",
            },
        )
        leave_id = resp.data["id"]

        self.client.force_authenticate(user=self.manager)
        self.client.patch(f"/api/leaves/{leave_id}/approve/", {})

        # Check audit log (only created on approval, not on creation)
        self.assertEqual(AuditLog.objects.count(), 1)

    def test_hr_admin_can_view_audit_logs(self):
        AuditLog.objects.create(
            actor=self.employee,
            action="CREATED",
            target_id=1,
            target_model="LeaveRequest",
            from_state=None,
            to_state="PENDING",
            metadata={"leave_type": "SICK"},
        )

        self.client.force_authenticate(user=self.hr_admin)
        resp = self.client.get("/api/leaves/audit/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)

    def test_employee_cannot_view_audit_logs(self):
        self.client.force_authenticate(user=self.employee)
        resp = self.client.get("/api/leaves/audit/")
        self.assertEqual(resp.status_code, 403)
