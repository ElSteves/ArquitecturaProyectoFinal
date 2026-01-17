import pygame
import sys
import math
import os  # <--- IMPORTANTE: Necesario para navegar entre carpetas

# 1. Inicializar Pygame
pygame.init()

# --- CONFIGURACIÓN GENERAL ---
ANCHO_VENTANA = 1080
ALTO_VENTANA = 720

# Color de fondo (Púrpura pizarra)
COLOR_FONDO = (107, 102, 128)

COLOR_BOTON = (0, 150, 0)
COLOR_BOTON_HOVER = (0, 200, 0)
COLOR_TEXTO = (255, 255, 255)
COLOR_TEXTO_ENTER = (200, 200, 200)

pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA), pygame.RESIZABLE)

pygame.display.set_caption("Simulación: Cuello de Botella (1920x1080)")
fuente = pygame.font.SysFont("Arial", 24, bold=True)
fuente_aviso = pygame.font.SysFont("Arial", 30, bold=False)

# --- CARGAR IMÁGENES DESDE CARPETA ---
# Definimos el nombre de la carpeta donde pusiste las imágenes
CARPETA_IMAGENES = "assets"

# Nombres de los archivos
nombre_imagen_centro = "CPU- RAM-CLOCK.png"
nombre_imagen_titulo = "Titulo.png"
nombre_imagen_puntero = "imgCLOCK-puntero_base.png"
nombre_imagen_dato = "Bit brillando.png"
nombre_imagen_waiting = "waiting-text.png"

try:
    # Usamos os.path.join para construir la ruta: "assets/archivo.png"
    ruta_centro = os.path.join(CARPETA_IMAGENES, nombre_imagen_centro)
    img_centro = pygame.image.load(ruta_centro)

    ruta_titulo = os.path.join(CARPETA_IMAGENES, nombre_imagen_titulo)
    img_titulo = pygame.image.load(ruta_titulo)

    ruta_dato = os.path.join(CARPETA_IMAGENES, nombre_imagen_dato)
    img_dato = pygame.image.load(ruta_dato)

    ruta_waiting = os.path.join(CARPETA_IMAGENES, nombre_imagen_waiting)
    img_waiting = pygame.image.load(ruta_waiting)

    # --- AJUSTE DEL PUNTERO ---
    ruta_puntero = os.path.join(CARPETA_IMAGENES, nombre_imagen_puntero)
    img_puntero_original = pygame.image.load(ruta_puntero)

    # Factor de escala: 0.6 (60%)
    FACTOR_ESCALA_PUNTERO = 0.6

    nuevo_ancho_p = int(img_puntero_original.get_width() * FACTOR_ESCALA_PUNTERO)
    nuevo_alto_p = int(img_puntero_original.get_height() * FACTOR_ESCALA_PUNTERO)
    img_puntero = pygame.transform.scale(img_puntero_original, (nuevo_ancho_p, nuevo_alto_p))

except FileNotFoundError as e:
    print(f"Error al cargar imagen: {e}")
    print(f"Asegúrate de que la carpeta '{CARPETA_IMAGENES}' exista y tenga las imágenes dentro.")
    sys.exit()

