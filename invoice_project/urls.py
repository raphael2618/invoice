from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls), # <-- On a corrigé 'name' par 'urls'
    path('accounts/', include('django.contrib.auth.urls')), 
    path('', include('extractor.urls')),
]