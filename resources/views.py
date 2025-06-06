from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone

from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Custom admin-only decorator
def admin_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.role == 'admin')(view_func)



def resource_list(request):
    resources = Resource.objects.all()
    resource_type = request.GET.get('category')
    if resource_type:
        resources = resources.filter(category=resource_type)
    q = request.GET.get('q')
    if q:
        resources = resources.filter(Q(name__icontains=q) | Q(description__icontains=q))
    resources = resources.order_by('date_uploaded')
    paginator = Paginator(resources, 10)  # 10 resources per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'resources/resource_list.html', {
        'page_obj': page_obj,
        'selected_type': resource_type,
        'query': q,
    })

@admin_required
def add_resource(request):
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.uploaded_by = request.user
            resource.save()
            messages.success(request, 'Resource added successfully.')
            return redirect('resource_list')
    else:
        form = ResourceForm()
    return render(request, 'resources/add_resource.html', {'form': form})

@admin_required
def edit_resource(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    form = ResourceForm(request.POST or None, request.FILES or None, instance=resource)
    if form.is_valid():
        form.save()
        messages.success(request, 'Resource updated successfully.')
        return redirect('resource_list')
    return render(request, 'resources/edit_resource.html', {'form': form})

@admin_required
def delete_resource(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    resource.delete()
    messages.success(request, 'Resource deleted successfully.')
    return redirect('resource_list')


@login_required
def my_feedbacks(request):
    feedbacks = Feedback.objects.filter(user=request.user).order_by('-submitted_at')
    return render(request, 'feedback/my_feedbacks.html', {'feedbacks': feedbacks})


def submit_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            if request.user.is_authenticated:
                feedback.user = request.user  # Assign only if authenticated
            feedback.save()
            if request.user.is_authenticated:
                return redirect('my_feedbacks')
            else:
                return redirect('about')
    else:
        form = FeedbackForm()
    return render(request, 'feedback/submit_feedback.html', {'form': form})


@user_passes_test(lambda u: u.role == 'admin')
def feedback_list(request):
    feedbacks = Feedback.objects.all().order_by('-submitted_at')
    return render(request, 'feedback/feedback_list.html', {'feedbacks': feedbacks})

@user_passes_test(lambda u: u.role == 'admin')
def reply_feedback(request, pk):
    feedback = get_object_or_404(Feedback, pk=pk)

    if request.method == 'POST':
        form = AdminReplyForm(request.POST)
        if form.is_valid():
            new_reply = form.cleaned_data['admin_reply']  # Get new reply

            # Append new reply while preserving previous replies
            if feedback.admin_reply:
                feedback.admin_reply += "\n\n" + f"{new_reply}"
            else:
                feedback.admin_reply = f"{new_reply}"  # First reply

            feedback.replied_at = timezone.now()
            feedback.save()
            return redirect('feedback_list')
    else:
        form = AdminReplyForm(instance=feedback)

    return render(request, 'feedback/reply_feedback.html', {'form': form, 'feedback': feedback})


@user_passes_test(lambda u: u.role == 'admin')
def delete_feedback(request, pk):
    feedback = get_object_or_404(Feedback, pk=pk)
    feedback.delete()
    return redirect('feedback_list')


@login_required
def admin_logs_view(request):
    logs = LogEntry.objects.select_related('user', 'content_type').order_by('-action_time')[:100]
    return render(request, 'logs/admin_logs.html', {'logs': logs})
