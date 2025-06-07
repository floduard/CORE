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
from .models import *
from datetime import timedelta
from django.utils import timezone
from django.db.models.functions import ExtractMonth
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt 
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.utils.crypto import get_random_string
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from cases.views import *
from django.db.models import Count
from collections import OrderedDict
from datetime import datetime
import csv
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from io import BytesIO
from django.views.decorators.http import require_GET
from django.utils import timezone
from django.core.mail import send_mail
import requests
from django.conf import settings
import csv
from io import BytesIO
from reportlab.pdfgen import canvas


def officer_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.role == 'officer' or u.role == 'admin')(view_func)

def citizen_register(request):
    if request.method == 'POST':
        form = CitizenRegisterForm(request.POST)
        # Check if terms were agreed
        if not request.POST.get('agree_terms'):
            form.add_error(None, "You must agree to the Terms and Conditions to register.")
            return render(request, 'accounts/register.html', {'form': form})

        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Mark user inactive
            user.save()

            # Send email verification
            current_site = get_current_site(request)
            mail_subject = 'Activate your account'
            message = render_to_string('accounts/admin/activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()

            return render(request, 'accounts/admin/email_verification_sent.html')
    else:
        form = CitizenRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def dashboard(request):
    if request.user.role == 'admin':
        activity_logs = ActivityLog.objects.all().order_by('-timestamp')[:10]
        return render(request, 'accounts/dashboards/admin_dashboard.html', {
            'activity_logs': activity_logs
        })

    elif request.user.role == 'officer':
        activity_logs = ActivityLog.objects.filter(user=request.user)[:10]
        return render(request, 'accounts/dashboards/officer_dashboard.html', {
            'activity_logs': activity_logs
        })

    elif request.user.role == 'citizen':
        activity_logs = ActivityLog.objects.filter(user=request.user)[:10]
        return render(request, 'accounts/dashboards/citizen_dashboard.html', {
            'activity_logs':activity_logs
        })

def activate_account(request, uid, token):
    try:
        uid = urlsafe_base64_decode(uid).decode()
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError, OverflowError):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Account activated. Please log in and change your password.")
        return redirect('login')
    else:
        return HttpResponse("Activation link is invalid!", status=400)


@login_required
@user_passes_test(lambda u: u.role == 'admin')
def add_user(request):
    if request.method == 'POST':
        form = OfficerCreationForm(request.POST)
        if form.is_valid():
            User = form.save(commit=False)
            temp_password = get_random_string(length=8)
            User.password = make_password(temp_password)
            User.is_active = False  # Require email verification
            User.must_change_password = True  # Custom field for password change
            User.save()

            # Email verification link setup
            current_site = get_current_site(request)
            subject = 'Activate Your Cybercrime Reporting System Account'
            DEFAULT_FROM_EMAIL='noreply@cras.com'
            message = render_to_string('accounts/admin/activation_email.html', {
                'User': User,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(User.pk)),
                'token': default_token_generator.make_token(User),
                'temp_password': temp_password,
            })

            send_mail(
                subject,
                message,
                DEFAULT_FROM_EMAIL,
                [User.email],
                fail_silently=False,
            )
            ActivityLog.objects.create(
            user=request.user,
            action=f"User {{request.user}} Added to the system",
        )

            return redirect('manage_users')
    else:
        form = OfficerCreationForm()
    return render(request, 'accounts/admin/add_user.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')  # already logged in

    if request.method == 'POST':
        # 1. Verify reCAPTCHA first
        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': settings.RECAPTCHA_SECRET_KEY,  # add this to your settings
            'response': recaptcha_response
        }
        recaptcha_verify = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = recaptcha_verify.json()
        if not result.get('success'):
            messages.error(request, 'Invalid reCAPTCHA. Please try again.')
            return render(request, 'accounts/login.html')
        
        # 2. Continue with your login logic
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
            ActivityLog.objects.create(
                user=request.user,
                action=f"User {user} Logged in",
            )
            # Redirect based on role
            if user.role == 'admin':
                return redirect('dashboard')  # admin dashboard
            elif user.role == 'officer':
                return redirect('dashboard')  # officer dashboard
            else:
                return redirect('dashboard')  # citizen dashboard
        else:
            messages.error(request, 'Invalid username/email or password.')

    return render(request, 'accounts/login.html', {'RECAPTCHA_SITE_KEY': settings.RECAPTCHA_SITE_KEY})

