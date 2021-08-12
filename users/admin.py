from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from users.models import CustomUser, Profile
from django.utils.translation import gettext_lazy as _


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required fields. Plus a repeated password."""
    password1 = forms.CharField(label=_('Password'), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_('Password Confirmation'), widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('name', 'email', 'password1', 'password2')

    def clean_password2(self):
        """Check if the two passwords match"""
        password1 = self.cleaned_data.get("Password1")
        password2 = self.cleaned_data.get("Password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("Password doesn't match!"))
        return password2

    def save(self, commit=True):
        """Save the provided password in a hashed format"""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on the user, but replaces the password field with admin's
    password hash display field """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = CustomUser
        fields = ('name', 'email', 'password', 'is_active', 'is_admin')

    def clean_password(self):
        return self.initial['password']


class CustomUserAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    # The fields to be used in displaying the user model
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('name', 'email', 'is_admin')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('name', 'email', 'password')}),
        ('Permissions', {'fields': ('is_admin',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'email', 'password1', 'password2'),
        }),
    )

    search_fields = ('name', 'email')
    ordering = ('name',)
    filter_horizontal = ()


admin.site.register(get_user_model(), CustomUserAdmin)
admin.site.register(Profile)

# Remove Group Model
admin.site.unregister(Group)
