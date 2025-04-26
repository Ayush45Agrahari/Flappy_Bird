import pygame
import sys
import random
pygame.mixer.init()

pygame.init()

# Constants
WIDTH, HEIGHT = 1200, 650
BIRD_SIZE = 50
PIPE_WIDTH = 50
MAX_PIPE_HEIGHT = 100
GRAVITY = 0.5
JUMP_VELOCITY = -7
FPS = 60

# Colors
WHITE = (255, 255, 255)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
BLUE = (0, 0, 255)


#bg image
image = pygame.image.load('bg.jpeg')
def background_sky(image):
    size = pygame.transform .scale(image,(1200,650))
    screen.blit(size,(0,0))
# Pygame setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()

# Bird GIF
bird_gif = pygame.image.load("bird.gif")
bird_gif = pygame.transform.scale(bird_gif, (BIRD_SIZE, BIRD_SIZE))

def draw_bird(y):
    screen.blit(bird_gif, (100, y))

def draw_pipe(x, upper_height, lower_height):
    pygame.draw.rect(screen, BROWN, (x, 0, PIPE_WIDTH, upper_height))
    pygame.draw.rect(screen, BROWN, (x, HEIGHT - lower_height, PIPE_WIDTH, lower_height))

    # Add decorations to pipes
    pygame.draw.rect(screen, (255, 0, 0), (x, upper_height - 10, PIPE_WIDTH, 10))  # Example decoration for the upper pipe
    pygame.draw.rect(screen, (255, 0, 0), (x, HEIGHT - lower_height, PIPE_WIDTH, 10))  # Example decoration for the lower pipe

def draw_score(score):
    font = pygame.font.Font(None, 50)
    text = font.render(f"Score: {score}", True, BLUE)
    text_rect = text.get_rect(center=(WIDTH // 2, 50))
    screen.blit(text, text_rect)

def game_over(score):
    font = pygame.font.Font(None, 48)
    text1 = font.render(f"Game Over!", True, BLUE)  # Change to blue
    text1_rect = text1.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 36))
    screen.blit(text1, text1_rect)

    text2 = font.render(f"Your Score: {score}", True, BLUE)  # Change to blue
    text2_rect = text2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 18))
    screen.blit(text2, text2_rect)

    text3 = font.render(f"Press R to Restart", True, BLUE)  # Change to blue
    text3_rect = text3.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 72))
    screen.blit(text3, text3_rect)
    pygame.display.flip()
    pygame.mixer.music.load('bomb.wav')
    pygame.mixer.music.play()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True

        clock.tick(FPS)

# Main game loop
while True:
    bird_y = HEIGHT // 2
    bird_velocity = 0
    pipes = []
    game_active = True
    score = 0
    pygame.mixer.music.load('beep.mp3')
    pygame.mixer.music.play()
    while game_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    
                    bird_velocity = JUMP_VELOCITY

        bird_y += bird_velocity
        bird_velocity += GRAVITY

        # Generate pipes
        if random.randint(0, 20) == 0:
            pipe_height = random.randint(50, MAX_PIPE_HEIGHT)
            pipes.append({'x': WIDTH, 'height': pipe_height})

        # Move pipes
        for pipe in pipes:
            pipe['x'] -= 5

        # Remove off-screen pipes
        pipes = [pipe for pipe in pipes if pipe['x'] > -PIPE_WIDTH]

        # Check for collisions
        bird_rect = pygame.Rect(100, bird_y, BIRD_SIZE, BIRD_SIZE)
        for pipe in pipes:
            pipe_rect_upper = pygame.Rect(pipe['x'], 0, PIPE_WIDTH, pipe['height'])
            pipe_rect_lower = pygame.Rect(pipe['x'], pipe['height'] + 350, PIPE_WIDTH, HEIGHT - pipe['height'] - 350)
            if bird_rect.colliderect(pipe_rect_upper) or bird_rect.colliderect(pipe_rect_lower) or bird_y < 0 or bird_y > HEIGHT:
                game_active = False
                if game_over(score):
                    break

        # Check for passing pipes and update score
        for pipe in pipes:
            if pipe['x'] == 150 - BIRD_SIZE:
                score += 1

        # Draw background
        screen.fill(GRAY)
        background_sky(image)

        # Draw bird
        draw_bird(bird_y)

        # Draw pipes
        for pipe in pipes:
            draw_pipe(pipe['x'], pipe['height'], HEIGHT - pipe['height'] - 350)

        # Draw score
        draw_score(score)

        pygame.display.flip()
        clock.tick(FPS)