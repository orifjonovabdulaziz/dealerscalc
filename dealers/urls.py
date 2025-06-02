from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import DealerGroupViewSet

router = DefaultRouter()
router.register(r'', DealerGroupViewSet, basename='dealergroup')

urlpatterns = [
    path('', include(router.urls)),
]
