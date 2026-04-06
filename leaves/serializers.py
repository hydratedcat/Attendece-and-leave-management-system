from rest_framework import serializers
from .models import LeaveRequest, AuditLog


class LeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = '__all__'
        read_only_fields = ('employee', 'status', 'created_at', 'updated_at')


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = '__all__'
        read_only_fields = (
            'actor',
            'action',
            'target_id',
            'target_model',
            'from_state',
            'to_state',
            'timestamp',
            'metadata',
        )
