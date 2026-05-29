import pygame
from Databases import MONKEY_DATA, BLOON_CONFIG
from btd.Bloon import BLOON_DATA

from Player import PINK

pygame.font.init()
UI_FONT = pygame.font.SysFont("Arial", 18, bold=True)
COST_FONT = pygame.font.SysFont("Arial", 16, bold=True) # Slightly smaller for costs

class InterfaceButton:
    def __init__(self, rect, name, color=(70, 70, 70), image=None):
        self.rect = rect
        self.name = name
        self.color = color
        self.image = image
        self.label = ""
        self.cost = 0  # New attribute for the price tag

        if not self.image:
            self.load_default_image()

    def load_default_image(self):
        try:
            if self.name in BLOON_CONFIG.keys():
                path = f"assets/bloons/{BLOON_DATA[BLOON_CONFIG[self.name]['color']]['image']}"
                # Auto-load cost for bloons
                self.cost = BLOON_CONFIG[self.name].get('cost', 0)
            elif 'monkey_' in self.name:
                from Game import MONKEY_MAP

                m_type = MONKEY_MAP[self.name]
                path = f"assets/monkeys/{m_type}/{MONKEY_DATA[m_type]['image']}"
                # Auto-load placement cost for monkeys
                self.cost = MONKEY_DATA[m_type].get('cost', 0)
            elif 'path_' in self.name:
                from Game import MONKEY_MAP

                # Upgrades handle cost dynamically in the UpgradeMenu class
                path = f"assets/monkeys/{MONKEY_MAP[self.name]}/{MONKEY_DATA[MONKEY_MAP[self.name]]['upgrades'][self.name]}"
            else:
                return

            self.image = pygame.image.load(path).convert()
            self.image.set_colorkey(PINK)
        except Exception:
            self.image = None

    def draw_button(self, surface, offset_y=0):
        draw_rect = self.rect.move(0, offset_y)
        pygame.draw.rect(surface, self.color, draw_rect, border_radius=5)

        # 1. Draw the Label (Top Left)
        if self.label:
            text_surf = UI_FONT.render(self.label, True, (255, 255, 255))
            surface.blit(text_surf, (draw_rect.x + 8, draw_rect.y + 5))

        # 2. Draw the Image
        if self.image:
            if 'path_' in self.name:
                size = int(self.rect.h * 0.65)
                img = pygame.transform.scale(self.image, (size, size))
                # Bottom-Left to stay clear of the Label and Cost
                surface.blit(img, (draw_rect.x + 5, draw_rect.bottom - size - 5))
            else:
                # Standard scaling for shop icons
                img = pygame.transform.scale(self.image, (self.rect.w - 10, self.rect.h - 10))
                surface.blit(img, (draw_rect.x + 5, draw_rect.y + 5))

        # 3. Draw the Cost (Bottom Right)
        if self.cost > 0:
            cost_surf = COST_FONT.render(f"${self.cost}", True, (255, 255, 0))  # Yellow for money
            # Position at bottom-right with a 5px margin
            cost_x = draw_rect.right - cost_surf.get_width() - 5
            cost_y = draw_rect.bottom - cost_surf.get_height() - 5
            surface.blit(cost_surf, (cost_x, cost_y))
        elif self.label == "MAXED":  # Special case for maxed upgrades
            pass

    def set_img(self, m_type):
        try:
            path = f"assets/monkeys/{m_type}/{MONKEY_DATA[m_type]['image']}"
            self.image = pygame.image.load(path).convert()
            self.image.set_colorkey(PINK)
        except Exception as e:
            print(f"Error loading image for {m_type}: {e}")


