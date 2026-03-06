from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Invoice
from .services import extract_invoice_data # Ton service Gemini

@login_required
def upload_invoice(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        
        # 1. Appel à ton service Gemini
        data = extract_invoice_data(uploaded_file)
        
        # 2. Sauvegarde en base liée à l'utilisateur CONNECTÉ
        Invoice.objects.create(
            user=request.user,  # <--- CRUCIAL
            supplier=data.get('supplier'),
            date=data.get('date'),
            total_ttc=data.get('total_ttc'),
            currency=data.get('currency'),
            tva=data.get('tva'),
            pdf_file=uploaded_file
        )
        return redirect('upload_invoice')

    # 3. On ne récupère QUE les factures de l'utilisateur actuel
    invoices = Invoice.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'upload.html', {'invoices': invoices})