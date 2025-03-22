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
        <link rel="icon" href="https://img.icons8.com/color/48/000000/movie-projector.png" type="image/x-icon">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
        <style>
            /* Reset básico */
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            /* Estilos globais */
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

            /* Botão de exemplo */
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

            /* Botão do WhatsApp */
            .whatsapp-button {
                display: inline-block;
                margin-top: 20px;
                padding: 10px 20px;
                background: linear-gradient(90deg, #25D366, #128C7E);
                color: #fff;
                border: none;
                border-radius: 5px;
                font-size: 1em;
                cursor: pointer;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                text-decoration: none;
            }

            .whatsapp-button:hover {
                transform: translateY(-3px);
                box-shadow: 0 5px 15px rgba(18, 140, 126, 0.4);
            }

            .whatsapp-button i {
                margin-right: 10px;
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

            <button class="example-button" onclick="window.location.href='/filmes'">Testar Rota /filmes</button>
            <a class="whatsapp-button" href="https://wa.me/?text=Confira%20a%20SphereAPI%20de%20filmes%3A%20http%3A%2F%2F127.0.0.1%3A5000%2F" target="_blank">
                <i class="fab fa-whatsapp"></i> Compartilhar no WhatsApp
            </a>
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
