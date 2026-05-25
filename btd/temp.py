# def move_bloon(self, dt):
#     width = pygame.display.get_surface().get_width()
#     pixels_per_second = self.speed * width
#
#     if self.target_node < len(self.path):
#         target = self.path[self.target_node]
#         direction = target - self.pos
#         distance_to_target = direction.length()
#
#         move_distance = pixels_per_second * (dt / 1000)
#
#         if distance_to_target > 0:
#             # 1. Movement
#             if distance_to_target > move_distance:
#                 self.pos += direction.normalize() * move_distance
#             else:
#                 self.pos = pygame.Vector2(target)
#                 self.target_node += 1
#
#         self.rect = self.image.get_rect(center=(round(self.pos.x), round(self.pos.y)))
#
#         self.image.set_colorkey(PINK)
#         self.distance += move_distance