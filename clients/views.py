from rest_framework import viewsets, filters

from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Client
from .serializers import ClientSerializer


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'phone_number', 'comment', 'created_at', 'updated_at'] 
    filterset_fields = ['debt_status'] 


from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.utils.timezone import now
from datetime import datetime
from .models import Client
from incomes.models import Income
from sales.models import Outcome
from django.db.models import Sum
from decimal import Decimal


@extend_schema(
    parameters=[
        OpenApiParameter(name='start_date', type=OpenApiTypes.DATE, location=OpenApiParameter.QUERY, description='Начальная дата (YYYY-MM-DD)'),
        OpenApiParameter(name='end_date', type=OpenApiTypes.DATE, location=OpenApiParameter.QUERY, description='Конечная дата (YYYY-MM-DD)'),
    ]
)
class ClientReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Обработка периода фильтрации
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        today = now().date()
        default_start = today.replace(day=1)
        default_end = today

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else default_start
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else default_end
        except ValueError:
            return Response({'error': 'Некорректный формат даты. Используйте YYYY-MM-DD.'}, status=400)

        clients = Client.objects.all()

        report = []
        for client in clients:
            incomes_sum = Income.objects.filter(
                client=client,
                user=user,
                created_at__date__range=(start_date, end_date)
            ).aggregate(Sum('kredit'))['kredit__sum'] or Decimal(0)

            sales = Outcome.objects.filter(
                client=client,
                user=user,
                created_at__date__range=(start_date, end_date)
            )

            total_sales = sales.aggregate(Sum('sold_sum_price'))['sold_sum_price__sum'] or Decimal(0)
            total_profit = sales.aggregate(Sum('profit'))['profit__sum'] or Decimal(0)

            report.append({
                'id': client.id,
                'name': client.name,
                'phone_number': client.phone_number,
                'total_debt': float(client.total_debt),
                'debt_status': client.debt_status,
                'income_sum': float(incomes_sum),
                'sales_sum': float(total_sales),
                'profit_sum': float(total_profit),
            })

        return Response({
            'start_date': str(start_date),
            'end_date': str(end_date),
            'clients': report,
        })
