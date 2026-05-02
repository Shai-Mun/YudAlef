import os
from Bloon import *
from Monkey import *

PINK = (255, 128, 255)

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


def update_loc(bloons_list, monkeys_list, new_size):
    for bloon in bloons_list:
        match bloon.side:
            case 1:
                bloon.path = PATHS["PATH"]
            case 2:
                bloon.path = PATHS["INVERSE_PATH"]
        bloon.update_visuals(new_size)

    for monkey in monkeys_list:
        monkey.update_visuals(new_size)
        monkey.update_range(new_size)

class Maps:
    def __init__(self, track):
        self.ratios = get_ratios(track)
        self.bg = pygame.image.load(f'assets/maps/{track}.png')

        # UI Settings
        self.pillar_width = 15
        self.border_thickness = 8
        self.ui_color = (150, 94, 63)  # Dark Grey for borders/pillar
        self.shop_color = (183, 117, 80)  # Slightly darker for shop

        self.shop_width = pygame.display.Info().current_w * 0.104

        self.size = (pygame.display.Info().current_w - self.shop_width, pygame.display.Info().current_h)
        self.screen = pygame.display.set_mode((self.size[0] + self.shop_width, self.size[1]), pygame.NOFRAME)
        self.bg_scaled = pygame.transform.scale(self.bg, self.size)

        self.screen.blit(self.bg_scaled, (self.shop_width, 0))
        update_path(self.size[0] / 2, self.size[1], self.shop_width)


    def update_size(self, bloons_list, monkeys_list, fullscreen, event = None):

        if not fullscreen:
            if event is not None:
                self.shop_width = event.w * 0.104

                update_path((event.w - self.shop_width) / 2, event.h, self.shop_width)
                update_loc(bloons_list, monkeys_list, (event.w, event.h))

                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                self.bg_scaled = pygame.transform.scale(self.bg, (event.w - self.shop_width, event.h))

            else:
                self.shop_width = 1080 * 0.104

                update_path((1080 - self.shop_width) / 2, 700, self.shop_width)
                update_loc(bloons_list, monkeys_list, (1080, 700))

                os.environ['SDL_VIDEO_WINDOW_POS'] = "center"
                self.screen = pygame.display.set_mode((1080, 700), pygame.RESIZABLE)
                self.bg_scaled = pygame.transform.scale(self.bg, (1080 - self.shop_width, 700))

        else:
            self.shop_width = 1960 * 0.104

            update_path(self.size[0] / 2, self.size[1], self.shop_width)
            update_loc(bloons_list, monkeys_list, (self.size[0] + self.shop_width, self.size[1]))

            self.screen = pygame.display.set_mode((self.size[0] + self.shop_width, self.size[1]), pygame.NOFRAME)
            self.bg_scaled = pygame.transform.scale(self.bg, self.size)

    def draw(self, bloons_list, monkeys_list, dt):

        self.screen.blit(self.bg_scaled, (self.shop_width, 0))
        bloons_list.draw(self.screen)
        monkeys_list.draw(self.screen)

