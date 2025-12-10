from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
    path('', views.customer_list, name='customer_list'),       # List all customers
    path('add/', views.customer_create, name='customer_add'),  # Add new customer
    path('edit/<int:pk>/', views.customer_edit, name='customer_edit'),
    path('delete/<int:pk>/', views.customer_delete, name='customer_delete'),
]
