from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import CitizenRegisterForm
from django.contrib.auth.decorators import login_required
from .forms import *
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count
from django.utils.timezone import now
from cases.models import *
from datetime import timedelta
from django.utils import timezone
from django.db.models.functions import ExtractMonth
from django.urls import reverse


def officer_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.role == 'officer' or u.role == 'admin')(view_func)

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
            return redirect('manage_users')
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

    if user.role == 'officer' or user.role == 'admin':       # Get all reports
            reports = CybercrimeReport.objects.all()

            # General Stats
            total_reports = reports.count()
            report_link = reverse("all_reports")
            recent_reports = reports.filter(date__gte=now()-timedelta(days=7)).count()
            irrelevant_cases = reports.filter(status='irrelevant').count()
            pending_cases = reports.filter(status='pending').count()
            under_investigation = reports.filter(status='under_investigation').count()
            resolved_cases = reports.filter(status='resolved').count()
            closed_cases = reports.filter(status='closed').count()
            clitical_cases = reports.filter(priority='critical').count()
            
            most_frequent = (
                               reports.values('crime_type').annotate(count=Count('crime_type')).order_by('-count').first()
                               )
            
            if most_frequent:
               crime_count = most_frequent['count']
               crime_name = reports.filter(crime_type=crime_count)              
               crime_stat_label = f"{crime_name.first()} : {crime_count}"
               
            else:
               crime_stat_label = "N/A"
            # Most affected zone (province/city)
            top_zone = reports.values('province_city').annotate(count=Count('province_city')).order_by('-count').first()
            top_zone_name = top_zone['province_city'] if top_zone else 'N/A'

            # Monthly counts
            months = ["May", "June", "July", "August", "September", "October",
                    "November", "December", "January", "February", "March", "April"]
            monthly_data = (
            reports.exclude(date__isnull=True)
            .annotate(month=ExtractMonth('date'))
            .values('month')
            .annotate(count=Count('id'))
        )

                # Create a dictionary mapping month number to count
            counts_dict = {item['month']: item['count'] for item in monthly_data}

                # Arrange counts in calendar order (May to April)
            month_order = [5,6,7,8,9,10,11,12,1,2,3,4]
            counts = [counts_dict.get(month, 0) for month in month_order]
            
    
    else:
        reports = CybercrimeReport.objects.filter(user=user)

            # General Stats
        total_reports = reports.count()
        report_link = reverse("my_reports")
        recent_reports = reports.filter(date__gte=now()-timedelta(days=7)).count()
        irrelevant_cases = reports.filter(status='irrelevant').count()
        pending_cases = reports.filter(status='pending').count()
        under_investigation = reports.filter(status='under_investigation').count()
        resolved_cases = reports.filter(status='resolved').count()        
        closed_cases = reports.filter(status='closed').count()
        clitical_cases = reports.filter(priority='critical').count()
        
        most_frequent = (
                               reports.values('crime_type').annotate(count=Count('crime_type')).order_by('-count').first()
                               )
            
        if most_frequent:
               crime_count = most_frequent['count']
               crime_name = reports.filter(crime_type=crime_count)              
               crime_stat_label = f"{crime_name.first()} : {crime_count}"
               
        else:
               crime_stat_label = "N/A"

            # Most affected zone (province/city)
        top_zone = reports.values('province_city').annotate(count=Count('province_city')).order_by('-count').first()
        top_zone_name = top_zone['province_city'] if top_zone else 'N/A'

            # Monthly counts
        months = ["May", "June", "July", "August", "September", "October",
                    "November", "December", "January", "February", "March", "April"]
        monthly_data = (
            reports.exclude(date__isnull=True)
            .annotate(month=ExtractMonth('date'))
            .values('month')
            .annotate(count=Count('id'))
        )

                # Create a dictionary mapping month number to count
        counts_dict = {item['month']: item['count'] for item in monthly_data}

                # Arrange counts in calendar order (May to April)
        month_order = [5,6,7,8,9,10,11,12,1,2,3,4]
        counts = [counts_dict.get(month, 0) for month in month_order]

        
# Month labels in the same order

    
    # counts = [reports.filter(date=((i % 12) + 1)).count() for i in range(12)]

    # Define cards
    stats = [
        {"title": "Total Reported Cases", "value": total_reports, "link":  report_link },
        {"title": "Pending Cases", "value": pending_cases, "link": "/cases/pending/"},
        {"title": "Cases Under Investigation", "value": under_investigation, "link": "/cases/investigating/"},
        {"title": "Closed", "value": closed_cases, "link": "/cases/closed_cases/"},        
        {"title": "Recent Reported Cases", "value": recent_reports, "link": "/reports/recent/"},
        {"title": "Irrelevant Cases", "value": irrelevant_cases, "link": "/cases/irrelevant/"},      
        {"title": "Resolved Cases", "value": resolved_cases, "link": "/cases/resolved/"},
        {"title": "Clitical Cases", "value": clitical_cases, "link": "/cases/clitical/"},
        {"title": "Most Reported Crime","value":  crime_stat_label , "link": "/reports/most/",},
        {"title": "High Rated Zone", "value": top_zone_name, "link": "/zones/top/"},
    ]

    context = {
        'stats': stats,
        'chart_labels': months,
        'chart_data': counts,
    }

    # Role-based rendering
    if user.role == 'citizen':
        return render(request, 'accounts/dashboards/citizen_dashboard.html', context)
    if user.role == 'officer':
        return render(request, 'accounts/dashboards/officer_dashboard.html', context)
    elif user.role == 'admin':
        return render(request, 'accounts/dashboards/admin_dashboard.html', context)
    else:
        return redirect('login')


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


