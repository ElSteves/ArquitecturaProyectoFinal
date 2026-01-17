import pygame
import sys

# 1. Inicializar Pygame
pygame.init()

# --- CONFIGURACIÓN GENERAL ---
ANCHO_VENTANA = 800
ALTO_VENTANA = 600
COLOR_FONDO = (30, 30, 30)
COLOR_BOTON = (0, 150, 0)
COLOR_BOTON_HOVER = (0, 200, 0)
COLOR_TEXTO = (255, 255, 255)

pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
pygame.display.set_caption("Simulación: Cuello de Botella")
fuente = pygame.font.SysFont("Arial", 24, bold=True)

# --- CARGAR IMÁGENES ---
nombre_imagen_centro = "CPU- RAM-CLOCK.png"  # Placa base
nombre_imagen_titulo = "Titulo.png"  # Título
nombre_imagen_puntero = "imgCLOCK-puntero_base.png"  # Puntero
nombre_imagen_dato = "Bit brillando.png"  # Dato (punto azul)
nombre_imagen_waiting = "waiting-text.png"  # <-- NUEVA IMAGEN "Waiting..."

try:
    img_centro = pygame.image.load(nombre_imagen_centro)
    img_titulo = pygame.image.load(nombre_imagen_titulo)
    img_puntero = pygame.image.load(nombre_imagen_puntero)
    img_dato = pygame.image.load(nombre_imagen_dato)
    # Cargamos la nueva imagen de espera
    img_waiting = pygame.image.load(nombre_imagen_waiting)
except FileNotFoundError as e:
    print(f"Error al cargar imagen: {e}")
    print("Asegúrate de que todos los archivos .png estén en la carpeta.")
    sys.exit()

# --- POSICIONAMIENTO FIJO ---
rect_centro = img_centro.get_rect()
rect_centro.center = (ANCHO_VENTANA // 2, ALTO_VENTANA // 2)

posicion_titulo = (10, 10)

# Puntero del reloj
AJUSTE_RELOJ_X = 252
AJUSTE_RELOJ_Y = 48
centro_fijo_puntero = (rect_centro.x + AJUSTE_RELOJ_X, rect_centro.y + AJUSTE_RELOJ_Y)

# Posición de la imagen "Waiting..." dentro del recuadro de la CPU
# Ajusta estos valores si no queda perfectamente centrado en tu recuadro
AJUSTE_WAITING_X = 23
AJUSTE_WAITING_Y = 225
posicion_waiting = (rect_centro.x + AJUSTE_WAITING_X, rect_centro.y + AJUSTE_WAITING_Y)

# --- CONFIGURACIÓN DEL BOTÓN ---
boton_rect = pygame.Rect(0, 0, 150, 50)
boton_rect.center = (ANCHO_VENTANA // 2, ALTO_VENTANA - 60)
texto_boton = fuente.render("INICIAR", True, COLOR_TEXTO)
rect_texto_boton = texto_boton.get_rect(center=boton_rect.center)

# --- CONFIGURACIÓN DE ANIMACIÓN DE DATOS ---
OFFSET_Y_CABLE = 25
inicio_cable_x = rect_centro.left + 140
fin_cable_x = rect_centro.right - 100
altura_cable_y = rect_centro.center[1] + OFFSET_Y_CABLE

# Estado del dato
dato_x = inicio_cable_x
dato_y = altura_cable_y
enviando_dato = False
velocidad_dato = 5

# --- VARIABLES DEL RELOJ ---
angulo = 0
velocidad_rotacion = 2

# --- BUCLE PRINCIPAL ---
corriendo = True
clock = pygame.time.Clock()

while corriendo:
    mouse_pos = pygame.mouse.get_pos()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            corriendo = False

        if evento.type == pygame.MOUSEBUTTONDOWN:
            if boton_rect.collidepoint(mouse_pos):
                if not enviando_dato:
                    enviando_dato = True
                    dato_x = inicio_cable_x

    # 1. Lógica del Reloj
    angulo -= velocidad_rotacion
    if angulo <= -360: angulo = 0
    img_puntero_rotada = pygame.transform.rotate(img_puntero, angulo)
    rect_puntero_rotado = img_puntero_rotada.get_rect(center=centro_fijo_puntero)

    # 2. Lógica del Dato
    if enviando_dato:
        dato_x += velocidad_dato
        if dato_x >= fin_cable_x:
            dato_x = fin_cable_x
            enviando_dato = False  # El dato llegó, el estado "waiting" debe terminar

    # --- DIBUJADO ---
    pantalla.fill(COLOR_FONDO)

    # A. Imágenes Base
    pantalla.blit(img_centro, rect_centro)

    # NUEVO: Dibujar "Waiting..." solo si se está enviando el dato
    if enviando_dato:
        pantalla.blit(img_waiting, posicion_waiting)

    pantalla.blit(img_puntero_rotada, rect_puntero_rotado)
    pantalla.blit(img_titulo, posicion_titulo)

    # B. Dibujar el Dato
    if enviando_dato:
        offset_centro_img = img_dato.get_height() // 2
        pantalla.blit(img_dato, (dato_x, dato_y - offset_centro_img))

    # C. Dibujar el Botón
    color_actual_boton = COLOR_BOTON_HOVER if boton_rect.collidepoint(mouse_pos) else COLOR_BOTON
    pygame.draw.rect(pantalla, color_actual_boton, boton_rect, border_radius=10)
    pantalla.blit(texto_boton, rect_texto_boton)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()