from .cart import Cart


def cart_context(request):
    """
    Context processor providing cart information across all templates.
    """
    cart = Cart(request)
    return {
        'cart': cart,
        'cart_count': len(cart),
        'cart_total': cart.get_subtotal(),
    }

