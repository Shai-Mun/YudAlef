import pygame
import math

from numpy.matlib import empty

from btd.Player import _BASE_GAME_W, _BASE_GAME_H, PINK

_PROJ_NORM_W = 30 / _BASE_GAME_W
_PROJ_NORM_H = 30 / _BASE_GAME_H


class Projectile(pygame.sprite.Sprite):
    def __init__(self, monkey, dest):
        super().__init__()

        self.range = monkey.range + 10
        self.original_range = self.range
        self.normalized_range_limit = monkey.original_range / _BASE_GAME_W

        self.pierce = monkey.pierce
        self.image = pygame.image.load(f"assets/projectiles/{monkey.projectile}.png").convert()
        self.sized_image = self.image
        self.original_image = self.image
        self.image.set_colorkey(PINK)
        # 224
        self.speed = 490 / 1960

        self.angle = 0
        self.distance = 0

        self.pos = pygame.Vector2(monkey.pos.x, monkey.pos.y)
        # self.img_ratio = (self.image.get_width() / 1960, self.image.get_height() / 1080)
        self.rect = self.image.get_rect()
        self.target_pos = pygame.Vector2((dest.x, dest.y))

        self.hit_bloons = set()

        # self.update_visuals(pygame.display.get_window_size())

    def update_proj_rect(self, game_rect):
        """
        Convert the normalised pos into screen pixels and rebuild self.image /
        self.rect.  Call once per frame *after* move(), before drawing.

        This is the only place pixels appear – everything else stays in 0..1 space.
        """

        sx = game_rect.x + self.pos.x * game_rect.width
        sy = game_rect.y + self.pos.y * game_rect.height
        pw = max(1, int(_PROJ_NORM_W * game_rect.width))
        ph = max(1, int(_PROJ_NORM_H * game_rect.height))

        self.image = pygame.transform.scale(self.original_image, (pw, ph))
        self.image = pygame.transform.rotate(self.image, self.angle)
        self.image.set_colorkey(PINK)
        self.rect = self.image.get_rect(center=(round(sx), round(sy)))

    def move_proj(self, dt: float):
        """
        Advance the bloon along its path by one frame.
        Args:
            dt: Delta time in milliseconds.
        Returns:
            True if the bloon has escaped (reached/passed the last waypoint).
        """
        direction = self.target_pos - self.pos
        dist = direction.length()
        step = self.speed * (dt / 1000)  # Normalised step this frame

        if dist > 0:
            rads = math.atan2(-direction.y, direction.x)  # Negative Y because pygame Y is inverted
            self.angle = math.degrees(rads)

            if dist <= step:
                self.kill()
                return
            else:
                self.pos += direction.normalize() * step

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
                curr_children, money = bloon.take_damage(1)
                money_earned += money

                if curr_children:
                    children.extend(curr_children)

                self.hit_bloons.add(bloon)
                self.pierce -= 1

                if self.pierce <= 0:
                    self.kill()
                    break
        return children, money_earned
