from django.db import models
from dealers.models import DealerGroup 


class Product(models.Model):
    name = models.CharField(max_length=255)
    dealer_group = models.ForeignKey(DealerGroup, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    