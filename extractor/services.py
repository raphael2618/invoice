import google.generativeai as genai
import json
import gspread
import re
import os
from google.oauth2.service_account import Credentials
from .models import Facture
from dotenv import load_dotenv

# Chargement de la clé API depuis le fichier .env
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def analyser_facture_ai(file_path):
    try:
        # UTILISATION DU MODÈLE 2.5 FLASH DÉTECTÉ DANS TON DIAGNOSTIC
        model = genai.GenerativeModel('gemini-2.5-flash') 
        
        prompt = """
        Analyse cette facture et renvoie UNIQUEMENT un objet JSON valide :
        {
          "fournisseur": "nom du vendeur",
          "date": "YYYY-MM-DD",
          "total_ttc": 0.00,
          "tva": 0.00,
          "devise": "EUR"
        }
        Ne réponds rien d'autre que le JSON.
        """
        
        # Envoi du fichier à Gemini
        sample_file = genai.upload_file(path=file_path)
        response = model.generate_content([prompt, sample_file])
        
        # Nettoyage pour extraire le JSON même s'il y a du texte autour
        raw_text = response.text.strip()
        json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        
        if json_match:
            data = json.loads(json_match.group())
        else:
            raise ValueError("L'IA n'a pas renvoyé un format JSON valide.")

        # Sauvegarde dans ta base SQLite locale
        facture_obj = Facture.objects.create(
            fournisseur=data.get('fournisseur', 'Inconnu'),
            date_facture=data.get('date'),
            total_ttc=data.get('total_ttc', 0.00),
            tva=data.get('tva', 0.00),
            devise=data.get('devise', 'EUR'),
            fichier_pdf=file_path
        )
        print(f"✅ Succès : {facture_obj.fournisseur} enregistré.")
        return facture_obj

    except Exception as e:
        print(f"❌ Erreur Gemini : {e}")
        raise e

def envoyer_vers_sheet(facture_obj):
    try:
        # Vérifie que credentials.json est bien à la racine de ton projet
        SERVICE_ACCOUNT_FILE = 'credentials.json'
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
        client = gspread.authorize(creds)

        # Ouvre ton fichier Google Sheet (doit être nommé 'facture')
        spreadsheet = client.open('facture').sheet1
        
        row = [
            facture_obj.date_upload.strftime("%d/%m/%Y"), 
            facture_obj.fournisseur, 
            str(facture_obj.date_facture), 
            float(facture_obj.tva), 
            float(facture_obj.total_ttc), 
            facture_obj.devise
        ]
        
        spreadsheet.append_row(row)
        print("🚀 Données envoyées à Google Sheets !")
    except Exception as e:
        print(f"❌ Erreur Sheets : {e}")