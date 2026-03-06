from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_invoice, name='upload_invoice'),
    path('register/', views.register, name='register'), # Nouvelle route
    path('delete/<int:invoice_id>/', views.delete_invoice, name='delete_invoice'),
    path('export/', views.export_excel, name='export_excel'),
]