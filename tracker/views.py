from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView, ListView

from datetime import datetime, timedelta

from .models import Transaction
from users.forms import UserUpdateForm
from .forms import TransactionForm

# Create your views here.


@login_required
def dashboard(request, period='month'):
    current_balance = Transaction.objects.get_user_total_transactions(
        request.user)

    if period == 'week':
        transactions = Transaction.objects.filter(user=request.user,date_created__gte=datetime.now()-timedelta(days=7))
    elif period == 'month':
        transactions = Transaction.objects.filter(user=request.user,date_created__gte=datetime.now()-timedelta(days=30))
    elif period == 'all':
        transactions = Transaction.objects.filter(user=request.user)
    else:
        transactions = Transaction.objects.filter(user=request.user,date_created__gte=datetime.now()-timedelta(days=365, hours=6))

    if not transactions:
        return render(request, 'tracker/dashboard.html', {'page': 'dashboard','no_transactions': True})

    category_totals = {}

    for category in Transaction._meta.get_field('category').choices:
        if category != 'Income':
            category_totals[category[0]] = transactions.filter(category=category[0]).aggregate(sum=Sum('amount')).get('sum') or 0
    
    income_total = transactions.filter(category='Income').order_by('-date_created')
    expenses_total = transactions.exclude(category='Income').order_by('-date_created')

    context = {'page': 'dashboard',
            'current_balance': current_balance,
            'balance_date': transactions.order_by('-date_created').first(),
            'expenses_total' : expenses_total.aggregate(sum=Sum('amount')).get('sum') or 0,
            'expenses_date': expenses_total.first(),
            'income_total': income_total.aggregate(sum=Sum('amount')).get('sum') or 0,
            'income_date': income_total.first(),
            'food_total': category_totals['Food and Consumables'],
            'investment_total': category_totals['Investments'],
            'hobbies_total': category_totals['Hobbies'],
            'rent_total': category_totals['Rent'],
            'transportation_total': category_totals['Transportation'],
            'utilities_total': category_totals['Utilities'],
            'others_total': category_totals['Others'],
            'latest_expenses': expenses_total[:5] or None,
            'period': period}
    return render(request, 'tracker/dashboard.html', context)


class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'tracker/transactions.html'
    context_object_name = 'transactions'
    paginate_by = 5

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by('-date_created')


class TransactionDetailView(UserPassesTestMixin, DetailView):
    model = Transaction

    def test_func(self):
        transaction = self.get_object()
        if self.request.user == transaction.user:
            return True
        return False


class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    form_class = TransactionForm

    def form_valid(self, form):
        form.instance.user = self.request.user

        if form.instance.amount > 0 and form.instance.category != 'Income':
            form.instance.amount = form.instance.amount*-1

        return super().form_valid(form)


class TransactionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Transaction
    form_class = TransactionForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def test_func(self):
        transaction = self.get_object()
        if self.request.user == transaction.user:
            return True
        return False


class TransactionDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Transaction
    success_url = '/transactions'

    def test_func(self):
        transaction = self.get_object()
        if self.request.user == transaction.user:
            return True
        return False


@login_required
def userBalance(request):
    current_balance = Transaction.objects.get_user_total_transactions(
        request.user)
    user_records = Transaction.objects.filter(
        user=request.user).order_by('-date_created')
    initial_balance = current_balance
    history = []

    if not user_records:
        return render(request, 'tracker/balance.html', {'page': 'balance','no_records': True})

    for row in user_records[:5]:

        history.append((row.date_created, row.amount, initial_balance))
        initial_balance = initial_balance - row.amount

    last_update = history[0][0]

    context = {'page': 'balance',
               'records': history,
               'current_balance': current_balance,
               'last_update': last_update}
    return render(request, 'tracker/balance.html', context)


@login_required
def userBalanceHistory(request):
    current_balance = Transaction.objects.get_user_total_transactions(
        request.user)
    user_records = Transaction.objects.filter(
        user=request.user).order_by('-date_created')
    initial_balance = current_balance
    history = []

    for row in user_records:

        history.append((row.date_created, row.amount, initial_balance))
        initial_balance = initial_balance - row.amount

    paginator = Paginator(history, 10)

    page = request.GET.get('page')
    # Get the current slice (page) of products
    results = paginator.get_page(page)

    context = {'paginator': results}
    return render(request, 'tracker/balance_history.html', context)


@login_required
def settings(request):

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)

        if u_form.is_valid():
            u_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('settings')
    else:
        u_form = UserUpdateForm(instance=request.user)

    context = {
        'page': 'settings',
        'u_form': u_form
    }
    return render(request, 'tracker/settings.html', context)

def about(request):
    context = {}
    return render(request, 'tracker/about.html', context)
