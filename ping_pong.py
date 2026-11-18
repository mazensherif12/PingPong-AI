import pygame
import random
import platform
import asyncio

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
PADDLE_WIDTH, PADDLE_HEIGHT = 20, 100
BALL_RADIUS = 8
WIN_SCORE = 5
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FONT = pygame.font.SysFont("Arial", 40)

# Set up display
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ping Pong: AI vs Player")

class Paddle:
    COLOR = WHITE
    SPEED = 5

    def _init_(self, x, y, width, height):
        self.x = self.original_x = x
        self.y = self.original_y = y
        self.width = width
        self.height = height

    def draw(self, window):
        pygame.draw.rect(window, self.COLOR, (self.x, self.y, self.width, self.height))

    def move(self, up=True):
        target_y = self.y - self.SPEED if up else self.y + self.SPEED
        if 0 <= target_y <= HEIGHT - self.height:
            self.y = target_y

    def reset(self):
        self.y = self.original_y

class Ball:
    MAX_VEL = 10
    COLOR = WHITE
    SPEED_INCREMENT = 0.2

    def _init_(self, x, y, radius):
        self.x = self.original_x = x
        self.y = self.original_y = y
        self.radius = radius
        self.x_vel = self.initial_velocity()
        self.y_vel = 0

    def initial_velocity(self):
        return random.choice([5, -5])

    def draw(self, window):
        pygame.draw.circle(window, self.COLOR, (self.x, self.y), self.radius)

    def move(self):
        self.x += self.x_vel
        self.y += self.y_vel

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y
        self.x_vel = self.initial_velocity()
        self.y_vel = 0

