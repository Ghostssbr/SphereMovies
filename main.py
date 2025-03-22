from fastapi import FastAPI, HTTPException, Query
import json
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Modelo Pydantic para validar os dados do filme
class Filme(BaseModel):
    id: int
    titulo: str
    ano: str
    duracao: str
    classificacao: str
    imdb: str
    sinopse: str
    generos: str
    qualidade: str
    player: str

# Nome do arquivo JSON
DB_FILE = "filmes.json"

# Função para ler o banco de dados JSON
def ler_db():
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"filmes": []}  # Retorna uma lista vazia se o arquivo não existir
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Erro ao processar JSON")

# Função para salvar no banco de dados JSON
def salvar_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

# Rota para listar todos os filmes
@app.get("/filmes", response_model=List[Filme])
def listar_filmes():
    db = ler_db()
    return db.get("filmes", [])

# Rota para buscar um filme por ID
@app.get("/filmes/{id}", response_model=Filme)
def buscar_filme(id: int):
    db = ler_db()
    for filme in db.get("filmes", []):
        if filme["id"] == id:
            return filme
    raise HTTPException(status_code=404, detail="Filme não encontrado")

# Rota para pesquisar filmes por título
@app.get("/filmes/pesquisa", response_model=List[Filme])
def pesquisar_filmes_por_titulo(titulo: str = Query(..., description="Palavra-chave para pesquisa no título")):
    db = ler_db()
    resultados = [filme for filme in db.get("filmes", []) if titulo.lower() in filme["titulo"].lower()]
    
    if not resultados:
        raise HTTPException(status_code=404, detail="Nenhum filme encontrado com esse título")
    
    return resultados

# Rota para adicionar um novo filme
@app.post("/filmes", response_model=Filme)
def adicionar_filme(filme: Filme):
    db = ler_db()
    
    # Verifica se o ID já existe
    if any(f["id"] == filme.id for f in db.get("filmes", [])):
        raise HTTPException(status_code=400, detail="ID já existe")

    db["filmes"].append(filme.dict())
    salvar_db(db)
    return filme

# Rota para atualizar um filme existente
@app.put("/filmes/{id}", response_model=Filme)
def atualizar_filme(id: int, filme: Filme):
    db = ler_db()
    
    for index, f in enumerate(db.get("filmes", [])):
        if f["id"] == id:
            db["filmes"][index] = filme.dict()
            salvar_db(db)
            return filme
    
    raise HTTPException(status_code=404, detail="Filme não encontrado")

# Rota para excluir um filme
@app.delete("/filmes/{id}")
def excluir_filme(id: int):
    db = ler_db()
    
    for index, f in enumerate(db.get("filmes", [])):
        if f["id"] == id:
            db["filmes"].pop(index)
            salvar_db(db)
            return {"message": "Filme excluído com sucesso"}
    
    raise HTTPException(status_code=404, detail="Filme não encontrado")
