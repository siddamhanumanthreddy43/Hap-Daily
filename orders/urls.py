from django.urls import path
from . import views

urlpatterns = [
    # Cart URLs
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/update/<int:product_id>/', views.cart_update, name='cart_update'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/clear/', views.cart_clear, name='cart_clear'),

    # Checkout & Customer Payment
    path('checkout/', views.checkout_view, name='checkout'),
    path('checkout/upi/<str:order_number>/', views.payment_upi_view, name='payment_upi'),
    path('checkout/upi/<str:order_number>/switch-to-cod/', views.switch_order_to_cod, name='switch_to_cod'),
    path('order/success/<str:order_number>/', views.order_success_view, name='order_success'),
    path('orders/history/', views.order_history_view, name='order_history'),
    path('orders/<str:order_number>/', views.order_detail_view, name='order_detail'),
    path('orders/<str:order_number>/cancel/', views.customer_cancel_order, name='customer_cancel_order'),

    # Owner Dashboard & Status Operations
    path('owner/dashboard/', views.owner_dashboard_view, name='owner_dashboard'),
    path('owner/upi-settings/', views.owner_upi_settings_view, name='owner_upi_settings'),
    path('owner/upi-settings/remove-qr/', views.owner_remove_custom_qr_view, name='owner_upi_remove_qr'),
    path('owner/order/<int:order_id>/status/', views.owner_update_order_status, name='owner_update_order_status'),
    path('owner/order/<int:order_id>/payment/', views.owner_update_payment_status, name='owner_update_payment_status'),
]

