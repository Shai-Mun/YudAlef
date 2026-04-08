import os
from Bloon import *
from Monkey import *

PINK = (255, 128, 255)
GUI = pygame.image.load('assets/gui.png')

track_ratios = []

PATHS = {
    "PATH": [],
    "INVERSE_PATH": []
}


def get_ratios(track):
    match track:
        case "galili":
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

def inverse():
    return [(1 - r[0], 1 - r[1]) for r in track_ratios]

def update_path(width, height, shop_width):
    global track_ratios

    track_ratios = get_ratios("galili")
    PATHS["PATH"] = [pygame.Vector2(width*r[0] + shop_width, height*r[1]) for r in track_ratios]
    PATHS["INVERSE_PATH"] = [pygame.Vector2(width*r[0] + width + shop_width, height*r[1]) for r in inverse()]

def update_loc(bloons_list, monkeys_list, old_size, new_size):
    for bloon in bloons_list:
        ratio = bloon.pos.x / old_size[0]
        bloon.pos.x = new_size[0] * ratio
        ratio = bloon.pos.y / old_size[1]
        bloon.pos.y = new_size[1] * ratio

        match bloon.side:
            case 1:
                bloon.path = PATHS["PATH"]
            case 2:
                bloon.path = PATHS["INVERSE_PATH"]

    for monkey in monkeys_list:
        ratio = monkey.pos.x / old_size[0]
        monkey.pos.x = new_size[0] * ratio
        ratio = monkey.pos.y / old_size[1]
        monkey.pos.y = new_size[1] * ratio
        monkey.rect = monkey.image.get_rect(center=(round(monkey.pos.x), round(monkey.pos.y)))


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


    def update_size(self, bloons_list, monkeys_list, fullscreen, event = None):
        global GUI

        if not fullscreen:
            if event is not None:
                self.shop_width = event.w * 0.104

                update_path((event.w - self.shop_width) / 2, event.h, self.shop_width)
                update_loc(bloons_list, monkeys_list, (self.screen.get_width(), self.screen.get_height())
                           , (event.w, event.h))

                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                self.bg_scaled = pygame.transform.scale(self.bg, (event.w - self.shop_width, event.h))
                GUI = pygame.transform.scale(GUI, (event.w, event.h))

            else:
                self.shop_width = 1080 * 0.104

                update_path((1080 - self.shop_width) / 2, 700, self.shop_width)
                update_loc(bloons_list, monkeys_list, (self.screen.get_width(), self.screen.get_height())
                                , (1080, 700))

                os.environ['SDL_VIDEO_WINDOW_POS'] = "center"
                self.screen = pygame.display.set_mode((1080, 700), pygame.RESIZABLE)
                self.bg_scaled = pygame.transform.scale(self.bg, (1080 - self.shop_width, 700))
                GUI = pygame.transform.scale(GUI, (1080, 700))

        else:
            self.shop_width = 1960 * 0.104

            update_path(self.size[0] / 2, self.size[1], self.shop_width)
            update_loc(bloons_list, monkeys_list, (self.screen.get_width(), self.screen.get_height())
                       , (self.size[0] + self.shop_width, self.size[1]))

            self.screen = pygame.display.set_mode((self.size[0] + self.shop_width, self.size[1]), pygame.NOFRAME)
            self.bg_scaled = pygame.transform.scale(self.bg, self.size)
            GUI = pygame.transform.scale(GUI, (self.size[0] + self.shop_width, self.size[1]))

    def draw(self, bloons_list, monkeys_list, dt):
        global GUI

        self.screen.blit(self.bg_scaled, (self.shop_width, 0))
        GUI.set_colorkey(PINK)
        self.screen.blit(GUI, (0, 0))

        bloons_list.draw(self.screen)
        monkeys_list.draw(self.screen)
        pygame.display.flip()

