import pygame
import random
import os

# Initialize Pygame
pygame.init()

# Get the absolute path of the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600

# Colors
WHITE, BLACK, GREEN = (255, 255, 255), (0, 0, 0), (0, 255, 0)
PLAYER_COLOR, PLAYER_INVISIBLE_COLOR = (0, 128, 255), (0, 0, 255)  # Changed invis color to blue
OBSTACLE_COLOR = (255, 0, 0)
BACKGROUND_COLOR = (30, 30, 30)
TEXT_COLOR = (255, 255, 255)
invis_BAR_BORDER_COLOR = (200, 200, 200)
invis_BAR_FILL_COLOR = (0, 255, 0)
PIT_COLOR = (255, 0, 0)  # Grey color for the pit

# Player settings
PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_SPEED, PLAYER_JUMP_SPEED = 200, 200, 10, 2  # Reduced jump speed for more realistic motion
BASE_INVISIBLE_DURATION, INVISIBLE_RECHARGE_RATE = 150, 2

# Obstacle settings
OBSTACLE_WIDTH, OBSTACLE_HEIGHT, OBSTACLE_SPEED = 100, 100, 5
TALL_OBSTACLE_WIDTH, TALL_OBSTACLE_HEIGHT = 200, 200  # Separate dimensions for tall obstacles
PIT_WIDTH = 80  # Width of the pit

