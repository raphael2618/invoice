from django.db import models
from django.contrib.auth.models import User

class Invoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="invoices")
    supplier = models.CharField(max_length=255)
    date = models.DateField()
    total_ttc = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="EUR")
    tva = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pdf_file = models.FileField(upload_to='invoices/')
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=100, default="Divers")

    def __str__(self):
        return f"{self.supplier} - {self.total_ttc} {self.currency}"

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items")
    description = models.CharField(max_length=255)
    quantity = models.IntegerField(default=1)
    price_unit = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.description} x {self.quantity}"