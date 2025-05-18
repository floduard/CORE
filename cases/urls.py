from django.urls import path
from . import views

urlpatterns = [
    # Available cybercrimes

    path('available-cybercrimes/', views.available_cybercrimes, name='available_cybercrimes'),
    path('available-cybercrimes/add/', views.add_cybercrime, name='add_cybercrime'),
    path('available-cybercrimes/<int:pk>/edit/', views.edit_cybercrime, name='edit_cybercrime'),
    path('available-cybercrimes/<int:pk>/delete/', views.delete_cybercrime, name='delete_cybercrime'),
    path('cybercrimes/<int:pk>/', views.cybercrime_detail, name='detail_cybercrime'),

    # Report incident
    path('report/cybercrime/', views.submit_cybercrime_report, name='submit_cybercrime_report'),
    # Admin Actions On Reports
    path('admin/reports/', views.all_reports_view, name='all_reports'),
    path('admin/reports/<int:pk>/', views.report_detail_view, name='report_detail'),
    path('admin/reports/<int:pk>/edit/', views.report_update_view, name='report_edit'),
    path('admin/reports/<int:pk>/delete/', views.report_delete_view, name='report_delete'),

    # My reports
     path('my-reports/', views.my_reports, name='my_reports'),
    path('delete-report/<int:pk>/', views.delete_report, name='delete_report'),

    # My Assigned Incidents
    path('assigned-reports/', views.assigned_reports, name='assigned_reports'),
    
]
    


