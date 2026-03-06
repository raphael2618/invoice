import google.generativeai as genai
import PIL.Image
import pandas as pd
import json

# Ta clé récupérée
API_KEY = "AIzaSyBKRrMaXX387C_haOvH59zs6PfPh-Z49f8"
genai.configure(api_key="AIzaSyBKRrMaXX387C_haOvH59zs6PfPh-Z49f8")


def traiter_et_sauvegarder(chemin_image):
    model = genai.GenerativeModel("gemini-1.5-flash")
    img = PIL.Image.open(chemin_image)

    prompt = """
    Analyse cette facture. Extrais les infos en JSON uniquement :
    {"fournisseur": "nom", "date": "JJ/MM/AAAA", "total_ttc": 0.00, "devise": "EUR"}
    """

    # L'IA analyse l'image
    response = model.generate_content([prompt, img])

    # On nettoie la réponse pour avoir du JSON pur
    donnees_json = response.text.replace("```json", "").replace("```", "").strip()
    data = json.loads(donnees_json)

    # On transforme en tableau Excel (Pandas)
    df = pd.DataFrame([data])
    df.to_excel("comptabilite.xlsx", index=False)

    print("✅ Succès ! Le fichier 'comptabilite.xlsx' a été généré.")


# TESTE ICI : Mets une photo de ticket dans le même dossier et change le nom
# traiter_et_sauvegarder('ton_ticket.jpg')
