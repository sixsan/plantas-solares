from dataclasses import dataclass


@dataclass
class InversorSpecs:
    """Especificaciones técnicas de un inversor solar fotovoltaico.

    Attributes:
        id (str): Identificador único del inversor/especificación (ej: 'INV-001').
        modelo (str): Modelo comercial del inversor.
        potencia_nominal_kw (float): Potencia nominal en corriente alterna (kW).
        eficiencia_porc (float): Eficiencia del inversor en porcentaje (0-100%).
    """

    id: str
    modelo: str
    potencia_nominal_kw: float
    eficiencia_porc: float
