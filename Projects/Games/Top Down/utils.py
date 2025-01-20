import pygame
import math

def check_collision(new_pos, size, obstacles, width, height):
    rect = pygame.Rect(new_pos[0], new_pos[1], size, size)
    if rect.left < 0 or rect.right > width or rect.top < 0 or rect.bottom > height:
        return True
    for obstacle in obstacles:
        if rect.colliderect(obstacle):
            return True
    return False

def is_player_detected(player, enemy):
    dx = player.pos[0] - enemy.pos[0]
    dy = player.pos[1] - enemy.pos[1]
    distance = math.hypot(dx, dy)
    if distance < enemy.fov_length:
        angle = math.degrees(math.atan2(dy, dx))
        if -enemy.fov / 2 < angle < enemy.fov / 2:
            return True
    return False

def menu_screen(screen, width, height):
    screen.fill((30, 30, 30))
    font = pygame.font.Font(None, 74)
    text = font.render("Top-Down Stealth Game", True, (255, 255, 255))
    screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - text.get_height() // 2 - 100))

    start_button = pygame.Rect(width // 2 - 100, height // 2, 200, 50)
    quit_button = pygame.Rect(width // 2 - 100, height // 2 + 100, 200, 50)

    pygame.draw.rect(screen, (0, 255, 0), start_button)
    pygame.draw.rect(screen, (255, 0, 0), quit_button)

    start_text = font.render("Start", True, (0, 0, 0))
    quit_text = font.render("Quit", True, (0, 0, 0))

    screen.blit(start_text, (start_button.x + start_button.width // 2 - start_text.get_width() // 2, start_button.y + start_button.height // 2 - start_text.get_height() // 2))
    screen.blit(quit_text, (quit_button.x + quit_button.width // 2 - quit_text.get_width() // 2, quit_button.y + quit_button.height // 2 - quit_text.get_height() // 2))

    pygame.display.flip()

    return start_button, quit_button

def display_score(screen, score):
    screen.fill((30, 30, 30))
    font = pygame.font.Font(None, 74)
    text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, screen.get_height() // 2 - text.get_height() // 2))
    pygame.display.flip()
    pygame.time.wait(3000)