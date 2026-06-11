import hashlib
import string
import secrets
import pygame
from CollisionGrid import CollisionGrid
from typing import Optional
from Maps import PATHS
from Databases import SOUNDS
from enc_utils import send_with_size

_BASE_GAME_W = (1960 - int(1960 * 0.12)) // 2
_BASE_GAME_H = 1080
PINK = (255, 128, 255)

class User:
    """
    Handles secure authentication setups, cryptographic password salting,
    and SHA-256 validation signatures.
    """
    def __init__(self, username, email):
        self.username = username
        self.email = email
        self.hashpass = ""
        self.salt = ""

    def __str__(self):
        return super().__str__()

    @staticmethod
    def hash_salt_passwd(passwd, salt=None):
        """
        Creates a randomized cryptographic salt and appends it to plain text
        passwords before signing.
        """
        if not salt:
            salt = User.salt_generator()
        both = salt + passwd
        return salt, User.hash_item(both)

    @staticmethod
    def hash_item(item):
        """
        Computes the definitive SHA-256 hex string value of a cleartext source string.
        """
        m = hashlib.sha256()
        m.update(item.encode())
        return m.hexdigest()

    @staticmethod
    def salt_generator(length=16):
        """
        Generates a secure cryptographic sequence string out of digits,
        alphabets, and punctuation characters.
        """
        alphabet = string.ascii_letters + string.digits + string.punctuation
        salt = ''.join(secrets.choice(alphabet) for _ in range(length))
        return salt


class GameUser:
    """
    Tracks local game states, covering round sequences, current bank balances,
    economy payout intervals, and batched networking events.
    """
    def __init__(self, side, name):
        self.username = name

        self.side = side
        self.monkey_map = {
            "monkey_0": "dart_monkey",
            "monkey_1": "tack_shooter",
            "monkey_2": "sniper_monkey",
            "monkey_3": "bomb_shooter"
        }
        self.lives = 200

        self.money = 650
        self.eco = 250
        self.eco_timer = 0
        self.ECO_INTERVAL = 6000
        self.bloons_queue = []
        self.last_send = 0
        self.bloons_list = pygame.sprite.Group()
        self.monkeys_list = pygame.sprite.Group()
        self.grid = CollisionGrid()

        self.send_queue = []

        pygame.mixer.init()

        info = pygame.display.Info()
        self.full_size = [info.current_w, info.current_h]
        self.size = [self.full_size[0], self.full_size[1]]
        self.game_rect = pygame.Rect(0, 0, 0, 0)
        self.path = PATHS[str(side)]

        self.selected_tower: Optional[str] = None
        from Monkey import Monkey
        self.active_monkey: Optional[Monkey] = None

        self.round_bloons = []
        self.round_finished = False
        self.last_round_send = 0

        self.calc_game_rect()

        self.pending_hits = []

    def queue_hit(self, bloon_id, damage, stun=0):
        """
        Stashes single weapon hit metrics into a localized array to avoid
        spamming socket buffers with individual packets.
        """
        self.pending_hits.append((str(bloon_id), int(damage), int(stun)))

    def flush_hits(self, sock, e_key):
        """
        Serializes and pushes all buffered frame hits across the active network
        stream as a consolidated game action message.
        """
        if not self.pending_hits:
            return
        entries = "|".join(f"{bid}~{dmg}~{stun}" for bid, dmg, stun in self.pending_hits)
        self.pending_hits.clear()
        send_with_size(sock,
                       f"GAME_ACTION~BATCH_HITS~{self.side}~{entries}".encode(),
                       e_key)

    def update_eco(self, dt):
        """
        Tracks round timers and periodically injects automatic revenue payouts
        based on current economic multipliers.
        """
        self.eco_timer += dt

        if self.eco_timer >= self.ECO_INTERVAL:
            self.money += round(self.eco)
            self.eco_timer = 0
            pygame.mixer.Sound(f"assets/sounds/{SOUNDS['cash']}").play()

    def check_send(self, curr_time):
        """
        Monitors pacing delays and handles sequential logic for spawning
        threat units out of active queues.
        """
        if len(self.bloons_queue) > 0:
            if curr_time - self.last_send >= self.bloons_queue[0][1]:
                self.bloons_list.add(self.bloons_queue.pop(0)[0])
                self.last_send = curr_time

        if len(self.round_bloons) > 0:
            if curr_time - self.last_round_send >= self.round_bloons[0][1]:
                self.bloons_list.add(self.round_bloons.pop(0)[0])
                self.last_round_send = curr_time
        else:
            if len(self.bloons_list) == 0 and curr_time > 10000:
                self.round_finished = True
            else:
                self.round_finished = False

    def update(self, dt, current_time, sock):
        """
        Master frame update cycle. Tracks local combat execution, updates spatial grids,
        evaluates entity positions, and checks live boundaries.
        """
        self.update_eco(dt)

        self.check_send(current_time)

        if len(self.send_queue) > 0:
            active = self.send_queue[0]
            if current_time - active["last_tick"] >= active["load_time"]:
                active["count"] -= 1
                active["last_tick"] = current_time
                if active["count"] <= 0:
                    self.send_queue.pop(0)
                    if len(self.send_queue) > 0:
                        self.send_queue[0]["last_tick"] = current_time

        from Game import e_key

        self.grid.clear()
        for b in self.bloons_list:
            if b.move_bloon(dt):
                if self.username == 'You':
                    self.lives -= b.dmg
                    send_with_size(sock,
                                   f"GAME_ACTION~LIVES_UPDATE~{self.side}~{self.lives}".encode(),
                                   e_key)
                b.kill()
            b.update_bloon_rect(self.game_rect)
            self.grid.insert_bloon(b)

        for m in self.monkeys_list:
            m.move_projectiles(dt, self.game_rect)
            m.update_monkey_rect(self.game_rect)

            if self.username == 'You' or getattr(m, 'ability_active', False):
                m.check_shoot(current_time, self.bloons_list)

            if self.username == 'You':
                children, money, hits = m.check_hits(self.grid)
                self.money += money
                if len(children) > 0:
                    for child in children:
                        self.bloons_list.add(child)

                for hit in hits:
                    self.queue_hit(hit['id'], hit['dmg'], hit.get('stun', 0))

    def try_purchase(self, cost):
        """
        Checks cash balances to validate shop purchases. Decrements funds on success.
        """
        if self.money >= cost:
            self.money -= cost
            return True
        return False

    def calc_game_rect(self):
        """
        Computes exact display layouts using coordinate spacing formulas.
        Reserves a top area for stats and divides the screen for 1v1 play fields.
        """
        w, h = self.size[0], self.size[1]
        shop_width = int(w * 0.12)
        game_width = (w - shop_width) // 2

        self.header_height = 45

        if self.side == 1:
            self.game_rect = pygame.Rect(shop_width, self.header_height, game_width, h - self.header_height)
        else:
            self.game_rect = pygame.Rect(shop_width + game_width, self.header_height, game_width,
                                         h - self.header_height)