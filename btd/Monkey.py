import pygame
import math
from Upgrades import MONKEY_DATA

PINK = (255, 128, 255)

class Monkey(pygame.sprite.Sprite):
    def __init__(self, m_type, m_pos):
        super().__init__()
        stats = MONKEY_DATA[m_type]['base']

        self.cost = stats['cost']
        self.range = stats['range']
        self.fire_rate = stats['fire_rate']
        self.image = pygame.image.load(f"assets/monkeys/{stats['image']}").convert()
        self.original_image = self.image
        self.image.set_colorkey(PINK)

        self.projectile = stats['projectile']
        self.last_shot_time = 0

        self.pos = pygame.Vector2(m_pos)
        self.rect = self.image.get_rect()
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def check_shoot(self, current_time, bloons_list):
        if current_time - self.last_shot_time >= self.fire_rate:
            target = self.find_target(bloons_list)

            if target:
                direction = target.pos - self.pos
                rads = math.atan2(-direction.y, direction.x)
                angle = math.degrees(rads)
                self.image = pygame.transform.rotate(self.original_image, angle-90)
                self.rect = self.image.get_rect(center=(round(self.pos.x), round(self.pos.y)))
                self.image.set_colorkey(PINK)

                target.hit()
                self.last_shot_time = current_time


    def find_target(self, bloons_list):
        target = None
        max_distance = -1

        for bloon in bloons_list:
            dist = pygame.math.Vector2(self.rect.center).distance_to(bloon.rect.center)

            if dist <= self.range:
                if bloon.distance > max_distance:
                    max_distance = bloon.distance
                    target = bloon
        return target

