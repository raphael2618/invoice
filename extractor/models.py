from django.db import models
from django.contrib.auth.models import User

class Invoice(models.Model):
    # Le lien magique : chaque facture appartient à UN utilisateur
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="invoices")
    
    supplier = models.CharField(max_length=255)
    date = models.DateField()
    total_ttc = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="EUR")
    tva = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pdf_file = models.FileField(upload_to='invoices/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.supplier} - {self.total_ttc} {self.currency} ({self.user.username})"