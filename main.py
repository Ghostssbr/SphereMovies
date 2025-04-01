from fastapi import FastAPI, HTTPException
import cloudscraper
from bs4 import BeautifulSoup
import html
import re
import json
from concurrent.futures import ThreadPoolExecutor
import asyncio
from typing import List, Dict

app = FastAPI()

# Configura o Cloudscraper
scraper = cloudscraper.create_scraper()

@app.get("/filmes", response_model=List[Dict])
async def listar_filmes():
    """Retorna todos os filmes com detalhes completos"""
    try:
        filmes = await carregar_filmes()
        detalhes = await processar_em_paralelo(filmes)
        return detalhes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/filmes/{filme_id}", response_model=Dict)
async def detalhes_filme(filme_id: int):
    """Retorna detalhes de um filme específico"""
    try:
        filmes = await carregar_filmes()
        filme = next((f for f in filmes if f["id"] == filme_id), None)
        
        if not filme:
            raise HTTPException(status_code=404, detail="Filme não encontrado")
        
        return await pegar_detalhes_do_filme(filme)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Funções de scraping
async def carregar_filmes() -> List[Dict]:
    """Carrega a lista básica de filmes"""
    url = "https://visioncine-1.com.br/movies"
    response = scraper.get(url)
    response.encoding = 'utf-8'

    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    filmes = soup.find_all("div", class_="swiper-slide item poster")
    
    return [{
        "id": idx + 1,
        "titulo": html.unescape(filme.find("h6").text.strip() if filme.find("h6") else "Desconhecido"),
        "ano": html.unescape(filme.find("span", string=lambda x: x and "2025" in x).text.strip() 
               if filme.find("span", string=lambda x: x and "2025" in x) else "Desconhecido"),
        "imagem": filme.find("div", class_="content")["style"].split("url(")[1].split(")")[0] 
                 if filme.find("div", class_="content") else "Imagem não disponível",
        "link_assistir": filme.find("a")["href"] if filme.find("a") else "Link não disponível"
    } for idx, filme in enumerate(filmes)]

async def pegar_detalhes_do_filme(filme: Dict) -> Dict:
    """Obtém detalhes completos de um filme"""
    if filme["link_assistir"] == "Link não disponível":
        return {**filme, "error": "Link indisponível"}

    try:
        # Página de detalhes
        response = scraper.get(filme["link_assistir"])
        soup = BeautifulSoup(response.content, "html.parser")

        # Extração dos dados
        dados = {
            "titulo": html.unescape(soup.select_one("h1.fw-bolder.mb-0").text.strip() 
                    if soup.select_one("h1.fw-bolder.mb-0") else filme["titulo"],
            "sinopse": html.unescape(soup.select_one("p.small.linefive").text.strip() 
                    if soup.select_one("p.small.linefive") else "Sinopse não disponível"),
            "generos": html.unescape(", ".join(
                    [span.text.strip() for span in soup.select("p.lineone > span:nth-of-type(2) span")]
                    if soup.select("p.lineone > span:nth-of-type(2) span") else ["Gêneros não disponíveis"])),
            "player": await extrair_link_player(filme["link_assistir"])
        }

        # Metadados (duração, ano, etc.)
        spans = soup.select_one("p.log").find_all("span") if soup.select_one("p.log") else []
        metadados = {
            "duracao": html.unescape(spans[0].text.strip()) if len(spans) > 0 else "Não informado",
            "ano": html.unescape(spans[1].text.strip()) if len(spans) > 1 else filme["ano"],
            "classificacao": html.unescape(spans[2].text.strip()) if len(spans) > 2 else "Não classificada",
            "qualidade": html.unescape(spans[3].text.strip()) if len(spans) > 3 else "Qualidade não especificada",
            "imdb": html.unescape(spans[4].text.strip()) if len(spans) > 4 else "N/A"
        }

        return {**filme, **dados, **metadados}

    except Exception as e:
        return {**filme, "error": f"Erro ao processar: {str(e)}"}

async def extrair_link_player(url_filme: str) -> str:
    """Extrai o link do player de vídeo"""
    try:
        response = scraper.get(url_filme)
        match = re.search(r"initializePlayer\('([^']+)'", response.text)
        return match.group(1) if match else "Link não encontrado"
    except:
        return "Erro ao extrair link"

async def processar_em_paralelo(filmes: List[Dict]) -> List[Dict]:
    """Processa os filmes em paralelo para melhor performance"""
    with ThreadPoolExecutor(max_workers=5) as executor:
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(executor, pegar_detalhes_do_filme, filme) for filme in filmes]
        return await asyncio.gather(*tasks)
