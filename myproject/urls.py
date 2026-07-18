from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render, redirect
from django.conf import settings
from django.conf.urls.static import static


def home(request):
    # If already logged in, skip the landing page and go straight to
    # the correct dashboard based on role.
    if request.user.is_authenticated:
        try:
            from core.models import Profile
            profile = Profile.objects.get(user=request.user)
            if profile.role == 'doctor':
                return redirect('doctor_dashboard')
            else:
                return redirect('patient_form')  # adjust if patients have a different home page
        except Profile.DoesNotExist:
            pass  # fall through to landing page if profile lookup fails

    return render(request, 'landing.html')


urlpatterns = [
    path('admin/', admin.site.urls),

    # HOME PAGE
    path('', home),

    # app urls
    path('', include('core.urls')),
]

# MEDIA FILES (QR IMAGE FIX)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)