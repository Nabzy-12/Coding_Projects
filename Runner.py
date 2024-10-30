import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600

# Colors
WHITE, BLACK, GREEN = (255, 255, 255), (0, 0, 0), (0, 255, 0)
PLAYER_COLOR, PLAYER_FADE_COLOR = (0, 128, 255), (0, 0, 255)  # Changed fade color to blue
OBSTACLE_COLOR = (255, 0, 0)
BACKGROUND_COLOR = (30, 30, 30)
TEXT_COLOR = (255, 255, 255)
FADE_BAR_BORDER_COLOR = (200, 200, 200)
FADE_BAR_FILL_COLOR = (0, 255, 0)

# Player settings
PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_SPEED, PLAYER_JUMP_SPEED = 50, 50, 10, 2  # Reduced jump speed for more realistic motion
BASE_FADE_DURATION, FADE_RECHARGE_RATE = 150, 5

# Obstacle settings
OBSTACLE_WIDTH, OBSTACLE_HEIGHT, OBSTACLE_SPEED = 50, 50, 5
WALL_HEIGHT = SCREEN_HEIGHT - 450  # Make walls tall enough so the player can't jump over them

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Endless Runner")

# Font for displaying speed and score
font = pygame.font.Font(None, 36)

# Jump settings
PLAYER_JUMP_HEIGHT = 12  # Increased jump height to clear two obstacles
GRAVITY = 0.4  # Further reduced gravity for smoother fall
MAX_JUMPS = 2  # Allow two jumps

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)
        self.image.fill(PLAYER_COLOR)
        self.rect = self.image.get_rect(x=100, y=SCREEN_HEIGHT - PLAYER_HEIGHT - 10)
        self.mask = pygame.mask.from_surface(self.image)
        self.fade, self.invincible = False, False
        self.fade_counter = BASE_FADE_DURATION
        self.alpha = 255
        self.is_jumping = False
        self.jump_speed = 0
        self.on_ground = True
        self.angle = 0
        self.total_rotation = 360  # Total rotation angle for one full rotation
        self.rotation_speed = -self.total_rotation / (10 * PLAYER_JUMP_HEIGHT / GRAVITY)  # Distribute rotation over jump duration

    def update(self):
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:  # Left mouse button
            self.fade, self.invincible = True, True
        elif mouse_buttons[2]:  # Right mouse button
            self.fade, self.invincible = False, False

        if self.fade:
            self.alpha = max(0, 255 * (self.fade_counter / BASE_FADE_DURATION))
            self.fade_counter -= 1
            if self.fade_counter <= 0:
                self.fade, self.invincible = False, False
        else:
            self.fade_counter = min(BASE_FADE_DURATION, self.fade_counter + FADE_RECHARGE_RATE)
            self.alpha = min(255, 255 * (self.fade_counter / BASE_FADE_DURATION))

        self.image.fill((*PLAYER_FADE_COLOR[:3], int(self.alpha)) if self.fade else (*PLAYER_COLOR[:3], int(self.alpha)))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.on_ground:
            self.is_jumping = True
            self.jump_speed = -PLAYER_JUMP_HEIGHT
            self.on_ground = False

        if self.is_jumping:
            self.rect.x += PLAYER_JUMP_SPEED // 2  # Reduce horizontal movement during jump
            self.rect.y += self.jump_speed
            self.jump_speed += GRAVITY  # Adjust gravity effect for smoother jump
            self.angle += self.rotation_speed  # Rotate the player while jumping
            if self.rect.y >= SCREEN_HEIGHT - PLAYER_HEIGHT - 10:
                self.rect.y = SCREEN_HEIGHT - PLAYER_HEIGHT - 10
                self.is_jumping = False
                self.on_ground = True
                self.angle = 0  # Reset angle when on the ground

        # Rotate the player image
        original_image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)
        original_image.fill((*PLAYER_FADE_COLOR[:3], int(self.alpha)) if self.fade else (*PLAYER_COLOR[:3], int(self.alpha)))
        self.image = pygame.transform.rotate(original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.mask = pygame.mask.from_surface(self.image)

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.image = pygame.Surface((OBSTACLE_WIDTH, OBSTACLE_HEIGHT))
        self.image.fill(OBSTACLE_COLOR)
        self.rect = self.image.get_rect(x=x, y=SCREEN_HEIGHT - OBSTACLE_HEIGHT - 10)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x -= OBSTACLE_SPEED

class Wall(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.image = pygame.Surface((OBSTACLE_WIDTH, WALL_HEIGHT))
        self.image.fill(OBSTACLE_COLOR)
        self.rect = self.image.get_rect(x=x, y=SCREEN_HEIGHT - WALL_HEIGHT - 10)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x -= OBSTACLE_SPEED

all_sprites = pygame.sprite.Group()
obstacles = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

def generate_obstacle(player_x):
    obstacle_type = random.choice(['obstacle', 'wall'])
    if obstacle_type == 'obstacle':
        obstacle_x = player_x + SCREEN_WIDTH + random.randint(100, 300)
        obstacle = Obstacle(obstacle_x)
    else:
        obstacle_x = player_x + SCREEN_WIDTH + random.randint(100, 300)
        obstacle = Wall(obstacle_x)
    obstacles.add(obstacle)
    all_sprites.add(obstacle)

# Initial obstacle generation
for i in range(5):
    generate_obstacle(player.rect.x + i * 300)

def show_start_menu():
    start_menu = True
    while start_menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                start_menu = False

        screen.fill(BACKGROUND_COLOR)
        title_text = font.render("Endless Runner", True, TEXT_COLOR)
        instruction_text = font.render("Press Enter to Start", True, TEXT_COLOR)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
        pygame.display.flip()

def show_keybinds():
    keybinds_screen = True
    while keybinds_screen:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                keybinds_screen = False

        screen.fill(BACKGROUND_COLOR)
        title_text = font.render("Keybinds", True, TEXT_COLOR)
        fade_text = font.render("Left Mouse Button: Fade", True, TEXT_COLOR)
        jump_text = font.render("Space: Jump", True, TEXT_COLOR)
        start_text = font.render("Press Enter to Continue", True, TEXT_COLOR)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(fade_text, (SCREEN_WIDTH // 2 - fade_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(jump_text, (SCREEN_WIDTH // 2 - jump_text.get_width() // 2, SCREEN_HEIGHT // 2))
        screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
        pygame.display.flip()

running, clock, score = True, pygame.time.Clock(), 0

show_start_menu()
show_keybinds()

camera_x = 0  # Initialize camera position

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    player.update()
    all_sprites.update()

    score += 1  # Increment score every frame

    if not player.invincible and pygame.sprite.spritecollide(player, obstacles, False, pygame.sprite.collide_mask):
        running = False

    camera_x = player.rect.x - 100  # Update camera position to follow the player

    # Remove obstacles that are far behind the player
    for obstacle in obstacles:
        if obstacle.rect.x < player.rect.x - SCREEN_WIDTH:
            obstacle.kill()

    # Generate new obstacles ahead of the player
    if len(obstacles) < 5:
        generate_obstacle(player.rect.x)

    screen.fill(BACKGROUND_COLOR)
    for sprite in all_sprites:
        screen.blit(sprite.image, (sprite.rect.x - camera_x, sprite.rect.y))

    # Display the score
    score_text = font.render(f"Score: {score // 60}", True, TEXT_COLOR)  # Assuming 60 FPS, score is in seconds
    screen.blit(score_text, (10, 10))

    fade_bar_width, fade_bar_height = 200, 20
    fade_bar_x, fade_bar_y = (SCREEN_WIDTH - fade_bar_width) // 2, 10
    fade_bar_fill_width = min(fade_bar_width, int(fade_bar_width * (player.fade_counter / BASE_FADE_DURATION)))
    pygame.draw.rect(screen, FADE_BAR_BORDER_COLOR, (fade_bar_x - 2, fade_bar_y - 2, fade_bar_width + 4, fade_bar_height + 4), 0, border_radius=12)
    pygame.draw.rect(screen, FADE_BAR_BORDER_COLOR, (fade_bar_x, fade_bar_y, fade_bar_width, fade_bar_height), 2, border_radius=10)
    pygame.draw.rect(screen, FADE_BAR_FILL_COLOR, (fade_bar_x, fade_bar_y, fade_bar_fill_width, fade_bar_height), border_radius=10)

    pygame.display.flip()
    clock.tick(60)

# Display the final score
def show_final_score(score):
    final_score_screen = True
    while final_score_screen:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                final_score_screen = False

        screen.fill(BACKGROUND_COLOR)
        score_text = font.render(f"Final Score: {score}", True, TEXT_COLOR)
        instruction_text = font.render("Press Enter to Exit", True, TEXT_COLOR)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
        pygame.display.flip()

show_final_score(score // 60)  # Convert score to seconds
pygame.quit()
