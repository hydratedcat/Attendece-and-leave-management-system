from django.urls import path
from .views import (
    MarkAttendanceView,
    MyAttendanceView,
    TeamAttendanceView,
    DailyAttendanceReportView,
    MonthlyAttendanceReportView,
)

urlpatterns = [
    path('mark/', MarkAttendanceView.as_view(), name='attendance_mark'),
    path('my/', MyAttendanceView.as_view(), name='attendance_my'),
    path('team/', TeamAttendanceView.as_view(), name='attendance_team'),
    path('reports/daily/', DailyAttendanceReportView.as_view(), name='attendance_report_daily'),
    path('reports/monthly/', MonthlyAttendanceReportView.as_view(), name='attendance_report_monthly'),
]
