import streamlit as st
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
import requests
from markdown import Markdown 
import textwrap
import google.generativeai as genai


links=[]
# Formatage des valeurs à afficher
def format_value(value):
    suffixes = ["", "K", "M", "Md"]
    suffix_index = 0
    while value >= 1000 and suffix_index < len(suffixes) - 1:
        value /= 1000
        suffix_index += 1
    return f"${value:.1f}{suffixes[suffix_index]}"

def safe_format(value, fmt="{:.2f}", fallback="N/A"):
    try:
        return fmt.format(value) if value is not None else fallback
    except (ValueError, TypeError):
        return fallback

# fonction scraping generale
def scrape_page_recursive(ticker, url, reference_date, nbr_page=1):
    global links
    ticker_without_pa = ticker[:-3]
    # Mise à jour de l'URL avec la page actuelle
    url = f"https://www.boursorama.com/cours/analyses/1rP{ticker_without_pa}/page-{nbr_page}"

    try: # Envoi de la requête
        response = requests.get(url)
        response.raise_for_status()  # Affiche une erreur si la requête n'a pas fonctionné
        soup = BeautifulSoup(response.content, "html.parser")

        # Scraping des dates dans la page Bousorama
        span_tags = soup.find_all("span", class_="c-source__time")
        filtered_span_tags = [span for span in span_tags if ":" not in span.get_text(strip=True)]

        nbr_fresher_date = 0  # Nombre d'articles rplus récents trouvés

        # Traitement des dates
        for span in filtered_span_tags:
            raw_date = span.get_text(strip=True)
            try:
                scraped_date = datetime.strptime(raw_date, "%d.%m.%Y").date() # convertion dans le même format de date
                if scraped_date > reference_date:
                    nbr_fresher_date += 1
                    continue
                elif scraped_date == reference_date:
                    link_tag = span.find_previous("a")
                    if link_tag and link_tag.get("href"):
                        full_link = f"https://www.boursorama.com{link_tag['href']}"
                        links.append(full_link)
            except ValueError as e:
                st.error(f"Date non reconnue : {raw_date}, erreur : {e}")
    except requests.exceptions.RequestException as e :
         st.error(f"Erreur dans la requete web : {e}")

    # Condition pour passer à la page suivante
    if nbr_fresher_date >= 10:
        return scrape_page_recursive(ticker, url, reference_date, nbr_page + 1)
    #return

# fonction scrap des liens
def scrape_article(links):
    global text_to_save
    for link in links:
        try :
            response = requests.get(link)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            # Recherche de la div qui contient le contenu principal de l'article
            article = soup.find("div", class_="c-news-detail")

        # Si l'article est trouvé
            if article:
                # Extraire tout le texte et le contenu HTML
                text = article.get_text(separator="\n", strip=True)
                text_to_save.append(text)
            else:
               st.error(f"Aucun article trouvé pour {link}")
        except requests.exceptions.RequestException as e :
            st.error(f"Erreur dans la requete web : {e}")
            return
# fonction ecriture API Gemini
def generate_summary_from_text(text):
    prompt= f"résume ceci de maniére claire et concis en quelques points, et donne un résumé en début du texte : {text}"
    response= model_api.generate_content(prompt)

    if response.text : # S'assure que response contient un text
       return response.text  # Retourne la reponse de Gimini

    return st.error("Pas de résumé generer.") # Sinon, message d'erreur
