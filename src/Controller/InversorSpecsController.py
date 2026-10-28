import sys
from pathlib import Path
from typing import List, Optional

# Asegurar que la raíz del proyecto esté en sys.path
_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.Service.InversorSpecsService import InversorSpecsService


# Modelos Pydantic para Validación y Serialización
class InversorSpecsCreate(BaseModel):
    id: str = Field(..., json_schema_extra={"example": "INV-001"}, description="Identificador único del inversor")
    modelo: str = Field(..., json_schema_extra={"example": "SUN2000-100KTL-M1"}, description="Modelo comercial del inversor")
    potencia_nominal_kw: float = Field(..., gt=0, json_schema_extra={"example": 100.0}, description="Potencia nominal en kW (mayor que 0)")
    eficiencia_porc: float = Field(..., gt=0, le=100.0, json_schema_extra={"example": 98.6}, description="Eficiencia en porcentaje (0-100%)")


class InversorSpecsUpdate(BaseModel):
    modelo: Optional[str] = Field(None, json_schema_extra={"example": "SUN2000-100KTL-M2"}, description="Nuevo modelo comercial")
    potencia_nominal_kw: Optional[float] = Field(None, gt=0, json_schema_extra={"example": 110.0}, description="Nueva potencia nominal en kW")
    eficiencia_porc: Optional[float] = Field(None, gt=0, le=100.0, json_schema_extra={"example": 98.8}, description="Nueva eficiencia en porcentaje")


class InversorSpecsResponse(BaseModel):
    id: str
    modelo: str
    potencia_nominal_kw: float
    eficiencia_porc: float


router = APIRouter(
    prefix="/inversores-specs",
    tags=["Inversores Specs"],
)


def get_service() -> InversorSpecsService:
    """Proveedor de dependencias para el servicio de InversorSpecs."""
    return InversorSpecsService()


@router.post(
    "/",
    response_model=InversorSpecsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear especificaciones de un nuevo inversor",
)
def crear_inversor(
    datos: InversorSpecsCreate,
    service: InversorSpecsService = Depends(get_service),
):
    try:
        return service.crear_inversor(
            id=datos.id,
            modelo=datos.modelo,
            potencia_nominal_kw=datos.potencia_nominal_kw,
            eficiencia_porc=datos.eficiencia_porc,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/",
    response_model=List[InversorSpecsResponse],
    summary="Obtener todas las especificaciones de inversores",
)
def obtener_todos(
    service: InversorSpecsService = Depends(get_service),
):
    return service.obtener_todos()


@router.get(
    "/{id}",
    response_model=InversorSpecsResponse,
    summary="Obtener especificaciones de un inversor por su ID",
)
def obtener_por_id(
    id: str,
    service: InversorSpecsService = Depends(get_service),
):
    inversor = service.obtener_inversor(id)
    if inversor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inversor con ID '{id}' no encontrado.",
        )
    return inversor


@router.put(
    "/{id}",
    response_model=InversorSpecsResponse,
    summary="Actualizar especificaciones de un inversor existente",
)
def actualizar_inversor(
    id: str,
    datos: InversorSpecsUpdate,
    service: InversorSpecsService = Depends(get_service),
):
    try:
        return service.actualizar_inversor(
            id=id,
            modelo=datos.modelo,
            potencia_nominal_kw=datos.potencia_nominal_kw,
            eficiencia_porc=datos.eficiencia_porc,
        )
    except ValueError as e:
        error_msg = str(e)
        if "No existe ningún inversor" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg,
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar especificaciones de un inversor por su ID",
)
def eliminar_inversor(
    id: str,
    service: InversorSpecsService = Depends(get_service),
):
    eliminado = service.eliminar_inversor(id)
    if not eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inversor con ID '{id}' no encontrado.",
        )
    return None

