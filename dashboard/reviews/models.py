from django.contrib.auth.models import User
from django.db import models


class Review(models.Model):
    content = models.TextField(default=None)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)


class Metrics(models.Model):
    review = models.OneToOneField(Review, on_delete=models.CASCADE)
    negative_rate = models.DecimalField(max_digits=3, decimal_places=2)
    neutral_rate = models.DecimalField(max_digits=3, decimal_places=2)
    positive_rate = models.DecimalField(max_digits=3, decimal_places=2)


