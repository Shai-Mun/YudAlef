import pygame
from CollisionGrid import CollisionGrid
from typing import Optional
from Maps import PATHS

_BASE_GAME_W = (1960 - int(1960 * 0.12)) // 2  # 862 px reference
_BASE_GAME_H = 1080
PINK = (255, 128, 255)

class User:


    def __init__(self, side):
        self.side = side
        self.monkey_map = {
            "monkey_0": "dart_monkey",
            "monkey_1": "dart_monkey",
            "monkey_2": "dart_monkey",
            "monkey_3": "dart_monkey"
        }
        self.lives = 200

        self.money = 10000
        self.eco = 250
        self.eco_timer = 0  # Tracks time until next payout
        self.ECO_INTERVAL = 6000  # 6 seconds in milliseconds
        self.bloons_queue = []
        self.last_send = 0
        self.bloons_list = pygame.sprite.Group()
        self.monkeys_list = pygame.sprite.Group()
        self.grid = CollisionGrid()

        self.size = [1960, 1080]
        self.game_rect = pygame.Rect(0, 0, 0, 0)

        self.path = PATHS[str(side)]

        self.selected_tower: Optional[str] = None
        from Monkey import Monkey
        self.active_monkey: Optional[Monkey] = None

        self.calc_game_rect()

    def update_eco(self, dt):
        self.eco_timer += dt

        if self.eco_timer >= self.ECO_INTERVAL:
            self.money += round(self.eco)
            self.eco_timer = 0  # Reset the clock for the next 6 seconds
            print(f"Payout! Current Money: {self.money}")

    def check_send(self, curr_time):
        if len(self.bloons_queue) > 0:
            if curr_time - self.last_send >= self.bloons_queue[0][1]:
                self.bloons_list.add(self.bloons_queue.pop(0)[0])
                self.last_send = curr_time

    def update(self, dt, current_time):
        # 1. Handle Income Timer
        self.update_eco(dt)

        # 2. Spawn queued bloons
        self.check_send(current_time)

        # 3. Collision & Combat
        self.grid.clear()
        for b in self.bloons_list:
            if b.move_bloon(dt):
                self.lives -= 1
            b.update_bloon_rect(self.game_rect)
            # Check if bloon reached the end
            # if b.reached_end:
            #     self.lives -= b.leak_damage
            #     b.kill()
            # else:
            self.grid.insert_bloon(b)

        for m in self.monkeys_list:
            m.check_shoot(current_time, self.bloons_list)
            m.move_projectiles(dt, self.game_rect)  # Pass game_rect instead of self.size
            m.update_monkey_rect(self.game_rect)  # Rebuild monkey's pixel rect for rendering
            print(m.range)
            self.money += m.check_hits(self.grid)


    def try_purchase(self, cost):
        if self.money >= cost:
            self.money -= cost
            return True  # Purchase successful
        return False  # Too poor!

    def calc_game_rect(self):
        """Dynamically computes the exact screen rectangle for this player's play field."""
        w, h = self.size[0], self.size[1]
        shop_width = int(w * 0.12)
        game_width = (w - shop_width) // 2

        if self.side == 1:
            # Player 1 occupies the left half of the remaining space
            self.game_rect = pygame.Rect(shop_width, 0, game_width, h)
        else:
            # Player 2 occupies the right half of the remaining space
            self.game_rect = pygame.Rect(shop_width + game_width, 0, game_width, h)

