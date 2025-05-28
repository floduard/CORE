from django.shortcuts import render
from .models import *
from accounts.models import *
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from .forms import *
from django.utils.crypto import get_random_string
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q
from django.urls import reverse
from accounts.utils import notify_user
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import F
from django.db.models.functions import Concat
from django.db.models import Value
from django.utils.timezone import localtime, now


def available_cybercrimes(request):
    cybercrimes = CybercrimeType.objects.all()
    return render(request, 'cases/available_cybercrimes.html', {'cybercrimes': cybercrimes})



def is_admin(user):
    return user.is_authenticated and user.role == 'admin'
    

def officer_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.role == 'officer' or u.role == 'admin')(view_func)

@user_passes_test(is_admin)
def add_cybercrime(request):
    if request.method == 'POST':
        form = CybercrimeForm(request.POST)
        if form.is_valid():
            form.save()
            new_crime = form.save()
            url = f"/cases/cybercrimes/{new_crime.pk}/"            
            users = User.objects.all()
            for user in users:
                notify_user(
                    recipient=user,
                    message=f"A new cybercrime type '{new_crime.name}' has been added.",
                    url=url
                )
                ActivityLog.objects.create(
                    user=request.user,
                    action='Cybercrime category added'
                )
            return redirect('available_cybercrimes')
    else:
        form = CybercrimeForm()
    return render(request, 'cases/cybercrime_form.html', {'form': form, 'action': 'Add'})

@user_passes_test(is_admin)
def edit_cybercrime(request, pk):
    crime = get_object_or_404(CybercrimeType, pk=pk)
    if request.method == 'POST':
        form = CybercrimeForm(request.POST, instance=crime)
        if form.is_valid():
            form.save()
            return redirect('available_cybercrimes')
    else:
        form = CybercrimeForm(instance=crime)
    return render(request, 'cases/cybercrime_form.html', {'form': form, 'action': 'Edit'})

@user_passes_test(is_admin)
def delete_cybercrime(request, pk):
    crime = get_object_or_404(CybercrimeType, pk=pk)
    crime_name = crime.name

    users = User.objects.filter(email__isnull=False).exclude(role='admin')
    if request.method == 'POST':
        crime.delete()        
        for user in users:
                notify_user(
                    recipient=user,
                    message=f"A cybercrime type '{crime_name}' has been deleted.",
                    url=reverse('available_cybercrimes')
                )
        ActivityLog.objects.create(
                    user=request.user,
                    action='Cybercrime category deleted'
                )
        return redirect('available_cybercrimes')
    return render(request, 'cases/cybercrime_confirm_delete.html', {'crime': crime})

def cybercrime_detail(request, pk):
    crime = get_object_or_404(CybercrimeType, pk=pk)
    return render(request, 'cases/cybercrime_detail.html', {
        'crime': crime
    })



def submit_cybercrime_report(request):    
    recipient_email=request.user.email
    if request.method == 'POST':
        form = CybercrimeReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.tracking_id = get_random_string(12).upper()
            if request.user.is_authenticated:
                report.user = request.user
            report.save()
            if request.user.is_authenticated:
                Notification.objects.create(
                    recipient=request.user,
                    message=f"Your cybercrime report was submitted successfully.Your Tracking ID is: {report.tracking_id} ",
                    url=reverse('report_detail', args=[report.pk])
                )
                ActivityLog.objects.create(
                    user=request.user,
                    action=f"Case with {report.tracking_id} Tracking ID submitted. "
                )

                subject = "Case submitted successfully"
                DEFAULT_FROM_EMAIL='noreply@cras.com'
                message =f"Your case  has been submitted successfully. Your Tracking ID is: {report.tracking_id} Our Team is going to work on it as soon as possible. stay tuned for updates."

                send_mail(
                                subject,
                                message,
                                DEFAULT_FROM_EMAIL,
                                [recipient_email],
                                fail_silently=False,
                            )
            if request.user.is_authenticated:
              messages.success(request, f"Report submitted successfully! Your Tracking ID is: {report.tracking_id}")
            return redirect('report_success') 
             # Or wherever you want to redirect after submission
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = CybercrimeReportForm()

    return render(request, 'reports/submit_cybercrime_report.html', {'form': form})



