import time
import pygame
import math

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 900

pygame.init()
size = (WINDOW_WIDTH, WINDOW_HEIGHT)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Game")

WHITE = (255, 255, 255)
# screen.fill(WHITE)
# pygame.display.flip()

IMAGE = 'dog.jpg'
img = pygame.image.load(IMAGE)
screen.blit(img, (450, 450))
pygame.display.flip()

for i in range(100):
    # rad = a * pi /180
    angle = (i * 3.6 * math.pi) / 180
    pygame.draw.line(screen, WHITE, (450, 450), (450 + math.cos(angle)*350, 450 + math.sin(angle)*350), 4)
    pygame.display.flip()

clock = pygame.time.Clock()
REFRESH_RATE = 60

# pygame.mouse.set_visible(False)
LEFT = 1
SCROLL = 2
RIGHT = 3

finish = False
while not finish:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finish = True

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
            mouse_point = pygame.mouse.get_pos()
            screen.blit(img, mouse_point)
    pygame.display.flip()
    clock.tick(REFRESH_RATE)

pygame.quit()
