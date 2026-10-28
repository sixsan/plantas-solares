from typing import List, Optional
from src.Model.InversorSpecs import InversorSpecs
from src.Repository.InversorSpecsRepository import InversorSpecsRepository


class InversorSpecsService:
    def __init__(self, repository: Optional[InversorSpecsRepository] = None):
        self.repository = repository if repository is not None else InversorSpecsRepository()

    def _validar_specs(self, potencia_nominal_kw: float, eficiencia_porc: float) -> None:
        if potencia_nominal_kw <= 0:
            raise ValueError("La potencia nominal del inversor en kW debe ser mayor que 0.")
        if not (0 < eficiencia_porc <= 100):
            raise ValueError(f"La eficiencia del inversor ({eficiencia_porc}%) debe estar comprendida entre 0 y 100%.")

    def crear_inversor(
        self,
        id: str,
        modelo: str,
        potencia_nominal_kw: float,
        eficiencia_porc: float,
    ) -> InversorSpecs:
        if not id or not id.strip():
            raise ValueError("El id del inversor no puede estar vacío.")
        if not modelo or not modelo.strip():
            raise ValueError("El modelo del inversor no puede estar vacío.")

        self._validar_specs(potencia_nominal_kw, eficiencia_porc)

        id_limpio = id.strip()
        if self.repository.exists(id_limpio):
            raise ValueError(f"Ya existe un inversor con el id '{id_limpio}'.")

        inversor = InversorSpecs(
            id=id_limpio,
            modelo=modelo.strip(),
            potencia_nominal_kw=float(potencia_nominal_kw),
            eficiencia_porc=float(eficiencia_porc),
        )
        return self.repository.create(inversor)

    def obtener_inversor(self, id: str) -> Optional[InversorSpecs]:
        if not id or not id.strip():
            raise ValueError("El id no puede estar vacío.")
        return self.repository.get_by_id(id.strip())

    def obtener_todos(self) -> List[InversorSpecs]:
        return self.repository.get_all()

    def actualizar_inversor(
        self,
        id: str,
        modelo: Optional[str] = None,
        potencia_nominal_kw: Optional[float] = None,
        eficiencia_porc: Optional[float] = None,
    ) -> InversorSpecs:
        if not id or not id.strip():
            raise ValueError("El id no puede estar vacío.")

        id_limpio = id.strip()
        inversor_existente = self.repository.get_by_id(id_limpio)
        if not inversor_existente:
            raise ValueError(f"No existe ningún inversor con el id '{id_limpio}'.")

        nuevo_modelo = inversor_existente.modelo
        nueva_potencia = inversor_existente.potencia_nominal_kw
        nueva_eficiencia = inversor_existente.eficiencia_porc

        if modelo is not None:
            if not modelo.strip():
                raise ValueError("El modelo no puede estar vacío.")
            nuevo_modelo = modelo.strip()

        if potencia_nominal_kw is not None:
            if potencia_nominal_kw <= 0:
                raise ValueError("La potencia nominal del inversor en kW debe ser mayor que 0.")
            nueva_potencia = float(potencia_nominal_kw)

        if eficiencia_porc is not None:
            if not (0 < eficiencia_porc <= 100):
                raise ValueError(f"La eficiencia del inversor ({eficiencia_porc}%) debe estar comprendida entre 0 y 100%.")
            nueva_eficiencia = float(eficiencia_porc)

        inversor_actualizado = InversorSpecs(
            id=id_limpio,
            modelo=nuevo_modelo,
            potencia_nominal_kw=nueva_potencia,
            eficiencia_porc=nueva_eficiencia,
        )
        self.repository.update(inversor_actualizado)
        return inversor_actualizado

    def eliminar_inversor(self, id: str) -> bool:
        if not id or not id.strip():
            raise ValueError("El id no puede estar vacío.")
        return self.repository.delete(id.strip())
