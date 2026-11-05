from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('CUSTOMER', 'Customer'),
        ('OWNER', 'Store Owner / Admin'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='CUSTOMER',
        help_text="Role determining user permissions"
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text="Customer contact number for order and delivery coordination"
    )
    delivery_address = models.TextField(
        blank=True,
        help_text="Saved delivery address (Street, Apartment, Landmark)"
    )
    city = models.CharField(max_length=100, blank=True, default="Bengaluru")
    pincode = models.CharField(max_length=10, blank=True)

    @property
    def is_owner_user(self):
        return self.role == 'OWNER' or self.is_superuser

    @property
    def is_customer_user(self):
        return self.role == 'CUSTOMER'

    def __str__(self):
        display_name = self.get_full_name() or self.username
        return f"{display_name} ({self.get_role_display()})"
