"""Análisis de sensibilidad del umbral de cercanía (distancia punto-polígono).

Uso:  python scripts/03_umbral_proximidad.py [--datos datos] [--umbrales 250 400 500 800 1000]
Requiere: pip install shapely pyproj
Proyecta a EPSG:32618 (UTM 18N, metros). Escribe datos/sensibilidad_umbral.md.
Contar como accesible en ADA: ada = 1 (total) y, por separado, ada in (1, 2).
"""
import argparse, statistics
from pathlib import Path
import numpy as np
from pyproj import Transformer
from shapely import STRtree, distance
from shapely.geometry import shape, Point
from shapely.ops import transform
from cargar import cargar

T = Transformer.from_crs("EPSG:4326", "EPSG:32618", always_xy=True).transform


def pts(filas, lat, lon):
    out = []
    for i, f in enumerate(filas):
        try:
            out.append((i, transform(T, Point(float(f[lon]), float(f[lat])))))
        except (KeyError, TypeError, ValueError):
            pass
    return out


def conteos(parques_g, puntos, umbral):
    """Por parque: lista de índices de punto a <= umbral m (usa predicado dwithin)."""
    arbol = STRtree([p for _, p in puntos])
    pares = arbol.query(parques_g, predicate="dwithin", distance=umbral)  # [[parque],[punto]]
    cerca = [[] for _ in parques_g]
    for pi, qi in zip(pares[0], pares[1]):
        cerca[pi].append(puntos[qi][0])
    return cerca


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--datos", default="datos")
    ap.add_argument("--umbrales", type=int, nargs="+", default=[250, 400, 500, 800, 1000])
    a = ap.parse_args()
    parques, metro, bici = cargar(a.datos)

    geoms = []
    for p in parques:
        g = p.get("multipolygon")
        geoms.append(transform(T, shape(g)) if g else None)
    ok = [i for i, g in enumerate(geoms) if g is not None]
    sin_geom = len(parques) - len(ok)
    G = np.array([geoms[i] for i in ok], dtype=object)

    m_pts = pts(metro, "gtfs_latitude", "gtfs_longitude")
    m_total = [(i, p) for i, p in m_pts if str(metro[i].get("ada")) == "1"]
    m_ada12 = [(i, p) for i, p in m_pts if str(metro[i].get("ada")) in ("1", "2")]
    b_pts = pts(bici, "lat", "lon")

    md = ["# Sensibilidad del umbral de cercanía\n",
          f"Parques con geometría: {len(ok)} de {len(parques)} (sin geometría: {sin_geom}). "
          f"Estaciones de metro: {len(m_pts)}; ADA total (ada=1): {len(m_total)}; ADA total o parcial: {len(m_ada12)}. "
          f"Estaciones Citi Bike: {len(b_pts)}.\n",
          "| Umbral (m) | % parques con metro | % con metro ADA total | % con metro ADA total o parcial | % con estación Citi Bike | % con ambos (metro y bici) | Mediana de estaciones Citi Bike por parque |",
          "|---|---|---|---|---|---|---|"]
    n = len(ok)
    for u in a.umbrales:
        cm = conteos(G, m_pts, u); ct = conteos(G, m_total, u); c12 = conteos(G, m_ada12, u); cb = conteos(G, b_pts, u)
        pct = lambda lst: round(100 * sum(bool(x) for x in lst) / n, 1)
        ambos = round(100 * sum(bool(x) and bool(y) for x, y in zip(cm, cb)) / n, 1)
        md.append(f"| {u} | {pct(cm)} | {pct(ct)} | {pct(c12)} | {pct(cb)} | {ambos} | {statistics.median(len(x) for x in cb)} |")
    md.append("\nLectura: el umbral se justifica por la zona donde la curva deja de cambiar bruscamente y por el tiempo de caminata "
              "(500 m en línea recta, aprox. 6 min a 5 km/h; la ruta real por calles es más larga). Cita una fuente de planificación del transporte para el rango elegido.")
    salida = Path(a.datos) / "sensibilidad_umbral.md"
    salida.write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md)); print(f"\nEscrito en {salida}")


if __name__ == "__main__":
    main()
