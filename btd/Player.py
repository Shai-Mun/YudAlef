import pygame
from CollisionGrid import CollisionGrid
from typing import Optional
from Monkey import *
from btd.GUI import GameInterface, UpgradeMenu
from btd.Maps import Maps, PATHS


class Player:
    def __init__(self, side):
        self.side = side
        self.monkey_map = {
            "monkey_0": "dart_monkey",
            "monkey_1": "dart_monkey",
            "monkey_2": "dart_monkey",
            "monkey_3": "dart_monkey"
        }
        self.money = 300
        self.eco = 250
        self.eco_timer = 0  # Tracks time until next payout
        self.ECO_INTERVAL = 6000  # 6 seconds in milliseconds
        self.bloons_queue = []
        self.last_send = 0
        self.bloons_list = pygame.sprite.Group()
        self.monkeys_list = pygame.sprite.Group()
        self.grid = CollisionGrid()

        # self.game_map = Maps("galili")
        # self.gui = GameInterface()
        # self.gui.set_monkey_imgs(self.monkey_map)
        # self.upgrade_gui = UpgradeMenu()

        self.path = PATHS[str(side)]

        self.selected_tower: Optional[str] = None
        self.active_monkey: Optional[Monkey] = None

    def update_eco(self, dt):
        self.eco_timer += dt

        if self.eco_timer >= self.ECO_INTERVAL:
            self.money += self.eco
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
            b.move(dt)
            # Check if bloon reached the end
            # if b.reached_end:
            #     self.lives -= b.leak_damage
            #     b.kill()
            # else:
            self.grid.insert_bloon(b)

        for m in self.monkeys_list:
            m.check_shoot(current_time, self.bloons_list)
            self.money += m.move_projectiles(dt, self.grid)

    def try_purchase(self, cost):
        if self.money >= cost:
            self.money -= cost
            return True  # Purchase successful
        return False  # Too poor!

