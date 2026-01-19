from fastapi import FastAPI

app = FastAPI()

KONSULENTER = [
    {"id": 1, "navn": "Anna K.", "ferdigheter": ["python", "react", "aws"], "belastning_prosent": 40},
    {"id": 2, "navn": "Leo T.", "ferdigheter": ["python", "kubernetes", "terraform"], "belastning_prosent": 20},
    {"id": 3, "navn": "Maria S.", "ferdigheter": ["java", "spring", "azure"], "belastning_prosent": 85},
    {"id": 4, "navn": "Erik B.", "ferdigheter": ["react", "typescript", "node.js"], "belastning_prosent": 50},
    {"id": 5, "navn": "Sofia L.", "ferdigheter": ["python", "machine-learning", "docker"], "belastning_prosent": 70},
    {"id": 6, "navn": "Oliver N.", "ferdigheter": ["golang", "microservices", "mongodb"], "belastning_prosent": 10},
    {"id": 7, "navn": "Emma R.", "ferdigheter": ["react", "vue", "css"], "belastning_prosent": 95},
    {"id": 8, "navn": "Lucas M.", "ferdigheter": ["python", "django", "postgresql"], "belastning_prosent": 35}
]

@app.get("/konsulenter")
def hent_konsulenter():
    return KONSULENTER

@app.get("/health")
def health_check():
    return {"status": "ok"}
