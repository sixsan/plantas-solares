import sys
from pathlib import Path

# Asegurar que la carpeta raíz del proyecto esté en sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI
from src.Controller.PlantaSolarController import router as planta_solar_router
from src.Controller.InversorSpecsController import router as inversor_specs_router

app = FastAPI(
    title="API Plantas Solares",
    description="API REST para la gestión y monitorización de plantas solares fotovoltaicas e inversores.",
    version="1.0.0",
)

app.include_router(planta_solar_router)
app.include_router(inversor_specs_router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "API de Plantas Solares activa"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)
