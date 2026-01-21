from fastapi import FastAPI, Query
import httpx
import os

app = FastAPI()

@app.get("/tilgjengelige-konsulenter/sammendrag")
async def get_sammendrag(
    min_tilgjengelighet_prosent: int = Query(..., ge=0, le=100), 
    pakrevd_ferdighet: str = Query(...)
):
    # Her henter jeg data fra backend 
    api_url = os.getenv('KONSULENT_API_URL', 'http://konsulent-api:8000')
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{api_url}/konsulenter")
            konsulenter = response.json()
        except httpx.RequestError as e:
            return {"error": f"Kunne ikke hente data fra backend API"}

    # Filtrer konsulenter basert på kriterier
    filtrerte = []
    for k in konsulenter:
        tilgjengelighet = 100 - k["belastning_prosent"]

        # Sjekker om konsulenten har den påkrevde ferdigheten
        har_ferdighet = False
        for ferdighet in k["ferdigheter"]:
            if ferdighet.lower() == pakrevd_ferdighet.lower():
                har_ferdighet = True
                break
        
        # Vi legger til konsulenten hvis begge kriteriene er oppfylt
        if tilgjengelighet >= min_tilgjengelighet_prosent and har_ferdighet:
            k["tilgjengelighet_prosent"] = tilgjengelighet
            filtrerte.append(k)
    
    # Sorterer konsulentene med høyest tilgjengelighet først
    # Bruker bubble sort for å gjøre det enkelt
    for i in range(len(filtrerte)):
        for j in range(i + 1, len(filtrerte)):
            if filtrerte[i]["tilgjengelighet_prosent"] < filtrerte[j]["tilgjengelighet_prosent"]:

                temp = filtrerte[i]
                filtrerte[i] = filtrerte[j] 
                filtrerte[j] = temp
    
    # Dersom det er ingen konsulenter som matcher kriteriene returnerer vi en fin melding
    if not filtrerte:
        melding = f"Fant ingen konsulenter med minst {min_tilgjengelighet_prosent}% tilgjengelighet og ferdigheten '{pakrevd_ferdighet}'."
        return {"sammendrag": melding}
    
    # Vi lager prompt for Claude
    prompt = "Lag et kort sammendrag på norsk:\n\n"

    for k in filtrerte:
        ferdigheter = ", ".join(k["ferdigheter"])
        prompt += f"- {k['navn']}: {k['tilgjengelighet_prosent']}% tilgjengelighet, ferdigheter: {ferdigheter}\n"
    
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
