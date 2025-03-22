from fastapi import FastAPI
from typing import List
import json
from pydantic import BaseModel

app = FastAPI()

# Nome do arquivo JSON
arquivo_json = "filmes.json"

# Modelo para representar um Filme
class Filme(BaseModel):
    titulo: str
    ano: int
    duracao: str
    classificacao: str
    imdb: float
    sinopse: str
    generos: List[str]
    qualidade: str
    player: str

# Função para ler e retornar os dados do JSON
def ler_filmes(arquivo: str):
    try:
        with open(arquivo, "r", encoding="utf-8") as file:
            filmes = json.load(file)
            return filmes
    except Exception as e:
        return {"erro": f"Erro ao ler o arquivo: {e}"}

# Rota da API para obter os filmes
@app.get("/api/filmes", response_model=List[Filme])
async def get_filmes():
    filmes = ler_filmes(arquivo_json)
    if "erro" in filmes:
        return filmes
    return filmes

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
