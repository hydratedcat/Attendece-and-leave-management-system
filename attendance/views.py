from datetime import date
from django.db.models import Count, Q
from django.db.models.functions import ExtractMonth
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from django.views.decorators.cache import cache_page
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework import serializers
from .models import Attendance
from .serializers import AttendanceSerializer
from users.permissions import IsEmployee, IsManager


@method_decorator(ratelimit(key='user', rate='10/m', method='POST', block=True), name='dispatch')
class MarkAttendanceView(generics.CreateAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated, IsEmployee]

    def perform_create(self, serializer):
        today = date.today()
        if Attendance.objects.filter(user=self.request.user, date=today).exists():
            raise serializers.ValidationError({'detail': 'Attendance already marked for today.'})
        serializer.save(user=self.request.user, date=today)


class MyAttendanceView(generics.ListAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated, IsEmployee]

    def get_queryset(self):
        return Attendance.objects.filter(user=self.request.user).order_by('-date')


class TeamAttendanceView(generics.ListAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def get_queryset(self):
        return Attendance.objects.select_related('user').all().order_by('-date')


class DailyAttendanceReportView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, IsManager]

    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    def get(self, request, *args, **kwargs):
        data = Attendance.objects.values('date').annotate(
            present=Count('id', filter=Q(status='PRESENT')),
            absent=Count('id', filter=Q(status='ABSENT')),
            half_day=Count('id', filter=Q(status='HALF_DAY')),
        ).order_by('date')
        return Response(data)


class MonthlyAttendanceReportView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, IsManager]

    @method_decorator(cache_page(60 * 60))  # Cache for 1 hour
    def get(self, request, *args, **kwargs):
        data = Attendance.objects.annotate(month=ExtractMonth('date')).values('month', 'user').annotate(
            present=Count('id', filter=Q(status='PRESENT')),
            absent=Count('id', filter=Q(status='ABSENT')),
            half_day=Count('id', filter=Q(status='HALF_DAY')),
        ).order_by('month', 'user')
        return Response(data)
