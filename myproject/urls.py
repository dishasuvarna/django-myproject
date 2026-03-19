from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static


def home(request):
    return HttpResponse("Hospital Management System Running ✅")


urlpatterns = [
    path('admin/', admin.site.urls),

    # ✅ HOME PAGE FIX
    path('', home),

    # app urls
    path('', include('core.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)