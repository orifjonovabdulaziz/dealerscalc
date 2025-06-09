from rest_framework import serializers
from .models import Income, DebtRepaymentHistory

class IncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Income
        fields = '__all__'
        read_only_fields = ['user', 'created_at']

    def validate(self, data):
        payment_type = data.get('payment_type')
        rate = data.get('rate')

        if payment_type == 'transfer' and rate is None:
            raise serializers.ValidationError({
                'rate': 'Поле обязательно при типе оплаты "перечисление".'
            })

        if payment_type == 'cash' and rate is not None:
            raise serializers.ValidationError({
                'rate': 'Поле "rate" не должно быть заполнено при оплате наличными.'
            })

        return data

class DebtRepaymentHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DebtRepaymentHistory
        fields = ['id', 'income', 'amount', 'delta_debt', 'created_at']