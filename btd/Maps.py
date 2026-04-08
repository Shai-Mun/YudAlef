import os
from Bloon import *

def get_ratios(track):
    match track:
        case "Galili":
            return [
                (0.27, 0.0),  # 1
                (0.27, 0.78),  # 2
                (0.42, 0.88),
                (0.6, 0.9),  # 3
                (0.8, 0.88),
                (0.93, 0.78),  # 4
                (0.93, 0.17),  # 5
                (0.8, 0.08),
                (0.6, 0.04),  # 6
                (0.42, 0.08),
                (0.27, 0.17),  # 7
                (0.27, 1.1),  # 8
            ]
        case _:
            return []

PINK = (255, 128, 255)
GUI = pygame.image.load('assets/gui.png')
GUI.set_colorkey(PINK)

class Maps:

    def __init__(self, track):
        self.ratios = get_ratios(track)
        self.bg = pygame.image.load(f'assets/maps/{track}.png')
        self.shop_width = pygame.display.Info().current_w * 0.104
        self.size = (pygame.display.Info().current_w - self.shop_width, pygame.display.Info().current_h)
        self.screen = pygame.display.set_mode((self.size[0] + self.shop_width, self.size[1]), pygame.NOFRAME)
        self.bg_scaled = pygame.transform.scale(self.bg, self.size)

        self.screen.blit(self.bg_scaled, (self.shop_width, 0))
        update_path(self.size[0] / 2, self.size[1], self.shop_width)


    def update_size(self, bloons_list, fullscreen, event = None):
        global GUI

        if not fullscreen:
            if event is not None:
                self.shop_width = event.w * 0.104

                update_path((event.w - self.shop_width) / 2, event.h, self.shop_width)
                update_loc(bloons_list, (self.screen.get_width(), self.screen.get_height())
                           , (event.w, event.h))

                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                self.bg_scaled = pygame.transform.scale(self.bg, (event.w - self.shop_width, event.h))
                GUI = pygame.transform.scale(GUI, (event.w, event.h))

            else:
                self.shop_width = 1080 * 0.104

                update_path((1080 - self.shop_width) / 2, 700, self.shop_width)
                update_loc(bloons_list, (self.screen.get_width(), self.screen.get_height()), (1080, 700))

                os.environ['SDL_VIDEO_WINDOW_POS'] = "center"
                self.screen = pygame.display.set_mode((1080, 700), pygame.RESIZABLE)
                self.bg_scaled = pygame.transform.scale(self.bg, (1080 - self.shop_width, 700))
                GUI = pygame.transform.scale(GUI, (1080, 700))

        else:
            self.shop_width = 1960 * 0.104

            update_path(self.size[0] / 2, self.size[1], self.shop_width)
            update_loc(bloons_list, (self.screen.get_width(), self.screen.get_height())
                       , (self.size[0] + self.shop_width, self.size[1]))

            self.screen = pygame.display.set_mode((self.size[0] + self.shop_width, self.size[1]), pygame.NOFRAME)
            self.bg_scaled = pygame.transform.scale(self.bg, self.size)
            GUI = pygame.transform.scale(GUI, (self.size[0] + self.shop_width, self.size[1]))


    def draw(self, bloons_list, dt):
        global GUI

        self.screen.blit(self.bg_scaled, (self.shop_width, 0))
        self.screen.blit(GUI, (0, 0))
        for bloon in bloons_list:
            bloon.update(dt)
        bloons_list.draw(self.screen)
        pygame.display.flip()



