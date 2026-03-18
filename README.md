# Project World Earthquakes 🌍🌋

Este proyecto descarga datos de terremotos a nivel mundial usando una API y los almacena en una base de datos **MongoDB**.
El analisis se desarrollo en MongoDB, debido a que es un entregable para el Master de Data science en la Universidad Complutense de MAdrid.

## Características del Script
* **Segmentación Anual:** Descarga datos año por año para optimizar el uso de memoria y respetar los límites de la API.
* **Filtros Personalizables:** Permite ajustar magnitud mínima, rango de años y coordenadas geográficas.
* **Almacenamiento NoSQL:** Los datos se guardan en formato GeoJSON directamente en MongoDB.

## Requisitos
* Python 3.12+
* MongoDB corriendo localmente (puerto 27017)

## Instalación

1. Clonar el repositorio.
2. Crear el entorno virtual:
   ```bash
   python3 -m venv venv
   ```
3. Activar el entorno:
   ```bash
   source venv/bin/activate
   ```
4. Instalar librerías:
   ```bash
   pip install -r requirements.txt
   ```

## Uso
Ejecuta el script principal:
```bash
python3 project_world_earthquakes.py
```
