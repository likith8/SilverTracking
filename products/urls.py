from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='product_list'),       # List all products
    path('add/', views.product_create, name='product_add'),  # Add new product
    path('edit/<int:pk>/', views.product_update, name='product_update'),   # <-- important
    path('delete/<int:pk>/', views.product_delete, name='product_delete')
]
