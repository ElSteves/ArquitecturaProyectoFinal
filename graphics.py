import pygame
import math
import random
from config import *


def _dibujar_tabla_program_counter(superficie, recursos, program_counter, highlight_scale=0.0):
    """Dibuja la tabla del program counter y resalta el paso actual con animación de escala."""
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
    
    # Resaltar el paso actual si la escala es visible (> 0.01)
    if highlight_scale > 0.01 and 1 <= program_counter <= 7:
        # Parámetros del resalte (ajustados para la tabla redimensionada)
        resalte_x = tabla_x + 8            # Posición X relativa al inicio de la tabla
        resalte_ancho = 262                 # Ancho del rectángulo de resalte
        resalte_alto = 32                  # Alto del rectángulo de resalte
        espaciado_entre_pasos = 33         # Distancia vertical entre cada paso
        resalte_y_inicio = tabla_y + 63    # Posición Y del primer paso
        
        # Calcular Y según el paso actual
        resalte_y = resalte_y_inicio + (program_counter - 1) * espaciado_entre_pasos
        
        # Calcular dimensiones animadas (Pop Up / Pop Out)
        ancho_actual = int(resalte_ancho * highlight_scale)
        alto_actual = int(resalte_alto * highlight_scale)

        # Calcular centro para que crezca desde el medio
        centro_x = resalte_x + resalte_ancho // 2
        centro_y = resalte_y + resalte_alto // 2
        
        # Crear rectángulo centrado con el tamaño animado
        rect_resalte = pygame.Rect(0, 0, ancho_actual, alto_actual)
        rect_resalte.center = (centro_x, int(centro_y))
        
        # Dibujar rectángulo amarillo semitransparente
        superficie_resalte = pygame.Surface((ancho_actual, alto_actual))
        superficie_resalte.set_alpha(120)  # Transparencia: 0-255 (120 = semi-transparente)
        superficie_resalte.fill((255, 255, 0))  # Amarillo brillante
        superficie.blit(superficie_resalte, rect_resalte)


def dibujar_juego(pantalla, recursos, estado, bits, bit_reloj, slider_frecuencia=None, slider_latencia=None, program_counter=1, tiempo=0, ciclos=0, eficiencia=0, tiempo_ocio=0):
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
        frec_actual = slider_frecuencia.obtener_valor() if slider_frecuencia else 0
        # Dibujar base
        _dibujar_elementos_base(pantalla, recursos, estado, bits, bit_reloj, frecuencia=frec_actual)
        # Título fijo
        pantalla.blit(pygame.transform.smoothscale(recursos["titulo"], (int(recursos["titulo"].get_width() * 0.2),
                                                                        int(recursos["titulo"].get_height() * 0.2))),
                      (POS_TITULO_FINAL_X, POS_TITULO_FINAL_Y))

        # Dibujar tabla del Program Counter
        _dibujar_tabla_program_counter(pantalla, recursos, program_counter, estado.get("pc_highlight_scale", 0.0))

        # Dibujar HUD de estadísticas (Nuevo UI)
        _dibujar_estadisticas(pantalla, recursos, tiempo, ciclos)

        # Dibujar Resultados Finales (Estadísticas y Botón)
        if estado.get("mostrar_stats", False):
            _dibujar_resultados_finales(pantalla, recursos, estado, eficiencia, tiempo_ocio)

        fuente = pygame.font.SysFont("Montserrat", 20, bold=False)
        # Dibujar sliders si existen (se atenuarán cuando la simulación esté activa)
        if slider_frecuencia and slider_latencia:
            disabled = estado.get("simulacion", False)
            slider_frecuencia.dibujar(pantalla, fuente, disabled=disabled)
            slider_latencia.dibujar(pantalla, fuente, disabled=disabled)


# --- FUNCIONES PRIVADAS DE DIBUJO (Ayudantes) ---

