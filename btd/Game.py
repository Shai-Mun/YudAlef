import os, random
from pygame import VIDEORESIZE, KEYDOWN
from Bloon import *
from Maps import *

pygame.init()
pygame.display.set_caption("BTD Battles")

fullscreen = True
game_map = Maps("galili")

clock = pygame.time.Clock()
REFRESH_RATE = 60
frame_count = 0

finish = False

bloons_list = pygame.sprite.Group()

while not finish:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finish = True
        if event.type == VIDEORESIZE:
            if not fullscreen:
                game_map.update_size(bloons_list, fullscreen, event)

        if event.type == KEYDOWN:
            if event.key == pygame.K_f:
                fullscreen = not fullscreen
                game_map.update_size(bloons_list, fullscreen)

        if event.type == pygame.MOUSEBUTTONDOWN:
            colors = {1: "red", 2: "blue", 3: "green", 4: "yellow", 5: "pink", 6: "black"}
            ran_color = random.randint(1, 6)
            match int(event.button):
                case 1: # LEFT
                    bloon = Bloon(colors[ran_color], 1)
                case 3: # RIGHT
                    bloon = Bloon(colors[ran_color], 2)
                case 2: # SCROLL
                    bloon = Bloon(colors[ran_color], 1)
                    bloons_list.add(bloon)
                    bloon = Bloon(colors[ran_color], 2)
            bloons_list.add(bloon)

    dt = clock.tick(REFRESH_RATE)
    game_map.draw(bloons_list, dt)
pygame.quit()
