import google.generativeai as genai
import os
import json
from django.conf import settings

# Configuration Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def extract_invoice_data(uploaded_file):
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    # IMPORTANT : On lit les bytes du fichier
    file_bytes = uploaded_file.read()
    
    prompt = """
    Extraire les infos de cette facture en JSON :
    {
        "supplier": "nom",
        "date": "YYYY-MM-DD",
        "total_ttc": nombre,
        "currency": "EUR",
        "tva": nombre
    }
    Répondre UNIQUEMENT en JSON.
    """

    try:
        response = model.generate_content([
            prompt,
            {"mime_type": uploaded_file.content_type, "data": file_bytes}
        ])
        
        # Nettoyage du JSON
        clean_text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_text)
    except Exception as e:
        print(f"Erreur Gemini: {e}")
        return {"supplier": "Erreur", "date": "2026-01-01", "total_ttc": 0, "currency": "EUR", "tva": 0}