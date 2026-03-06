import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

try:
    print("--- Liste des modèles disponibles ---")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"Nom : {m.name}")
except Exception as e:
    print(f"Erreur lors de la liste : {e}")