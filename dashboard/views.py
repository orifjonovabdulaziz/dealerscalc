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
from rest_framework.exceptions import PermissionDenied
from decimal import Decimal
from django.utils.timezone import now, make_aware
from incomes.models import Income
from sales.models import Outcome, OutcomeItem
from clients.models import Client
from dealers.models import DealerGroup

class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get_data_for_period(self, user, start, end):
        if not user:
            raise PermissionDenied("Пользователь не определён.")

        dealer_group = getattr(user, 'dealer_groups', None)
        if dealer_group is None:
            raise PermissionDenied("У пользователя нет поля dealer_groups.")

        dealer_group = dealer_group.first()
        if not dealer_group:
            raise PermissionDenied("Вы не состоите ни в одной группе.")

        date_filter = Q(created_at__range=(start, end))

        total_income = Income.objects.filter(
            user__in=dealer_group.members.all()
        ).filter(date_filter).aggregate(Sum('kredit'))['kredit__sum'] or Decimal(0)

        total_outcome_stock = Outcome.objects.filter(
            dealer_group=dealer_group
        ).filter(date_filter).aggregate(Sum('stock_sum_price'))['stock_sum_price__sum'] or Decimal(0)

        total_profit = Outcome.objects.filter(
            dealer_group=dealer_group
        ).filter(date_filter).aggregate(Sum('profit'))['profit__sum'] or Decimal(0)

        total_quantity_kg = OutcomeItem.objects.filter(
            outcome__dealer_group=dealer_group,
            outcome__created_at__range=(start, end)
        ).aggregate(Sum('quantity'))['quantity__sum'] or Decimal(0)

        total_quantity_tons = total_quantity_kg / Decimal(1000)

        clients = Client.objects.filter(dealer_group=dealer_group)
        total_clients = clients.count()
        paid_clients = clients.filter(total_debt=0).count()
        debt_sum = clients.aggregate(Sum('total_debt'))['total_debt__sum'] or Decimal(0)
        total_dealers_debt = DealerGroup.objects.all()

        client_history = [
            {
                'id': c.id,
                'name': c.name,
                'phone_number': c.phone_number,
                'total_debt': c.total_debt
            } for c in clients
        ]

        return {
            'filter_period': {
                'start': start,
                'end': end
            },
            'header': {
                'total_income': float(total_income),
                'total_outcome': float(total_outcome_stock),
                'total_profit': float(total_profit),
                'total_dealers_debt': total_dealers_debt,
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
        }

    @extend_schema(
        parameters=[
            OpenApiParameter(name='start', description='Начало периода (YYYY-MM-DD)', required=False, type=str),
            OpenApiParameter(name='end', description='Конец периода (YYYY-MM-DD)', required=False, type=str),
        ]
    )
    def get(self, request):
        user = request.user
        today = now()

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

        data = self.get_data_for_period(user, start.date(), end.date())
        return Response(data)

    # def get(self, request):
    #     user = request.user
    #     today = now()

    #     # Получаем первую группу пользователя
    #     dealer_group = user.dealer_groups.first()
    #     if not dealer_group:
    #         return Response({"detail": "Вы не состоите ни в одной группе."}, status=403)

    #     # Период
    #     start_str = request.query_params.get('start')
    #     end_str = request.query_params.get('end')

    #     try:
    #         start = make_aware(datetime.strptime(start_str, "%Y-%m-%d")) if start_str else today.replace(day=1)
    #     except ValueError:
    #         start = today.replace(day=1)

    #     try:
    #         end = make_aware(datetime.strptime(end_str, "%Y-%m-%d")) if end_str else today
    #     except ValueError:
    #         end = today

    #     # Фильтр по дате
    #     date_filter = Q(created_at__range=(start, end))

    #     # Доходы
    #     total_income = Income.objects.filter(
    #         user__in=dealer_group.members.all()
    #     ).filter(date_filter).aggregate(Sum('kredit'))['kredit__sum'] or Decimal(0)

    #     # Расходы
    #     total_outcome_stock = Outcome.objects.filter(
    #         dealer_group=dealer_group
    #     ).filter(date_filter).aggregate(Sum('stock_sum_price'))['stock_sum_price__sum'] or Decimal(0)

    #     total_profit = Outcome.objects.filter(
    #         dealer_group=dealer_group
    #     ).filter(date_filter).aggregate(Sum('profit'))['profit__sum'] or Decimal(0)

    #     # Количество продуктов
    #     total_quantity_kg = OutcomeItem.objects.filter(
    #         outcome__dealer_group=dealer_group,
    #         outcome__created_at__range=(start, end)
    #     ).aggregate(Sum('quantity'))['quantity__sum'] or Decimal(0)

    #     total_quantity_tons = total_quantity_kg / Decimal(1000)

    #     # Клиенты этой группы
    #     clients = Client.objects.filter(dealer_group=dealer_group)
    #     total_clients = clients.count()
    #     paid_clients = clients.filter(total_debt=0).count()
    #     debt_sum = clients.aggregate(Sum('total_debt'))['total_debt__sum'] or Decimal(0)

    #     # История клиентов
    #     client_history = [
    #         {
    #             'id': c.id,
    #             'name': c.name,
    #             'phone_number': c.phone_number,
    #             'total_debt': c.total_debt
    #         } for c in clients
    #     ]

    #     return Response({
    #         'filter_period': {
    #             'start': start.date(),
    #             'end': end.date()
    #         },
    #         'header': {
    #             'total_income': float(total_income),
    #             'total_outcome': float(total_outcome_stock),
    #             'total_profit': float(total_profit),
    #         },
    #         'product_quantity': {
    #             'kg': float(total_quantity_kg),
    #             'tons': float(total_quantity_tons),
    #         },
    #         'clients': {
    #             'total': total_clients,
    #             'paid': paid_clients,
    #             'debt_sum': float(debt_sum),
    #         },
    #         'client_history': client_history
    #     })


# from rest_framework.permissions import IsAuthenticated
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from django.http import FileResponse
# from datetime import datetime, date
# from dashboard.excel_utils import generate_report_excel
# from django.utils.timezone import now


# class ExcelReportAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         today = now().date()
#         start_str = request.query_params.get('start')
#         end_str = request.query_params.get('end')

#         try:
#             start_date = datetime.strptime(start_str, "%Y-%m-%d").date() if start_str else today.replace(day=1)
#         except ValueError:
#             return Response({'error': 'Неверный формат даты "start". Используйте YYYY-MM-DD'}, status=400)

#         try:
#             end_date = datetime.strptime(end_str, "%Y-%m-%d").date() if end_str else today
#         except ValueError:
#             return Response({'error': 'Неверный формат даты "end". Используйте YYYY-MM-DD'}, status=400)

#         file_path = generate_report_excel(start_date, end_date, user=request.user)
#         return FileResponse(open(file_path, 'rb'), as_attachment=True, filename='report.xlsx')

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils.timezone import now, make_aware
from datetime import datetime
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.conf import settings

import io
from openpyxl import Workbook
import requests
from decimal import Decimal

class ExcelReportAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def create_excel_report(self, data):
        wb = Workbook()
        ws = wb.active
        ws.title = "Статистика"

        ws.append(["Период", f"{data['filter_period']['start']} — {data['filter_period']['end']}"])
        ws.append([])

        ws.append(["Доход", data['header']['total_income']])
        ws.append(["Расход", data['header']['total_outcome']])
        ws.append(["Прибыль", data['header']['total_profit']])
        ws.append(["Количество (кг)", data['product_quantity']['kg']])
        ws.append(["Количество (тонн)", data['product_quantity']['tons']])
        ws.append(["Всего клиентов", data['clients']['total']])
        ws.append(["Оплативших клиентов", data['clients']['paid']])
        ws.append(["Общая задолженность", data['clients']['debt_sum']])
        ws.append([])

        ws.append(["ID", "Имя", "Телефон", "Задолженность"])
        for client in data['client_history']:
            ws.append([
                client['id'],
                client['name'],
                client['phone_number'],
                client['total_debt']
            ])

        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return buffer

    def send_to_telegram(self, file_buffer, filename="report.xlsx"):
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendDocument"
        files = {
            'document': (filename, file_buffer, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        }
        data = {
            'chat_id': settings.TELEGRAM_CHAT_ID,
            'caption': "📊 Новый отчёт по статистике",
        }
        response = requests.post(url, data=data, files=files)
        return response.ok

    @extend_schema(
        parameters=[
            OpenApiParameter(name='start', description='Начало периода (YYYY-MM-DD)', required=False, type=str),
            OpenApiParameter(name='end', description='Конец периода (YYYY-MM-DD)', required=False, type=str),
        ]
    )
    def get(self, request):
        from .views import DashboardStatsView  # или импортируй как utils метод

        user = request.user
        today = now()

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

        data = DashboardStatsView().get_data_for_period(user, start.date(), end.date())
        file_buffer = self.create_excel_report(data)
        sent = self.send_to_telegram(file_buffer)

        return Response({"success": sent, "message": "Отчёт отправлен в Telegram." if sent else "Ошибка отправки."})



# bot = telegram.Bot(token=settings.TELEGRAM_BOT_TOKEN)
# chat_id = settings.TELEGRAM_GROUP_CHAT_ID  # например: -1001234567890
