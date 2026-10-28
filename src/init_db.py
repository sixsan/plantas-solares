import sys
from pathlib import Path

# Asegurar que la raíz del proyecto esté en sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.Repository.PlantaSolarRepository import PlantaSolarRepository
from src.Repository.InversorSpecsRepository import InversorSpecsRepository


def init_database(db_name: str = "plantas_solares.db"):
    # Ubicar la base de datos en la raíz del proyecto peir-pv
    db_path = Path(__file__).resolve().parent.parent / db_name
    print(f"Inicializando base de datos en: {db_path}")

    # Al instanciar los repositorios se ejecuta _ensure_schema() y se crean las tablas
    repo_inv = InversorSpecsRepository(db_path=str(db_path))
    repo_plantas = PlantaSolarRepository(db_path=str(db_path))
    print(f"Base de datos '{db_name}' creada e inicializada correctamente con tablas de plantas solares e inversores.")
    return repo_plantas, repo_inv


if __name__ == "__main__":
    init_database()
