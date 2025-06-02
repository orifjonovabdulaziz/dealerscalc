from django.contrib import admin
from .models import Income, DebtRepaymentHistory

@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'client', 'kredit', 'payment_type', 'rate', 'created_at')
    list_filter = ('payment_type', 'created_at')
    search_fields = ('user__username', 'client__name')
    readonly_fields = ('created_at',)

@admin.register(DebtRepaymentHistory)
class DebtRepaymentHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'income', 'outcome', 'amount', 'delta_debt', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('income__id', 'outcome__id')
    readonly_fields = ('created_at',)