from django.urls import path
from . import views

urlpatterns = [
    path('resource-list/', views.resource_list, name='resource_list'),
    path('add/', views.add_resource, name='add_resource'),
    path('edit/<int:pk>/', views.edit_resource, name='edit_resource'),
    path('delete/<int:pk>/', views.delete_resource, name='delete_resource'),
]
