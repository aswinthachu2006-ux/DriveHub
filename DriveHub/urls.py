"""
URL configuration for DriveHub project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts import views as account_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('bookings/', include('bookings.urls')),
    path('cars/', include('cars.urls')),
    path('inspection/', include('inspection.urls')),

    # Friendly root-level shortcuts for accounts
    path('login/', account_views.login_view),
    path('signup/', account_views.signup_view),
    path('register/', account_views.register_view),
    path('dashboard/', account_views.dashboard_view),
    path('logout/', account_views.logout_view),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