@login_required
def logout_view(request):
    if request.user.is_authenticated:
        ActivityLog.objects.create(
                user=request.user,
                action=f"User {request.user}  Logged out",
            )
    logout(request)    
    messages.success(request, 'Logged out successfully.')
    return redirect('login')





@login_required
def role_based_dashboard(request):
    user = request.user

    if user.role in ['officer', 'admin']:
        reports = CybercrimeReport.objects.all()
    else:
        reports = CybercrimeReport.objects.filter(user=user)

       

    total_reports = reports.count()
    report_link = reverse("all_reports") if user.role in ['admin', 'officer'] else reverse("my_reports")
    recent_reports = reports.filter(submitted_at__gte=now() - timedelta(days=7)).count()
    irrelevant_cases = reports.filter(status='irrelevant').count()
    pending_cases = reports.filter(status='pending').count()
    under_investigation = reports.filter(status='under_investigation').count()
    resolved_cases = reports.filter(status='resolved').count()
    closed_cases = reports.filter(status='closed').count()
    critical_cases_count = reports.filter(priority='critical').count()
    most_common = (
    reports.values('crime_type')
    .annotate(count=Count('crime_type'))
    .order_by('-count')
    .first()
)

    if most_common:
            most_reported_crime = reports.filter(crime_type=most_common['crime_type'])
            crime_stat_label = f"{most_reported_crime.first().crime_type.name} : {most_common['count']}"
    else:
            most_reported_crime = None
            crime_stat_label = "N/A"
    # Most frequent crime type
      

    # Most affected zone (province/city)
    top_zone = reports.values('province_city').annotate(count=Count('province_city')).order_by('-count').first()
    top_zone_name = top_zone['province_city'] if top_zone else 'N/A'

    # Monthly trend stats
    months = ["May", "June", "July", "August", "September", "October",
              "November", "December", "January", "February", "March", "April"]
    monthly_data = (
        reports.exclude(date__isnull=True)
        .annotate(month=ExtractMonth('date'))
        .values('month')
        .annotate(count=Count('id'))
    )
    counts_dict = {item['month']: item['count'] for item in monthly_data}
    month_order = [5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4]
    counts = [counts_dict.get(month, 0) for month in month_order]

    # Status and priority chart data
    status_labels = [label for _, label in CybercrimeReport.STATUS_CHOICES]
    status_counts = [reports.filter(status=code).count() for code, _ in CybercrimeReport.STATUS_CHOICES]

    priority_labels = [label for _, label in CybercrimeReport.PRIORITY_CHOICES]
    priority_counts = [reports.filter(priority=code).count() for code, _ in CybercrimeReport.PRIORITY_CHOICES]


    stats = [
        {"title": "Total Reported Cases", "value": total_reports, "link": report_link},
        {"title": "Pending Cases", "value": pending_cases, "link": reverse("pending_cases")},
        {"title": "Cases Under Investigation", "value": under_investigation, "link": reverse("investigating_cases")},       
        {"title": "Cases Resolved", "value": resolved_cases, "link": reverse("resolved_cases")},
        {"title": "Closed Cases", "value": closed_cases, "link": reverse("closed_cases")},
        {"title": "Recent Reported Cases", "value": recent_reports, "link": reverse("recent_reports")},
        {"title": "Irrelevant Cases", "value": irrelevant_cases, "link": reverse("irrelevant_cases")},
        {"title": "Critical Cases", "value": critical_cases_count, "link": reverse("critical_cases")},
        {"title": "Most Reported Crime", "value": crime_stat_label, "link":reverse("most_reported_crime")},
        {"title": "High Rated Zone", "value": top_zone_name, "link": reverse("top_zones")},
    ]
    recent_activities = [] 
    if request.user.role == 'admin':
            recent_activities = ActivityLog.objects.all().order_by('-timestamp')[:5]           

    elif request.user.role == 'officer':
            recent_activities = ActivityLog.objects.filter(user=request.user)[:5]           

    elif request.user.role == 'citizen':
            recent_activities = ActivityLog.objects.filter(user=request.user)[:5]

    context = {
        'stats': stats,
        'chart_labels': months,
        'chart_data': counts,
        'status_labels': status_labels,
        'status_data': status_counts,
        'priority_labels': priority_labels,
        'priority_data': priority_counts,
        'recent_activities':recent_activities,
    }

    if user.role == 'admin':
        return render(request, 'accounts/dashboards/admin_dashboard.html', context)
    elif user.role == 'officer':
        return render(request, 'accounts/dashboards/officer_dashboard.html', context)
    else:
        return render(request, 'accounts/dashboards/citizen_dashboard.html', context)


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
    recipient_email = user.email
    user.delete()
    ActivityLog.objects.create(
            user=request.user,
            action=f"User {user} Deleted",
        )
    subject = 'Account Deleted'
    DEFAULT_FROM_EMAIL='noreply@cras.com'
    message =f"User {user} has been deleted from cybercrime reporting system."

    send_mail(
                subject,
                message,
                DEFAULT_FROM_EMAIL,
                [recipient_email],
                fail_silently=False,
            )
    messages.success(request, 'User deleted successfully.')
    return redirect('manage_users')

