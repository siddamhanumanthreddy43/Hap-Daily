from decimal import Decimal
from django.conf import settings
from products.models import Product


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if cart is None:
            cart = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price)
            }

        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity

        if self.cart[product_id]['quantity'] <= 0:
            self.remove(product)
        else:
            self.session['cart'] = self.cart
            self.save()

    def update(self, product, quantity):
        self.add(product, quantity=quantity, override_quantity=True)

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.session['cart'] = self.cart
            self.save()

    def clear(self):
        if 'cart' in self.session:
            del self.session['cart']
        self.save()

    def save(self):
        self.session.modified = True

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()

        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            if 'product' in item:
                item['price'] = Decimal(item['price'])
                item['total_price'] = item['price'] * item['quantity']
                yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_subtotal(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def get_delivery_threshold(self):
        """Returns the order subtotal amount above which delivery is free (default ₹199)."""
        try:
            from .models import UpiSetting
            return UpiSetting.get_settings().free_delivery_threshold
        except Exception:
            return getattr(settings, 'FREE_DELIVERY_THRESHOLD', Decimal('199.00'))

    def get_standard_delivery_fee(self):
        """Returns standard delivery fee (default ₹5.00)."""
        try:
            from .models import UpiSetting
            return UpiSetting.get_settings().delivery_fee
        except Exception:
            return getattr(settings, 'DEFAULT_DELIVERY_FEE', Decimal('5.00'))

    def get_delivery_fee(self):
        subtotal = self.get_subtotal()
        threshold = self.get_delivery_threshold()
        if subtotal == 0 or subtotal >= threshold:
            return Decimal('0.00')
        return self.get_standard_delivery_fee()

    def get_grand_total(self):
        return self.get_subtotal() + self.get_delivery_fee()

