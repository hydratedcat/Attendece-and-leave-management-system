from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status


class UserTests(TestCase):
    def setUp(self):
        self.employee = get_user_model().objects.create_user(
            username='employee',
            password='pass',
            email='employee@test.com',
            role='EMPLOYEE'
        )
        self.manager = get_user_model().objects.create_user(
            username='manager',
            password='pass',
            email='manager@test.com',
            role='MANAGER'
        )
        self.hr_admin = get_user_model().objects.create_user(
            username='hr',
            password='pass',
            email='hr@test.com',
            role='HR_ADMIN'
        )
        self.client = APIClient()

    def test_user_creation(self):
        user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass',
            email='test@example.com',
            role='EMPLOYEE'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.role, 'EMPLOYEE')
        self.assertTrue(user.check_password('testpass'))

    def test_jwt_authentication(self):
        # Test login endpoint
        resp = self.client.post('/api/auth/login/', {
            'username': 'employee',
            'password': 'pass'
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('access', resp.data)
        self.assertIn('refresh', resp.data)

    def test_invalid_login(self):
        resp = self.client.post('/api/auth/login/', {
            'username': 'employee',
            'password': 'wrongpass'
        })
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh(self):
        # Get initial tokens
        resp = self.client.post('/api/auth/login/', {
            'username': 'employee',
            'password': 'pass'
        })
        refresh_token = resp.data['refresh']

        # Refresh token
        resp = self.client.post('/api/auth/refresh/', {
            'refresh': refresh_token
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('access', resp.data)

    def test_user_profile_access(self):
        self.client.force_authenticate(user=self.employee)
        resp = self.client.get('/api/users/profile/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['username'], 'employee')
        self.assertEqual(resp.data['role'], 'EMPLOYEE')

    def test_user_list_access_hr_admin(self):
        self.client.force_authenticate(user=self.hr_admin)
        resp = self.client.get('/api/users/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(resp.data), 3)  # At least the 3 users we created

    def test_user_list_access_denied_employee(self):
        self.client.force_authenticate(user=self.employee)
        resp = self.client.get('/api/users/')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_creation_by_hr_admin(self):
        self.client.force_authenticate(user=self.hr_admin)
        resp = self.client.post('/api/users/', {
            'username': 'newuser',
            'password': 'newpass',
            'email': 'new@test.com',
            'role': 'EMPLOYEE'
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(get_user_model().objects.filter(username='newuser').exists())

    def test_user_creation_denied_employee(self):
        self.client.force_authenticate(user=self.employee)
        resp = self.client.post('/api/users/', {
            'username': 'newuser2',
            'password': 'newpass',
            'email': 'new2@test.com',
            'role': 'EMPLOYEE'
        })
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_role_based_permissions(self):
        # Test that permissions work correctly
        from .permissions import IsEmployee, IsManagerOrHRAdmin, IsHRAdmin

        # Employee permission
        permission = IsEmployee()
        self.assertTrue(permission.has_permission(None, None, self.employee))
        self.assertFalse(permission.has_permission(None, None, self.manager))

        # Manager/HR permission
        permission = IsManagerOrHRAdmin()
        self.assertTrue(permission.has_permission(None, None, self.manager))
        self.assertTrue(permission.has_permission(None, None, self.hr_admin))
        self.assertFalse(permission.has_permission(None, None, self.employee))

        # HR Admin permission
        permission = IsHRAdmin()
        self.assertTrue(permission.has_permission(None, None, self.hr_admin))
        self.assertFalse(permission.has_permission(None, None, self.manager))

    def test_user_serializer_validation(self):
        from .serializers import UserSerializer
        serializer = UserSerializer(data={
            'username': 'test',
            'password': 'pass',
            'email': 'test@example.com',
            'role': 'INVALID_ROLE'
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('role', serializer.errors)

    def test_custom_user_model_methods(self):
        # Test the custom methods on CustomUser
        self.assertEqual(self.employee.get_full_name(), 'employee')  # Since no first/last name
        self.assertEqual(str(self.employee), 'employee')
