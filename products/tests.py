from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from products.models import Product
from users.models import CustomUser


class ProductModelAndCatalogTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = CustomUser.objects.create_user(
            username='owner_user',
            password='password123',
            role='OWNER',
            is_staff=True
        )
        self.product = Product.objects.create(
            name='Test Whole Milk',
            category='MILK',
            unit='1 Litre',
            price=Decimal('65.00'),
            stock_quantity=20,
            is_available=True
        )

    def test_product_in_stock(self):
        self.assertTrue(self.product.in_stock)
        self.product.stock_quantity = 0
        self.product.save()
        self.assertFalse(self.product.in_stock)

    def test_catalog_view(self):
        response = self.client.get(reverse('catalog'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Whole Milk')

    def test_owner_toggle_stock(self):
        self.client.login(username='owner_user', password='password123')
        url = reverse('owner_toggle_stock', kwargs={'pk': self.product.id})
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.product.refresh_from_db()
        self.assertFalse(self.product.is_available)

    def test_owner_update_price(self):
        self.client.login(username='owner_user', password='password123')
        url = reverse('owner_update_price', kwargs={'pk': self.product.id})
        response = self.client.post(url, {
            'price': '72.50',
            'stock_quantity': '35'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.product.refresh_from_db()
        self.assertEqual(self.product.price, Decimal('72.50'))
        self.assertEqual(self.product.stock_quantity, 35)

    def test_owner_product_delete_get_confirm(self):
        self.client.login(username='owner_user', password='password123')
        url = reverse('owner_product_delete', kwargs={'pk': self.product.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Completely Delete Product?')

    def test_owner_product_delete_post(self):
        self.client.login(username='owner_user', password='password123')
        prod_id = self.product.id
        url = reverse('owner_product_delete', kwargs={'pk': prod_id})
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Product.objects.filter(id=prod_id).exists())
