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

# Rota principal com documentação estilizada
@app.route('/')
def documentacao():
    doc_html = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SphereAPI - Documentação</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: 'Poppins', sans-serif;
                background: linear-gradient(135deg, #1a1a1a, #000);
                color: #fff;
                line-height: 1.6;
                padding: 20px;
            }

            .container {
                max-width: 800px;
                margin: 50px auto;
                padding: 30px;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 15px;
                backdrop-filter: blur(10px);
                box-shadow: 0 0 20px rgba(255, 0, 0, 0.5);
                border: 1px solid rgba(255, 255, 255, 0.1);
            }

            h1 {
                color: #fff;
                text-align: center;
                font-size: 3em;
                margin-bottom: 20px;
                font-weight: 600;
                background: linear-gradient(90deg, #ff0000, #ff6f00);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                animation: glow 2s infinite alternate;
            }

            @keyframes glow {
                0% {
                    text-shadow: 0 0 5px rgba(255, 0, 0, 0.7);
                }
                100% {
                    text-shadow: 0 0 20px rgba(255, 0, 0, 0.9);
                }
            }

            h2 {
                color: #ff0000;
                font-size: 1.8em;
                margin-top: 30px;
                margin-bottom: 15px;
                font-weight: 500;
                border-bottom: 2px solid #ff0000;
                padding-bottom: 5px;
            }

            p {
                font-size: 1.1em;
                margin-bottom: 20px;
            }

            code {
                background: rgba(255, 0, 0, 0.1);
                color: #ff0000;
                padding: 3px 8px;
                border-radius: 4px;
                font-family: 'Courier New', monospace;
                font-size: 0.95em;
            }

            a {
                color: #ff0000;
                text-decoration: none;
                transition: color 0.3s ease;
            }

            a:hover {
                color: #ff6f00;
            }

            ul {
                list-style-type: none;
                padding: 0;
            }

            li {
                margin: 10px 0;
                font-size: 1.1em;
            }

            pre {
                background: rgba(255, 0, 0, 0.1);
                padding: 15px;
                border-radius: 8px;
                color: #fff;
                overflow-x: auto;
                font-size: 0.95em;
                line-height: 1.5;
                margin: 20px 0;
            }

            .highlight {
                color: #ff0000;
                font-weight: bold;
            }

            .example-button {
                display: inline-block;
                margin-top: 20px;
                padding: 10px 20px;
                background: linear-gradient(90deg, #ff0000, #ff6f00);
                color: #fff;
                border: none;
                border-radius: 5px;
                font-size: 1em;
                cursor: pointer;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }

            .example-button:hover {
                transform: translateY(-3px);
                box-shadow: 0 5px 15px rgba(255, 0, 0, 0.4);
            }
        </style>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap" rel="stylesheet">
    </head>
    <body>
        <div class="container">
            <h1>SphereAPI</h1>
            <p>Bem-vindo à <span class="highlight">SphereAPI</span>, sua API de filmes! Abaixo estão os detalhes de como usar a API.</p>
            
            <h2>Rotas Disponíveis</h2>
            <ul>
                <li><strong>GET /filmes</strong>: Retorna a lista completa de filmes locais.</li>
                <li><strong>GET /filmes/search</strong>: Permite pesquisar filmes locais por título ou ID.</li>
                <li><strong>GET /tmdb/search</strong>: Busca filmes no TMDB por título.</li>
                <li><strong>GET /tmdb</strong>: Retorna uma lista de filmes populares do TMDB.</li>
            </ul>

            <h2>Exemplo de Uso</h2>
            <p>Para obter a lista de filmes locais, faça uma requisição GET para:</p>
            <code>GET /filmes</code>

            <p>Para pesquisar filmes locais por título ou ID, use:</p>
            <code>GET /filmes/search?title=Homem</code><br>
            <code>GET /filmes/search?id=1</code><br>
            <code>GET /filmes/search?title=Homem&id=1</code>

            <p>Para buscar filmes no TMDB por título, use:</p>
            <code>GET /tmdb/search?title=Homem</code>

            <p>Para obter filmes populares do TMDB, use:</p>
            <code>GET /tmdb</code>

            <h2>Resposta de Exemplo</h2>
            <pre>
{
    "filmes": [
        {
            "id": 634649,
            "titulo": "Homem-Aranha: Sem Volta para Casa",
            "ano": "2021",
            "genero": "Ação, Aventura, Ficção Científica",
            "sinopse": "Peter Parker é desmascarado e não consegue mais separar sua vida normal dos grandes riscos de ser um super-herói...",
            "avaliacao": 8.3,
            "producao": ["Marvel Studios", "Columbia Pictures"],
            "poster": "https://image.tmdb.org/t/p/w500/1g0dhYtq4irTY1GPXvft6k4YLjm.jpg"
        }
    ]
}
            </pre>

            <h2>Erros</h2>
            <p>Se ocorrer um erro ao ler o arquivo JSON, a API retornará:</p>
            <pre>
{
    "erro": "Erro ao ler o arquivo: [mensagem de erro]"
}
            </pre>

            <button class="example-button" onclick="window.location.href='/filmes'">Testar Rota /filmes</button>
        </div>
    </body>
    </html>
    """
    return render_template_string(doc_html)

# Rota para obter os filmes locais
@app.route('/filmes', methods=['GET'])
def get_filmes():
    filmes = ler_filmes(arquivo_json)
    if "erro" in filmes:
        return jsonify(filmes), 500
    return jsonify({"filmes": filmes})

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
            detalhes = buscar_detalhes_filme(filme.get("id"))
            if detalhes:
                filmes.append({
                    "id": filme.get("id"),
                    "titulo": filme.get("title"),
                    "ano": filme.get("release_date", "").split("-")[0] if filme.get("release_date") else "N/A",
                    "genero": ", ".join([str(g) for g in filme.get("genre_ids", [])]),
                    "sinopse": filme.get("overview"),
                    "avaliacao": detalhes.get("vote_average"),
                    "producao": [empresa.get("name") for empresa in detalhes.get("production_companies", [])],
                    "poster": f"https://image.tmdb.org/t/p/w500{filme.get('poster_path')}" if filme.get("poster_path") else None
                })

        return jsonify({"filmes": filmes})
    except requests.exceptions.RequestException as e:
        return jsonify({"erro": f"Erro ao buscar no TMDB: {e}"}), 500

# Rota para obter filmes populares do TMDB
@app.route('/tmdb', methods=['GET'])
def get_tmdb_populares():
    url = f"{TMDB_BASE_URL}/movie/popular"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "pt-BR",
        "page": 1  # Página de resultados (pode ser ajustada)
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        dados = response.json()

        filmes = []
        for filme in dados.get("results", []):
            detalhes = buscar_detalhes_filme(filme.get("id"))
            if detalhes:
                filmes.append({
                    "id": filme.get("id"),
                    "titulo": filme.get("title"),
                    "ano": filme.get("release_date", "").split("-")[0] if filme.get("release_date") else "N/A",
                    "genero": ", ".join([str(g) for g in filme.get("genre_ids", [])]),
                    "sinopse": filme.get("overview"),
                    "avaliacao": detalhes.get("vote_average"),
                    "producao": [empresa.get("name") for empresa in detalhes.get("production_companies", [])],
                    "poster": f"https://image.tmdb.org/t/p/w500{filme.get('poster_path')}" if filme.get("poster_path") else None
                })

        return jsonify({"filmes": filmes})
    except requests.exceptions.RequestException as e:
        return jsonify({"erro": f"Erro ao buscar no TMDB: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
