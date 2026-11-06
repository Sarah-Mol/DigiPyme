"""Adaptador del DENUE con proxy de caché.

- AdaptadorDENUE (Adapter): traduce el JSON del INEGI a objetos del dominio.
- ProxyCacheDENUE (Proxy de caché): guarda respuestas para repetir la demo
  sin conexión (OCP: se agrega sin cambiar el adaptador).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import httpx

from backend.dominio.interfaces import FuenteUnidadesEconomicas


class AdaptadorDENUE(FuenteUnidadesEconomicas):
    """Adapter: traduce el JSON del INEGI a objetos del dominio (ResumenZona).

    SRP: la conversión no se mezcla con la lógica del agente.
    """

    # URL base de la API del DENUE del INEGI
    URL_BASE = "https://www.inegi.org.mx/app/api/denue/v1/consulta"

    def __init__(self, token: str | None = None) -> None:
        self._token = token or os.getenv("DENUE_TOKEN", "")

    def cuantificar(self, clave_municipio: str, clase_scian: str) -> int:
        """Cuenta unidades económicas usando el método Cuantificar del DENUE.

        URL: Cuantificar/{actividad}/{area_geografica}/{estrato}/{token}
        """
        url = (
            f"{self.URL_BASE}/Cuantificar/{clase_scian}/{clave_municipio}"
            f"/0/{self._token}"
        )
        try:
            resp = httpx.get(url, timeout=30.0)
            resp.raise_for_status()
            datos = resp.json()
            if isinstance(datos, list) and datos:
                return int(datos[0].get("Total", 0))
            return int(resp.text.strip().strip('"'))
        except (httpx.HTTPError, ValueError, KeyError):
            return 0

    def buscar_area(
        self, clave_municipio: str, clase_scian: str
    ) -> list[dict[str, Any]]:
        """Busca establecimientos usando BuscarAreaActEstr del DENUE.

        URL: BuscarAreaActEstr/{entidad}/{municipio}/{localidad}/{AGEB}/{manzana}/
             {sector}/{subsector}/{rama}/{clase}/{nombre}/{reg_ini}/{reg_fin}/
             {id}/{estrato}/{token}
        La clave_municipio viene como "14098" → entidad=14, municipio=098.
        """
        entidad = clave_municipio[:2]
        municipio = clave_municipio[2:]
        url = (
            f"{self.URL_BASE}/BuscarAreaActEstr/{entidad}/{municipio}"
            f"/0/0/0/0/0/0/{clase_scian}/0/1/50/0/0/{self._token}"
        )
        try:
            resp = httpx.get(url, timeout=30.0)
            resp.raise_for_status()
            datos = resp.json()
            if isinstance(datos, list):
                return datos
            return []
        except (httpx.HTTPError, json.JSONDecodeError):
            return []


class ProxyCacheDENUE(FuenteUnidadesEconomicas):
    """Proxy de caché (OCP): guarda respuestas del DENUE.

    Se agrega sin cambiar el AdaptadorDENUE.
    Si hay caché, la usa; si no, delega al adaptador y guarda la respuesta.
    Si el DENUE falla, usa la caché y avisa.
    """

    def __init__(
        self,
        adaptador: AdaptadorDENUE,
        ruta_cache: str = "backend/datos/cache_denue",
    ) -> None:
        self._adaptador = adaptador
        self._ruta_cache = Path(ruta_cache)
        self._ruta_cache.mkdir(parents=True, exist_ok=True)

    def _clave(self, metodo: str, municipio: str, scian: str) -> str:
        return f"{metodo}_{municipio}_{scian}"

    def _leer_cache(self, clave: str) -> Any | None:
        archivo = self._ruta_cache / f"{clave}.json"
        if archivo.exists():
            with open(archivo, encoding="utf-8") as f:
                return json.load(f)
        return None

    def _guardar_cache(self, clave: str, datos: Any) -> None:
        archivo = self._ruta_cache / f"{clave}.json"
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False)

    def cuantificar(self, clave_municipio: str, clase_scian: str) -> int:
        """Intenta caché primero; si no, consulta el DENUE y guarda."""
        clave = self._clave("cuantificar", clave_municipio, clase_scian)
        cached = self._leer_cache(clave)
        if cached is not None:
            return int(cached)

        resultado = self._adaptador.cuantificar(clave_municipio, clase_scian)
        if resultado > 0:
            self._guardar_cache(clave, resultado)
        return resultado

    def buscar_area(
        self, clave_municipio: str, clase_scian: str
    ) -> list[dict[str, Any]]:
        """Intenta caché primero; si no, consulta el DENUE y guarda."""
        clave = self._clave("buscar_area", clave_municipio, clase_scian)
        cached = self._leer_cache(clave)
        if cached is not None and isinstance(cached, list):
            return cached

        resultado = self._adaptador.buscar_area(clave_municipio, clase_scian)
        if resultado:
            self._guardar_cache(clave, resultado)
        return resultado
