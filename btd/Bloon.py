import pygame
import math  # Imported for calculating the movement angle along the road

from Player import _BASE_GAME_W, _BASE_GAME_H, PINK

_BLOON_NORM_W = 40 / _BASE_GAME_W
_BLOON_NORM_H = 40 / _BASE_GAME_H

DEF_SPEED = 65 / _BASE_GAME_W
DEFAULT_BLOON = {"speed": DEF_SPEED * 1, "child": None, "image": "red_bloon.png"}
BLOON_DATA = {
    "zomg": {"speed": DEF_SPEED * 0.18, "child": "bfb~4", "dmg": 4000, "image": "zomg.png", "is_moab": True, "hp": 4000,
             "size": (120, 120)},
    "bfb": {"speed": DEF_SPEED * 0.25, "child": "moab~4", "dmg": 700, "image": "bfb.png", "is_moab": True, "hp": 700,
            "size": (100, 100)},
    "moab": {"speed": DEF_SPEED * 0.5, "child": "ceramic~4", "dmg": 200, "image": "moab.png", "is_moab": True,
             "hp": 200, "size": (80, 80)},
    "ceramic": {"speed": DEF_SPEED * 1.5, "child": "rainbow~2", "dmg": 104, "image": "ceramic_bloon.png", "hp": 10},
    "rainbow": {"speed": DEF_SPEED * 1, "child": "zebra~2", "dmg": 47, "image": "rainbow_bloon.png"},
    "zebra": {"speed": DEF_SPEED * 1, "child": "black~1~white~1", "dmg": 23, "image": "zebra_bloon.png",
              "immunity": ["freeze", "explosion"]},
    "lead": {"speed": DEF_SPEED * 1, "child": "black~2", "dmg": 23, "image": "lead_bloon.png", "immunity": ["sharp"]},
    "white": {"speed": DEF_SPEED * 2, "child": "pink~2", "dmg": 11, "image": "white_bloon.png", "immunity": ["freeze"]},
    "black": {"speed": DEF_SPEED * 1.8, "child": "pink~2", "dmg": 11, "image": "black_bloon.png",
              "immunity": ["explosion"]},
    "pink": {"speed": DEF_SPEED * 3.5, "child": "yellow", "dmg": 4, "image": "pink_bloon.png"},
    "yellow": {"speed": DEF_SPEED * 3.2, "child": "green", "dmg": 3, "image": "yellow_bloon.png"},
    "green": {"speed": DEF_SPEED * 1.8, "child": "blue", "dmg": 3, "image": "green_bloon.png"},
    "blue": {"speed": DEF_SPEED * 1.4, "child": "red", "dmg": 2, "image": "blue_bloon.png"},
    "red": {"speed": DEF_SPEED * 1, "child": None, "dmg": 1, "image": "red_bloon.png"}
}


