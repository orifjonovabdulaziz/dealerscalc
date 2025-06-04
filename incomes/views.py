from rest_framework import viewsets
from .models import Income
from .serializers import IncomeSerializer
from rest_framework.permissions import IsAuthenticated
from .services import process_income_and_repay_debts, validate_income_amount

class IncomeViewSet(viewsets.ModelViewSet):
    queryset = Income.objects.all()
    serializer_class = IncomeSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        validated_data = serializer.validated_data

        client = validated_data['client']
        kredit = validated_data['kredit']
        payment_type = validated_data['payment_type']
        rate = validated_data.get('rate')

        validate_income_amount(client, kredit, payment_type, rate)

        income = serializer.save(user=user)
        process_income_and_repay_debts(income)
