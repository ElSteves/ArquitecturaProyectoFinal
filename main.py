import pygame
import sys
import math  # Importamos math para el efecto de parpadeo suave

# 1. Inicializar Pygame
pygame.init()

# --- CONFIGURACIÓN GENERAL ---
ANCHO_VENTANA = 1080
ALTO_VENTANA = 720
COLOR_FONDO = (30, 30, 30)
COLOR_BOTON = (0, 150, 0)
COLOR_BOTON_HOVER = (0, 200, 0)
COLOR_TEXTO = (255, 255, 255)
COLOR_TEXTO_ENTER = (200, 200, 200)  # Un blanco un poco gris para el texto de abajo

pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA), pygame.RESIZABLE)

pygame.display.set_caption("Simulación: Cuello de Botella (1920x1080)")
fuente = pygame.font.SysFont("Arial", 24, bold=True)
fuente_aviso = pygame.font.SysFont("Arial", 30, bold=False)  # Fuente para "Presione Enter"

# --- CARGAR IMÁGENES ---
nombre_imagen_centro = "CPU- RAM-CLOCK.png"
nombre_imagen_titulo = "Titulo.png"
nombre_imagen_puntero = "imgCLOCK-puntero_base.png"
nombre_imagen_dato = "Bit brillando.png"
nombre_imagen_waiting = "waiting-text.png"

try:
    img_centro = pygame.image.load(nombre_imagen_centro)
    img_titulo = pygame.image.load(nombre_imagen_titulo)
    img_puntero = pygame.image.load(nombre_imagen_puntero)
    img_dato = pygame.image.load(nombre_imagen_dato)
    img_waiting = pygame.image.load(nombre_imagen_waiting)
except FileNotFoundError as e:
    print(f"Error al cargar imagen: {e}")
    sys.exit()

# --- POSICIONAMIENTO FIJO ---
rect_centro = img_centro.get_rect()
rect_centro.center = (ANCHO_VENTANA // 2, ALTO_VENTANA // 2)

# --- CONFIGURACIÓN INTRO Y ESTADOS ---
pantalla_inicio = True  # Estado 1: Pantalla de "Presione Enter"
intro_activa = False  # Estado 2: Animación de movimiento
tiempo_inicio_intro = 0
DURACION_INTRO = 2500  # AUMENTADO: 5 segundos para que sea más lento y suave

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

            # Si estamos en la pantalla de inicio y presionan ENTER
            if evento.key == pygame.K_RETURN:
                if pantalla_inicio:
                    pantalla_inicio = False
                    intro_activa = True
                    # Importante: reiniciamos el tiempo justo ahora para que la intro empiece desde 0
                    tiempo_inicio_intro = pygame.time.get_ticks()

            # Saltar intro con ESPACIO (opcional)
            if evento.key == pygame.K_SPACE and intro_activa:
                intro_activa = False

        if evento.type == pygame.MOUSEBUTTONDOWN:
            # Solo permitimos clic si YA PASÓ la intro y la pantalla de inicio
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
        # 1. Título Gigante en el centro (Escala 3.0 igual que el inicio de la animación)
        escala_inicio = 2.5
        ancho_t = int(img_titulo.get_width() * escala_inicio)
        alto_t = int(img_titulo.get_height() * escala_inicio)
        titulo_grande = pygame.transform.smoothscale(img_titulo, (ancho_t, alto_t))
        rect_titulo_grande = titulo_grande.get_rect(center=(ANCHO_VENTANA // 2, ALTO_VENTANA // 2))
        pantalla.blit(titulo_grande, rect_titulo_grande)

        # 2. Texto "Presione ENTER" con parpadeo suave
        # Usamos seno del tiempo para oscilar alpha
        tiempo = pygame.time.get_ticks()
        alpha_texto = int(abs(math.sin(tiempo / 500)) * 255)  # Oscila cada 0.5s aprox

        texto_enter = fuente_aviso.render("Presione ENTER para iniciar el programa", True, COLOR_TEXTO_ENTER)
        texto_enter.set_alpha(alpha_texto)  # Aplicamos transparencia

        rect_enter = texto_enter.get_rect(center=(ANCHO_VENTANA // 2, ALTO_VENTANA // 2 + 150))
        pantalla.blit(texto_enter, rect_enter)

    # ESTADO 2: ANIMACIÓN (INTRO)
    elif intro_activa:
        tiempo_actual = pygame.time.get_ticks()
        progreso = (tiempo_actual - tiempo_inicio_intro) / DURACION_INTRO

        if progreso >= 1.0:
            progreso = 1.0
            intro_activa = False  # Fin de la intro

        suavizado = 1 - pow(1 - progreso, 3)  # Cubic Ease Out

        # A. Elementos del juego apareciendo lentamente (Fade In)
        capa_juego = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA), pygame.SRCALPHA)
        dibujar_elementos_juego(capa_juego)
        alpha_actual = int(255 * suavizado)
        capa_juego.set_alpha(alpha_actual)
        pantalla.blit(capa_juego, (0, 0))

        # B. Título moviéndose y achicándose
        escala_inicial = 2.5
        escala_final = 1.0
        escala_actual = escala_inicial + (escala_final - escala_inicial) * suavizado

        ancho_t = int(img_titulo.get_width() * escala_actual)
        alto_t = int(img_titulo.get_height() * escala_actual)
        titulo_animado = pygame.transform.smoothscale(img_titulo, (ancho_t, alto_t))

        # Posiciones
        x_inicio = ANCHO_VENTANA // 2
        y_inicio = ALTO_VENTANA // 2
        x_fin = pos_titulo_final_x + img_titulo.get_width() // 2
        y_fin = pos_titulo_final_y + img_titulo.get_height() // 2

        x_actual = x_inicio + (x_fin - x_inicio) * suavizado
        y_actual = y_inicio + (y_fin - y_inicio) * suavizado

        rect_animado = titulo_animado.get_rect(center=(int(x_actual), int(y_actual)))
        pantalla.blit(titulo_animado, rect_animado)

    # ESTADO 3: PROGRAMA NORMAL
    else:
        dibujar_elementos_juego(pantalla)
        pantalla.blit(img_titulo, (pos_titulo_final_x, pos_titulo_final_y))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()