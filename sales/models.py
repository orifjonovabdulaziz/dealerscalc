from django.db import models
from users.models import User
from clients.models import Client
from products.models import Product
from dealers.models import DealerGroup


class Outcome(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dealer_group = models.ForeignKey(DealerGroup, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    sold_sum_price = models.DecimalField(max_digits=12, decimal_places=5, default=0)
    stock_sum_price = models.DecimalField(max_digits=12, decimal_places=5, default=0)
    profit = models.DecimalField(max_digits=12, decimal_places=5, default=0)
    debt = models.DecimalField(max_digits=12, decimal_places=5) # Долг
    paid = models.BooleanField(default=False) # Статус заплатил или нет
    received_profit = models.BooleanField(default=False)
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.profit = self.sold_sum_price - self.stock_sum_price
        self.paid = self.debt == 0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Продажа {self.id} клиенту {self.client.name}"


class OutcomeItem(models.Model):
    outcome = models.ForeignKey(Outcome, related_name='product_list', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=5)
    sold_price = models.DecimalField(max_digits=12, decimal_places=5)
    stock_price = models.DecimalField(max_digits=12, decimal_places=5)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_total_sold(self):
        return self.quantity * self.sold_price

    def get_total_stock(self):
        return self.quantity * self.stock_price