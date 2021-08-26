from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, CustomUser
from django.utils.translation import gettext_lazy as _
from bootstrap_modal_forms.forms import BSModalModelForm, BSModalForm
from bootstrap_modal_forms.mixins import PopRequestMixin, CreateUpdateAjaxMixin


class UserRegisterForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)

    email = forms.EmailField()
    # phone = forms.CharField(label=_('Phone'), max_length=14)
    # name = forms.CharField(label=_('Username'), max_length=250)
    password1 = forms.CharField(label=_('Password'), widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'type': 'password', 'required': 'true', 'data-toggle': 'password'}))
    password2 = forms.CharField(label=_('Confirm Password'), widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'type': 'password', 'required': 'true', 'data-toggle': 'password'}))

    class Meta:
        model = get_user_model()
        fields = ('name', 'email', 'password1', 'password2',)


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email', widget=forms.EmailInput())
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = get_user_model()
        fields = ['email', 'password']

        widgets = {
            'password': forms.PasswordInput(
                attrs={'placeholder': '********', 'autocomplete': 'off', 'data-toggle': 'password'}),
        }


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('name', 'email',)


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('image',)
