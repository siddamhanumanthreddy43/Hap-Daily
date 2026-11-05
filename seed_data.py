import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freshdairy.settings')
django.setup()

from users.models import CustomUser
from products.models import Product
from orders.models import Order, OrderItem
from orders.utils import create_order_upi_qr


def run_seed():
    print("[*] Seeding Arokya Milk Store Database with Accounts & Dairy Products...")

    # 1. Create or update Demo Store Owner
    owner, created = CustomUser.objects.get_or_create(username='owner', defaults={
        'email': 'owner@arokyamilk.in',
        'first_name': 'Ramesh',
        'last_name': 'Yadav',
        'role': 'OWNER',
        'is_staff': True,
        'is_superuser': True,
        'phone': '+91 98450 11223',
        'delivery_address': 'Arokya Milk Store Outlet 1, Whitefield, Bengaluru',
        'city': 'Bengaluru',
        'pincode': '560066',
    })
    owner.set_password('owner123')
    owner.role = 'OWNER'
    owner.is_staff = True
    owner.is_superuser = True
    owner.save()
    print("[OK] Store Owner Account: username='owner', password='owner123'")

    # 2. Create or update Demo Customer
    customer, created = CustomUser.objects.get_or_create(username='customer', defaults={
        'email': 'customer@example.com',
        'first_name': 'Sneha',
        'last_name': 'Kulkarni',
        'role': 'CUSTOMER',
        'phone': '+91 98765 43210',
        'delivery_address': 'Flat 304, Palm Grove Apartments, 12th Cross, Indiranagar',
        'city': 'Bengaluru',
        'pincode': '560038',
    })
    customer.set_password('customer123')
    customer.role = 'CUSTOMER'
    customer.save()
    print("[OK] Customer Account: username='customer', password='customer123'")

    # 3. Dairy Products Catalog
    products_data = [
        # MILK
        {
            'name': 'Farm Fresh Whole Cow Milk',
            'category': 'MILK',
            'unit': '1 Litre',
            'price': 68.00,
            'stock_quantity': 45,
            'description': 'Direct from pasture-fed cows. Non-homogenized, rich cream layer on top, naturally packed with calcium, vitamin B12, and healthy fats.',
            'image_url': 'https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=800&q=80',
        },
        {
            'name': 'Pasteurized Toned Fresh Milk',
            'category': 'MILK',
            'unit': '500 ml',
            'price': 29.00,
            'stock_quantity': 60,
            'description': 'Standardized 3.0% fat and 8.5% SNF. Perfect daily milk for tea, coffee, cereal, and children nutrition.',
            'image_url': 'https://images.unsplash.com/photo-1563636619-e9143da7973b?auto=format&fit=crop&w=800&q=80',
        },
        {
            'name': 'Buffalo Whole Cream Milk',
            'category': 'MILK',
            'unit': '1 Litre',
            'price': 78.00,
            'stock_quantity': 35,
            'description': 'Rich 6.5% natural fat buffalo milk. Thick texture, unmatched for traditional kheer, rich curd, and homemade mawa.',
            'image_url': 'https://images.unsplash.com/photo-1527153857715-3908f2ae5e81?auto=format&fit=crop&w=800&q=80',
        },
        {
            'name': 'Homogenized Toned Milk Pouch',
            'category': 'MILK',
            'unit': '1 Litre',
            'price': 56.00,
            'stock_quantity': 50,
            'description': 'Gently pasteurized and micro-filtered. Uniform texture and long freshness under continuous cold refrigeration.',
            'image_url': 'https://images.unsplash.com/photo-1559181567-c3190ca9959b?auto=format&fit=crop&w=800&q=80',
        },

        # CURD & DAHI
        {
            'name': 'Farm Fresh Thick Curd / Dahi',
            'category': 'CURD',
            'unit': '500 g',
            'price': 45.00,
            'stock_quantity': 40,
            'description': 'Naturally set traditional curd using authentic probiotic cultures. Thick, non-sour, and rich in gut-healthy bacteria.',
            'image_url': 'https://images.unsplash.com/photo-1488477181946-6428a0291777?auto=format&fit=crop&w=800&q=80',
        },
        {
            'name': 'Natural Set Dahi Cup',
            'category': 'CURD',
            'unit': '200 g',
            'price': 22.00,
            'stock_quantity': 55,
            'description': 'Convenient portion for lunch boxes and light meals. High protein and delicious with parathas or rice.',
            'image_url': 'https://images.unsplash.com/photo-1571212515416-fef01fc43637?auto=format&fit=crop&w=800&q=80',
        },
        {
            'name': 'Artisanal Greek Yogurt (Plain)',
            'category': 'CURD',
            'unit': '200 g',
            'price': 75.00,
            'stock_quantity': 25,
            'description': 'Triple-strained velvety yogurt with double the protein. 0% added sugar and rich velvety texture.',
            'image_url': 'https://images.unsplash.com/photo-1505253716362-afaea1d3d1af?auto=format&fit=crop&w=800&q=80',
        },

        # PANEER & BUTTER
        {
            'name': 'Fresh Malai Paneer Block',
            'category': 'PANEER',
            'unit': '200 g',
            'price': 90.00,
            'stock_quantity': 30,
            'description': 'Crafted same morning from pure cow milk and curdled with natural lemon. Ultra-soft, spongy, and melt-in-the-mouth texture.',
            'image_url': 'https://images.unsplash.com/photo-1631452180519-c014fe946bc7?auto=format&fit=crop&w=800&q=80',
        },
        {
            'name': 'Fresh Malai Paneer Family Pack',
            'category': 'PANEER',
            'unit': '500 g',
            'price': 210.00,
            'stock_quantity': 20,
            'description': 'Freshly pressed 500g paneer slab. Retains firmness and moisture without rubbery chewiness in curries and tikkas.',
            'image_url': 'https://images.unsplash.com/photo-1599488615731-7e5c2823ff28?auto=format&fit=crop&w=800&q=80',
        },
        {
            'name': 'White Cultured Makhan / Butter',
            'category': 'PANEER',
            'unit': '250 g',
            'price': 140.00,
            'stock_quantity': 18,
            'description': 'Traditional churned desi butter from cultured cream. Unsalted, preservative-free, perfect on hot rotis and dal.',
            'image_url': 'https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?auto=format&fit=crop&w=800&q=80',
        },

        # GHEE
        {
            'name': 'Pure A2 Bilona Desi Cow Ghee',
            'category': 'GHEE',
            'unit': '500 ml',
            'price': 650.00,
            'stock_quantity': 15,
            'description': 'Crafted using the ancient Vedic Bilona method from curd of grass-fed Gir cows. Golden danedar texture and divine aroma.',
            'image_url': 'https://images.unsplash.com/photo-1589367920969-ab8e050bbb04?auto=format&fit=crop&w=800&q=80',
        },
        {
            'name': 'Traditional Danedar Cow Ghee Jar',
            'category': 'GHEE',
            'unit': '1 Litre',
            'price': 1150.00,
            'stock_quantity': 12,
            'description': 'Slow-simmered in small batches with sweet nutty fragrance. Boosts immunity and digestion.',
            'image_url': 'https://images.unsplash.com/photo-1628088062854-d1870b4553da?auto=format&fit=crop&w=800&q=80',
        },

        # ICE CREAM
        {
            'name': 'Alphonso Mango Artisan Ice Cream',
            'category': 'ICECREAM',
            'unit': '500 ml Tub',
            'price': 185.00,
            'stock_quantity': 28,
            'description': 'Made with 100% Ratnagiri Alphonso mango pulp and fresh dairy cream. No artificial colors or essence.',
            'image_url': 'https://images.unsplash.com/photo-1501443762994-82bd5dace89a?auto=format&fit=crop&w=800&q=80',
        },
        {
            'name': 'Belgian Dark Chocolate Waffle Cone',
            'category': 'ICECREAM',
            'unit': '1 Cone',
            'price': 65.00,
            'stock_quantity': 40,
            'description': 'Crisp waffle cone packed with 70% dark Belgian cocoa ice cream, topped with roasted almonds and chocolate dip.',
            'image_url': 'https://images.unsplash.com/photo-1549395156-e0c1fe6fc7a5?auto=format&fit=crop&w=800&q=80',
        },
        {
            'name': 'Royal Kesar Pista Ice Cream Cup',
            'category': 'ICECREAM',
            'unit': '125 ml Cup',
            'price': 45.00,
            'stock_quantity': 35,
            'description': 'Kashmiri saffron infused whole milk ice cream generously studded with roasted Iranian pistachios.',
            'image_url': 'https://images.unsplash.com/photo-1563805042-7684c019e1cb?auto=format&fit=crop&w=800&q=80',
        },

        # BEVERAGES
        {
            'name': 'Spiced Masala Chaas / Buttermilk',
            'category': 'BEVERAGES',
            'unit': '200 ml',
            'price': 18.00,
            'stock_quantity': 50,
            'description': 'Refreshing digestive buttermilk churned with roasted cumin (jeera), fresh ginger, curry leaves, and Himalayan black salt.',
            'image_url': 'https://images.unsplash.com/photo-1517256064527-09c73fc73e38?auto=format&fit=crop&w=800&q=80',
        },
        {
            'name': 'Royal Kesar Badam Chilled Milk',
            'category': 'BEVERAGES',
            'unit': '200 ml Bottle',
            'price': 38.00,
            'stock_quantity': 45,
            'description': 'Chilled whole milk slow-cooked with real almond slivers, cardamom, and saffron strands.',
            'image_url': 'https://images.unsplash.com/photo-1572490122747-3968b75cc699?auto=format&fit=crop&w=800&q=80',
        },
    ]

    for pdata in products_data:
        prod, _ = Product.objects.update_or_create(
            name=pdata['name'],
            unit=pdata['unit'],
            defaults=pdata
        )

    print(f"[OK] Loaded {len(products_data)} Dairy Products across all categories.")

    # 4. Create Sample Orders for Demonstration
    # Order 1: UPI Order with submitted UTR pending verification
    milk = Product.objects.filter(category='MILK').first()
    curd = Product.objects.filter(category='CURD').first()
    paneer = Product.objects.filter(category='PANEER').first()

    order1, created = Order.objects.get_or_create(
        order_number='FD-DEMO-001',
        defaults={
            'customer': customer,
            'total_amount': 225.00,
            'payment_method': 'UPI',
            'payment_status': 'PENDING',
            'order_status': 'ACCEPTED',
            'delivery_slot': 'MORNING',
            'delivery_address': 'Flat 304, Palm Grove Apartments, Indiranagar, Bengaluru',
            'delivery_phone': '+91 98765 43210',
            'upi_ref_number': '430291845109',
            'notes': 'Please drop at front door milk basket',
        }
    )
    if created:
        OrderItem.objects.create(order=order1, product=milk, product_name=milk.name, unit=milk.unit, quantity=2, unit_price=milk.price, subtotal=milk.price*2)
        OrderItem.objects.create(order=order1, product=curd, product_name=curd.name, unit=curd.unit, quantity=1, unit_price=curd.price, subtotal=curd.price)
        create_order_upi_qr(order1)
        print("[OK] Sample Order 1 (UPI, Accepted) created.")

    # Order 2: COD Order Out for Delivery
    icecream = Product.objects.filter(category='ICECREAM').first()
    order2, created = Order.objects.get_or_create(
        order_number='FD-DEMO-002',
        defaults={
            'customer': customer,
            'total_amount': 275.00,
            'payment_method': 'COD',
            'payment_status': 'PENDING',
            'order_status': 'OUT_FOR_DELIVERY',
            'delivery_slot': 'EVENING',
            'delivery_address': 'Flat 304, Palm Grove Apartments, Indiranagar, Bengaluru',
            'delivery_phone': '+91 98765 43210',
            'notes': 'Call on arrival before ringing bell',
        }
    )
    if created:
        OrderItem.objects.create(order=order2, product=paneer, product_name=paneer.name, unit=paneer.unit, quantity=1, unit_price=paneer.price, subtotal=paneer.price)
        OrderItem.objects.create(order=order2, product=icecream, product_name=icecream.name, unit=icecream.unit, quantity=1, unit_price=icecream.price, subtotal=icecream.price)
        print("[OK] Sample Order 2 (COD, Out for Delivery) created.")

    print("\n[SUCCESS] Arokya Milk Store Database Ready!")


if __name__ == '__main__':
    run_seed()
