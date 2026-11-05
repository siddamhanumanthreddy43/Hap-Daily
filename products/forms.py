from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name',
            'category',
            'unit',
            'price',
            'stock_quantity',
            'is_available',
            'image',
            'image_url',
            'description',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-500 focus:outline-none',
                'placeholder': 'e.g. Farm Fresh Whole Cow Milk'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-500 focus:outline-none'
            }),
            'unit': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-500 focus:outline-none',
                'placeholder': 'e.g. 500ml, 1 Litre, 200g, 1 Tub'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-500 focus:outline-none',
                'placeholder': 'Price in ₹',
                'step': '0.50'
            }),
            'stock_quantity': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-500 focus:outline-none',
                'placeholder': 'Available stock units'
            }),
            'is_available': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 text-emerald-600 rounded focus:ring-emerald-500'
            }),
            'image': forms.FileInput(attrs={
                'class': 'w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100'
            }),
            'image_url': forms.URLInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-500 focus:outline-none',
                'placeholder': 'https://images.unsplash.com/...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-500 focus:outline-none',
                'rows': 3,
                'placeholder': 'Fresh pasteurized farm milk, rich in calcium and vitamin D...'
            }),
        }

