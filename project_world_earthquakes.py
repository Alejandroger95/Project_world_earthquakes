import requests
from pymongo import MongoClient
import time
from datetime import datetime

# --- FILTROS PERSONALIZABLES ---
CONFIG = {
    # Conexión local a MongoDB
    "mongo_uri": "mongodb://localhost:27017/",
    "db_name": "geo_monitoring_db",
    "collection": "world_earthquakes",

    # Borramos los  datos viejos antes de empezar la nueva carga
    "limpiar_coleccion_antes": True, 

    # Rango de Fechas y Magnitud Mínima
    "anio_inicio": 1900,
    "anio_fin": 2026,
    "magnitud_min": 4.5,

    # --- FILTROS OPCIONALES (Descomentar para activar) ---
    # "minlatitude": -18.5, 
    # "maxlatitude": 0,      
    # "minlongitude": -81.5, 
    # "maxlongitude": -68.5,  
    # "tsunami": 1,           
    
    "eventtype": "earthquake", 
    "orderby": "time",
    "format": "geojson"
}


def ejecutar_ingesta():
    # Conexión a MongoDB
    client = MongoClient(CONFIG["mongo_uri"])
    db = client[CONFIG["db_name"]]
    coleccion = db[CONFIG["collection"]]

    # Limpieza previa de la colección
    if CONFIG["limpiar_coleccion_antes"]:
        print(f"--- Limpiando colección '{CONFIG['collection']}' ---")
        coleccion.drop() 
        print("   [OK] Espacio liberado para nueva carga.\n")

    url_api = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    
    print(f"--- Iniciando Ingesta Histórica (M{CONFIG['magnitud_min']}+) ---")
    print(f"Destino: {CONFIG['db_name']} > {CONFIG['collection']}")
    print(f"Periodo: {CONFIG['anio_inicio']} - {CONFIG['anio_fin']}")
    print(f"----------------------------------------------------------")

    # Bucle año por año para no saturar la RAM ni la API
    for anio in range(CONFIG["anio_inicio"], CONFIG["anio_fin"] + 1):
        print(f"Procesando año {anio}...", end="\r")
        
        # Parámetros base para la petición
        params = {
            "format": CONFIG["format"],
            "starttime": f"{anio}-01-01",
            "endtime": f"{anio}-12-31",
            "minmagnitude": CONFIG["magnitud_min"],
            "orderby": CONFIG["orderby"],
            "eventtype": CONFIG["eventtype"]
        }

        # Inyectar filtros adicionales si están presentes en el diccionario
        filtros_extras = ["minlatitude", "maxlatitude", "minlongitude", "maxlongitude", "tsunami"]
        for filtro in filtros_extras:
            if filtro in CONFIG:
                params[filtro] = CONFIG[filtro]

        try:
            response = requests.get(url_api, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                features = data.get('features', [])
                
                if features:
                    # Inserción masiva en MongoDB
                    coleccion.insert_many(features)
                    print(f"   [OK] Año {anio}: {len(features)} sismos guardados.")
                else:
                    # En años muy antiguos (1900s) puede no haber registros, lo cual es normal
                    print(f"   [!] Año {anio}: Sin registros encontrados.           ")
            
            elif response.status_code == 400:
                print(f"   [Error 400] Año {anio}: Demasiada data pedida.         ")
            else:
                print(f"   [Error API] Año {anio}: Status {response.status_code}   ")
                
        except Exception as e:
            print(f"   [Error Crítico] Año {anio}: {e}                         ")
        
        # Pausa breve para evitar saturar la API y respetar límites de tasa
        time.sleep(1)

    print("\n----------------------------------------------------------")
    print(f"--- ¡Ingesta Completada con Éxito! ---")
    print(f"Total de sismos en la base de datos: {coleccion.count_documents({})}")


if __name__ == "__main__":
    ejecutar_ingesta()