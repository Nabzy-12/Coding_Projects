import pygame
import random
from map import generate_obstacles, draw_obstacles
from player import Player
from enemy import Enemy
from utils import is_player_detected, menu_screen, display_score

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Top-Down Stealth Game")

# Colors
BACKGROUND_COLOR = (30, 30, 30)
PLAYER_COLOR = (0, 255, 0)
ENEMY_COLOR = (255, 0, 0)
OBSTACLE_COLOR = (50, 50, 50)

# Game loop
running = True
clock = pygame.time.Clock()

player = Player(WIDTH // 2, HEIGHT // 2, PLAYER_COLOR)
enemies = [Enemy(random.randint(0, WIDTH), random.randint(0, HEIGHT // 2), ENEMY_COLOR) for _ in range(3)]
obstacles = generate_obstacles(WIDTH, HEIGHT, 20)

in_menu = True
score = 0

while running:
    if in_menu:
        start_button, quit_button = menu_screen(screen, WIDTH, HEIGHT)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    in_menu = False
                elif quit_button.collidepoint(event.pos):
                    running = False
    else:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        player.move(keys, obstacles, WIDTH, HEIGHT)

        for enemy in enemies:
            enemy.move(player, obstacles, WIDTH, HEIGHT)

        # Generate new obstacles as the player advances
        if player.pos[1] < HEIGHT // 2:
            player.pos[1] += HEIGHT // 2
            obstacles.extend(generate_obstacles(WIDTH, HEIGHT, max(5, 20 - score // 100)))
            enemies.append(Enemy(random.randint(0, WIDTH), random.randint(0, HEIGHT // 2), ENEMY_COLOR))

        # Remove obstacles that are no longer visible
        obstacles = [obstacle for obstacle in obstacles if obstacle.y + obstacle.height > 0]

        # Camera offset
        camera_offset = [player.pos[0] - WIDTH // 2, player.pos[1] - HEIGHT // 2]

        screen.fill(BACKGROUND_COLOR)

        # Draw player
        player.draw(screen, camera_offset)

        # Draw enemies
        for enemy in enemies:
            enemy.draw(screen, camera_offset)

        # Draw obstacles
        draw_obstacles(screen, obstacles, OBSTACLE_COLOR, camera_offset)

        if any(is_player_detected(player, enemy) for enemy in enemies):
            running = False
            display_score(screen, score)

        score += 1

        pygame.display.flip()
        clock.tick(30)

pygame.quit()