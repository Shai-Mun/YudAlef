import pygame
import math

from btd.Player import _BASE_GAME_W, _BASE_GAME_H, PINK

_PROJ_NORM_W = 30 / _BASE_GAME_W
_PROJ_NORM_H = 30 / _BASE_GAME_H


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

        self.pos = pygame.Vector2(monkey.pos.x, monkey.pos.y)
        # self.img_ratio = (self.image.get_width() / 1960, self.image.get_height() / 1080)
        self.rect = self.image.get_rect()
        self.target_pos = pygame.Vector2(bloon.pos)

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



    # def update_visuals(self, new_screen_size):
    #     old_size = pygame.display.get_window_size()
    #
    #     self.pos.x = self.pos_ratio[0] * new_screen_size[0]
    #     self.pos.y = self.pos_ratio[1] * new_screen_size[1]
    #
    #     self.target_pos.x = (self.target_pos.x / old_size[0]) * new_screen_size[0]
    #     self.target_pos.y = (self.target_pos.y / old_size[1]) * new_screen_size[1]
    #
    #     self.sized_image = pygame.transform.scale(self.original_image,
    #                                               (self.img_ratio[0] * new_screen_size[0],
    #                                                self.img_ratio[1] * new_screen_size[1]))
    #     self.image = self.sized_image
    #     self.rect = self.image.get_rect(center=(round(self.pos.x), round(self.pos.y)))

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
            else:
                self.pos += direction.normalize() * step

            self.distance += step

    # def move_proj(self, dt):
    #     width = pygame.display.get_surface().get_width()
    #     pixels_per_second = self.speed * width
    #
    #     direction = self.target_pos - self.pos
    #     distance_to_target = direction.length()
    #
    #     move_distance = pixels_per_second * (dt / 1000)
    #
    #     if distance_to_target > 0:
    #         rads = math.atan2(-direction.y, direction.x)  # Negative Y because pygame Y is inverted
    #         self.angle = math.degrees(rads)
    #
    #         # 2. Movement
    #         if distance_to_target > move_distance:
    #             self.pos += direction.normalize() * move_distance
    #         else:
    #             self.kill()
    #
    #     self.distance += move_distance
    #
    #     # self.image = pygame.transform.rotate(self.original_image, self.angle)
    #     # self.rect = self.image.get_rect(center=(round(self.pos.x), round(self.pos.y)))
    #     #
    #     # self.image.set_colorkey(PINK)


    def check_hit(self, grid):
        money_earned = 0

        targets = grid.get_nearby_bloons(self)
        hits = pygame.sprite.spritecollide(self, targets, False)

        for bloon in hits:
            if bloon not in self.hit_bloons and self.pierce > 0:
                # The bloon tells us how much money we just made
                money_earned += bloon.take_damage(1)
                self.hit_bloons.add(bloon)
                self.pierce -= 1

                if self.pierce <= 0:
                    self.kill()
                    break

        return money_earned