class GameInterface:
    def __init__(self):
        # Define Colors
        self.COLOR_PILLAR_HEADER = (100, 60, 40)  # Darker wood panel
        self.COLOR_SHOP = (185, 120, 85)
        self.COLOR_BORDER = (145, 90, 60)
        self.COLOR_PILLAR = (145, 90, 60)
        self.COLOR_BANNER_BG = (85, 50, 32)       # Warm dark wood to match the UI scheme
        self.COLOR_MONKEY_BTN = (100, 100, 100)
        self.COLOR_BLOON_BTN = (30, 150, 240)

        self.scroll_y = 0
        self.monkey_buttons = []
        self.bloon_buttons = []
        self.update_layout(True)

    def update_layout(self, fullscreen, event=None):
        if fullscreen:
            info = pygame.display.Info()
            w, h = info.current_w, info.current_h
        else:
            w, h = (event.w, event.h) if event else (1080, 700)

        self.screen_width, self.screen_height = w, h
        self.shop_width = int(w * 0.12)
        self.border_thickness, self.pillar_width = 8, 35
        self.shop_rect = pygame.Rect(0, 0, self.shop_width, h)
        self.col_w = self.shop_width // 2

        # --- Monkey Buttons ---
        self.monkey_area_h = int(h * 0.4)
        m_margin = 5
        m_btn_h = (self.monkey_area_h - (m_margin * 5)) // 4

        # Check if we need to instantiate buttons for the first time
        create_monkeys = len(self.monkey_buttons) == 0

        for i in range(4):
            rect = pygame.Rect(self.col_w + m_margin, m_margin + i * (m_btn_h + m_margin),
                               self.col_w - (m_margin * 2), m_btn_h)
            if create_monkeys:
                self.monkey_buttons.append(InterfaceButton(rect, f"monkey_{i}", self.COLOR_MONKEY_BTN))
            else:
                self.monkey_buttons[i].rect = rect  # Just update the position!

        # --- Bloon Buttons ---
        self.bloon_area_rect = pygame.Rect(0, self.monkey_area_h, self.shop_width, h - self.monkey_area_h)
        b_margin = 4
        b_btn_w = (self.shop_width - (b_margin * 3)) // 2
        b_btn_h = b_btn_w

        # Check if we need to instantiate buttons for the first time
        create_bloons = len(self.bloon_buttons) == 0

        for i in range(16):
            col, row = i % 2, i // 2
            x = b_margin + col * (b_btn_w + b_margin)
            y = self.monkey_area_h + b_margin + row * (b_btn_h + b_margin)
            rect = pygame.Rect(x, y, b_btn_w, b_btn_h)
            if create_bloons:
                self.bloon_buttons.append(InterfaceButton(rect, f"bloon_{i}", self.COLOR_BLOON_BTN))
            else:
                self.bloon_buttons[i].rect = rect  # Just update the position!

    def set_monkey_imgs(self, monkey_map):
        for btn in self.monkey_buttons:
            btn.set_img(monkey_map[btn.name])

    def handle_scroll(self, direction):
        rows = len(self.bloon_buttons) // 2
        content_height = rows * self.col_w
        max_scroll = max(0, content_height - self.bloon_area_rect.height + 50)
        self.scroll_y = max(0, min(self.scroll_y + (direction * 30), max_scroll))

    def get_clicked_item(self, pos):
        for btn in self.monkey_buttons:
            if btn.rect.collidepoint(pos): return btn.name
        if self.bloon_area_rect.collidepoint(pos):
            for btn in self.bloon_buttons:
                if btn.rect.move(0, -self.scroll_y).collidepoint(pos):
                    return btn.name
        return None

    def draw_gui(self, surface, timer_seconds, p1, p2):
        # 1. Draw the main sidebar base
        pygame.draw.rect(surface, self.COLOR_SHOP, self.shop_rect)
        for btn in self.monkey_buttons: btn.draw_button(surface)

        surface.set_clip(self.bloon_area_rect)
        for btn in self.bloon_buttons: btn.draw_button(surface, -self.scroll_y)
        surface.set_clip(None)

        # 2. Draw sidebar Borders
        pygame.draw.rect(surface, self.COLOR_BORDER, (self.shop_width - 2, 0, 4, self.screen_height))

        # --- CALCULATE GEOMETRY ---
        play_area_width = self.screen_width - self.shop_width
        center_x = self.shop_width + (play_area_width // 2)
        half_play_width = play_area_width // 2
        header_h = 45  # Consistent banner height

        # --- STEP 1: DRAW PLAYER TOP BANNERS FIRST (BACKGROUND LAYER) ---
        p1_banner_rect = pygame.Rect(self.shop_width, 0, half_play_width, header_h)
        pygame.draw.rect(surface, self.COLOR_BANNER_BG, p1_banner_rect)
        pygame.draw.line(surface, self.COLOR_BORDER, (self.shop_width, header_h),
                         (self.shop_width + half_play_width, header_h), 2)

        p2_banner_rect = pygame.Rect(self.shop_width + half_play_width, 0, half_play_width, header_h)
        pygame.draw.rect(surface, self.COLOR_BANNER_BG, p2_banner_rect)
        pygame.draw.line(surface, self.COLOR_BORDER, (self.shop_width + half_play_width, header_h),
                         (self.screen_width, header_h), 2)

        # --- STEP 2: DRAW THE PILLAR OVER THE BANNERS ---
        pillar_x = center_x - (self.pillar_width // 2)
        pygame.draw.rect(surface, self.COLOR_PILLAR, (pillar_x, 0, self.pillar_width, self.screen_height))

        # --- STEP 3: DRAW THE CENTRAL SCORES/TIMER BADGE OVER THE PILLAR ---
        badge_h = int(self.screen_height * 0.08)
        badge_w = int(self.pillar_width * 7)
        badge_x = center_x - (badge_w // 2)
        header_rect = pygame.Rect(badge_x, 0, badge_w, badge_h)

        pygame.draw.rect(surface, self.COLOR_PILLAR_HEADER, header_rect, border_radius=5)
        pygame.draw.rect(surface, self.COLOR_BORDER, header_rect, 3, border_radius=5)

        # --- STEP 4: RENDER AND BLIT PLAYER HUD LABELS (SOCIALLY DISTANCED) ---
        hud_font = pygame.font.SysFont("Arial", 16, bold=True)
        lives_font = pygame.font.SysFont("calibri", 16, bold=True)

        # Player 1 Info (Left Side)
        p1_name = p1.username
        p1_lives = f"<3 {p1.lives}"
        txt_p1_name = hud_font.render(p1_name, True, (230, 230, 230))
        txt_p1_lives = lives_font.render(p1_lives, True, (240, 70, 70))

        surface.blit(txt_p1_name, (self.shop_width + 15, 12))
        # Anchor lives safely to the left edge of the center wood badge
        surface.blit(txt_p1_lives, (header_rect.x - txt_p1_lives.get_width() - 15, 12))

        # Player 2 Info (Right Side)
        p2_name = p2.username
        p2_lives = f"<3 {p2.lives}"
        txt_p2_name = hud_font.render(p2_name, True, (230, 230, 230))
        txt_p2_lives = lives_font.render(p2_lives, True, (240, 70, 70))

        # Anchor name safely to the right edge of the center wood badge
        surface.blit(txt_p2_name, (header_rect.right + 15, 12))
        surface.blit(txt_p2_lives, (self.screen_width - txt_p2_lives.get_width() - 15, 12))

        # --- STEP 5: DRAW THE 3 BADGE COUNTERS (CASH, TIMER, ECO) ---
        mins, secs = divmod(int(timer_seconds), 60)
        timer_str = f"{mins:02d}:{secs:02d}"

        player = p1 if p1.username == "You" else p2

        cash_surf = UI_FONT.render(f"${player.money}", True, (255, 255, 0))
        time_surf = UI_FONT.render(timer_str, True, (255, 255, 255))
        income_surf = UI_FONT.render(f"+{player.eco}", True, (100, 255, 100))

        label_font = pygame.font.SysFont("Arial", 12, bold=True)
        eco_label = label_font.render("INCOME", True, (210, 210, 210))
        cash_label = label_font.render("CASH", True, (210, 210, 210))

        text_y = header_rect.centery - (time_surf.get_height() // 2)

        # Money (Left side of badge)
        surface.blit(cash_label, (header_rect.x + 8, header_rect.y + 4))
        surface.blit(cash_surf, (header_rect.x + 8, text_y + 5))

        # Timer (Center of badge)
        surface.blit(time_surf, (center_x - time_surf.get_width() // 2, text_y))

        # Income (Right side of badge)
        surface.blit(eco_label, (header_rect.right - eco_label.get_width() - 8, header_rect.y + 4))
        surface.blit(income_surf, (header_rect.right - income_surf.get_width() - 8, text_y + 5))

        # 3. Draw screen borders
        pygame.draw.rect(surface, self.COLOR_BORDER, (0, 0, self.screen_width, self.border_thickness))
        pygame.draw.rect(surface, self.COLOR_BORDER,
                         (0, self.screen_height - self.border_thickness, self.screen_width, self.border_thickness))


class UpgradeMenu:
    def __init__(self):
        self.COLOR_BG = (80, 50, 30)
        self.buttons = {}
        self.image_cache = {}
        self.update_layout(True)

    def get_upgrade_image(self, path):
        if path not in self.image_cache:
            try:
                img = pygame.image.load(path).convert()
                img.set_colorkey(PINK)
                self.image_cache[path] = img
            except:
                self.image_cache[path] = None
        return self.image_cache[path]

    def update_layout(self, fullscreen, event=None):
        if fullscreen:
            info = pygame.display.Info()
            w, h = info.current_w, info.current_h
        else:
            w, h = (event.w, event.h) if event else (1080, 700)

        self.screen_width, self.screen_height = w, h
        self.shop_width = int(w * 0.12)
        self.height = int(h * 0.22)
        self.rect = pygame.Rect(self.shop_width, h - self.height, w - self.shop_width, self.height)

        margin = 10
        p_size = self.height - (margin * 2)
        self.portrait_rect = pygame.Rect(self.rect.x + margin, self.rect.y + margin, p_size, p_size)
        self.sell_rect = pygame.Rect(self.portrait_rect.right + margin, self.rect.y + margin, 120,
                                     self.height - (margin * 2))

        rem_w = self.rect.right - (self.sell_rect.right + margin)
        path_w = (rem_w - (margin * 3)) // 2.05

        self.path1_rect = pygame.Rect(self.sell_rect.right + margin, self.rect.y + margin, path_w,
                                      self.height - (margin * 2))
        self.path2_rect = pygame.Rect(self.path1_rect.right + margin, self.rect.y + margin, path_w,
                                      self.height - (margin * 2))

        # Check if dictionary is empty before making new buttons
        if not self.buttons:
            self.buttons["sell"] = InterfaceButton(self.sell_rect, "sell", (200, 50, 50))
            self.buttons["path1"] = InterfaceButton(self.path1_rect, "path_1", (50, 150, 50))
            self.buttons["path2"] = InterfaceButton(self.path2_rect, "path_2", (50, 150, 50))
        else:
            # Just safely update their dimensions
            self.buttons["sell"].rect = self.sell_rect
            self.buttons["path1"].rect = self.path1_rect
            self.buttons["path2"].rect = self.path2_rect

    def draw_upgrade_gui(self, surface, monkey):
        pygame.draw.rect(surface, self.COLOR_BG, self.rect)
        pygame.draw.rect(surface, (120, 90, 60), self.portrait_rect)
        img = pygame.image.load(f"assets/monkeys/{monkey.type}/{MONKEY_DATA[monkey.type]['image']}").convert()
        img = pygame.transform.scale(img, (self.portrait_rect.w - 10, self.portrait_rect.h - 10))
        img.set_colorkey(PINK)
        surface.blit(img, (self.portrait_rect.x + 5, self.portrait_rect.y + 5))

        for btn in self.buttons.values():
            if 'path_' in btn.name:
                self.gui_upgrade(monkey, int(btn.name[-1:]), 0)
            btn.draw_button(surface)

    def get_click(self, pos):
        for name, btn in self.buttons.items():
            if btn.rect.collidepoint(pos): return name
        if not self.rect.collidepoint(pos): return "close"
        return None

    def gui_upgrade(self, monkey, path, next_u=1):
        target_btn = self.buttons[f"path{path}"]

        if (monkey.paths[path] == 3 and next_u == 1) or monkey.paths[path] == 4 or (
                monkey.paths[0] == abs(path - 3) and monkey.paths[path] == 2):
            target_btn.label = "MAXED"
            target_btn.image = None
            target_btn.cost = 0
            monkey.paths[path] = 4

        elif monkey.paths[path] < 4:
            data = MONKEY_DATA.get(monkey.type)['upgrades'][f'path_{path}'][monkey.paths[path]]
            target_btn.label = data['name']
            target_btn.cost = data.get('cost', 0)

            file_path = f"assets/monkeys/{monkey.type}/"
            full_path = file_path + f"{data['name']}.png"
            target_btn.image = self.get_upgrade_image(full_path)

            if next_u == 1:
                if monkey.paths[path] == 2 and monkey.paths[0] == '_':
                    monkey.paths[0] = path
                monkey.paths[path] += 1
                monkey.monkey_upgrade(data)

                path_img = 1 if monkey.paths[1] >= monkey.paths[2] else 2
                monkey.upgrade_image(path_img, monkey.paths[path_img])