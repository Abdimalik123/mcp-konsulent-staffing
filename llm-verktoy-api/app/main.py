from fastapi import FastAPI, Query
import httpx
import os

app = FastAPI()

@app.get("/tilgjengelige-konsulenter/sammendrag")
async def get_sammendrag(
    min_tilgjengelighet_prosent: int = Query(..., ge=0, le=100), 
    pakrevd_ferdighet: str = Query(...)
):
    # Hent konsulenter fra backend
    api_url = os.getenv('KONSULENT_API_URL', 'http://konsulent-api:8000')
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{api_url}/konsulenter")
        konsulenter = response.json()
    
    # Filtrer basert på kriterier
    filtrerte = []
    for k in konsulenter:
        tilgjengelighet = 100 - k["belastning_prosent"]
        har_ferdighet = pakrevd_ferdighet.lower() in [f.lower() for f in k["ferdigheter"]]
        
        if tilgjengelighet >= min_tilgjengelighet_prosent and har_ferdighet:
            k["tilgjengelighet_prosent"] = tilgjengelighet
            filtrerte.append(k)
    
    # Sorter høyest tilgjengelighet først
    filtrerte.sort(key=lambda x: x["tilgjengelighet_prosent"], reverse=True)
    
    # Ingen treff
    if not filtrerte:
        melding = f"Fant ingen konsulenter med minst {min_tilgjengelighet_prosent}% tilgjengelighet og ferdigheten '{pakrevd_ferdighet}'."
        return {"sammendrag": melding}
    
    # Lag prompt for Claude
    intro = f"Lag et kort sammendrag på norsk av disse {len(filtrerte)} konsulentene med minst {min_tilgjengelighet_prosent}% tilgjengelighet og '{pakrevd_ferdighet}':\n"
    
    konsulent_linjer = []
    for k in filtrerte:
        ferdigheter = ', '.join(k['ferdigheter'])
        linje = f"- {k['navn']}: {k['tilgjengelighet_prosent']}%, {ferdigheter}"
        konsulent_linjer.append(linje)
    
    prompt = intro + "\n".join(konsulent_linjer)
    
    # Kall Claude via OpenRouter
    api_key = os.getenv('OPENROUTER_API_KEY')
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "anthropic/claude-3.5-sonnet",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 300
            },
            timeout=30.0
        )
        
        data = response.json()
        sammendrag = data["choices"][0]["message"]["content"].strip()
        return {"sammendrag": sammendrag}

@app.get("/health")
def health_check():
    return {"status": "ok"}
