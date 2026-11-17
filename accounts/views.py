from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .decorators import role_required
from .forms import EmailLoginForm, ProfileForm, RegisterForm
from .models import User


def home(request):
    if request.user.is_authenticated:
        return redirect(request.user.get_dashboard_url())
    return redirect('accounts:login')


def register_view(request):
    if request.user.is_authenticated:
        return redirect(request.user.get_dashboard_url())

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully. You can now log in.')
            return redirect('accounts:login')
        messages.error(request, 'Please fix the errors below.')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect(request.user.get_dashboard_url())

    next_url = request.POST.get('next') or request.GET.get('next', '')

    if request.method == 'POST':
        form = EmailLoginForm(request, request.POST)
        if form.is_valid():
            login(request, form.user)
            messages.success(request, f'Welcome back, {form.user.first_name or form.user.username}!')
            if next_url and url_has_allowed_host_and_scheme(
                next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
            ):
                return redirect(next_url)
            return redirect(form.user.get_dashboard_url())
    else:
        form = EmailLoginForm(request)
    return render(request, 'accounts/login.html', {'form': form, 'next': next_url})


@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('accounts:login')


# ---- Role-based dashboards ----

@role_required(User.Role.ADMIN)
def admin_dashboard(request):
    context = {
        'total_users': User.objects.count(),
        'admin_count': User.objects.filter(role=User.Role.ADMIN).count(),
        'editor_count': User.objects.filter(role=User.Role.EDITOR).count(),
        'citizen_count': User.objects.filter(role=User.Role.CITIZEN).count(),
    }
    return render(request, 'dashboards/admin.html', context)


@role_required(User.Role.EDITOR)
def editor_dashboard(request):
    return render(request, 'dashboards/editor.html')


@role_required(User.Role.CITIZEN)
def citizen_dashboard(request):
    return render(request, 'dashboards/citizen.html')


# ---- Profile (always the logged-in user's own; no ID in the URL) ----

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')


@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')
        messages.error(request, 'Please fix the errors below.')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'accounts/profile_edit.html', {'form': form})