@login_required
@user_passes_test(is_admin)
def toggle_user_status(request, user_id):
    user = get_object_or_404(User, id=user_id)
    recipient_email = user.email 
    user.is_active = not user.is_active
    user.save()
    status = 'enabled' if user.is_active else 'disabled'
    subject = f"{user} Account   {status}"
    DEFAULT_FROM_EMAIL='noreply@cras.com'
    message =f"User {user} has been {status} from cybercrime reporting system."

    send_mail(
                subject,
                message,
                DEFAULT_FROM_EMAIL,
                [recipient_email],
                fail_silently=False,
            )
    ActivityLog.objects.create(
            user=request.user,
            action=f"User {user} is now {status}",
        )
    messages.success(request, f'User {status} successfully.')
    return redirect('manage_users')


@login_required
def all_notifications(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    return render(request, 'notifications/all_notifications.html', {
        'notifications': notifications
    })

@require_GET
@login_required
def fetch_notifications(request):
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:10]
    data = [{
        'id': n.id,
        'message': n.message,
        'timestamp': n.created_at.strftime("%Y-%m-%d %H:%M"),
        'url': n.url if hasattr(n, 'url') else '#'
    } for n in notifications]
    
    return JsonResponse({'notifications': data, 'count': notifications.count()})

@require_POST
@login_required
def mark_notifications_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'success'})


@require_GET
@login_required
def unread_notifications(request):
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')
    return JsonResponse({
        "count": notifications.count(),
        "notifications": [
            {
                "id": n.id,
                "message": n.message,
                "url": n.url if hasattr(n, 'url') else '#',
                "created_at": n.created_at.strftime('%Y-%m-%d %H:%M'),
            }
            for n in notifications
        ]
    })


@require_POST
@login_required
def mark_as_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.is_read = True
    notif.save()
    return JsonResponse({"success": True})




