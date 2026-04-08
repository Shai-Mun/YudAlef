import pygame
import math
from btd.Maps import get_ratios

track_ratios = []

PATH = []
INVERSE_PATH = []
def inverse():
    return [(1 - r[0], 1 - r[1]) for r in track_ratios]

def update_path(width, height, shop_width):
    global PATH, INVERSE_PATH, track_ratios

    track_ratios = get_ratios("Galili")
    PATH = [pygame.Vector2(width*r[0] + shop_width, height*r[1]) for r in track_ratios]
    INVERSE_PATH = [pygame.Vector2(width*r[0] + width + shop_width, height*r[1]) for r in inverse()]

def update_loc(bloons_list, old_size, new_size):
    for bloon in bloons_list:
        ratio = bloon.pos.x / old_size[0]
        bloon.pos.x = new_size[0] * ratio
        ratio = bloon.pos.y / old_size[1]
        bloon.pos.y = new_size[1] * ratio

        match bloon.side:
            case 1:
                bloon.path = PATH
            case 2:
                bloon.path = INVERSE_PATH


PINK = (255, 128, 255)
DEF_SPEED = 70


class Bloon(pygame.sprite.Sprite):
    DEFAULT_BLOON = {"speed": DEF_SPEED * 1, "child": None,   "image": "red_bloon.png"}
    BLOON_DATA = {
        "black": {"speed": DEF_SPEED * 1.8, "child": "pink", "image": "black_bloon.png"},
        "pink": {"speed": DEF_SPEED * 3.5, "child": "yellow", "image": "pink_bloon.png"},
        "yellow": {"speed": DEF_SPEED * 3.2, "child": "green", "image": "yellow_bloon.png"},
        "green": {"speed": DEF_SPEED * 1.8, "child": "blue", "image": "green_bloon.png"},
        "blue": {"speed": DEF_SPEED * 1.4, "child": "red",  "image": "blue_bloon.png"},
        "red": {"speed": DEF_SPEED * 1, "child": None,   "image": "red_bloon.png"}
    }

    def __init__(self, color, side):
        super().__init__()
        stats = self.BLOON_DATA.get(color.lower(), self.DEFAULT_BLOON)

        self.type = color.lower()
        self.speed = stats["speed"]
        self.image = pygame.image.load(f"assets/bloons/{stats['image']}").convert()
        self.original_image = self.image
        self.side = side

        # side: 1 - p1 side, 2 - p2 side
        match self.side:
            case 1:
                self.path = PATH
                self.pos = pygame.Vector2(PATH[0])
            case 2:
                self.path = INVERSE_PATH
                self.pos = pygame.Vector2(INVERSE_PATH[0])

        self.target_node = 1
        self.angle = 0

        self.rect = self.image.get_rect()
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        self.distance = 0


    def update(self, dt):
        if self.target_node < len(self.path):
            target = self.path[self.target_node]
            direction = target - self.pos
            distance_to_target = direction.length()

            move_distance = self.speed * (dt / 1000)

            if distance_to_target > 0:
                # 1. Update Angle (for rotation)
                # math.atan2 returns radians; we convert to degrees
                rads = math.atan2(-direction.y, direction.x)  # Negative Y because pygame Y is inverted
                self.angle = math.degrees(rads)

                # 2. Movement
                if distance_to_target > move_distance:
                    self.pos += direction.normalize() * move_distance
                else:
                    self.pos = pygame.Vector2(target)
                    self.target_node += 1
                    # self.hit()

            # self.image = pygame.transform.rotate(self.original_image, self.angle)
            self.rect = self.image.get_rect(center=(round(self.pos.x), round(self.pos.y)))

            self.image.set_colorkey(PINK)
            self.distance += move_distance
            print(self.pos.x)

    def hit(self):
        child_type = self.BLOON_DATA[self.type]["child"]

        if child_type is not None:
            self.type = child_type

            stats = self.BLOON_DATA[self.type]
            self.speed = stats["speed"]

            self.image = pygame.image.load(f"assets/bloons/{stats['image']}").convert()
            self.original_image = self.image
            old_center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = old_center
        else:
            self.kill()