def _dibujar_elementos_base(superficie, recursos, estado, bits, bit_reloj, frecuencia=0):
    """Dibuja CPU, Reloj, Botón y Dato (Lo común)."""
    # 1. Placa central
    rect_centro = recursos["centro"].get_rect(center=CENTRO_PANTALLA)
    superficie.blit(recursos["centro"], rect_centro)

    # 2. Efectos CPU (Humo y Calor) - Se dibuja sobre la placa pero bajo los textos/cables
    _dibujar_efectos_cpu(superficie, estado, frecuencia)

    # 3. Texto de pantalla cpu
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
        color_parar = COLOR_BTN_PARAR_HOVER if boton_parar_rect.collidepoint(mouse_pos) else COLOR_BTN_PARAR

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

    # 7. Botón Fast Forward (FF)
    boton_ff_rect = estado.get("boton_ff_rect")
    if boton_ff_rect:
        activo = estado.get("ff_activo", False)
        
        # Color: Naranja brillante si está activo, naranja oscuro si no
        color_ff = (255, 200, 50) if activo else (200, 140, 20)
        if boton_ff_rect.collidepoint(mouse_pos):
            color_ff = COLOR_BTN_ADELANTAR_ACTIVE_HOVER if activo else COLOR_BTN_ADELANTAR_ACTIVE
            
        # Animación de escala
        tamaño_ff = estado.get("tamaño_ff_actual", 1.0)
        ancho_ff = int(boton_ff_rect.width * tamaño_ff)
        alto_ff = int(boton_ff_rect.height * tamaño_ff)
        
        rect_ff_anim = pygame.Rect(0, 0, ancho_ff, alto_ff)
        rect_ff_anim.center = boton_ff_rect.center
        
        # Dibujar botón
        pygame.draw.rect(superficie, color_ff, rect_ff_anim, border_radius=10)
        
        # Símbolo ">>"
        fuente_ff = recursos["fuente_boton"]
        txt_ff = fuente_ff.render(">>", True, (255, 255, 255))
        superficie.blit(txt_ff, txt_ff.get_rect(center=rect_ff_anim.center))


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
    frec_intro = slider_frecuencia.obtener_valor() if slider_frecuencia else 0
    _dibujar_elementos_base(capa, recursos, estado, bits, bit_reloj, frecuencia=frec_intro)
    _dibujar_tabla_program_counter(capa, recursos, 1, False)
    _dibujar_estadisticas(capa, recursos, 0, 0)
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


def _dibujar_estadisticas(superficie, recursos, tiempo, ciclos):
    """Dibuja el HUD de estadísticas con estilo de tarjetas en la esquina superior derecha."""
    # Configuración de estilo
    ancho_tarjeta = 130
    alto_tarjeta = 60  # Aumentado para fuente más grande
    margen_derecho = 30
    margen_superior = 30
    espacio_entre = 15
    offset_etiqueta = 25  # Espacio vertical para el texto arriba
    color_fondo = COLOR_FONDO_SECUNDARIO  # Gris azulado
    color_borde = COLOR_FONDO_SECUNDARIO # Borde acorde al fondo

    # Fuentes locales para el HUD
    fuente_titulo = pygame.font.SysFont("Montserrat", 20, bold=False)
    fuente_valor = pygame.font.SysFont("Montserrat", 42, bold=True)

    # --- Tarjeta 1: Ciclos (Izquierda) ---
    x_ciclos = ANCHO_VENTANA - margen_derecho - 2 * ancho_tarjeta - espacio_entre
    y_burbuja = margen_superior + offset_etiqueta
    rect_ciclos = pygame.Rect(x_ciclos, y_burbuja, ancho_tarjeta, alto_tarjeta)

    # Etiqueta fuera (arriba)
    lbl_ciclos = fuente_titulo.render("Ciclos de reloj", True, (180, 180, 190))
    superficie.blit(lbl_ciclos, lbl_ciclos.get_rect(centerx=rect_ciclos.centerx, bottom=rect_ciclos.top - 5))

    # Burbuja (solo valor)
    pygame.draw.rect(superficie, color_fondo, rect_ciclos)
    pygame.draw.rect(superficie, color_borde, rect_ciclos, 2)

    val_ciclos = fuente_valor.render(f"{int(ciclos)}", True, (255, 255, 255))
    superficie.blit(val_ciclos, val_ciclos.get_rect(center=rect_ciclos.center))

    # --- Tarjeta 2: Tiempo (Derecha) ---
    x_tiempo = ANCHO_VENTANA - margen_derecho - ancho_tarjeta
    rect_tiempo = pygame.Rect(x_tiempo, y_burbuja, ancho_tarjeta, alto_tarjeta)

    # Etiqueta fuera (arriba)
    lbl_tiempo = fuente_titulo.render("Tiempo trans.", True, (180, 180, 190))
    superficie.blit(lbl_tiempo, lbl_tiempo.get_rect(centerx=rect_tiempo.centerx, bottom=rect_tiempo.top - 5))

    # Burbuja (solo valor)
    pygame.draw.rect(superficie, color_fondo, rect_tiempo)
    pygame.draw.rect(superficie, color_borde, rect_tiempo, 2)

    val_tiempo = fuente_valor.render(f"{tiempo:.1f}s", True, (255, 255, 255))
    superficie.blit(val_tiempo, val_tiempo.get_rect(center=rect_tiempo.center))


