from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms

from mysite.core.models import Profile, Order


class CustomAuthForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        self.error_messages['invalid_login'] = 'Custom error'
        super().__init__(*args, **kwargs)


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2',)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('phone_number', 'street1', 'street2', 'city', 'state', 'zip_code')


class SaleForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('vendor', 'item', 'number', 'purchase_date', 'client')
