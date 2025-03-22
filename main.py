from flask import Flask, jsonify, render_template_string, request
import json
import requests

app = Flask(__name__)

# Nome do arquivo JSON local
arquivo_json = "filmes.json"

# Chave da API do TMDB (substitua pela sua chave)
TMDB_API_KEY = "e83f31e1c568e9c4c7ed9f9fea0cd541"  # Substitua pela sua chave
TMDB_BASE_URL = "https://api.themoviedb.org/3"

# Função para ler e retornar os dados do JSON local
def ler_filmes(arquivo):
    try:
        with open(arquivo, "r", encoding="utf-8") as file:
            filmes = json.load(file)
            return filmes
    except Exception as e:
        return {"erro": f"Erro ao ler o arquivo: {e}"}

# Função para buscar detalhes de um filme no TMDB por título
def buscar_filme_no_tmdb(titulo):
    url = f"{TMDB_BASE_URL}/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": titulo,
        "language": "pt-BR"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        dados = response.json()
        if dados.get("results"):
            return dados["results"][0]  # Retorna o primeiro resultado
        return None
    except requests.exceptions.RequestException as e:
        return None

# Função para buscar detalhes completos de um filme no TMDB
def buscar_detalhes_filme(filme_id):
    url = f"{TMDB_BASE_URL}/movie/{filme_id}"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "pt-BR"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return None

# Função para buscar créditos de um filme no TMDB
def buscar_creditos_filme(filme_id):
    url = f"{TMDB_BASE_URL}/movie/{filme_id}/credits"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "pt-BR"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return None

# Função para buscar detalhes de uma pessoa no TMDB
def buscar_detalhes_pessoa(pessoa_id):
    url = f"{TMDB_BASE_URL}/person/{pessoa_id}"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "pt-BR"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return None

# Função para atualizar os filmes locais com informações do TMDB
def atualizar_filmes_com_tmdb(filmes):
    for filme in filmes:
        titulo = filme.get("titulo")
        if titulo:
            dados_tmdb = buscar_filme_no_tmdb(titulo)
            if dados_tmdb:
                filme_id = dados_tmdb.get("id")
                detalhes_filme = buscar_detalhes_filme(filme_id)
                creditos_filme = buscar_creditos_filme(filme_id)

                if detalhes_filme and creditos_filme:
                    # Busca diretores, roteiristas e elenco
                    diretores = [pessoa["name"] for pessoa in creditos_filme.get("crew", []) if pessoa["job"] == "Director"]
                    roteiristas = [pessoa["name"] for pessoa in creditos_filme.get("crew", []) if pessoa["job"] == "Screenplay"]
                    elenco = [{"nome": pessoa["name"], "personagem": pessoa["character"], "foto": f"https://image.tmdb.org/t/p/w500{pessoa['profile_path']}" if pessoa.get("profile_path") else None} for pessoa in creditos_filme.get("cast", [])[:5]]  # Limita a 5 atores

                    # Atualiza as informações do filme
                    player = filme.get("player", "")  # Preserva o campo "player"
                    filme.update({
                        "id": filme_id,
                        "titulo": detalhes_filme.get("title"),
                        "ano": detalhes_filme.get("release_date", "").split("-")[0] if detalhes_filme.get("release_date") else "N/A",
                        "generos": ", ".join([g["name"] for g in detalhes_filme.get("genres", [])]),
                        "sinopse": detalhes_filme.get("overview"),
                        "avaliacao": detalhes_filme.get("vote_average"),
                        "duracao": detalhes_filme.get("runtime"),
                        "diretores": diretores,
                        "roteiristas": roteiristas,
                        "elenco": elenco,
                        "poster": f"https://image.tmdb.org/t/p/w500{detalhes_filme.get('poster_path')}" if detalhes_filme.get("poster_path") else None,
                        "player": player  # Mantém o campo "player" original
                    })
    return filmes

# Rota principal (documentação)
@app.route('/')
def documentacao():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>SphereAPI - Documentação</title>
    </head>
    <body>
        <h1>SphereAPI</h1>
        <p>Bem-vindo à SphereAPI, sua API de filmes!</p>
    </body>
    </html>
    """)

# Rota para obter os filmes locais atualizados com informações do TMDB
@app.route('/filmes', methods=['GET'])
def get_filmes():
    filmes = ler_filmes(arquivo_json)
    if "erro" in filmes:
        return jsonify(filmes), 500

    # Atualiza os filmes com informações do TMDB
    filmes_atualizados = atualizar_filmes_com_tmdb(filmes)
    return jsonify({"filmes": filmes_atualizados})

# Rota para pesquisar filmes locais
@app.route('/filmes/search', methods=['GET'])
def search_filmes():
    filmes = ler_filmes(arquivo_json)
    if "erro" in filmes:
        return jsonify(filmes), 500

    titulo = request.args.get('title', '').lower().strip('"\'')
    id_filme = request.args.get('id', type=int)

    resultados = []
    for filme in filmes:
        if id_filme is not None and filme.get('id') != id_filme:
            continue
        if titulo and titulo not in filme.get('titulo', '').lower():
            continue
        resultados.append(filme)

    return jsonify({"filmes": resultados})

# Rota para buscar filmes no TMDB por título
@app.route('/tmdb/search', methods=['GET'])
def search_tmdb():
    titulo = request.args.get('title', '').strip()
    if not titulo:
        return jsonify({"erro": "O parâmetro 'title' é obrigatório"}), 400

    url = f"{TMDB_BASE_URL}/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": titulo,
        "language": "pt-BR"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        dados = response.json()

        filmes = []
        for filme in dados.get("results", []):
            filme_id = filme.get("id")
            detalhes_filme = buscar_detalhes_filme(filme_id)
            creditos_filme = buscar_creditos_filme(filme_id)

            if detalhes_filme and creditos_filme:
                diretores = [pessoa["name"] for pessoa in creditos_filme.get("crew", []) if pessoa["job"] == "Director"]
                roteiristas = [pessoa["name"] for pessoa in creditos_filme.get("crew", []) if pessoa["job"] == "Screenplay"]
                elenco = [{"nome": pessoa["name"], "personagem": pessoa["character"], "foto": f"https://image.tmdb.org/t/p/w500{pessoa['profile_path']}" if pessoa.get("profile_path") else None} for pessoa in creditos_filme.get("cast", [])[:5]]

                filmes.append({
                    "id": filme_id,
                    "titulo": detalhes_filme.get("title"),
                    "ano": detalhes_filme.get("release_date", "").split("-")[0] if detalhes_filme.get("release_date") else "N/A",
                    "generos": ", ".join([g["name"] for g in detalhes_filme.get("genres", [])]),
                    "sinopse": detalhes_filme.get("overview"),
                    "avaliacao": detalhes_filme.get("vote_average"),
                    "duracao": detalhes_filme.get("runtime"),
                    "diretores": diretores,
                    "roteiristas": roteiristas,
                    "elenco": elenco,
                    "poster": f"https://image.tmdb.org/t/p/w500{detalhes_filme.get('poster_path')}" if detalhes_filme.get("poster_path") else None
                })

        return jsonify({"filmes": filmes})
    except requests.exceptions.RequestException as e:
        return jsonify({"erro": f"Erro ao buscar no TMDB: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
