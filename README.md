# Práctica bimestral 1B: Parques y transporte en Nueva York

Carpetas: `datos` (archivos descargados y perfiles), `modelos` (MER), `rdf` (esquema y Turtle), `scripts`.

## Cómo reproducir (desde la raíz del repositorio)
```
pip install requests shapely pyproj
python scripts/01_descargar_datos.py     # descarga las tres fuentes en datos/
python scripts/02_perfilar_calidad.py    # escribe datos/perfil_calidad.md
python scripts/03_umbral_proximidad.py   # escribe datos/sensibilidad_umbral.md
```

## Modelo entidad-relación
`modelos/mer.mmd` (Mermaid) y `modelos/mer.png`. Para volver a renderizar en blanco y negro:
`mmdc -i modelos/mer.mmd -o modelos/mer.png -c modelos/mermaid-bw.json -s 3 -b white`
