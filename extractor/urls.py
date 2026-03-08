from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_invoice, name='upload_invoice'),
    path('register/', views.register, name='register'),
    path('update-invoice-full/', views.update_invoice_full, name='update_invoice_full'),
    path('delete/<int:invoice_id>/', views.delete_invoice, name='delete_invoice'),
    path('export/', views.export_excel, name='export_excel'),
    path('serve-pdf/<int:invoice_id>/', views.serve_invoice_pdf, name='serve_invoice_pdf'),
]