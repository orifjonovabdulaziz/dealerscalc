import openpyxl
from datetime import date
from django.utils.timezone import now
from dashboard.views import DashboardStatsView
from tempfile import NamedTemporaryFile

def generate_report_excel():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Отчёт"

    data = DashboardStatsView().get_data_for_period(now().date(), now().date())

    ws.append(['Метрика', 'Значение'])
    ws.append(['Доход', data['header']['total_income']])
    ws.append(['Расход', data['header']['total_outcome']])
    ws.append(['Прибыль', data['header']['total_profit']])
    ws.append(['Клиенты (всего)', data['clients']['total']])
    ws.append(['Клиенты (оплатили)', data['clients']['paid']])
    ws.append(['Долг', data['clients']['debt_sum']])

    tmp = NamedTemporaryFile(delete=False, suffix=".xlsx")
    wb.save(tmp.name)
    return tmp.name
