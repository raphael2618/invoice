import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import random
from datetime import datetime

def generate_fake_invoice(filename):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # Liste de fournisseurs pour varier les tests
    suppliers = ["TechMarket", "Boulangerie Paris", "Station Total", "Amazon Business", "Ramy Levy"]
    supplier = random.choice(suppliers)
    
    # Infos de la facture
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, f"FACTURE : {supplier}")
    
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 70, f"Date: {datetime.now().strftime('%d/%m/%Y')}")
    c.drawString(50, height - 85, f"Numéro: INV-{random.randint(1000, 9999)}")

    # Corps de la facture
    c.line(50, height - 120, 550, height - 120)
    c.drawString(60, height - 135, "Article")
    c.drawString(400, height - 135, "Prix")
    c.line(50, height - 145, 550, height - 145)

    items = [("Clavier RGB", 45.00), ("Café Grain", 12.50), ("Ecran 24p", 120.00), ("Câble HDMI", 8.90)]
    y = height - 165
    subtotal = 0
    
    for _ in range(random.randint(1, 3)):
        name, price = random.choice(items)
        c.drawString(60, y, name)
        c.drawString(400, y, f"{price:.2f} EUR")
        subtotal += price
        y -= 20

    # Calculs
    tva = subtotal * 0.20
    total_ttc = subtotal + tva

    c.line(350, y - 10, 550, y - 10)
    c.drawString(360, y - 30, f"Total HT: {subtotal:.2f} EUR")
    c.drawString(360, y - 50, f"TVA (20%): {tva:.2f} EUR")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(360, y - 75, f"TOTAL TTC: {total_ttc:.2f} EUR")

    c.save()
    print(f"✅ Facture générée : {filename}")

if __name__ == "__main__":
    # Génère 3 factures pour commencer
    for i in range(3):
        generate_fake_invoice(f"facture_test_{i+1}.pdf")