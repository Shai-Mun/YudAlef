import random
import pygame
import math
from Databases import SOUNDS

from Player import _BASE_GAME_W, _BASE_GAME_H, PINK

_PROJ_NORM_W = 30 / _BASE_GAME_W
_PROJ_NORM_H = 30 / _BASE_GAME_H


class Projectile(pygame.sprite.Sprite):
    """
    Manages active projectiles, handling straight-line physics updates,
    out-of-bounds entity destruction, and blast radius calculations.
    """
    def __init__(self, monkey, dest):
        super().__init__()
        global _PROJ_NORM_W, _PROJ_NORM_H

        self.normalized_range_limit = (monkey.original_range * monkey.proj_dist_mult) / _BASE_GAME_W

        self.pierce = monkey.pierce
        self.type = monkey.projectile
        self.image = pygame.image.load(f"assets/projectiles/{self.type}.png").convert()
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
        Translates internal decimal positions into active screen canvas pixels.
        Terminates the sprite instance instantly if it travels past lane boundaries.
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
        Advances the projectile forward along its fixed directional path.
        Tracks the total distance covered and cleans up the instance if it passes range limits.
        """
        step = self.speed * (dt / 1000)

        rads = math.atan2(-self.direction.y, self.direction.x)
        self.angle = math.degrees(rads)
        self.pos += self.direction.normalize() * step
        self.distance += step

        if self.distance >= self.normalized_range_limit:
            self.kill()

    def check_hit(self, grid):
        """
        Queries proximity structures to evaluate collisions with enemy boxes.
        Applies damage formulas, manages pierce point depletion, and triggers radial explosions.
        """
        money_earned = 0
        bloons_hit = []
        children = []

        targets = grid.get_nearby_bloons(self)
        hits = pygame.sprite.spritecollide(self, targets, False)

        for primary_bloon in hits:
            if primary_bloon in self.hit_bloons or primary_bloon.type in self.weaknesses:
                continue

            if "bomb" in self.type or "missile" in self.type:
                pygame.mixer.Sound(f"assets/sounds/{SOUNDS['explosion']}").play()

                blast_radius = 0.08

                for splash_bloon in targets:
                    if self.pierce <= 0:
                        break

                    if splash_bloon in self.hit_bloons or splash_bloon.type in self.weaknesses:
                        continue

                    if self.pos.distance_to(splash_bloon.pos) <= blast_radius:
                        stun_duration = 0

                        if self.type == 'impact_bomb':
                            if splash_bloon.type not in ['moab', 'bfb', 'zomg']:
                                stun_duration = 2000
                                curr_children, money = splash_bloon.take_damage(self.dmg, 2000)
                            else:
                                curr_children, money = splash_bloon.take_damage(self.dmg)
                        else:
                            curr_children, money = splash_bloon.take_damage(self.dmg)

                        bloons_hit.append({"id": splash_bloon.id, "dmg": self.dmg, "stun": stun_duration})
                        money_earned += money
                        children.extend(curr_children)

                        self.hit_bloons.add(splash_bloon)
                        self.pierce -= 1

                self.kill()
                break

            else:
                stun_duration = 0
                curr_children, money = primary_bloon.take_damage(self.dmg)

                bloons_hit.append({"id": primary_bloon.id, "dmg": self.dmg, "stun": stun_duration})
                money_earned += money
                children.extend(curr_children)

                self.hit_bloons.add(primary_bloon)
                self.pierce -= 1

                if self.pierce <= 0:
                    self.kill()
                    break

        return children, money_earned, bloons_hit