from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
     path('silver-given/add/', views.silver_given_create, name='silver_given_add'),
    path('silver-given/list/', views.silver_given_list, name='silver_given_list'),
    path('silver-given/edit/<int:pk>/', views.silver_given_edit, name='silver_given_edit'),
    path('silver-given/delete/<int:pk>/', views.silver_given_delete, name='silver_given_delete'),

    # Product Return
    path('product-return/add/', views.product_return_create, name='product_return_add'),
    path('product-return/list/', views.product_return_list, name='product_return_list'),
    path('product-return/edit/<int:pk>/', views.product_return_edit, name='product_return_edit'),
    path('product-return/delete/<int:pk>/', views.product_return_delete, name='product_return_delete'),

     path('report/', views.transactions_report, name='transactions_report'),
]
