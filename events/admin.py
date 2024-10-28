from django.contrib import admin
from .models import Event, Expense, Debts, Friendship

admin.site.register(Event)
admin.site.register(Expense)
admin.site.register(Debts)
admin.site.register(Friendship)
