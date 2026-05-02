import pygame
from Databases import MONKEY_DATA, BLOON_CONFIG
from Bloon import BLOON_DATA

PINK = (255, 128, 255)

# Initialize Font logic
pygame.font.init()
# Bold font for better visibility on the wood/green backgrounds
UI_FONT = pygame.font.SysFont("Arial", 18, bold=True)


class InterfaceButton:
    def __init__(self, rect, name, color=(70, 70, 70), image=None):
        self.rect = rect
        self.name = name
        self.color = color
        self.image = image
        self.label = ""  # New attribute to hold the upgrade name

        if not self.image:
            self.load_default_image()

    def load_default_image(self):
        # Local import to prevent circular import issues
        from Game import MONKEY_MAP
        try:
            if self.name in BLOON_CONFIG.keys():
                path = f"assets/bloons/{BLOON_DATA[BLOON_CONFIG[self.name]['color']]['image']}"
            elif 'monkey_' in self.name:
                path = f"assets/monkeys/{MONKEY_MAP[self.name]}/{MONKEY_DATA[MONKEY_MAP[self.name]]['image']}"
            elif 'path_' in self.name:
                path = f"assets/monkeys/{MONKEY_MAP[self.name]}/{MONKEY_DATA[MONKEY_MAP[self.name]]['upgrades'][self.name]}"
            else:
                # path = f"assets/monkeys/dart_monkey/{MONKEY_DATA['dart_monkey']['image']}"
                return

            self.image = pygame.image.load(path).convert()
            self.image.set_colorkey(PINK)
        except Exception:
            self.image = None

    def draw(self, surface, offset_y=0):
        """Standardized draw method with the new Top-Text/Bottom-Left Image layout"""
        draw_rect = self.rect.move(0, offset_y)
        pygame.draw.rect(surface, self.color, draw_rect, border_radius=5)

        # 1. Draw the Label (Upgrade Name) at the Top
        if self.label:
            text_surf = UI_FONT.render(self.label, True, (255, 255, 255))
            # Position at top-left with a small margin
            surface.blit(text_surf, (draw_rect.x + 8, draw_rect.y + 5))

        # 2. Draw the Image
        if self.image:
            if 'path_' in self.name:
                # Scale image to 65% of the button height
                size = int(self.rect.h * 0.65)
                img = pygame.transform.scale(self.image, (size, size))
                # Position: Bottom Left corner
                img_x = draw_rect.x + 5
                img_y = draw_rect.bottom - size - 5
                surface.blit(img, (img_x, img_y))
            else:
                # Standard scaling for shop/bloon buttons
                img = pygame.transform.scale(self.image, (self.rect.w - 10, self.rect.h - 10))
                surface.blit(img, (draw_rect.x + 5, draw_rect.y + 5))

    def set_img(self, m_type):
        try:
            path = f"assets/monkeys/{m_type}/{MONKEY_DATA[m_type]['image']}"
            self.image = pygame.image.load(path).convert()
            self.image.set_colorkey(PINK)
        except Exception as e:
            print(f"Error loading image for {m_type}: {e}")


