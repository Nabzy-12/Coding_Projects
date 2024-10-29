import pygame

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
PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_SPEED = 50, 50, 10
BASE_FADE_DURATION, FADE_RECHARGE_RATE = 150, 5

# Obstacle settings
OBSTACLE_WIDTH, OBSTACLE_HEIGHT, OBSTACLE_SPEED = 50, 50, 5
OBSTACLE_SPEED_INCREMENT, SPEED_INCREASE_INTERVAL = 1, 150

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Endless Runner")

# Font for displaying speed and score
font = pygame.font.Font(None, 36)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)
        self.image.fill(PLAYER_COLOR)
        self.rect = self.image.get_rect(x=100, y=SCREEN_HEIGHT - PLAYER_HEIGHT - 10)
        self.fade, self.invincible = False, False
        self.fade_counter = BASE_FADE_DURATION
        self.alpha = 255

    def update(self, fade_duration=BASE_FADE_DURATION + OBSTACLE_SPEED * 2):
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:  # Left mouse button
            self.fade, self.invincible = True, True
        elif mouse_buttons[2]:  # Right mouse button
            self.fade, self.invincible = False, False

        if self.fade:
            self.alpha = max(0, 255 * (self.fade_counter / fade_duration))
            self.fade_counter -= 1
            if self.fade_counter <= 0:
                self.fade, self.invincible = False, False
        else:
            self.fade_counter = min(fade_duration, self.fade_counter + FADE_RECHARGE_RATE)
            self.alpha = min(255, 255 * (self.fade_counter / fade_duration))

        self.image.fill((*PLAYER_FADE_COLOR[:3], int(self.alpha)) if self.fade else (*PLAYER_COLOR[:3], int(self.alpha)))

class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((OBSTACLE_WIDTH, OBSTACLE_HEIGHT))
        self.image.fill(OBSTACLE_COLOR)
        self.rect = self.image.get_rect(x=SCREEN_WIDTH, y=SCREEN_HEIGHT - OBSTACLE_HEIGHT - 10)

    def update(self):
        self.rect.x -= OBSTACLE_SPEED
        if self.rect.x < -OBSTACLE_WIDTH:
            self.rect.x = SCREEN_WIDTH

all_sprites = pygame.sprite.Group()
obstacles = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

def check_obstacle_distance(obstacles, new_obstacle, min_distance):
    return all(abs(obstacle.rect.x - new_obstacle.rect.x) >= min_distance for obstacle in obstacles)

min_distance, max_group_size, group_size = 200, 2, 0

for i in range(5):
    obstacle = Obstacle()
    obstacle.rect.x = SCREEN_WIDTH + i * 300
    if group_size < max_group_size and check_obstacle_distance(obstacles, obstacle, min_distance):
        obstacles.add(obstacle)
        all_sprites.add(obstacle)
        group_size += 1
    else:
        group_size = 0

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

running, clock, frame_counter, score = True, pygame.time.Clock(), 0, 0

show_start_menu()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    player.update()
    all_sprites.update()

    frame_counter += 1
    score += 1  # Increment score every frame
    if frame_counter >= SPEED_INCREASE_INTERVAL:
        OBSTACLE_SPEED += OBSTACLE_SPEED_INCREMENT
        frame_counter = 0

    if not player.invincible and pygame.sprite.spritecollideany(player, obstacles):
        running = False

    screen.fill(BACKGROUND_COLOR)
    all_sprites.draw(screen)

    speed_text = font.render(f"Speed: {OBSTACLE_SPEED}", True, TEXT_COLOR)
    screen.blit(speed_text, (10, 10))
    # Display the score
    score_text = font.render(f"Score: {score // 60}", True, TEXT_COLOR)  # Assuming 60 FPS, score is in seconds
    screen.blit(score_text, (10, 50))

    fade_bar_width, fade_bar_height = 200, 20
    fade_bar_x, fade_bar_y = (SCREEN_WIDTH - fade_bar_width) // 2, 10
    fade_bar_fill_width = min(fade_bar_width, int(fade_bar_width * (player.fade_counter / (BASE_FADE_DURATION + OBSTACLE_SPEED * 2))))
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