# Y-axis positions
OBSTACLE_Y_POS = SCREEN_HEIGHT - OBSTACLE_HEIGHT - 30
TALL_OBSTACLE_Y_POS = SCREEN_HEIGHT - TALL_OBSTACLE_HEIGHT - 30
PIT_Y_POS = SCREEN_HEIGHT - (TALL_OBSTACLE_HEIGHT // 2) + 35

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Endless Runner")

# Font for displaying speed and score
font = pygame.font.Font(None, 36)

# Jump settings
PLAYER_JUMP_HEIGHT = 10  # Increased jump height to clear two obstacles
GRAVITY = 0.4  # Further reduced gravity for smoother fall
MAX_JUMPS = 2  # Allow two jumps

BACKGROUND_IMAGE = pygame.image.load(os.path.join(script_dir, 'background.png')).convert()
BACKGROUND_IMAGE = pygame.transform.scale(BACKGROUND_IMAGE, (SCREEN_WIDTH, SCREEN_HEIGHT))

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(os.path.join(script_dir, 'player.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (PLAYER_WIDTH, PLAYER_HEIGHT))
        self.rect = self.image.get_rect(x=100, y=SCREEN_HEIGHT - PLAYER_HEIGHT - 10)
        self.mask = pygame.mask.from_surface(self.image)
        self.invisible, self.invincible = False, False
        self.invisible_counter = BASE_INVISIBLE_DURATION
        self.alpha = 255
        self.is_jumping = False
        self.jump_speed = 0
        self.on_ground = True

    def update(self):
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:  # Left mouse button
            self.invisible, self.invincible = True, True
        elif mouse_buttons[2]:  # Right mouse button
            self.invisible, self.invincible = False, False

        if self.invisible:
            self.alpha = max(0, 255 * (self.invisible_counter / BASE_INVISIBLE_DURATION))
            self.invisible_counter -= 1
            if self.invisible_counter <= 0:
                self.invisible, self.invincible = False, False
        else:
            self.invisible_counter = min(BASE_INVISIBLE_DURATION, self.invisible_counter + INVISIBLE_RECHARGE_RATE)
            self.alpha = min(255, 255 * (self.invisible_counter / BASE_INVISIBLE_DURATION))

        self.image.set_alpha(self.alpha)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.on_ground and not self.invisible:
            self.is_jumping = True
            self.jump_speed = -PLAYER_JUMP_HEIGHT
            self.on_ground = False

        if self.is_jumping:
            self.rect.x += PLAYER_JUMP_SPEED // 2  # Reduce horizontal movement during jump
            self.rect.y += self.jump_speed
            self.jump_speed += GRAVITY  # Adjust gravity effect for smoother jump
            if self.rect.y >= SCREEN_HEIGHT - PLAYER_HEIGHT - 10:
                self.rect.y = SCREEN_HEIGHT - PLAYER_HEIGHT - 10
                self.is_jumping = False
                self.on_ground = True

        # Update the player image without rotation
        self.image = pygame.image.load(os.path.join(script_dir, 'player.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (PLAYER_WIDTH, PLAYER_HEIGHT))
        self.image.set_alpha(self.alpha)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.mask = pygame.mask.from_surface(self.image)

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.image = pygame.image.load(os.path.join(script_dir, 'obstacle.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (OBSTACLE_WIDTH, OBSTACLE_HEIGHT))
        self.rect = self.image.get_rect(x=x, y=OBSTACLE_Y_POS)  # Use variable for y position
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x -= OBSTACLE_SPEED

class Wall(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.image = pygame.image.load(os.path.join(script_dir, 'tall obstacle.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TALL_OBSTACLE_WIDTH, TALL_OBSTACLE_HEIGHT))  # Use separate dimensions
        self.rect = self.image.get_rect(x=x, y=TALL_OBSTACLE_Y_POS)  # Use variable for y position
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x -= OBSTACLE_SPEED

class Pit(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.image = pygame.Surface((PIT_WIDTH, 10))
        self.image.fill(PIT_COLOR)
        self.rect = self.image.get_rect(x=x, y=PIT_Y_POS)  # Use variable for y position
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x -= OBSTACLE_SPEED

all_sprites = pygame.sprite.Group()
obstacles = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

def generate_obstacle(player_x):
    obstacle_type = random.choice(['obstacle', 'wall', 'pit'])
    min_distance = 350  # Minimum distance between obstacles
    max_distance = 400  # Maximum distance between obstacles
    obstacle_x = player_x + SCREEN_WIDTH + random.randint(min_distance, max_distance)
    
    if obstacle_type == 'obstacle':
        obstacle = Obstacle(obstacle_x)
    elif obstacle_type == 'wall':
        obstacle = Wall(obstacle_x)
    else:
        obstacle = Pit(obstacle_x)
    
    # Ensure no overlap with existing obstacles
    for existing_obstacle in obstacles:
        if abs(existing_obstacle.rect.x - obstacle.rect.x) < min_distance:
            return  # Skip this generation if too close to an existing obstacle
    
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
        invis_text = font.render("Left Mouse Button: Invisible", True, TEXT_COLOR)
        jump_text = font.render("Space: Jump", True, TEXT_COLOR)
        start_text = font.render("Press Enter to Continue", True, TEXT_COLOR)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(invis_text, (SCREEN_WIDTH // 2 - invis_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(jump_text, (SCREEN_WIDTH // 2 - jump_text.get_width() // 2, SCREEN_HEIGHT // 2))
        screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
        pygame.display.flip()

running, clock, score = True, pygame.time.Clock(), 0

show_start_menu()
show_keybinds()

camera_x = 0  # Initialize camera position
background_x = 0  # Initialize background position

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    player.update()
    all_sprites.update()

    score += 1  # Increment score every frame

    if not player.invincible and pygame.sprite.spritecollide(player, obstacles, False, pygame.sprite.collide_mask):
        running = False

    if pygame.sprite.spritecollide(player, [pit for pit in obstacles if isinstance(pit, Pit)], False, pygame.sprite.collide_mask):
        running = False

    camera_x = player.rect.x - 100  # Update camera position to follow the player

    # Remove obstacles that are far behind the player
    for obstacle in obstacles:
        if obstacle.rect.x < player.rect.x - SCREEN_WIDTH:
            obstacle.kill()

    # Generate new obstacles ahead of the player
    if len(obstacles) < 5:
        generate_obstacle(player.rect.x)

    # Scroll the background
    background_x -= 5
    if background_x <= -SCREEN_WIDTH:
        background_x = 0

    screen.blit(BACKGROUND_IMAGE, (background_x, 0))
    screen.blit(BACKGROUND_IMAGE, (background_x + SCREEN_WIDTH, 0))

    for sprite in all_sprites:
        screen.blit(sprite.image, (sprite.rect.x - camera_x, sprite.rect.y))

    # Display the score
    score_text = font.render(f"Score: {score // 60}", True, TEXT_COLOR)  # Assuming 60 FPS, score is in seconds
    screen.blit(score_text, (10, 10))

    invis_bar_width, invis_bar_height = 200, 20
    invis_bar_x, invis_bar_y = (SCREEN_WIDTH - invis_bar_width) // 2, 10
    invis_bar_fill_width = min(invis_bar_width, int(invis_bar_width * (player.invisible_counter / BASE_INVISIBLE_DURATION)))
    pygame.draw.rect(screen, invis_BAR_BORDER_COLOR, (invis_bar_x - 2, invis_bar_y - 2, invis_bar_width + 4, invis_bar_height + 4), 0, border_radius=12)
    pygame.draw.rect(screen, invis_BAR_BORDER_COLOR, (invis_bar_x, invis_bar_y, invis_bar_width, invis_bar_height), 2, border_radius=10)
    pygame.draw.rect(screen, invis_BAR_FILL_COLOR, (invis_bar_x, invis_bar_y, invis_bar_fill_width, invis_bar_height), border_radius=10)

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
