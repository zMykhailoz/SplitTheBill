from django.contrib.auth.models import User
from django.db import models


class Event(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_completed = models.DateTimeField(null=True, blank=True)  # Дата завершення
    is_completed = models.BooleanField(default=False)  # Статус завершення
    participants = models.ManyToManyField(User, related_name="events")

    def __str__(self):
        return self.name


class Expense(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="expenses")
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="expenses_paid")

    def __str__(self):
        return f"{self.name} - {self.amount} грн"


class Debts(models.Model):
    borrower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrowed_debts', null=True, blank=True)

    lender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lent_debts')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.borrower} -> {self.lender}: {self.amount} грн"


class Friendship(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Очікує підтвердження'),
        ('accepted', 'Прийнято'),
        ('rejected', 'Відхилено'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friends')
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_of')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} -> {self.friend.username} ({self.get_status_display()})"
