import pygame
import math
from config import *
#wasa

def dibujar_juego(pantalla, recursos, estado):
    """Función maestra de dibujado."""
    pantalla.fill(COLOR_FONDO)

    # Desempaquetamos el estado para usarlo fácil
    pantalla_inicio = estado["pantalla_inicio"]
    intro_activa = estado["intro_activa"]

    # --- CASO 1: PANTALLA DE INICIO ---
    if pantalla_inicio:
        _dibujar_inicio(pantalla, recursos)

    # --- CASO 2: ANIMACIÓN INTRO ---
    elif intro_activa:
        _dibujar_intro(pantalla, recursos, estado)

    # --- CASO 3: SIMULACIÓN NORMAL ---
    else:
        # Dibujar base
        _dibujar_elementos_base(pantalla, recursos, estado)
        # Título fijo
        pantalla.blit(recursos["titulo"], (POS_TITULO_FINAL_X, POS_TITULO_FINAL_Y))


# --- FUNCIONES PRIVADAS DE DIBUJO (Ayudantes) ---

def _dibujar_elementos_base(superficie, recursos, estado):
    """Dibuja CPU, Reloj, Botón y Dato (Lo común)."""
    # 1. Placa central
    rect_centro = recursos["centro"].get_rect(center=CENTRO_PANTALLA)
    superficie.blit(recursos["centro"], rect_centro)

    # 2. Waiting text
    if estado["enviando_dato"]:
        pos_w = (rect_centro.x + AJUSTE_WAITING_X, rect_centro.y + AJUSTE_WAITING_Y)
        superficie.blit(recursos["waiting"], pos_w)

    # 3. Puntero Reloj
    img_rotada = pygame.transform.rotate(recursos["puntero"], ANGULO_FIJO_RELOJ)
    pos_puntero = (rect_centro.x + AJUSTE_RELOJ_X, rect_centro.y + AJUSTE_RELOJ_Y)
    rect_rotado = img_rotada.get_rect(center=pos_puntero)
    superficie.blit(img_rotada, rect_rotado)

    # 4. El Dato (Bit)
    if estado["enviando_dato"]:
        offset = recursos["dato"].get_height() // 2
        superficie.blit(recursos["dato"], (estado["dato_x"], estado["dato_y"] - offset))

    # 5. Botón
    boton_rect = estado["boton_rect"]
    mouse_pos = pygame.mouse.get_pos()
    color = COLOR_BOTON_HOVER if boton_rect.collidepoint(mouse_pos) else COLOR_BOTON

    pygame.draw.rect(superficie, color, boton_rect, border_radius=10)

    # Texto del botón
    txt = recursos["fuente_boton"].render("INICIAR", True, COLOR_TEXTO)
    txt_rect = txt.get_rect(center=boton_rect.center)
    superficie.blit(txt, txt_rect)


def _dibujar_inicio(pantalla, recursos):
    """Dibuja el título gigante y el texto parpadeante."""
    # Título Grande
    img_t = recursos["titulo"]
    escala = 2.5
    nw = int(img_t.get_width() * escala)
    nh = int(img_t.get_height() * escala)
    img_grande = pygame.transform.smoothscale(img_t, (nw, nh))
    pantalla.blit(img_grande, img_grande.get_rect(center=CENTRO_PANTALLA))

    # Texto Parpadeante
    tiempo = pygame.time.get_ticks()
    alpha = int(abs(math.sin(tiempo / 500)) * 255)
    txt_enter = recursos["fuente_aviso"].render("Presione ENTER para iniciar", True, COLOR_TEXTO_ENTER)
    txt_enter.set_alpha(alpha)
    rect_enter = txt_enter.get_rect(center=(CENTRO_PANTALLA[0], CENTRO_PANTALLA[1] + 150))
    pantalla.blit(txt_enter, rect_enter)


def _dibujar_intro(pantalla, recursos, estado):
    """Calcula las interpolaciones de la intro."""
    progreso = estado["intro_progreso"]
    suavizado = 1 - pow(1 - progreso, 3)

    # A. Elementos base apareciendo (Fade In)
    capa = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA), pygame.SRCALPHA)
    _dibujar_elementos_base(capa, recursos, estado)
    capa.set_alpha(int(255 * suavizado))
    pantalla.blit(capa, (0, 0))

    # B. Título moviéndose
    img_t = recursos["titulo"]
    escala = 2.5 + (1.0 - 2.5) * suavizado
    nw = int(img_t.get_width() * escala)
    nh = int(img_t.get_height() * escala)
    img_anim = pygame.transform.smoothscale(img_t, (nw, nh))

    # Interpolación de posición
    xi, yi = CENTRO_PANTALLA
    # Centro destino: Posición final + mitad del tamaño de la imagen original
    xf = POS_TITULO_FINAL_X + img_t.get_width() // 2
    yf = POS_TITULO_FINAL_Y + img_t.get_height() // 2

    cur_x = xi + (xf - xi) * suavizado
    cur_y = yi + (yf - yi) * suavizado

    pantalla.blit(img_anim, img_anim.get_rect(center=(int(cur_x), int(cur_y))))