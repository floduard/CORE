from django.shortcuts import render, redirect, get_object_or_404
from .models import Resource
from .forms import ResourceForm
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q

# Custom admin-only decorator
def admin_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.role == 'admin')(view_func)



def resource_list(request):
    resources = Resource.objects.all()

    # Visibility: Only show approved/visible resources to non-admins
    

    # Filtering by type and search
    resource_type = request.GET.get('type')
    if resource_type:
        resources = resources.filter(type=resource_type)

    q = request.GET.get('q')
    if q:
        resources = resources.filter(Q(name__icontains=q) | Q(description__icontains=q))

    resources = resources.order_by('date_uploaded')

    # Pagination
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
