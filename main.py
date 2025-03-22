from flask import Flask, jsonify
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

# Rota da API para obter os filmes
@app.route('/api/filmes', methods=['GET'])
def get_filmes():
    filmes = ler_filmes(arquivo_json)
    if "erro" in filmes:
        return jsonify(filmes), 500
    return jsonify(filmes)

if __name__ == '__main__':
    app.run(debug=True)
