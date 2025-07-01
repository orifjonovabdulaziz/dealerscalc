from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClientViewSet, ClientReportView

router = DefaultRouter()
router.register(r'', ClientViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('report/', ClientReportView.as_view(), name='client-report'),

]