@officer_required
def all_reports_view(request):
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status')
    crime_type_filter = request.GET.get('crime_type')

    reports = CybercrimeReport.objects.all().order_by('id')

    if query:
        reports = reports.filter(
            Q(tracking_id__icontains=query) |
            Q(user__username__icontains=query)
        )

    if status_filter:
        reports = reports.filter(status=status_filter)

    if crime_type_filter:
        reports = reports.filter(crime_type__name=crime_type_filter)

    paginator = Paginator(reports, 10)  # 10 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # For filter dropdowns
    statuses = CybercrimeReport.objects.values_list('status', flat=True).distinct()
    types = CybercrimeReport.objects.values_list('crime_type__name', flat=True).distinct()

    context = {
        'page_obj': page_obj,
        'query': query,
        'statuses': statuses,
        'crime_types': types,
        'selected_status': status_filter,
        'selected_type': crime_type_filter,
    }
    
    return render(request, 'reports/all_reports.html', context)

@login_required
def report_detail_view(request, pk):
    report = get_object_or_404(CybercrimeReport, pk=pk)
    officers = User.objects.filter(role='officer', is_active=True).order_by('last_name')
    if request.user.role == 'admin':
        activity_logs = ActivityLog.objects.filter(action__icontains=report.tracking_id)
    else:
        activity_logs = ActivityLog.objects.filter(user=request.user, action__icontains=report.tracking_id)
    return render(request, 'reports/report_detail.html', {
        'report': report,
        'activity_logs': activity_logs,
        'officers': officers,
        # other context data
    })
    

@user_passes_test(is_admin)
def report_update_view(request, pk):
    report = get_object_or_404(CybercrimeReport, pk=pk)
    form = CybercrimeReportForm(request.POST or None, request.FILES or None, instance=report)
    if form.is_valid():
        form.save()
        if request.user.is_authenticated:
            ActivityLog.objects.create(
                        user=request.user,
                        action=f"Case with {report.tracking_id} Tracking ID updated. "
                    )
            messages.success(request, "Report updated successfully.")
            return redirect('all_reports')
    return render(request, 'reports/report_form.html', {'form': form, 'title': 'Edit Report'})

@user_passes_test(is_admin)
def report_delete_view(request, pk):
    report = get_object_or_404(CybercrimeReport, pk=pk)
    tracking = report.tracking_id
    report.delete()
    if request.user.is_authenticated:
        Notification.objects.create(
                    recipient=report.user,
                    message=f"A case with  Tracking ID is: {tracking} have been Deleted",
                    url=reverse('all_reports')
                )
        ActivityLog.objects.create(
                        user=request.user,
                        action=f"Case with {tracking} Tracking ID deleted. "
                    )
        messages.success(request, "Report deleted.")
    return redirect('all_reports')


@login_required
def my_reports(request):
    reports = CybercrimeReport.objects.filter(user=request.user)
    return render(request, 'reports/my_reports.html', {'reports': reports})

@login_required
def delete_report(request, pk):
    report = get_object_or_404(CybercrimeReport, pk=pk, user=request.user)
    if report.status.lower() == 'pending':
        report.delete()
        ActivityLog.objects.create(
                    user=request.user,
                    action=f"Case with {report.tracking_id} Tracking ID deleted. "
                )
        messages.success(request, "Report deleted successfully.")
    else:
        messages.warning(request, "Only pending reports can be deleted.")
    return redirect('my_reports')

@login_required
def assigned_reports(request):    
        reports = CybercrimeReport.objects.filter(assignee=request.user)        
        return render(request, 'reports/assigned_reports.html', {'reports': reports})


@login_required
def update_report_status(request, pk):
    report = get_object_or_404(CybercrimeReport, pk=pk)
    user_instance = User.objects.get(id=report.assignee.pk)
    if request.method == 'POST' and request.user.role in ['admin', 'officer']:
        new_status = request.POST.get('status')
        if new_status in ['Pending', 'Under Investigation', 'Resolved','Rejected','Closed', 'Irrelevant']:
            notify_user(
                    recipient=user_instance,
                    message=f"Your Case Status updated to {new_status}.",
                    url=reverse('report_detail', args=[report.pk])
                )
            ActivityLog.objects.create(
                    user=request.user,
                    action=f"Case with {report.tracking_id} Tracking ID status changed from '{report.status}' to '{new_status}'. "
                )
            report.status = new_status
            report.save()
    return redirect('report_detail', pk)


