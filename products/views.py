from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from .models import Product
from .forms import ProductForm
from users.decorators import owner_required


def catalog_view(request):
    category = request.GET.get('category', '').upper()
    search_query = request.GET.get('q', '').strip()
    sort_by = request.GET.get('sort', '')

    products = Product.objects.all()

    # Filter by category
    if category and category != 'ALL':
        products = products.filter(category=category)

    # Search filter
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(unit__icontains=search_query)
        )

    # Sorting
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')

    categories = Product.CATEGORY_CHOICES

    context = {
        'products': products,
        'categories': categories,
        'selected_category': category or 'ALL',
        'search_query': search_query,
        'sort_by': sort_by,
    }
    return render(request, 'products/catalog.html', context)


def product_detail_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    related_products = Product.objects.filter(category=product.category).exclude(pk=product.pk)[:4]
    return render(request, 'products/product_detail.html', {
        'product': product,
        'related_products': related_products,
    })


@owner_required
def owner_product_list(request):
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'products/owner_product_list.html', {'products': products})


@owner_required
def owner_product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"Product '{product.name}' has been added successfully to FreshDairy inventory.")
            return redirect('owner_dashboard')
        else:
            messages.error(request, "Failed to add product. Please check the form errors.")
    else:
        form = ProductForm()

    return render(request, 'products/owner_product_form.html', {
        'form': form,
        'title': 'Add New Dairy Product'
    })


@owner_required
def owner_product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"Product '{product.name}' updated successfully.")
            return redirect('owner_dashboard')
        else:
            messages.error(request, "Failed to update product. Please check errors.")
    else:
        form = ProductForm(instance=product)

    return render(request, 'products/owner_product_form.html', {
        'form': form,
        'product': product,
        'title': f'Edit Product: {product.name}'
    })


@owner_required
@require_POST
def owner_toggle_stock(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.is_available = not product.is_available
    product.save()

    status_str = "Available (In Stock)" if product.is_available else "Out of Stock (Disabled)"
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'is_available': product.is_available,
            'message': f"{product.name} is now {status_str}"
        })

    messages.info(request, f"{product.name} is now marked as {status_str}.")
    return redirect(request.META.get('HTTP_REFERER', 'owner_dashboard'))


@owner_required
@require_POST
def owner_update_price(request, pk):
    product = get_object_or_404(Product, pk=pk)
    new_price = request.POST.get('price')
    new_stock = request.POST.get('stock_quantity')

    if new_price is not None and new_price.strip() != '':
        try:
            product.price = Decimal(new_price.strip())
        except (ValueError, InvalidOperation):
            messages.error(request, "Invalid price format.")
            return redirect(request.META.get('HTTP_REFERER', 'owner_dashboard'))

    if new_stock is not None and new_stock.strip() != '':
        try:
            product.stock_quantity = max(0, int(new_stock.strip()))
            if product.stock_quantity > 0:
                product.is_available = True
        except ValueError:
            pass

    product.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f"Price for '{product.name}' updated to ₹{product.price}",
            'price': float(product.price),
            'stock_quantity': product.stock_quantity
        })

    messages.success(request, f"Updated '{product.name}' price to ₹{product.price} (Stock: {product.stock_quantity} units).")
    return redirect(request.META.get('HTTP_REFERER', 'owner_dashboard'))


@owner_required
def owner_product_delete(request, pk):
    """
    Completely deletes an old dairy product from the database catalog.
    Handles both direct POST deletion and GET confirmation screen.
    """
    product = get_object_or_404(Product, pk=pk)
    name = product.name
    unit = product.unit

    if request.method == 'POST':
        # Remove uploaded image file if present to free disk space
        if product.image:
            try:
                product.image.delete(save=False)
            except Exception:
                pass
        product.delete()
        messages.success(request, f"Product '{name}' ({unit}) has been permanently and completely deleted.")
        return redirect('owner_dashboard')

    return render(request, 'products/owner_product_confirm_delete.html', {'product': product})
