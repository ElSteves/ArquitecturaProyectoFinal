import pygame
import math
import random
from config import *


def _dibujar_tabla_program_counter(superficie, recursos, program_counter, simulacion_activa=False):
    """Dibuja la tabla del program counter y resalta el paso actual en verde solo si la simulación está activa."""
    # Posición inicial de la tabla
    tabla_x = 48
    tabla_y = 210
    
    # Redimensionar la tabla
    tabla_original = recursos["tabla"]
    ancho_nuevo = 280
    alto_nuevo = 310
    tabla_redimensionada = pygame.transform.scale(tabla_original, (ancho_nuevo, alto_nuevo))
    
    # Dibujar imagen de la tabla redimensionada
    superficie.blit(tabla_redimensionada, (tabla_x, tabla_y))
    
    # Resaltar el paso actual en verde SOLO si la simulación está activa
    if simulacion_activa and 1 <= program_counter <= 7:
        # Parámetros del resalte (ajustados para la tabla redimensionada)
        resalte_x = tabla_x + 8            # Posición X relativa al inicio de la tabla
        resalte_ancho = 262                 # Ancho del rectángulo de resalte
        resalte_alto = 32                  # Alto del rectángulo de resalte
        espaciado_entre_pasos = 33         # Distancia vertical entre cada paso
        resalte_y_inicio = tabla_y + 63    # Posición Y del primer paso
        
        # Calcular Y según el paso actual
        resalte_y = resalte_y_inicio + (program_counter - 1) * espaciado_entre_pasos
        
        # Crear rectángulo de resalte
        rect_resalte = pygame.Rect(resalte_x, resalte_y, resalte_ancho, resalte_alto)
        
        # Dibujar rectángulo verde semitransparente
        superficie_resalte = pygame.Surface((resalte_ancho, resalte_alto))
        superficie_resalte.set_alpha(120)  # Transparencia: 0-255 (120 = semi-transparente)
        superficie_resalte.fill((0, 255, 0))  # Verde
        superficie.blit(superficie_resalte, rect_resalte)


def dibujar_juego(pantalla, recursos, estado, bits, bit_reloj, slider_frecuencia=None, slider_latencia=None, program_counter=1):
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
        _dibujar_intro(pantalla, recursos, estado, bits, bit_reloj, slider_frecuencia, slider_latencia)

    # --- CASO 3: SIMULACIÓN NORMAL ---
    else:
        # Dibujar base
        _dibujar_elementos_base(pantalla, recursos, estado, bits, bit_reloj)
        # Título fijo
        pantalla.blit(pygame.transform.smoothscale(recursos["titulo"], (int(recursos["titulo"].get_width() * 0.2),
                                                                        int(recursos["titulo"].get_height() * 0.2))),
                      (POS_TITULO_FINAL_X, POS_TITULO_FINAL_Y))

        # Dibujar tabla del Program Counter
        _dibujar_tabla_program_counter(pantalla, recursos, program_counter, estado.get("simulacion", False))

        # Dibujar sliders si existen (se atenuarán cuando la simulación esté activa)
        if slider_frecuencia and slider_latencia:
            disabled = estado.get("simulacion", False)
            slider_frecuencia.dibujar(pantalla, recursos["fuente_aviso"], disabled=disabled)
            slider_latencia.dibujar(pantalla, recursos["fuente_aviso"], disabled=disabled)


# --- FUNCIONES PRIVADAS DE DIBUJO (Ayudantes) ---

