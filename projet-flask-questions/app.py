import os
import google.generativeai as genai
from flask import Flask, request, render_template, flash # flash est optionnel pour des messages plus avancés
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

app = Flask(__name__)
# Optionnel: Configurer une clé secrète pour utiliser flash (messages éphémères)
# app.secret_key = os.urandom(24) # Génère une clé aléatoire

# --- Configuration de l'API Google Gemini ---
api_key = os.getenv("GOOGLE_API_KEY")
model = None
model_name = 'models/gemini-1.5-flash-latest' # Ou un autre modèle de votre choix

if not api_key:
    print("ERREUR: La variable d'environnement GOOGLE_API_KEY n'est pas définie.")
    print("Veuillez créer un fichier .env avec GOOGLE_API_KEY=VOTRE_CLE")
else:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        print(f"Modèle Gemini '{model_name}' initialisé avec succès.")
    except Exception as e:
        print(f"ERREUR lors de l'initialisation du modèle Gemini: {e}")
        model = None # Empêcher l'utilisation si l'initialisation échoue
# -------------------------------------------

@app.route('/', methods=['GET', 'POST'])
def index():
    questions_generees = None
    texte_original = ""
    erreur = None

    if model is None:
         erreur = "Erreur critique: Le modèle de génération n'a pas pu être initialisé. Vérifiez la clé API et la configuration."
         # Pas besoin d'aller plus loin si le modèle n'est pas prêt
         return render_template('index.html', erreur=erreur)

    if request.method == 'POST':
        texte_original = request.form.get('texte_enseignant')

        if not texte_original or not texte_original.strip():
            erreur = "Veuillez fournir un texte source."
        else:
            print(f"--- Réception du texte - Lancement de la génération avec '{model_name}' ---")
            # Définir le Prompt
            prompt = f"""
            أنت مساعد تعليمي متخصص في اللغة العربية. مهمتك هي قراءة النص التالي الذي قدمه المعلم وإنشاء 5 أسئلة **مفتوحة** بناءً عليه.
            يجب أن تتطلب هذه الأسئلة تفكيرًا وفهمًا للنص، وليس مجرد استرجاع مباشر للمعلومات.
            ركز على الأسباب، النتائج، المقارنات، أو التطبيقات المحتملة المذكورة أو التي يمكن استنتاجها من النص.
            تجنب الأسئلة التي يمكن الإجابة عليها بـ "نعم" أو "لا" أو بكلمة واحدة.

            النص المقدم من المعلم:
            ---
            {texte_original}
            ---

            الأسئلة المقترحة (اكتب 5 أسئلة مفتوحة هنا):
            """

            try:
                # Appeler l'API Gemini
                response = model.generate_content(prompt)

                # Traiter la réponse
                if response and hasattr(response, 'text') and response.text:
                    questions_generees = response.text.strip()
                    print("--- Questions générées avec succès ---")
                else:
                    erreur = "La génération de questions a échoué ou la réponse est vide."
                    print(f"--- Échec de la génération - Réponse reçue: {response} ---")
                    # Essayer d'obtenir plus de détails sur l'échec (sécurité, etc.)
                    try:
                        feedback = response.prompt_feedback
                        candidates = response.candidates
                        if feedback:
                            erreur += f" Feedback: {feedback}"
                        if candidates and candidates[0].finish_reason != 'STOP':
                             erreur += f" Raison: {candidates[0].finish_reason}. Sécurité: {candidates[0].safety_ratings}"
                    except Exception:
                         pass # Ignorer si les détails ne sont pas accessibles

            except Exception as e:
                erreur = f"Une erreur technique est survenue lors de l'appel à l'API : {e}"
                print(f"--- Erreur API : {e} ---")

    # Renvoyer le template avec les données (même pour GET initial)
    return render_template('index.html',
                           questions_generees=questions_generees,
                           texte_original=texte_original,
                           erreur=erreur)

if __name__ == '__main__':
    # debug=True recharge automatiquement si le code change et donne plus d'infos en cas d'erreur
    # Mettre debug=False en production !
    # host='0.0.0.0' rend l'app accessible depuis d'autres machines sur le réseau
    app.run(debug=True, host='0.0.0.0', port=5000)

