from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .backends import CustomAuthBackend
from .forms import UserRegisterForm, LoginForm, ProfileUpdateForm, UserUpdateForm
from .admin import UserCreationForm


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _(f'You have successfully registered to our chatApp!'))
            return redirect('users:login')
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})


def login(request):
    context = {}
    if request.method == 'POST':
        form = LoginForm(request.POST)
        email = request.POST['email']
        password = request.POST['password']
        user = CustomAuthBackend.authenticate(self=request,
                                              email=email,
                                              password=password)
        if user:
            if user.is_active:
                auth_login(request, user, backend='users.backends.CustomAuthBackend')
                return redirect(request.GET.get('next') or reverse('chat:home'))
            else:
                messages.error(request,
                               _(f'Please enter the correct email and password. Note that both fields might be case '
                                 f'sensitive.'))
                return redirect(reverse('users:login'))
    else:
        form = LoginForm()
        context = {'form': form}
    return render(request, 'users/login.html', context)


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, _(f'Successfully updated your profile!'))
            return redirect('users:profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'users/profile.html', context)


def logout(request):
    context = {'title': 'Logout'}
    return render(request, 'users/logout.html', context)

