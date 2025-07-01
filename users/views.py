from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, PasswordChangeForm, SetPasswordForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms
from .forms import CustomUserCreationForm, UserEditForm, ProfileEditForm
from .models import Profile  # Make sure you have a Profile model
from django.utils import timezone
from tickets.models import Ticket
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode

# Profile Edit Form
class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['photo']

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_superuser:
                return redirect('admin_dashboard')
            else:
                return redirect('user_dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

def user_register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            # Save the profile photo
            photo = form.cleaned_data.get('photo')
            if photo:
                profile, created = Profile.objects.get_or_create(user=user)
                profile.photo = photo
                profile.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    tickets = Ticket.objects.filter(user=request.user).select_related('event').order_by('-purchase_date')
    return render(request, 'users/profile.html', {
        'tickets': tickets,
        'now': timezone.now(),
    })

@login_required
def profile_edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=request.user)
        profile_form = ProfileEditForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    return render(request, 'users/profile_edit.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })

def user_logout(request):
    logout(request)
    return redirect('login')

def password_reset(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(
                request=request,
                use_https=request.is_secure(),
                email_template_name='registration/password_reset_email.html'
            )
            return render(request, 'users/password_reset_done.html')
    else:
        form = PasswordResetForm()
    return render(request, 'users/password_reset.html', {'form': form})

@login_required
def password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'users/password_change.html', {'form': form})

def password_reset_done(request):
    return render(request, 'users/password_reset_done.html')

def password_reset_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                return redirect('password_reset_complete')
        else:
            form = SetPasswordForm(user)
        return render(request, 'users/password_reset_confirm.html', {'form': form})
    else:
        return render(request, 'users/password_reset_invalid.html')

def password_reset_complete(request):
    return render(request, 'users/password_reset_complete.html')

# Create your views here.