@login_required
def send_additional_details(request, pk):
    report = get_object_or_404(CybercrimeReport, pk=pk)
    if report.assignee:  # Ensure assignee is not None
         user_instance = User.objects.get(id=report.assignee.pk)
    else:
         user_instance = None  # Or handle it appropriately

    if request.method == 'POST' and request.user.role in ['citizen']:
        
        new_details= request.POST.get('more_details', "")
        report.more_details = Concat(F('more_details'), Value("\n"), Value(new_details))
        report.save()

        ActivityLog.objects.create(
                    user= request.user,
                    action=f"Additional details submitted for case {report.tracking_id} as {new_details}. "
                )
        notify_user(
                    recipient=user_instance,
                    message=f"Additional details submitted for case {report.tracking_id} as {new_details}.",
                    url=reverse('report_detail', args=[report.pk])
                )
    return redirect('report_detail', pk=pk)


@login_required
def request_more_info(request, pk):
    report = get_object_or_404(CybercrimeReport, pk=pk)
    
    

    if request.method == 'POST' and request.user.role in ['admin', 'officer']:
        request_more_info_data = request.POST.get('request_more_info', "").strip()
        
        # Append new info to existing info
        if report.request_more_info:
            report.request_more_info += f"\n{request_more_info_data}"
        else:
            report.request_more_info = request_more_info_data

        report.save()

        messages.success(request, "More info requested.")

        
        notify_user(
                recipient=report.user,
                message=f"More info requested for case {report.tracking_id}: {request_more_info_data}",
                url=reverse('report_detail', args=[report.pk])
            )

        ActivityLog.objects.create(
            user=request.user,
            action=f"Details requested for case {report.tracking_id}."
        )

    return redirect('report_detail', pk)
    
@login_required
def provide_recommendation(request, pk):
    report = get_object_or_404(CybercrimeReport, pk=pk)    
   
    if request.method == 'POST' and request.user.role in ['admin', 'officer']:
            new_recommendation = request.POST.get('recommendations', "").strip()
            if new_recommendation:
                if report.recommendations:
                    report.recommendations += f"\n{new_recommendation}"
                else:
                    report.recommendations = new_recommendation
                report.save()

                messages.success(request, "Recommendations provided.")
                
                notify_user(
                        recipient=report.user,
                        message=f"Recommendations provided: {new_recommendation}",
                        url=reverse('report_detail', args=[report.pk])
                    )

                ActivityLog.objects.create(
                    user=request.user,
                    action=f"Recommendations provided for case {report.tracking_id}."
                )
    return redirect('report_detail', pk)

@login_required
def update_status_priority(request, pk):
    report = get_object_or_404(CybercrimeReport, pk=pk)

    if request.user.role not in ['admin', 'officer']:
        messages.error(request, "You are not authorized to perform this action.")
        return redirect('report_detail', pk=pk)

    if request.method == 'POST':
        status = request.POST.get('status')
        priority = request.POST.get('priority')

        if status and priority:
            report.status = status
            report.priority = priority
            report.save()
            messages.success(request, "Report status and priority updated.")
        else:
            messages.error(request, "Invalid input provided.")

    return redirect('report_detail', pk=pk)

# views.py

@login_required
def update_report_status(request, pk):
    report = get_object_or_404(CybercrimeReport, pk=pk)
    if request.user.role != 'officer':
        return redirect('permission_denied')

    if request.method == 'POST':
        new_status = request.POST.get('status')
        old_status = report.status
        report.status = new_status
        report.save()

        if new_status!= 'Closed':
            notify_user(
                        recipient=report.user,
                        message=f"Your Case with {report.tracking_id} have been Closed at {localtime(now()).strftime("%Y-%m-%d %H:%M:%S")} .",
                        url=reverse('report_detail', args=[report.pk])
                    )

        ActivityLog.objects.create(
            user=request.user,
            action=f"Report with {report.tracking_id} Tracking ID Status updated from '{old_status}' to '{new_status}'",
        )

        return redirect('report_detail', pk=pk)

