import requests

# Caché en memoria para evitar consultas HTTP duplicadas por la misma fecha
_CACHE_TC: dict[str, tuple[float, str]] = {}

# Valores de respaldo en caso de fallo de red o límite de la API pública
_RESPALDO_TC: dict[str, float] = {
    "2026-11-10": 3.748,
    "2026-11-12": 3.752,
    "2026-11-15": 3.755,
    "2026-11-18": 3.741,
}


def obtener_tipo_cambio(fecha: str, moneda: str) -> tuple[float, str]:
    """Devuelve (tipo_cambio_venta, fuente) para una fecha y moneda dadas."""
    if moneda == "PEN":
        return 1.0, "Moneda base (PEN)"

    if fecha in _CACHE_TC:
        return _CACHE_TC[fecha]

    url = "https://api.apis.net.pe/v1/tipo-cambio-sunat"
    try:
        respuesta = requests.get(url, params={"fecha": fecha}, timeout=4)
        if respuesta.status_code == 200:
            data = respuesta.json()
            tc_venta = float(data["venta"])
            resultado = (tc_venta, "API SUNAT")
            _CACHE_TC[fecha] = resultado
            return resultado
    except (requests.RequestException, KeyError, ValueError):
        pass

    tc_fallback = _RESPALDO_TC.get(fecha, 3.750)
    resultado = (tc_fallback, "Respaldo local")
    _CACHE_TC[fecha] = resultado
    return resultado


if __name__ == "__main__":
    print("Prueba USD 2026-11-10:", obtener_tipo_cambio("2026-11-10", "USD"))
    print("Prueba PEN 2026-11-12:", obtener_tipo_cambio("2026-11-12", "PEN"))