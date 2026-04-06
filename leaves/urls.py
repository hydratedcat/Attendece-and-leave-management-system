from django.urls import path

from .views import (
    ApplyLeaveView,
    ApproveLeaveView,
    AuditLogView,
    LeavesRootView,
    LeaveSummaryReportView,
    MyLeavesView,
    PendingLeavesView,
    RejectLeaveView,
)

urlpatterns = [
    path("", LeavesRootView.as_view(), name="leaves_root"),
    path("apply/", ApplyLeaveView.as_view(), name="apply_leave"),
    path("<int:pk>/approve/", ApproveLeaveView.as_view(), name="approve_leave"),
    path("<int:pk>/reject/", RejectLeaveView.as_view(), name="reject_leave"),
    path("my/", MyLeavesView.as_view(), name="my_leaves"),
    path("pending/", PendingLeavesView.as_view(), name="pending_leaves"),
    path("audit/", AuditLogView.as_view(), name="audit_logs"),
    path("reports/summary/", LeaveSummaryReportView.as_view(), name="leave_summary"),
]
