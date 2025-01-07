import pygame
import random
import math
from utils import check_collision, is_player_detected

class Enemy:
    def __init__(self, x, y, color):
        self.size = 20
        self.pos = [x, y]
        self.speed = 2
        self.fov = 60  # Field of vision in degrees
        self.fov_length = 150
        self.direction = random.choice(['left', 'right', 'up', 'down'])
        self.color = color

    def draw(self, screen, camera_offset):
        rect = pygame.Rect(self.pos[0] - camera_offset[0], self.pos[1] - camera_offset[1], self.size, self.size)
        pygame.draw.rect(screen, self.color, rect)
        self.draw_fov(screen, camera_offset)

    def draw_fov(self, screen, camera_offset):
        start_angle = math.radians(-self.fov / 2)
        end_angle = math.radians(self.fov / 2)
        for angle in range(int(start_angle * 180 / math.pi), int(end_angle * 180 / math.pi)):
            x = self.pos[0] + self.size // 2 + self.fov_length * math.cos(math.radians(angle)) - camera_offset[0]
            y = self.pos[1] + self.size // 2 + self.fov_length * math.sin(math.radians(angle)) - camera_offset[1]
            pygame.draw.line(screen, self.color, (self.pos[0] + self.size // 2 - camera_offset[0], self.pos[1] + self.size // 2 - camera_offset[1]), (x, y), 1)

    def move(self, player, obstacles, width, height):
        if random.random() < 0.01:
            self.direction = random.choice(['left', 'right', 'up', 'down'])

        new_pos = self.pos[:]
        if self.direction == 'left':
            new_pos[0] -= self.speed
        elif self.direction == 'right':
            new_pos[0] += self.speed
        elif self.direction == 'up':
            new_pos[1] -= self.speed
        elif self.direction == 'down':
            new_pos[1] += self.speed

        if not check_collision(new_pos, self.size, obstacles, width, height):
            self.pos = new_pos

        if is_player_detected(player, self):
            if player.pos[0] < self.pos[0]:
                self.pos[0] -= self.speed
            elif player.pos[0] > self.pos[0]:
                self.pos[0] += self.speed
            if player.pos[1] < self.pos[1]:
                self.pos[1] -= self.speed
            elif player.pos[1] > self.pos[1]:
                self.pos[1] += self.speed