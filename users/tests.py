from django.test import TestCase, Client
from django.urls import reverse
from users.models import CustomUser


class UserRBACAndAuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer = CustomUser.objects.create_user(
            username='test_customer',
            password='password123',
            email='customer@test.com',
            phone='9876543210',
            role='CUSTOMER'
        )
        self.owner = CustomUser.objects.create_user(
            username='test_owner',
            password='password123',
            email='owner@test.com',
            phone='9845011223',
            role='OWNER',
            is_staff=True
        )

    def test_role_properties(self):
        self.assertTrue(self.customer.is_customer_user)
        self.assertFalse(self.customer.is_owner_user)

        self.assertTrue(self.owner.is_owner_user)
        self.assertFalse(self.owner.is_customer_user)

    def test_customer_cannot_access_owner_dashboard(self):
        self.client.login(username='test_customer', password='password123')
        response = self.client.get(reverse('owner_dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_owner_can_access_owner_dashboard(self):
        self.client.login(username='test_owner', password='password123')
        response = self.client.get(reverse('owner_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_dedicated_customer_login(self):
        response = self.client.post(reverse('customer_login'), {
            'username': '9876543210',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302)

    def test_customer_cannot_login_through_owner_login(self):
        # A customer account attempting owner login should be blocked with an error
        response = self.client.post(reverse('owner_login'), {
            'username': 'test_customer',
            'password': 'password123'
        }, follow=True)
        self.assertContains(response, 'Access Denied')

    def test_owner_login_success(self):
        response = self.client.post(reverse('owner_login'), {
            'username': 'test_owner',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('owner_dashboard'))

    def test_new_owner_registration(self):
        response = self.client.post(reverse('owner_register'), {
            'username': 'new_owner',
            'first_name': 'New Store Manager',
            'email': 'manager@arokyamilk.in',
            'phone': '9845099999',
            'delivery_address': 'Arokya Milk Store Outlet 5',
            'city': 'Bengaluru',
            'pincode': '560001',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('owner_dashboard'))

        # Verify role is OWNER
        new_owner = CustomUser.objects.get(username='new_owner')
        self.assertEqual(new_owner.role, 'OWNER')
        self.assertTrue(new_owner.is_owner_user)