@login_required
def update_report_priority(request, pk):
    report = get_object_or_404(CybercrimeReport, pk=pk)
    if request.user.role != 'admin':
        return redirect('permission_denied')

    if request.method == 'POST':
        new_priority = request.POST.get('priority')
        old_priority = report.priority
        report.priority = new_priority
        report.save()

        ActivityLog.objects.create(
            user=request.user,
            action=f"Report with {report.tracking_id} Tracking ID priority updated from '{old_priority}' to '{new_priority}'",
        )

        return redirect('report_detail', pk=pk)

@login_required
@user_passes_test(lambda u: u.role == 'admin')
def assign_case_to_officer(request, pk):
    case = get_object_or_404(CybercrimeReport, pk=pk)
    if request.method == 'POST':
        form = AssignCaseForm(request.POST, instance=case)
        if form.is_valid():
            reassigned = case.assignee is not None
            new_officer = form.cleaned_data['assignee']
            case.assignee = new_officer
            case.save()
            if reassigned:
                messages.success(request, f"New Case Assigned: {case.tracking_id}.")
                notify_user(
                    recipient=new_officer,
                    message=f"New Case Assigned: {case.tracking_id}.",
                     url=reverse('report_detail', args=[case.pk])
                )
                ActivityLog.objects.create(
                    user=request.user,
                    action=f"Report with {case.tracking_id} Tracking ID have been assigned to {new_officer} ,"
                )
            else:
                messages.success(request, f"New Case Assigned: {case.tracking_id}.")
                notify_user(
                    recipient=new_officer,
                    message=f"New Case Assigned: {case.tracking_id}.",
                     url=reverse('report_detail', args=[case.pk])
                )

                ActivityLog.objects.create(
                    user=request.user,
                    action=f"Report with {report.tracking_id} Tracking ID have been assigned to {new_officer} ,"
                )
            # Log history
            CaseAssignmentHistory.objects.create(
                case=case,
                assigned_by=request.user,
                assigned_to=new_officer
            )

            messages.success(request, "Case assigned successfully.")
            return redirect('report_detail', pk=case.pk)
    else:
        form = AssignCaseForm(instance=case)

    return render(request, 'reports/assign_case.html', {'form': form, 'case': case})

def case_assignment_history(request, pk):
    case = get_object_or_404(CybercrimeReport, pk=pk)
    history = CaseAssignmentHistory.objects.filter(case=case).order_by('-timestamp')
    return render(request, 'reports/assignment_history.html', {'case': case, 'history': history})

def get_reports_by_role(request, queryset):
    if request.user.role == 'citizen':
        return queryset.filter(user=request.user)
    return queryset

@login_required
def recent_reports(request):
    last_week = now() - timedelta(days=7)
    reports = CybercrimeReport.objects.filter(submitted_at__gte=last_week)
    reports = get_reports_by_role(request, reports)
    return render(request, 'reports/report_list.html', {'reports': reports, 'title': 'Recent Reports'})

@login_required
def most_reported_crime(request):
    from django.db.models import Count

    base_qs = CybercrimeReport.objects
    if request.user.role == 'citizen':
        base_qs = base_qs.filter(user=request.user)

    most_common = (base_qs
                   .values('crime_type')
                   .annotate(count=Count('crime_type'))
                   .order_by('-count')
                   .first())

    if most_common:
        reports = base_qs.filter(crime_type=most_common['crime_type'])
    else:
        reports = CybercrimeReport.objects.none()

    return render(request, 'reports/report_list.html', {'reports': reports, 'title': 'Most Reported Crime'})

@login_required
def top_zones(request):
    from django.db.models import Count

    base_qs = CybercrimeReport.objects
    if request.user.role == 'citizen':
        base_qs = base_qs.filter(user=request.user)

    top_zone = (base_qs
                .values('province_city')
                .annotate(count=Count('province_city'))
                .order_by('-count')
                .first())

    if top_zone:
        reports = base_qs.filter(province_city=top_zone['province_city'])
    else:
        reports = CybercrimeReport.objects.none()

    return render(request, 'reports/report_list.html', {'reports': reports, 'title': 'Most Affected Zone'})

@login_required
def pending_cases(request):
    reports = CybercrimeReport.objects.filter(status='pending')
    reports = get_reports_by_role(request, reports)
    return render(request, 'reports/report_list.html', {'reports': reports, 'title': 'Pending Cases'})

