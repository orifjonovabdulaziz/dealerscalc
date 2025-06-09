from rest_framework import viewsets
from .models import Income
from .serializers import IncomeSerializer
from rest_framework.permissions import IsAuthenticated
from .services import process_income_and_repay_debts, validate_income_amount
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import DebtRepaymentHistory
from .serializers import DebtRepaymentHistorySerializer
from rest_framework import status

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


class IncomeHistoryByOutcomeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, outcome_id):
        history = DebtRepaymentHistory.objects.filter(outcome_id=outcome_id).order_by('created_at')
        if not history.exists():
            return Response({"detail": "History not found for this outcome."}, status=status.HTTP_404_NOT_FOUND)

        serializer = DebtRepaymentHistorySerializer(history, many=True)
        return Response(serializer.data)