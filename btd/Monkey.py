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
    """
    Checks if a screen coordinate collides with an existing monkey tower box.
    Returns the selected tower reference, or None if the space is empty.
    """
    for monkey in monkeys_list:
        if monkey.rect.collidepoint(pos):
            return monkey
    return None


class Monkey(pygame.sprite.Sprite):
    """
    Represents defensive units, managing combat statistics, weapon firing rates,
    targeting vectors, and cooldown loops for active abilities.
    """
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

        self.hitscan = stats.get('hitscan', False)
        self.pending_children = []
        self.pending_money = 0
        self.pending_hits = []

        self.proj_size = stats.get('proj_size')
        self.size = None
        if "size" in stats:
            self.size = [stats['size'][0] / _BASE_GAME_W]
            self.size.append(stats['size'][1] / _BASE_GAME_H)

        self.ability = None
        self.last_ability_time = None
        self.ability_active = False
        self.ability_start_time = 0

    def update_monkey_rect(self, game_rect):
        """
        Translates normalized float vectors into actual pixel boundaries.
        Handles orientation adjustments to rotate toward dynamic targets.
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
        """
        Updates the operational combat range metric when display scales shift.
        """
        self.range = self.original_range * (game_rect.width / _BASE_GAME_W)


    def check_shoot(self, current_time, bloons_list):
        """
        Handles weapon fire timing checks. Implements hitscan processing,
        projectile spawning loops, and active duration states.
        """
        if getattr(self, 'ability_active', False) and getattr(self, 'ability', {}).get(
                'type') == 'super_monkey_fan_club':
            if current_time - self.ability_start_time >= self.ability.get('duration', 10000):
                self.ability_active = False

                self.fire_rate = getattr(self, 'original_fire_rate_smfc', self.fire_rate)
                self.dmg = getattr(self, 'original_dmg_smfc', self.dmg)

        if getattr(self, 'ability_active', False) and self.ability and self.ability.get('type') == 'blade_maelstrom':
            if current_time - self.ability_start_time >= self.ability.get('duration', 3000):
                self.ability_active = False
            else:
                ability_fire_rate = self.ability.get('fire_rate', 60)
                if current_time - self.last_shot_time >= ability_fire_rate:
                    maelstrom_count = 24
                    angle_step = 360 / maelstrom_count
                    base_vector = pygame.Vector2(1, 0)

                    for i in range(maelstrom_count):
                        dest_norm = base_vector.rotate(i * angle_step)
                        self.projectile_list.add(Projectile(self, self.pos + dest_norm))

                    self.last_shot_time = current_time
            return

        if current_time - self.last_shot_time >= self.fire_rate:
            target = self.find_target(bloons_list)

            if target:
                normalized_direction = target.pos - self.pos
                rads = math.atan2(-normalized_direction.y, normalized_direction.x)
                self.angle = math.degrees(rads)
                self.rect = self.image.get_rect(center=self.rect.center)
                self.image.set_colorkey(PINK)

                if self.hitscan:
                    stun_duration = 0
                    if self.proj_angle != 0:
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
                    self.pending_hits.append({"id": target.id, "dmg": self.dmg, "stun": stun_duration})

                    if children:
                        self.pending_children.extend(children)

                    self.last_shot_time = current_time

                else:
                    normalized_direction = target.pos - self.pos
                    for i in range(-int(self.proj_count / 2), math.ceil(self.proj_count / 2)):
                        dest_norm = normalized_direction.rotate(i * self.proj_angle)
                        self.projectile_list.add(Projectile(self, self.pos + dest_norm))

                    self.last_shot_time = current_time

                num = random.randint(1, 4)
                pygame.mixer.Sound(f"assets/sounds/{SOUNDS['pop' + str(num)]}").play()

    def find_target(self, bloons_list):
        """
        Scans for threats inside the tower's range radius.
        Targets the threat that has traveled furthest along the path layout.
        """
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
        """
        Mutates tower state dictionaries with upgraded stats.
        Dynamically modifies firing rates, resistance sets, and bounding setups.
        """
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
                    setattr(self, key, upgrade[key])

    def upgrade_image(self, path, upgrade):
        """
        Replaces the source bitmap asset reference when an upgrade tier is unlocked.
        """
        self.original_image = pygame.image.load(f"assets/monkeys/{self.type}/{self.type}{path}{upgrade}.png").convert()

    def move_projectiles(self, dt, game_rect):
        """
        Advances the physical positions of all projectiles spawned by this tower.
        """
        for p in self.projectile_list:
            p.move_proj(dt)
            p.update_proj_rect(game_rect)

    def check_hits(self, grid):
        """
        Gathers structural metrics on projectile hits recorded during the current frame.
        Aggregates cash generated, hits scored, and new child entities spawned.
        """
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
        """
        Executes unique active abilities, managing ability durations,
        cooldown conditions, and screen-wide target checks.
        """
        if not hasattr(self, 'ability') or not self.ability:
            return False

        if not hasattr(self, 'last_ability_time'):
            self.last_ability_time = 0

        if self.last_ability_time is not None and current_time - self.last_ability_time < self.ability.get('cooldown', 0):
            return False

        a_type = self.ability.get('type')

        if a_type == 'supply_drop':
            min_c = self.ability.get('min_cash', 500)
            max_c = self.ability.get('max_cash', 1000)
            cash = random.randint(min_c, max_c)

            self.pending_money += cash

            pygame.mixer.Sound(f"assets/sounds/{SOUNDS['cash']}").play()

            self.last_ability_time = current_time
            return True

        elif a_type == 'moab_assassin':
            if not bloons_list:
                return False

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

                pygame.mixer.Sound(f"assets/sounds/{SOUNDS['explosion']}").play()

                self.last_ability_time = current_time
                return True

            return False

        elif a_type == 'super_monkey_fan_club':
            self.ability_active = True
            self.ability_start_time = current_time
            self.last_ability_time = current_time

            self.original_fire_rate_smfc = self.fire_rate
            self.original_dmg_smfc = self.dmg

            self.fire_rate = 30
            self.dmg = 1

            return True

        elif a_type == 'blade_maelstrom':
            self.ability_active = True
            self.ability_start_time = current_time
            self.last_ability_time = current_time
            self.last_shot_time = 0
            return True

        return False