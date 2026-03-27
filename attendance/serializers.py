from rest_framework import serializers
from .models import Attendance


class AttendanceSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=Attendance.STATUS_CHOICES, required=False)

    class Meta:
        model = Attendance
        fields = '__all__'
        read_only_fields = ('user', 'date')
