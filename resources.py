import pygame
import os
import sys
from config import *
#wasa

def cargar_recursos():
    """Carga todas las imágenes y fuentes, retornando un diccionario."""
    recursos = {}

    # Nombres de archivos
    nombres = {
        "centro": "CPU- RAM-CLOCK.png",
        "titulo": "Titulo.png",
        "puntero": "imgCLOCK-puntero_base.png",
        "dato": "Bit brillando.png",
        "waiting": "waiting-text.png"
    }

    try:
        # Cargar imágenes básicas
        for clave, archivo in nombres.items():
            ruta = os.path.join(CARPETA_IMAGENES, archivo)
            img = pygame.image.load(ruta)
            recursos[clave] = img

        # --- PROCESAMIENTO ESPECIAL: EL PUNTERO ---
        # Reemplazamos la imagen del puntero original por la escalada
        img_puntero_orig = recursos["puntero"]
        factor = 0.6
        nw = int(img_puntero_orig.get_width() * factor)
        nh = int(img_puntero_orig.get_height() * factor)
        recursos["puntero"] = pygame.transform.scale(img_puntero_orig, (nw, nh))

        # --- FUENTES ---
        recursos["fuente_boton"] = pygame.font.SysFont("Arial", 24, bold=True)
        recursos["fuente_aviso"] = pygame.font.SysFont("Arial", 30, bold=False)

    except FileNotFoundError as e:
        print(f"Error cargando recursos: {e}")
        print(f"Verifica que la carpeta '{CARPETA_IMAGENES}' exista.")
        sys.exit()

    return recursos