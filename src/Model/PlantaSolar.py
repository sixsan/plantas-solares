from dataclasses import dataclass
from typing import Optional
from .Coordenadas import Coordenadas
from .InversorSpecs import InversorSpecs


@dataclass
class PlantaSolar:
    id: str
    nombre: str
    potencia_dc_kw: float
    coordenadas: Optional[Coordenadas] = None
    inversor_specs: Optional[InversorSpecs] = None

    @property
    def InversorSpecs(self) -> Optional[InversorSpecs]:
        """Propiedad que permite acceder al inversor mediante InversorSpecs."""
        return self.inversor_specs

    @InversorSpecs.setter
    def InversorSpecs(self, valor: Optional[InversorSpecs]) -> None:
        self.inversor_specs = valor
