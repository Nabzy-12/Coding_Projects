import pygame

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# Player settings
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 50
PLAYER_COLOR = (0, 128, 255)
PLAYER_FADE_COLOR = (128, 128, 128)  # Color when fading
PLAYER_SPEED = 10
BASE_FADE_DURATION = 150  # Base duration of the fade effect in frames
FADE_RECHARGE_RATE = 5  # Rate at which the fade meter recharges

# Obstacle settings
OBSTACLE_WIDTH = 50
OBSTACLE_HEIGHT = 50
OBSTACLE_COLOR = (255, 0, 0)
OBSTACLE_SPEED = 5
OBSTACLE_SPEED_INCREMENT = 0.01  # Speed increment per frame

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Endless Runner")

# Font for displaying speed
font = pygame.font.Font(None, 36)

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)
        self.image.fill(PLAYER_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = SCREEN_HEIGHT - PLAYER_HEIGHT - 10
        self.fade = False
        self.fade_counter = BASE_FADE_DURATION
        self.invincible = False

    def update(self, fade_duration=None):
        if fade_duration is None:
            fade_duration = BASE_FADE_DURATION + OBSTACLE_SPEED * 2  # Adjust the multiplier as needed
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:  # Left mouse button
            self.fade = True
            self.invincible = True
        elif mouse_buttons[2]:  # Right mouse button
            self.fade = False
            self.invincible = False
            self.image.fill(PLAYER_COLOR)

        if self.fade:
            alpha = max(0, 255 * (self.fade_counter / fade_duration))
            self.image.fill((*PLAYER_FADE_COLOR[:3], int(alpha)))
            self.fade_counter -= 1
            if self.fade_counter <= 0:
                self.fade = False
                self.invincible = False
                self.image.fill(PLAYER_COLOR)
        else:
            if self.fade_counter < fade_duration:
                self.fade_counter = min(fade_duration, self.fade_counter + FADE_RECHARGE_RATE)

# Obstacle class
class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((OBSTACLE_WIDTH, OBSTACLE_HEIGHT))
        self.image.fill(OBSTACLE_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = SCREEN_HEIGHT - OBSTACLE_HEIGHT - 10

    def update(self):
        self.rect.x -= OBSTACLE_SPEED
        if self.rect.x < -OBSTACLE_WIDTH:
            self.rect.x = SCREEN_WIDTH
            self.rect.y = SCREEN_HEIGHT - OBSTACLE_HEIGHT - 10

# Create sprite groups
all_sprites = pygame.sprite.Group()
obstacles = pygame.sprite.Group()

# Create player
player = Player()
all_sprites.add(player)

# Function to check distance between obstacles
def check_obstacle_distance(obstacles, new_obstacle, min_distance):
    for obstacle in obstacles:
        if abs(obstacle.rect.x - new_obstacle.rect.x) < min_distance:
            return False
    return True

# Create obstacles
min_distance = 200
max_group_size = 2
group_size = 0

for i in range(5):
    obstacle = Obstacle()
    obstacle.rect.x = SCREEN_WIDTH + i * 300
    if group_size < max_group_size and check_obstacle_distance(obstacles, obstacle, min_distance):
        obstacles.add(obstacle)
        all_sprites.add(obstacle)
        group_size += 1
    else:
        group_size = 0

# Function to display the start menu
def show_start_menu():
    start_menu = True
    while start_menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    start_menu = False

        screen.fill(WHITE)
        title_text = font.render("Endless Runner", True, BLACK)
        instruction_text = font.render("Press Enter to Start", True, BLACK)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
        pygame.display.flip()

# Game loop
running = True
clock = pygame.time.Clock()

# Show start menu
show_start_menu()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update
    fade_duration = BASE_FADE_DURATION + OBSTACLE_SPEED * 2  # Adjust the multiplier as needed
    player.update(fade_duration)
    all_sprites.update()

    # Increase obstacle speed
    OBSTACLE_SPEED += OBSTACLE_SPEED_INCREMENT

    # Check for collisions
    if not player.invincible and pygame.sprite.spritecollideany(player, obstacles):
        running = False

    # Draw
    screen.fill(WHITE)
    all_sprites.draw(screen)

    # Display current speed
    speed_text = font.render(f"Speed: {OBSTACLE_SPEED:.2f}", True, BLACK)
    screen.blit(speed_text, (10, 10))

    # Display fade time bar
    fade_bar_width = 200
    fade_bar_height = 20
    fade_bar_x = SCREEN_WIDTH - fade_bar_width - 10
    fade_bar_y = 10
    fade_bar_fill_width = int(fade_bar_width * (player.fade_counter / fade_duration))
    pygame.draw.rect(screen, BLACK, (fade_bar_x, fade_bar_y, fade_bar_width, fade_bar_height), 2)
    pygame.draw.rect(screen, GREEN, (fade_bar_x, fade_bar_y, fade_bar_fill_width, fade_bar_height))

    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

pygame.quit()
