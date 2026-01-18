import pygame
import sys
import random
import threading
import time 
from config import *
import resources
import graphics

## SIMULACION, PARÁMETROS Y MÉTODOS 
class Simulacion:
    def __init__(self, inx, finx, frecuenciaCPU, latenciaRAM):
        ## Parametros Simulacion
        self.frecuenciaCPU = frecuenciaCPU #hz
        self.latenciaRAM = latenciaRAM #segundos
        self.periodo_CPU= 1/frecuenciaCPU #s

        ## Parametros para animaciones 
        # Distancias
        self.distancia_RAM = 190
        self.distancia_CPU = 261
        self.inx = inx
        self.finx = finx
        self.pixelsPorSeg = (60*self.periodo_CPU/self.frecuenciaCPU)
        self.velBitRelojRAM = int(self.distancia_RAM/self.pixelsPorSeg)
        self.velBitRelojCPU = int(self.distancia_CPU/self.pixelsPorSeg)

    ## Se debe llamar con un hilo, demora la ejecucion de la simulación el tiempo de latencia 
    def proceso_RAM(self, bits, estado):
        self.transportar_bit(bits, 0)
        time.sleep(TIEMPO_DATO) #segundos
        print("esperando ram")
        
        time.sleep(self.latenciaRAM)
        print("Fin de la espera devolviendo datos")
        
        self.transportar_bit(bits, 1)
        time.sleep(TIEMPO_DATO)

        estado["waiting"] = False

    #configura los bits para envio o captación de datos 
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

#wasa
def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA), pygame.RESIZABLE)
    pygame.display.set_caption("Simulación: Cuello de Botella")
    clock = pygame.time.Clock()
    
    # VARIABLES SIMULACION
    simulacion = False
    hilo_iniciado = False 
    txt_tiempo = None
    reloj_interno = relojInterno()
    ciclos_totales= 0
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
        "exec": False
    }

    # Coordenadas de los cables para la lógica
    inicio_cable_x = rect_centro.left + 140
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
        "direccion": 0, # hacia derecha 0, hacia izquierda 1
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
    estado["boton_rect"].center = (ANCHO_VENTANA // 2, ALTO_VENTANA - 100)

    

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

            if evento.type == pygame.MOUSEBUTTONDOWN:
                if not estado["pantalla_inicio"] and not estado["intro_activa"]:
                    if estado["boton_rect"].collidepoint(mouse_pos):
                        if not simulacion: 
                            simulacion = True
                            reloj_interno.iniciarReloj()
                            ## AQUI SE DEBE INICIALIZAR LOS VALORES PARA LA SIMULACION 
                            frecuencia = 2 #en ciclos por segundo 
                            latencia = 2 #en segundos
                            program_counter = 0
                            sim = Simulacion(inicio_cable_x, fin_cable_x, frecuencia, latencia)
                        
        # B. LÓGICA / ACTUALIZACIÓN

        ## Simulacion 
        
        if simulacion:
            program_counter = 0
            
            ### Tiempo de simulación 
            tiempo_actual_seg = reloj_interno.obtenerTiempoActual()

            ### Ciclos transcurridos
            ciclos_actuales = int(tiempo_actual_seg /sim.periodo_CPU)

            if ciclos_actuales > ultimo_ciclo_procesado:
                ultimo_ciclo_procesado = ciclos_actuales
                ciclos_totales +=1

                # Iniciar animación bits rejol 
                if not bit_reloj["enviando"]:
                    bit_reloj["x_d"] = 600
                    bit_reloj["y_d"] = 230
                    bit_reloj["x_i"] = 530
                    bit_reloj["y_i"] = 230
                    bit_reloj["enviando"] = True

                ## ACCIONES EN CADA CICLO 
                if not estado["waiting"] : 
                    estado["waiting"]= True
                    hilo = threading.Thread(
                        target=sim.proceso_RAM, 
                        args=(bits, estado),
                        daemon=True)
                    hilo.start()

            if reloj_interno.obtenerTiempoActual() > 10:
                simulacion = False
                bits["enviando"] = False
                bit_reloj["enviando"] = False
                ciclos_actuales = 0
                ciclos_totales = 0
                ultimo_ciclo_procesado = 0

            ### RENDERIZAR VALORES ### 
            #renderzar tiempo y ciclos 
            txt_tiempo = assets["fuente_aviso"].render(
                f"Tiempo Reloj: {tiempo_actual_seg:.0f} s \n Ciclos: {ciclos_totales}", 
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
            if bits["direccion"] == 1 :
                bits["x"] -= VELOCIDAD_DATO
                if bits["x"] <= inicio_cable_x:
                    bits["x"] = inicio_cable_x
                    bits["enviando"] = False
            elif bits["direccion"] == 0 : # Hacia la derecha 
                bits["x"] += VELOCIDAD_DATO
                if bits["x"] >= fin_cable_x:
                    bits["x"] = fin_cable_x
                    bits["enviando"] = False

        #envio de datos reloj 
        if bit_reloj["enviando"]:
            bit_reloj["estado"] = True
            ##derecha
            if bit_reloj["y_d"] == 230 and bit_reloj["x_d"] < 640:
                bit_reloj["x_d"] += sim.velBitRelojRAM
                if bit_reloj["x_d"] > 640:
                    bit_reloj["x_d"] = 640

            if bit_reloj["x_d"] == 640 and bit_reloj["y_d"] < 340:
                bit_reloj["y_d"] += sim.velBitRelojRAM
                if bit_reloj["y_d"] > 340:
                    bit_reloj["y_d"] = 340
                    
            if bit_reloj["y_d"] == 340 and bit_reloj["x_d"] < 680:
                bit_reloj["x_d"] += sim.velBitRelojRAM
                if bit_reloj["x_d"] > 680:
                    bit_reloj["x_d"] = 680
                    

            ##izquierda 
            if (bit_reloj["y_i"] == 230 and bit_reloj["x_i"] >355):
                bit_reloj["x_i"] -= sim.velBitRelojCPU
                if bit_reloj["x_i"] < 355:
                    bit_reloj["x_i"] = 355
            if (bit_reloj["x_i"] == 355 and bit_reloj["y_i"] < 316):
                bit_reloj["y_i"] += sim.velBitRelojCPU
                if bit_reloj["y_i"] > 316:
                    bit_reloj["y_i"] = 316
                    bit_reloj["enviando"] = False
                    bit_reloj["estado"] = False


            

        # C. DIBUJADO (Delegado al módulo graphics)
        graphics.dibujar_juego(pantalla, assets, estado, bits, bit_reloj)
        if txt_tiempo != None: 
            pantalla.blit(txt_tiempo, (10, 200))
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()