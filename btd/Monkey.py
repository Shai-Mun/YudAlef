import random

import pygame
import math
from Databases import MONKEY_DATA
from Projectile import Projectile
from Databases import SOUNDS

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
        global _MONKEY_NORM_W, _MONKEY_NORM_H

        stats = MONKEY_DATA[m_type]['base']

        self.type = m_type
        self.cost = stats['cost']
        self.original_range = stats['original_range']
        self.range = 0.0
        self.pierce = stats['pierce']
        self.fire_rate = stats['fire_rate']
        self.dmg = stats['dmg']
        self.image = pygame.image.load(f"assets/monkeys/{m_type}/{stats['image']}").convert()
        self.original_image = self.image
        self.image.set_colorkey(PINK)
        self.angle = 90

        self.paths = ['_', 0, 0]

        self.projectile = stats['projectile']
        self.projectile_list = pygame.sprite.Group()
        self.last_shot_time = 0
        self.proj_count = stats['proj_count']
        self.proj_angle = stats['proj_angle']
        self.projectile_speed = stats['projectile_speed']
        self.proj_dist_mult = stats['proj_dist_mult']
        self.weaknesses = stats['weaknesses'].copy()

        self.pos = pygame.Vector2(r_pos[0], r_pos[1])
        self.rect = self.image.get_rect()

        self.id = m_id

        self.hitscan = stats.get('hitscan', False)  # Check if hitscan weapon
        self.pending_children = []
        self.pending_money = 0
        self.pending_hits = []

        self.proj_size = stats.get('proj_size')
        self.size = None
        if "size" in stats:
            self.size = [stats['size'][0] / _BASE_GAME_W]
            self.size.append(stats['size'][1] / _BASE_GAME_H)

        self.ability = None  # Stores the ability dictionary when upgraded
        self.last_ability_time = None  # Timestamp tracking for cooldowns
        self.ability_active = False  # Used exclusively for duration-based states (Maelstrom)
        self.ability_start_time = 0  # Tracking variable for active duration expiration

    def update_monkey_rect(self, game_rect):
        """
        Convert the normalised pos into screen pixels and rebuild self.image /
        self.rect.  Call once per frame *after* move(), before drawing.

        This is the only place pixels appear – everything else stays in 0..1 space.
        """
        sx = game_rect.x + self.pos.x * game_rect.width
        sy = game_rect.y + self.pos.y * game_rect.height
        if self.size is None:
            pw = max(1, int(_MONKEY_NORM_W * game_rect.width))
            ph = max(1, int(_MONKEY_NORM_H * game_rect.height))
        else:
            pw = max(1, int(self.size[0] * game_rect.width))
            ph = max(1, int(self.size[1] * game_rect.height))

        self.image = pygame.transform.scale(self.original_image, (pw, ph))
        if self.type != "tack_shooter":
            self.image = pygame.transform.rotate(self.image, self.angle - 90)
        self.image.set_colorkey(PINK)
        self.rect = self.image.get_rect(center=(round(sx), round(sy)))

        self.range = self.original_range * (game_rect.width / _BASE_GAME_W)

    def update_range(self, game_rect):
        # we calculate with * 0.88 since the shop takes up 12% of the screen
        self.range = self.original_range * (game_rect.width / _BASE_GAME_W)


    def check_shoot(self, current_time, bloons_list):
        if getattr(self, 'ability_active', False) and getattr(self, 'ability', {}).get(
                'type') == 'super_monkey_fan_club':
            if current_time - self.ability_start_time >= self.ability.get('duration', 10000):
                self.ability_active = False  # Duration finished

                # Revert back to normal dart monkey stats
                self.fire_rate = getattr(self, 'original_fire_rate_smfc', self.fire_rate)
                self.dmg = getattr(self, 'original_dmg_smfc', self.dmg)

        # --- ACTIVE ABILITY RUNTIME: Blade Maelstrom ---
        if getattr(self, 'ability_active', False) and self.ability and self.ability.get('type') == 'blade_maelstrom':
            if current_time - self.ability_start_time >= self.ability.get('duration', 3000):
                self.ability_active = False  # Duration finished
            else:
                ability_fire_rate = self.ability.get('fire_rate', 60)
                if current_time - self.last_shot_time >= ability_fire_rate:
                    # Shoot 24 projectiles evenly spaced in a 360-degree radius
                    maelstrom_count = 24
                    angle_step = 360 / maelstrom_count
                    base_vector = pygame.Vector2(1, 0)

                    for i in range(maelstrom_count):
                        dest_norm = base_vector.rotate(i * angle_step)
                        self.projectile_list.add(Projectile(self, self.pos + dest_norm))

                    self.last_shot_time = current_time
            return  # Skip normal single-target targeting while Maelstrom is running

        if current_time - self.last_shot_time >= self.fire_rate:
            target = self.find_target(bloons_list)

            if target:
                normalized_direction = target.pos - self.pos
                rads = math.atan2(-normalized_direction.y, normalized_direction.x)
                self.angle = math.degrees(rads)
                self.rect = self.image.get_rect(center=self.rect.center)
                self.image.set_colorkey(PINK)

                # if self.projectile_speed >= 2000:

                if self.hitscan:
                    # Instantly apply ALL damage to the single target.
                    stun_duration = 0
                    if self.proj_angle != 0:
                        # --- FIX: Changed 'is' to '==' and tracking stun_duration ---
                        if target.type == "moab" or target.type == "bfb":
                            stun_duration = 2000
                            children, money = target.take_damage(self.dmg, 2000)
                        elif target.type == "zomg":
                            stun_duration = 500
                            children, money = target.take_damage(self.dmg, 500)
                        else:
                            children, money = target.take_damage(self.dmg)
                    else:
                        children, money = target.take_damage(self.dmg)

                    self.pending_money += money
                    # --- FIX: Add stun to pending hits data dictionary ---
                    self.pending_hits.append({"id": target.id, "dmg": self.dmg, "stun": stun_duration})

                    if children:
                        self.pending_children.extend(children)

                    # Play the popping sound
                    num = random.randint(1, 4)
                    pygame.mixer.Sound(f"assets/sounds/{SOUNDS['pop' + str(num)]}").play()

                    self.last_shot_time = current_time

                else:
                    # Standard Projectile Spawning (keep your existing code here)
                    normalized_direction = target.pos - self.pos
                    for i in range(-int(self.proj_count / 2), math.ceil(self.proj_count / 2)):
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
                if key == 'fire_rate':
                    setattr(self, key, getattr(self, key) - upgrade[key])
                elif key == 'weaknesses':
                    getattr(self, key).remove(upgrade[key])
                elif key == 'size':
                    setattr(self, key, [upgrade[key][0] / _BASE_GAME_W, upgrade[key][1] / _BASE_GAME_H])
                else:
                    if key == 'ability':
                        self.last_ability_time = pygame.time.get_ticks()
                    # This dynamically sets the attribute named after whatever is in 'key'
                    setattr(self, key, upgrade[key])

    def upgrade_image(self, path, upgrade):
        self.original_image = pygame.image.load(f"assets/monkeys/{self.type}/{self.type}{path}{upgrade}.png").convert()

    def move_projectiles(self, dt, game_rect):
        for p in self.projectile_list:
            p.move_proj(dt)
            p.update_proj_rect(game_rect)

    def check_hits(self, grid):
        all_bloons_hit = []
        all_children = []
        total_monkey_earnings = 0

        if self.pending_money > 0:
            total_monkey_earnings += self.pending_money
            self.pending_money = 0

        if self.pending_children:
            all_children.extend(self.pending_children)
            self.pending_children = []

        if self.pending_hits:
            all_bloons_hit.extend(self.pending_hits)
            self.pending_hits = []

        for p in self.projectile_list:
            curr_children, curr_earnings, curr_hits = p.check_hit(grid)

            all_children.extend(curr_children)
            all_bloons_hit.extend(curr_hits)
            total_monkey_earnings += curr_earnings
        return all_children, total_monkey_earnings, all_bloons_hit

    def trigger_ability(self, current_time, bloons_list):
        if not hasattr(self, 'ability') or not self.ability:
            return False

        # Ensure last_ability_time exists
        if not hasattr(self, 'last_ability_time'):
            self.last_ability_time = 0

        # Cooldown check
        if self.last_ability_time is not None and current_time - self.last_ability_time < self.ability.get('cooldown', 0):
            return False

        a_type = self.ability.get('type')

        # 1. SUPPLY DROP (Sniper Monkey)
        if a_type == 'supply_drop':
            min_c = self.ability.get('min_cash', 500)
            max_c = self.ability.get('max_cash', 1000)
            cash = random.randint(min_c, max_c)

            # Safe injection into the main thread's balance loop
            self.pending_money += cash

            # Play cash sound effect
            pygame.mixer.Sound(f"assets/sounds/{SOUNDS['cash']}").play()

            self.last_ability_time = current_time
            return True

        # 2. MOAB ASSASSIN (Bomb Shooter)
        elif a_type == 'moab_assassin':
            if not bloons_list:
                return False

            # Screen-wide prioritization targeting the strongest/furthest MOAB
            moab_target = None
            max_dist_traveled = -1

            for bloon in bloons_list:
                if getattr(bloon, 'type', '') in ['moab', 'bfb', 'zomg']:
                    if bloon.distance > max_dist_traveled:
                        max_dist_traveled = bloon.distance
                        moab_target = bloon

            if moab_target:
                dmg = self.ability.get('damage', 1000)
                children, money = moab_target.take_damage(dmg)

                self.pending_money += money
                self.pending_hits.append({"id": moab_target.id, "dmg": dmg, "stun": 0})
                if children:
                    self.pending_children.extend(children)

                # Play explosion audio
                pygame.mixer.Sound(f"assets/sounds/{SOUNDS['explosion']}").play()

                self.last_ability_time = current_time
                return True

            return False  # No MOAB active on screen; ability does not consume cooldown

            # 4. SUPER MONKEY FAN CLUB (Dart Monkey)
        elif a_type == 'super_monkey_fan_club':
            self.ability_active = True
            self.ability_start_time = current_time
            self.last_ability_time = current_time

            # Store original stats so we can revert them when the duration ends
            self.original_fire_rate_smfc = self.fire_rate
            self.original_dmg_smfc = self.dmg

            # Temporarily turn this monkey into a "Super Monkey"
            self.fire_rate = 30  # Shoots incredibly fast (machine gun speed)
            self.dmg = 1  # Standard super monkey damage

            return True

        # 3. BLADE MAELSTROM (Tack Shooter)
        elif a_type == 'blade_maelstrom':
            self.ability_active = True
            self.ability_start_time = current_time
            self.last_ability_time = current_time
            self.last_shot_time = 0
            return True

        return False