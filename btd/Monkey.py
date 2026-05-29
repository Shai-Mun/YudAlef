import pygame
import math
from Databases import MONKEY_DATA
from Projectile import Projectile

from Player import _BASE_GAME_W, _BASE_GAME_H, PINK

_MONKEY_NORM_W = 60 / _BASE_GAME_W
_MONKEY_NORM_H = 60 / _BASE_GAME_H

def upgrade_menu(monkeys_list, pos):
    for monkey in monkeys_list:
        if monkey.rect.collidepoint(pos):
            return monkey
    return None


class Monkey(pygame.sprite.Sprite):
    def __init__(self, m_type, r_pos, m_id):
        super().__init__()
        stats = MONKEY_DATA[m_type]['base']

        self.type = m_type
        self.cost = stats['cost']
        self.original_range = stats['original_range']
        self.range = 0.0
        self.pierce = stats['pierce']
        self.fire_rate = stats['fire_rate']
        self.image = pygame.image.load(f"assets/monkeys/{m_type}/{stats['image']}").convert()
        self.original_image = self.image
        self.image.set_colorkey(PINK)
        self.angle = 90

        self.paths = ['_', 0, 0]

        self.projectile = stats['projectile']
        self.projectile_list = pygame.sprite.Group()
        self.last_shot_time = 0
        self.proj_count = 1
        self.proj_angle = 0

        self.pos = pygame.Vector2(r_pos[0], r_pos[1])
        self.rect = self.image.get_rect()

        self.id = m_id

    def update_monkey_rect(self, game_rect):
        """
        Convert the normalised pos into screen pixels and rebuild self.image /
        self.rect.  Call once per frame *after* move(), before drawing.

        This is the only place pixels appear – everything else stays in 0..1 space.
        """
        sx = game_rect.x + self.pos.x * game_rect.width
        sy = game_rect.y + self.pos.y * game_rect.height
        pw = max(1, int(_MONKEY_NORM_W * game_rect.width))
        ph = max(1, int(_MONKEY_NORM_H * game_rect.height))

        self.image = pygame.transform.scale(self.original_image, (pw, ph))
        self.image = pygame.transform.rotate(self.image, self.angle - 90)
        self.image.set_colorkey(PINK)
        self.rect = self.image.get_rect(center=(round(sx), round(sy)))

        self.range = self.original_range * (game_rect.width / _BASE_GAME_W)

    def update_range(self, game_rect):
        # we calculate with * 0.88 since the shop takes up 12% of the screen
        ratio_w = game_rect.width / ((1960 - int(1960 * 0.12)) // 2)
        ratio_h = game_rect.height / 1080
        avg_ratio = (ratio_w + ratio_h) / 2

        self.range = avg_ratio * self.original_range
        self.range = self.original_range * (game_rect.width / _BASE_GAME_W)


    def check_shoot(self, current_time, bloons_list, game_rect):
        if current_time - self.last_shot_time >= self.fire_rate:
            target = self.find_target(bloons_list)

            if target:
                # m_pos = pygame.math.Vector2(game_rect.x + self.pos.x * game_rect.width, game_rect.y + self.pos.y * game_rect.height)
                # b_pos = pygame.math.Vector2(game_rect.x + target.pos.x * game_rect.width, game_rect.y + target.pos.y * game_rect.height)
                normalized_direction = target.pos - self.pos

                # direction = b_pos - m_pos
                # rads = math.atan2(-direction.y, direction.x)
                rads = math.atan2(-normalized_direction.y, normalized_direction.x)
                self.angle = math.degrees(rads)
                # self.image = pygame.transform.rotate(self.sized_image, angle-90)
                self.rect = self.image.get_rect(center=self.rect.center)
                self.image.set_colorkey(PINK)


                for i in range(-int(self.proj_count/2), math.ceil(self.proj_count/2)):
                    dest_norm = normalized_direction.rotate(i * self.proj_angle)
                    self.projectile_list.add(Projectile(self, self.pos + dest_norm))
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

    def monkey_upgrade(self, upgrade):
        print(upgrade)
        for key in upgrade:
            if key != 'name':
                if key != 'fire_rate':
                    setattr(self, key, upgrade[key])
                else:
                    # This dynamically sets the attribute named after whatever is in 'key'
                    setattr(self, key, getattr(self, key) - upgrade[key])

    def upgrade_image(self, path, upgrade):
        self.original_image = pygame.image.load(f"assets/monkeys/{self.type}/{self.type}{path}{upgrade}.png").convert()

    def move_projectiles(self, dt, game_rect):
        for p in self.projectile_list:
            p.move_proj(dt)
            p.update_proj_rect(game_rect)

    def check_hits(self, grid):
        children = []
        total_monkey_earnings = 0
        for p in self.projectile_list:
            curr_children, curr_earnings = p.check_hit(grid)
            if curr_children:
                children.extend(curr_children)
            total_monkey_earnings += curr_earnings
        return children, total_monkey_earnings

