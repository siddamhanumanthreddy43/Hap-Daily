from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from users.models import CustomUser
from products.models import Product
from orders.models import Order, OrderItem, UpiSetting
from orders.cart import Cart
from orders.utils import create_order_upi_qr, generate_upi_payload


class CartAndOrderFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer = CustomUser.objects.create_user(
            username='test_buyer',
            password='password123',
            email='buyer@test.com',
            role='CUSTOMER',
            delivery_address='42 Lake Road, Bengaluru',
            phone='9988776655'
        )
        self.owner = CustomUser.objects.create_user(
            username='store_owner',
            password='password123',
            role='OWNER',
            is_staff=True
        )
        self.milk = Product.objects.create(
            name='Farm Milk 1L',
            category='MILK',
            unit='1 Litre',
            price=Decimal('60.00'),
            stock_quantity=50,
            is_available=True
        )
        self.paneer = Product.objects.create(
            name='Fresh Paneer 200g',
            category='PANEER',
            unit='200g',
            price=Decimal('90.00'),
            stock_quantity=30,
            is_available=True
        )

    def test_cart_add_and_delivery_fee(self):
        # Add 1 milk (₹60) -> Subtotal < 199, delivery fee should be 5.00
        self.client.post(reverse('cart_add', kwargs={'product_id': self.milk.id}), {'quantity': 1})
        cart = Cart(self.client)
        self.assertEqual(cart.get_subtotal(), Decimal('60.00'))
        self.assertEqual(cart.get_delivery_fee(), Decimal('5.00'))
        self.assertEqual(cart.get_grand_total(), Decimal('65.00'))

        # Add 2 paneer (2 * 90 = 180) -> Subtotal 60 + 180 = 240 >= 199 -> Free delivery
        self.client.post(reverse('cart_add', kwargs={'product_id': self.paneer.id}), {'quantity': 2})
        cart = Cart(self.client)
        self.assertEqual(cart.get_subtotal(), Decimal('240.00'))
        self.assertEqual(cart.get_delivery_fee(), Decimal('0.00'))
        self.assertEqual(cart.get_grand_total(), Decimal('240.00'))

    def test_checkout_cod_flow(self):
        self.client.login(username='test_buyer', password='password123')
        # Add product to cart
        self.client.post(reverse('cart_add', kwargs={'product_id': self.milk.id}), {'quantity': 2})

        # Submit checkout for COD
        response = self.client.post(reverse('checkout'), {
            'first_name': 'Test Buyer',
            'delivery_address': '42 Lake Road, Bengaluru',
            'delivery_phone': '9988776655',
            'delivery_slot': 'MORNING',
            'payment_method': 'COD',
            'notes': 'Leave at door',
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        # Order should exist
        order = Order.objects.filter(customer=self.customer).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.payment_method, 'COD')
        self.assertEqual(order.order_status, 'PENDING')
        self.assertEqual(order.items.count(), 1)

        # Stock should be decremented
        self.milk.refresh_from_db()
        self.assertEqual(self.milk.stock_quantity, 48)

    def test_upi_qr_generation(self):
        order = Order.objects.create(
            customer=self.customer,
            total_amount=Decimal('150.00'),
            payment_method='UPI',
            delivery_address='42 Lake Road',
            delivery_phone='9988776655'
        )
        b64_qr = create_order_upi_qr(order)
        self.assertTrue(b64_qr.startswith('data:image/png;base64,'))
        self.assertIn('upi://pay?pa=arokyamilk%40upi', order.upi_intent_url)
        self.assertTrue(bool(order.upi_qr_code))

    def test_owner_accept_and_status_transitions(self):
        order = Order.objects.create(
            customer=self.customer,
            total_amount=Decimal('150.00'),
            payment_method='UPI',
            order_status='PENDING',
            delivery_address='42 Lake Road',
            delivery_phone='9988776655'
        )

        self.client.login(username='store_owner', password='password123')

        # 1. Accept Order
        self.client.post(reverse('owner_update_order_status', kwargs={'order_id': order.id}), {
            'order_status': 'ACCEPTED'
        })
        order.refresh_from_db()
        self.assertEqual(order.order_status, 'ACCEPTED')

        # 2. Mark Out for Delivery
        self.client.post(reverse('owner_update_order_status', kwargs={'order_id': order.id}), {
            'order_status': 'OUT_FOR_DELIVERY'
        })
        order.refresh_from_db()
        self.assertEqual(order.order_status, 'OUT_FOR_DELIVERY')

        # 3. Mark Delivered
        self.client.post(reverse('owner_update_order_status', kwargs={'order_id': order.id}), {
            'order_status': 'DELIVERED'
        })
        order.refresh_from_db()
        self.assertEqual(order.order_status, 'DELIVERED')

    def test_switch_order_to_cod(self):
        order = Order.objects.create(
            customer=self.customer,
            total_amount=Decimal('150.00'),
            payment_method='UPI',
            order_status='PENDING',
            delivery_address='42 Lake Road',
            delivery_phone='9988776655'
        )
        self.client.login(username='test_buyer', password='password123')
        url = reverse('switch_to_cod', kwargs={'order_number': order.order_number})
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.payment_method, 'COD')

    def test_owner_upi_settings_get(self):
        self.client.login(username='store_owner', password='password123')
        url = reverse('owner_upi_settings')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "UPI & Payment Settings")

    def test_owner_upi_settings_post_update(self):
        self.client.login(username='store_owner', password='password123')
        url = reverse('owner_upi_settings')
        response = self.client.post(url, {
            'merchant_name': 'Arokya Dairy Farm',
            'upi_id': '9876543210@paytm',
            'qr_mode': 'DYNAMIC',
            'instructions': 'Pay via Paytm or GPay',
            'delivery_fee': '5.00',
            'free_delivery_threshold': '199.00',
            'is_active': True,
        }, follow=True)
        self.assertEqual(response.status_code, 200)

        # Check that UpiSetting updated
        setting = UpiSetting.get_settings()
        self.assertEqual(setting.upi_id, '9876543210@paytm')
        self.assertEqual(setting.merchant_name, 'Arokya Dairy Farm')
        self.assertEqual(setting.delivery_fee, Decimal('5.00'))

        # Generate payload for an order and verify updated UPI ID is used
        order = Order.objects.create(
            customer=self.customer,
            total_amount=Decimal('220.00'),
            payment_method='UPI',
            order_status='PENDING',
            delivery_address='42 Lake Road',
            delivery_phone='9988776655'
        )
        payload = generate_upi_payload(order)
        self.assertIn('9876543210%40paytm', payload)
        self.assertIn('Arokya+Dairy+Farm', payload)

    def test_customer_cannot_access_owner_upi_settings(self):
        self.client.login(username='test_buyer', password='password123')
        url = reverse('owner_upi_settings')
        response = self.client.get(url)
        # Should be redirected to home or forbidden
        self.assertEqual(response.status_code, 302)

    def test_customer_cancel_pending_order_restocks_inventory(self):
        self.client.login(username='test_buyer', password='password123')
        initial_stock = self.milk.stock_quantity

        # 1. Place order
        order = Order.objects.create(
            customer=self.customer,
            total_amount=Decimal('120.00'),
            payment_method='COD',
            order_status='PENDING',
            delivery_address='42 Lake Road',
            delivery_phone='9988776655'
        )
        OrderItem.objects.create(
            order=order,
            product=self.milk,
            product_name=self.milk.name,
            unit=self.milk.unit,
            quantity=2,
            unit_price=Decimal('60.00'),
            subtotal=Decimal('120.00')
        )
        self.milk.stock_quantity -= 2
        self.milk.save()

        self.assertEqual(self.milk.stock_quantity, initial_stock - 2)

        # 2. Cancel order
        cancel_url = reverse('customer_cancel_order', kwargs={'order_number': order.order_number})
        response = self.client.post(cancel_url, follow=True)
        self.assertEqual(response.status_code, 200)

        order.refresh_from_db()
        self.assertEqual(order.order_status, 'CANCELLED')

        # 3. Stock should be restored
        self.milk.refresh_from_db()
        self.assertEqual(self.milk.stock_quantity, initial_stock)

    def test_cannot_cancel_dispatched_order(self):
        self.client.login(username='test_buyer', password='password123')
        order = Order.objects.create(
            customer=self.customer,
            total_amount=Decimal('120.00'),
            payment_method='COD',
            order_status='OUT_FOR_DELIVERY',
            delivery_address='42 Lake Road',
            delivery_phone='9988776655'
        )
        cancel_url = reverse('customer_cancel_order', kwargs={'order_number': order.order_number})
        response = self.client.post(cancel_url, follow=True)
        self.assertEqual(response.status_code, 200)

        # Status must remain unchanged
        order.refresh_from_db()
        self.assertEqual(order.order_status, 'OUT_FOR_DELIVERY')


