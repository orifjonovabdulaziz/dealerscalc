from django.shortcuts import render
from django.db.models import Sum, Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.timezone import now, make_aware
from datetime import datetime, timedelta
from clients.models import Client
from incomes.models import Income
from sales.models import Outcome, OutcomeItem
from decimal import Decimal
from drf_spectacular.utils import extend_schema, OpenApiParameter


class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(name='start', description='Начало периода (YYYY-MM-DD)', required=False, type=str),
            OpenApiParameter(name='end', description='Конец периода (YYYY-MM-DD)', required=False, type=str),
        ]
    )
    def get(self, request):
        user = request.user
        today = now()

        # Получаем первую группу пользователя
        dealer_group = user.dealer_groups.first()
        if not dealer_group:
            return Response({"detail": "Вы не состоите ни в одной группе."}, status=403)

        # Период
        start_str = request.query_params.get('start')
        end_str = request.query_params.get('end')

        try:
            start = make_aware(datetime.strptime(start_str, "%Y-%m-%d")) if start_str else today.replace(day=1)
        except ValueError:
            start = today.replace(day=1)

        try:
            end = make_aware(datetime.strptime(end_str, "%Y-%m-%d")) if end_str else today
        except ValueError:
            end = today

        # Фильтр по дате
        date_filter = Q(created_at__range=(start, end))

        # Доходы
        total_income = Income.objects.filter(
            user__in=dealer_group.members.all()
        ).filter(date_filter).aggregate(Sum('kredit'))['kredit__sum'] or Decimal(0)

        # Расходы
        total_outcome_stock = Outcome.objects.filter(
            dealer_group=dealer_group
        ).filter(date_filter).aggregate(Sum('stock_sum_price'))['stock_sum_price__sum'] or Decimal(0)

        total_profit = Outcome.objects.filter(
            dealer_group=dealer_group
        ).filter(date_filter).aggregate(Sum('profit'))['profit__sum'] or Decimal(0)

        # Количество продуктов
        total_quantity_kg = OutcomeItem.objects.filter(
            outcome__dealer_group=dealer_group,
            outcome__created_at__range=(start, end)
        ).aggregate(Sum('quantity'))['quantity__sum'] or Decimal(0)

        total_quantity_tons = total_quantity_kg / Decimal(1000)

        # Клиенты этой группы
        clients = Client.objects.filter(dealer_group=dealer_group)
        total_clients = clients.count()
        paid_clients = clients.filter(total_debt=0).count()
        debt_sum = clients.aggregate(Sum('total_debt'))['total_debt__sum'] or Decimal(0)

        # История клиентов
        client_history = [
            {
                'id': c.id,
                'name': c.name,
                'phone_number': c.phone_number,
                'total_debt': c.total_debt
            } for c in clients
        ]

        return Response({
            'filter_period': {
                'start': start.date(),
                'end': end.date()
            },
            'header': {
                'total_income': float(total_income),
                'total_outcome': float(total_outcome_stock),
                'total_profit': float(total_profit),
            },
            'product_quantity': {
                'kg': float(total_quantity_kg),
                'tons': float(total_quantity_tons),
            },
            'clients': {
                'total': total_clients,
                'paid': paid_clients,
                'debt_sum': float(debt_sum),
            },
            'client_history': client_history
        })


from rest_framework.parsers import FormParser
from rest_framework.decorators import api_view
from django.http import FileResponse
from datetime import datetime
from dashboard.excel_utils import generate_report_excel

class ExcelReportAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start = request.query_params.get('start')
        end = request.query_params.get('end')

        try:
            start_date = datetime.strptime(start, "%Y-%m-%d").date()
            end_date = datetime.strptime(end, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            return Response({'error': 'Неверный формат даты. Используйте YYYY-MM-DD'}, status=400)

        file_path = generate_report_excel(start_date, end_date)
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename='report.xlsx')
