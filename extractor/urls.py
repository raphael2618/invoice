from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_invoice, name='upload_invoice'), # Route pour la page principale
    path('export/', views.export_excel, name='export_excel'),
]