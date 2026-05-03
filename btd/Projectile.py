import pygame
import math

PINK = (255, 128, 255)

class Projectile(pygame.sprite.Sprite):
    def __init__(self, monkey, bloon):
        super().__init__()

        self.range = monkey.range + 10
        self.original_range = self.range
        self.pierce = monkey.pierce
        self.image = pygame.image.load(f"assets/projectiles/{monkey.projectile}.png").convert()
        self.sized_image = self.image
        self.original_image = self.image
        self.image.set_colorkey(PINK)
        # 224
        self.speed = 490 / 1960

        self.angle = 0
        self.distance = 0

        self.pos_ratio = monkey.pos_ratio
        self.pos = pygame.Vector2(0, 0)
        self.img_ratio = (self.image.get_width() / 1960, self.image.get_height() / 1080)
        self.rect = self.image.get_rect()
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        self.target_pos = pygame.Vector2(bloon.pos)
        self.target = bloon

        self.update_visuals(pygame.display.get_window_size())

    def update_visuals(self, new_screen_size):
        old_size = pygame.display.get_window_size()

        self.pos.x = self.pos_ratio[0] * new_screen_size[0]
        self.pos.y = self.pos_ratio[1] * new_screen_size[1]

        self.target_pos.x = (self.target_pos.x / old_size[0]) * new_screen_size[0]
        self.target_pos.y = (self.target_pos.y / old_size[1]) * new_screen_size[1]

        self.sized_image = pygame.transform.scale(self.original_image,
                                                  (self.img_ratio[0] * new_screen_size[0],
                                                   self.img_ratio[1] * new_screen_size[1]))
        self.image = self.sized_image
        self.rect = self.image.get_rect(center=(round(self.pos.x), round(self.pos.y)))

    def move(self, dt):
        width = pygame.display.get_surface().get_width()
        pixels_per_second = self.speed * width

        direction = self.target_pos - self.pos
        distance_to_target = direction.length()

        move_distance = pixels_per_second * (dt / 1000)

        if distance_to_target > 0:
            rads = math.atan2(-direction.y, direction.x)  # Negative Y because pygame Y is inverted
            self.angle = math.degrees(rads)

            # 2. Movement
            if distance_to_target > move_distance:
                self.pos += direction.normalize() * move_distance
            else:
                self.target.hit()
                self.kill()

        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=(round(self.pos.x), round(self.pos.y)))

        self.image.set_colorkey(PINK)
        self.distance += move_distance

