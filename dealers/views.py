from rest_framework import viewsets
from .models import DealerGroup
from .serializers import DealerGroupSerializer
from rest_framework.permissions import IsAuthenticated


class DealerGroupViewSet(viewsets.ModelViewSet):
    serializer_class = DealerGroupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DealerGroup.objects.filter(members=self.request.user)


