# dashboard/urls.py

from django.urls import path
from .views import DashboardStatsView, ExcelReportAPIView

urlpatterns = [
    path('', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('excel-report/', ExcelReportAPIView.as_view()),

]
