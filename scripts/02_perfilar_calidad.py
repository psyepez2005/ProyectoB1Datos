"""Perfila calidad: conteos, claves, duplicados, faltantes y valores de campos clave.

Uso:  python scripts/02_perfilar_calidad.py [--datos datos]
Escribe datos/perfil_calidad.md con los números para pegar en el informe.
"""
import argparse, json
from collections import Counter
from pathlib import Path
from cargar import cargar

VACIOS = {"", "nan", "none", "null", "n/a"}


def es_vacio(v):
    return v is None or (isinstance(v, str) and v.strip().lower() in VACIOS)


def faltantes(filas):
    campos = sorted({k for f in filas for k in f})
    res = []
    for c in campos:
        n = sum(es_vacio(f.get(c)) for f in filas)
        if n:
            res.append((c, n, round(100 * n / len(filas), 1)))
    return sorted(res, key=lambda x: -x[1])


def duplicados_exactos(filas):
    c = Counter(json.dumps(f, sort_keys=True, ensure_ascii=False) for f in filas)
    return sum(v - 1 for v in c.values() if v > 1)


def unicidad(filas, campo):
    vals = [f.get(campo) for f in filas if not es_vacio(f.get(campo))]
    return len(vals), len(set(vals))


def tabla(titulo, filas):
    md = [f"\n#### {titulo}\n"]
    if not filas:
        return md + ["Sin casos.\n"]
    md += ["| Campo | Vacíos o 'NaN' | % |", "|---|---|---|"]
    md += [f"| `{c}` | {n} | {p} |" for c, n, p in filas]
    return md


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--datos", default="datos")
    a = ap.parse_args()
    parques, metro, bici = cargar(a.datos)
    md = ["# Perfil de calidad de datos\n"]

    # Parques
    cats = Counter(p.get("typecategory") for p in parques)
    md += ["## Parks Properties", f"- Registros: {len(parques)}",
           f"- Suma por typecategory: {sum(cats.values())} en {len(cats)} categorías",
           f"- gispropnum (con valor, únicos): {unicidad(parques, 'gispropnum')}",
           f"- globalid (con valor, únicos): {unicidad(parques, 'globalid')}",
           f"- Filas duplicadas exactas: {duplicados_exactos(parques)}",
           f"- Distritos (borough): {dict(Counter(p.get('borough') for p in parques))}"]
    md += tabla("Valores faltantes", faltantes(parques))

    # Metro
    ada = Counter(m.get("ada") for m in metro)
    rutas = Counter(r for m in metro for r in str(m.get("daytime_routes", "")).split())
    md += ["\n## MTA Subway Stations", f"- Registros: {len(metro)}",
           f"- gtfs_stop_id (con valor, únicos): {unicidad(metro, 'gtfs_stop_id')}",
           f"- station_id (con valor, únicos): {unicidad(metro, 'station_id')}",
           f"- complex_id (con valor, únicos): {unicidad(metro, 'complex_id')}",
           f"- Filas duplicadas exactas: {duplicados_exactos(metro)}",
           f"- Valores de ada: {dict(ada)}",
           f"- ada_northbound: {dict(Counter(m.get('ada_northbound') for m in metro))}",
           f"- ada_southbound: {dict(Counter(m.get('ada_southbound') for m in metro))}",
           f"- Distritos (borough): {dict(Counter(m.get('borough') for m in metro))}",
           f"- Rutas distintas en daytime_routes: {len(rutas)} -> {sorted(rutas)}",
           f"- Tipos de dato de gtfs_latitude: {dict(Counter(type(m.get('gtfs_latitude')).__name__ for m in metro))}"]
    md += tabla("Valores faltantes", faltantes(metro))

    # Citi Bike
    caps = [b.get("capacity") for b in bici if isinstance(b.get("capacity"), (int, float))]
    md += ["\n## Citi Bike (GBFS)", f"- Estaciones: {len(bici)}",
           f"- station_id (con valor, únicos): {unicidad(bici, 'station_id')}",
           f"- Filas duplicadas exactas: {duplicados_exactos(bici)}",
           f"- Capacidad total: {int(sum(caps))}; estaciones con capacidad 0: {sum(c == 0 for c in caps)}",
           f"- station_type: {dict(Counter(b.get('station_type') for b in bici))}",
           f"- region_id: {dict(Counter(b.get('region_id') for b in bici))}",
           f"- Campos por estación (máximo observado): {max(len(b) for b in bici)}"]
    md += tabla("Valores faltantes", faltantes(bici))

    salida = Path(a.datos) / "perfil_calidad.md"
    salida.write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))
    print(f"\nEscrito en {salida}")


if __name__ == "__main__":
    main()
