import pygame, sys, os
from pygame import VIDEORESIZE, KEYDOWN

from Bloon import *

pygame.init()
pygame.display.set_caption("BTD Battles")

info = pygame.display.Info()
WINDOW_WIDTH, WINDOW_HEIGHT = info.current_w, info.current_h
size = (WINDOW_WIDTH, WINDOW_HEIGHT)
screen = pygame.display.set_mode(size, pygame.NOFRAME)
fullscreen = True

map = pygame.image.load(f'assets/maps/background.png')
screen.blit(map, (0, 0))

clock = pygame.time.Clock()
REFRESH_RATE = 60

LEFT = 1
SCROLL = 2
RIGHT = 3

finish = False
bloon = None

bloons_list = pygame.sprite.Group()

while not finish:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finish = True
        if event.type == VIDEORESIZE:
            if not fullscreen:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
        if event.type == KEYDOWN:
            if event.key == pygame.K_f:
                fullscreen = not fullscreen
                if fullscreen:
                    screen = pygame.display.set_mode(size, pygame.NOFRAME)
                if not fullscreen:
                    os.environ['SDL_VIDEO_WINDOW_POS'] = "center"
                    screen = pygame.display.set_mode((1080, 700), pygame.RESIZABLE)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
            balloon = Bloon("black")
            bloons_list.add(balloon)

    screen.blit(map, (0, 0))
    for bloon in bloons_list:
        bloon.update()
    bloons_list.draw(screen)
    pygame.display.flip()
    clock.tick(REFRESH_RATE)

pygame.quit()
