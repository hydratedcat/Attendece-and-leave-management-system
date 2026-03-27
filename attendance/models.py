from django.db import models
from django.conf import settings


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('HALF_DAY', 'Half Day'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PRESENT')

    class Meta:
        unique_together = ('user', 'date')
        indexes = [models.Index(fields=['user', 'date'])]

    def __str__(self):
        return f"{self.user} - {self.date} - {self.status}"
