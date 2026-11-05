from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Sum, Count, Q
from django.utils import timezone
from .models import Order, OrderItem, UpiSetting
from .cart import Cart
from .forms import CheckoutForm, UpiReferenceForm, UpiSettingForm
from .utils import create_order_upi_qr, generate_upi_payload, generate_preview_qr_base64
from products.models import Product
from users.decorators import owner_required, customer_required


# ==========================================
# CART VIEWS
# ==========================================

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'orders/cart.html', {'cart': cart})


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    if not product.in_stock:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': f'{product.name} is currently out of stock.'}, status=400)
        messages.error(request, f"{product.name} is currently out of stock.")
        return redirect(request.META.get('HTTP_REFERER', 'catalog'))

    cart.add(product=product, quantity=quantity)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'Added {product.name} to cart!',
            'cart_count': len(cart),
            'cart_subtotal': float(cart.get_subtotal()),
            'delivery_fee': float(cart.get_delivery_fee()),
            'cart_grand_total': float(cart.get_grand_total()),
        })

    messages.success(request, f"Added {product.name} ({product.unit}) to your cart.")
    return redirect(request.META.get('HTTP_REFERER', 'catalog'))


@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    if quantity > product.stock_quantity:
        return JsonResponse({
            'success': False,
            'message': f"Only {product.stock_quantity} units available in stock."
        }, status=400)

    cart.update(product=product, quantity=quantity)
    
    # Calculate updated item total
    item_total = float(product.price * quantity)

    return JsonResponse({
        'success': True,
        'item_quantity': quantity,
        'item_total': item_total,
        'cart_count': len(cart),
        'cart_subtotal': float(cart.get_subtotal()),
        'delivery_fee': float(cart.get_delivery_fee()),
        'cart_grand_total': float(cart.get_grand_total()),
    })


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'Removed {product.name} from cart.',
            'cart_count': len(cart),
            'cart_subtotal': float(cart.get_subtotal()),
            'delivery_fee': float(cart.get_delivery_fee()),
            'cart_grand_total': float(cart.get_grand_total()),
        })

    messages.info(request, f"Removed {product.name} from your cart.")
    return redirect('cart_detail')


def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    messages.info(request, "Your cart has been cleared.")
    return redirect('cart_detail')


# ==========================================
# CHECKOUT & PAYMENT VIEWS
# ==========================================

@login_required
def checkout_view(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, "Your cart is empty. Add dairy products before checkout.")
        return redirect('catalog')

    # Verify inventory availability before proceeding
    for item in cart:
        product = item['product']
        if item['quantity'] > product.stock_quantity:
            messages.error(request, f"Insufficient stock for {product.name}. Only {product.stock_quantity} available.")
            return redirect('cart_detail')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)
                order.customer = request.user
                order.total_amount = cart.get_grand_total()
                order.payment_status = 'PENDING'
                order.order_status = 'PENDING'
                order.save()

                # Save order items and deduct stock
                for item in cart:
                    product = item['product']
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        product_name=product.name,
                        unit=product.unit,
                        quantity=item['quantity'],
                        unit_price=item['price'],
                        subtotal=item['total_price']
                    )
                    # Deduct inventory
                    product.stock_quantity = max(0, product.stock_quantity - item['quantity'])
                    if product.stock_quantity == 0:
                        product.is_available = False
                    product.save()

                # If customer chose UPI, generate dynamic QR code
                if order.payment_method == 'UPI':
                    create_order_upi_qr(order)
                    cart.clear()
                    messages.success(request, f"Order #{order.order_number} initiated! Please scan the UPI QR code to complete payment.")
                    return redirect('payment_upi', order_number=order.order_number)
                else:
                    # Cash on Delivery
                    cart.clear()
                    messages.success(request, f"Order #{order.order_number} placed successfully with Cash on Delivery!")
                    return redirect('order_success', order_number=order.order_number)
        else:
            messages.error(request, "Please correct the errors in the checkout form.")
    else:
        # Prepopulate with user saved profile info
        initial_data = {
            'first_name': request.user.first_name or request.user.username,
            'delivery_address': request.user.delivery_address or '',
            'delivery_phone': request.user.phone or '',
            'delivery_slot': 'MORNING',
            'payment_method': 'COD',
        }
        form = CheckoutForm(initial=initial_data)

    return render(request, 'orders/checkout.html', {
        'form': form,
        'cart': cart,
    })


