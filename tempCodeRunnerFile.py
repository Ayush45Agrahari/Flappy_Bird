import pygame
import sys
import random
import os

# --- Initialize ---
pygame.init()
pygame.mixer.init()

# --- Constants ---
BIRD_SIZE = 50
PIPE_WIDTH = 80
PIPE_GAP = 200
GRAVITY = 0.5
JUMP_VELOCITY = -8
PIPE_SPEED = 5
FPS = 60
FLAP_ANIM_SPEED = 5
GROUND_HEIGHT = 100
CLOUD_COUNT = 5

# --- Colors ---
WHITE = (255, 255, 255)
GREEN = (34, 177, 76)
RED = (200, 0, 0)
GRAY = (120, 120, 120)
SKY_BLUE = (135, 206, 235)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
LIGHT_GRAY = (200, 200, 200)

# --- Window Buttons ---
BTN_COLOR = (200, 200, 200)
BTN_HOVER = (150, 150, 150)
BTN_SIZE = 30

# --- Screen Setup ---
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()

# --- Load Bird ---
bird_frames = []
for i in range(1, 4):
    try:
        img = pygame.image.load(f"bird{i}.png").convert_alpha()
        bird_frames.append(pygame.transform.scale(img, (BIRD_SIZE, BIRD_SIZE)))
    except:
        print(f"Error: bird{i}.png not found!")
        sys.exit()
bird_frame_index = 0
frame_counter = 0

# --- Load Sounds ---
try:
    flap_sound = pygame.mixer.Sound("beep.mp3")
    gameover_sound = pygame.mixer.Sound("gameover.wav")
except:
    print("Error: Sound files not found!")
    sys.exit()

# --- High Score ---
HIGH_SCORE_FILE = "highscore.txt"
def load_high_score():
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, "r") as f:
            return int(f.read().strip())
    return 0

def save_high_score(score):
    with open(HIGH_SCORE_FILE, "w") as f:
        f.write(str(score))

# --- Utility Functions ---
def draw_text(text, size, color, x, y):
    font = pygame.font.Font(None, size)
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(x, y))
    screen.blit(surf, rect)

def button(text, rect, color, hover_color):
    mouse = pygame.mouse.get_pos()
    clicked = pygame.mouse.get_pressed()[0]
    if rect.collidepoint(mouse):
        pygame.draw.rect(screen, hover_color, rect, border_radius=10)
    else:
        pygame.draw.rect(screen, color, rect, border_radius=10)
    draw_text(text, 40, WHITE, rect.centerx, rect.centery)
    return rect.collidepoint(mouse) and clicked

