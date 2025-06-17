from django.db import models
from users.models import User
from clients.models import Client

class Income(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('cash', 'Наличные'),
        ('transfer', 'Перечисление'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    kredit = models.DecimalField(max_digits=12, decimal_places=2)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    rate = models.DecimalField(max_digits=5, decimal_places=2, default=97)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.client.name} — {self.kredit} ({self.payment_type})"


class DebtRepaymentHistory(models.Model):
    income = models.ForeignKey(Income, on_delete=models.CASCADE)
    outcome = models.ForeignKey('sales.Outcome', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=12, decimal_places=5)
    delta_debt = models.DecimalField(max_digits=12, decimal_places=5)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.outcome.id} — {self.amount} (осталось: {self.delta_debt})"


class DebtRepaymentHistoryDealers(models.Model):
    income = models.ForeignKey(Income, on_delete=models.CASCADE)
    dealer = models.ForeignKey(User, on_delete=models.CASCADE)
    dealer_group = models.ForeignKey('dealers.DealerGroup', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=12, decimal_places=5)
    delta_debt = models.DecimalField(max_digits=12, decimal_places=5)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.dealer.name} - {self.amount} (осталось: {self.delta_debt})"
