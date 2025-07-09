import pygame
import random
import sys
import json
import os
# Initialize Pygame
pygame.init()
# Game constants
WIDTH, HEIGHT = 400, 600
FPS = 60
GRAVITY = 0.5
JUMP_STRENGTH = -8
PIPE_SPEED = 3
PIPE_GAP = 150
PIPE_FREQUENCY = 1500  # milliseconds
# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (135, 206, 235)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 150, 0)  # Added for pipe details
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird Clone")
clock = pygame.time.Clock()
# Score file
SCORE_FILE = "highscore.json"
class Bird:
    def __init__(self):
        self.radius = 15
        self.x = 50
        self.y = HEIGHT // 2
        self.velocity = 0
        self.rotation = 0
        self.wing_animation = 0
        self.wing_direction = 1
    
    def flap(self):
        self.velocity = JUMP_STRENGTH
        self.wing_direction = -1
    
    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        
        # Rotate bird based on velocity
        self.rotation = -self.velocity * 3
        
        # Wing animation
        self.wing_animation += 0.2 * self.wing_direction
        if self.wing_animation > 10 or self.wing_animation < -10:
            self.wing_direction *= -1
        
        # Keep bird within screen bounds
        if self.y < self.radius:
            self.y = self.radius
            self.velocity = 0
        if self.y > HEIGHT - 100 - self.radius:  # Ground level
            self.y = HEIGHT - 100 - self.radius
            self.velocity = 0
    
    def draw(self):
        # Create bird surface
        bird_surface = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        
        # Bird body
        pygame.draw.circle(bird_surface, YELLOW, (self.radius, self.radius), self.radius)
        
        # Bird eye
        pygame.draw.circle(bird_surface, BLACK, (self.radius + 8, self.radius - 5), 3)
        
        # Bird beak
        beak_points = [
            (self.radius + 12, self.radius),
            (self.radius + 20, self.radius - 3),
            (self.radius + 20, self.radius + 3)
        ]
        pygame.draw.polygon(bird_surface, ORANGE, beak_points)
        
        # Bird wing
        wing_y = self.radius + self.wing_animation
        wing_points = [
            (self.radius - 5, self.radius),
            (self.radius - 10, wing_y),
            (self.radius, wing_y + 5)
        ]
        pygame.draw.polygon(bird_surface, ORANGE, wing_points)
        
        # Rotate the bird
        rotated_bird = pygame.transform.rotate(bird_surface, self.rotation)
        rect = rotated_bird.get_rect(center=(self.x, self.y))
        screen.blit(rotated_bird, rect.topleft)
class Pipe:
    def __init__(self, x):
        self.x = x
        self.width = 70
        self.gap = PIPE_GAP
        self.top_height = random.randint(50, HEIGHT - self.gap - 150)
        self.bottom_y = self.top_height + self.gap
        self.passed = False
        self.speed = PIPE_SPEED
        self.scored = False
    
    def update(self):
        self.x -= self.speed
    
    def draw(self):
        # Top pipe
        pygame.draw.rect(screen, GREEN, (self.x, 0, self.width, self.top_height))
        pygame.draw.rect(screen, BROWN, (self.x, self.top_height - 20, self.width, 20))
        
        # Pipe details - FIXED THIS LINE
        for i in range(0, self.top_height, 30):
            pygame.draw.rect(screen, DARK_GREEN, (self.x + 10, i, 50, 15))
        
        # Bottom pipe
        pygame.draw.rect(screen, GREEN, (self.x, self.bottom_y, self.width, HEIGHT - self.bottom_y))
        pygame.draw.rect(screen, BROWN, (self.x, self.bottom_y, self.width, 20))
        
        # Pipe details - FIXED THIS LINE
        for i in range(self.bottom_y, HEIGHT, 30):
            pygame.draw.rect(screen, DARK_GREEN, (self.x + 10, i, 50, 15))
    
    def collides_with(self, bird):
        # Simple collision detection
        if bird.x + bird.radius > self.x and bird.x - bird.radius < self.x + self.width:
            if bird.y - bird.radius < self.top_height or bird.y + bird.radius > self.bottom_y:
                return True
        return False