@login_required
def generate_report(request):
    user = request.user
    format_type = request.GET.get('format', 'html')

    # Parse date range from GET
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date() if start_date_str else now().date() - timedelta(days=30)
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date() if end_date_str else now().date()
    except ValueError:
        start_date = now().date() - timedelta(days=30)
        end_date = now().date()

    if user.role == 'admin' or user.role == 'officer':
        total_users = User.objects.count()
        total_citizens = User.objects.filter(role='citizen').count()
        total_officers = User.objects.filter(role='officer').count()
        total_admins = User.objects.filter(role='admin').count()
        total_reports = CybercrimeReport.objects.count()
        filtered_reports = CybercrimeReport.objects.filter(date__range=[start_date, end_date])
        recent_reports = filtered_reports.count()
        assigned_reports = filtered_reports.filter(assignee__isnull=False).count()
        closed_reports = CybercrimeReport.objects.filter(status='closed').count()
        under_investigation = CybercrimeReport.objects.filter(status='under_investigation').count()
        unassigned_reports = CybercrimeReport.objects.filter(assignee__isnull=True).count()
        total_suspects = Suspect.objects.count()
        total_evidence = AdditionalEvidence.objects.count()

        period = request.GET.get('period', 'all')
        today = now().date()
        end_date = today
        start_date = None

        if period == 'today':
            start_date = today - timedelta(days=1)
        elif period == 'last_7_days':
            start_date = today - timedelta(days=7)
        elif period == 'last_30_days':
            start_date = today - timedelta(days=30)
        elif period == 'this_month':
            start_date = today.replace(day=1)
        elif period == 'this_year':
            start_date = today.replace(month=1, day=1)

        reports = CybercrimeReport.objects.all()
        if start_date:
            reports = reports.filter(date__range=(start_date, end_date))
        reports_in_period = reports  


        # Trends
        recent_period_start = today - timedelta(days=30)
        older_period_start = today - timedelta(days=60)
        last_30 = CybercrimeReport.objects.filter(date__range=[recent_period_start, today]).count()
        prev_30 = CybercrimeReport.objects.filter(date__range=[older_period_start, recent_period_start]).count()
        report_trend = f"{abs(((last_30 - prev_30) / prev_30) * 100):.2f}% {'increase' if last_30 > prev_30 else 'decrease'}" if prev_30 else "N/A"

        summary_message = f"""📊 Report Summary:
        - Total Users: {total_users}
        - Citizens: {total_citizens}
        - Officers: {total_officers}
        - Admins: {total_admins}
        - Total Reports: {total_reports}
        - Reports from {start_date} to {end_date}: {recent_reports}
        - Assigned Cases: {assigned_reports}"""

          # CSV Export
        if format_type == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="admin_report.csv"'
            writer = csv.writer(response)
            writer.writerow(['Metric', 'Value'])
            writer.writerow(['Total Users', total_users])
            writer.writerow(['Citizens', total_citizens])
            writer.writerow(['Officers', total_officers])
            writer.writerow(['Admins', total_admins])
            writer.writerow(['Total Reports', total_reports])
            writer.writerow([f'Reports Since {start_date}', reports_in_period])
            writer.writerow(['Open Reports', open_reports])
            writer.writerow(['Closed Reports', closed_reports])
            writer.writerow(['Under Investigation', under_investigation])
            writer.writerow(['Assigned Reports', assigned_reports])
            writer.writerow(['Unassigned Reports', unassigned_reports])
            writer.writerow(['Total Suspects', total_suspects])
            writer.writerow(['Total Evidence Items', total_evidence])
            return response

        # PDF Export
        if format_type == 'pdf':
            buffer = BytesIO()
            p = canvas.Canvas(buffer)
            p.drawString(100, 800, "Admin Report Summary")
            y = 780
            lines = [
                f"Total Users: {total_users}",
                f"Citizens: {total_citizens}",
                f"Officers: {total_officers}",
                f"Admins: {total_admins}",
                f"Total Reports: {total_reports}",
                f"Closed Reports: {closed_reports}",
                f"Under Investigation: {under_investigation}",
                f"Assigned Reports: {assigned_reports}",
                f"Unassigned Reports: {unassigned_reports}",
                f"Total Suspects: {total_suspects}",
                f"Total Evidence Items: {total_evidence}",
            ]
            for line in lines:
                p.drawString(100, y, line)
                y -= 20
            p.showPage()
            p.save()
            buffer.seek(0)
            return HttpResponse(buffer, content_type='application/pdf')

        return render(request, 'accounts/report_summary.html', {
            'title': f"Report Summary from {start_date} to {end_date}",
            'total_users': total_users,
            'total_citizens': total_citizens,
            'total_officers': total_officers,
            'total_admins': total_admins,
            'total_reports': total_reports,
            'recent_reports': recent_reports,
            'assigned_reports': assigned_reports,
            'report_trend': report_trend,
            'summary_message': summary_message.strip(),
            'start_date': start_date,
            'end_date': end_date,
            'summary_message': summary_message.strip(),
            'under_investigation': under_investigation,
            'unassigned_reports': unassigned_reports,
            'total_suspects': total_suspects,
            'total_evidence': total_evidence,
            'filter_period': period,
            'reports_in_period': reports_in_period,
        })

    return render(request, '403.html')


