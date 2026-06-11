import random
import pygame
from pygame import *
from Maps import Map
from Monkey import Monkey, upgrade_menu
from GUI import GameInterface, UpgradeMenu
from Databases import BLOON_CONFIG
from Bloon import Bloon
from Databases import MONKEY_DATA, SOUNDS
from enc_utils import recv_by_size, send_with_size


def load_sprite(path, colorkey=None):
    # Handles automated conversion and color transparency settings for newly loaded images
    try:
        image = pygame.image.load(path).convert()
        if colorkey:
            image.set_colorkey(colorkey)
        return image
    except pygame.error as e:
        print(f"Unable to load image at {path}: {e}")
        return pygame.Surface((32, 32))


def initialize_assets():
    # Allocates default graphics into central runtime cache to avoid recurring file reading operations
    from Player import PINK
    return {
        "dart_monkey": load_sprite("assets/monkeys/dart_monkey/dart_base.png", PINK),
        "tack_shooter": load_sprite("assets/monkeys/tack_shooter/tack_base.png", PINK),
        "sniper_monkey": load_sprite("assets/monkeys/sniper_monkey/sniper_base.png", PINK),
        "bomb_shooter": load_sprite("assets/monkeys/bomb_shooter/bomb_base.png", PINK),
    }


def handle_left_click(gui, upg_gui, pos, player, oppon):
    global e_key, curr_monkey_id, sock

    # Evaluates whether the click event intersects an existing tower placement
    clicked_m = upgrade_menu(player.monkeys_list, pos)
    if clicked_m:
        player.active_monkey = clicked_m
        player.selected_tower = None
        return

    action = None
    if player.active_monkey:
        action = upg_gui.get_click(pos, player.active_monkey)
        if action == "sell":
            player.active_monkey.kill()
            send_with_size(sock, f"GAME_ACTION~SELL_MONKEY~{player.side}~{player.active_monkey.id}".encode(), e_key)
            player.active_monkey = None
            pygame.mixer.Sound(f"assets/sounds/{SOUNDS['sell']}").play()
            return

        elif action == "path1":
            if upg_gui.buttons["path1"].label == "MAXED":
                return

            current_p1_level = min(player.active_monkey.paths[1], 3)
            upgrade_data = MONKEY_DATA[player.active_monkey.type]['upgrades']['path_1'][current_p1_level]

            if player.try_purchase(upgrade_data['cost']):
                upg_gui.gui_upgrade(player.active_monkey, 1)
                send_with_size(sock, f"GAME_ACTION~UPGRADE_MONKEY~{player.side}~{player.active_monkey.id}~1".encode(),
                               e_key)
            else:
                print("Can't afford upgrade!")

        elif action == "path2":
            if upg_gui.buttons["path2"].label == "MAXED":
                return

            current_p2_level = min(player.active_monkey.paths[2], 3)
            upgrade_data = MONKEY_DATA[player.active_monkey.type]['upgrades']['path_2'][current_p2_level]

            if player.try_purchase(upgrade_data['cost']):
                upg_gui.gui_upgrade(player.active_monkey, 2)
                send_with_size(sock, f"GAME_ACTION~UPGRADE_MONKEY~{player.side}~{player.active_monkey.id}~2".encode(),
                               e_key)
            else:
                print("Can't afford upgrade!")

        elif action == "ability":
            current_time = pygame.time.get_ticks()
            success = player.active_monkey.trigger_ability(current_time, player.bloons_list)
            if success:
                send_with_size(sock, f"GAME_ACTION~USE_ABILITY~{player.side}~{player.active_monkey.id}".encode(), e_key)
        elif action == "close":
            player.active_monkey = None
            return

    # Processes interactions occurring on the main side selection interface
    menu_action = gui.get_clicked_item(pos)
    if menu_action:
        if 'monkey_' in menu_action:
            player.selected_tower = player.monkey_map.get(menu_action)
            player.active_monkey = None
        elif 'bloon_' in menu_action:
            send_bloon(player, oppon, menu_action)
        return

    # Validates position limits and processes the deployment of a selected tower type
    if player.selected_tower:
        if player.game_rect.x < pos[0] < player.game_rect.x + player.game_rect.width:
            cost = MONKEY_DATA[player.selected_tower]['base']['cost']
            if player.try_purchase(cost):
                rel_x = (pos[0] - player.game_rect.x) / player.game_rect.width
                rel_y = (pos[1] - player.game_rect.y) / player.game_rect.height

                new_monkey = Monkey(player.selected_tower, (rel_x, rel_y), curr_monkey_id)
                new_monkey.update_monkey_rect(player.game_rect)
                pygame.mixer.Sound(f"assets/sounds/{SOUNDS['place']}").play()

                send_with_size(sock,
                               f"GAME_ACTION~PLACE_MONKEY~{player.selected_tower}~{rel_x}~{rel_y}~{curr_monkey_id}".encode(),
                               e_key)
                curr_monkey_id += 1

                player.monkeys_list.add(new_monkey)
                player.selected_tower = None
            else:
                print("Not enough money for this tower!")
        else:
            player.selected_tower = None
    elif action is None:
        player.active_monkey = None


