import sys
from pathlib import Path
from typing import List, Optional

# Asegurar que la raíz del proyecto esté en sys.path
_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.Model.Coordenadas import Coordenadas
from src.Model.InversorSpecs import InversorSpecs
from src.Service.PlantaSolarService import PlantaSolarService


# Modelos Pydantic para Validación y Serialización
class CoordenadasDTO(BaseModel):
    latitud: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
        json_schema_extra={"example": 40.4168},
        description="Latitud en grados decimales (-90 a 90)",
    )
    longitud: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
        json_schema_extra={"example": -3.7038},
        description="Longitud en grados decimales (-180 a 180)",
    )
    altitud_m: float = Field(
        ...,
        json_schema_extra={"example": 650.0},
        description="Altitud en metros sobre el nivel del mar",
    )


class InversorSpecsDTO(BaseModel):
    id: str = Field(..., json_schema_extra={"example": "INV-001"}, description="Identificador único del inversor")
    modelo: str = Field(..., json_schema_extra={"example": "SUN2000-100KTL"}, description="Modelo comercial del inversor")
    potencia_nominal_kw: float = Field(..., gt=0, json_schema_extra={"example": 100.0}, description="Potencia nominal en kW (mayor que 0)")
    eficiencia_porc: float = Field(..., gt=0, le=100.0, json_schema_extra={"example": 98.6}, description="Eficiencia en porcentaje (0-100%)")


class PlantaSolarCreate(BaseModel):
    id: str = Field(..., json_schema_extra={"example": "PS-001"}, description="Identificador único de la planta solar")
    nombre: str = Field(..., json_schema_extra={"example": "Planta Solar Norte"}, description="Nombre descriptivo de la planta")
    potencia_dc_kw: float = Field(..., gt=0, json_schema_extra={"example": 5000.0}, description="Potencia DC en kW (debe ser mayor que 0)")
    coordenadas: Optional[CoordenadasDTO] = Field(None, description="Coordenadas geográficas de la planta")
    inversor_specs: Optional[InversorSpecsDTO] = Field(None, description="Especificaciones del inversor asociado")


class PlantaSolarUpdate(BaseModel):
    nombre: Optional[str] = Field(None, json_schema_extra={"example": "Planta Solar Norte Actualizada"}, description="Nuevo nombre de la planta")
    potencia_dc_kw: Optional[float] = Field(None, gt=0, json_schema_extra={"example": 6000.0}, description="Nueva potencia DC en kW")
    coordenadas: Optional[CoordenadasDTO] = Field(None, description="Nuevas coordenadas geográficas de la planta")
    inversor_specs: Optional[InversorSpecsDTO] = Field(None, description="Nuevas especificaciones del inversor asociado")


class PlantaSolarResponse(BaseModel):
    id: str
    nombre: str
    potencia_dc_kw: float
    coordenadas: Optional[CoordenadasDTO] = None
    inversor_specs: Optional[InversorSpecsDTO] = None


router = APIRouter(
    prefix="/plantas-solares",
    tags=["Plantas Solares"],
)


def get_service() -> PlantaSolarService:
    """Proveedor de dependencias para el servicio de PlantaSolar."""
    return PlantaSolarService()


@router.post(
    "/",
    response_model=PlantaSolarResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva planta solar",
)
def crear_planta(
    datos: PlantaSolarCreate,
    service: PlantaSolarService = Depends(get_service),
):
    try:
        coords = (
            Coordenadas(
                latitud=datos.coordenadas.latitud,
                longitud=datos.coordenadas.longitud,
                altitud_m=datos.coordenadas.altitud_m,
            )
            if datos.coordenadas is not None
            else None
        )

        inv_specs = (
            InversorSpecs(
                id=datos.inversor_specs.id,
                modelo=datos.inversor_specs.modelo,
                potencia_nominal_kw=datos.inversor_specs.potencia_nominal_kw,
                eficiencia_porc=datos.inversor_specs.eficiencia_porc,
            )
            if datos.inversor_specs is not None
            else None
        )

        planta = service.crear_planta(
            id=datos.id,
            nombre=datos.nombre,
            potencia_dc_kw=datos.potencia_dc_kw,
            coordenadas=coords,
            inversor_specs=inv_specs,
        )
        return planta
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/",
    response_model=List[PlantaSolarResponse],
    summary="Obtener todas las plantas solares",
)
def obtener_todas(
    service: PlantaSolarService = Depends(get_service),
):
    return service.obtener_todas()


@router.get(
    "/{id}",
    response_model=PlantaSolarResponse,
    summary="Obtener una planta solar por su ID",
)
def obtener_por_id(
    id: str,
    service: PlantaSolarService = Depends(get_service),
):
    planta = service.obtener_planta(id)
    if planta is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Planta solar con ID '{id}' no encontrada.",
        )
    return planta


@router.put(
    "/{id}",
    response_model=PlantaSolarResponse,
    summary="Actualizar una planta solar existente",
)
def actualizar_planta(
    id: str,
    datos: PlantaSolarUpdate,
    service: PlantaSolarService = Depends(get_service),
):
    try:
        coords = (
            Coordenadas(
                latitud=datos.coordenadas.latitud,
                longitud=datos.coordenadas.longitud,
                altitud_m=datos.coordenadas.altitud_m,
            )
            if datos.coordenadas is not None
            else None
        )

        inv_specs = (
            InversorSpecs(
                id=datos.inversor_specs.id,
                modelo=datos.inversor_specs.modelo,
                potencia_nominal_kw=datos.inversor_specs.potencia_nominal_kw,
                eficiencia_porc=datos.inversor_specs.eficiencia_porc,
            )
            if datos.inversor_specs is not None
            else None
        )

        planta = service.actualizar_planta(
            id=id,
            nombre=datos.nombre,
            potencia_dc_kw=datos.potencia_dc_kw,
            coordenadas=coords,
            inversor_specs=inv_specs,
        )
        return planta
    except ValueError as e:
        error_msg = str(e)
        if "No existe ninguna planta solar" in error_msg:
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
    summary="Eliminar una planta solar por su ID",
)
def eliminar_planta(
    id: str,
    service: PlantaSolarService = Depends(get_service),
):
    eliminado = service.eliminar_planta(id)
    if not eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Planta solar con ID '{id}' no encontrada.",
        )
    return None
