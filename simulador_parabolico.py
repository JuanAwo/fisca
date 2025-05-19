
import pygame
import math

pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 900, 600
ventana = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulador Movimiento Parabólico")

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
AZUL = (0, 0, 100)
GRIS = (200, 200, 200)
VERDE = (0, 200, 0)
ROJO = (255, 0, 0)

# Física
g = 9.8
escala = 10

# Fuente
fuente = pygame.font.SysFont("arial", 20)

# Inputs
input_angulo = "    "
input_velocidad = "    "
angulo_activo = True
velocidad_activa = False
input_finalizado = False

# Botones
boton_lanzar = pygame.Rect(700, 100, 120, 40)
boton_reset = pygame.Rect(700, 160, 120, 40)

# Estados simulación
simulando = False
t_actual = 0
dt = 0.05
vx = vy = 0
estela = []

# Variables físicas
tiempo_total = 0
altura_max = 0
alcance = 0

# Carga recursos
try:
    muñeco = pygame.image.load("muñeco.png")
    muñeco = pygame.transform.scale(muñeco, (100, 150))
except:
    muñeco = None

try:
    sonido_lanzamiento = pygame.mixer.Sound("lanzamiento.wav")
    sonido_impacto = pygame.mixer.Sound("impacto.mp3")
except:
    sonido_lanzamiento = None
    sonido_impacto = None

def calcular_iniciales(v0, angulo):
    ang_rad = math.radians(angulo)
    vx = v0 * math.cos(ang_rad)
    vy = v0 * math.sin(ang_rad)
    tiempo_total = (2 * vy) / g
    altura_max = (vy ** 2) / (2 * g)
    alcance = vx * tiempo_total
    return vx, vy, altura_max, tiempo_total, alcance

def dibujar_proyectil(x, y):
    pygame.draw.circle(ventana, ROJO, (int(x), int(y)), 6)

def dibujar():
    ventana.fill(BLANCO)

    # Dibuja muñeco
    if muñeco:
        ventana.blit(muñeco, (50, HEIGHT - 200))

    # Inputs
    pygame.draw.rect(ventana, GRIS if angulo_activo else AZUL, (100, 50, 100, 30))
    ventana.blit(fuente.render("Ángulo (°):", True, NEGRO), (10, 55))
    ventana.blit(fuente.render(input_angulo, True, AZUL), (105, 55))

    pygame.draw.rect(ventana, GRIS if velocidad_activa else AZUL, (100, 100, 100, 30))
    ventana.blit(fuente.render("Velocidad (m/s):", True, NEGRO), (10, 105))
    ventana.blit(fuente.render(input_velocidad, True, AZUL), (105, 105))

    # Botones
    pygame.draw.rect(ventana, AZUL, boton_lanzar)
    ventana.blit(fuente.render("Lanzar", True, BLANCO), (boton_lanzar.x + 30, boton_lanzar.y + 10))

    pygame.draw.rect(ventana, VERDE, boton_reset)
    ventana.blit(fuente.render("Reset", True, BLANCO), (boton_reset.x + 35, boton_reset.y + 10))

    # Piso
    pygame.draw.line(ventana, NEGRO, (0, HEIGHT - 50), (WIDTH, HEIGHT - 50), 2)

    # Estela del proyectil
    for punto in estela:
        pygame.draw.circle(ventana, ROJO, punto, 3)

    # Datos
    if input_finalizado:
        ventana.blit(fuente.render(f"Altura máxima: {altura_max:.2f} m", True, NEGRO), (10, 160))
        ventana.blit(fuente.render(f"Tiempo total: {tiempo_total:.2f} s", True, NEGRO), (10, 190))
        ventana.blit(fuente.render(f"Alcance: {alcance:.2f} m", True, NEGRO), (10, 220))

    pygame.display.update()

reloj = pygame.time.Clock()
corriendo = True

while corriendo:
    reloj.tick(60)
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            corriendo = False

        if evento.type == pygame.MOUSEBUTTONDOWN:
            if 100 <= evento.pos[0] <= 200:
                if 50 <= evento.pos[1] <= 80:
                    angulo_activo = True
                    velocidad_activa = False
                elif 100 <= evento.pos[1] <= 130:
                    angulo_activo = False
                    velocidad_activa = True
            else:
                angulo_activo = False
                velocidad_activa = False

            if boton_lanzar.collidepoint(evento.pos):
                try:
                    v = float(input_velocidad)
                    a = float(input_angulo)
                    vx, vy, altura_max, tiempo_total, alcance = calcular_iniciales(v, a)
                    t_actual = 0
                    estela = []
                    simulando = True
                    input_finalizado = True
                    if sonido_lanzamiento:
                        sonido_lanzamiento.play()
                except:
                    input_finalizado = False
                    simulando = False

            if boton_reset.collidepoint(evento.pos):
                input_angulo = ""
                input_velocidad = ""
                simulando = False
                input_finalizado = False
                estela = []

        if evento.type == pygame.KEYDOWN:
            if angulo_activo:
                if evento.key == pygame.K_BACKSPACE:
                    input_angulo = input_angulo[:-1]
                elif evento.unicode.isdigit() or evento.unicode == ".":
                    input_angulo += evento.unicode
            elif velocidad_activa:
                if evento.key == pygame.K_BACKSPACE:
                    input_velocidad = input_velocidad[:-1]
                elif evento.unicode.isdigit() or evento.unicode == ".":
                    input_velocidad += evento.unicode

    if simulando:
        t_actual += dt
        x = vx * t_actual * escala
        y = (vy * t_actual - 0.5 * g * t_actual ** 2) * escala
        pantalla_x = int(x) + 50 + 30  # Offset para que salga desde muñeco
        pantalla_y = HEIGHT - 50 - int(y)

        if pantalla_y >= HEIGHT - 50 or pantalla_x >= WIDTH:
            simulando = False
            if sonido_impacto:
                sonido_impacto.play()
        else:
            estela.append((pantalla_x, pantalla_y))
            dibujar()
            pygame.draw.circle(ventana, ROJO, (pantalla_x, pantalla_y), 6)
            pygame.display.update()
            continue

    dibujar()

pygame.quit()
