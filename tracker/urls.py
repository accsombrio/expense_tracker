from django.urls import path
from . import views
from .views import (
    TransactionDetailView, 
    TransactionCreateView, 
    TransactionUpdateView,
    TransactionDeleteView,
    TransactionListView,
)

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard/<str:period>', views.dashboard, name='dashboard-period'),
    path('transaction/<int:pk>', TransactionDetailView.as_view(), name='transaction-detail'),
    path('transaction/<int:pk>/update/', TransactionUpdateView.as_view(), name='transaction-update'),
    path('transaction/<int:pk>/delete/', TransactionDeleteView.as_view(), name='transaction-delete'),
    path('transaction/new/', TransactionCreateView.as_view(), name='transaction-create'),
    path('transactions/', TransactionListView.as_view(), name='transactions'),
    path('balance/', views.userBalance, name='balance'),
    path('balance/history/', views.userBalanceHistory, name='balance-history'),
    path('settings/', views.settings, name='settings'),
]
