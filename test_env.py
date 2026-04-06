import os
import sys

import django

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

django.setup()

print("Django setup successful!")

# Try importing our apps
try:
    from attendance.models import Attendance
    from leaves.models import LeaveRequest
    from users.models import CustomUser

    print("All models imported successfully!", Attendance, LeaveRequest, CustomUser)
except ImportError as e:
    print(f"Import error: {e}")

print("Environment test completed.")