def draw_transparent_rectangle(screen, c, enemy):
    # Renders temporary alpha surface overlays representing restricted placement fields
    temp_surface = pygame.Surface((enemy.game_rect.width, enemy.game_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(temp_surface, c, (0, 0, enemy.game_rect.width, enemy.game_rect.height))
    screen.blit(temp_surface, (enemy.game_rect.x, enemy.game_rect.y))


def draw_transparent_circle(screen, c, player):
    # Generates visual boundary overlay mapping the current selection's attacking range
    radius = player.active_monkey.range
    if player.active_monkey.type == "sniper_monkey":
        radius = 20
    center = (player.active_monkey.pos.x * player.game_rect.width + player.game_rect.x,
              player.active_monkey.pos.y * player.game_rect.height + player.game_rect.y)

    temp_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(temp_surface, c, (radius, radius), radius)
    screen.blit(temp_surface, (center[0] - radius, center[1] - radius))


def send_bloon(sender, receiver, bloon_name):
    global e_key, sock, current_round, curr_bloon_id

    # Enforces queue limits to regulate processing workloads
    if len(sender.send_queue) >= 5:
        return

    data = BLOON_CONFIG.get(bloon_name)
    cost = data["cost"]

    # Processes payment transactions, adjustments to eco parameters, and network event sync updates
    if current_round >= int(data['round']) and sender.try_purchase(cost):
        sender.eco += round(data["eco"])

        last_t = pygame.time.get_ticks() if len(sender.send_queue) == 0 else 0
        sender.send_queue.append({
            "color": data["color"],
            "count": data["count"],
            "load_time": data["load_time"],
            "last_tick": last_t
        })

        for _ in range(data["count"]):
            b_id = f"sent_{sender.side}_{curr_bloon_id}"
            new_bloon = Bloon(data["color"], receiver.side, receiver.path, b_id)
            receiver.bloons_queue.append((new_bloon, data["load_time"]))
            send_with_size(sock,
                           f"GAME_ACTION~SPAWN_BLOON~{receiver.side}~{data['color']}~{data['load_time']}~{b_id}".encode(),
                           e_key)
            curr_bloon_id += 1


def update_all_layouts(game_map, gui, upg_gui, players, f_screen, e=None):
    # Recalculates interface scale parameters and bounding rectangles upon window resize updates
    size = game_map.update_size(players[0], f_screen, e)
    players[1].size = size
    players[1].calc_game_rect()
    gui.update_layout(f_screen, e)
    upg_gui.update_layout(f_screen, e)


e_key = ""
sock = ""
curr_monkey_id = 1
curr_bloon_id = 1
current_round = 0
time_for_round = 45
last_round_start = -35 * 1000


def launch_multiplayer_game(socket, enc_key, role, enemy_name):
    from Player import GameUser
    global sock, e_key, current_round, time_for_round, last_round_start, curr_bloon_id

    e_key = enc_key
    sock = socket

    pygame.init()
    pygame.mixer.init()
    pygame.display.set_caption("BTD Battles")

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

    game_map = Map("galili", p1)
    refresh_rate = 60
    fullscreen = True
    game_gui = GameInterface()
    game_gui.set_monkey_imgs(me.monkey_map)
    upgrade_gui = UpgradeMenu()

    ghost_cache = initialize_assets()
    clock = pygame.time.Clock()
    running = True
    game_over = False
    winner_name = ""
    pending_remote_hits: dict[str, list] = {}

    while running:
        # Processes remote socket buffers and network game synchronization packets
        while True:
            try:
                byte_data = recv_by_size(sock, e_key)
                if not byte_data:
                    break

                msg = byte_data.decode()

                if msg.startswith("PLACE_MONKEY~"):
                    _, m_type, rel_x, rel_y, num = msg.split("~")
                    enemy.monkeys_list.add(Monkey(m_type, (float(rel_x), float(rel_y)), num))

                elif msg.startswith("SPAWN_BLOON~"):
                    _, side, b_color, loadtime, curr_id = msg.split("~")
                    player = p1 if int(side) == 1 else p2
                    player.bloons_queue.append((Bloon(b_color, player.side, player.path, curr_id), int(loadtime)))

                elif msg.startswith("UPGRADE_MONKEY~"):
                    _, side, m_id, path = msg.split("~")
                    player = p1 if int(side) == 1 else p2
                    for monkey in player.monkeys_list:
                        if int(monkey.id) == int(m_id):
                            upgrade_gui.gui_upgrade(monkey, int(path))

                elif msg.startswith("SELL_MONKEY~"):
                    _, side, m_id = msg.split("~")
                    player = p1 if int(side) == 1 else p2
                    for monkey in player.monkeys_list:
                        if int(monkey.id) == int(m_id):
                            monkey.kill()

                elif msg.startswith("HIT_BLOON~"):
                    parts = msg.split("~")
                    side = parts[1]
                    b_id = parts[2]
                    dmg = int(parts[3])
                    stun = int(parts[4]) if len(parts) > 4 else 0
                    player = p1 if int(side) == 1 else p2
                    bloon_map = {str(b.id): b for b in player.bloons_list}
                    bloon = bloon_map.get(b_id)
                    if bloon:
                        nc, _ = bloon.take_damage(dmg, stun)
                        for child in nc:
                            player.bloons_list.add(child)
                    else:
                        pending_remote_hits.setdefault(side, []).append((b_id, dmg, stun))

                elif msg.startswith("BATCH_HITS~"):
                    _, side, payload = msg.split("~", 2)
                    player = p1 if int(side) == 1 else p2
                    bloon_map = {str(b.id): b for b in player.bloons_list}

                    if side in pending_remote_hits:
                        still_pending = []
                        for pb_id, pdmg, pstun in pending_remote_hits[side]:
                            pb = bloon_map.get(pb_id)
                            if pb:
                                nc, _ = pb.take_damage(pdmg, pstun)
                                for child in nc:
                                    player.bloons_list.add(child)
                                    bloon_map[str(child.id)] = child
                            else:
                                still_pending.append((pb_id, pdmg, pstun))
                        if still_pending:
                            pending_remote_hits[side] = still_pending
                        else:
                            del pending_remote_hits[side]

                    for entry in payload.split("|"):
                        parts = entry.split("~")
                        b_id = parts[0]
                        dmg = int(parts[1])
                        stun = int(parts[2]) if len(parts) > 2 else 0
                        bloon = bloon_map.get(b_id)
                        if bloon:
                            nc, _ = bloon.take_damage(dmg, stun)
                            if nc:
                                for child in nc:
                                    player.bloons_list.add(child)
                                    bloon_map[str(child.id)] = child
                        else:
                            pending_remote_hits.setdefault(side, []).append((b_id, dmg, stun))

                elif msg.startswith("USE_ABILITY~"):
                    _, side, monkey_id = msg.split("~")
                    target_player = p1 if int(side) == 1 else p2
                    for monkey in target_player.monkeys_list:
                        if str(monkey.id) == str(monkey_id):
                            monkey.trigger_ability(pygame.time.get_ticks(), target_player.bloons_list)
                            break

                elif msg.startswith("LIVES_UPDATE~"):
                    _, side, new_lives = msg.split("~")
                    player = p1 if int(side) == 1 else p2
                    player.lives = int(new_lives)

                elif msg.startswith("GAME_OVER~"):
                    _, loser_side = msg.split("~")
                    if not game_over:
                        game_over = True
                        loser = p1 if int(loser_side) == 1 else p2
                        winner_name = (enemy if loser is me else me).username

            except BlockingIOError:
                break
            except Exception as e:
                print(f"Network error during match: {e}")
                break

        current_time = pygame.time.get_ticks()

        # Dispatches local user peripheral actions (clicks, system keystrokes)
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            elif event.type == VIDEORESIZE:
                update_all_layouts(game_map, game_gui, upgrade_gui, (p1, p2), fullscreen, event)

            elif event.type == KEYDOWN and event.key == pygame.K_f:
                fullscreen = not fullscreen
                update_all_layouts(game_map, game_gui, upgrade_gui, (p1, p2), fullscreen)

            elif event.type == MOUSEBUTTONDOWN and not game_over:
                if event.button == 1:
                    handle_left_click(game_gui, upgrade_gui, event.pos, me, enemy)
                elif event.button == 2:
                    colors = ["ceramic", "moab", "bfb", "zomg"]
                    c = random.choice(colors)
                    b_id = f"sent_{me.side}_{curr_bloon_id}"
                    enemy.bloons_list.add(Bloon(c, 2, enemy.path, b_id))
                    send_with_size(sock, f"GAME_ACTION~SPAWN_BLOON~{enemy.side}~{c}~0~{b_id}".encode(), e_key)
                    curr_bloon_id += 1

            elif event.type == MOUSEWHEEL and not game_over:
                game_gui.handle_scroll(-event.y)

        # Calculates game round progressions and handles spawning deterministic wave patterns
        if not game_over and (current_time - last_round_start >= time_for_round * 1000 or (
                me.round_finished and enemy.round_finished)):
            current_round += 1
            last_round_start = current_time

            from Databases import NATURAL_ROUNDS
            batches = NATURAL_ROUNDS[current_round]
            round_bloon_counter = 0

            for batch in batches:
                for _ in range(int(batch['count'])):
                    b_id = f"nat_{current_round}_{round_bloon_counter}"

                    new_bloon = Bloon(batch["color"], me.side, me.path, b_id)
                    me.round_bloons.append((new_bloon, batch["spacing"]))
                    me.round_finished = False

                    new_bloon = Bloon(batch["color"], enemy.side, enemy.path, b_id)
                    enemy.round_bloons.append((new_bloon, batch["spacing"]))
                    enemy.round_finished = False

                    round_bloon_counter += 1

            if current_round % 2 == 0 and current_round > 0:
                game_gui.bloon_buttons[current_round - 2].set_img('bloon_' + str(current_round - 2))
                game_gui.bloon_buttons[current_round - 1].set_img('bloon_' + str(current_round - 1))

        dt = clock.tick(refresh_rate)

        # Updates game state variables and processes local player hit validations
        if not game_over:
            me.update(dt, current_time, sock)
            me.flush_hits(sock, e_key)

            enemy.update(dt, current_time, sock)

            if me.lives <= 0:
                game_over = True
                winner_name = enemy.username
                send_with_size(sock, f"GAME_ACTION~GAME_OVER~{me.side}".encode(), e_key)
            elif enemy.lives <= 0:
                game_over = True
                winner_name = me.username

        # Dispatches draw functions onto frame buffers
        game_map.draw_map((p1, p2))
        game_gui.draw_gui(game_map.screen, current_time / 1000, p1, p2, current_round)

        if not game_over:
            if me.selected_tower:
                img = ghost_cache[me.selected_tower].copy()
                img.set_alpha(150)
                rect = img.get_rect(center=pygame.mouse.get_pos())
                game_map.screen.blit(img, rect)
                draw_transparent_rectangle(game_map.screen, (255, 0, 0, 128), enemy)

            if me.active_monkey:
                draw_transparent_circle(game_map.screen, (255, 0, 0, 128), me)
                upgrade_gui.draw_upgrade_gui(game_map.screen, me.active_monkey)

        if game_over:
            overlay = pygame.Surface(game_map.screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            game_map.screen.blit(overlay, (0, 0))

            win_font = pygame.font.SysFont("Arial", 80, bold=True)
            win_text = win_font.render(f"{winner_name} won!", True, (255, 215, 0))
            text_rect = win_text.get_rect(center=(game_map.screen.get_width() // 2, game_map.screen.get_height() // 2))
            game_map.screen.blit(win_text, text_rect)

        pygame.display.flip()

    pygame.quit()