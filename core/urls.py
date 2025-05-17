from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', lambda request: redirect('dashboard'), name='home'),
    path('resources/', include('resources.urls')),
    path('cases/', include('cases.urls')),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),

]
