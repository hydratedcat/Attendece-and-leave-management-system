import random
import string

from locust import HttpUser, between, task


class AttendanceUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Register and login"""
        username = f"user_{''.join(random.choices(string.ascii_lowercase, k=8))}"
        response = self.client.post(
            "/api/auth/register/",
            json={
                "username": username,
                "email": f"{username}@test.com",
                "password": "TestPassword123!",
                "role": "EMPLOYEE",
            },
        )
        if response.status_code == 201:
            # Login
            login_response = self.client.post(
                "/api/auth/login/",
                json={"username": username, "password": "TestPassword123!"},
            )
            if login_response.status_code == 200:
                self.token = login_response.json().get("access")
                self.client.headers.update({"Authorization": f"Bearer {self.token}"})

    @task(3)
    def mark_attendance(self):
        """Mark attendance"""
        self.client.post("/api/attendance/mark/", json={})

    @task(2)
    def view_my_attendance(self):
        """View own attendance"""
        self.client.get("/api/attendance/my/")

    @task(1)
    def apply_leave(self):
        """Apply for leave"""
        self.client.post(
            "/api/leaves/apply/",
            json={
                "leave_type": "CASUAL",
                "start_date": "2026-04-20",
                "end_date": "2026-04-21",
                "reason": "Personal leave",
            },
        )

    @task(1)
    def view_my_leaves(self):
        """View own leaves"""
        self.client.get("/api/leaves/my/")

    @task(1)
    def get_daily_report(self):
        """Get daily attendance report"""
        self.client.get("/api/attendance/reports/daily/")


class ManagerUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        """Login as manager"""
        response = self.client.post(
            "/api/auth/login/",
            json={"username": "manager", "password": "manager123"},
        )
        if response.status_code == 200:
            self.token = response.json().get("access")
            self.client.headers.update({"Authorization": f"Bearer {self.token}"})

    @task(2)
    def view_team_attendance(self):
        """View team attendance"""
        self.client.get("/api/attendance/team/")

    @task(2)
    def view_pending_leaves(self):
        """View pending leave requests"""
        self.client.get("/api/leaves/pending/")

    @task(1)
    def get_daily_report(self):
        """Get daily report"""
        self.client.get("/api/attendance/reports/daily/")

    @task(1)
    def get_monthly_report(self):
        """Get monthly report"""
        self.client.get("/api/attendance/reports/monthly/")
