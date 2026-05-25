import pygame

from btd.Player import _BASE_GAME_W, _BASE_GAME_H, PINK

_BLOON_NORM_W = 40 / _BASE_GAME_W
_BLOON_NORM_H = 40 / _BASE_GAME_H

DEF_SPEED = 70 / _BASE_GAME_W
# DEF_SPEED = 70
DEFAULT_BLOON = {"speed": DEF_SPEED * 1, "child": None,   "image": "red_bloon.png"}
BLOON_DATA = {
    "black": {"speed": DEF_SPEED * 1.8, "child": "pink", "image": "black_bloon.png"},
    "pink": {"speed": DEF_SPEED * 3.5, "child": "yellow", "image": "pink_bloon.png"},
    "yellow": {"speed": DEF_SPEED * 3.2, "child": "green", "image": "yellow_bloon.png"},
    "green": {"speed": DEF_SPEED * 1.8, "child": "blue", "image": "green_bloon.png"},
    "blue": {"speed": DEF_SPEED * 1.4, "child": "red",  "image": "blue_bloon.png"},
    "red": {"speed": DEF_SPEED * 1, "child": None,   "image": "red_bloon.png"}
}



class Bloon(pygame.sprite.Sprite):
    # def __init__(self, color, side, path_list):
    #     super().__init__()
    #     stats = BLOON_DATA.get(color.lower(), DEFAULT_BLOON)
    #
    #     self.type = color.lower()
    #     self.speed = stats["speed"] / 1960
    #     self.image = pygame.image.load(f"assets/bloons/{stats['image']}").convert()
    #     self.sized_image = self.image
    #     self.original_image = self.image
    #     self.side = side
    #     self.path = path_list
    #
    #     self.target_node = 1
    #     self.angle = 0
    #     self.distance = 0
    #
    #     self.pos = pygame.Vector2(path_list[0])
    #     self.img_ratio = (self.image.get_width() / 1960, self.image.get_height() / 1080)
    #     self.rect = self.image.get_rect()
    #     self.rect.center = (int(self.pos.x), int(self.pos.y))
    #
    #     self.update_visuals(pygame.display.get_window_size())

    def __init__(self, color: str, side: int, path_list: list):
        """
        Args:
            color:     Bloon colour key ("red", "blue", …).
            side:      Which player this bloon belongs to (1 or 2).
            path_list: List of normalised Vector2 waypoints (x, y both in 0..1)
                       relative to the player's game-area rectangle.
        """
        super().__init__()
        stats = BLOON_DATA.get(color.lower(), DEFAULT_BLOON)

        self.type = color.lower()
        self.speed = stats["speed"]  # Fraction of game-area width per second
        self.side = side
        self.path = path_list  # Normalised waypoints – shared reference is fine

        self.target_node = 1
        self.distance = 0.0  # Normalised distance travelled (targeting priority)

        # pos is always normalised (0..1) within the player's game_rect.
        self.pos = pygame.Vector2(self.path[0])

        self.original_image = pygame.image.load(f"assets/bloons/{stats['image']}").convert()
        self.original_image.set_colorkey(PINK)
        self.image = self.original_image
        self.rect = self.image.get_rect()

    def update_bloon_rect(self, game_rect):
        """
        Convert the normalised pos into screen pixels and rebuild self.image /
        self.rect.  Call once per frame *after* move(), before drawing.

        This is the only place pixels appear – everything else stays in 0..1 space.
        """
        sx = game_rect.x + self.pos.x * game_rect.width
        sy = game_rect.y + self.pos.y * game_rect.height
        pw = max(1, int(_BLOON_NORM_W * game_rect.width))
        ph = max(1, int(_BLOON_NORM_H * game_rect.height))

        self.image = pygame.transform.scale(self.original_image, (pw, ph))
        self.image.set_colorkey(PINK)
        self.rect = self.image.get_rect(center=(round(sx), round(sy)))

    # def update_visuals(self, new_screen_size):
    #     old_size = pygame.display.get_window_size()
    #
    #     ratio_x = self.pos.x / old_size[0]
    #     ratio_y = self.pos.y / old_size[1]
    #     self.pos.x = ratio_x * new_screen_size[0]
    #     self.pos.y = ratio_y * new_screen_size[1]
    #
    #     self.sized_image = pygame.transform.scale(self.original_image,
    #                                               (self.img_ratio[0] * new_screen_size[0],
    #                                                self.img_ratio[1] * new_screen_size[1]))
    #     self.image = self.sized_image
    #     self.rect = self.image.get_rect(center=(round(self.pos.x), round(self.pos.y)))

    def move_bloon(self, dt: float) -> bool:
        """
        Advance the bloon along its path by one frame.
        Args:
            dt: Delta time in milliseconds.
        Returns:
            True if the bloon has escaped (reached/passed the last waypoint).
        """
        if self.target_node >= len(self.path):
            return True  # Escaped – caller should deduct lives and kill()

        target = self.path[self.target_node]
        direction = target - self.pos
        dist = direction.length()
        step = self.speed * (dt / 1000)  # Normalised step this frame

        if dist <= step:
            self.pos = pygame.Vector2(target)
            self.target_node += 1
        else:
            self.pos += direction.normalize() * step

        self.distance += step
        return False

    # def move_bloon(self, dt):
    #     width = pygame.display.get_surface().get_width()
    #     pixels_per_second = self.speed * width
    #
    #     if self.target_node < len(self.path):
    #         target = self.path[self.target_node]
    #         direction = target - self.pos
    #         distance_to_target = direction.length()
    #
    #         move_distance = pixels_per_second * (dt / 1000)
    #
    #         if distance_to_target > 0:
    #             # 1. Movement
    #             if distance_to_target > move_distance:
    #                 self.pos += direction.normalize() * move_distance
    #             else:
    #                 self.pos = pygame.Vector2(target)
    #                 self.target_node += 1
    #
    #         self.rect = self.image.get_rect(center=(round(self.pos.x), round(self.pos.y)))
    #
    #         self.image.set_colorkey(PINK)
    #         self.distance += move_distance

    # def take_damage(self, dmg):
    #     amount = 0
    #     for _ in range(dmg):
    #
    #         child_type = BLOON_DATA[self.type]["child"]
    #
    #         if child_type:
    #             self.type = child_type
    #
    #             stats = BLOON_DATA[self.type]
    #             self.speed = stats["speed"] / 1960
    #             self.image = pygame.image.load(f"assets/bloons/{stats['image']}").convert()
    #             self.sized_image = self.image
    #             self.original_image = self.image
    #             self.image.set_colorkey(PINK)
    #
    #             self.img_ratio = (self.image.get_width() / 1960, self.image.get_height() / 1080)
    #             old_center = self.rect.center
    #             self.rect = self.image.get_rect()
    #             self.rect.center = old_center
    #
    #             # self.update_visuals(pygame.display.get_window_size())
    #             amount += 1
    #         else:
    #             self.kill()
    #             return amount
    #     return amount

    def take_damage(self, dmg: int) -> int:
        """
        Apply damage, downgrading the bloon layer by layer.

        Returns:
            Number of layers popped (used to award money to the player).
        """
        popped = 0
        for _ in range(dmg):
            child_type = BLOON_DATA[self.type]["child"]
            if child_type:
                self.type = child_type
                stats = BLOON_DATA[self.type]
                self.speed = stats["speed"]
                self.original_image = pygame.image.load(
                    f"assets/bloons/{stats['image']}"
                ).convert()
                self.original_image.set_colorkey(PINK)
                popped += 1
            else:
                self.kill()
                return popped
        return popped
