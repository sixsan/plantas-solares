from typing import List, Optional
from src.Model.Coordenadas import Coordenadas
from src.Model.InversorSpecs import InversorSpecs
from src.Model.PlantaSolar import PlantaSolar
from src.Repository.PlantaSolarRepository import PlantaSolarRepository


class PlantaSolarService:
    def __init__(self, repository: Optional[PlantaSolarRepository] = None):
        self.repository = repository if repository is not None else PlantaSolarRepository()

    def _validar_coordenadas(self, coords: Coordenadas) -> None:
        if not (-90.0 <= coords.latitud <= 90.0):
            raise ValueError(f"Latitud inválida ({coords.latitud}). Debe estar comprendida entre -90 y 90 grados.")
        if not (-180.0 <= coords.longitud <= 180.0):
            raise ValueError(f"Longitud inválida ({coords.longitud}). Debe estar comprendida entre -180 y 180 grados.")

    def _validar_inversor_specs(self, specs: InversorSpecs) -> None:
        if not specs.id or not specs.id.strip():
            raise ValueError("El id del inversor no puede estar vacío.")
        if not specs.modelo or not specs.modelo.strip():
            raise ValueError("El modelo del inversor no puede estar vacío.")
        if specs.potencia_nominal_kw <= 0:
            raise ValueError("La potencia nominal del inversor en kW debe ser mayor que 0.")
        if not (0 < specs.eficiencia_porc <= 100):
            raise ValueError(f"La eficiencia del inversor ({specs.eficiencia_porc}%) debe estar comprendida entre 0 y 100%.")

    def crear_planta(
        self,
        id: str,
        nombre: str,
        potencia_dc_kw: float,
        coordenadas: Optional[Coordenadas] = None,
        inversor_specs: Optional[InversorSpecs] = None,
    ) -> PlantaSolar:
        if not id or not id.strip():
            raise ValueError("El id de la planta solar no puede estar vacío.")
        if not nombre or not nombre.strip():
            raise ValueError("El nombre de la planta solar no puede estar vacío.")
        if potencia_dc_kw <= 0:
            raise ValueError("La potencia DC en kW debe ser mayor que 0.")

        if coordenadas is not None:
            self._validar_coordenadas(coordenadas)

        if inversor_specs is not None:
            self._validar_inversor_specs(inversor_specs)

        id_limpio = id.strip()
        if self.repository.exists(id_limpio):
            raise ValueError(f"Ya existe una planta solar con el id '{id_limpio}'.")

        planta = PlantaSolar(
            id=id_limpio,
            nombre=nombre.strip(),
            potencia_dc_kw=float(potencia_dc_kw),
            coordenadas=coordenadas,
            inversor_specs=inversor_specs,
        )
        return self.repository.create(planta)

    def obtener_planta(self, id: str) -> Optional[PlantaSolar]:
        if not id or not id.strip():
            raise ValueError("El id no puede estar vacío.")
        return self.repository.get_by_id(id.strip())

    def obtener_todas(self) -> List[PlantaSolar]:
        return self.repository.get_all()

    def actualizar_planta(
        self,
        id: str,
        nombre: Optional[str] = None,
        potencia_dc_kw: Optional[float] = None,
        coordenadas: Optional[Coordenadas] = None,
        inversor_specs: Optional[InversorSpecs] = None,
    ) -> PlantaSolar:
        if not id or not id.strip():
            raise ValueError("El id no puede estar vacío.")

        id_limpio = id.strip()
        planta_existente = self.repository.get_by_id(id_limpio)
        if not planta_existente:
            raise ValueError(f"No existe ninguna planta solar con el id '{id_limpio}'.")

        nuevo_nombre = planta_existente.nombre
        nueva_potencia = planta_existente.potencia_dc_kw
        nuevas_coordenadas = planta_existente.coordenadas
        nuevo_inversor = planta_existente.inversor_specs

        if nombre is not None:
            if not nombre.strip():
                raise ValueError("El nombre no puede estar vacío.")
            nuevo_nombre = nombre.strip()

        if potencia_dc_kw is not None:
            if potencia_dc_kw <= 0:
                raise ValueError("La potencia DC en kW debe ser mayor que 0.")
            nueva_potencia = float(potencia_dc_kw)

        if coordenadas is not None:
            self._validar_coordenadas(coordenadas)
            nuevas_coordenadas = coordenadas

        if inversor_specs is not None:
            self._validar_inversor_specs(inversor_specs)
            nuevo_inversor = inversor_specs

        planta_actualizada = PlantaSolar(
            id=id_limpio,
            nombre=nuevo_nombre,
            potencia_dc_kw=nueva_potencia,
            coordenadas=nuevas_coordenadas,
            inversor_specs=nuevo_inversor,
        )
        self.repository.update(planta_actualizada)
        return planta_actualizada

    def eliminar_planta(self, id: str) -> bool:
        if not id or not id.strip():
            raise ValueError("El id no puede estar vacío.")
        return self.repository.delete(id.strip())
