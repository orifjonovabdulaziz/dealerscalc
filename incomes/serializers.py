from rest_framework import serializers
from .models import Income

class IncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Income
        fields = '__all__'
        read_only_fields = ['user', 'created_at']  # user и created_at ставятся автоматически

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
