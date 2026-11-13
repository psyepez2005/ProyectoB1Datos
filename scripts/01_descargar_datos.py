"""Descarga las tres fuentes completas y guarda una copia con fecha de consulta.

Uso:  python scripts/01_descargar_datos.py [--salida datos]
Requiere: pip install requests
Genera en datos/: parks_properties_AAAAMMDD.json, mta_subway_stations_AAAAMMDD.json,
citibike_station_information_AAAAMMDD.json y manifiesto_AAAAMMDD.json
"""
import argparse, hashlib, json, datetime as dt
from pathlib import Path
import requests

FUENTES = {
    "parks_properties": "https://data.cityofnewyork.us/resource/enfh-gkve.json",
    "mta_subway_stations": "https://data.ny.gov/resource/39hk-dx4f.json",
}
GBFS = "https://gbfs.citibikenyc.com/gbfs/en/station_information.json"
PAGINA = 1000  # los multipolígonos pesan: páginas pequeñas


def socrata(url):
    filas, offset = [], 0
    while True:
        r = requests.get(url, params={"$limit": PAGINA, "$offset": offset, "$order": ":id"}, timeout=120)
        r.raise_for_status()
        lote = r.json()
        filas += lote
        if len(lote) < PAGINA:
            return filas
        offset += PAGINA


def guardar(ruta, obj):
    texto = json.dumps(obj, ensure_ascii=False)
    ruta.write_text(texto, encoding="utf-8")
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", default="datos")
    a = ap.parse_args()
    out = Path(a.salida); out.mkdir(parents=True, exist_ok=True)
    hoy = dt.date.today().strftime("%Y%m%d")
    manifiesto = {"fecha_consulta": dt.date.today().isoformat(), "fuentes": {}}

    for nombre, url in FUENTES.items():
        filas = socrata(url)
        sha = guardar(out / f"{nombre}_{hoy}.json", filas)
        manifiesto["fuentes"][nombre] = {"url": url, "registros": len(filas), "sha256": sha}
        print(f"{nombre}: {len(filas)} registros")

    r = requests.get(GBFS, timeout=120); r.raise_for_status()
    feed = r.json()
    sha = guardar(out / f"citibike_station_information_{hoy}.json", feed)
    est = feed["data"]["stations"]
    manifiesto["fuentes"]["citibike_station_information"] = {
        "url": GBFS, "registros": len(est), "last_updated_feed": feed.get("last_updated"), "sha256": sha}
    print(f"citibike_station_information: {len(est)} estaciones")

    (out / f"manifiesto_{hoy}.json").write_text(json.dumps(manifiesto, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
