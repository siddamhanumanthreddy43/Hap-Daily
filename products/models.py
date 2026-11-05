from django.db import models


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('MILK', 'Fresh Milk'),
        ('CURD', 'Curd & Dahi'),
        ('PANEER', 'Fresh Paneer & Butter'),
        ('GHEE', 'Pure Desi Ghee'),
        ('ICECREAM', 'Artisan Ice Creams'),
        ('BEVERAGES', 'Flavoured Milk & Chaas'),
    ]

    name = models.CharField(max_length=200, help_text="Product title (e.g., Farm Fresh Whole Cow Milk)")
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='MILK')
    unit = models.CharField(max_length=50, help_text="Unit/Size packaging (e.g., 500ml, 1L, 200g, 1 Tub)")
    price = models.DecimalField(max_digits=8, decimal_places=2, help_text="Price in INR")
    image = models.ImageField(upload_to='products/', blank=True, null=True, help_text="Uploaded product photo")
    image_url = models.URLField(max_length=500, blank=True, null=True, help_text="External image URL fallback")
    description = models.TextField(blank=True, help_text="Detailed nutritional info, benefits, or description")
    stock_quantity = models.PositiveIntegerField(default=50, help_text="Units currently in inventory")
    is_available = models.BooleanField(default=True, help_text="Flag to quickly toggle item active/inactive in shop")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} - {self.unit} (₹{self.price})"

    @property
    def in_stock(self):
        return self.is_available and self.stock_quantity > 0

    @property
    def get_image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        if self.image_url:
            return self.image_url
        # Category-based default illustrative fallback
        category_placeholders = {
            'MILK': 'https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=600&q=80',
            'CURD': 'https://images.unsplash.com/photo-1488477181946-6428a0291777?auto=format&fit=crop&w=600&q=80',
            'PANEER': 'https://images.unsplash.com/photo-1631452180519-c014fe946bc7?auto=format&fit=crop&w=600&q=80',
            'GHEE': 'https://images.unsplash.com/photo-1589367920969-ab8e050bbb04?auto=format&fit=crop&w=600&q=80',
            'ICECREAM': 'https://images.unsplash.com/photo-1501443762994-82bd5dace89a?auto=format&fit=crop&w=600&q=80',
            'BEVERAGES': 'https://images.unsplash.com/photo-1517256064527-09c73fc73e38?auto=format&fit=crop&w=600&q=80',
        }
        return category_placeholders.get(self.category, 'https://images.unsplash.com/photo-1527153857715-3908f2ae5e81?auto=format&fit=crop&w=600&q=80')
