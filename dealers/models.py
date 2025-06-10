from django.db import models
from django.db import models
from users.models import User

class DealerGroup(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name='dealer_groups')
    total_debt = models.DecimalField(max_digits=12, decimal_places=5, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
