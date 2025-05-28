from django.urls import path
from .views import DealerGroupListView

urlpatterns = [
    path('', DealerGroupListView.as_view()),
]
