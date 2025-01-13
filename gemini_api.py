import streamlit as st
import google.generativeai as genai

ma_cle_secrete = st.secrets["GEMINI_API_KEY"] #Récupération de la clé API
genai.configure(api_key=ma_cle_secrete) # Configuration de la clé API
model_api = genai.GenerativeModel('gemini-1.5-flash')
