from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models import Sum

from datetime import timedelta

# Create your models here.
class TransactionManager(models.Manager):
    def get_user_total_transactions(self, user): 

        return self.filter(user=user).aggregate(sum=Sum('amount')).get('sum')


class Transaction(models.Model):

    CATEGORY = (
            ('Income', 'Income'),
            ('Rent', 'Rent'),
            ('Utilities', 'Utilities'),
            ('Food and Consumables', 'Food and Consumables'),
            ('Transportation', 'Transportation'),
            ('Hobbies', 'Hobbies'),
            ('Investments', 'Investments'),
            ('Others', 'Others'),
            )

    title = models.CharField(max_length=100)
    amount = models.FloatField()
    category = models.CharField(max_length=200, choices=CATEGORY)
    date_created = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    objects = TransactionManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('transactions')


class BalanceRecord(models.Model):
    amount = models.FloatField()
    date_created = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
