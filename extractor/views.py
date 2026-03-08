import os
import json
import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.views.decorators.csrf import csrf_exempt

from .models import Invoice
from .services import extract_invoice_data

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Bienvenue {user.username} !")
            return redirect('upload_invoice')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def upload_invoice(request):
    if request.method == 'POST' and request.FILES.get('pdf_file'):
        file = request.FILES['pdf_file']
        try:
            data = extract_invoice_data(file)
            Invoice.objects.create(
                user=request.user,
                supplier=data.get('supplier', 'Inconnu'),
                date=data.get('date'),
                total_ttc=data.get('total_ttc', 0),
                currency=data.get('currency', 'EUR'),
                tva=data.get('tva', 0),
                pdf_file=file
            )
            messages.success(request, "Facture analysée avec succès !")
        except Exception as e:
            messages.error(request, f"Erreur : {str(e)}")
        return redirect('upload_invoice')

    user_invoices = Invoice.objects.filter(user=request.user)
    monthly_stats = user_invoices.annotate(month=TruncMonth('date')).values('month').annotate(total=Sum('total_ttc')).order_by('month')
    supplier_stats = user_invoices.values('supplier').annotate(total=Sum('total_ttc')).order_by('-total')[:5]

    context = {
        'invoices': user_invoices.order_by('-id'),
        'total_month': user_invoices.aggregate(Sum('total_ttc'))['total_ttc__sum'] or 0,
        'tva_month': user_invoices.aggregate(Sum('tva'))['tva__sum'] or 0,
        'count_month': user_invoices.count(),
        'monthly_labels': json.dumps([d['month'].strftime("%b %Y") for d in monthly_stats if d['month']]),
        'monthly_totals': json.dumps([float(d['total']) for d in monthly_stats]),
        'supplier_labels': json.dumps([d['supplier'] for d in supplier_stats]),
        'supplier_totals': json.dumps([float(d['total']) for d in supplier_stats]),
    }
    return render(request, 'extractor/upload.html', context)

@login_required
@csrf_exempt
def update_invoice_field(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            invoice = get_object_or_404(Invoice, id=data.get('id'), user=request.user)
            field = data.get('field')
            value = data.get('value')
            
            if field == 'supplier':
                invoice.supplier = value
            elif field == 'total_ttc':
                invoice.total_ttc = float(value.replace(',', '.'))
            
            invoice.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'invalid method'}, status=405)

@login_required
def delete_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
    if invoice.pdf_file and os.path.isfile(invoice.pdf_file.path):
        os.remove(invoice.pdf_file.path)
    invoice.delete()
    messages.success(request, "Facture supprimée.")
    return redirect('upload_invoice')

@login_required
def export_excel(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    invoices = Invoice.objects.filter(user=request.user)
    if start_date: invoices = invoices.filter(date__gte=start_date)
    if end_date: invoices = invoices.filter(date__lte=end_date)
    
    df = pd.DataFrame(list(invoices.values('supplier', 'date', 'total_ttc', 'currency', 'tva')))
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=export_compta.xlsx'
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return response