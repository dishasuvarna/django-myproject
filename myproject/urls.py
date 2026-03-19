from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static


# Simple home page
def home(request):
    return HttpResponse("Hospital Management System Running ✅")


urlpatterns = [
    path('', home),  # ✅ fix for /
    path('admin/', admin.site.urls),  # ✅ fix for admin
    path('', include('core.urls')),  # your app urls
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)