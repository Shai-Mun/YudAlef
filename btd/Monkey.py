import pygame
import math
from Databases import MONKEY_DATA
from Projectile import Projectile

PINK = (255, 128, 255)

def upgrade_menu(monkeys_list, pos):
    for monkey in monkeys_list:
        if monkey.rect.collidepoint(pos):
            return monkey
    return None


class Monkey(pygame.sprite.Sprite):
    def __init__(self, m_type, r_pos):
        super().__init__()
        stats = MONKEY_DATA[m_type]['base']

        self.type = m_type
        self.cost = stats['cost']
        self.range = stats['range']
        self.original_range = self.range
        self.pierce = stats['pierce']
        self.fire_rate = stats['fire_rate']
        self.image = pygame.image.load(f"assets/monkeys/{m_type}/{stats['image']}").convert()
        self.sized_image = self.image
        self.original_image = self.image
        self.image.set_colorkey(PINK)

        self.paths = ['_', 0, 0]

        self.projectile = stats['projectile']
        self.projectile_list = pygame.sprite.Group()
        self.last_shot_time = 0

        self.pos_ratio = r_pos
        self.pos = pygame.Vector2(0, 0)
        self.img_ratio = (self.image.get_width()/1960, self.image.get_height()/1080)
        self.rect = self.image.get_rect()
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        self.update_visuals(pygame.display.get_window_size())
        self.update_range(pygame.display.get_window_size())

    def update_visuals(self, new_screen_size):
        self.pos.x = self.pos_ratio[0] * new_screen_size[0]
        self.pos.y = self.pos_ratio[1] * new_screen_size[1]
        # Only the monkey knows how to scale itself
        self.sized_image = pygame.transform.scale(self.original_image,
                                                  (self.img_ratio[0] * new_screen_size[0],
                                                   self.img_ratio[1] * new_screen_size[1]))
        self.image = self.sized_image
        self.rect = self.image.get_rect(center=(round(self.pos.x), round(self.pos.y)))

    def update_range(self, new_screen_size):
        # we calculate with * 0.88 since the shop takes up 12% of the screen
        ratio_w = (new_screen_size[0] * 0.88) / (1960 * 0.88)
        ratio_h = new_screen_size[1] / 1080

        avg_ratio = (ratio_w + ratio_h) / 2
        self.range = avg_ratio * self.original_range

    def check_shoot(self, current_time, bloons_list):
        if current_time - self.last_shot_time >= self.fire_rate:
            target = self.find_target(bloons_list)

            if target:
                direction = target.pos - self.pos
                rads = math.atan2(-direction.y, direction.x)
                angle = math.degrees(rads)
                self.image = pygame.transform.rotate(self.sized_image, angle-90)
                self.rect = self.image.get_rect(center=self.rect.center)
                # self.rect = self.sized_image.get_rect(center=(round(self.pos.x), round(self.pos.y)))
                self.image.set_colorkey(PINK)

                self.projectile_list.add(Projectile(self, target))
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

    def upgrade(self, upgrade):
        print(upgrade)
        for key in upgrade:
            if key != 'name':
                if key != 'fire_rate':
                    setattr(self, key, upgrade[key])
                else:
                    # This dynamically sets the attribute named after whatever is in 'key'
                    setattr(self, key, getattr(self, key) - upgrade[key])

    def move_projectiles(self, dt):
        for p in self.projectile_list:
            p.move(dt)