class GameEnvironment:
    def _init_(self):
        self.left_paddle = Paddle(10, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.right_paddle = Paddle(WIDTH - 10 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.ball = Ball(WIDTH // 2, HEIGHT // 2, BALL_RADIUS)
        self.left_score = 0
        self.right_score = 0
        self.game_state = "start"  # start, playing, game_over
        self.winner = None

    def get_state(self):
        return (self.ball.x, self.ball.y, self.ball.x_vel, self.ball.y_vel, self.right_paddle.y)

    def apply_action(self, action):
        if action == 1:
            self.right_paddle.move(up=True)
        elif action == 2:
            self.right_paddle.move(up=False)

    def step(self):
        if self.game_state != "playing":
            return 0
        self.ball.move()
        reward = self.handle_collision()
        score_reward = self.check_scores()
        return reward + score_reward

    def handle_collision(self):
        reward = 0
        # Ceiling and floor
        if self.ball.y + self.ball.radius >= HEIGHT:
            self.ball.y = HEIGHT - self.ball.radius
            self.ball.y_vel = -abs(self.ball.y_vel)
        elif self.ball.y - self.ball.radius <= 0:
            self.ball.y = self.ball.radius
            self.ball.y_vel = abs(self.ball.y_vel)

        # Paddle collisions
        if self.ball.x_vel < 0:
            if (self.left_paddle.y <= self.ball.y <= self.left_paddle.y + self.left_paddle.height and
                    self.ball.x - self.ball.radius <= self.left_paddle.x + self.left_paddle.width):
                self.ball.x_vel = -self.ball.x_vel + Ball.SPEED_INCREMENT
                self.ball.x_vel = min(self.ball.x_vel, Ball.MAX_VEL)
                middle_y = self.left_paddle.y + self.left_paddle.height / 2
                displacement = middle_y - self.ball.y
                reduction = (self.left_paddle.height / 2) / Ball.MAX_VEL
                self.ball.y_vel = -(displacement / reduction)
        else:
            if (self.right_paddle.y <= self.ball.y <= self.right_paddle.y + self.right_paddle.height and
                    self.ball.x + self.ball.radius >= self.right_paddle.x):
                self.ball.x_vel = -self.ball.x_vel + Ball.SPEED_INCREMENT
                self.ball.x_vel = max(self.ball.x_vel, -Ball.MAX_VEL)
                middle_y = self.right_paddle.y + self.right_paddle.height / 2
                displacement = middle_y - self.ball.y
                reduction = (self.right_paddle.height / 2) / Ball.MAX_VEL
                self.ball.y_vel = -(displacement / reduction)
                reward = 1
        return reward

    def check_scores(self):
        reward = 0
        if self.ball.x < 0:
            self.right_score += 1
            reward = 5
            self.reset_round()
        elif self.ball.x > WIDTH:
            self.left_score += 1
            reward = -5
            self.reset_round()
        if self.left_score >= WIN_SCORE or self.right_score >= WIN_SCORE:
            self.winner = "Player" if self.left_score >= WIN_SCORE else "AI"
            self.game_state = "game_over"
        return reward

    def reset_round(self):
        self.ball.reset()
        self.left_paddle.reset()
        self.right_paddle.reset()

    def draw(self, window):
        window.fill(BLACK)
        # Draw center line
        for i in range(10, HEIGHT, HEIGHT // 20):
            if i % 2 == 1:
                continue
            pygame.draw.rect(window, WHITE, (WIDTH // 2 - 5, i, 10, HEIGHT // 20))
        # Draw paddles and ball
        self.left_paddle.draw(window)
        self.right_paddle.draw(window)
        self.ball.draw(window)
        # Draw scores
        left_score_text = FONT.render(str(self.left_score), True, WHITE)
        right_score_text = FONT.render(str(self.right_score), True, WHITE)
        window.blit(left_score_text, (WIDTH // 4 - left_score_text.get_width() // 2, 20))
        window.blit(right_score_text, (WIDTH * 3 // 4 - right_score_text.get_width() // 2, 20))
        # Draw prompts
        if self.game_state == "start":
            start_text = FONT.render("Press SPACE to Start", True, WHITE)
            window.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2))
        elif self.game_state == "game_over":
            win_text = FONT.render(f"{self.winner} Wins!", True, WHITE)
            replay_text = FONT.render("Press R to Replay, Q to Quit", True, WHITE)
            window.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2 - 40))
            window.blit(replay_text, (WIDTH // 2 - replay_text.get_width() // 2, HEIGHT // 2 + 20))
        pygame.display.update()

class AIAgent:
    def _init_(self):
        self.error_margin = 5  # Small error for realism

    def select_action(self, state):
        ball_x, ball_y, ball_x_vel, ball_y_vel, paddle_y = state
        if ball_x_vel <= 0:
            target_y = HEIGHT // 2  # Center paddle when ball moves away
        else:
            # Predict ball's y-position at right paddle
            steps = (WIDTH - PADDLE_WIDTH - ball_x) / ball_x_vel
            predicted_y = ball_y + ball_y_vel * steps
            while predicted_y < 0 or predicted_y > HEIGHT:
                if predicted_y < 0:
                    predicted_y = -predicted_y
                elif predicted_y > HEIGHT:
                    predicted_y = 2 * HEIGHT - predicted_y
            # Add small random error
            predicted_y += random.uniform(-self.error_margin, self.error_margin)
            target_y = predicted_y

        # Greedy action: Move to minimize distance to target_y
        paddle_center = paddle_y + PADDLE_HEIGHT / 2
        if paddle_center < target_y - 10:
            return 2  # Move down
        elif paddle_center > target_y + 10:
            return 1  # Move up
        return 0  # Stay

async def main():
    clock = pygame.time.Clock()
    env = GameEnvironment()
    ai = AIAgent()
    run = True

    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if env.game_state == "start" and event.key == pygame.K_SPACE:
                    env.game_state = "playing"
                elif env.game_state == "game_over":
                    if event.key == pygame.K_r:
                        env = GameEnvironment()
                        ai = AIAgent()
                    elif event.key == pygame.K_q:
                        run = False

        if env.game_state == "playing":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                env.left_paddle.move(up=True)
            if keys[pygame.K_s]:
                env.left_paddle.move(up=False)
            state = env.get_state()
            action = ai.select_action(state)
            env.apply_action(action)
            env.step()

        env.draw(WINDOW)
        await asyncio.sleep(1.0 / FPS)

    pygame.quit()

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if _name_ == "_main_":
        asyncio.run(main())