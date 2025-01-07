import pygame
from utils import check_collision

class Player:
    def __init__(self, x, y, color):
        self.size = 20
        self.pos = [x, y]
        self.speed = 5
        self.color = color

    def draw(self, screen, camera_offset):
        rect = pygame.Rect(self.pos[0] - camera_offset[0], self.pos[1] - camera_offset[1], self.size, self.size)
        pygame.draw.rect(screen, self.color, rect)

    def move(self, keys, obstacles, width, height):
        new_pos = self.pos[:]
        if keys[pygame.K_LEFT]:
            new_pos[0] -= self.speed
        if keys[pygame.K_RIGHT]:
            new_pos[0] += self.speed
        if keys[pygame.K_UP]:
            new_pos[1] -= self.speed
        if keys[pygame.K_DOWN]:
            new_pos[1] += self.speed

        if not check_collision(new_pos, self.size, obstacles, width, height):
            self.pos = new_pos