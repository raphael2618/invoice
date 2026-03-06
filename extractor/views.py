from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.http import HttpResponse
from .models import Invoice
from .services import extract_invoice_data
from django.db.models import Sum
from django.db.models.functions import TruncMonth
import json
import pandas as pd

# --- NOUVELLE VUE : INSCRIPTION ---
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Connecte l'utilisateur direct après inscription
            return redirect('upload_invoice')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def upload_invoice(request):
    if request.method == 'POST' and request.FILES.get('file'):
        data = extract_invoice_data(request.FILES['file'])
        Invoice.objects.create(
            user=request.user,
            supplier=data.get('supplier'),
            date=data.get('date'),
            total_ttc=data.get('total_ttc'),
            currency=data.get('currency'),
            tva=data.get('tva'),
            pdf_file=request.FILES['file']
        )
        return redirect('upload_invoice')

    user_invoices = Invoice.objects.filter(user=request.user)
    monthly_stats = user_invoices.annotate(month=TruncMonth('date')).values('month').annotate(total=Sum('total_ttc')).order_by('month')
    supplier_stats = user_invoices.values('supplier').annotate(total=Sum('total_ttc')).order_by('-total')[:5]

    context = {
        'invoices': user_invoices.order_by('-created_at'),
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
def delete_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
    invoice.delete()
    return redirect('upload_invoice')

@login_required
def export_excel(request):
    invoices = Invoice.objects.filter(user=request.user).values('supplier', 'date', 'total_ttc', 'currency', 'tva')
    df = pd.DataFrame(list(invoices))
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=export_compta.xlsx'
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return response