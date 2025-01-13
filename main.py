import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
from io import StringIO

from data import data_tickers
from fonctions import format_value, safe_format, scrape_page_recursive, scrape_article, generate_summary_from_text, links, text_to_save

st.link_button("🎯 Voir mon Portfolio", "https://jullienjeremy.notion.site/Bonjour-je-suis-Jeremy-Jullien-161909f0060e80f29683c272b92ca931?pvs=74")

# Utiliser StringIO pour convertir la chaîne en un fichier-like object
data_io = StringIO(data_tickers)

# Lire les données avec Pandas
df_chart = pd.read_csv(data_io)

st.title("Analyse financière")
st.subheader("Vision globale")
entreprise = st.selectbox("Choisissez l'entreprise :", df_chart["nom"].unique(), index=25, key="selectbox_entreprise")
period = st.selectbox("Choisissez la période :", ("1D", "5D", "1M", "6M", "YTD", "1Y", "5Y", "MAX"), index=7, key="selectbox_period")

# Analyse fine avec Gemini
st.subheader("Analyse fine avec Gemini")
st.text("Pour lancer l'analyse fine, merci de saisir une date, sinon, vider le cartouche et appuyer sur le bouton 'Entrer'.")
current_date = datetime.now().date()
st.caption = "Il n'a pas d'archives avant 2015."
user_date = st.text_input("Entrez une date (format: YYYY-MM-DD) :", "2024-12-02")

#lancer la machine
button = st.button("Entrer", key="button1")

#attribution du ticker de l'entreprise choisie
ticker = df_chart[df_chart["nom"] == entreprise]["ticker"].values[0]

# Date actuelle
current_date = datetime.now().date()


if button: # Vue des infos de bases
    if ticker:
        try:
            with st.spinner('Please wait...'):
                # Récupération des infos de l'entreprise grâce au ticker
                stock = yf.Ticker(ticker)
                info = stock.info

                st.subheader(f"{ticker} - {info.get('longName', 'N/A')}")

                 # Création du graphique
                period_map = { # Choix période et intervalle
                    "1D": ("1d", "1h"),
                    "5D": ("5d", "1d"),
                    "1M": ("1mo", "1d"),
                    "6M": ("6mo", "1wk"),
                    "YTD": ("ytd", "1mo"),
                    "1Y": ("1y", "1mo"),
                    "5Y": ("5y", "3mo"),
                    "MAX": ("max", "1mo")
                } # Mapping période et intervalle
                selected_period, interval = period_map.get(period, ("1mo", "1d"))
                history_data = stock.history(period=selected_period, interval=interval)

                chart_data = pd.DataFrame(history_data["Close"])
                st.line_chart(chart_data) # affichage du graphique

                col1, col2, col3 = st.columns(3) # Affichage du graphique
                # Infos stock
                stock_info = [
                    ("Stock Info", "Value"),
                    ("Country", info.get('country', 'N/A')),
                    ("Sector", info.get('sector', 'N/A')),
                    ("Industry", info.get('industry', 'N/A')),
                    ("Market Cap", format_value(info.get('marketCap'))),
                    ("Enterprise Value", format_value( info.get('enterpriseValue'))),
                    ("Employees", info.get('fullTimeEmployees', 'N/A'))
                ]

                df = pd.DataFrame(stock_info[1:], columns=stock_info[0]).astype(str)
                col1.dataframe(df, width=400, hide_index=True)

                # Informations relatives aux prix et à leurs évolutions
                price_info = [
                    ("Price Info", "Value"),
                    ("Current Price", safe_format(info.get('currentPrice'), fmt="${:.2f}")),
                    ("Previous Close", safe_format(info.get('previousClose'), fmt="${:.2f}")),
                    ("Day High", safe_format(info.get('dayHigh'), fmt="${:.2f}")),
                    ("Day Low", safe_format(info.get('dayLow'), fmt="${:.2f}")),
                    ("52 Week High", safe_format(info.get('fiftyTwoWeekHigh'), fmt="${:.2f}")),
                    ("52 Week Low", safe_format(info.get('fiftyTwoWeekLow'), fmt="${:.2f}"))
                ]

                df = pd.DataFrame(price_info[1:], columns=price_info[0]).astype(str)
                col2.dataframe(df, width=400, hide_index=True)

                # Metrics business
                biz_metrics = [
                    ("Business Metrics", "Value"),
                    ("EPS (FWD)", safe_format(info.get('forwardEps'))),
                    ("P/E (FWD)", safe_format(info.get('forwardPE'))),
                    ("PEG Ratio", safe_format(info.get('pegRatio'))),
                    ("Div Rate (FWD)", safe_format(info.get('dividendRate'), fmt="${:.2f}")),
                    ("Div Yield (FWD)", safe_format(info.get('dividendYield') * 100, fmt="{:.2f}%") if info.get('dividendYield') else 'N/A'),
                    ("Recommendation", info.get('recommendationKey', 'N/A').capitalize())
                ]

                df = pd.DataFrame(biz_metrics[1:], columns=biz_metrics[0]).astype(str)
                col3.dataframe(df, width=400, hide_index=True)

                history_data2 = stock.history(period="max")  # Récupérer toutes les données disponibles

                if not history_data2.empty:
                    # Convertir l'index en format 'YYYY-MM-DD' sans heure et fuseau horaire
                    history_data2.index = history_data2.index.date
                    if user_date: # Vérifier si la date saisie existe dans les données
                        st.subheader(f"Analyse fine de la date : {user_date}") # Sous-titre
                        try:
                            reference_date = pd.to_datetime(user_date).date()  # Convertir la date saisie en datetime.date
                            url = "" # L’URL est définie ici en prévision du scraping
                            if reference_date in history_data2.index:
                                selected_data = history_data2.loc[reference_date]
                                st.write(selected_data)
                                scrape_page_recursive(ticker, url, reference_date) # Fonction scraping des liens
                                if links: # Check le résultat du scraping de liens
                                    st.warning("ATTENTION  Ces données proviennent du site boursorama.com. Les informations vous sont résumées par une intelligence artificielle, rien de cela ne constitue des conseils financiers sous aucunes formes.", icon="⚠️")
                                    scrape_article(links) # Fonction scraping des articles
                                    if text_to_save: # Check le resultat du scraping d'articles
                                        text_to_summarize = " ".join(text_to_save) # On rassemble le texte de toutes les pages
                                        summarize_text_gemini = generate_summary_from_text(text_to_summarize) #Fonction de résumé par Gemini
                                        container = st.container(border=True) # Graphisme encadré
                                        container.write(summarize_text_gemini) # Affiche résumé dans l'encadré du container
                                        nbrlink = 0 # Compte les liens trouvés
                                        st.balloons() # Des ballons qui signifient l’affichage du résumé 
                                        for link in links :
                                            nbrlink += 1
                                            st.write(f"lien {nbrlink} : {link}") #Affiche le nombre de liens et les liens trouvés
                                        st.write(f"Nombre de liens trouvés : {nbrlink}")
                                else:
                                    st.error("La date saisie n'est pas ne contient pas d'article.")
                            else:
                                st.error("La date saisie n'est pas présente dans les données.")
                        except ValueError as e:
                            st.error(f"Le format de la date est incorrect. Veuillez entrer une date au format YYYY-MM-DD, Error: {e}")
                    else:
                        st.text('Pas de date dans le cartouche "Entrez une date (format: YYYY-MM-DD)":')
        except Exception as e:
                    st.exception(f"An error occurred: {e}")
