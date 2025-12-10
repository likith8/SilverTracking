from django.urls import path
from . import views
app_name = 'reports'
urlpatterns = [
    path('transactions/', views.transactions_report, name='transactions_report'),
]
