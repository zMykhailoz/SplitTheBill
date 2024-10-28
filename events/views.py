
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from .models import Event, Expense, Friendship, Debts
from .forms import EventForm, ExpenseForm
from django.contrib.auth import login
from .forms import SignUpForm
from collections import defaultdict


def home(request):
    events = Event.objects.filter(is_completed=False)  # Активні івенти
    archived_events = Event.objects.filter(is_completed=True)  # Завершені івенти
    return render(request, 'events/home.html', {
        'events': events,
        'archived_events': archived_events,  # Додаємо архів
    })


def minimize_transactions(balances):
    # Перетворюємо залишки на два списки: хто має отримати та хто винен
    creditors = [(name, balance) for name, balance in balances.items() if balance > 0]
    debtors = [(name, -balance) for name, balance in balances.items() if balance < 0]

    transactions = []  # Список транзакцій

    # Оптимізуємо розрахунки
    i, j = 0, 0
    while i < len(creditors) and j < len(debtors):
        creditor_name, credit_amount = creditors[i]
        debtor_name, debt_amount = debtors[j]

        # Мінімальна сума для взаємозаліку
        amount = min(credit_amount, debt_amount)
        transactions.append(f"{debtor_name} повинен заплатити {creditor_name} {amount:.2f} грн")

        # Оновлюємо залишки
        creditors[i] = (creditor_name, credit_amount - amount)
        debtors[j] = (debtor_name, debt_amount - amount)

        # Якщо борг або кредит погашений, переходимо до наступного учасника
        if creditors[i][1] == 0:
            i += 1
        if debtors[j][1] == 0:
            j += 1

    return transactions


def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    expenses = event.expenses.all()

    # Загальна сума витрат і середня сума на людину
    total_expense = sum(exp.amount for exp in expenses)
    participants = event.participants.all()
    per_person = total_expense / participants.count()

    # Підрахунок балансу кожного учасника
    balances = defaultdict(float)
    for participant in participants:
        paid = sum(exp.amount for exp in expenses.filter(paid_by=participant))
        balances[participant.username] = round(paid - per_person, 2)

    # Оптимізуємо транзакції
    transactions = minimize_transactions(balances)

    return render(request, 'events/event_detail.html', {
        'event': event,
        'expenses': expenses,
        'total_expense': total_expense,
        'per_person': per_person,
        'transactions': transactions,
    })


def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save()
            return redirect('event_detail', event_id=event.id)
    else:
        form = EventForm()
    return render(request, 'events/create_event.html', {'form': form})


def add_expense(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.event = event
            expense.save()
            return redirect('event_detail', event_id=event.id)
    else:
        form = ExpenseForm()
    return render(request, 'events/add_expense.html', {'form': form, 'event': event})


def add_friend(request, friend_id):
    friend = get_object_or_404(User, id=friend_id)
    Friendship.objects.get_or_create(user=request.user, friend=friend)
    return redirect('profile')


def calculate_debts(event):
    total_expenses = sum(exp.amount for exp in event.expenses.all())
    per_person = total_expenses / event.participants.count()
    debts = {}
    for participant in event.participants.all():
        paid = sum(exp.amount for exp in participant.expenses_paid.filter(event=event))
        debts[participant.username] = per_person - paid
    return debts


def complete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        event.is_completed = True
        event.date_completed = timezone.now()  # Зберігаємо дату завершення
        event.save()
        return redirect('event_detail', event_id=event.id)
    return render(request, 'events/complete_event.html', {'event': event})


def add_debt(request, borrower_id, amount):
    borrower = get_object_or_404(User, id=borrower_id)
    Debts.objects.create(
        borrower=borrower,
        lender=request.user,
        amount=amount,
        description="Борг за участь у події"
    )
    return redirect('profile')


def profile(request):
    borrowed_debts = request.user.borrowed_debts.all()
    lent_debts = request.user.lent_debts.all()

    # Отримані запити, що очікують на підтвердження
    friend_requests = Friendship.objects.filter(friend=request.user, status='pending')

    # Список друзів
    friends = Friendship.objects.filter(
        (models.Q(user=request.user) | models.Q(friend=request.user)),
        status='accepted'
    ).values_list('user', 'friend')

    # Унікальний список друзів
    friend_list = User.objects.filter(id__in={id for pair in friends for id in pair})

    return render(request, 'users/profile.html', {
        'borrowed_debts': borrowed_debts,
        'lent_debts': lent_debts,
        'friends': friend_list,
        'friend_requests': friend_requests,
    })


def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Автоматичний вхід після реєстрації
            return redirect('home')  # Перенаправлення на головну сторінку
    else:
        form = SignUpForm()
    return render(request, 'registration/register.html', {'form': form})


def send_friend_request(request, friend_id):
    friend = get_object_or_404(User, id=friend_id)
    if not Friendship.objects.filter(user=request.user, friend=friend).exists():
        Friendship.objects.create(user=request.user, friend=friend, status='pending')
    return redirect('profile')


def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(Friendship, id=request_id, friend=request.user)
    friend_request.status = 'accepted'
    friend_request.save()
    return redirect('profile')


def reject_friend_request(request, request_id):
    friend_request = get_object_or_404(Friendship, id=request_id, friend=request.user)
    friend_request.status = 'rejected'
    friend_request.save()
    return redirect('profile')


def remove_friend(request, friend_id):
    friend = get_object_or_404(User, id=friend_id)

    # Знайти та видалити дружбу з обох сторін (user -> friend та friend -> user)
    friendship = Friendship.objects.filter(
        models.Q(user=request.user, friend=friend) |
        models.Q(user=friend, friend=request.user),
        status='accepted'
    ).first()

    if friendship:
        friendship.delete()

    return redirect('profile')