@login_required
def investigating_cases(request):
    reports = CybercrimeReport.objects.filter(status='under_investigation')
    reports = get_reports_by_role(request, reports)
    return render(request, 'reports/report_list.html', {'reports': reports, 'title': 'Under Investigation'})

@login_required
def closed_cases(request):
    reports = CybercrimeReport.objects.filter(status='closed')
    reports = get_reports_by_role(request, reports)
    return render(request, 'reports/report_list.html', {'reports': reports, 'title': 'Closed Cases'})

@login_required
def irrelevant_cases(request):
    reports = CybercrimeReport.objects.filter(status='irrelevant')
    reports = get_reports_by_role(request, reports)
    return render(request, 'reports/report_list.html', {'reports': reports, 'title': 'Irrelevant Cases'})

@login_required
def resolved_cases(request):
    reports = CybercrimeReport.objects.filter(status='resolved')
    reports = get_reports_by_role(request, reports)
    return render(request, 'reports/report_list.html', {'reports': reports, 'title': 'Resolved Cases'})

@login_required
def critical_cases(request):
    reports = CybercrimeReport.objects.filter(priority='critical')
    reports = get_reports_by_role(request, reports)
    return render(request, 'reports/report_list.html', {'reports': reports, 'title': 'Critical Cases'})




def report_success(request):
    if request.user.is_authenticated:
        user = request.user
        user_reports = CybercrimeReport.objects.filter(user=user)

        stats = {
            'total_reports': user_reports.count(),
            'pending': user_reports.filter(status='pending').count(),
            'resolved': user_reports.filter(status='resolved').count(),
            'closed': user_reports.filter(status='closed').count(),
        }

        return render(request, 'reports/success.html', {
            'user': user,
            'stats': stats,
        })

    else:
       return render(request, 'reports/report_success.html')


@login_required
def report_logs(request, report_id):
    report = get_object_or_404(CybercrimeReport, id=report_id)

    # Optional: Restrict access
    if request.user.role != 'admin' and request.user != report.assigned_officer:
        return HttpResponseForbidden("You are not allowed to view this report's logs.")

    logs = report.activity_logs.select_related('user')
    paginator = Paginator(logs, 10)  # Show 10 logs per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'partial/audit_history.html', {
        'report': report,
        'page_obj': page_obj,
    })

@login_required
def activity_logs_view(request):
    user = request.user
    if user.role == 'admin':  # Adjust depending on how you store roles
        logs = ActivityLog.objects.all()
    else:
        logs = ActivityLog.objects.filter(user=user)
    
    return render(request, 'logs/activity_logs.html', {'logs': logs})

@login_required
def upload_additional_evidence(request, report_id):
    report = get_object_or_404(CybercrimeReport, id=report_id)

    if request.method == 'POST':
        form = AdditionalEvidenceForm(request.POST, request.FILES)
        if form.is_valid():
            evidence = form.save(commit=False)
            evidence.report = report
            evidence.uploaded_by = request.user
            evidence.save()
            messages.success(request, "Evidence uploaded successfully.")
            return redirect('report_detail',report_id)
    else:
        form = AdditionalEvidenceForm()

    return render(request, 'partials/upload_additional_evidence.html', {'form': form, 'report': report})


@login_required
@user_passes_test(is_admin)
def delete_additional_evidence(request, evidence_id):
    evidence = get_object_or_404(AdditionalEvidence, id=evidence_id)
    report_id = evidence.report.id

    # Delete the file from storage
    evidence.file.delete(save=False)

    # Delete the DB entry
    evidence.delete()
    messages.success(request, "Additional evidence deleted successfully.")
    return redirect('report_detail', report_id)


@login_required
@user_passes_test(lambda u: u.role == 'admin')  # Only admin can assign
def assign_to_officer(request, report_id):
    report = get_object_or_404(CybercrimeReport, id=report_id)
    
    if request.method == 'POST':
        officer_id = request.POST.get('officer_id')
        if officer_id:
            officer = get_object_or_404(User, id=officer_id, role='officer', is_active=True)
            report.assignee = officer
            report.save()
            messages.success(request, f"Assigned to Officer {officer.get_full_name()}")
        else:
            messages.error(request, "No officer selected.")
    
    return redirect('report_detail', report_id)