@login_required
def payment_upi_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)

    # Security check: only order owner or store owner can view
    if order.customer != request.user and not request.user.is_owner_user:
        messages.error(request, "Unauthorized access to order payment.")
        return redirect('home')

    upi_setting = UpiSetting.get_settings()

    # Always generate/refresh live dynamic QR data URI using current store UPI settings
    qr_data_uri = create_order_upi_qr(order)

    if request.method == 'POST':
        form = UpiReferenceForm(request.POST)
        if form.is_valid():
            order.upi_ref_number = form.cleaned_data['upi_ref_number'].strip()
            order.save(update_fields=['upi_ref_number'])
            messages.success(
                request,
                f"UPI Reference {order.upi_ref_number} submitted! The store owner will verify and confirm your order shortly."
            )
            return redirect('order_detail', order_number=order.order_number)
    else:
        form = UpiReferenceForm(initial={'upi_ref_number': order.upi_ref_number or ''})

    return render(request, 'orders/payment_upi.html', {
        'order': order,
        'form': form,
        'upi_setting': upi_setting,
        'qr_data_uri': qr_data_uri,
    })


@login_required
@require_POST
def switch_order_to_cod(request, order_number):
    """
    Allows customers (or store owners) to easily switch an unpaid order to Cash on Delivery (COD).
    """
    order = get_object_or_404(Order, order_number=order_number)
    if order.customer != request.user and not request.user.is_owner_user:
        messages.error(request, "Unauthorized access to order.")
        return redirect('home')

    if order.order_status in ['DELIVERED', 'CANCELLED']:
        messages.warning(request, "Cannot change payment method for this completed order.")
        return redirect('order_detail', order_number=order.order_number)

    order.payment_method = 'COD'
    order.payment_status = 'PENDING'
    order.save(update_fields=['payment_method', 'payment_status'])
    messages.success(request, f"Order #{order.order_number} has been switched to Cash on Delivery (COD)! You can pay ₹{order.total_amount} in cash upon doorstep delivery.")
    return redirect('order_detail', order_number=order.order_number)


@login_required
@require_POST
def customer_cancel_order(request, order_number):
    """
    Allows a customer to cancel an order before it is dispatched (OUT_FOR_DELIVERY).
    Restores product inventory back to stock upon cancellation.
    """
    order = get_object_or_404(Order, order_number=order_number)

    # Permission check: must be the order customer or store owner
    if order.customer != request.user and not request.user.is_owner_user:
        messages.error(request, "Unauthorized access to order.")
        return redirect('home')

    if not order.can_be_cancelled_by_customer:
        messages.warning(
            request,
            f"Order #{order.order_number} cannot be cancelled as it is already '{order.get_order_status_display()}'."
        )
        return redirect('order_detail', order_number=order.order_number)

    with transaction.atomic():
        order.order_status = 'CANCELLED'
        if order.payment_status == 'PENDING':
            order.payment_status = 'FAILED'
        order.save(update_fields=['order_status', 'payment_status'])

        # Restock product quantities
        for item in order.items.all():
            if item.product:
                item.product.stock_quantity += item.quantity
                if item.product.stock_quantity > 0:
                    item.product.is_available = True
                item.product.save(update_fields=['stock_quantity', 'is_available'])

    messages.success(
        request,
        f"Order #{order.order_number} has been cancelled successfully. All items have been returned to inventory."
    )
    referer = request.META.get('HTTP_REFERER')
    if referer and ('/orders/' in referer or '/shop/' in referer):
        return redirect(referer)
    return redirect('order_detail', order_number=order.order_number)



