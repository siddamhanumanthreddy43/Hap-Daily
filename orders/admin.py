from django.contrib import admin
from .models import Order, OrderItem, UpiSetting


@admin.register(UpiSetting)
class UpiSettingAdmin(admin.ModelAdmin):
    list_display = ('merchant_name', 'upi_id', 'qr_mode', 'is_active', 'updated_at')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'unit', 'unit_price', 'quantity', 'subtotal')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer', 'total_amount', 'payment_method', 'payment_status', 'order_status', 'delivery_slot', 'created_at')
    list_filter = ('order_status', 'payment_status', 'payment_method', 'delivery_slot', 'created_at')
    search_fields = ('order_number', 'customer__username', 'customer__email', 'delivery_phone', 'upi_ref_number')
    inlines = [OrderItemInline]
