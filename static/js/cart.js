/**
 * FreshDairy - Cart & Interactive Client Logic
 * Provides smooth asynchronous cart updates, quantity steppers, and toast notifications.
 */

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// Toast Notification Manager
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    const bgColors = {
        success: 'bg-emerald-600 text-white',
        error: 'bg-rose-600 text-white',
        info: 'bg-blue-600 text-white',
        warning: 'bg-amber-500 text-white',
    };

    const icon = {
        success: 'fa-circle-check',
        error: 'fa-circle-exclamation',
        info: 'fa-circle-info',
        warning: 'fa-triangle-exclamation',
    }[type] || 'fa-bell';

    toast.className = `flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg text-sm font-medium transition-all duration-300 transform translate-y-2 opacity-0 ${bgColors[type] || bgColors.success}`;
    toast.innerHTML = `
        <i class="fa-solid ${icon} text-base"></i>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    // Animate in
    setTimeout(() => {
        toast.classList.remove('translate-y-2', 'opacity-0');
    }, 10);

    // Auto dismiss after 3.5s
    setTimeout(() => {
        toast.classList.add('opacity-0', 'translate-y-2');
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

// Update Cart Badge everywhere
function updateCartBadges(count) {
    const badges = document.querySelectorAll('.cart-badge-count');
    badges.forEach(badge => {
        badge.textContent = count;
        if (count > 0) {
            badge.classList.remove('hidden');
        } else {
            badge.classList.add('hidden');
        }
    });
}

// AJAX Add to Cart
function addToCart(productId, quantity = 1) {
    const formData = new FormData();
    formData.append('quantity', quantity);

    fetch(`/shop/cart/add/${productId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: formData
    })
    .then(response => response.json().then(data => ({ status: response.status, body: data })))
    .then(({ status, body }) => {
        if (status === 200 && body.success) {
            updateCartBadges(body.cart_count);
            showToast(body.message, 'success');
        } else {
            showToast(body.message || 'Could not add product.', 'error');
        }
    })
    .catch(err => {
        console.error(err);
        showToast('Network error adding to cart.', 'error');
    });
}

// AJAX Update Cart Item Quantity
function updateCartItem(productId, newQuantity) {
    if (newQuantity < 1) {
        removeCartItem(productId);
        return;
    }

    const formData = new FormData();
    formData.append('quantity', newQuantity);

    fetch(`/shop/cart/update/${productId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: formData
    })
    .then(response => response.json().then(data => ({ status: response.status, body: data })))
    .then(({ status, body }) => {
        if (status === 200 && body.success) {
            updateCartBadges(body.cart_count);

            // Update item row in DOM
            const qtyInput = document.getElementById(`qty-${productId}`);
            if (qtyInput) qtyInput.value = body.item_quantity;

            const itemTotalEl = document.getElementById(`item-total-${productId}`);
            if (itemTotalEl) itemTotalEl.textContent = `₹${body.item_total.toFixed(2)}`;

            // Update subtotal, delivery, grand total
            const subtotalEl = document.getElementById('cart-subtotal');
            if (subtotalEl) subtotalEl.textContent = `₹${body.cart_subtotal.toFixed(2)}`;

            const deliveryEl = document.getElementById('cart-delivery-fee');
            if (deliveryEl) {
                if (body.delivery_fee === 0) {
                    deliveryEl.innerHTML = '<span class="text-emerald-600 font-bold uppercase tracking-wide text-xs">FREE</span>';
                } else {
                    deliveryEl.textContent = `₹${body.delivery_fee.toFixed(2)}`;
                }
            }

            const grandTotalEl = document.getElementById('cart-grand-total');
            if (grandTotalEl) grandTotalEl.textContent = `₹${body.cart_grand_total.toFixed(2)}`;

            showToast('Cart updated', 'info');
        } else {
            showToast(body.message || 'Failed to update quantity', 'error');
        }
    })
    .catch(err => {
        console.error(err);
        showToast('Error updating item quantity', 'error');
    });
}

// AJAX Remove Cart Item
function removeCartItem(productId) {
    fetch(`/shop/cart/remove/${productId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateCartBadges(data.cart_count);
            showToast(data.message, 'info');

            // Remove table row
            const row = document.getElementById(`cart-row-${productId}`);
            if (row) {
                row.remove();
            }

            if (data.cart_count === 0) {
                window.location.reload();
            } else {
                const subtotalEl = document.getElementById('cart-subtotal');
                if (subtotalEl) subtotalEl.textContent = `₹${data.cart_subtotal.toFixed(2)}`;

                const grandTotalEl = document.getElementById('cart-grand-total');
                if (grandTotalEl) grandTotalEl.textContent = `₹${data.cart_grand_total.toFixed(2)}`;
            }
        }
    })
    .catch(err => {
        console.error(err);
        window.location.reload();
    });
}

// Copy to Clipboard helper
function copyToClipboard(text, message = 'Copied to clipboard!') {
    navigator.clipboard.writeText(text).then(() => {
        showToast(message, 'success');
    }).catch(() => {
        showToast('Failed to copy', 'error');
    });
}

