import os
import pygame

PATHS = {
    "1": [],
    "2": []
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

def inverse(track):
    return [(1 - r[0], r[1]) for r in track]

def update_path():
    global PATHS

    track_ratios = get_ratios("galili")
    inverse_track_ratios = inverse(track_ratios)
    # PATHS["1"] = [pygame.Vector2(width*r[0] + shop_width, height*r[1]) for r in track_ratios]
    # PATHS["2"] = [pygame.Vector2(width*r[0] + width + shop_width, height*r[1]) for r in inverse()]
    PATHS["1"].clear()
    PATHS["1"].extend(track_ratios)

    PATHS["2"].clear()
    PATHS["2"].extend(inverse_track_ratios)


def update_loc(player, game_rect):
    for bloon in player.bloons_list:
        match bloon.side:
            case 1:
                bloon.path = PATHS["1"]
            case 2:
                bloon.path = PATHS["2"]
        bloon.update_bloon_rect(game_rect)

    for monkey in player.monkeys_list:
        monkey.update_monkey_rect(game_rect)
        monkey.update_range(game_rect)

class Map:
    def __init__(self, track):
        self.ratios = get_ratios(track)
        self.bg = pygame.image.load(f'assets/maps/{track}.png')

        self.shop_width = int(pygame.display.Info().current_w * 0.12)

        self.size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        self.screen = pygame.display.set_mode((self.size[0], self.size[1]), pygame.NOFRAME)
        self.bg_scaled = pygame.transform.scale(self.bg, (self.size[0] - self.shop_width, self.size[1]))

        self.screen.blit(self.bg_scaled, (self.shop_width, 0))
        # update_path((self.size[0] - self.shop_width) / 2, self.size[1], self.shop_width)
        update_path()

    def update_size(self, player, fullscreen, event = None):
        if fullscreen:
            w, h = 1960, 1080
        else:
            if event:
                w, h = (event.w, event.h)
            else:
                w, h = 1080, 700
                os.environ['SDL_VIDEO_WINDOW_POS'] = "center"

        self.shop_width = int(w * 0.12)

        # update_path((w - self.shop_width) / 2, h, self.shop_width)
        update_loc(player, player.game_rect)

        self.screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)
        self.bg_scaled = pygame.transform.scale(self.bg, (w - self.shop_width, h))

        return [w, h]

    def draw_map(self, players):
        self.screen.blit(self.bg_scaled, (self.shop_width, 0))
        for p in players:
            p.bloons_list.draw(self.screen)
            p.monkeys_list.draw(self.screen)
            for m in p.monkeys_list: m.projectile_list.draw(self.screen)

