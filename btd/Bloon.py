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