# --- POSICIONAMIENTO FIJO ---
rect_centro = img_centro.get_rect()
rect_centro.center = (ANCHO_VENTANA // 2, ALTO_VENTANA // 2)

# --- CONFIGURACIÓN INTRO Y ESTADOS ---
pantalla_inicio = True
intro_activa = False
tiempo_inicio_intro = 0
DURACION_INTRO = 2000  # 2 segundos

# Posición final del título
pos_titulo_final_x = 50
pos_titulo_final_y = 50

# --- AJUSTES RELATIVOS ---
AJUSTE_RELOJ_X = 255
AJUSTE_RELOJ_Y = 48
centro_fijo_puntero = (rect_centro.x + AJUSTE_RELOJ_X, rect_centro.y + AJUSTE_RELOJ_Y)

AJUSTE_WAITING_X = 23
AJUSTE_WAITING_Y = 225
posicion_waiting = (rect_centro.x + AJUSTE_WAITING_X, rect_centro.y + AJUSTE_WAITING_Y)

# --- CONFIGURACIÓN DEL BOTÓN ---
boton_rect = pygame.Rect(0, 0, 150, 50)
boton_rect.center = (ANCHO_VENTANA // 2, ALTO_VENTANA - 100)

texto_boton = fuente.render("INICIAR", True, COLOR_TEXTO)
rect_texto_boton = texto_boton.get_rect(center=boton_rect.center)

# --- CONFIGURACIÓN DE ANIMACIÓN DE DATOS ---
OFFSET_Y_CABLE = 25
inicio_cable_x = rect_centro.left + 140
fin_cable_x = rect_centro.right - 100
altura_cable_y = rect_centro.center[1] + OFFSET_Y_CABLE

dato_x = inicio_cable_x
dato_y = altura_cable_y
enviando_dato = False
velocidad_dato = 5

# --- VARIABLES DEL RELOJ ---
angulo_fijo = 45


# --- FUNCIONES AUXILIARES ---
def dibujar_elementos_juego(superficie):
    """Dibuja las cosas MENOS el título."""
    superficie.blit(img_centro, rect_centro)
    if enviando_dato:
        superficie.blit(img_waiting, posicion_waiting)

    # Dibujamos el puntero (que ahora es más pequeño)
    img_puntero_rotada = pygame.transform.rotate(img_puntero, angulo_fijo)
    rect_puntero_rotado = img_puntero_rotada.get_rect(center=centro_fijo_puntero)
    superficie.blit(img_puntero_rotada, rect_puntero_rotado)

    if enviando_dato:
        offset_centro_img = img_dato.get_height() // 2
        superficie.blit(img_dato, (dato_x, dato_y - offset_centro_img))

    color_actual_boton = COLOR_BOTON_HOVER if boton_rect.collidepoint(pygame.mouse.get_pos()) else COLOR_BOTON
    pygame.draw.rect(superficie, color_actual_boton, boton_rect, border_radius=10)
    superficie.blit(texto_boton, rect_texto_boton)


# --- BUCLE PRINCIPAL ---
corriendo = True
clock = pygame.time.Clock()

while corriendo:
    mouse_pos = pygame.mouse.get_pos()

    # --- EVENTOS ---
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            corriendo = False

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                corriendo = False

            # ENTER para iniciar
            if evento.key == pygame.K_RETURN:
                if pantalla_inicio:
                    pantalla_inicio = False
                    intro_activa = True
                    tiempo_inicio_intro = pygame.time.get_ticks()

            # ESPACIO para saltar intro
            if evento.key == pygame.K_SPACE and intro_activa:
                intro_activa = False

        if evento.type == pygame.MOUSEBUTTONDOWN:
            if not pantalla_inicio and not intro_activa:
                if boton_rect.collidepoint(mouse_pos):
                    if not enviando_dato:
                        enviando_dato = True
                        dato_x = inicio_cable_x

    # --- LÓGICA DE JUEGO GENERAL ---
    if not pantalla_inicio and not intro_activa and enviando_dato:
        dato_x += velocidad_dato
        if dato_x >= fin_cable_x:
            dato_x = fin_cable_x
            enviando_dato = False

    # --- DIBUJADO ---
    pantalla.fill(COLOR_FONDO)

    # ESTADO 1: PANTALLA DE INICIO
    if pantalla_inicio:
        escala_inicio = 2.5
        ancho_t = int(img_titulo.get_width() * escala_inicio)
        alto_t = int(img_titulo.get_height() * escala_inicio)
        titulo_grande = pygame.transform.smoothscale(img_titulo, (ancho_t, alto_t))
        rect_titulo_grande = titulo_grande.get_rect(center=(ANCHO_VENTANA // 2, ALTO_VENTANA // 2))
        pantalla.blit(titulo_grande, rect_titulo_grande)

        # Texto parpadeante
        tiempo = pygame.time.get_ticks()
        alpha_texto = int(abs(math.sin(tiempo / 500)) * 255)

        texto_enter = fuente_aviso.render("Presione ENTER para iniciar el programa", True, COLOR_TEXTO_ENTER)
        texto_enter.set_alpha(alpha_texto)

        rect_enter = texto_enter.get_rect(center=(ANCHO_VENTANA // 2, ALTO_VENTANA // 2 + 150))
        pantalla.blit(texto_enter, rect_enter)

    # ESTADO 2: ANIMACIÓN (INTRO)
    elif intro_activa:
        tiempo_actual = pygame.time.get_ticks()
        progreso = (tiempo_actual - tiempo_inicio_intro) / DURACION_INTRO

        if progreso >= 1.0:
            progreso = 1.0
            intro_activa = False

        suavizado = 1 - pow(1 - progreso, 3)

        # Fade In del juego
        capa_juego = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA), pygame.SRCALPHA)
        dibujar_elementos_juego(capa_juego)
        alpha_actual = int(255 * suavizado)
        capa_juego.set_alpha(alpha_actual)
        pantalla.blit(capa_juego, (0, 0))

        # Movimiento del Título
        escala_inicial = 2.5
        escala_final = 1.0
        escala_actual = escala_inicial + (escala_final - escala_inicial) * suavizado

        ancho_t = int(img_titulo.get_width() * escala_actual)
        alto_t = int(img_titulo.get_height() * escala_actual)
        titulo_animado = pygame.transform.smoothscale(img_titulo, (ancho_t, alto_t))

        x_inicio = ANCHO_VENTANA // 2
        y_inicio = ALTO_VENTANA // 2
        x_fin = pos_titulo_final_x + img_titulo.get_width() // 2
        y_fin = pos_titulo_final_y + img_titulo.get_height() // 2

        x_actual = x_inicio + (x_fin - x_inicio) * suavizado
        y_actual = y_inicio + (y_fin - y_inicio) * suavizado

        rect_animado = titulo_animado.get_rect(center=(int(x_actual), int(y_actual)))
        pantalla.blit(titulo_animado, rect_animado)

    # ESTADO 3: JUEGO NORMAL
    else:
        dibujar_elementos_juego(pantalla)
        pantalla.blit(img_titulo, (pos_titulo_final_x, pos_titulo_final_y))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()