@login_required
def order_success_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    if order.customer != request.user and not request.user.is_owner_user:
        return redirect('home')

    return render(request, 'orders/order_success.html', {'order': order})


@login_required
def order_history_view(request):
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'orders/order_history.html', {'orders': orders})


@login_required
def order_detail_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    if order.customer != request.user and not request.user.is_owner_user:
        messages.error(request, "You are not authorized to view this order.")
        return redirect('home')

    # Steps for timeline
    timeline_steps = [
        {'code': 'PENDING', 'label': 'Order Placed', 'desc': 'Awaiting confirmation'},
        {'code': 'ACCEPTED', 'label': 'Accepted', 'desc': 'Packed at dairy farm'},
        {'code': 'OUT_FOR_DELIVERY', 'label': 'Out for Delivery', 'desc': 'Delivery agent on route'},
        {'code': 'DELIVERED', 'label': 'Delivered', 'desc': 'Delivered fresh at your doorstep'},
    ]

    status_order = ['PENDING', 'ACCEPTED', 'OUT_FOR_DELIVERY', 'DELIVERED']
    current_index = status_order.index(order.order_status) if order.order_status in status_order else -1

    return render(request, 'orders/order_detail.html', {
        'order': order,
        'timeline_steps': timeline_steps,
        'current_index': current_index,
    })


# ==========================================
# OWNER DASHBOARD & ACTIONS
# ==========================================

