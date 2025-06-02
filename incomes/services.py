from decimal import Decimal
from sales.models import Outcome
from .models import DebtRepaymentHistory
from django.db import models

def process_income_and_repay_debts(income):
    if income.payment_type == 'transfer':
        if income.rate is None:
            raise ValueError("Rate must be provided for transfer payments")
        available_amount = income.kredit * Decimal(income.rate) / Decimal(100)
    else:
        available_amount = income.kredit

    outcomes = Outcome.objects.filter(
        client=income.client,
        paid=False
    ).order_by('created_at')

    for outcome in outcomes:
        remaining_debt = outcome.debt

        if remaining_debt <= 0:
            outcome.paid = True
            outcome.save()
            continue

        if available_amount <= 0:
            break

        if available_amount >= remaining_debt:
            payment = remaining_debt
            outcome.debt -= payment
            outcome.paid = True
        else:
            payment = available_amount
            outcome.debt -= payment

        available_amount -= payment
        outcome.save()

        DebtRepaymentHistory.objects.create(
            income=income,
            outcome=outcome,
            amount=payment,
            delta_debt=outcome.debt
        )

    total_debt = Outcome.objects.filter(
        client=income.client,
        paid=False
    ).aggregate(total=models.Sum('debt'))['total'] or 0

    income.client.total_debt = total_debt
    income.client.debt_status = 'has_debt' if total_debt > 0 else 'no_debt'
    income.client.save()
