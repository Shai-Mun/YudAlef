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

class Map:
    def __init__(self, track, player):
        self.ratios = get_ratios(track)
        self.bg = pygame.image.load(f'assets/maps/{track}.png')

        # self.shop_width = int(pygame.display.Info().current_w * 0.12)
        self.shop_width = player.game_rect.x

        # self.size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        self.size = [player.game_rect.width, player.game_rect.height + player.header_height]

        self.screen = pygame.display.set_mode((self.shop_width + self.size[0] * 2, self.size[1]), pygame.NOFRAME)
        self.bg_scaled = pygame.transform.scale(self.bg, (self.size[0], self.size[1]))

        update_path()

    def update_size(self, player, fullscreen, event = None):
        if fullscreen:
            w, h = player.full_size[0], player.full_size[1]
        else:
            if event:
                w, h = (event.w, event.h)
            else:
                w, h = 1080, 700
                os.environ['SDL_VIDEO_WINDOW_POS'] = "center"

        player.size = [w, h]
        player.calc_game_rect()

        self.shop_width = player.game_rect.x
        self.size = [player.game_rect.width, player.game_rect.height + player.header_height]

        update_loc(player, player.game_rect)

        self.screen = pygame.display.set_mode((self.shop_width + self.size[0] * 2, self.size[1]), pygame.RESIZABLE)
        self.bg_scaled = pygame.transform.scale(self.bg, (self.size[0], self.size[1]))

        return [w, h]

    def draw_map(self, players):
        for p in players:
            self.screen.blit(self.bg_scaled, (p.game_rect.x, 0))
            p.bloons_list.draw(self.screen)
            p.monkeys_list.draw(self.screen)
            for m in p.monkeys_list: m.projectile_list.draw(self.screen)
            self.bg_scaled = pygame.transform.flip(self.bg_scaled, True, False)

