from flask import Flask, jsonify
import cloudscraper
from bs4 import BeautifulSoup
import vercel_wsgi

app = Flask(__name__)

@app.route('/lancamentos', methods=['GET'])
def get_lancamentos():
    url = "https://animefire.plus/"
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url)

    if response.status_code != 200:
        return jsonify({"error": "Não foi possível acessar o site."}), 500

    soup = BeautifulSoup(response.text, 'html.parser')
    item_elements = soup.select("div.divArticleLancamentos")
    item_info_list = []

    for item in item_elements:
        capa = item.select_one("img").get("data-src", "")
        link = item.select_one("a").get("href", "")
        nome = item.select_one("h3.animeTitle").text.strip()

        item_info_list.append({
            "capa": capa,
            "link": link,
            "nome": nome
        })

    return jsonify(item_info_list)
