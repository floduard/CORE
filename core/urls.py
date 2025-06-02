from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', lambda request: redirect('dashboard'), name='home'),
    path('resources/', include('resources.urls')),
    path('cases/', include('cases.urls')),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('terms/', TemplateView.as_view(template_name='terms_and_conditions.html'),name='terms_and_conditions'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

else:
    urlpatterns += [
        re_path(r'^evidence/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]