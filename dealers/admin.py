from django.contrib import admin
from .models import DealerGroup


@admin.register(DealerGroup)
class DealerGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'total_debt', 'created_at')
    search_fields = ('name',)
    filter_horizontal = ('members',)