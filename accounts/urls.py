from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', views.citizen_register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/', views.role_based_dashboard, name='dashboard'),

    # summary report
    path('reports/summary/', views.generate_report, name='report_summary'),
   

    # Profiles
     path('profile/', views.view_profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    # add Users
    path('admin/add-user/', views.add_user, name='add_user'),
    # urls.py
    path('activate/<uid>/<token>/', views.activate_account, name='activate_account'),


    # Manage Users
    path('manage-users/', views.manage_users, name='manage_users'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('toggle-user-status/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),

    # Password change URLs
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='accounts/password/password_change.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='accounts/password/password_change_done.html'), name='password_change_done'),

    # Password reset URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='accounts/password/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password/password_reset_complete.html'), name='password_reset_complete'),

    # Notification
    path('notifications/', views.all_notifications, name='all_notifications'),
    path('notifications/fetch/', views.fetch_notifications, name='fetch_notifications'),
    path('notifications/mark-read/', views.mark_notifications_read, name='mark_notifications_read'),
    path('notifications/unread/', views.unread_notifications, name='unread_notifications'),
    path('notifications/read/<int:pk>/', views.mark_as_read, name='mark_notification_read'),

    # statistics redirect

   
]

