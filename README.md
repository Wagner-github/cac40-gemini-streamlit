# cac40-gemini-streamlit
Analyse Financière avec Streamlit et Gemini

Ce projet est une application Streamlit permettant d'analyser des données financières du CAC 40 en utilisant l'API Yahoo Finance et Google Gemini pour des résumés automatisés d'articles d'actualités financières.

Fonctionnalités

Sélection d'une entreprise du CAC 40 : Choix d'une entreprise à partir d'une liste déroulante.

Visualisation des données financières : Graphique de l'évolution du prix des actions et indicateurs clés.

Scraping des actualités : Récupération des articles récents via Boursorama.

Résumé automatisé avec Gemini : Résumé des articles collectés via l'API Gemini.

Prérequis

Python 3.8+

Librairies Python : streamlit, yfinance, pandas, requests, beautifulsoup4, google.generativeai, python-dotenv

Installation

Cloner ce dépôt :

git clone <URL_du_repo>

Installer les dépendances :

pip install -r requirements.txt

Créer un fichier .env à la racine du projet et y ajouter la clé API Gemini :

GEMINI_API_KEY=VotreCléAPI

Lancer l'application

streamlit run app.py

Structure du projet

app.py : Script principal de l'application.

.env : Fichier contenant la clé API (non partagé dans le repo public).

requirements.txt : Liste des dépendances.

Utilisation

Choisissez une entreprise et une période.

Visualisez les données de marché.

(Optionnel) Saisissez une date spécifique pour obtenir des articles d'actualités.

L'application affiche les données et génère un résumé des articles collectés.

Contributions

Les contributions sont les bienvenues ! Merci de bien commenter le code et de suivre la structure existante.

Licence

Ce projet est sous licene MT







