from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Item(models.Model):
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=50, default='new')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.owner})"
