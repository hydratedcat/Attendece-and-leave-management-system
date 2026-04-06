from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from .models import LeaveRequest
from .serializers import LeaveRequestSerializer
from users.permissions import IsEmployee, IsManagerOrHRAdmin, IsHRAdmin


class LeavesRootView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        return Response({
            'endpoints': [
                {'apply': '/api/leaves/apply/'},
                {'my': '/api/leaves/my/'},
                {'pending': '/api/leaves/pending/'},
                {'approve': '/api/leaves/<id>/approve/'},
                {'reject': '/api/leaves/<id>/reject/'},
                {'audit_logs': '/api/leaves/audit/logs/'},
            ]
        })


class ApplyLeaveView(generics.CreateAPIView):
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsEmployee]

    def perform_create(self, serializer):
        serializer.save(employee=self.request.user)


class ApproveLeaveView(generics.UpdateAPIView):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsManagerOrHRAdmin]

    def patch(self, request, *args, **kwargs):
        leave = self.get_object()
        if leave.status != 'PENDING':
            return Response({'detail': 'Invalid transition'}, status=status.HTTP_400_BAD_REQUEST)
        leave.manager = request.user
        leave.approve()
        leave.save()
        serializer = self.get_serializer(leave)
        return Response(serializer.data)


class RejectLeaveView(generics.UpdateAPIView):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsManagerOrHRAdmin]

    def patch(self, request, *args, **kwargs):
        leave = self.get_object()
        if leave.status != 'PENDING':
            return Response({'detail': 'Invalid transition'}, status=status.HTTP_400_BAD_REQUEST)
        leave.manager = request.user
        leave.reject()
        leave.save()
        serializer = self.get_serializer(leave)
        return Response(serializer.data)


class MyLeavesView(generics.ListAPIView):
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsEmployee]

    def get_queryset(self):
        return LeaveRequest.objects.filter(employee=self.request.user)


class PendingLeavesView(generics.ListAPIView):
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsManagerOrHRAdmin]

    def get_queryset(self):
        return LeaveRequest.objects.filter(status='PENDING')


from .serializers import AuditLogSerializer
from .models import AuditLog


class AuditLogView(generics.ListAPIView):
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsHRAdmin]

    def get_queryset(self):
        return AuditLog.objects.all()
