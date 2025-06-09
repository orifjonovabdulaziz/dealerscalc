from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IncomeViewSet, IncomeHistoryByOutcomeView

router = DefaultRouter()
router.register(r'', IncomeViewSet, basename='income')

urlpatterns = [
    path('', include(router.urls)),
    path('history/<int:outcome_id>/', IncomeHistoryByOutcomeView.as_view(), name='income-history'),
]
