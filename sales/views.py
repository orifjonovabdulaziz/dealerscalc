from drf_spectacular.types import OpenApiTypes
from rest_framework import viewsets
from .models import Outcome
from .serializers import OutcomeSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema


class OutcomeViewSet(viewsets.ModelViewSet):
    queryset = Outcome.objects.all()
    serializer_class = OutcomeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Outcome.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save()

    @extend_schema(request=None, responses={200: OpenApiTypes.OBJECT})
    @action(detail=True, methods=['post'], url_path='receive-profit')
    def receive_profit(self, request, pk=None):
        outcome = self.get_object()

        if not outcome.paid:
            return Response({'detail': 'Нельзя получить выручку: продажа не оплачена полностью.'}, status=400)

        if outcome.received_profit:
            return Response({'detail': 'Выручка уже была получена ранее.'}, status=400)

        outcome.received_profit = True
        outcome.save()
        return Response({'detail': 'Выручка получена успешно.'}, status=200)
