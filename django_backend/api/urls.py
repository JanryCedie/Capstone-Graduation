from django.urls import path
from .views_auth import (
    register, login, forgot_password, reset_password, 
    get_all_users, export_residents, verify_user, get_current_user
)
from .views_events import (
    handle_events, get_global_logs, get_barangay_stats, join_event,
    get_my_participation, get_participants, export_participants,
    verify_attendance, event_detail, get_leaderboard
)

urlpatterns = [
    # Auth URLs (/api/auth)
    path('auth/register', register, name='register'),
    path('auth/login', login, name='login'),
    path('auth/forgot-password', forgot_password, name='forgot_password'),
    path('auth/reset-password', reset_password, name='reset_password'),
    path('auth/users', get_all_users, name='get_all_users'),
    path('auth/users/export', export_residents, name='export_residents'),
    path('auth/users/verify/<int:user_id>', verify_user, name='verify_user'),
    path('auth/me', get_current_user, name='get_current_user'),

    # Events URLs (/api/events)
    path('events/', handle_events, name='handle_events'),
    path('events/global-logs', get_global_logs, name='get_global_logs'),
    path('events/barangay-stats', get_barangay_stats, name='get_barangay_stats'),
    path('events/join/<int:event_id>', join_event, name='join_event'),
    path('events/my-participation', get_my_participation, name='get_my_participation'),
    path('events/participants/<int:event_id>', get_participants, name='get_participants'),
    path('events/<int:event_id>/participants/export', export_participants, name='export_participants'),
    path('events/verify/<int:participation_id>', verify_attendance, name='verify_attendance'),
    path('events/<int:event_id>', event_detail, name='event_detail'),
    path('events/leaderboard', get_leaderboard, name='get_leaderboard'),
]
