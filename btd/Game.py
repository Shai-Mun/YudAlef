import random
from pygame import VIDEORESIZE, KEYDOWN, QUIT, MOUSEBUTTONDOWN, MOUSEWHEEL
from Maps import *
from Maps import PATHS
from Monkey import *
from GUI import GameInterface, UpgradeMenu
from Databases import BLOON_CONFIG
from typing import Optional
from CollisionGrid import CollisionGrid
from Player import *

# --- 1. SETTINGS & INITIALIZATION ---
pygame.init()
pygame.display.set_caption("BTD Battles")

# --- 2. ASSET LOADING HELPERS ---
def load_sprite(path, colorkey=None):
    """Helper to load image, convert it, and set colorkey in one go."""
    try:
        image = pygame.image.load(path).convert()
        if colorkey:
            image.set_colorkey(colorkey)
        return image
    except pygame.error as e:
        print(f"Unable to load image at {path}: {e}")
        return pygame.Surface((32, 32))  # Placeholder


def initialize_assets():
    """Load all images into a cache once at startup."""
    return {
        "dart_monkey": load_sprite("assets/monkeys/dart_monkey/dart_base.png", PINK),
        # Add other monkeys here as you create them
    }


def handle_left_click(pos, player):
    # Priority 1: Check Upgrade Menu (if it's open)

    if player.active_monkey:
        action = upgrade_gui.get_click(pos)
        if action == "sell":
            player.active_monkey.kill()
            player.active_monkey = None
            return

        elif action == "path1":
            # Get the cost of the NEXT upgrade
            current_p1_level = player.active_monkey.paths[1]
            upgrade_data = MONKEY_DATA[player.active_monkey.type]['upgrades']['path_1'][current_p1_level]

            if player.try_purchase(upgrade_data['cost']):
                upgrade_gui.gui_upgrade(player.active_monkey, 1)
            else:
                print("Can't afford upgrade!")

        elif action == "path2":
            # Get the cost of the NEXT upgrade
            current_p2_level = player.active_monkey.paths[2]
            upgrade_data = MONKEY_DATA[player.active_monkey.type]['upgrades']['path_2'][current_p2_level]

            if player.try_purchase(upgrade_data['cost']):
                upgrade_gui.gui_upgrade(player.active_monkey, 2)
            else:
                print("Can't afford upgrade!")

        elif action == "close":
            player.active_monkey = None
            return

    # Priority 2: Check Main Sidebar
    menu_action = gui.get_clicked_item(pos)
    if menu_action:
        if 'monkey_' in menu_action:
            player.selected_tower = player.monkey_map.get(menu_action)
            player.active_monkey = None
        elif 'bloon_' in menu_action:
            send_bloon(player, P2, menu_action)
        return

    # Priority 3: Check for Monkey selection on the map
    clicked_m = upgrade_menu(player.monkeys_list, pos)
    if clicked_m:
        player.active_monkey = clicked_m
        player.selected_tower = None  # Don't hold a tower while upgrading
        return

    # Priority 4: Place a Tower
    if player.selected_tower and pos[0] > gui.shop_width:
        cost = MONKEY_DATA[player.selected_tower]['base']['cost']
        if player.try_purchase(cost):
            rel_x = pos[0] / game_map.screen.get_width()
            rel_y = pos[1] / game_map.screen.get_height()
            # Place the tower logic here
            new_monkey = Monkey(player.selected_tower, (rel_x, rel_y))
            player.monkeys_list.add(new_monkey)
            player.selected_tower = None
        else:
            print("Not enough money for this tower!")
    else:
        # Clicked empty map space
        player.active_monkey = None


def draw_transparent_circle(surface, color, center, radius):
    # 1. Create a temporary surface with an alpha channel
    # The size must be at least the diameter of the circle
    temp_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)

    # 2. Draw the circle onto the temp surface
    # Note: center is (radius, radius) because it's relative to the temp surface
    pygame.draw.circle(temp_surface, color, (radius, radius), radius)

    # 3. Blit the temp surface onto the main screen
    # Adjust position so the center matches the intended coordinates
    surface.blit(temp_surface, (center[0] - radius, center[1] - radius))


def send_bloon(sender, receiver, bloon_name):
    data = BLOON_CONFIG.get(bloon_name)
    if sender.money >= data["cost"]:
        sender.money -= data["cost"]
        sender.eco += data["eco"]  # Increase eco

        # Add to the OPPONENT'S queue
        for _ in range(data["count"]):
            # Create bloon with the receiver's path type
            new_bloon = Bloon(data["color"], receiver.side, receiver.path)
            receiver.bloons_queue.append((new_bloon, data["load_time"]))


def update_all_layouts(players, f_screen, e=None):
    for p in players:
        game_map.update_size(p.bloons_list, p.monkeys_list, f_screen, e)
        p.path = PATHS[str(p.side)]
        gui.update_layout(f_screen, e)
        upgrade_gui.update_layout(f_screen, e)


# -------------------------------------------------------------------------------------------------------------------
# Configuration
REFRESH_RATE = 60
PINK = (255, 128, 255)
P1 = Player(1)
P2 = Player(2)

# --- 4. GLOBAL STATE SETUP ---
fullscreen = True
game_map = Maps("galili")
gui = GameInterface()
gui.set_monkey_imgs(P1.monkey_map)
upgrade_gui = UpgradeMenu()

# Now that the screen is set, load images
ghost_cache = initialize_assets()

clock = pygame.time.Clock()
grid = CollisionGrid()

# selected_tower: Optional[str] = None
# active_monkey: Optional[Monkey] = None
finish = False


# --- 5. MAIN LOOP ---
while not finish:
    current_time = pygame.time.get_ticks()

    # A. EVENT HANDLING
    for event in pygame.event.get():
        if event.type == QUIT:
            finish = True

        elif event.type == VIDEORESIZE:
            update_all_layouts((P1, P2), fullscreen, event)

        elif event.type == KEYDOWN and event.key == pygame.K_f:
            fullscreen = not fullscreen
            update_all_layouts((P1, P2), fullscreen)

        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:  # LEFT CLICK
                handle_left_click(event.pos, P1)
            elif event.button == 2:  # SCROLL CLICK (Random Spawner)
                colors = ["red", "blue", "green", "yellow", "pink", "black"]
                c = random.choice(colors)
                P1.bloons_list.add(Bloon(c, 1, P1.path))
                P2.bloons_list.add(Bloon(c, 2, P2.path))

        elif event.type == MOUSEWHEEL:
            gui.handle_scroll(-event.y)

    # B. GAME LOGIC UPDATES
    dt = clock.tick(REFRESH_RATE)
    P1.update(dt, current_time)
    P2.update(dt, current_time)



    # C. RENDERING
    game_map.draw_map((P1, P2))
    gui.draw_gui(game_map.screen, pygame.time.get_ticks() / 1000, P1)

    # Draw "Ghost" Tower
    if P1.selected_tower:
        img = ghost_cache[P1.selected_tower].copy()
        img.set_alpha(150)
        rect = img.get_rect(center=pygame.mouse.get_pos())
        game_map.screen.blit(img, rect)

    # Draw Upgrade Menu
    if P1.active_monkey:
        draw_transparent_circle(game_map.screen, (255, 0, 0, 128), P1.active_monkey.pos, P1.active_monkey.range)
        upgrade_gui.draw_upgrade_gui(game_map.screen, P1.active_monkey)

    pygame.display.flip()

pygame.quit()
