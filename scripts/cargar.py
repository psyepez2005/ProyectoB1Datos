"""Utilidades comunes: localiza el archivo más reciente de cada fuente."""
import json
from pathlib import Path


def ultimo(datos, prefijo):
    cand = sorted(Path(datos).glob(f"{prefijo}_*.json"))
    if not cand:
        raise SystemExit(f"No hay archivos {prefijo}_*.json en {datos}. Ejecuta primero 01_descargar_datos.py")
    return cand[-1]


def cargar(datos):
    parques = json.loads(ultimo(datos, "parks_properties").read_text(encoding="utf-8"))
    metro = json.loads(ultimo(datos, "mta_subway_stations").read_text(encoding="utf-8"))
    bici = json.loads(ultimo(datos, "citibike_station_information").read_text(encoding="utf-8"))["data"]["stations"]
    return parques, metro, bici