def draw_background(current_time):
    # Sky gradient
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(BLUE[0] * (1 - ratio) + WHITE[0] * ratio)
        g = int(BLUE[1] * (1 - ratio) + WHITE[1] * ratio)
        b = int(BLUE[2] * (1 - ratio) + WHITE[2] * ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))
    
    # Clouds
    for i in range(5):
        cloud_x = (current_time // 50 + i * 100) % (WIDTH + 200) - 100
        cloud_y = 50 + i * 30
        draw_cloud(cloud_x, cloud_y)
def draw_cloud(x, y):
    cloud_color = (255, 255, 255)
    pygame.draw.circle(screen, cloud_color, (x, y), 20)
    pygame.draw.circle(screen, cloud_color, (x + 15, y - 10), 15)
    pygame.draw.circle(screen, cloud_color, (x + 30, y), 20)
    pygame.draw.circle(screen, cloud_color, (x + 15, y + 10), 15)
def draw_ground():
    # Ground
    pygame.draw.rect(screen, BROWN, (0, HEIGHT - 100, WIDTH, 100))
    
    # Grass
    pygame.draw.rect(screen, GREEN, (0, HEIGHT - 100, WIDTH, 20))
    
    # Ground details
    for i in range(0, WIDTH, 30):
        pygame.draw.line(screen, (100, 50, 0), (i, HEIGHT - 100), (i + 15, HEIGHT - 90), 2)
def draw_score(score, high_score):
    font = pygame.font.SysFont('Arial', 40, bold=True)
    score_text = font.render(f"Score: {score}", True, BLACK)
    high_score_text = font.render(f"Best: {high_score}", True, RED)
    
    screen.blit(score_text, (20, 20))
    screen.blit(high_score_text, (WIDTH - high_score_text.get_width() - 20, 20))
def draw_game_over(score, high_score):
    # Semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    font_large = pygame.font.SysFont('Arial', 60, bold=True)
    font_medium = pygame.font.SysFont('Arial', 36, bold=True)
    font_small = pygame.font.SysFont('Arial', 24)
    
    game_over_text = font_large.render("Game Over", True, WHITE)
    score_text = font_medium.render(f"Score: {score}", True, WHITE)
    
    if score == high_score and score > 0:
        new_record_text = font_medium.render("New Record!", True, ORANGE)
        screen.blit(new_record_text, (WIDTH//2 - new_record_text.get_width()//2, HEIGHT//2 + 20))
    
    restart_text = font_small.render("Press 'R' to Restart", True, WHITE)
    
    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 80))
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
    screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 60))
def save_high_score(score):
    try:
        if os.path.exists(SCORE_FILE):
            with open(SCORE_FILE, 'r') as f:
                data = json.load(f)
                if score > data['high_score']:
                    data['high_score'] = score
                    with open(SCORE_FILE, 'w') as f:
                        json.dump(data, f)
        else:
            with open(SCORE_FILE, 'w') as f:
                json.dump({'high_score': score}, f)
    except:
        pass  # Silently fail if we can't save
def load_high_score():
    try:
        if os.path.exists(SCORE_FILE):
            with open(SCORE_FILE, 'r') as f:
                data = json.load(f)
                return data['high_score']
    except:
        pass
    return 0