def _dibujar_resultados_finales(superficie, recursos, estado, eficiencia, tiempo_ocio):
    """Dibuja las estadísticas finales y el botón de más resultados."""
    # Configuración de posición (alineado a la derecha, bajo sliders)
    # Sliders están en x=950 con ancho 200 -> borde derecho = 1150
    x_derecha = 1150
    y_inicio = 420    # Debajo del segundo slider

    # Fuentes
    fuente_titulo = pygame.font.SysFont("Montserrat", 20, bold=True)
    fuente_etiqueta = pygame.font.SysFont("Montserrat", 18, bold=False)
    fuente_valor = pygame.font.SysFont("Montserrat", 22, bold=True)

    # 1. Título
    txt_titulo = fuente_titulo.render("Estadísticas Simulación", True, (255, 255, 255))
    rect_titulo = txt_titulo.get_rect(topright=(x_derecha, y_inicio))
    superficie.blit(txt_titulo, rect_titulo)

    y_actual = rect_titulo.bottom + 20

    # 2. Eficiencia (Cian)
    txt_ef_val = fuente_valor.render(f"{eficiencia:.0f}%", True, (0, 255, 255))
    rect_ef_val = txt_ef_val.get_rect(topright=(x_derecha, y_actual))
    
    txt_ef_lbl = fuente_etiqueta.render("Eficiencia:", True, (255, 255, 255))
    rect_ef_lbl = txt_ef_lbl.get_rect(topright=(rect_ef_val.left - 10, y_actual + 2))

    superficie.blit(txt_ef_val, rect_ef_val)
    superficie.blit(txt_ef_lbl, rect_ef_lbl)

    y_actual += 30

    # 3. Tiempo de Ocio (Rosa Neón)
    txt_ocio_val = fuente_valor.render(f"{tiempo_ocio:.0f}s", True, (255, 20, 147))
    rect_ocio_val = txt_ocio_val.get_rect(topright=(x_derecha, y_actual))

    txt_ocio_lbl = fuente_etiqueta.render("Tiempo de Ocio:", True, (255, 255, 255))
    rect_ocio_lbl = txt_ocio_lbl.get_rect(topright=(rect_ocio_val.left - 10, y_actual + 2))

    superficie.blit(txt_ocio_val, rect_ocio_val)
    superficie.blit(txt_ocio_lbl, rect_ocio_lbl)

    y_actual += 50

    # 4. Botón 'Mostrar más resultados'
    boton_rect = estado["boton_resultados_rect"]
    # Actualizamos la posición del rect en el estado para que coincida con el dibujo
    boton_rect.topright = (x_derecha, y_actual)
    
    # Animación de escala
    tamaño = estado.get("tamaño_resultados_actual", 1.0)
    ancho_anim = int(boton_rect.width * tamaño)
    alto_anim = int(boton_rect.height * tamaño)
    
    rect_anim = pygame.Rect(0, 0, ancho_anim, alto_anim)
    rect_anim.center = boton_rect.center

    # Color e interacción visual
    mouse_pos = pygame.mouse.get_pos()
    color_base = COLOR_BTN_MOSTRAR_MAS # Magenta oscuro
    color_hover = COLOR_BTN_MOSTRAR_MAS_HOVER
    color = color_hover if boton_rect.collidepoint(mouse_pos) else color_base

    pygame.draw.rect(superficie, color, rect_anim, border_radius=10)
    
    # Texto del botón
    fuente_btn = pygame.font.SysFont("Montserrat", 16, bold=True)
    txt_btn = fuente_btn.render("   Mostrar más resultados   ", True, (255, 255, 255))
    superficie.blit(txt_btn, txt_btn.get_rect(center=rect_anim.center))