# --- Clouds ---
clouds = [{'x': random.randint(0, WIDTH), 'y': random.randint(50, 250), 'size': random.randint(50, 120)} for _ in range(CLOUD_COUNT)]
def draw_clouds():
    for cloud in clouds:
        pygame.draw.ellipse(screen, LIGHT_GRAY, (cloud['x'], cloud['y'], cloud['size'], cloud['size']//2))
        cloud['x'] -= 1
        if cloud['x'] + cloud['size'] < 0:
            cloud['x'] = WIDTH
            cloud['y'] = random.randint(50, 250)
            cloud['size'] = random.randint(50, 120)

# --- Window Buttons Functions ---
def draw_window_buttons():
    x = WIDTH - BTN_SIZE - 10
    y = 10

    # Close
    close_rect = pygame.Rect(x, y, BTN_SIZE, BTN_SIZE)
    pygame.draw.rect(screen, BTN_COLOR, close_rect)
    pygame.draw.line(screen, RED, (x+5, y+5), (x+BTN_SIZE-5, y+BTN_SIZE-5), 2)
    pygame.draw.line(screen, RED, (x+BTN_SIZE-5, y+5), (x+5, y+BTN_SIZE-5), 2)

    # Fullscreen
    fs_rect = pygame.Rect(x-BTN_SIZE-5, y, BTN_SIZE, BTN_SIZE)
    pygame.draw.rect(screen, BTN_COLOR, fs_rect)
    pygame.draw.rect(screen, BLUE, (fs_rect.x+5, fs_rect.y+5, BTN_SIZE-10, BTN_SIZE-10), 2)

    # Minimize
    min_rect = pygame.Rect(x-BTN_SIZE*2-10, y, BTN_SIZE, BTN_SIZE)
    pygame.draw.rect(screen, BTN_COLOR, min_rect)
    pygame.draw.line(screen, BLUE, (min_rect.x+5, min_rect.y+BTN_SIZE-5), (min_rect.x+BTN_SIZE-5, min_rect.y+BTN_SIZE-5), 2)

    return close_rect, fs_rect, min_rect

def handle_window_buttons(mouse_pos):
    global screen, WIDTH, HEIGHT
    close_rect, fs_rect, min_rect = draw_window_buttons()

    if close_rect.collidepoint(mouse_pos):
        pygame.quit()
        sys.exit()
    elif fs_rect.collidepoint(mouse_pos):
        WIDTH, HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    elif min_rect.collidepoint(mouse_pos):
        pygame.display.iconify()

# --- Main Game Function ---
def main_game():
    global bird_frame_index, frame_counter
    bird_y = HEIGHT // 2
    bird_velocity = 0
    pipes = []
    score = 0
    high_score = load_high_score()
    running = True
    ground_scroll = 0

    while running and STATE == "GAME":
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird_velocity = JUMP_VELOCITY
                    flap_sound.play()
                if event.key == pygame.K_ESCAPE:
                    return "MENU", score
            if event.type == pygame.MOUSEBUTTONDOWN:
                handle_window_buttons(mouse_pos)

        # --- Physics ---
        bird_velocity += GRAVITY
        bird_y += bird_velocity

        # --- Pipes ---
        if len(pipes) == 0 or pipes[-1]['x'] < WIDTH - 300:
            upper_height = random.randint(100, HEIGHT - PIPE_GAP - GROUND_HEIGHT - 50)
            pipes.append({'x': WIDTH, 'upper': upper_height, 'passed': False})

        for pipe in pipes:
            pipe['x'] -= PIPE_SPEED
        pipes = [p for p in pipes if p['x'] > -PIPE_WIDTH]

        # --- Collision ---
        bird_rect = pygame.Rect(100, bird_y, BIRD_SIZE, BIRD_SIZE)
        hit_pipe = False
        for pipe in pipes:
            upper_rect = pygame.Rect(pipe['x'], 0, PIPE_WIDTH, pipe['upper'])
            lower_rect = pygame.Rect(pipe['x'], pipe['upper'] + PIPE_GAP, PIPE_WIDTH, HEIGHT - pipe['upper'] - GROUND_HEIGHT)
            if bird_rect.colliderect(upper_rect) or bird_rect.colliderect(lower_rect):
                hit_pipe = True
                break

        if hit_pipe or bird_y < 0 or bird_y > HEIGHT - BIRD_SIZE - GROUND_HEIGHT:
            flap_sound.stop()
            gameover_sound.play()
            if score > high_score:
                save_high_score(score)
            pygame.time.delay(700)
            return "GAMEOVER", score

        # --- Score ---
        for pipe in pipes:
            if not pipe['passed'] and pipe['x'] + PIPE_WIDTH < 100:
                pipe['passed'] = True
                score += 1

        # --- Bird Animation ---
        frame_counter += 1
        if frame_counter >= FLAP_ANIM_SPEED:
            bird_frame_index = (bird_frame_index + 1) % len(bird_frames)
            frame_counter = 0
        bird_img = bird_frames[bird_frame_index]
        angle = max(-25, min(90, -bird_velocity*3 if bird_velocity < 0 else bird_velocity*3))
        rotated_bird = pygame.transform.rotate(bird_img, -angle)
        bird_rect_rotated = rotated_bird.get_rect(center=(100 + BIRD_SIZE//2, bird_y + BIRD_SIZE//2))

        # --- Draw everything ---
        screen.fill(SKY_BLUE)
        draw_clouds()

        for pipe in pipes:
            pygame.draw.rect(screen, GREEN, (pipe['x'], 0, PIPE_WIDTH, pipe['upper']))
            pygame.draw.rect(screen, GREEN, (pipe['x'], pipe['upper'] + PIPE_GAP, PIPE_WIDTH, HEIGHT - pipe['upper'] - GROUND_HEIGHT))

        ground_scroll -= PIPE_SPEED
        if ground_scroll <= -WIDTH:
            ground_scroll = 0
        pygame.draw.rect(screen, BROWN, (ground_scroll, HEIGHT - GROUND_HEIGHT, WIDTH*2, GROUND_HEIGHT))

        screen.blit(rotated_bird, bird_rect_rotated.topleft)
        draw_text(f"Score: {score}", 50, WHITE, WIDTH // 2, 50)

        # Draw window buttons
        draw_window_buttons()

        pygame.display.flip()
        clock.tick(FPS)

    return "MENU", 0

# --- Main Loop ---
STATE = "MENU"
score_on_death = 0
while True:
    mouse_pos = pygame.mouse.get_pos()

    if STATE == "MENU":
        screen.fill(SKY_BLUE)
        draw_clouds()
        draw_text("Flappy Bird", 100, WHITE, WIDTH // 2, HEIGHT // 4)

        play_btn = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 40, 300, 60)
        hs_btn = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 40, 300, 60)
        quit_btn = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 120, 300, 60)

        if button("PLAY", play_btn, BLUE, (0, 200, 255)):
            STATE = "GAME"
        if button("HIGH SCORE", hs_btn, GRAY, (180, 180, 180)):
            STATE = "HIGHSCORE"
        if button("QUIT", quit_btn, RED, (255, 80, 80)):
            pygame.quit(); sys.exit()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                handle_window_buttons(mouse_pos)

        draw_window_buttons()
        pygame.display.flip()
        clock.tick(30)

    elif STATE == "GAME":
        STATE, score_on_death = main_game()

    elif STATE == "GAMEOVER":
        screen.fill(SKY_BLUE)
        draw_clouds()
        hs = load_high_score()
        draw_text("GAME OVER", 90, RED, WIDTH // 2, HEIGHT // 3)
        draw_text(f"Score: {score_on_death}", 60, WHITE, WIDTH // 2, HEIGHT // 2)
        draw_text(f"Best: {hs}", 40, WHITE, WIDTH // 2, HEIGHT // 2 + 60)
        draw_text("Press R to Restart or ESC for Menu", 40, WHITE, WIDTH // 2, HEIGHT - 100)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    STATE = "GAME"
                elif event.key == pygame.K_ESCAPE:
                    STATE = "MENU"
            if event.type == pygame.MOUSEBUTTONDOWN:
                handle_window_buttons(mouse_pos)

        draw_window_buttons()
        pygame.display.flip()
        clock.tick(30)

    elif STATE == "HIGHSCORE":
        screen.fill(SKY_BLUE)
        draw_clouds()
        hs = load_high_score()
        draw_text("HIGH SCORE", 80, WHITE, WIDTH // 2, HEIGHT // 3)
        draw_text(str(hs), 100, BLUE, WIDTH // 2, HEIGHT // 2)
        draw_text("Press ESC to return", 40, WHITE, WIDTH // 2, HEIGHT - 100)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                STATE = "MENU"
            if event.type == pygame.MOUSEBUTTONDOWN:
                handle_window_buttons(mouse_pos)

        draw_window_buttons()
        pygame.display.flip()
        clock.tick(30)