def draw_start_screen(high_score):
    # Background
    draw_background(0)
    draw_ground()
    
    # Title
    font_title = pygame.font.SysFont('Arial', 70, bold=True)
    title_text = font_title.render("Flappy Bird", True, YELLOW)
    screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//4))
    
    # Instructions
    font_instructions = pygame.font.SysFont('Arial', 30)
    instructions1 = font_instructions.render("Tap or Press SPACE to flap", True, WHITE)
    instructions2 = font_instructions.render("Avoid the pipes!", True, WHITE)
    
    screen.blit(instructions1, (WIDTH//2 - instructions1.get_width()//2, HEIGHT//2))
    screen.blit(instructions2, (WIDTH//2 - instructions2.get_width()//2, HEIGHT//2 + 40))
    
    # Best score
    font_score = pygame.font.SysFont('Arial', 24)
    if high_score > 0:
        best_score = font_score.render(f"Best Score: {high_score}", True, ORANGE)
        screen.blit(best_score, (WIDTH//2 - best_score.get_width()//2, HEIGHT//2 + 100))
    
    # Play button
    font_button = pygame.font.SysFont('Arial', 36, bold=True)
    play_button = font_button.render("PLAY", True, WHITE)
    button_rect = play_button.get_rect(center=(WIDTH//2, HEIGHT//2 + 180))
    
    # Button background
    button_color = (0, 150, 0)
    pygame.draw.rect(screen, button_color, button_rect.inflate(20, 10))
    pygame.draw.rect(screen, WHITE, button_rect.inflate(20, 10), 2)
    
    screen.blit(play_button, button_rect)
    
    return button_rect
def main():
    bird = Bird()
    pipes = []
    score = 0
    high_score = load_high_score()
    last_pipe_time = 0
    game_over = False
    current_time = 0
    game_state = "start"  # "start", "playing", "game_over"
    
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if game_state == "start":
                if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.FINGERDOWN and event.x < 1.0):
                    # Check if play button was clicked
                    mouse_pos = pygame.mouse.get_pos()
                    if play_button_rect.collidepoint(mouse_pos):
                        game_state = "playing"
                        bird = Bird()
                        pipes = []
                        score = 0
                        last_pipe_time = current_time
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        game_state = "playing"
                        bird = Bird()
                        pipes = []
                        score = 0
                        last_pipe_time = current_time
            
            elif game_state == "playing":
                if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN or (event.type == pygame.FINGERDOWN and event.x < 1.0):
                    if event.type == pygame.FINGERDOWN and event.x < 1.0:
                        # Touch event on mobile
                        bird.flap()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        # Mouse click
                        bird.flap()
                    elif event.key == pygame.K_SPACE:
                        # Keyboard space
                        bird.flap()
            
            elif game_state == "game_over":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        # Restart game
                        bird = Bird()
                        pipes = []
                        score = 0
                        last_pipe_time = current_time
                        game_state = "playing"
        
        if game_state == "start":
            play_button_rect = draw_start_screen(high_score)
        
        elif game_state == "playing":
            # Generate new pipes
            if current_time - last_pipe_time > PIPE_FREQUENCY:
                pipes.append(Pipe(WIDTH))
                last_pipe_time = current_time
            
            # Update bird
            bird.update()
            
            # Update pipes
            for pipe in pipes[:]:
                pipe.update()
                
                # Check if bird passed pipe
                if not pipe.passed and pipe.x + pipe.width < bird.x:
                    pipe.passed = True
                    pipe.scored = True
                    score += 1
                    save_high_score(score)
                
                # Remove off-screen pipes
                if pipe.x + pipe.width < 0:
                    pipes.remove(pipe)
                
                # Check collision
                if pipe.collides_with(bird):
                    game_state = "game_over"
            
            # Check ground collision
            if bird.y + bird.radius > HEIGHT - 100:
                game_state = "game_over"
            
            # Drawing
            draw_background(current_time)
            for pipe in pipes:
                pipe.draw()
            draw_ground()
            bird.draw()
            draw_score(score, high_score)
        
        elif game_state == "game_over":
            # Drawing
            draw_background(current_time)
            for pipe in pipes:
                pipe.draw()
            draw_ground()
            bird.draw()
            draw_score(score, high_score)
            draw_game_over(score, high_score)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()
if __name__ == "__main__":
    main()