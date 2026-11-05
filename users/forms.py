from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser


class CustomerRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label="Full Name")
    email = forms.EmailField(required=True, label="Email Address")
    phone = forms.CharField(max_length=15, required=True, label="Mobile Number (for delivery SMS/WhatsApp)")
    delivery_address = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'House/Flat No, Apartment/Street, Landmark'}),
        required=True,
        label="Delivery Address"
    )
    city = forms.CharField(max_length=100, initial="Bengaluru", required=True)
    pincode = forms.CharField(max_length=10, required=True, label="Pincode")

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'email', 'phone', 'delivery_address', 'city', 'pincode')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'CUSTOMER'
        user.first_name = self.cleaned_data['first_name']
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']
        user.delivery_address = self.cleaned_data['delivery_address']
        user.city = self.cleaned_data['city']
        user.pincode = self.cleaned_data['pincode']
        if commit:
            user.save()
        return user


class OwnerRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label="Store Owner Full Name")
    email = forms.EmailField(required=True, label="Store Email Address")
    phone = forms.CharField(max_length=15, required=True, label="Official Contact / WhatsApp Phone")
    delivery_address = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Store / Dairy Outlet Address'}),
        required=True,
        label="Store / Dairy Outlet Address"
    )
    city = forms.CharField(max_length=100, initial="Bengaluru", required=True, label="City")
    pincode = forms.CharField(max_length=10, required=True, label="Pincode")

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'email', 'phone', 'delivery_address', 'city', 'pincode')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'OWNER'
        user.is_staff = True
        user.first_name = self.cleaned_data['first_name']
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']
        user.delivery_address = self.cleaned_data['delivery_address']
        user.city = self.cleaned_data['city']
        user.pincode = self.cleaned_data['pincode']
        if commit:
            user.save()
        return user


class CustomerLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username, Phone, or Email",
        widget=forms.TextInput(attrs={'placeholder': 'Enter username, phone, or email', 'autofocus': True})
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••'})
    )


class CustomerProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=True, label="Full Name")

    class Meta:
        model = CustomUser
        fields = ('first_name', 'email', 'phone', 'delivery_address', 'city', 'pincode')
        widgets = {
            'delivery_address': forms.Textarea(attrs={'rows': 3}),
        }

