import pygame
import math


class Monkey(pygame.sprite.Sprite):
    def __init__(self, type):
        super().__init__()


    def base_stats(self, type: str):
        match type:
            case "dart":
