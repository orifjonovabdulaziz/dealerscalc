from django.contrib import admin
from .models import Client
# Register your models here.


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'total_debt', 'debt_status')
    search_fields = ('name', 'phone_number')