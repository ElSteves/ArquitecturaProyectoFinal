import pygame
import sys
import random
import threading
import time
from config import *
import resources
import graphics
from slider import Slider


## SIMULACION, PARÁMETROS Y MÉTODOS
class Simulacion:
    def __init__(self, inx, finx, frecuenciaCPU, latenciaRAM):
        ## Parametros Simulacion
        self.frecuenciaCPU = frecuenciaCPU  # hz
        self.latenciaRAM = latenciaRAM  # segundos
        self.periodo_CPU = 1 / frecuenciaCPU  # s
        self.program_counter = 1
        self.out = 0
        self.simulando = True
        self.tiempo_ocio = 0.0
        self.eficiencia = 0.0

        ## Parametros para animaciones
        # Distancias
        self.distancia_RAM = 190
        self.distancia_CPU = 261
        self.inx = inx
        self.finx = finx
        self.pixelsPorSeg = (60 * self.periodo_CPU / self.frecuenciaCPU)
        self.velBitRelojRAM = int(self.distancia_RAM / self.pixelsPorSeg)
        self.velBitRelojCPU = int(self.distancia_CPU / self.pixelsPorSeg)

    # Obtener stats
    def obtener_estadisticas(self, tiempo_total_sim):
        aux = tiempo_total_sim - self.tiempo_ocio
        self.eficiencia = (aux / tiempo_total_sim) * 100
        return self.eficiencia, self.tiempo_ocio

    ## Se debe llamar con un hilo, demora la ejecucion de la simulación el tiempo de latencia
    def proceso_RAM(self, bits, estado):
        estado["fetching"], estado["waiting"], estado["exec"] = False, True, False

        self.transportar_bit(bits, 0)
        time.sleep(TIEMPO_DATO)  # segundos

        inicio_espera = time.time()
        # RAM espera en base a su latencia
        time.sleep(self.latenciaRAM)
        self.tiempo_ocio += (time.time() - inicio_espera)

        self.transportar_bit(bits, 1)

        time.sleep(TIEMPO_DATO)

        estado["fetching"], estado["waiting"], estado["exec"] = False, False, False

    ## Se tarda por ciclos en funcion de la instruccion a ser ejecutada
    def proceso_CPU(self, bits, estado):
        estado["ejecutando..."] = True
        # FETCH: Pedir instruccion
        estado["fetching"], estado["waiting"], estado["exec"] = True, False, False
        time.sleep(self.periodo_CPU)  # Demora 1 ciclo
        self.proceso_RAM(bits, estado)  # Pide instruccion
        time.sleep(TIEMPO_DATO)

        # EXCEC- PC: Program Counter
        match self.program_counter:
            # LOAD  10
            case 1:  #
                self.proceso_RAM(bits, estado)  # pide dato de la direccion 10
                # LLeva el dato al acumulador - 1 ciclo
                estado["fetching"], estado["waiting"], estado["exec"] = False, False, True
                time.sleep(self.periodo_CPU)
                estado["fetching"], estado["waiting"], estado["exec"] = False, False, False
                self.program_counter += 1
            # ADD 11
            case 2:
                self.proceso_RAM(bits, estado)  # pide dato de la direccion 11
                # Lleva el dato al registro y lo suma en la ALU (2 ciclos )
                estado["fetching"], estado["waiting"], estado["exec"] = False, False, True
                time.sleep(self.periodo_CPU * 2)
                estado["fetching"], estado["waiting"], estado["exec"] = False, False, False
                self.program_counter += 1
            # STORE 10
            case 3:
                # Guarda lo que hay en el acumulador en la dir 10
                self.transportar_bit(bits, 0)
                time.sleep(TIEMPO_DATO)  # segundos
                estado["fetching"], estado["waiting"], estado["exec"] = False, False, True
                time.sleep(self.periodo_CPU)
                estado["fetching"], estado["waiting"], estado["exec"] = False, False, False
                time.sleep(self.latenciaRAM)
                estado["fetching"], estado["waiting"], estado["exec"] = False, False, False
                self.program_counter += 1
            # OUT 10
            case 4:
                # Envía instrucción a la ram
                self.transportar_bit(bits, 0)
                time.sleep(TIEMPO_DATO)  # segundos
                time.sleep(self.latenciaRAM)
                # RAM responde al dispositivo de salida
                ### FALTA IMPLEMENTAR
                self.out += 1
                self.program_counter += 1
            # SUB 12
            case 5:
                self.proceso_RAM(bits, estado)  # pide dato de la direccion 12 (limite del contador )
                # LLeva el dato al registro y lo resta en la ALU - 2 ciclos
                estado["fetching"], estado["waiting"], estado["exec"] = False, False, True
                time.sleep(self.periodo_CPU * 2)
                estado["fetching"], estado["waiting"], estado["exec"] = False, False, False
                self.program_counter += 1
            # JNZ 01
            case 6:
                ### Demora un ciclo en comprobar si el contador llebo al limite
                # La actualizacion del contador se lo hace en el bucle principal
                estado["fetching"], estado["waiting"], estado["exec"] = False, False, True
                time.sleep(self.periodo_CPU)
                estado["fetching"], estado["waiting"], estado["exec"] = False, False, False

                if self.out < LIMIT_COUNTER:
                    self.program_counter = 1
                elif self.out >= LIMIT_COUNTER:
                    self.program_counter = 7

            # HALT
            case 7:
                ### Demora un ciclo en terminal el programa
                # La finalizacion del programa se lo hace en el bucle principal
                estado["fetching"], estado["waiting"], estado["exec"] = False, False, True
                time.sleep(self.periodo_CPU)
                self.simulando = False

        estado["ejecutando..."] = False

        # configura los bits para envio o captación de datos

    # 0 hacia derecha
    # 1 hacia izquierda
    def transportar_bit(self, bits, direccion=0):
        bits["enviando"] = True
        bits["x"] = self.finx if direccion else self.inx
        bits["direccion"] = direccion
        bits_activos = []
        for i in range(8):
            valor_aleatorio = random.choice([True, False])
            bits_activos.append(valor_aleatorio)
        bits["activo"] = bits_activos


