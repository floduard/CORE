from django.urls import path
from . import views

urlpatterns = [

    # resources
    path('resource-list/', views.resource_list, name='resource_list'),
    path('add/', views.add_resource, name='add_resource'),
    path('edit/<int:pk>/', views.edit_resource, name='edit_resource'),
    path('delete/<int:pk>/', views.delete_resource, name='delete_resource'),

    # feedbacks
    path('feedback/submit/', views.submit_feedback, name='submit_feedback'),
    path('feedback/list/', views.feedback_list, name='feedback_list'),
    path('feedback/reply/<int:pk>/', views.reply_feedback, name='reply_feedback'),
    path('feedback/my/', views.my_feedbacks, name='my_feedbacks'),
    path('admin/feedback/delete/<int:pk>/', views.delete_feedback, name='delete_feedback'),
]
