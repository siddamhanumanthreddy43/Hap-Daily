import io
import base64
import urllib.parse
import qrcode
from django.conf import settings
from django.core.files.base import ContentFile


def generate_upi_payload(order):
    """
    Constructs the official UPI Deep Link specification URL.
    Format: upi://pay?pa=...&pn=...&am=...&tn=...&cu=INR
    """
    try:
        from .models import UpiSetting
        upi_setting = UpiSetting.get_settings()
        vpa = upi_setting.upi_id or getattr(settings, 'UPI_MERCHANT_VPA', 'arokyamilk@upi')
        merchant_name = upi_setting.merchant_name or getattr(settings, 'UPI_MERCHANT_NAME', 'Arokya Milk Store')
    except Exception:
        vpa = getattr(settings, 'UPI_MERCHANT_VPA', 'arokyamilk@upi')
        merchant_name = getattr(settings, 'UPI_MERCHANT_NAME', 'Arokya Milk Store')

    amount = f"{order.total_amount:.2f}"
    transaction_note = f"Order_{order.order_number}"

    params = {
        'pa': vpa,
        'pn': merchant_name,
        'am': amount,
        'tn': transaction_note,
        'cu': 'INR',
    }
    encoded_query = urllib.parse.urlencode(params)
    return f"upi://pay?{encoded_query}"


def generate_preview_qr_base64(upi_id=None, merchant_name=None, amount="100.00"):
    """
    Generates a live in-memory preview QR code for the owner settings page.
    """
    try:
        from .models import UpiSetting
        upi_setting = UpiSetting.get_settings()
        vpa = upi_id or upi_setting.upi_id or 'arokyamilk@upi'
        name = merchant_name or upi_setting.merchant_name or 'Arokya Milk Store'
    except Exception:
        vpa = upi_id or 'arokyamilk@upi'
        name = merchant_name or 'Arokya Milk Store'

    params = {
        'pa': vpa,
        'pn': name,
        'am': str(amount),
        'tn': 'Arokya_Milk_Store_Test',
        'cu': 'INR',
    }
    encoded_query = urllib.parse.urlencode(params)
    payload = f"upi://pay?{encoded_query}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(payload)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#065F46", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    encoded_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{encoded_b64}", payload



def create_order_upi_qr(order):
    """
    Generates a QR code image from the UPI payload and saves it to the order instance.
    Returns the base64-encoded data URI string for instantaneous inline rendering.
    """
    upi_payload = generate_upi_payload(order)
    order.upi_intent_url = upi_payload

    # Create QR Code instance with high error correction for mobile scanners
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(upi_payload)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#065F46", back_color="white") # Forest Green theme

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    image_bytes = buffer.getvalue()

    # Save to model ImageField
    file_name = f"upi_qr_{order.order_number}.png"
    order.upi_qr_code.save(file_name, ContentFile(image_bytes), save=False)
    order.save(update_fields=['upi_intent_url', 'upi_qr_code'])

    # Return base64 string for immediate HTML usage
    encoded_b64 = base64.b64encode(image_bytes).decode('utf-8')
    return f"data:image/png;base64,{encoded_b64}"

