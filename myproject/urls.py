# from django.contrib import admin
# from django.urls import path, include
# from django.shortcuts import render, redirect
# from django.conf import settings
# from django.conf.urls.static import static

# def home(request):
#     if request.user.is_authenticated:
#         try:
#             from core.models import Profile
#             profile = Profile.objects.get(user=request.user)
#             if profile.role == 'doctor':
#                 return redirect('doctor_dashboard')
#             else:
#                 return redirect('patient_form')  # adjust if patients have a different home page
#         except Profile.DoesNotExist:
#             pass  # fall through to landing page if profile lookup fails

#     return render(request, 'landing.html')


# urlpatterns = [
#     path('admin/', admin.site.urls),

#     # HOME PAGE
#     path('', home),

#     # app urls
#     path('', include('core.urls')),
# ]

# # MEDIA FILES 
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



from django.contrib import admin
from django.urls import path, include, re_path
from django.shortcuts import render, redirect
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve


def home(request):
    if request.user.is_authenticated:
        try:
            from core.models import Profile
            profile = Profile.objects.get(user=request.user)
            if profile.role == 'doctor':
                return redirect('doctor_dashboard')
            else:
                return redirect('patient_form')
        except Profile.DoesNotExist:
            pass
    return render(request, 'landing.html')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),
    path('', include('core.urls')),

    # Serve media files even when DEBUG=False (needed for Railway)
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

# Also keep this for local dev (DEBUG=True) - harmless overlap, not a conflict
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)