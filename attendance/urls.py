from django.urls import path
from .views import (
    AttendanceRootView,
    MarkAttendanceView,
    MyAttendanceView,
    TeamAttendanceView,
    DailyAttendanceReportView,
    MonthlyAttendanceReportView,
)

urlpatterns = [
    path('', AttendanceRootView.as_view(), name='attendance_root'),
    path('mark/', MarkAttendanceView.as_view(), name='attendance_mark'),
    path('my/', MyAttendanceView.as_view(), name='attendance_my'),
    path('team/', TeamAttendanceView.as_view(), name='attendance_team'),
    path('reports/daily/', DailyAttendanceReportView.as_view(), name='attendance_report_daily'),
    path('reports/monthly/', MonthlyAttendanceReportView.as_view(), name='attendance_report_monthly'),
]
