import pygame

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Player settings
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 50
PLAYER_COLOR = (0, 128, 255)
PLAYER_SPEED = 10

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
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
        self.image.fill(PLAYER_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = SCREEN_HEIGHT - PLAYER_HEIGHT - 10
        self.jump = False
        self.jump_speed = 10
        self.gravity = 0.7

    def update(self):
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and not self.jump:
            self.jump = True
            self.jump_speed = -15

        if self.jump:
            self.rect.y += self.jump_speed
            self.jump_speed += self.gravity
            if self.rect.y >= SCREEN_HEIGHT - PLAYER_HEIGHT - 10:
                self.rect.y = SCREEN_HEIGHT - PLAYER_HEIGHT - 10
                self.jump = False

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

# Game loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update
    
    # Update
    all_sprites.update()

    # Increase obstacle speed

    # Check for collisions
    if pygame.sprite.spritecollideany(player, obstacles):
        running = False

    # Draw
    screen.fill(WHITE)
    all_sprites.draw(screen)

    # Display current speed
    speed_text = font.render(f"Speed: {OBSTACLE_SPEED:.2f}", True, BLACK)
    screen.blit(speed_text, (10, 10))

    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

pygame.quit()