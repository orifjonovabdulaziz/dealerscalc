from django.contrib import admin
from .models import Outcome, OutcomeItem

class OutcomeItemInline(admin.TabularInline):
    model = OutcomeItem
    extra = 0
    readonly_fields = ('get_total_sold', 'get_total_stock')
    fields = ('product', 'quantity', 'sold_price', 'stock_price', 'get_total_sold', 'get_total_stock')

    def get_total_sold(self, obj):
        if obj.quantity is None or obj.sold_price is None:
            return "-"
        return obj.quantity * obj.sold_price

    get_total_sold.short_description = "Итог прод."

    def get_total_stock(self, obj):
        if obj.quantity is None or obj.stock_price is None:
            return "-"
        return obj.quantity * obj.stock_price

    get_total_stock.short_description = "Итог зак."


@admin.register(Outcome)
class OutcomeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'client', 'sold_sum_price', 'stock_sum_price', 'profit', 'paid', 'created_at')
    list_filter = ('paid', 'created_at')
    search_fields = ('client__name', 'user__username')
    inlines = [OutcomeItemInline]
    readonly_fields = ('sold_sum_price', 'stock_sum_price', 'profit', 'paid', 'created_at')
