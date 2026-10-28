from dataclasses import dataclass


@dataclass
class Coordenadas:
    """Representa la ubicación geográfica de una planta solar.

    Attributes:
        latitud (float): Latitud en grados decimales (-90 a 90).
        longitud (float): Longitud en grados decimales (-180 a 180).
        altitud_m (float): Altitud en metros sobre el nivel del mar.
    """

    latitud: float
    longitud: float
    altitud_m: float