@login_required
def profile_view(request):
    if request.user.role == "citizen":
        skip_fields = ["badge_id", "department", "office_name", "managed_since"]
    elif request.user.role == "officer":
        skip_fields = ["id_number", "office_name", "managed_since"]
    elif request.user.role == "admin":
        skip_fields = ["id_number", "badge_id", "department"]
    else:
        skip_fields = []

    # Create a context dictionary
    context = {
        'skip_fields': skip_fields,
        # Add any other context variables you need here
    }

    return render(request, 'accounts/profiles/profile_view.html', context)


@login_required
def edit_profile(request):
    user = request.user
    # Calculate skip_fields based on role
    if user.role == "citizen":
        skip_fields = ["badge_id", "department", "office_name", "managed_since"]
    elif user.role == "officer":
        skip_fields = ["id_number", "office_name", "managed_since"]
    elif user.role == "admin":
        skip_fields = ["id_number", "badge_id", "department"]
    else:
        skip_fields = []

    if request.method == 'POST':
        form = CombinedUserProfileForm(request.POST, request.FILES, instance=user, user=user)
        password_form = PasswordChangeForm(user=user, data=request.POST)
        
        if form.is_valid():
            form.save()
            ActivityLog.objects.create(
                user=request.user,
                action="updated profile "
            )
            messages.success(request, "Profile updated successfully.")
            return redirect('profile_view')
        
        elif password_form.is_valid():
            password_form.save()
            update_session_auth_hash(request, password_form.user)
            messages.success(request, "Password changed successfully.")
            return redirect('edit_profile')
    else:
        form = CombinedUserProfileForm(instance=user, user=user)
        password_form = PasswordChangeForm(user=user)

    return render(request, 'accounts/profiles/profile.html', {
        'form': form,
        'password_form': password_form,
        'skip_fields': skip_fields,  # Pass skip_fields to the template
    })


@user_passes_test(is_admin)
def admin_update_user_view(request, user_id):
    target_user = get_object_or_404(User, id=user_id)

    # Determine skip_fields based on the target user's role
    if target_user.role == "citizen":
        skip_fields = ["badge_id", "department", "office_name", "managed_since"]
    elif target_user.role == "officer":
        skip_fields = ["id_number", "office_name", "managed_since"]
    elif target_user.role == "admin":
        skip_fields = ["id_number",  "badge_id", "department"]
    else:
        skip_fields = []

    if request.method == 'POST':
        form = CombinedUserProfileForm(request.POST, instance=target_user)
        if form.is_valid():
            form.save()
            return redirect('manage_users')
    else:
        form = CombinedUserProfileForm(instance=target_user)

    return render(
        request,
        'accounts/profiles/profile.html',
        {
            'form': form,
            'target_user': target_user,
            'skip_fields': skip_fields,  # Pass skip_fields to template
        }
    )
