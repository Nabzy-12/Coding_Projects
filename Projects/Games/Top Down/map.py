import pygame
import random

def generate_obstacles(width, height, num_obstacles):
    obstacles = []
    for _ in range(num_obstacles):
        x = random.randint(0, width - 50)
        y = random.randint(-height, 0)
        w = random.randint(50, 150)
        h = random.randint(50, 150)
        obstacles.append(pygame.Rect(x, y, w, h))
    return obstacles

def draw_obstacles(screen, obstacles, color, camera_offset):
    for obstacle in obstacles:
        rect = obstacle.move(-camera_offset[0], -camera_offset[1])
        pygame.draw.rect(screen, color, rect)