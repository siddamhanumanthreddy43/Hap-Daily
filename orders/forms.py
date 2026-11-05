from django import forms
from .models import Order, UpiSetting


class CheckoutForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=True, label="Full Name")
    
    class Meta:
        model = Order
        fields = [
            'delivery_address',
            'delivery_phone',
            'delivery_slot',
            'payment_method',
            'notes'
        ]
        widgets = {
            'delivery_address': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-500 focus:outline-none',
                'rows': 3,
                'placeholder': 'Flat/House No., Wing, Apartment Name, Street, Landmark'
            }),
            'delivery_phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-500 focus:outline-none',
                'placeholder': '+91 98765 43210'
            }),
            'delivery_slot': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-500 focus:outline-none'
            }),
            'payment_method': forms.RadioSelect(attrs={
                'class': 'text-emerald-600 focus:ring-emerald-500'
            }),
            'notes': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-500 focus:outline-none',
                'placeholder': 'e.g., Leave at door / Call on arrival / Ring bell'
            }),
        }


class UpiReferenceForm(forms.Form):
    upi_ref_number = forms.CharField(
        max_length=50,
        required=True,
        label="UPI Reference / UTR Number",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border-2 border-emerald-500 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-600 text-lg font-mono tracking-wider',
            'placeholder': 'e.g. 430219842109 (12-digit UTR)'
        })
    )


class UpiSettingForm(forms.ModelForm):
    class Meta:
        model = UpiSetting
        fields = [
            'merchant_name',
            'upi_id',
            'qr_mode',
            'custom_qr_image',
            'instructions',
            'delivery_fee',
            'free_delivery_threshold',
            'is_active',
        ]
        widgets = {
            'merchant_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 font-medium text-slate-800 text-sm shadow-2xs',
                'placeholder': 'e.g. Arokya Milk Store'
            }),
            'upi_id': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 font-mono font-bold text-slate-900 text-sm shadow-2xs',
                'placeholder': 'e.g. arokyamilk@upi or 9876543210@paytm'
            }),
            'qr_mode': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 font-medium text-slate-800 text-sm bg-white shadow-2xs'
            }),
            'custom_qr_image': forms.FileInput(attrs={
                'class': 'w-full text-xs text-slate-500 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-bold file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100 cursor-pointer border border-slate-200 rounded-xl p-2'
            }),
            'instructions': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 font-normal text-slate-800 text-sm shadow-2xs',
                'rows': 3,
                'placeholder': 'Instructions for the customer on the checkout payment screen...'
            }),
            'delivery_fee': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 font-mono font-bold text-slate-900 text-sm shadow-2xs',
                'step': '0.50',
                'min': '0',
                'placeholder': '5.00'
            }),
            'free_delivery_threshold': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 font-mono font-bold text-slate-900 text-sm shadow-2xs',
                'step': '1.00',
                'min': '0',
                'placeholder': '199.00'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 text-emerald-600 rounded-lg focus:ring-emerald-500 border-slate-300'
            }),
        }

    def clean_upi_id(self):
        upi_id = self.cleaned_data.get('upi_id', '').strip()
        if not upi_id:
            raise forms.ValidationError("UPI ID is required.")
        if '@' not in upi_id:
            raise forms.ValidationError("Please enter a valid UPI VPA address (e.g. yourname@upi, 9876543210@paytm).")
        return upi_id


