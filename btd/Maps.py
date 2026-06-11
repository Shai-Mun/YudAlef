import os
import pygame

# Global track layout registry mapping player lanes to coordinate sequences
PATHS = {
    "1": [],
    "2": []
}

# Master path repository matching level string IDs to background graphic paths
tracks = {
    "galili": f'assets/maps/galili.png'
}

def get_ratios(track):
    """
    Retrieves the raw path waypoints for a chosen layout.
    All pairs represent percentages of width and height (0.0 to 1.0)
    to maintain display-agnostic coordinate evaluation.
    """
    match track:
        case "galili":
            return [
                (0.27, 0.02),
                (0.27, 0.79),
                (0.41, 0.87),
                (0.56, 0.92),
                (0.74, 0.90),
                (0.88, 0.83),
                (0.93, 0.72),
                (0.93, 0.18),
                (0.82, 0.08),
                (0.62, 0.04),
                (0.46, 0.06),
                (0.27, 0.13),
                (0.27, 0.97),
            ]
        case _:
            return []

def inverse(track):
    """
    Horizontally mirrors a path coordinate sequence.
    Flips the X-axis decimal over the central axis line (1.0 - X)
    while preserving the Y structural height.
    """
    return [(1 - r[0], r[1]) for r in track]

def update_path():
    """
    Rebuilds the global PATHS dictionary.
    Computes standard trajectories for the local workspace and mirrored
    trajectories for the opponent workspace.
    """
    global PATHS

    track_ratios = get_ratios("galili")
    inverse_track_ratios = inverse(track_ratios)
    PATHS["1"].clear()
    PATHS["1"].extend(track_ratios)

    PATHS["2"].clear()
    PATHS["2"].extend(inverse_track_ratios)


def update_loc(player, game_rect):
    """
    Iterates through active workspace entities and instructs them to map
    their normalized vector spaces into updated display dimensions.
    """
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
    """
    Controls background graphic tracking, rendering surfaces,
    and aspect-ratio scaling transitions.
    """
    def __init__(self, track, player):
        self.ratios = get_ratios(track)
        self.bg = pygame.image.load(tracks[track])

        self.shop_width = player.game_rect.x

        self.size = [player.game_rect.width, player.game_rect.height + player.header_height]

        self.screen = pygame.display.set_mode((self.shop_width + self.size[0] * 2, self.size[1]), pygame.NOFRAME)
        self.bg_scaled = pygame.transform.scale(self.bg, (self.size[0], self.size[1]))

        update_path()

    def update_size(self, player, fullscreen, event = None):
        """
        Recalculates rendering surfaces on application resize boundaries.
        Updates internal viewport boxes and transforms spatial parameters fluidly.
        """
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
        self.size = [player.game_rect.width, player.game_rect.height]

        update_loc(player, player.game_rect)

        self.screen = pygame.display.set_mode((self.shop_width + self.size[0] * 2, self.size[1]), pygame.RESIZABLE)
        self.bg_scaled = pygame.transform.scale(self.bg, (self.size[0], self.size[1]))

        return [w, h]

    def draw_map(self, players):
        """
        Renders background layouts and composite asset layers on screen.
        Flips background surfaces on the fly to render mirrored segments correctly.
        """
        for p in players:
            self.screen.blit(self.bg_scaled, (p.game_rect.x, p.game_rect.y))
            p.bloons_list.draw(self.screen)
            p.monkeys_list.draw(self.screen)
            for m in p.monkeys_list: m.projectile_list.draw(self.screen)
            self.bg_scaled = pygame.transform.flip(self.bg_scaled, True, False)