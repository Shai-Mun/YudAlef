import random
from pygame import VIDEORESIZE, KEYDOWN, QUIT, MOUSEBUTTONDOWN, MOUSEWHEEL
from Maps import *
from Monkey import *
from GUI import GameInterface, UpgradeMenu
from Databases import BLOON_CONFIG
from typing import Optional
from CollisionGrid import CollisionGrid
from Player import *

# --- 1. SETTINGS & INITIALIZATION ---
pygame.init()
pygame.display.set_caption("BTD Battles")

# Configuration
REFRESH_RATE = 60
PINK = (255, 128, 255)
P1 = Player(1)
MONKEY_MAP = P1.monkey_map
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


# --- 3. LOGIC HANDLERS ---
def update_all_layouts(f_screen, e=None):
    game_map.update_size(P1.bloons_list, P1.monkeys_list, f_screen, e)
    gui.update_layout(f_screen, e)
    upgrade_gui.update_layout(f_screen, e)


def handle_left_click(pos, player):
    global active_monkey, selected_tower

    # Priority 1: Check Upgrade Menu (if it's open)
    if active_monkey:
        action = upgrade_gui.get_click(pos)
        if action == "sell":
            active_monkey.kill()
            active_monkey = None
            return
        elif action == "path1":
            upgrade_gui.upgrade(active_monkey, 1)
        elif action == "path2":
            upgrade_gui.upgrade(active_monkey, 2)
        elif action == "close":
            active_monkey = None
            return

    # Priority 2: Check Main Sidebar
    menu_action = gui.get_clicked_item(pos)
    if menu_action:
        if 'monkey_' in menu_action:
            selected_tower = P1.monkey_map.get(menu_action)
        elif 'bloon_' in menu_action:
            trigger_bloon_send(menu_action, PATHS["INVERSE_PATH"])
        return

    # Priority 3: Check for Monkey selection on the map
    clicked_m = upgrade_menu(player.monkeys_list, pos)
    if clicked_m:
        active_monkey = clicked_m
        selected_tower = None  # Don't hold a tower while upgrading
        return

    # Priority 4: Place a Tower
    if selected_tower and pos[0] > gui.shop_width:
        # Convert absolute pixels to relative coordinates (0.0 to 1.0)
        rel_x = pos[0] / game_map.screen.get_width()
        rel_y = pos[1] / game_map.screen.get_height()

        new_monkey = Monkey(selected_tower, (rel_x, rel_y))
        player.monkeys_list.add(new_monkey)
        selected_tower = None
    else:
        # Clicked empty map space
        active_monkey = None


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

selected_tower: Optional[str] = None
active_monkey: Optional[Monkey] = None
finish = False

def trigger_bloon_send(name, path_type):
    # Get the settings for this specific button from your database
    data = BLOON_CONFIG.get(name)

    if data:
        # Loop based on the 'count' defined in your config (e.g., 3 red bloons)
        for _ in range(data["count"]):
            # Create the bloon.
            new_bloon = Bloon(data["color"], 2, path_type)
            P1.bloons_queue.append((new_bloon, data["load_time"]))

def check_send(curr_time, player):
    if len(player.bloons_queue) > 0:
        if curr_time - player.last_send >= player.bloons_queue[0][1]:
            player.bloons_list.add(player.bloons_queue.pop(0)[0])
            player.last_send = curr_time

# --- 5. MAIN LOOP ---
while not finish:
    current_time = pygame.time.get_ticks()

    # A. EVENT HANDLING
    for event in pygame.event.get():
        if event.type == QUIT:
            finish = True

        elif event.type == VIDEORESIZE:
            update_all_layouts(fullscreen, event)

        elif event.type == KEYDOWN and event.key == pygame.K_f:
            fullscreen = not fullscreen
            update_all_layouts(fullscreen)

        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:  # LEFT CLICK
                handle_left_click(event.pos, P1)
            elif event.button == 2:  # SCROLL CLICK (Random Spawner)
                colors = ["red", "blue", "green", "yellow", "pink", "black"]
                c = random.choice(colors)
                P1.bloons_list.add(Bloon(c, 1, PATHS["PATH"]))
                P1.bloons_list.add(Bloon(c, 2, PATHS["INVERSE_PATH"]))

        elif event.type == MOUSEWHEEL:
            gui.handle_scroll(-event.y)

    # B. GAME LOGIC UPDATES
    dt = clock.tick(REFRESH_RATE)
    check_send(current_time, P1)
    grid.clear()
    for b in P1.bloons_list:
        b.move(dt)
        grid.insert_bloon(b)
    P1.check_hit(current_time, dt)



    # C. RENDERING
    game_map.draw(P1.bloons_list, P1.monkeys_list)
    gui.draw(game_map.screen, pygame.time.get_ticks() / 1000, P1.money, P1.income)

    # Draw "Ghost" Tower
    if selected_tower:
        img = ghost_cache[selected_tower].copy()
        img.set_alpha(150)
        rect = img.get_rect(center=pygame.mouse.get_pos())
        game_map.screen.blit(img, rect)

    # Draw Upgrade Menu
    if active_monkey:
        draw_transparent_circle(game_map.screen, (255, 0, 0, 128), active_monkey.pos, active_monkey.range)
        upgrade_gui.draw(game_map.screen, active_monkey)

    pygame.display.flip()

pygame.quit()