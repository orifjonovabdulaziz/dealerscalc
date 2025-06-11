from django.shortcuts import render

# Create your views here.
from django.db.models import Sum, Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.timezone import now
from datetime import timedelta
from clients.models import Client
from incomes.models import Income
from sales.models import Outcome, OutcomeItem
from decimal import Decimal


class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = now()
        start_of_month = today.replace(day=1)
        start_of_year = today.replace(month=1, day=1)
        start_of_quarter = today.replace(month=((today.month - 1) // 3) * 3 + 1, day=1)

        # Доход
        total_income = Income.objects.filter(user=user).aggregate(Sum('kredit'))['kredit__sum'] or Decimal(0)

        # Расход (по себестоимости)
        total_outcome_stock = Outcome.objects.filter(user=user).aggregate(Sum('stock_sum_price'))['stock_sum_price__sum'] or Decimal(0)

        # Прибыль (по Outcome)
        total_profit = Outcome.objects.filter(user=user).aggregate(Sum('profit'))['profit__sum'] or Decimal(0)

        # Кол-во продуктов (в кг и тоннах)
        total_quantity_kg = OutcomeItem.objects.filter(outcome__user=user).aggregate(Sum('quantity'))['quantity__sum'] or Decimal(0)
        total_quantity_tons = total_quantity_kg / Decimal(1000)

        # Статистика клиентов
        clients = Client.objects.all()
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
            'header': {
                'month_period': f"{start_of_month.date()} — {today.date()}",
                'quarter_period': f"{start_of_quarter.date()} — {today.date()}",
                'year_period': f"{start_of_year.date()} — {today.date()}",
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