class GameInterface:
    def __init__(self):
        self.COLOR_SHOP = (185, 120, 85)
        self.COLOR_BORDER = (145, 90, 60)
        self.COLOR_PILLAR = (145, 90, 60)
        self.COLOR_MONKEY_BTN = (100, 100, 100)
        self.COLOR_BLOON_BTN = (30, 150, 240)

        self.scroll_y = 0
        self.monkey_buttons = []
        self.bloon_buttons = []
        self.update_layout(True)

    def update_layout(self, fullscreen, event=None):
        if fullscreen:
            w, h = 1960, 1080
        else:
            w, h = (event.w, event.h) if event else (1080, 700)

        self.screen_width, self.screen_height = w, h
        self.shop_width = int(w * 0.12)
        self.border_thickness, self.pillar_width = 8, 15
        self.shop_rect = pygame.Rect(0, 0, self.shop_width, h)
        self.col_w = self.shop_width // 2

        self.monkey_area_h = int(h * 0.4)
        self.monkey_buttons = []
        m_margin = 5
        m_btn_h = (self.monkey_area_h - (m_margin * 5)) // 4

        for i in range(4):
            rect = pygame.Rect(self.col_w + m_margin, m_margin + i * (m_btn_h + m_margin),
                               self.col_w - (m_margin * 2), m_btn_h)
            self.monkey_buttons.append(InterfaceButton(rect, f"monkey_{i}", self.COLOR_MONKEY_BTN))

        self.bloon_area_rect = pygame.Rect(0, self.monkey_area_h, self.shop_width, h - self.monkey_area_h)
        self.bloon_buttons = []
        b_margin = 4
        b_btn_w = (self.shop_width - (b_margin * 3)) // 2
        b_btn_h = b_btn_w

        for i in range(16):
            col, row = i % 2, i // 2
            x = b_margin + col * (b_btn_w + b_margin)
            y = self.monkey_area_h + b_margin + row * (b_btn_h + b_margin)
            self.bloon_buttons.append(
                InterfaceButton(pygame.Rect(x, y, b_btn_w, b_btn_h), f"bloon_{i}", self.COLOR_BLOON_BTN))

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

    def draw(self, surface):
        pygame.draw.rect(surface, self.COLOR_SHOP, self.shop_rect)
        for btn in self.monkey_buttons: btn.draw(surface)

        surface.set_clip(self.bloon_area_rect)
        for btn in self.bloon_buttons: btn.draw(surface, -self.scroll_y)
        surface.set_clip(None)

        game_area_w = self.screen_width - self.shop_width
        pillar_x = self.shop_width + (game_area_w // 2) - (self.pillar_width // 2)
        pygame.draw.rect(surface, self.COLOR_PILLAR, (pillar_x, 0, self.pillar_width, self.screen_height))
        pygame.draw.rect(surface, self.COLOR_BORDER, (self.shop_width - 2, 0, 4, self.screen_height))
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
            w, h = 1960, 1080
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
        path_w = (rem_w - (margin * 3)) // 2

        self.path1_rect = pygame.Rect(self.sell_rect.right + margin, self.rect.y + margin, path_w,
                                      self.height - (margin * 2))
        self.path2_rect = pygame.Rect(self.path1_rect.right + margin, self.rect.y + margin, path_w,
                                      self.height - (margin * 2))

        self.buttons["sell"] = InterfaceButton(self.sell_rect, "sell", (200, 50, 50))
        self.buttons["path1"] = InterfaceButton(self.path1_rect, "path_1", (50, 150, 50))
        self.buttons["path2"] = InterfaceButton(self.path2_rect, "path_2", (50, 150, 50))

    def draw(self, surface, monkey):
        pygame.draw.rect(surface, self.COLOR_BG, self.rect)
        pygame.draw.rect(surface, (120, 90, 60), self.portrait_rect)
        if monkey.original_image:
            img = pygame.transform.scale(monkey.original_image, (self.portrait_rect.w - 10, self.portrait_rect.h - 10))
            surface.blit(img, (self.portrait_rect.x + 5, self.portrait_rect.y + 5))

        for btn in self.buttons.values():
            if 'path_' in btn.name:
                # Update the button visual content before drawing
                self.upgrade(monkey, int(btn.name[-1:]), 0)
            btn.draw(surface)

    def get_click(self, pos):
        for name, btn in self.buttons.items():
            if btn.rect.collidepoint(pos): return name
        if not self.rect.collidepoint(pos): return "close"
        return None

    def upgrade(self, monkey, path, next_u=1):
        target_btn = self.buttons[f"path{path}"]

        if (monkey.paths[path] == 3 and next_u == 1) or monkey.paths[path] == 4 or (monkey.paths[0] == abs(path - 3) and monkey.paths[path] == 2):
            target_btn.label = "MAXED"
            target_btn.image = None
            monkey.paths[path] = 4

        elif monkey.paths[path] < 3:
            data = MONKEY_DATA.get(monkey.type)['upgrades'][f'path_{path}'][monkey.paths[path] + next_u]

            # 1. Update the label text
            target_btn.label = data['name']
            # 2. Update the image
            file_path = f"assets/monkeys/{monkey.type}/"
            full_path = file_path + f"{data['name']}.png"
            target_btn.image = self.get_upgrade_image(full_path)

            if next_u == 1:
                if monkey.paths[path] == 2 and monkey.paths[0] == '_':
                    monkey.paths[0] = path
                monkey.paths[path] += next_u
                monkey.upgrade(data)

#
