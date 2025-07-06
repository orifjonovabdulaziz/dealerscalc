from decimal import Decimal

from rest_framework import serializers
from .models import Outcome, OutcomeItem
from products.models import Product


class OutcomeItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OutcomeItem
        fields = ['product', 'quantity', 'sold_price', 'stock_price', 'created_at', 'updated_at']


class OutcomeSerializer(serializers.ModelSerializer):
    product_list = OutcomeItemSerializer(many=True)
    sold_sum_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    stock_sum_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    profit = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    paid = serializers.BooleanField(read_only=True)

    class Meta:
        model = Outcome
        fields = [
            'id', 'user', 'client', 'created_at', 'product_list',
            'sold_sum_price', 'stock_sum_price', 'debt',
            'profit', 'paid', 'received_profit', 'comment', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'sold_sum_price', 'stock_sum_price', 'debt', 'received_profit', 'profit', 'paid', 'created_at', 'updated_at']

    def create(self, validated_data):
        items_data = validated_data.pop('product_list')
        user = self.context['request'].user
        dealer_group = user.dealer_groups.first()
        client = validated_data.pop('client')

        validated_data.pop('user', None)
        validated_data.pop('dealer_group', None)

        total_sold = Decimal('0')
        total_stock = Decimal('0')

        for item in items_data:
            total_sold += item['quantity'] * item['sold_price']
            total_stock += item['quantity'] * item['stock_price']

        debt = validated_data.get('debt') or total_sold

        outcome = Outcome.objects.create(
            user=user,
            dealer_group=dealer_group,
            client=client,
            sold_sum_price=total_sold,
            stock_sum_price=total_stock,
            profit=total_sold - total_stock,
            debt=debt,
            paid=debt == 0,
            **validated_data
        )

        for item in items_data:
            OutcomeItem.objects.create(outcome=outcome, **item)

        client.total_debt += debt
        client.save()

        if dealer_group:
            dealer_group.total_debt += total_stock
            dealer_group.save()

        return outcome



