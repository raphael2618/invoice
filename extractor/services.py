import google.generativeai as genai
import os
import json
from django.conf import settings

# Configuration de l'API avec la clé du fichier .env
genai.configure(api_key=os.getenv("AIzaSyBrlJr2MP9xi5ZGmJVGdWQ3B28iAGElzJQ"))

def extract_invoice_data(uploaded_file):
    """
    Analyse réelle du fichier par Gemini 2.5 Flash.
    """
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    # Lecture du contenu du fichier (PDF ou Image)
    file_bytes = uploaded_file.read()
    
    prompt = """
    Analyse cette facture et extrait les données suivantes en JSON pur :
    {
        "supplier": "nom du fournisseur",
        "date": "YYYY-MM-DD",
        "total_ttc": montant_total_nombre,
        "currency": "EUR",
        "tva": montant_tva_nombre
    }
    Réponds uniquement avec le JSON, sans texte autour.
    """

    try:
        # Envoi à l'IA
        response = model.generate_content([
            prompt,
            {"mime_type": uploaded_file.content_type, "data": file_bytes}
        ])
        
        # Nettoyage du formatage Markdown si présent
        clean_text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_text)

    except Exception as e:
        print(f"Erreur d'extraction : {e}")
        # Retour par défaut neutre en cas de problème
        return {
            "supplier": "Non identifié",
            "date": "2026-01-01",
            "total_ttc": 0.0,
            "currency": "EUR",
            "tva": 0.0
        }