from django.shortcuts import render
from rest_framework import generics
from .models import DealerGroup
from .serializers import DealerGroupSerializer
from rest_framework.permissions import IsAuthenticated


class DealerGroupListView(generics.ListAPIView):
    serializer_class = DealerGroupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DealerGroup.objects.filter(members=self.request.user)