from django.shortcuts import render
from .models import CybercrimeType
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from .forms import CybercrimeForm

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
