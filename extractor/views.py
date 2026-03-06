from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Invoice
from .services import extract_invoice_data
from django.db.models import Sum
from django.db.models.functions import TruncMonth
import json
import pandas as pd

@login_required
def upload_invoice(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        
        # Extraction réelle via Gemini
        data = extract_invoice_data(uploaded_file)
        
        # Sauvegarde en base de données
        Invoice.objects.create(
            user=request.user,
            supplier=data.get('supplier', 'Inconnu'),
            date=data.get('date', '2026-01-01'),
            total_ttc=data.get('total_ttc', 0),
            currency=data.get('currency', 'EUR'),
            tva=data.get('tva', 0),
            pdf_file=uploaded_file
        )
        return redirect('upload_invoice')

    # Statistiques pour le Dashboard
    user_invoices = Invoice.objects.filter(user=request.user)
    
    # Cards de résumé
    total_month = user_invoices.aggregate(Sum('total_ttc'))['total_ttc__sum'] or 0
    tva_month = user_invoices.aggregate(Sum('tva'))['tva__sum'] or 0
    count_month = user_invoices.count()

    # Données graphiques
    monthly_stats = user_invoices.annotate(month=TruncMonth('date')) \
        .values('month').annotate(total=Sum('total_ttc')).order_by('month')
    
    supplier_stats = user_invoices.values('supplier') \
        .annotate(total=Sum('total_ttc')).order_by('-total')[:5]

    context = {
        'invoices': user_invoices.order_by('-created_at'),
        'total_month': total_month,
        'tva_month': tva_month,
        'count_month': count_month,
        'monthly_labels': json.dumps([d['month'].strftime("%b %Y") for d in monthly_stats if d['month']]),
        'monthly_totals': json.dumps([float(d['total']) for d in monthly_stats]),
        'supplier_labels': json.dumps([d['supplier'] for d in supplier_stats]),
        'supplier_totals': json.dumps([float(d['total']) for d in supplier_stats]),
    }
    
    return render(request, 'extractor/upload.html', context)

@login_required
def export_excel(request):
    """Génère le fichier Excel pour l'utilisateur"""
    invoices = Invoice.objects.filter(user=request.user).values(
        'supplier', 'date', 'total_ttc', 'currency', 'tva'
    )
    df = pd.DataFrame(list(invoices))
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=export_factures.xlsx'
    
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    
    return response