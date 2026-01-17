import pygame
import sys

# 1. Inicializar Pygame
pygame.init()

# --- CONFIGURACIÓN GENERAL ---
ANCHO_VENTANA = 1080
ALTO_VENTANA = 720
COLOR_FONDO = (30, 30, 30)
COLOR_BOTON = (0, 150, 0)
COLOR_BOTON_HOVER = (0, 200, 0)
COLOR_TEXTO = (255, 255, 255)

pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA), pygame.RESIZABLE)

pygame.display.set_caption("Simulación: Cuello de Botella (1920x1080)")
fuente = pygame.font.SysFont("Arial", 24, bold=True)

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

posicion_titulo = (50, 50)

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

# --- VARIABLES DEL RELOJ (MODIFICADO) ---
# He puesto 45 grados para intentar que apunte hacia arriba (ajústalo si es necesario).
# Antes esto cambiaba, ahora se queda fijo.
angulo_fijo = 45

# --- BUCLE PRINCIPAL ---
corriendo = True
clock = pygame.time.Clock()

while corriendo:
    mouse_pos = pygame.mouse.get_pos()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            corriendo = False

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                corriendo = False

        if evento.type == pygame.MOUSEBUTTONDOWN:
            if boton_rect.collidepoint(mouse_pos):
                if not enviando_dato:
                    enviando_dato = True
                    dato_x = inicio_cable_x

    # 1. Lógica del Reloj (SIMPLIFICADA)
    # Ya no restamos velocidad, simplemente aplicamos el ángulo fijo.
    img_puntero_rotada = pygame.transform.rotate(img_puntero, angulo_fijo)
    rect_puntero_rotado = img_puntero_rotada.get_rect(center=centro_fijo_puntero)

    # 2. Lógica del Dato
    if enviando_dato:
        dato_x += velocidad_dato
        if dato_x >= fin_cable_x:
            dato_x = fin_cable_x
            enviando_dato = False

    # --- DIBUJADO ---
    pantalla.fill(COLOR_FONDO)

    pantalla.blit(img_centro, rect_centro)

    if enviando_dato:
        pantalla.blit(img_waiting, posicion_waiting)

    pantalla.blit(img_puntero_rotada, rect_puntero_rotado)
    pantalla.blit(img_titulo, posicion_titulo)

    # Dibujar el Dato
    if enviando_dato:
        offset_centro_img = img_dato.get_height() // 2
        pantalla.blit(img_dato, (dato_x, dato_y - offset_centro_img))

    # Dibujar el Botón
    color_actual_boton = COLOR_BOTON_HOVER if boton_rect.collidepoint(mouse_pos) else COLOR_BOTON
    pygame.draw.rect(pantalla, color_actual_boton, boton_rect, border_radius=10)
    pantalla.blit(texto_boton, rect_texto_boton)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()