import streamlit as st
import google.generativeai as genai
import os
from PIL import Image
from fpdf import FPDF
from datetime import datetime

# 1. CONFIGURATION DE L'INTERFACE MOBILE & THÈME PROFESSIONNEL HAUT DE GAMME
st.set_page_config(page_title="MecaVision Pro IA", page_icon="⚡", layout="centered")

# Design CSS Sombre Premium avec dégradés métalliques et boutons ergonomiques
st.markdown("""
    <style>
    .main { background-color: #0b0f19; color: #f3f4f6; }
    .stApp { background-color: #0b0f19; }
    h1 { color: #38bdf8; text-align: center; font-family: 'Arial Black', sans-serif; font-size: 26px; letter-spacing: 1px; }
    h3 { color: #94a3b8; text-align: center; font-size: 14px; margin-bottom: 25px; }
    .stButton>button { width: 100%; background: linear-gradient(90deg, #0284c7 0%, #0369a1 100%); color: white; border: none; border-radius: 10px; padding: 12px; font-weight: bold; font-size: 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.5); transition: 0.3s; }
    .stButton>button:hover { background: linear-gradient(90deg, #0369a1 0%, #0284c7 100%); cursor: pointer; }
    .css-145kmo2 { background-color: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155; }
    div.stSelectbox > div { background-color: #1e293b !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

# LOGO VISUEL ET TITRE DE L'APPLICATION
st.markdown("<div style='text-align: center; font-size: 50px; margin-bottom: -10px;'>⚡🔧⚙️</div>", unsafe_allow_html=True)
st.markdown("<h1>MECAVISION PRO IA</h1>", unsafe_allow_html=True)
st.markdown("<h3>L'Intelligence Artificielle Révolutionnaire pour la Maintenance Industrielle & Automobile</h3>", unsafe_allow_html=True)

# 2. GESTION DE L'HISTORIQUE EN MÉMOIRE (Session State)
if "historique_diagnostics" not in st.session_state:
    st.session_state.historique_diagnostics = []
if "current_report" not in st.session_state:
    st.session_state.current_report = None
if "current_lang_report" not in st.session_state:
    st.session_state.current_lang_report = None

# FONCTIONS TECHNIQUES (Nettoyage de texte et Génération du PDF)
def clean_text(text):
    return text.encode('latin-1', 'replace').decode('latin-1')

def generer_pdf(type_engin, type_analyse, langue, notes, diagnostic):
    pdf = FPDF()
    pdf.add_page()
    
    # En-tête Esthétique
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(2, 132, 199)
    pdf.cell(0, 10, clean_text("MECAVISION PRO IA - RAPPORT TECHNIQUE"), ln=True, align="C")
    pdf.ln(5)
    
    # Métadonnées d'intervention
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(50, 50, 50)
    date_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    pdf.cell(0, 6, clean_text(f"Date du diagnostic : {date_str}"), ln=True)
    pdf.cell(0, 6, clean_text(f"Type d'engin analysé : {type_engin}"), ln=True)
    pdf.cell(0, 6, clean_text(f"Type d'analyse : {type_analyse} | Langue : {langue}"), ln=True)
    pdf.cell(0, 6, clean_text(f"Notes complémentaires : {notes if notes else 'Aucune'}"), ln=True)
    pdf.ln(5)
    
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    # Contenu Principal
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 7, clean_text("ANALYSE DÉTAILLÉE ET PROTOCOLE DE RÉPARATION :"), ln=True)
    pdf.ln(2)
    
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, clean_text(diagnostic))
    
    # Clause de Sécurité Standard (Inspirée des règles SNIM / Mines Australie)
    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(220, 38, 38)
    pdf.multi_cell(0, 5, clean_text("AVERTISSEMENT SÉCURITÉ : Ce document est généré par un système IA de diagnostic multimodal. Avant toute intervention, appliquez scrupuleusement les procédures de consignation de l'entreprise (LOTO), portez vos EPI réglementaires et consultez les manuels officiels du constructeur."))
    
    return pdf.output()

# CONFIGURATION DE L'ACCÈS À L'IA GEMINI
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ Configuration requise : Ajoutez votre clé API sous le nom 'GEMINI_API_KEY' dans l'onglet Secrets de Replit.")
else:
    genai.configure(api_key=api_key)
    
    # 3. INTERFACE DE COMMANDE DE L'APPLICATION
    st.markdown("### 🛠️ Paramètres d'analyse")
    
    type_engin = st.selectbox(
        "Sélectionnez le type d'appareil ou engin :",
        ["Grue Mobile (Terex, Grove, Liebherr)", "Chariot Élévateur (Hyster, Cat, Toyota)", "Camion Poids Lourd / Tombereau", "Engin de Mine & Terrassement (Pelle, Dozer)", "Moteur Diesel Stationnaire / Générateur", "Automobile / Véhicule Léger"]
    )

    mode_analyse = st.radio("Sélectionnez le canal de détection :", ["📷 Panne Visuelle (Prendre une Photo / Importer)", "🔊 Panne Acoustique (Enregistrer un Bruit Moteur)"])

    fichier_analyse = None

    if mode_analyse == "📷 Panne Visuelle (Prendre une Photo / Importer)":
        source_image = st.radio("Source de la capture :", ["Appareil Photo (Direct)", "Galerie / Fichier"])
        if source_image == "Appareil Photo (Direct)":
            fichier_analyse = st.camera_input("Scanner le composant défectueux")
        else:
            fichier_analyse = st.file_uploader("Téléverser la photo de la panne", type=["jpg", "jpeg", "png"])
    else:
        source_audio = st.radio("Source du signal sonore :", ["Microphone (Direct)", "Fichier Audio"])
        if source_audio == "Microphone (Direct)":
            fichier_analyse = st.audio_input("Enregistrer le bruit suspect du moteur en fonctionnement")
        else:
            fichier_analyse = st.file_uploader("Téléverser le fichier audio", type=["mp3", "wav", "m4a"])

    # 4. MODULE DE TRADUCTION DE L'APPLICATION
    st.markdown("### 🌐 Langue du rapport technique")
    langue_cible = st.selectbox("Choisissez la langue de sortie du diagnostic :", ["Français", "Anglais (Standard Australien)", "Arabe (Classique)", "Hassanya (Mauritanie)"])

    notes = st.text_input("Symptômes observés (ex: baisse de pression hydraulique, sifflement au niveau du turbo, fumée opaque)")

    # ÉCHANGER AVEC L'IA LORS DU CLIC
    if st.button("🚀 EXÉCUTER LE DIAGNOSTIC ET CRÉER LE RAPPORT"):
        if fichier_analyse is None:
            st.warning("⚠️ Veuillez capturer une photo ou enregistrer un son avant de lancer l'analyse.")
        else:
            with st.spinner("MecaVision Pro analyse les fréquences acoustiques et éléments visuels..."):
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    if mode_analyse == "📷 Panne Visuelle (Prendre une Photo / Importer)":
                        image = Image.open(fichier_analyse)
                        contenu_ia = image
                    else:
                        audio_data = fichier_analyse.read()
                        contenu_ia = {
                            "mime_type": "audio/wav" if hasattr(fichier_analyse, 'name') and fichier_analyse.name.endswith('wav') else "audio/mp3",
                            "data": audio_data
                        }
                    
                    consignes_ia = f"""
                    Tu es un ingénieur en chef expert en mécanique industrielle, automobile et d'engins miniers lourds, formé selon les critères rigoureux de la SNIM et des compagnies minières australiennes.
                    Analyse ce fichier média pour l'engin suivant : {type_engin}.
                    Type d'analyse : {mode_analyse}.
                    Symptômes décrits : {notes}.
                    
                    Rédige l'intégralité de ta réponse en langue : {langue_cible}. Si la langue choisie est le Hassanya, utilise un vocabulaire mauritanien parlé tout en gardant les termes techniques clairs.
                    
                    Structure strictement ta réponse ainsi :
                    1. DIAGNOSTIC PRECIS : Identifiez précisément la panne (visuelle ou d'après le spectre sonore du bruit).
                    2. ORIGINE ET CAUSES DE LA PANNE : Pourquoi ce problème est survenu.
                    3. PROTOCOLE DE RÉPARATION : Guide d'action chronologique étape par étape pour remettre l'engin en état.
                    4. COMPOSANTS ET OUTILLAGE : Liste précise du matériel et des pièces de rechange à prévoir.
                    5. SÉCURITÉ INDUSTRIELLE : Consignes vitales à respecter sur le chantier pour cette intervention.
                    """
                    
                    response = model.generate_content([consignes_ia, contenu_ia])
                    
                    # Sauvegarde des résultats en session
                    st.session_state.current_report = response.text
                    st.session_state.current_lang_report = langue_cible
                    
                    # Ajout automatique à l'historique
                    diagnostic_sauvegarde = {
                        "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "engin": type_engin,
                        "mode": mode_analyse,
                        "langue": langue_cible,
                        "texte": response.text,
                        "notes": notes
                    }
                    st.session_state.historique_diagnostics.insert(0, diagnostic_sauvegarde)
                    
                except Exception as e:
                    st.error(f"Échec de l'analyse IA : {e}")

    # AFFICHAGE DU RAPPORT ACTIF ET OPTION TÉLÉCHARGEMENT PDF
    if st.session_state.current_report:
        st.success("✅ Analyse effectuée avec succès !")
        st.markdown(f"### 📋 Rapport Final ({st.session_state.current_lang_report})")
        st.write(st.session_state.current_report)
        
        # Génération dynamique du PDF
        pdf_bytes = generer_pdf(type_engin, mode_analyse, st.session_state.current_lang_report, notes, st.session_state.current_report)
