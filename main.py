import cloudscraper
from bs4 import BeautifulSoup
import html
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, jsonify

app = Flask(__name__)

# Inicializa o cloudscraper
scraper = cloudscraper.create_scraper()

# Variável global para armazenar os filmes em cache
filmes_cache = None

def carregar_filmes():
    global filmes_cache
    url = "https://visioncine-1.com.br/movies"
    
    try:
        response = scraper.get(url)
        response.encoding = 'utf-8'

        if response.status_code != 200:
            print("Erro ao carregar os filmes.")
            return []

        soup = BeautifulSoup(response.content, "html.parser")
        filmes = soup.find_all("div", class_="swiper-slide item poster")
        filmes_info = []

        for filme in filmes:
            titulo_tag = filme.find("h6")
            titulo = titulo_tag.text.strip() if titulo_tag else "Desconhecido"

            ano_tag = filme.find("span", string=lambda x: x and "2025" in x)
            ano = ano_tag.text.strip() if ano_tag else "Desconhecido"

            imagem_tag = filme.find("div", class_="content")
            imagem = imagem_tag["style"].split("url(")[1].split(")")[0] if imagem_tag else "Imagem não disponível"

            link_assistir_tag = filme.find("a", href=True)
            link_assistir = link_assistir_tag["href"] if link_assistir_tag else "Link não disponível"

            filmes_info.append({
                "id": len(filmes_info) + 1,
                "titulo": html.unescape(titulo),
                "ano": html.unescape(ano),
                "imagem": imagem,
                "link_assistir": link_assistir
            })

        print(f"Carregados {len(filmes_info)} filmes.")
        filmes_cache = filmes_info
        return filmes_info
    except Exception as e:
        print(f"Erro ao carregar filmes: {str(e)}")
        return []

def pegar_detalhes_do_filme(filme):
    url_filme = filme["link_assistir"]

    if url_filme == "Link não disponível":
        return {"error": "Link de assistir não disponível."}

    try:
        # Primeira requisição: página de detalhes do filme
        print(f"Fazendo requisição para a página de detalhes: {url_filme}")
        response = scraper.get(url_filme)
        response.encoding = 'utf-8'

        if response.status_code != 200:
            print(f"Erro ao acessar a página do filme. Status code: {response.status_code}")
            return {"error": "Erro ao acessar a página do filme."}

        soup = BeautifulSoup(response.content, "html.parser")

        titulo = soup.select_one("h1.fw-bolder.mb-0")
        titulo = titulo.text.strip() if titulo else "Título não disponível"

        log_info = soup.select_one("p.log")
        if log_info:
            spans = log_info.find_all("span")
            if len(spans) >= 3:
                duracao = spans[0].text.strip() if spans[0] else "Duração não disponível"
                ano = spans[1].text.strip() if spans[1] else "Ano não disponível"
                classificacao = spans[2].text.strip() if spans[2] else "Classificação não disponível"
            else:
                duracao = "Duração não disponível"
                ano = "Ano não disponível"
                classificacao = "Classificação não disponível"
        else:
            duracao = "Duração não disponível"
            ano = "Ano não disponível"
            classificacao = "Classificação não disponível"

        imdb = soup.select_one("p.log > span:nth-of-type(5)")
        imdb = imdb.text.strip() if imdb else "IMDb não disponível"

        sinopse = soup.select_one("p.small.linefive")
        sinopse = sinopse.text.strip() if sinopse else "Sinopse não disponível"

        generos = soup.select_one("p.lineone > span:nth-of-type(2)")
        generos = ", ".join([span.text.strip() for span in generos.select("span")]) if generos else "Gêneros não disponíveis"

        qualidade = soup.select_one("p.log > span:nth-of-type(4)")
        qualidade = qualidade.text.strip() if qualidade else "Qualidade não disponível"

        # Extrair o link do botão "ASSISTIR"
        link_assistir = soup.select_one("a.btn.free.fw-bold:has(i.far.fa-play)")
        link_assistir = link_assistir["href"] if link_assistir else "Link de assistir não disponível"

        # Segunda requisição: página do player
        if link_assistir != "Link de assistir não disponível":
            print(f"Fazendo requisição para a página do player: {link_assistir}")
            response_player = scraper.get(link_assistir)
            response_player.encoding = 'utf-8'

            if response_player.status_code != 200:
                print(f"Erro ao acessar a página do player. Status code: {response_player.status_code}")
                return {"error": "Erro ao acessar a página do player."}

            # Extrair o link do player
            link_player = extrair_link_player(response_player.text)
        else:
            link_player = "Link do player não encontrado."

        return {
            "id": filme["id"],
            "titulo": html.unescape(titulo),
            "ano": html.unescape(ano),
            "duracao": html.unescape(duracao),
            "classificacao": html.unescape(classificacao),
            "imdb": html.unescape(imdb),
            "sinopse": html.unescape(sinopse),
            "generos": html.unescape(generos),
            "qualidade": html.unescape(qualidade),
            "player": link_player
        }
    except Exception as e:
        print(f"Erro ao obter detalhes do filme {filme['titulo']}: {str(e)}")
        return {
            "id": filme["id"],
            "titulo": filme["titulo"],
            "error": f"Erro ao obter detalhes: {str(e)}"
        }

def extrair_link_player(html_content):
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        scripts = soup.find_all("script")

        for script in scripts:
            script_content = script.string
            if script_content and "initializePlayer" in script_content:
                match = re.search(r"initializePlayer\('([^']+)'", script_content)
                if match:
                    return match.group(1)

        return "Link do player não encontrado."
    except Exception as e:
        print(f"Erro ao extrair link do player: {str(e)}")
        return "Erro ao extrair link do player"

def atualizar_filmes():
    global filmes_cache
    filmes = carregar_filmes()
    
    if not filmes:
        return filmes_cache or []
    
    detalhes_filmes = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(pegar_detalhes_do_filme, filme) for filme in filmes]
        for future in as_completed(futures):
            detalhes_filmes.append(future.result())
    
    filmes_cache = detalhes_filmes
    return detalhes_filmes

# Rotas da API
@app.route('/filmes', methods=['GET'])
def get_filmes():
    if filmes_cache is None:
        atualizar_filmes()
    return jsonify(filmes_cache or [])

@app.route('/filmes/<int:filme_id>', methods=['GET'])
def get_filme(filme_id):
    if filmes_cache is None:
        atualizar_filmes()
    
    filme = next((f for f in (filmes_cache or []) if f.get('id') == filme_id), None)
    if filme:
        return jsonify(filme)
    else:
        return jsonify({"error": "Filme não encontrado"}), 404

@app.route('/atualizar', methods=['GET'])
def atualizar():
    try:
        filmes = atualizar_filmes()
        return jsonify({
            "status": "success",
            "message": f"Filmes atualizados. Total: {len(filmes)}",
            "filmes": filmes
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    # Atualiza os filmes ao iniciar o servidor
    atualizar_filmes()
    # Inicia o servidor Flask
    app.run(host='0.0.0.0', port=5000, debug=True)()
