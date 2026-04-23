import pygame


class GameInterface:
    def __init__(self, screen_width, screen_height):
        self.update_layout(screen_width, screen_height)

        # Colors
        self.COLOR_SHOP = (40, 40, 40)
        self.COLOR_BORDER = (20, 20, 20)
        self.COLOR_PILLAR = (60, 60, 60)

    def update_layout(self, w, h):
        self.screen_width = w
        self.screen_height = h

        # Define Proportions
        self.shop_width = int(w * 0.15)  # 15% of screen for shop
        self.border_thickness = 10
        self.pillar_width = 20

        # Shop Rect
        self.shop_rect = pygame.Rect(0, 0, self.shop_width, h)

        # Playable Area (where the map goes)
        self.play_area_rect = pygame.Rect(self.shop_width, 0, w - self.shop_width, h)

        # Central Pillar Rect
        pillar_x = self.shop_width + (self.play_area_rect.width // 2) - (self.pillar_width // 2)
        self.pillar_rect = pygame.Rect(pillar_x, 0, self.pillar_width, h)

    def draw(self, surface):
        # 1. Draw Shop Background
        pygame.draw.rect(surface, self.COLOR_SHOP, self.shop_rect)

        # 2. Draw Central Pillar
        pygame.draw.rect(surface, self.COLOR_PILLAR, self.pillar_rect)

        # 3. Draw Outer Borders
        # Top
        pygame.draw.rect(surface, self.COLOR_BORDER, (0, 0, self.screen_width, self.border_thickness))
        # Bottom
        pygame.draw.rect(surface, self.COLOR_BORDER,
                         (0, self.screen_height - self.border_thickness, self.screen_width, self.border_thickness))
        # Right
        pygame.draw.rect(surface, self.COLOR_BORDER,
                         (self.screen_width - self.border_thickness, 0, self.border_thickness, self.screen_height))
        # Left (Shop edge)
        pygame.draw.rect(surface, self.COLOR_BORDER, (0, 0, self.border_thickness, self.screen_height))

        # 4. Draw Line separating Shop from Map
        pygame.draw.line(surface, (100, 100, 100), (self.shop_width, 0), (self.shop_width, self.screen_height), 2)