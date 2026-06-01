import random

import pygame
import math
from Databases import SOUNDS

from btd.Player import _BASE_GAME_W, _BASE_GAME_H, PINK

_PROJ_NORM_W = 30 / _BASE_GAME_W
_PROJ_NORM_H = 30 / _BASE_GAME_H


class Projectile(pygame.sprite.Sprite):
    def __init__(self, monkey, dest):
        super().__init__()
        global _PROJ_NORM_W, _PROJ_NORM_H

        self.normalized_range_limit = (monkey.original_range * monkey.proj_dist_mult) / _BASE_GAME_W

        self.pierce = monkey.pierce
        self.image = pygame.image.load(f"assets/projectiles/{monkey.projectile}.png").convert()
        self.sized_image = self.image
        self.original_image = self.image
        self.image.set_colorkey(PINK)
        self.speed = monkey.projectile_speed / _BASE_GAME_W
        self.weaknesses = monkey.weaknesses
        self.dmg = monkey.dmg

        self.angle = 0
        self.distance = 0

        self.pos = pygame.Vector2(monkey.pos)
        self.rect = self.image.get_rect()
        target_pos = pygame.Vector2(dest)
        self.direction = target_pos - self.pos


        self.hit_bloons = set()

        pygame.mixer.init()

        self.size = None
        if monkey.proj_size is not None:
            self.size = [monkey.proj_size[0] / _BASE_GAME_W]
            self.size.append(monkey.proj_size[1] / _BASE_GAME_H)


    def update_proj_rect(self, game_rect):
        """
        Convert the normalised pos into screen pixels and rebuild self.image /
        self.rect.  Call once per frame *after* move(), before drawing.

        This is the only place pixels appear – everything else stays in 0..1 space.
        """

        sx = game_rect.x + self.pos.x * game_rect.width
        sy = game_rect.y + self.pos.y * game_rect.height
        if self.size is None:
            pw = max(1, int(_PROJ_NORM_W * game_rect.width))
            ph = max(1, int(_PROJ_NORM_H * game_rect.height))
        else:
            pw = max(1, int(self.size[0] * game_rect.width))
            ph = max(1, int(self.size[1] * game_rect.height))

        self.image = pygame.transform.scale(self.original_image, (pw, ph))
        self.image = pygame.transform.rotate(self.image, self.angle)
        self.image.set_colorkey(PINK)
        self.rect = self.image.get_rect(center=(round(sx), round(sy)))

        if not game_rect.x < sx < game_rect.x + game_rect.width or not game_rect.y < sy < game_rect.y + game_rect.height:
            self.kill()

    def move_proj(self, dt: float):
        """
        Advance the bloon along its path by one frame.
        Args:
            dt: Delta time in milliseconds.
        Returns:
            True if the bloon has escaped (reached/passed the last waypoint).
        """
        step = self.speed * (dt / 1000)  # Normalised step this frame

        rads = math.atan2(-self.direction.y, self.direction.x)  # Negative Y because pygame Y is inverted
        self.angle = math.degrees(rads)
        self.pos += self.direction.normalize() * step
        self.distance += step

        if self.distance >= self.normalized_range_limit:
            self.kill()

    def check_hit(self, grid):
        money_earned = 0
        children = []
        targets = grid.get_nearby_bloons(self)
        hits = pygame.sprite.spritecollide(self, targets, False)

        for bloon in hits:
            if bloon not in self.hit_bloons and self.pierce > 0:
                # The bloon tells us how much money we just made
                if bloon.type not in self.weaknesses:
                    curr_children, money = bloon.take_damage(self.dmg)
                    money_earned += money

                    if curr_children:
                        children.extend(curr_children)

                    self.hit_bloons.add(bloon)

                    num = random.randint(1, 4)
                    pygame.mixer.Sound(f"assets/sounds/{SOUNDS["pop" + str(num)]}").play()
                    self.pierce -= 1
                    if self.pierce <= 0:
                        self.kill()
                        break
                else:
                    pygame.mixer.Sound(f"assets/sounds/{SOUNDS[bloon.type + "Hit"]}").play()
        return children, money_earned
