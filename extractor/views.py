import os
import json
import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse, FileResponse
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt
from django.utils.text import slugify

from .models import Invoice, InvoiceItem
from .services import extract_invoice_data

@login_required
def serve_invoice_pdf(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
    file_path = invoice.pdf_file.path
    content_type = "application/pdf" if file_path.lower().endswith('.pdf') else "image/jpeg"
    return FileResponse(open(file_path, 'rb'), content_type=content_type)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('upload_invoice')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def upload_invoice(request):
    if request.method == 'POST' and request.FILES.get('pdf_file'):
        file = request.FILES['pdf_file']
        name, ext = os.path.splitext(file.name)
        file.name = f"{slugify(name)}{ext}"
        try:
            data = extract_invoice_data(file)
            invoice = Invoice.objects.create(
                user=request.user,
                supplier=data.get('supplier', 'Inconnu'),
                date=data.get('date'),
                total_ttc=data.get('total_ttc', 0),
                currency=data.get('currency', 'EUR'),
                tva=data.get('tva', 0),
                category=data.get('category', 'Divers'),
                pdf_file=file
            )
            for item in data.get('items', []):
                InvoiceItem.objects.create(
                    invoice=invoice,
                    description=item.get('description', 'Article'),
                    quantity=item.get('quantity', 1),
                    price_unit=item.get('price_unit', 0)
                )
            messages.success(request, "Import réussi !")
        except Exception as e:
            messages.error(request, f"Erreur : {e}")
        return redirect('upload_invoice')

    user_invoices = Invoice.objects.filter(user=request.user).order_by('-date')
    total_ttc = user_invoices.aggregate(Sum('total_ttc'))['total_ttc__sum'] or 0
    return render(request, 'extractor/upload.html', {'invoices': user_invoices, 'total_month': total_ttc})

@login_required
@csrf_exempt
def update_invoice_full(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            invoice = get_object_or_404(Invoice, id=data.get('id'), user=request.user)
            invoice.supplier = data.get('supplier')
            invoice.currency = data.get('currency', 'EUR')
            invoice.total_ttc = float(data.get('total_ttc', 0))
            
            invoice.items.all().delete()
            for it in data.get('items', []):
                InvoiceItem.objects.create(
                    invoice=invoice,
                    description=it['description'],
                    quantity=int(it['quantity']),
                    price_unit=float(it['price_unit'])
                )
            invoice.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
def delete_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
    invoice.delete()
    return redirect('upload_invoice')

@login_required
def export_excel(request):
    invoices = Invoice.objects.filter(user=request.user)
    df = pd.DataFrame(list(invoices.values('supplier', 'date', 'total_ttc')))
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=compta.xlsx'
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return response