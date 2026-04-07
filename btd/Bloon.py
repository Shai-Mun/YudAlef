import pygame
import math

PATH = [
        pygame.Vector2(0, 200),  # Start (Off-screen left)
        pygame.Vector2(300, 200),  # First turn
        pygame.Vector2(300, 500),  # Second turn
        pygame.Vector2(600, 500),  # Third turn
        pygame.Vector2(600, -50)  # Exit (Off-screen top)
]
PINK = (255, 128, 255)
DEF_SPEED = 1

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

    def __init__(self, color):
        super().__init__()
        stats = self.BLOON_DATA.get(color.lower(), self.DEFAULT_BLOON)

        self.type = color.lower()
        self.speed = stats["speed"]
        self.image = pygame.image.load(f"assets/bloons/{stats['image']}").convert()
        self.original_image = self.image

        self.path = PATH
        self.pos = pygame.Vector2(PATH[0])
        self.target_node = 1
        self.angle = 0

        self.rect = self.image.get_rect()
        self.rect.center = (int(self.pos.x), int(self.pos.y))


    def update(self):
        if self.target_node < len(self.path):
            target = self.path[self.target_node]
            direction = target - self.pos

            if direction.length() > 0:
                # 1. Update Angle (for rotation)
                # math.atan2 returns radians; we convert to degrees
                rads = math.atan2(-direction.y, direction.x)  # Negative Y because pygame Y is inverted
                self.angle = math.degrees(rads)

                # 2. Movement
                if direction.length() > self.speed:
                    self.pos += direction.normalize() * self.speed
                else:
                    self.pos = pygame.Vector2(target)
                    self.target_node += 1
                    self.hit()


            self.image = pygame.transform.rotate(self.original_image, self.angle)
            self.rect = self.image.get_rect(center=self.pos)

            self.image.set_colorkey(PINK)



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

