En MCP-basert løsning som bruker Claude via OpenRouter for intelligent sammendrags-generering.

Løsningen består av to mikrotjenester:

1. konsulent-api: Dette er en backend-server med konsulent-data
2. llm-verktøy-api: AI drevet MCP-server som bruker Claude til å generere sammendrag


Kjøres med docker compose up --build

Løsningen har to endepunkter:
GET /konsulenter
    - returnerer hardkodet liste med konsulenter
GET /tilgjengelige-konsulenter/sammendrag
    - to query-parametre; min_tilgjengelighe_prosent og påkrevd_ferdighet.
    - returnerer sammendrag

Eksempel-respons:

{
  "sammendrag": "Fant 3 konsulenter med minst 50% tilgjengelighet og ferdigheten 'python'. Leo T. har 80% tilgjengelighet og kan også Kubernetes og Terraform. Lucas M. har 65% tilgjengelighet med Django og PostgreSQL erfaring. Anna K. har 60% tilgjengelighet og er også sterk i React og AWS."
}