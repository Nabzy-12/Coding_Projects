import pygame
import random
import time

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BRICK_WIDTH = 75
BRICK_HEIGHT = 20
PADDLE_WIDTH = 150
PADDLE_HEIGHT = 20
BALL_RADIUS = 10
PADDLE_SPEED = 0.4
BALL_SPEED_X = 0.2
BALL_SPEED_Y = 0.2

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
font = pygame.font.Font(None, 36)

# Brick class inheriting from pygame.Rect
class Brick(pygame.Rect):
    def __init__(self, x, y):
        super().__init__(x, y, BRICK_WIDTH, BRICK_HEIGHT)

# Ball class to handle ball properties and movement
class Ball:
    def __init__(self, x, y, speed_x, speed_y):
        self.x = x
        self.y = y
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.start_time = time.time()

    def move(self):
        # Increase speed gradually for the first second
        elapsed_time = time.time() - self.start_time
        if (elapsed_time < 1):
            factor = elapsed_time / 1  # Gradually increase factor from 0 to 1
            self.x += self.speed_x * factor
            self.y += self.speed_y * factor
        else:
            self.x += self.speed_x
            self.y += self.speed_y

    def bounce_x(self):
        self.speed_x = -self.speed_x

    def bounce_y(self):
        self.speed_y = -self.speed_y

# Paddle class to handle paddle properties and movement
class Paddle:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move_left(self):
        if self.x > 0:
            self.x -= PADDLE_SPEED

    def move_right(self):
        if self.x < SCREEN_WIDTH - PADDLE_WIDTH:
            self.x += PADDLE_SPEED

# Function to create a grid of bricks
def create_bricks():
    bricks = []
    for i in range(8):
        for j in range(5):
            bricks.append(Brick(i * (BRICK_WIDTH + 10) + 35, j * (BRICK_HEIGHT + 10) + 50))
    return bricks

# Main game loop
def main():
    bricks = create_bricks()
    paddle = Paddle(SCREEN_WIDTH // 2 - PADDLE_WIDTH // 2, SCREEN_HEIGHT - 30)
    ball = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, random.choice([-BALL_SPEED_X, BALL_SPEED_X]), BALL_SPEED_Y)
    game_over = False
    win = False
    running = True

    # Wait for 1 second before starting the game
    pygame.time.wait(1000)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            paddle.move_left()
        if keys[pygame.K_RIGHT]:
            paddle.move_right()

        if not game_over and not win:
            ball.move()

            # Ball collision with walls
            if ball.x <= 0 or ball.x >= SCREEN_WIDTH:
                ball.bounce_x()
            if ball.y <= 0:
                ball.bounce_y()

            # Ball collision with paddle
            if paddle.x < ball.x < paddle.x + PADDLE_WIDTH and paddle.y < ball.y + BALL_RADIUS < paddle.y + PADDLE_HEIGHT:
                ball.bounce_y()
                # Adjust ball position to be above the paddle to prevent hovering
                ball.y = paddle.y - BALL_RADIUS
                # Add some variation to the ball's horizontal speed based on where it hits the paddle
                offset = (ball.x - (paddle.x + PADDLE_WIDTH / 2)) / (PADDLE_WIDTH / 2)
                ball.speed_x += offset * 0.1

            # Ball collision with bricks
            for brick in bricks[:]:
                if brick.collidepoint(ball.x, ball.y):
                    bricks.remove(brick)
                    ball.bounce_y()
                    break

            # Check if ball exits the screen at the bottom
            if ball.y >= SCREEN_HEIGHT:
                game_over = True

            # Check for win state
            if not bricks:
                win = True

            # Render speed text
            speed_text = f"Speed X: {ball.speed_x:.2f}, Speed Y: {ball.speed_y:.2f}"
            text_surface = font.render(speed_text, True, (255, 255, 255))

        # Drawing code
        screen.fill((0, 0, 0))  # Clear screen with black
        for brick in bricks:
            pygame.draw.rect(screen, (255, 0, 0), brick)  # Draw bricks in red
        pygame.draw.rect(screen, (0, 255, 0), (paddle.x, paddle.y, PADDLE_WIDTH, PADDLE_HEIGHT))  # Draw paddle in green
        pygame.draw.circle(screen, (0, 0, 255), (ball.x, ball.y), BALL_RADIUS)  # Draw ball in blue
        screen.blit(text_surface, (10, 10))  # Draw speed text

        if game_over:
            game_over_text = font.render("Game Over", True, (255, 255, 255))
            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(game_over_text, game_over_rect)
            pygame.display.flip()  # Update the display to show the game over text
            pygame.time.wait(1000)  # Wait for 1 second
            pygame.quit()
            exit()

        if win:
            win_text = font.render("You Win!", True, (255, 255, 255))
            win_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(win_text, win_rect)
            pygame.display.flip()  # Update the display to show the win text
            pygame.time.wait(1000)  # Wait for 1 second
            pygame.quit()
            exit()

        pygame.display.flip()  # Update the display

    pygame.quit()

if __name__ == "__main__":
    main()