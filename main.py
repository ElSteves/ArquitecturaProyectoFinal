import pygame
import sys
from config import *
import resources
import graphics


def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA), pygame.RESIZABLE)
    pygame.display.set_caption("Simulación: Cuello de Botella")
    clock = pygame.time.Clock()

    # 1. Cargar Recursos
    assets = resources.cargar_recursos()

    # 2. Definir Estado Inicial
    # Usamos un diccionario para pasar el estado fácilmente al módulo de gráficos
    rect_centro = assets["centro"].get_rect(center=CENTRO_PANTALLA)

    estado = {
        "pantalla_inicio": True,
        "intro_activa": False,
        "intro_inicio": 0,
        "intro_progreso": 0.0,
        "enviando_dato": False,
        "dato_x": 0,
        "dato_y": rect_centro.center[1] + OFFSET_Y_CABLE,
        "boton_rect": pygame.Rect(0, 0, 150, 50)
    }

    # Ubicar botón
    estado["boton_rect"].center = (ANCHO_VENTANA // 2, ALTO_VENTANA - 100)

    # Coordenadas de los cables para la lógica
    inicio_cable_x = rect_centro.left + 140
    fin_cable_x = rect_centro.right - 100

    # --- BUCLE PRINCIPAL ---
    corriendo = True
    while corriendo:
        mouse_pos = pygame.mouse.get_pos()

        # A. EVENTOS
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    corriendo = False

                # Iniciar Intro
                if evento.key == pygame.K_RETURN and estado["pantalla_inicio"]:
                    estado["pantalla_inicio"] = False
                    estado["intro_activa"] = True
                    estado["intro_inicio"] = pygame.time.get_ticks()

                # Saltar Intro
                if evento.key == pygame.K_SPACE and estado["intro_activa"]:
                    estado["intro_activa"] = False

            if evento.type == pygame.MOUSEBUTTONDOWN:
                if not estado["pantalla_inicio"] and not estado["intro_activa"]:
                    if estado["boton_rect"].collidepoint(mouse_pos):
                        if not estado["enviando_dato"]:
                            estado["enviando_dato"] = True
                            estado["dato_x"] = inicio_cable_x

        # B. LÓGICA / ACTUALIZACIÓN

        # Lógica de la Intro
        if estado["intro_activa"]:
            now = pygame.time.get_ticks()
            estado["intro_progreso"] = (now - estado["intro_inicio"]) / DURACION_INTRO
            if estado["intro_progreso"] >= 1.0:
                estado["intro_progreso"] = 1.0
                estado["intro_activa"] = False

        # Lógica del Dato
        if estado["enviando_dato"]:
            estado["dato_x"] += VELOCIDAD_DATO
            if estado["dato_x"] >= fin_cable_x:
                estado["dato_x"] = fin_cable_x
                estado["enviando_dato"] = False

        # C. DIBUJADO (Delegado al módulo graphics)
        graphics.dibujar_juego(pantalla, assets, estado)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()