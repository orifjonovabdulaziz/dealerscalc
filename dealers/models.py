from django.db import models
from django.db import models
from users.models import User

class DealerGroup(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name='dealer_groups')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
