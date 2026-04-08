import random
from pygame import VIDEORESIZE, KEYDOWN
from Maps import *
from Monkey import *

pygame.init()
pygame.display.set_caption("BTD Battles")

fullscreen = True
game_map = Maps("galili")

clock = pygame.time.Clock()
REFRESH_RATE = 60

finish = False
bloon = None
bloons_list = pygame.sprite.Group()
monkeys_list = pygame.sprite.Group()

while not finish:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finish = True
        if event.type == VIDEORESIZE:
            if not fullscreen:
                game_map.update_size(bloons_list, monkeys_list, fullscreen, event)

        if event.type == KEYDOWN:
            if event.key == pygame.K_f:
                fullscreen = not fullscreen
                game_map.update_size(bloons_list, monkeys_list, fullscreen)

        if event.type == pygame.MOUSEBUTTONDOWN:
            colors = {1: "red", 2: "blue", 3: "green", 4: "yellow", 5: "pink", 6: "black"}
            ran_color = random.randint(1, 6)
            match int(event.button):
                case 1: # LEFT
                    # bloon = Bloon(colors[ran_color], 1, PATHS["PATH"])
                    mouse_point = pygame.mouse.get_pos()
                    monkey = Monkey("dart_monkey", mouse_point)
                    monkeys_list.add(monkey)

                case 3: # RIGHT
                    bloon = Bloon(colors[ran_color], 2, PATHS["INVERSE_PATH"])
                case 2: # SCROLL
                    bloon = Bloon(colors[ran_color], 1, PATHS["PATH"])
                    bloons_list.add(bloon)
                    bloon = Bloon(colors[ran_color], 2, PATHS["INVERSE_PATH"])
            if bloon is not None:
                bloons_list.add(bloon)

    dt = clock.tick(REFRESH_RATE)
    current_time = pygame.time.get_ticks()

    for bloon in bloons_list:
        bloon.move(dt)
    for monkey in monkeys_list:
        monkey.check_shoot(current_time, bloons_list)

    game_map.draw(bloons_list, monkeys_list, dt)
pygame.quit()
