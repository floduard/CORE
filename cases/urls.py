from django.urls import path
from . import views

urlpatterns = [
    path('available-cybercrimes/', views.available_cybercrimes, name='available_cybercrimes'),
    path('available-cybercrimes/add/', views.add_cybercrime, name='add_cybercrime'),
    path('available-cybercrimes/<int:pk>/edit/', views.edit_cybercrime, name='edit_cybercrime'),
    path('available-cybercrimes/<int:pk>/delete/', views.delete_cybercrime, name='delete_cybercrime'),
    path('cybercrimes/<int:pk>/', views.cybercrime_detail, name='detail_cybercrime'),
]
