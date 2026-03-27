from django.urls import path
from .views import (
    ApplyLeaveView,
    ApproveLeaveView,
    RejectLeaveView,
    MyLeavesView,
    PendingLeavesView,
    AuditLogView,
)

urlpatterns = [
    path('apply/', ApplyLeaveView.as_view(), name='apply_leave'),
    path('<int:pk>/approve/', ApproveLeaveView.as_view(), name='approve_leave'),
    path('<int:pk>/reject/', RejectLeaveView.as_view(), name='reject_leave'),
    path('my/', MyLeavesView.as_view(), name='my_leaves'),
    path('pending/', PendingLeavesView.as_view(), name='pending_leaves'),
    path('audit/logs/', AuditLogView.as_view(), name='audit_logs'),
]
