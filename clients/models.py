from django.db import models
from dealers.models import DealerGroup

# Create your models here.


class Client(models.Model):
    DEBT_STATUS_CHOICES = [
        ('no_debt', 'Нет долга'),
        ('has_debt', 'Есть долг'),
    ]

    name = models.CharField(max_length=255)
    dealer_group = models.ForeignKey(DealerGroup, on_delete=models.CASCADE, related_name='clients')

    total_debt = models.DecimalField(max_digits=12, decimal_places=5, default=0)
    comment = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    debt_status = models.CharField(max_length=20, choices=DEBT_STATUS_CHOICES, default='no_debt')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.total_debt == 0:
            self.debt_status = 'no_debt'
        else:
            self.debt_status = 'has_debt'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name