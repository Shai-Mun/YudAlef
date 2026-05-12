import pygame
import math

PINK = (255, 128, 255)
DEF_SPEED = 70
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
    def __init__(self, color, side, path_list):
        super().__init__()
        stats = BLOON_DATA.get(color.lower(), DEFAULT_BLOON)

        self.type = color.lower()
        self.speed = stats["speed"] / 1960
        self.image = pygame.image.load(f"assets/bloons/{stats['image']}").convert()
        self.sized_image = self.image
        self.original_image = self.image
        self.side = side
        self.path = path_list

        self.target_node = 1
        self.angle = 0
        self.distance = 0

        self.pos = pygame.Vector2(path_list[0])
        self.img_ratio = (self.image.get_width() / 1960, self.image.get_height() / 1080)
        self.rect = self.image.get_rect()
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        self.update_visuals(pygame.display.get_window_size())

    def update_visuals(self, new_screen_size):
        old_size = pygame.display.get_window_size()

        ratio_x = self.pos.x / old_size[0]
        ratio_y = self.pos.y / old_size[1]
        self.pos.x = ratio_x * new_screen_size[0]
        self.pos.y = ratio_y * new_screen_size[1]

        self.sized_image = pygame.transform.scale(self.original_image,
                                                  (self.img_ratio[0] * new_screen_size[0],
                                                   self.img_ratio[1] * new_screen_size[1]))
        self.image = self.sized_image
        self.rect = self.image.get_rect(center=(round(self.pos.x), round(self.pos.y)))

    def move(self, dt):
        width = pygame.display.get_surface().get_width()
        pixels_per_second = self.speed * width

        if self.target_node < len(self.path):
            target = self.path[self.target_node]
            direction = target - self.pos
            distance_to_target = direction.length()

            move_distance = pixels_per_second * (dt / 1000)

            if distance_to_target > 0:
                # 1. Movement
                if distance_to_target > move_distance:
                    self.pos += direction.normalize() * move_distance
                else:
                    self.pos = pygame.Vector2(target)
                    self.target_node += 1

            self.rect = self.image.get_rect(center=(round(self.pos.x), round(self.pos.y)))

            self.image.set_colorkey(PINK)
            self.distance += move_distance

    def take_damage(self, dmg):
        amount = 0
        for i in range(dmg):

            child_type = BLOON_DATA[self.type]["child"]

            if child_type is not None:
                self.type = child_type

                stats = BLOON_DATA[self.type]
                self.speed = stats["speed"] / 1960

                self.image = pygame.image.load(f"assets/bloons/{stats['image']}").convert()
                self.sized_image = self.image
                self.original_image = self.image
                self.image.set_colorkey(PINK)

                self.img_ratio = (self.image.get_width() / 1960, self.image.get_height() / 1080)
                old_center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = old_center

                self.update_visuals(pygame.display.get_window_size())
                amount += 1
            else:
                self.kill()
        return amount