@owner_required
def owner_dashboard_view(request):
    status_filter = request.GET.get('status', 'ALL').upper()
    payment_filter = request.GET.get('payment', 'ALL').upper()
    search_q = request.GET.get('q', '').strip()

    orders_qs = Order.objects.all().select_related('customer').prefetch_related('items').order_by('-created_at')

    if status_filter and status_filter != 'ALL':
        orders_qs = orders_qs.filter(order_status=status_filter)

    if payment_filter and payment_filter != 'ALL':
        orders_qs = orders_qs.filter(payment_status=payment_filter)

    if search_q:
        orders_qs = orders_qs.filter(
            Q(order_number__icontains=search_q) |
            Q(customer__first_name__icontains=search_q) |
            Q(customer__phone__icontains=search_q) |
            Q(delivery_phone__icontains=search_q) |
            Q(upi_ref_number__icontains=search_q)
        )

    # Key Analytics & Metrics
    total_orders = Order.objects.count()
    pending_orders_count = Order.objects.filter(order_status='PENDING').count()
    accepted_orders_count = Order.objects.filter(order_status='ACCEPTED').count()
    out_for_delivery_count = Order.objects.filter(order_status='OUT_FOR_DELIVERY').count()
    delivered_orders_count = Order.objects.filter(order_status='DELIVERED').count()
    
    total_revenue = Order.objects.filter(
        Q(payment_status='VERIFIED') | Q(order_status='DELIVERED')
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    pending_upi_verification_count = Order.objects.filter(
        payment_method='UPI', payment_status='PENDING'
    ).count()

    low_stock_products = Product.objects.filter(stock_quantity__lt=10, is_available=True)
    all_products = Product.objects.all().order_by('category', 'name')

    context = {
        'orders': orders_qs,
        'selected_status': status_filter,
        'selected_payment': payment_filter,
        'search_q': search_q,
        'total_orders': total_orders,
        'pending_orders_count': pending_orders_count,
        'accepted_orders_count': accepted_orders_count,
        'out_for_delivery_count': out_for_delivery_count,
        'delivered_orders_count': delivered_orders_count,
        'total_revenue': total_revenue,
        'pending_upi_verification_count': pending_upi_verification_count,
        'low_stock_products': low_stock_products,
        'all_products': all_products,
        'status_choices': Order.ORDER_STATUS_CHOICES,
        'upi_setting': UpiSetting.get_settings(),
    }
    return render(request, 'orders/owner_dashboard.html', context)


@owner_required
@require_POST
def owner_update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get('order_status')

    valid_statuses = [choice[0] for choice in Order.ORDER_STATUS_CHOICES]
    if new_status in valid_statuses:
        old_status = order.get_order_status_display()
        order.order_status = new_status
        
        # If moving to delivered and COD, also mark payment verified
        if new_status == 'DELIVERED' and order.payment_method == 'COD':
            order.payment_status = 'VERIFIED'
            
        order.save()
        messages.success(request, f"Order #{order.order_number} status updated to {order.get_order_status_display()}.")
    else:
        messages.error(request, "Invalid order status provided.")

    return redirect(request.META.get('HTTP_REFERER', 'owner_dashboard'))


@owner_required
@require_POST
def owner_update_payment_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get('payment_status')

    valid_statuses = [choice[0] for choice in Order.PAYMENT_STATUS_CHOICES]
    if new_status in valid_statuses:
        order.payment_status = new_status
        order.save()
        messages.success(request, f"Payment for Order #{order.order_number} marked as {order.get_payment_status_display()}.")
    else:
        messages.error(request, "Invalid payment status provided.")

    return redirect(request.META.get('HTTP_REFERER', 'owner_dashboard'))


@owner_required
def owner_upi_settings_view(request):
    """
    Dedicated view for store owners to update their UPI ID (VPA),
    merchant display name, custom QR image sticker, and QR mode.
    """
    upi_setting = UpiSetting.get_settings()

    if request.method == 'POST':
        form = UpiSettingForm(request.POST, request.FILES, instance=upi_setting)
        if form.is_valid():
            updated_setting = form.save(commit=False)

            # Auto-activate CUSTOM QR mode if a new custom QR image was uploaded
            if 'custom_qr_image' in request.FILES and request.FILES['custom_qr_image']:
                updated_setting.qr_mode = 'CUSTOM'
            elif not updated_setting.custom_qr_image and updated_setting.qr_mode == 'CUSTOM':
                updated_setting.qr_mode = 'DYNAMIC'

            updated_setting.save()

            # Refresh dynamic QR codes for any unpaid pending orders
            regenerated_count = 0
            if request.POST.get('regenerate_pending_qrs') == 'on':
                pending_upi_orders = Order.objects.filter(payment_method='UPI', payment_status='PENDING')
                for o in pending_upi_orders:
                    create_order_upi_qr(o)
                    regenerated_count += 1

            mode_name = "Custom Standee QR" if updated_setting.qr_mode == 'CUSTOM' else "Dynamic Amount QR"
            msg = f"UPI Payment Settings saved! Store UPI is '{updated_setting.upi_id}' (Mode: {mode_name})."
            if regenerated_count > 0:
                msg += f" {regenerated_count} pending order QR codes have been updated with the new UPI ID."
            messages.success(request, msg)
            return redirect('owner_upi_settings')
        else:
            messages.error(request, "Please correct the errors in the UPI configuration form.")
    else:
        form = UpiSettingForm(instance=upi_setting)

    # Generate live preview QR for the current settings
    preview_qr_b64, preview_payload = generate_preview_qr_base64(
        upi_id=upi_setting.upi_id,
        merchant_name=upi_setting.merchant_name,
        amount="150.00"
    )

    return render(request, 'orders/owner_upi_settings.html', {
        'form': form,
        'upi_setting': upi_setting,
        'preview_qr_b64': preview_qr_b64,
        'preview_payload': preview_payload,
    })


@owner_required
@require_POST
def owner_remove_custom_qr_view(request):
    """
    Safely removes the uploaded custom QR sticker and reverts store to dynamic QR mode.
    """
    upi_setting = UpiSetting.get_settings()
    if upi_setting.custom_qr_image:
        upi_setting.custom_qr_image.delete(save=False)
        upi_setting.custom_qr_image = None
        upi_setting.qr_mode = 'DYNAMIC'
        upi_setting.save()
        messages.success(request, "Custom QR sticker removed. Store has reverted to automatic Dynamic QR generation.")
    return redirect('owner_upi_settings')