def dibujar_ventana_resultados(pantalla, recursos, estado, historial):
    """Dibuja el overlay con la gráfica de rendimiento."""
    # 1. Fondo semitransparente
    overlay = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA))
    overlay.set_alpha(220)
    overlay.fill((20, 20, 30))
    pantalla.blit(overlay, (0, 0))

    # 2. Contenedor de la gráfica
    margen_x = 100
    margen_y = 100
    ancho_graph = ANCHO_VENTANA - 2 * margen_x
    alto_graph = ALTO_VENTANA - 2 * margen_y
    
    rect_graph = pygame.Rect(margen_x, margen_y, ancho_graph, alto_graph)
    pygame.draw.rect(pantalla, (40, 40, 50), rect_graph, border_radius=15)
    pygame.draw.rect(pantalla, (100, 100, 120), rect_graph, 2, border_radius=15)

    # Título de la gráfica
    fuente_titulo = pygame.font.SysFont("Montserrat", 28, bold=True)
    txt_titulo = fuente_titulo.render("Monitor de Actividad CPU (Tiempo Real)", True, (255, 255, 255))
    pantalla.blit(txt_titulo, txt_titulo.get_rect(center=(ANCHO_VENTANA // 2, margen_y + 40)))

    # --- Leyenda ---
    fuente_leyenda = pygame.font.SysFont("Montserrat", 14, bold=True)
    
    # Verde: Procesando
    pygame.draw.rect(pantalla, (0, 255, 100), (margen_x + 50, margen_y + 70, 12, 12))
    pantalla.blit(fuente_leyenda.render("Procesando (CPU Activa)", True, (200, 200, 200)), (margen_x + 70, margen_y + 68))

    # Rojo: Esperando
    pygame.draw.rect(pantalla, (255, 50, 50), (margen_x + 260, margen_y + 70, 12, 12))
    pantalla.blit(fuente_leyenda.render("Esperando (Latencia RAM)", True, (200, 200, 200)), (margen_x + 280, margen_y + 68))

    # 3. Dibujar Gráfica (Barras)
    if len(historial) > 0:
        # Área útil para las barras (ajustada para dar espacio a la leyenda)
        area_barras = pygame.Rect(margen_x + 30, margen_y + 100, ancho_graph - 60, alto_graph - 180)
        # pygame.draw.rect(pantalla, (0, 0, 0), area_barras) # Debug fondo barras

        ancho_barra = area_barras.width / 200  # 200 es el maxlen del deque
        
        for i, valor in enumerate(historial):
            # 1 = Activo (Verde, Alto), 0 = Espera (Rojo, Bajo)
            es_activo = (valor == 1)
            
            color = (0, 255, 100) if es_activo else (255, 50, 50)
            altura = area_barras.height * 0.8 if es_activo else area_barras.height * 0.15
            
            x = area_barras.x + i * ancho_barra
            y = area_barras.bottom - altura
            
            # Dibujar barra (con un pequeño espacio entre ellas si el ancho lo permite)
            ancho_dibujo = max(1, ancho_barra - 1)
            pygame.draw.rect(pantalla, color, (x, y, ancho_dibujo, altura))

    # 4. Botón Cerrar
    rect_cerrar = estado["boton_cerrar_resultados_rect"]
    # Aseguramos que esté posicionado visualmente donde queremos (abajo centro del modal)
    rect_cerrar.center = (ANCHO_VENTANA // 2, margen_y + alto_graph - 50)
    
    mouse_pos = pygame.mouse.get_pos()
    color_cerrar = (200, 50, 50) if rect_cerrar.collidepoint(mouse_pos) else (150, 30, 30)
    
    pygame.draw.rect(pantalla, color_cerrar, rect_cerrar, border_radius=10)
    pygame.draw.rect(pantalla, (255, 255, 255), rect_cerrar, 2, border_radius=10)
    
    txt_cerrar = recursos["fuente_boton"].render("CERRAR", True, (255, 255, 255))
    pantalla.blit(txt_cerrar, txt_cerrar.get_rect(center=rect_cerrar.center))


def _dibujar_efectos_cpu(superficie, estado, frecuencia):
    """Dibuja humo y efectos de calor sobre la CPU."""
    # 1. Humo
    for p in estado.get("particulas_humo", []):
        x, y, vy, r, a = p
        if a > 0:
            # Crear superficie temporal para transparencia
            diametro = int(r * 2)
            surf_humo = pygame.Surface((diametro, diametro), pygame.SRCALPHA)
            color = (100, 100, 100, int(a))
            pygame.draw.circle(surf_humo, color, (int(r), int(r)), int(r))
            superficie.blit(surf_humo, (x - r, y - r))

    # 2. Calor Extremo (Glow Rojo)
    if frecuencia >= 9.8:
        # AJUSTES DE POSICIÓN DEL CALOR (Deben coincidir con el humo)
        ajuste_x = -145
        ajuste_y = 30

        # Círculo rojo brillante con mezcla aditiva
        radio_calor = 70
        surf_calor = pygame.Surface((radio_calor * 2, radio_calor * 2), pygame.SRCALPHA)
        # Rojo con transparencia
        pygame.draw.circle(surf_calor, (255, 50, 0, 100), (radio_calor, radio_calor), radio_calor)
        
        rect_calor = surf_calor.get_rect(center=(CENTRO_PANTALLA[0] + ajuste_x, CENTRO_PANTALLA[1] + ajuste_y))
        # Usar BLEND_ADD para efecto de luz/brillo
        superficie.blit(surf_calor, rect_calor, special_flags=pygame.BLEND_ADD)


# hacer brillar el texto de output 

def texto_neon(font, text, color_nucleo, color_luz, radius=10):
    # 1. Renderizar el texto base (del color de la luz)
    # Este será nuestra base para el desenfoque
    txt_base = font.render(text, True, color_luz).convert_alpha()
    w, h = txt_base.get_size()
    w+=30
    h+=30
    
    # 2. Crear superficies para el efecto Glow (Desenfoque)
    # Calculamos un tamaño expandido para que el brillo quepa
    padding = radius * 2
    glow_surf = pygame.Surface((w + padding, h + padding), pygame.SRCALPHA)
    
    # TRUCO: Reducimos drásticamente el texto para "romper" los bordes definidos
    # Reducir a 1/10 del tamaño original y luego volver a escalar crea un blur natural
    factor_reduccion = 10 
    mini_w = max(1, w // factor_reduccion)
    mini_h = max(1, h // factor_reduccion)
    
    # Creamos la versión diminuta
    txt_mini = pygame.transform.smoothscale(txt_base, (mini_w, mini_h))
    
    # Escalamos la versión diminuta al tamaño grande (con el padding extra)
    # Esto estira los píxeles suavizándolos, creando el efecto "nube" de neón
    glow_blur = pygame.transform.smoothscale(txt_mini, (w + padding, h + padding))
    
    # 3. Dibujar el brillo (puedes ajustar el alpha aquí si es demasiado intenso)
    # Usamos BLEND_ADD si quieres que brille mucho (como luz real) o normal si prefieres color plano
    # glow_blur.set_alpha(180) # Descomenta si el brillo es demasiado fuerte
    
    # Centramos el brillo en la superficie final
    resplandor_final = pygame.Surface((w + padding, h + padding), pygame.SRCALPHA)
    
    # Dibujamos el brillo un par de veces para intensificar el núcleo sin hacerlo sólido
    resplandor_final.blit(glow_blur, (0, 0))
    resplandor_final.blit(glow_blur, (0, 0), special_flags=pygame.BLEND_RGBA_ADD) 

    # 4. Renderizar el Núcleo (el texto blanco/brillante del centro)
    # Generalmente el centro del neón es casi blanco
    txt_nucleo = font.render(text, True, color_nucleo).convert_alpha()
    
    # Centrar el núcleo sobre el brillo
    core_x = (resplandor_final.get_width() - txt_nucleo.get_width()) // 2
    core_y = (resplandor_final.get_height() - txt_nucleo.get_height()) // 2
    resplandor_final.blit(txt_nucleo, (core_x, core_y))
    
    return resplandor_final