from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import CitizenRegisterForm
from django.contrib.auth.decorators import login_required
from .forms import *
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test

def citizen_register(request):
    if request.method == 'POST':
        form = CitizenRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CitizenRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def dashboard(request):
    if request.user.role == 'admin':
        return render(request, 'accounts/dashboards/admin_dashboard.html')
    elif request.user.role == 'officer':
        return render(request, 'accounts/dashboards/officer_dashboard.html')
    elif request.user.role == 'citizen':
        return render(request, 'accounts/dashboards/citizen_dashboard.html')

@login_required
def profile_view(request):
    role = request.user.role
    if role == 'admin':
        return redirect('admin_profile')
    elif role == 'officer':
        return redirect('officer_profile')
    else:
        return redirect('citizen_profile')


@login_required
def admin_profile(request):
    return render(request, 'accounts/profiles/admin_profile.html', {'user': request.user})

@login_required
def officer_profile(request):
    return render(request, 'accounts/profiles/officer_profile.html', {'user': request.user})

@login_required
def citizen_profile(request):
    return render(request, 'accounts/profiles/citizen_profile.html', {'user': request.user})

@login_required
def edit_profile(request):
    user = request.user
    if user.role == 'admin':
        form_class = AdminProfileForm
        template = 'accounts/profiles/edit_admin.html'
    elif user.role == 'officer':
        form_class = OfficerProfileForm
        template = 'accounts/profiles/edit_officer.html'
    else:
        form_class = CitizenProfileForm
        template = 'accounts/profiles/edit_citizen.html'

    if request.method == 'POST':
        form = form_class(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = form_class(instance=user)

    return render(request, template, {'form': form})

@login_required
@user_passes_test(lambda u: u.role == 'admin')
def add_user(request):
    if request.method == 'POST':
        form = OfficerCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = OfficerCreationForm()
    return render(request, 'accounts/admin/add_user.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')  # already logged in
    if request.method == 'POST':
        login_input = request.POST['username']  # this can be username or email
        password = request.POST['password']
        # First try username authentication
        user = authenticate(request, username=login_input, password=password)

        if user is None:
            # If failed, try to find user by email and authenticate by username
            try:
                user_obj = User.objects.get(email=login_input)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

        if user is not None:
            if not user.is_active:
                messages.error(request, 'Your account is disabled. Please contact the administrator.')
                return render(request, 'accounts/login.html')
            
            login(request, user)
            # Redirect based on role
            if user.role == 'admin':
                return redirect('dashboard')  # admin dashboard
            elif user.role == 'officer':
                return redirect('dashboard')  # officer dashboard
            else:
                return redirect('dashboard')  # citizen dashboard
        else:
            messages.error(request, 'Invalid username/email or password.')

    return render(request, 'accounts/login.html')
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('login')

@login_required
def role_based_dashboard(request):
    user = request.user
    stats = [
    {"title": "Total Reported Cases", "value": 0, "link": "/reports/"},
    {"title": "Most Frequent Case", "value": "Online Harrasment", "link": "/cases/frequent/"},
    {"title": "High Rated Zone", "value": "Kigali", "link": "/zones/top/"},
    {"title": "Recent Reported Cases", "value": 0, "link": "/reports/recent/"},
    {"title": "Irrelevant Cases", "value": 0, "link": "/cases/irrelevant/"},
    {"title": "Pending Cases", "value": 0, "link": "/cases/pending/"},
    {"title": "Cases Under Investigation", "value": 0, "link": "/cases/investigating/"},
    {"title": "Resolved Cases", "value": 0, "link": "/cases/resolved/"},
    ]
    months = ["May", "June", "July", "August", "September", "October",
              "November", "December", "January", "February", "March", "April"]
    counts = [0] * 12

    context = {
        'stats': stats,
        'chart_labels': months,
        'chart_data': counts,
    }

    if user.role == 'citizen':
        return render(request, 'accounts/dashboards/citizen_dashboard.html', context)
    elif user.role == 'officer':
        return render(request, 'accounts/dashboards/officer_dashboard.html', context)
    elif user.role == 'admin':
        return render(request, 'accounts/dashboards/admin_dashboard.html', context)
    else:
        return redirect('login')  # fallback

def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

@login_required
@user_passes_test(is_admin)
def manage_users(request):
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'accounts/admin/manage_users.html', {'users': users})


@login_required
@user_passes_test(is_admin)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, 'User deleted successfully.')
    return redirect('manage_users')

@login_required
@user_passes_test(is_admin)
def toggle_user_status(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()
    status = 'enabled' if user.is_active else 'disabled'
    messages.success(request, f'User {status} successfully.')
    return redirect('manage_users')