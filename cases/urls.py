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

    # success
    path('report-success/', views.report_success, name='report_success'),
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
    path('assign_case/<int:pk>/', views.assign_case_to_officer, name='assign_case'),
    path('case/<int:pk>/assignment-history/', views.case_assignment_history, name='case_assignment_history'),

    
    # Report Handling
    # path('reports/<int:pk>/update-status/', views.update_report_status, name='update_report_status'),
    path('reports/<int:pk>/send-additional-details/', views.send_additional_details, name='send_additional_details'),
    path('reports/<int:pk>/request-more-info/', views.request_more_info, name='request_more_info'),
    path('reports/<int:pk>/provide-recommendation/', views.provide_recommendation, name='provide_recommendation'),
    path('report/<int:pk>/update-status-priority/', views.update_status_priority, name='update_status_priority'),
    path('reports/<int:report_id>/upload-additional-evidence/', views.upload_additional_evidence, name='upload_additional_evidence'),
    path('evidence/delete/<int:evidence_id>/', views.delete_additional_evidence, name='delete_additional_evidence'),



    #Links

    path('reports/recent/', views.recent_reports, name='recent_reports'),
    path('reports/most/', views.most_reported_crime, name='most_reported_crime'),
    path('zones/top/', views.top_zones, name='top_zones'),
    path('cases/pending/', views.pending_cases, name='pending_cases'),
    path('cases/investigating/', views.investigating_cases, name='investigating_cases'),
    path('cases/closed_cases/', views.closed_cases, name='closed_cases'),
    path('cases/irrelevant/', views.irrelevant_cases, name='irrelevant_cases'),
    path('cases/resolved/', views.resolved_cases, name='resolved_cases'),
    path('cases/critical/', views.critical_cases, name='critical_cases'),

    
    # update status
    path('reports/<int:pk>/update-status/', views.update_report_status, name='update_report_status'),
    path('reports/<int:pk>/update-priority/', views.update_report_priority, name='update_report_priority'),

    # logs
    # urls.py
    path('reports/<int:report_id>/logs/', views.report_logs, name='report_logs'),
    path('activity-logs/', views.activity_logs_view, name='activity_logs'),


]
    


