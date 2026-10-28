from dataclasses import dataclass
from datetime import datetime


@dataclass
class DatosMeteorologicos:
    """Clase que representa las mediciones y variables meteorológicas

    registradas en un instante de tiempo para una planta solar fotovoltaica.
    """

    timestamp: datetime
    ghi_w_m2: float  # Irradiancia Global Horizontal (W/m²)
    dni_w_m2: float  # Irradiancia Directa Normal (W/m²)
    dhi_w_m2: float  # Irradiancia Difusa Horizontal (W/m²)
    temp_ambiente_c: float  # Temperatura del aire ambiente (°C)
    velocidad_viento_m_s: float  # Velocidad del viento (m/s)