# FUNCIONES UTILITARIAS
# Inicia un cronómetro
class relojInterno:
    def __init__(self):
        self.tiempo_inicial = 0.0
        self.tiempo_actual = 0.0

    def iniciarReloj(self):
        self.tiempo_inicial = pygame.time.get_ticks()

    def obtenerTiempoActual(self):
        self.tiempo_actual = pygame.time.get_ticks()
        return (self.tiempo_actual - self.tiempo_inicial) / 1000


# wasa
def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
    pygame.display.set_caption("Simulación: Cuello de Botella")
    clock = pygame.time.Clock()

    # VARIABLES SIMULACION
    simulacion = False
    hilo_iniciado = False
    tiempo_actual_seg = 0.0
    txt_out = None
    txt_estadisticas = None
    reloj_interno = relojInterno()
    ciclos_totales = 0
    ultimo_ciclo_procesado = 0

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
        "boton_rect": pygame.Rect(0, 0, 150, 50),
        "waiting": False,
        "fetching": False,
        "exec": False,
        "ejecutando...": False,
        "simulacion": False,
        "pc_visual": 1.0,  # Posición visual suavizada del Program Counter
        "pc_highlight_scale": 0.0,  # Escala del resaltado (0.0 a 1.0) para animación Pop Up
        # Animación de botones
        "tamaño_boton_actual": 1.0,
        "tamaño_boton_objetivo": 1.0,
        "tamaño_parar_actual": 1.0,
        "tamaño_parar_objetivo": 1.0
    }

    # Crear sliders para frecuencia y latencia
    slider_frecuencia = Slider(950, 200, 200, 50, 1, 10, 2, "Frecuencia (Hz)", (100, 200, 255))
    slider_latencia = Slider(950, 300, 200, 50, 0, 10, 0, "Latencia (s)", (255, 150, 100))

    # Coordenadas de los cables para la lógica
    inicio_cable_x = rect_centro.left + 135
    fin_cable_x = rect_centro.right - 100

    distancia_primer_bit = rect_centro.center[1] + OFFSET_Y_CABLE - 24
    distancia_entre_cables = 9
    bits_y = []
    bits_activos = []
    for i in range(8):
        valor_aleatorio = random.choice([True, False])
        bits_y.append(distancia_primer_bit + i * distancia_entre_cables)
        bits_activos.append(valor_aleatorio)

    bits = {
        "enviando": False,
        "x": 0,
        "y": bits_y,
        "activo": bits_activos,
        "direccion": 0,  # hacia derecha 0, hacia izquierda 1
    }

    bit_reloj = {
        "enviando": False,
        "x_d": 0,
        "y_d": 0,
        "x_i": 0,
        "y_i": 0,
        "estado": True
    }

    # Ubicar botón
    estado["boton_rect"].center = (ANCHO_VENTANA // 2 - 90, ALTO_VENTANA - 100)

    # Crear botón para parar
    boton_parar_rect = pygame.Rect(0, 0, 150, 50)
    boton_parar_rect.center = (ANCHO_VENTANA // 2 + 90, ALTO_VENTANA - 100)
    estado["boton_parar_rect"] = boton_parar_rect

    # --- BUCLE PRINCIPAL ---
    corriendo = True
    while corriendo:
        mouse_pos = pygame.mouse.get_pos()
        # print("x:", mouse_pos[0], "y: ", mouse_pos[1])
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

            # Manejar eventos de sliders
            if not estado["pantalla_inicio"] and not estado["intro_activa"] and not simulacion:
                slider_frecuencia.manejar_evento(evento, mouse_pos)
                slider_latencia.manejar_evento(evento, mouse_pos)

            if evento.type == pygame.MOUSEBUTTONDOWN:
                if not estado["pantalla_inicio"] and not estado["intro_activa"]:
                    if estado["boton_rect"].collidepoint(mouse_pos):
                        estado["tamaño_boton_objetivo"] = 0.9  # Animación de compresión
                        if not simulacion:
                            ## Reestablecer valres de simulaciones anteriores
                            bits["enviando"] = False
                            bit_reloj["enviando"] = False
                            ciclos_actuales = 0
                            ciclos_totales = 0
                            ultimo_ciclo_procesado = 0
                            ## AQUIA SE DEBE INICIALIZAR LOS VALORES PARA LA SIMULACION
                            reloj_interno.iniciarReloj()  # Temporizador
                            frecuencia = int(slider_frecuencia.obtener_valor())  # en ciclos por segundo
                            latencia = slider_latencia.obtener_valor()  # en segundos
                            sim = Simulacion(inicio_cable_x, fin_cable_x, frecuencia, latencia)
                            simulacion = sim.simulando
                            estado["simulacion"] = simulacion

                    # Botón Parar
                    if estado["boton_parar_rect"].collidepoint(mouse_pos):
                        estado["tamaño_parar_objetivo"] = 0.9  # Animación de compresión
                        if simulacion:
                            # Detener simulación
                            simulacion = False
                            sim.simulando = False
                            estado["simulacion"] = False
                            # Calcular estadísticas
                            tiempo_actual_seg = reloj_interno.obtenerTiempoActual()
                            eficiencia, tiempo_ocio = sim.obtener_estadisticas(tiempo_actual_seg)
                            txt_estadisticas = assets["fuente_aviso"].render(
                                f"Eficiencia: {eficiencia:.00f}%, Ocio: {tiempo_ocio:.00f} s",
                                True, COLOR_TEXTO
                            )

            # Restaurar tamaño de botones cuando se suelta el mouse
            if evento.type == pygame.MOUSEBUTTONUP:
                estado["tamaño_boton_objetivo"] = 1.0
                estado["tamaño_parar_objetivo"] = 1.0

        # B. LÓGICA / ACTUALIZACIÓN

        # Actualizar animaciones de tamaño de botones
        diferencia_boton = estado["tamaño_boton_objetivo"] - estado["tamaño_boton_actual"]
        estado["tamaño_boton_actual"] += diferencia_boton * 0.50

        diferencia_parar = estado["tamaño_parar_objetivo"] - estado["tamaño_parar_actual"]
        estado["tamaño_parar_actual"] += diferencia_parar * 0.50

        # Actualizar posición visual del PC (interpolación suave)
        # Si hay simulación, el objetivo es el PC real, si no, vuelve a 1
        target_pc = sim.program_counter if simulacion else 1
        estado["pc_visual"] += (target_pc - estado["pc_visual"]) * 0.2

        # Actualizar escala del resaltado (Animación Pop Up / Pop Out)
        # Si hay simulación, crece a 1.0, si no, se encoge a 0.0
        target_scale = 1.0 if simulacion else 0.0
        estado["pc_highlight_scale"] += (target_scale - estado["pc_highlight_scale"]) * 0.2

        ## Simulacion

        if simulacion:
            ### Tiempo de simulación
            tiempo_actual_seg = reloj_interno.obtenerTiempoActual()

            ### Ciclos transcurridos
            ciclos_actuales = int(tiempo_actual_seg / sim.periodo_CPU)

            if ciclos_actuales > ultimo_ciclo_procesado:
                ultimo_ciclo_procesado = ciclos_actuales
                ciclos_totales += 1

                # Iniciar animación bits rejol
                if not bit_reloj["enviando"]:
                    bit_reloj["x_d"] = 660
                    bit_reloj["y_d"] = 230
                    bit_reloj["x_i"] = 610
                    bit_reloj["y_i"] = 230
                    bit_reloj["enviando"] = True

                ## ACCIONES EN CADA CICLO
                if not estado["ejecutando..."]:
                    hilo = threading.Thread(
                        target=sim.proceso_CPU,
                        args=(bits, estado),
                        daemon=True)
                    hilo.start()

            ### RENDERIZAR VALORES ###
            # renderzar tiempo y ciclos
            txt_out = assets["fuente_aviso"].render(
                f"OUTPUT: {sim.out}, PC: {sim.program_counter}",
                True, COLOR_TEXTO
            )

            simulacion = sim.simulando
            estado["simulacion"] = simulacion
            if simulacion == False:
                eficiencia, tiempo_ocio = sim.obtener_estadisticas(tiempo_actual_seg)
                txt_estadisticas = assets["fuente_aviso"].render(
                    f"Eficiencia: {eficiencia:.00f}%, Ocio: {tiempo_ocio:.00f} s",
                    True, COLOR_TEXTO
                )

        # Lógica de la Intro
        if estado["intro_activa"]:
            now = pygame.time.get_ticks()
            estado["intro_progreso"] = (now - estado["intro_inicio"]) / DURACION_INTRO
            if estado["intro_progreso"] >= 1.0:
                estado["intro_progreso"] = 1.0
                estado["intro_activa"] = False

        ### Lógica de envio de Dato (Bit)
        # 0: Hacia la derecha
        # 1: Hacia la izquierda
        if bits["enviando"]:
            if bits["direccion"] == 1:
                bits["x"] -= VELOCIDAD_DATO
                if bits["x"] <= inicio_cable_x:
                    bits["x"] = inicio_cable_x
                    bits["enviando"] = False
            elif bits["direccion"] == 0:  # Hacia la derecha
                bits["x"] += VELOCIDAD_DATO
                if bits["x"] >= fin_cable_x:
                    bits["x"] = fin_cable_x
                    bits["enviando"] = False

        # envio de datos reloj
        if bit_reloj["enviando"]:
            bit_reloj["estado"] = True
            ##derecha
            if bit_reloj["y_d"] == 230 and bit_reloj["x_d"] < 705:
                bit_reloj["x_d"] += sim.velBitRelojRAM
                if bit_reloj["x_d"] > 705:
                    bit_reloj["x_d"] = 705

            if bit_reloj["x_d"] == 705 and bit_reloj["y_d"] < 340:
                bit_reloj["y_d"] += sim.velBitRelojRAM
                if bit_reloj["y_d"] > 340:
                    bit_reloj["y_d"] = 340

            if bit_reloj["y_d"] == 340 and bit_reloj["x_d"] < 735:
                bit_reloj["x_d"] += sim.velBitRelojRAM
                if bit_reloj["x_d"] > 735:
                    bit_reloj["x_d"] = 735

            ##izquierda
            if (bit_reloj["y_i"] == 230 and bit_reloj["x_i"] > 420):
                bit_reloj["x_i"] -= sim.velBitRelojCPU
                if bit_reloj["x_i"] < 420:
                    bit_reloj["x_i"] = 420
            if (bit_reloj["x_i"] == 420 and bit_reloj["y_i"] < 316):
                bit_reloj["y_i"] += sim.velBitRelojCPU
                if bit_reloj["y_i"] > 316:
                    bit_reloj["y_i"] = 316
                    bit_reloj["enviando"] = False
                    bit_reloj["estado"] = False

        # C. DIBUJADO (Delegado al módulo graphics)
        graphics.dibujar_juego(pantalla, assets, estado, bits, bit_reloj, slider_frecuencia, slider_latencia, estado["pc_visual"], tiempo=tiempo_actual_seg, ciclos=ciclos_totales)
        ## Info simulacion solo para pruebas
        if txt_out != None:
            pantalla.blit(txt_out, (890, 470))
        if txt_estadisticas != None:
            pantalla.blit(txt_estadisticas, (890, 540))
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()