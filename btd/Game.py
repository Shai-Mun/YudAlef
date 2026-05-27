import random
import pygame
from pygame import *
from Maps import Map
from Monkey import Monkey, upgrade_menu
from GUI import GameInterface, UpgradeMenu
from Databases import BLOON_CONFIG
from Bloon import Bloon
from Databases import MONKEY_DATA
from enc_utils import recv_by_size, send_with_size


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
    from Player import PINK
    return {
        "dart_monkey": load_sprite("assets/monkeys/dart_monkey/dart_base.png", PINK),
        # Add other monkeys here as you create them
    }


def handle_left_click(gui, upg_gui, pos, player, oppon):
    # Priority 1: Check Upgrade Menu (if it's open)

    if player.active_monkey:
        action = upg_gui.get_click(pos)
        if action == "sell":
            player.active_monkey.kill()
            player.active_monkey = None
            return

        elif action == "path1":
            # Get the cost of the NEXT upgrade
            current_p1_level = player.active_monkey.paths[1]
            upgrade_data = MONKEY_DATA[player.active_monkey.type]['upgrades']['path_1'][current_p1_level]

            if player.try_purchase(upgrade_data['cost']):
                upg_gui.gui_upgrade(player.active_monkey, 1)
            else:
                print("Can't afford upgrade!")

        elif action == "path2":
            # Get the cost of the NEXT upgrade
            current_p2_level = player.active_monkey.paths[2]
            upgrade_data = MONKEY_DATA[player.active_monkey.type]['upgrades']['path_2'][current_p2_level]

            if player.try_purchase(upgrade_data['cost']):
                upg_gui.gui_upgrade(player.active_monkey, 2)
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
            send_bloon(player, oppon, menu_action)
        return

    # Priority 3: Check for Monkey selection on the map
    clicked_m = upgrade_menu(player.monkeys_list, pos)
    if clicked_m:
        player.active_monkey = clicked_m
        player.selected_tower = None  # Don't hold a tower while upgrading
        return

    # Priority 4: Place a Tower
    if player.selected_tower and player.game_rect.x < pos[0] < player.game_rect.x + player.game_rect.width:
        cost = MONKEY_DATA[player.selected_tower]['base']['cost']
        if player.try_purchase(cost):

            rel_x = (pos[0] - player.game_rect.x) / player.game_rect.width
            rel_y = (pos[1] - player.game_rect.y) / player.game_rect.height

            # Place the tower logic here
            new_monkey = Monkey(player.selected_tower, (rel_x, rel_y))
            new_monkey.update_monkey_rect(player.game_rect)
            # new_monkey.update_range(player.game_rect)

            send_with_size(sock, f"GAME_ACTION~PLACE_MONKEY~{player.selected_tower}~{rel_x}~{rel_y}", key)

            player.monkeys_list.add(new_monkey)
            player.selected_tower = None


        else:
            print("Not enough money for this tower!")
    else:
        # Clicked empty map space
        player.active_monkey = None


def draw_transparent_circle(surface, color, player):
    radius = player.active_monkey.range
    center = (player.active_monkey.pos.x * player.game_rect.width + player.game_rect.x,
              player.active_monkey.pos.y * player.game_rect.height + player.game_rect.y)
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
    global key, sock

    data = BLOON_CONFIG.get(bloon_name)
    cost = data["cost"]
    if sender.try_purchase(cost):
        sender.eco += round(data["eco"])  # Increase eco

        # Add to the OPPONENT'S queue
        for _ in range(data["count"]):
            # Create bloon with the receiver's path type
            new_bloon = Bloon(data["color"], receiver.side, receiver.path)
            receiver.bloons_queue.append((new_bloon, data["load_time"]))
            send_with_size(sock, f"GAME_ACTION~SPAWN_BLOON~{data["color"]}~", key)


def update_all_layouts(game_map, gui, upg_gui, p, f_screen, e=None):
    size = game_map.update_size(p, f_screen, e)
    p.size = size
    p.calc_game_rect()
    gui.update_layout(f_screen, e)
    upg_gui.update_layout(f_screen, e)


