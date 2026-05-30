import pygame

from btd.Player import _BASE_GAME_W, _BASE_GAME_H, PINK

_BLOON_NORM_W = 40 / _BASE_GAME_W
_BLOON_NORM_H = 40 / _BASE_GAME_H

DEF_SPEED = 65 / _BASE_GAME_W
DEFAULT_BLOON = {"speed": DEF_SPEED * 1, "child": None,   "image": "red_bloon.png"}
BLOON_DATA = {
    "rainbow": {"speed": DEF_SPEED * 1, "child": "zebra~2", "dmg": 47, "image": "rainbow_bloon.png"},
    "zebra": {"speed": DEF_SPEED * 1, "child": "black~1~white~1", "dmg": 23, "image": "zebra_bloon.png", "immunity": ["freeze", "explosion"]},
    "lead": {"speed": DEF_SPEED * 1, "child": "black~2", "dmg": 23, "image": "lead_bloon.png", "immunity": ["sharp"]},
    "white": {"speed": DEF_SPEED * 2, "child": "pink~2", "dmg": 11, "image": "white_bloon.png", "immunity": ["freeze"]},
    "black": {"speed": DEF_SPEED * 1.8, "child": "pink~2", "dmg": 11, "image": "black_bloon.png", "immunity": ["explosion"]},
    "pink": {"speed": DEF_SPEED * 3.5, "child": "yellow", "dmg": 4, "image": "pink_bloon.png"},
    "yellow": {"speed": DEF_SPEED * 3.2, "child": "green", "dmg": 3, "image": "yellow_bloon.png"},
    "green": {"speed": DEF_SPEED * 1.8, "child": "blue", "dmg": 3, "image": "green_bloon.png"},
    "blue": {"speed": DEF_SPEED * 1.4, "child": "red", "dmg": 2, "image": "blue_bloon.png"},
    "red": {"speed": DEF_SPEED * 1, "child": None, "dmg": 1, "image": "red_bloon.png"}
}



class Bloon(pygame.sprite.Sprite):
    def __init__(self, color: str, side: int, path_list: list, child_properties = None):
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
        self.dmg = stats["dmg"]
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
        if child_properties:
            self.target_node = child_properties["target_node"]
            self.distance = child_properties["distance"]
            self.pos = child_properties["pos"].copy()
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

        target = pygame.Vector2(self.path[self.target_node])
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

    def take_damage(self, dmg: int):
        """
        Apply damage, downgrading the bloon layer by layer.

        Returns:
            Number of layers popped (used to award money to the player).
        """
        children = []
        popped = 0
        for _ in range(dmg):
            child_type = BLOON_DATA[self.type]["child"]
            if child_type:
                if "~" in child_type:
                    fields = child_type.split("~")
                    for i in range(child_type.count("~") // 2 + 1):
                        for _ in range(int(fields[2*i+1])):
                            child_properties = {"target_node": self.target_node, "distance": self.distance, "pos": self.pos}
                            child = Bloon(fields[2*i], self.side, self.path, child_properties)
                            children.append(child)
                    self.kill()
                else:
                    self.type = child_type
                    stats = BLOON_DATA[self.type]
                    self.speed = stats["speed"]
                    self.dmg = stats["dmg"]
                    self.original_image = pygame.image.load(
                        f"assets/bloons/{stats['image']}"
                    ).convert()
                    self.original_image.set_colorkey(PINK)
                popped += 1
            else:
                self.kill()
                return children, popped
        return children, popped