def _dibujar_elementos_base(superficie, recursos, estado, bits, bit_reloj):
    """Dibuja CPU, Reloj, Botón y Dato (Lo común)."""
    # 1. Placa central
    rect_centro = recursos["centro"].get_rect(center=CENTRO_PANTALLA)
    superficie.blit(recursos["centro"], rect_centro)

    # 2. Texto de pantalla cpu
    # if bits["enviando"] :
    #     pos_w = (rect_centro.x + AJUSTE_WAITING_X, rect_centro.y + AJUSTE_WAITING_Y)
    if estado["waiting"]:
        pos_w = (rect_centro.x + AJUSTE_WAITING_X, rect_centro.y + AJUSTE_WAITING_Y)
        superficie.blit(recursos["waiting"], pos_w)
    if estado["fetching"]:
        pos_f = (rect_centro.x + AJUSTE_FETCH_X, rect_centro.y + AJUSTE_FETCH_Y)
        superficie.blit(recursos["fetch"], pos_f)
    if estado["exec"]:
        pos_e = (rect_centro.x + AJUSTE_EXEC_X, rect_centro.y + AJUSTE_EXEC_Y)
        superficie.blit(recursos["exec"], pos_e)

    # 3. Puntero Reloj
    angulo = -45 if bit_reloj["estado"] == True else 90
    img_rotada = pygame.transform.rotate(recursos["puntero"], angulo)
    pos_puntero = (rect_centro.x + AJUSTE_RELOJ_X, rect_centro.y + AJUSTE_RELOJ_Y)
    rect_rotado = img_rotada.get_rect(center=pos_puntero)
    superficie.blit(img_rotada, rect_rotado)

    # 4. El Dato (Bit)

    if bits["enviando"]:
        offset = recursos["dato"].get_height() // 2
        for i in range(8):
            if bits["activo"][i]:
                superficie.blit(recursos["dato"], (bits["x"], bits["y"][i] - offset))

    # Bit del rejol
    if bit_reloj["enviando"]:
        offset = recursos["dato"].get_height() // 2
        superficie.blit(recursos["dato"],
                        (bit_reloj["x_d"] - 25, bit_reloj["y_d"] - offset))
        superficie.blit(recursos["dato"],
                        (bit_reloj["x_i"] - 25, bit_reloj["y_i"] - offset))

    # 5. Botón Iniciar con animación
    boton_rect = estado["boton_rect"]
    mouse_pos = pygame.mouse.get_pos()
    color = COLOR_BOTON_HOVER if boton_rect.collidepoint(mouse_pos) else COLOR_BOTON

    # Aplicar escala de animación al botón Iniciar
    tamaño_boton = estado.get("tamaño_boton_actual", 1.0)
    ancho_animado = int(boton_rect.width * tamaño_boton)
    alto_animado = int(boton_rect.height * tamaño_boton)
    offset_x = (boton_rect.width - ancho_animado) // 2
    offset_y = (boton_rect.height - alto_animado) // 2

    rect_boton_animado = pygame.Rect(
        boton_rect.x + offset_x,
        boton_rect.y + offset_y,
        ancho_animado,
        alto_animado
    )

    pygame.draw.rect(superficie, color, rect_boton_animado, border_radius=10)

    # Texto del botón
    txt = recursos["fuente_boton"].render("INICIAR", True, COLOR_TEXTO)
    txt_rect = txt.get_rect(center=rect_boton_animado.center)
    superficie.blit(txt, txt_rect)

    # 6. Botón Parar con animación
    boton_parar_rect = estado.get("boton_parar_rect")
    if boton_parar_rect:
        color_parar = (200, 50, 50) if boton_parar_rect.collidepoint(mouse_pos) else (150, 30, 30)

        # Aplicar escala de animación al botón Parar
        tamaño_parar = estado.get("tamaño_parar_actual", 1.0)
        ancho_parar_animado = int(boton_parar_rect.width * tamaño_parar)
        alto_parar_animado = int(boton_parar_rect.height * tamaño_parar)
        offset_parar_x = (boton_parar_rect.width - ancho_parar_animado) // 2
        offset_parar_y = (boton_parar_rect.height - alto_parar_animado) // 2

        rect_parar_animado = pygame.Rect(
            boton_parar_rect.x + offset_parar_x,
            boton_parar_rect.y + offset_parar_y,
            ancho_parar_animado,
            alto_parar_animado
        )

        pygame.draw.rect(superficie, color_parar, rect_parar_animado, border_radius=10)
        txt_parar = recursos["fuente_boton"].render("PARAR", True, COLOR_TEXTO)
        txt_parar_rect = txt_parar.get_rect(center=rect_parar_animado.center)
        superficie.blit(txt_parar, txt_parar_rect)


def _dibujar_inicio(pantalla, recursos):
    """Dibuja el título gigante y el texto parpadeante."""
    # Título Grande
    img_t = recursos["titulo"]
    escala = 0.5
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


def _dibujar_intro(pantalla, recursos, estado, bits, bit_reloj, slider_frecuencia=None, slider_latencia=None):
    """Calcula las interpolaciones de la intro."""
    progreso = estado["intro_progreso"]
    suavizado = 1 - pow(1 - progreso, 3)

    # A. Elementos base apareciendo (Fade In)
    capa = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA), pygame.SRCALPHA)
    _dibujar_elementos_base(capa, recursos, estado, bits, bit_reloj)
    capa.set_alpha(int(255 * suavizado))
    pantalla.blit(capa, (0, 0))

    # Sliders con fade in
    if slider_frecuencia and slider_latencia:
        capa_sliders = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA), pygame.SRCALPHA)
        # En la intro siempre están activos (no deshabilitados)
        slider_frecuencia.dibujar(capa_sliders, recursos["fuente_aviso"], disabled=False)
        slider_latencia.dibujar(capa_sliders, recursos["fuente_aviso"], disabled=False)
        capa_sliders.set_alpha(int(255 * suavizado))
        pantalla.blit(capa_sliders, (0, 0))

    # B. Título moviéndose
    img_t = recursos["titulo"]
    escala = 0.5 + (0.2 - 0.5) * suavizado
    nw = int(img_t.get_width() * escala)
    nh = int(img_t.get_height() * escala)
    img_anim = pygame.transform.smoothscale(img_t, (nw, nh))

    # Interpolación de posición
    xi, yi = CENTRO_PANTALLA
    # Centro destino: Posición final + mitad del tamaño de la imagen original
    xf = POS_TITULO_FINAL_X + (img_t.get_width()) * 0.2 // 2
    yf = POS_TITULO_FINAL_Y + (img_t.get_height()) * 0.2 // 2

    cur_x = xi + (xf - xi) * suavizado
    cur_y = yi + (yf - yi) * suavizado

    pantalla.blit(img_anim, img_anim.get_rect(center=(int(cur_x), int(cur_y))))