# -------------------------------------------------------------------------------------------------------------------
key = ""
sock = ""


def launch_multiplayer_game(socket, enc_key, role, enemy_name):
    from Player import GameUser
    global key, sock

    key  = enc_key
    sock = socket

    if role == "P1":
        p1 = GameUser(1, 'You')
        p2 = GameUser(2, enemy_name)
        me = p1
        enemy = p2
    else:
        p2 = GameUser(2, 'You')
        p1 = GameUser(1, enemy_name)
        me = p2
        enemy = p1

    sock.setblocking(False)

    pygame.init()
    pygame.display.set_caption("BTD Battles")

    # Configuration
    game_map = Map("galili")
    refresh_rate = 60

    # --- 4. GLOBAL STATE SETUP ---
    fullscreen = True
    game_gui = GameInterface()
    game_gui.set_monkey_imgs(me.monkey_map)
    upgrade_gui = UpgradeMenu()

    # Now that the screen is set, load images
    ghost_cache = initialize_assets()
    clock = pygame.time.Clock()
    running = True


    # --- 5. MAIN LOOP ---
    while running:
        try:
            # Check if the server sent us an update about the enemy
            byte_data = recv_by_size(sock, key)
            if byte_data:
                msg = byte_data.decode()

                # Parse actions sent by the opponent
                if msg.startswith("PLACE_MONKEY~"):
                    _, m_type, rel_x, rel_y = msg.split("~")
                    # Force enemy instance to place a monkey on their side
                    enemy.monkeys_list.add(Monkey(m_type, (float(rel_x), float(rel_y))))

                elif msg.startswith("SPAWN_BLOON~"):
                    _, b_color = msg.split("~")
                    # Spawn a bloon on our side sent by the enemy
                    me.bloons_list.add(Bloon(b_color, me.side, me.path))

        except BlockingIOError:
            # This is normal! It means the server hasn't sent any data this frame.
            pass
        except Exception as e:
            print(f"Network error during match: {e}")

        current_time = pygame.time.get_ticks()

            # --- B. HANDLE LOCAL INPUTS & SEND TO SERVER ---
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            elif event.type == VIDEORESIZE:
                update_all_layouts(game_map, game_gui, upgrade_gui, me, fullscreen, event)

            elif event.type == KEYDOWN and event.key == pygame.K_f:
                fullscreen = not fullscreen
                update_all_layouts(game_map, game_gui, upgrade_gui, me, fullscreen)

            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # LEFT CLICK
                    handle_left_click(game_gui, upgrade_gui, event.pos, me, enemy)
                elif event.button == 2:  # SCROLL CLICK (Random Spawner)
                    colors = ["red", "blue", "green", "yellow", "pink", "black"]
                    c = random.choice(colors)
                    me.bloons_list.add(Bloon(c, 1, me.path))
                    enemy.bloons_list.add(Bloon(c, 2, enemy.path))
                    send_with_size(sock, f"GAME_ACTION~SPAWN_BLOON~{c}~", key)

            elif event.type == MOUSEWHEEL:
                game_gui.handle_scroll(-event.y)

        # B. GAME LOGIC UPDATES
        dt = clock.tick(refresh_rate)
        me.update(dt, current_time)
        enemy.update(dt, current_time)

        # C. RENDERING
        game_map.draw_map((me, enemy))
        game_gui.draw_gui(game_map.screen, pygame.time.get_ticks() / 1000, me)

        # Draw "Ghost" Tower
        if me.selected_tower:
            img = ghost_cache[me.selected_tower].copy()
            img.set_alpha(150)
            rect = img.get_rect(center=pygame.mouse.get_pos())
            game_map.screen.blit(img, rect)

        # Draw Upgrade Menu
        if me.active_monkey:
            draw_transparent_circle(game_map.screen, (255, 0, 0, 128), me)
            upgrade_gui.draw_upgrade_gui(game_map.screen, me.active_monkey)

        pygame.display.flip()

        # A. EVENT HANDLING


    pygame.quit()