class Bloon(pygame.sprite.Sprite):
    def __init__(self, color: str, side: int, path_list: list, b_id, child_properties=None):
        """
        Args:
            color:     Bloon colour key ("red", "blue", …).
            side:      Which player this bloon belongs to (1 or 2).
            path_list: List of normalised Vector2 waypoints (x, y both in 0..1)
                       relative to the player's game-area rectangle.
        """
        super().__init__()

        self.id = b_id

        stats = BLOON_DATA.get(color.lower(), DEFAULT_BLOON)

        self.type = color.lower()
        self.speed = stats["speed"]  # Fraction of game-area width per second
        self.dmg = stats["dmg"]
        self.hp = stats.get('hp')
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

        self.move = True
        self.time_stunned = 0
        self.when_stunned = 0

        # --- MOAB configuration and custom sizing pattern ---
        self.is_moab = stats.get("is_moab", False)
        self.size = None
        if "size" in stats:
            self.size = [stats['size'][0] / _BASE_GAME_W, stats['size'][1] / _BASE_GAME_H]

        if child_properties:
            self.target_node = child_properties["target_node"]
            self.distance = child_properties["distance"]
            self.pos = child_properties["pos"].copy()
            self.move = child_properties.get("move", True)
            self.time_stunned = child_properties.get("time_stunned", 0)
            self.when_stunned = child_properties.get("when_stunned", 0)

        # --- Track movement angle for MOAB rotation ---
        self.angle = 0
        if self.is_moab and self.target_node < len(self.path):
            direction = pygame.Vector2(self.path[self.target_node]) - self.pos
            if direction.length() > 0:
                rads = math.atan2(-direction.y, direction.x)
                self.angle = math.degrees(rads)

    def update_bloon_rect(self, game_rect):
        """
        Convert the normalised pos into screen pixels and rebuild self.image /
        self.rect.  Call once per frame *after* move(), before drawing.

        This is the only place pixels appear – everything else stays in 0..1 space.
        """
        sx = game_rect.x + self.pos.x * game_rect.width
        sy = game_rect.y + self.pos.y * game_rect.height

        # Use custom size if specified (matching Sniper Monkey pattern)
        if self.size is None:
            pw = max(1, int(_BLOON_NORM_W * game_rect.width))
            ph = max(1, int(_BLOON_NORM_H * game_rect.height))
        else:
            pw = max(1, int(self.size[0] * game_rect.width))
            ph = max(1, int(self.size[1] * game_rect.height))

        self.image = pygame.transform.scale(self.original_image, (pw, ph))

        # Only spin MOAB-class targets using the self.angle configuration
        if self.is_moab:
            self.image = pygame.transform.rotate(self.image, self.angle)

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

        if self.move:
            target = pygame.Vector2(self.path[self.target_node])
            direction = target - self.pos
            dist = direction.length()
            step = self.speed * (dt / 1000)  # Normalised step this frame

            if dist <= step:
                self.pos = pygame.Vector2(target)
                self.target_node += 1
            else:
                self.pos += direction.normalize() * step

            # --- Update angle dynamically along the road if it is a MOAB ---
            if self.is_moab and direction.length() > 0:
                rads = math.atan2(-direction.y, direction.x)
                self.angle = math.degrees(rads)

            self.distance += step
        else:
            if pygame.time.get_ticks() - self.when_stunned >= self.time_stunned:
                self.move = True
                self.time_stunned = 0
                self.when_stunned = 0

        return False

    def take_damage(self, dmg: int, stun=None):
        """
        Apply damage, downgrading the bloon layer by layer.
        Handles high-damage overflow perfectly for multi-child bloons.
        """
        children = []
        popped = 0
        rem_dmg = dmg

        while rem_dmg > 0:
            if self.hp is None or self.hp <= 0:
                child_type = BLOON_DATA[self.type]["child"]

                if child_type:
                    if "~" in child_type:
                        self.kill()
                        popped += 1
                        rem_dmg -= 1

                        fields = child_type.split("~")
                        spawned_children = []
                        child_index = 0
                        for i in range(len(fields) // 2):
                            c_type = fields[2 * i]
                            count = int(fields[2 * i + 1])
                            for _ in range(count):
                                child_properties = {
                                    "target_node": self.target_node,
                                    "distance": self.distance,
                                    "pos": self.pos
                                }

                                # Only apply stun properties if a valid stun duration exists
                                if stun is not None and stun > 0:
                                    child_properties["move"] = False
                                    child_properties["time_stunned"] = stun
                                    child_properties["when_stunned"] = pygame.time.get_ticks()

                                child_id = f"{self.id}_{child_index}"
                                child_index += 1
                                spawned_children.append(Bloon(c_type, self.side, self.path, child_id, child_properties))

                        if rem_dmg > 0:
                            dmg_per_child = rem_dmg // len(spawned_children)
                            extra_dmg = rem_dmg % len(spawned_children)

                            for idx, child in enumerate(spawned_children):
                                child_dmg = dmg_per_child + (1 if idx < extra_dmg else 0)
                                if child_dmg > 0:
                                    # --- FIX 1: Pass the stun argument down via recursion ---
                                    sub_children, sub_popped = child.take_damage(child_dmg, stun=stun)
                                    children.extend(sub_children)
                                    popped += sub_popped
                                else:
                                    children.append(child)
                        else:
                            children.extend(spawned_children)

                        return children, popped

                    else:
                        # Single child downgrade (e.g. Blue -> Red)
                        self.type = child_type
                        stats = BLOON_DATA[self.type]
                        self.speed = stats["speed"]
                        self.dmg = stats.get("dmg", 1)
                        self.original_image = pygame.image.load(f"assets/bloons/{stats['image']}").convert()
                        self.original_image.set_colorkey(PINK)

                        # --- Re-verify MOAB status and size configuration for downgrades ---
                        self.is_moab = stats.get("is_moab", False)
                        self.size = None
                        if "size" in stats:
                            self.size = [stats['size'][0] / _BASE_GAME_W, stats['size'][1] / _BASE_GAME_H]

                        # --- FIX 2: Only freeze movement if stun is explicitly passed ---
                        if stun is not None and stun > 0:
                            self.move = False
                            self.time_stunned = stun
                            self.when_stunned = pygame.time.get_ticks()

                        popped += 1
                        rem_dmg -= 1
                else:
                    self.kill()
                    popped += 1
                    return children, popped

            else:
                # --- FIX 3: Multi-HP layer damage (MOABs/Ceramics) ---
                if stun is not None and stun > 0:
                    self.move = False
                    self.time_stunned = stun
                    self.when_stunned = pygame.time.get_ticks()

                popped += 1
                self.hp -= 1
                rem_dmg -= 1

        return children, popped