from django.contrib.auth.models import User
from django import forms

from mysite.core.models import Profile, Sale


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username','first_name', 'last_name', 'email')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('street1','street2', 'city', 'state','zip_code')


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ('vendor', 'item', 'number', 'purchase_date',  'client')