from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_invoice, name='upload_invoice'),
    path('export/', views.export_excel, name='export_excel'),
]