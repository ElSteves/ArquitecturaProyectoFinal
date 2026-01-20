import pygame
from config import *


class Slider:
    """Clase para crear sliders interactivos y visuales."""

    def __init__(self, x, y, ancho, alto, valor_min, valor_max, valor_inicial, etiqueta,
                 color_principal= COLOR_SELECTOR_CPU):
        """
        Crea un slider visual.

        Args:
            x, y: Posición del slider
            ancho: Ancho total del slider
            alto: Alto del slider
            valor_min: Valor mínimo
            valor_max: Valor máximo
            valor_inicial: Valor inicial
            etiqueta: Texto a mostrar (ej: "Frecuencia")
            color_principal: Color del slider (RGB)
        """
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto
        self.valor_min = valor_min
        self.valor_max = valor_max
        self.valor = valor_inicial
        self.etiqueta = etiqueta
        self.color_principal = color_principal
        self.color_fondo = COLOR_FONDO_SECUNDARIO
        self.color_texto = (255, 255, 255)

        # Rects para colisión
        self.rect_fondo = pygame.Rect(x, y + 35, ancho, 15)
        self.rect_boton = pygame.Rect(0, 0, 20, 30)
        self._actualizar_posicion_boton()

        # Para arrastre
        self.siendo_arrastrado = False

        # Para animación de tamaño suave
        self.tamaño_boton_actual = 1.0  # Factor de escala (1.0 = tamaño normal)
        self.tamaño_boton_objetivo = 1.0
        self.velocidad_animacion = 0.15  # Qué tan suave es la transición

    def _actualizar_posicion_boton(self):
        """Actualiza la posición del botón basado en el valor actual."""
        rango = self.valor_max - self.valor_min
        proporcion = (self.valor - self.valor_min) / rango if rango > 0 else 0
        boton_x = self.x + (proporcion * self.ancho) - 10
        self.rect_boton.x = boton_x
        self.rect_boton.y = self.y + 25

    def _actualizar_animacion_tamaño(self):
        """Actualiza suavemente el tamaño del botón hacia el objetivo."""
        diferencia = self.tamaño_boton_objetivo - self.tamaño_boton_actual
        self.tamaño_boton_actual += diferencia * self.velocidad_animacion

    def manejar_evento(self, evento, mouse_pos):
        """Maneja eventos del mouse."""
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if self.rect_boton.collidepoint(mouse_pos):
                self.siendo_arrastrado = True
                self.tamaño_boton_objetivo = 0.7  # Reducir a 70%
        elif evento.type == pygame.MOUSEBUTTONUP:
            self.siendo_arrastrado = False
            self.tamaño_boton_objetivo = 1.0  # Volver al 100%
        elif evento.type == pygame.MOUSEMOTION and self.siendo_arrastrado:
            self._actualizar_valor_desde_mouse(mouse_pos[0])

    def _actualizar_valor_desde_mouse(self, mouse_x):
        """Actualiza el valor basado en la posición del mouse."""
        # Limitar mouse_x al rango del slider
        mouse_x = max(self.x, min(mouse_x, self.x + self.ancho))

        # Calcular proporción
        proporcion = (mouse_x - self.x) / self.ancho
        self.valor = self.valor_min + proporcion * (self.valor_max - self.valor_min)

        # Redondear si es decimal cercano a entero
        if abs(self.valor - round(self.valor)) < 0.05:
            self.valor = round(self.valor)

        self._actualizar_posicion_boton()

    def obtener_valor(self):
        """Retorna el valor actual del slider."""
        return self.valor

    def establecer_valor(self, valor):
        """Establece un nuevo valor."""
        self.valor = max(self.valor_min, min(valor, self.valor_max))
        self._actualizar_posicion_boton()

    def dibujar(self, superficie, fuente, disabled=False):
        """Dibuja el slider en la superficie.

        Si `disabled=True`, el slider se dibuja con menor alpha para indicar que no está activo.
        """

        self.ancho +=10
        self.x -=10
        # Actualizar animación de tamaño
        self._actualizar_animacion_tamaño()

        # Crear una superficie temporal para controlar alpha
        ancho_super = self.ancho + 200
        alto_super = 80
        surf = pygame.Surface((ancho_super, alto_super), pygame.SRCALPHA)

        # Etiqueta
        texto_etiqueta = fuente.render(self.etiqueta, True, self.color_texto)
        surf.blit(texto_etiqueta, (0, 0))

        # Fondo del slider (barra)
        rect_fondo_local = pygame.Rect(0, 35, self.ancho, 15)
        pygame.draw.rect(surf, self.color_fondo, rect_fondo_local, border_radius=7)

        # Barra de progreso (parte rellena)
        rango = self.valor_max - self.valor_min
        proporcion = (self.valor - self.valor_min) / rango if rango > 0 else 0
        ancho_progreso = int(self.ancho * proporcion)
        rect_progreso = pygame.Rect(0, 35, ancho_progreso+8, 15)
        pygame.draw.rect(surf, self.color_principal, rect_progreso, border_radius=7)

        # Botón con animación de tamaño
        tamaño_x = int(20 * self.tamaño_boton_actual)
        tamaño_y = int(30 * self.tamaño_boton_actual)
        offset_x = (20 - tamaño_x) // 2
        offset_y = (30 - tamaño_y) // 2

        boton_x_local = self.rect_boton.x - self.x
        boton_y_local = self.rect_boton.y - self.y

        rect_boton_animado = pygame.Rect(
            boton_x_local + offset_x,
            boton_y_local + offset_y,
            tamaño_x,
            tamaño_y
        )

        pygame.draw.rect(surf, self.color_principal, rect_boton_animado, border_radius=5)
        pygame.draw.rect(surf, (255, 255, 255), rect_boton_animado, 2, border_radius=5)

        # Valor numérico
        valor_mostrado = self.valor
        if isinstance(valor_mostrado, float):
            if "Latencia" in self.etiqueta:
                texto_valor = fuente.render(f"{valor_mostrado:.2f}", True, self.color_principal)
            else:
                texto_valor = fuente.render(f"{int(valor_mostrado)}", True, self.color_principal)
        else:
            texto_valor = fuente.render(f"{valor_mostrado}", True, self.color_principal)

        surf.blit(texto_valor, (self.ancho + 15, 32))

        # Aplicar alpha si está deshabilitado
        if disabled:
            surf.set_alpha(110)

        # Finalmente, blit en la superficie destino
        superficie.blit(surf, (self.x, self.y))

        self.ancho -=10
        self.x +=10
