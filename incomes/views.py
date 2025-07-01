from rest_framework import viewsets
from .models import Income
from .serializers import IncomeSerializer
from rest_framework.permissions import IsAuthenticated
from .services import process_income_and_repay_debts, validate_income_amount
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import DebtRepaymentHistory
from .serializers import DebtRepaymentHistorySerializer
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from datetime import datetime


@extend_schema(
    parameters=[
        OpenApiParameter(name='client_id', type=int, location=OpenApiParameter.QUERY, description='ID клиента для фильтрации доходов'),
        OpenApiParameter(name='start_date', type=OpenApiTypes.DATE, location=OpenApiParameter.QUERY, description='Начальная дата (YYYY-MM-DD)'),
        OpenApiParameter(name='end_date', type=OpenApiTypes.DATE, location=OpenApiParameter.QUERY, description='Конечная дата (YYYY-MM-DD)'),
    ]
)


class IncomeViewSet(viewsets.ModelViewSet):
    queryset = Income.objects.all()
    serializer_class = IncomeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Income.objects.filter(user=self.request.user)

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
        user = self.request.user
        validated_data = serializer.validated_data

        client = validated_data['client']
        kredit = validated_data['kredit']
        payment_type = validated_data['payment_type']
        rate = validated_data.get('rate')

        validate_income_amount(client, kredit, payment_type, rate)
        income = serializer.save(user=user)
        process_income_and_repay_debts(income)



class IncomeHistoryByOutcomeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, outcome_id):
        history = DebtRepaymentHistory.objects.filter(outcome_id=outcome_id).order_by('created_at')
        if not history.exists():
            return Response({"detail": "History not found for this outcome."}, status=status.HTTP_404_NOT_FOUND)

        serializer = DebtRepaymentHistorySerializer(history, many=True)
        return Response(serializer.data)