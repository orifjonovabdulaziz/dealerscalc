from rest_framework import serializers
from .models import DealerGroup

class DealerGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = DealerGroup
        fields = ['id', 'name', 'members', 'created_at', 'total_debt', 'created_at', 'updated_at']
