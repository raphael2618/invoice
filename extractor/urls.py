from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# Remplace 'myapp' par 'extractor'
from extractor import views
from django.urls import path
from . import views # Le "." suffit, c'est plus propre !

urlpatterns = [
    path('', views.upload_invoice, name='upload_invoice'),
]
urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Routes d'authentification (login/logout)
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Ta page principale
    path('', views.upload_invoice, name='upload_invoice'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)