import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from products.models import Product


class Order(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('COD', 'Cash on Delivery (COD)'),
        ('UPI', 'UPI / QR Code Scan (GPay, PhonePe, Paytm)'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending Verification'),
        ('VERIFIED', 'Payment Verified / Paid'),
        ('FAILED', 'Payment Failed / Rejected'),
    ]

    ORDER_STATUS_CHOICES = [
        ('PENDING', 'Pending Confirmation'),
        ('ACCEPTED', 'Accepted'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]

    DELIVERY_SLOT_CHOICES = [
        ('MORNING', 'Morning Slot (6:00 AM - 9:00 AM)'),
        ('EVENING', 'Evening Slot (5:00 PM - 8:00 PM)'),
    ]

    order_number = models.CharField(max_length=50, unique=True, editable=False)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total order amount in INR")
    
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, default='COD')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='PENDING')
    
    delivery_slot = models.CharField(max_length=20, choices=DELIVERY_SLOT_CHOICES, default='MORNING')
    delivery_address = models.TextField(help_text="Full address specified at checkout")
    delivery_phone = models.CharField(max_length=15, help_text="Delivery contact phone")
    
    # UPI Specific fields
    upi_intent_url = models.TextField(blank=True, help_text="Dynamic upi://pay link")
    upi_qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True, help_text="Generated QR image")
    upi_ref_number = models.CharField(max_length=100, blank=True, null=True, help_text="Customer submitted UTR/Txn ID")
    
    notes = models.TextField(blank=True, help_text="Delivery instructions or gate codes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate readable unique order ID, e.g. AMS-2026-A1B2C3
            self.order_number = f"AMS-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.order_number} - {self.customer.get_full_name() or self.customer.username} (₹{self.total_amount})"

    @property
    def status_badge_color(self):
        """Helper to return Tailwind color classes for order status badges"""
        colors = {
            'PENDING': 'bg-amber-100 text-amber-800 border-amber-300',
            'ACCEPTED': 'bg-blue-100 text-blue-800 border-blue-300',
            'OUT_FOR_DELIVERY': 'bg-purple-100 text-purple-800 border-purple-300',
            'DELIVERED': 'bg-emerald-100 text-emerald-800 border-emerald-300',
            'CANCELLED': 'bg-rose-100 text-rose-800 border-rose-300',
        }
        return colors.get(self.order_status, 'bg-gray-100 text-gray-800')

    @property
    def payment_badge_color(self):
        colors = {
            'PENDING': 'bg-amber-100 text-amber-800',
            'VERIFIED': 'bg-emerald-100 text-emerald-800',
            'FAILED': 'bg-rose-100 text-rose-800',
        }
        return colors.get(self.payment_status, 'bg-gray-100 text-gray-800')

    @property
    def can_be_cancelled_by_customer(self):
        """Customers can cancel orders that are PENDING or ACCEPTED (before being dispatched)."""
        return self.order_status in ['PENDING', 'ACCEPTED']


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=200)
    unit = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_name} x {self.quantity} ({self.order.order_number})"


class UpiSetting(models.Model):
    QR_MODE_CHOICES = [
        ('DYNAMIC', 'Dynamic QR Code (Auto-generates with exact order amount)'),
        ('CUSTOM', 'Custom Uploaded QR Image (Laminated Store Sticker / Standee)'),
    ]

    merchant_name = models.CharField(
        max_length=150,
        default="Arokya Milk Store",
        help_text="Store / Business name shown on customer's UPI app"
    )
    upi_id = models.CharField(
        max_length=100,
        default="arokyamilk@upi",
        help_text="Your UPI Virtual Payment Address (e.g. 9876543210@paytm, store@okaxis, shop@upi)"
    )
    qr_mode = models.CharField(
        max_length=20,
        choices=QR_MODE_CHOICES,
        default='DYNAMIC',
        help_text="Choose whether customers see an automatic dynamic QR or your custom uploaded QR sticker"
    )
    custom_qr_image = models.ImageField(
        upload_to='upi_settings/',
        blank=True,
        null=True,
        help_text="Upload your own shop's printed/laminated QR code image (PhonePe/GPay/Paytm standee)"
    )
    instructions = models.TextField(
        blank=True,
        default="Scan with any UPI app (GPay, PhonePe, Paytm, BHIM) and enter the 12-digit UTR reference number below.",
        help_text="Custom instructions displayed to customers on the UPI payment page"
    )
    delivery_fee = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('5.00'),
        help_text="Standard delivery fee in INR charged on orders below the free delivery threshold"
    )
    free_delivery_threshold = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('199.00'),
        help_text="Orders equal to or above this cart subtotal in INR qualify for Free Delivery"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Enable or disable UPI payment option across the store"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Store & Payment Setting"
        verbose_name_plural = "Store & Payment Settings"

    def __str__(self):
        return f"Store Settings (UPI: {self.upi_id}, Delivery: ₹{self.delivery_fee})"

    @classmethod
    def get_settings(cls):
        """
        Singleton-style helper: returns the active configuration without triggering
        unnecessary write locks on read-only serverless databases.
        """
        try:
            setting = cls.objects.filter(id=1).first()
            if setting:
                return setting
        except Exception:
            pass

        try:
            setting, _ = cls.objects.get_or_create(id=1, defaults={
                'merchant_name': 'Arokya Milk Store',
                'upi_id': 'arokyamilk@upi',
                'qr_mode': 'DYNAMIC',
                'instructions': 'Scan with any UPI app (GPay, PhonePe, Paytm, BHIM) and enter the 12-digit UTR reference number below.',
                'delivery_fee': Decimal('5.00'),
                'free_delivery_threshold': Decimal('199.00'),
                'is_active': True,
            })
            return setting
        except Exception:
            # Fallback memory instance if database is read-only (e.g. AWS Lambda / Vercel initial load)
            return cls(
                id=1,
                merchant_name='Arokya Milk Store',
                upi_id='arokyamilk@upi',
                qr_mode='DYNAMIC',
                instructions='Scan with any UPI app (GPay, PhonePe, Paytm, BHIM) and enter the 12-digit UTR reference number below.',
                delivery_fee=Decimal('5.00'),
                free_delivery_threshold=Decimal('199.00'),
                is_active=True,
            )

