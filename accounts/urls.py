from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('licence/upload/', views.licence_upload_view, name='licence_upload'),
    path('licence/status/', views.licence_status_view, name='licence_status'),
    path('licence/demo-verify/', views.demo_licence_verify_view, name='demo_licence_verify'),
    path('licence/admin-toggle/<int:profile_id>/<str:action>/', views.admin_toggle_licence, name='admin_toggle_licence'),
]
