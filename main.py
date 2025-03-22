from flask import Flask, jsonify, render_template_string, request
import json

app = Flask(__name__)

# Nome do arquivo JSON
arquivo_json = "filmes.json"

# Função para ler e retornar os dados do JSON
def ler_filmes(arquivo):
    try:
        with open(arquivo, "r", encoding="utf-8") as file:
            filmes = json.load(file)
            return filmes
    except Exception as e:
        return {"erro": f"Erro ao ler o arquivo: {e}"}

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
            body {
                font-family: 'Arial', sans-serif;
                background-color: #000;
                color: #fff;
                margin: 0;
                padding: 0;
            }
            .container {
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background-color: #111;
                border-radius: 10px;
                box-shadow: 0 0 15px rgba(255, 0, 0, 0.7);
            }
            h1 {
                color: #fff; /* Título em branco */
                text-align: center;
                font-size: 2.5em;
                margin-bottom: 20px;
            }
            h2 {
                color: #ff0000;
                border-bottom: 2px solid #ff0000;
                padding-bottom: 5px;
                margin-top: 30px;
            }
            code {
                background-color: #333;
                color: #ff0000;
                padding: 2px 5px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
            }
            a {
                color: #ff0000;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
            ul {
                list-style-type: none;
                padding: 0;
            }
            li {
                margin: 10px 0;
            }
            pre {
                background-color: #222;
                padding: 10px;
                border-radius: 5px;
                color: #fff;
                overflow-x: auto;
            }
            .highlight {
                color: #ff0000;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>SphereAPI</h1>
            <p>Bem-vindo à <span class="highlight">SphereAPI</span>, sua API de filmes! Abaixo estão os detalhes de como usar a API.</p>
            
            <h2>Rotas Disponíveis</h2>
            <ul>
                <li><strong>GET /filmes</strong>: Retorna a lista completa de filmes.</li>
                <li><strong>GET /filmes/search</strong>: Permite pesquisar filmes por título ou ID.</li>
            </ul>

            <h2>Exemplo de Uso</h2>
            <p>Para obter a lista de filmes, faça uma requisição GET para:</p>
            <code>GET /filmes</code>

            <p>Para pesquisar filmes por título ou ID, use:</p>
            <code>GET /filmes/search?title=Homem</code><br>
            <code>GET /filmes/search?id=1</code><br>
            <code>GET /filmes/search?title=Homem&id=1</code>

            <h2>Resposta de Exemplo</h2>
            <pre>
{
    "filmes": [
        {
            "id": 1,
            "titulo": "Homem-Aranha",
            "ano": 2021,
            "genero": "Ação"
        },
        {
            "id": 2,
            "titulo": "Homem de Ferro",
            "ano": 2008,
            "genero": "Ação"
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
        </div>
    </body>
    </html>
    """
    return render_template_string(doc_html)

# Rota para obter os filmes
@app.route('/filmes', methods=['GET'])
def get_filmes():
    filmes = ler_filmes(arquivo_json)
    if "erro" in filmes:
        return jsonify(filmes), 500
    return jsonify({"filmes": filmes})

# Rota para pesquisar filmes
@app.route('/filmes/search', methods=['GET'])
def search_filmes():
    filmes = ler_filmes(arquivo_json)
    if "erro" in filmes:
        return jsonify(filmes), 500

    # Obtém os parâmetros da query string
    titulo = request.args.get('title', '').lower().strip('"\'')  # Remove aspas se presentes
    id_filme = request.args.get('id', type=int)

    # Filtra os filmes com base nos parâmetros
    resultados = []
    for filme in filmes:
        # Verifica se o ID corresponde (se fornecido)
        if id_filme is not None and filme.get('id') != id_filme:
            continue
        # Verifica se o título contém a string fornecida (se fornecido)
        if titulo and titulo not in filme.get('titulo', '').lower():
            continue
        resultados.append(filme)

    return jsonify({"filmes": resultados})

if __name__ == '__main__':
    app.run(debug=True)
