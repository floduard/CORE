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

def available_cybercrimes(request):
    cybercrimes = CybercrimeType.objects.all()
    return render(request, 'cases/available_cybercrimes.html', {'cybercrimes': cybercrimes})



def is_admin(user):
    return user.is_authenticated and user.role == 'admin'
    


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
            return redirect('submit_cybercrime_report')  # Or wherever you want to redirect after submission
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = CybercrimeReportForm()

    return render(request, 'reports/submit_cybercrime_report.html', {'form': form})



@user_passes_test(is_admin)
def all_reports_view(request):
    reports = CybercrimeReport.objects.all().order_by('-date')
    return render(request, 'reports/all_reports.html', {'reports': reports})

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

