from django.urls import path
from . import views

urlpatterns = [
    path('', views.catalog_view, name='catalog'),
    path('product/<int:pk>/', views.product_detail_view, name='product_detail'),
    path('owner/products/', views.owner_product_list, name='owner_product_list'),
    path('owner/products/create/', views.owner_product_create, name='owner_product_create'),
    path('owner/products/<int:pk>/edit/', views.owner_product_edit, name='owner_product_edit'),
    path('owner/products/<int:pk>/update-price/', views.owner_update_price, name='owner_update_price'),
    path('owner/products/<int:pk>/toggle-stock/', views.owner_toggle_stock, name='owner_toggle_stock'),
    path('owner/products/<int:pk>/delete/', views.owner_product_delete, name='owner_product_delete'),
]

