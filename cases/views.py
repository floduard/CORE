from django.shortcuts import render
from .models import *
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
    if request.method == 'POST':
        crime.delete()
        return redirect('available_cybercrimes')
    return render(request, 'cases/cybercrime_confirm_delete.html', {'crime': crime})

def cybercrime_detail(request, pk):
    crime = get_object_or_404(CybercrimeType, pk=pk)
    return render(request, 'cases/cybercrime_detail.html', {
        'crime': crime
    })



def submit_cybercrime_report(request):
    if request.method == 'POST':
        form = CybercrimeReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.tracking_id = get_random_string(12).upper()
            if request.user.is_authenticated:
                report.user = request.user
            report.save()
            if request.user.is_authenticated:
              messages.success(request, f"Report submitted successfully! Your Tracking ID is: {report.tracking_id}")
            return redirect('about')  # Or wherever you want to redirect after submission
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

    reports = CybercrimeReport.objects.all()

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
    return render(request, 'reports/report_detail.html', {'report': report})

@user_passes_test(is_admin)
def report_update_view(request, pk):
    report = get_object_or_404(CybercrimeReport, pk=pk)
    form = CybercrimeReportForm(request.POST or None, request.FILES or None, instance=report)
    if form.is_valid():
        form.save()
        messages.success(request, "Report updated successfully.")
        return redirect('all_reports')
    return render(request, 'reports/report_form.html', {'form': form, 'title': 'Edit Report'})

@user_passes_test(is_admin)
def report_delete_view(request, pk):
    report = get_object_or_404(CybercrimeReport, pk=pk)
    report.delete()
    messages.success(request, "Report deleted.")
    return redirect('all_reports')


@login_required
def my_reports(request):
    reports = CybercrimeReport.objects.filter(user=request.user)
    return render(request, 'reports/my_reports.html', {'reports': reports})

@login_required
def delete_report(request, pk):
    report = get_object_or_404(CybercrimeReport, pk=pk, reported_by=request.user)
    if report.status.lower() == 'pending':
        report.delete()
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
    if request.method == 'POST' and request.user.role in ['admin', 'officer']:
        new_status = request.POST.get('status')
        if new_status in ['Pending', 'Under Investigation', 'Resolved','Rejected','Closed', 'Irrelevant']:
            report.status = new_status
            report.save()
    return redirect('report_detail', pk=pk)



@login_required
def send_additional_details(request, pk):
    report = get_object_or_404(CybercrimeReport, pk=pk)
    if request.method == 'POST' and request.user.role in ['citizen']:
        report.more_details = request.POST.get('more_details')
        report.save()
    return redirect('report_detail', pk=pk)

@login_required
def request_more_info(request, pk):
    report = get_object_or_404(CybercrimeReport, pk=pk)
    if request.method == 'POST' and request.user.role in ['admin', 'officer']:
        report.request_more_info  = request.POST.get('additional_contacts')
        report.save()
    return redirect('report_detail', pk=pk)

@login_required
def provide_recommendation(request, pk):
    report = get_object_or_404(CybercrimeReport, pk=pk)
    if request.method == 'POST' and request.user.role in ['admin', 'officer']:
        report.recommendations = request.POST.get('recommendations')
        report.save()
    return redirect('report_detail', pk=pk)

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