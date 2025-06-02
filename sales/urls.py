from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OutcomeViewSet

router = DefaultRouter()
router.register(r'', OutcomeViewSet, basename='outcome')

urlpatterns = [
    path('', include(router.urls)),
]
