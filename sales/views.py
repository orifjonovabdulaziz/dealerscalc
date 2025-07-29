from drf_spectacular.types import OpenApiTypes
from rest_framework import viewsets
from .models import Outcome
from .serializers import OutcomeSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from datetime import datetime


@extend_schema(
    parameters=[
        OpenApiParameter(name='client_id', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, description='ID клиента'),
        OpenApiParameter(name='start_date', type=OpenApiTypes.DATE, location=OpenApiParameter.QUERY, description='Начальная дата (YYYY-MM-DD)'),
        OpenApiParameter(name='end_date', type=OpenApiTypes.DATE, location=OpenApiParameter.QUERY, description='Конечная дата (YYYY-MM-DD)'),
    ]
)

class OutcomeViewSet(viewsets.ModelViewSet):
    queryset = Outcome.objects.all()
    serializer_class = OutcomeSerializer
    permission_classes = [IsAuthenticated]

    # def get_queryset(self):
    #     return Outcome.objects.filter(user=self.request.user)
    def get_queryset(self):
        user = self.request.user
        dealer_groups = user.dealer_groups.all()
        queryset = Outcome.objects.filter(dealer_group__in=dealer_groups)

        client_id = self.request.query_params.get('client_id')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if client_id:
            queryset = queryset.filter(client_id=client_id)

        if start_date:
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d")
                queryset = queryset.filter(created_at__gte=start)
            except ValueError:
                pass

        if end_date:
            try:
                end = datetime.strptime(end_date, "%Y-%m-%d")
                queryset = queryset.filter(created_at__lte=end)
            except ValueError:
                pass

        return queryset


    def perform_create(self, serializer):
        dealer_group = self.request.user.dealer_groups.first()
        serializer.save(user=self.request.user, dealer_group=dealer_group)

    def perform_update(self, serializer):
        return super().perform_update(serializer)


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
