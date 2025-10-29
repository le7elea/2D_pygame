import pygame
import sys
import os
import random

# --- Initialize Pygame ---
pygame.init()

# --- Screen setup ---
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 40
TOP_MARGIN = 80
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("MASID: Coding Quiz")

# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 60, 60)
GREEN = (0, 220, 0)
BLUE = (80, 150, 255)
YELLOW = (255, 220, 50)
GRAY = (50, 50, 50)

# --- Load images ---
ASSET_PATH = os.path.join(os.path.dirname(__file__), "assets")
player_img = pygame.image.load(os.path.join(ASSET_PATH, "player.png"))
wall_img = pygame.image.load(os.path.join(ASSET_PATH, "wall.jpg"))
floor_img = pygame.image.load(os.path.join(ASSET_PATH, "floor.jpg"))
enemy_img = pygame.image.load(os.path.join(ASSET_PATH, "enemy.png"))

player_img = pygame.transform.scale(player_img, (TILE_SIZE - 10, TILE_SIZE - 10))
wall_img = pygame.transform.scale(wall_img, (TILE_SIZE, TILE_SIZE))
floor_img = pygame.transform.scale(floor_img, (TILE_SIZE, TILE_SIZE))
enemy_img = pygame.transform.scale(enemy_img, (TILE_SIZE - 10, TILE_SIZE - 10))

# --- Maze map ---
maze = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,0,1,0,1,0,1,1,1,1,1,1,0,1],
    [1,0,1,0,0,0,1,0,0,0,0,1,0,1,0,1],
    [1,0,1,1,1,0,1,1,1,1,0,0,0,1,0,1],
    [1,0,0,0,0,0,0,0,1,0,0,1,0,1,0,1],
    [1,1,1,1,1,1,1,0,1,1,0,1,0,1,0,1],
    [1,0,0,0,0,0,1,0,0,0,0,1,0,0,0,1],
    [1,0,1,1,1,0,1,1,1,1,1,1,1,1,0,1],
    [1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

# --- Questions bank ---
questions = [
    {"question": "What is the output of: print(2 + 3 * 2)?", "choices": ["10", "8", "12", "5"], "correct": "8"},
    {"question": "Which data type is immutable in Python?", "choices": ["list", "set", "tuple", "dict"], "correct": "tuple"},
    {"question": "Which keyword is used to define a function?", "choices": ["func", "def", "lambda", "define"], "correct": "def"},
    {"question": "What is the output of len('hello')?", "choices": ["4", "5", "6", "error"], "correct": "5"},
    {"question": "Which symbol is used for comments in Python?", "choices": ["//", "#", "/*", "<!--"], "correct": "#"},
    {"question": "What is 10 % 3?", "choices": ["1", "3", "0", "2"], "correct": "1"},
    {"question": "Which data structure uses key-value pairs?", "choices": ["tuple", "set", "dict", "list"], "correct": "dict"},
    {"question": "What does 'int()' do in Python?", "choices": ["Convert to integer", "Convert to string", "Create list", "None"], "correct": "Convert to integer"}
]
random.shuffle(questions)

# --- Player setup ---
player_pos = [TILE_SIZE + 5, TOP_MARGIN + TILE_SIZE + 5]
player_speed = 4

# --- Enemy setup ---
enemy_pos = [7 * TILE_SIZE, 5 * TILE_SIZE + TOP_MARGIN]
enemy_speed = 40
enemy_dir = random.choice(["left", "right", "up", "down"])
last_enemy_move = pygame.time.get_ticks()

# --- Fonts ---
font_big = pygame.font.SysFont("arial", 36, bold=True)
font = pygame.font.SysFont("arial", 28, bold=True)
font_small = pygame.font.SysFont("arial", 22)

# --- Game variables ---
lives = 3
score = 0
TIMER_LIMIT = 30
clock = pygame.time.Clock()
question_index = 0
current_question = questions[question_index]

# --- Title Screen ---
def title_screen():
    title_font = pygame.font.SysFont("arial", 60, bold=True)
    sub_font = pygame.font.SysFont("arial", 32)
    while True:
        screen.fill(BLACK)
        title_text = title_font.render("MASID: Coding Quiz", True, YELLOW)
        subtitle_text = sub_font.render("Press ENTER to Start", True, WHITE)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//2 - 100))
        screen.blit(subtitle_text, (WIDTH//2 - subtitle_text.get_width()//2, HEIGHT//2 + 50))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return

# --- Draw maze ---
def draw_maze():
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE + TOP_MARGIN, TILE_SIZE, TILE_SIZE)
            screen.blit(floor_img if cell == 0 else wall_img, rect)

# --- Fixed can_move ---
def can_move(x, y):
    grid_x = int(x // TILE_SIZE)
    grid_y = int((y - TOP_MARGIN) // TILE_SIZE)
    if grid_y < 0 or grid_y >= len(maze) or grid_x < 0 or grid_x >= len(maze[0]):
        return False
    return maze[grid_y][grid_x] == 0

# --- Reset player ---
def reset_player():
    return [TILE_SIZE + 5, TOP_MARGIN + TILE_SIZE + 5]

# --- Spawn words ---
def spawn_words(level_data, choices):
    open_tiles = [(x, y) for y, row in enumerate(level_data) for x, v in enumerate(row) if v == 0]
    random.shuffle(open_tiles)
    words = []
    for i, choice in enumerate(choices):
        if i < len(open_tiles):
            x, y = open_tiles[i]
            words.append({"text": choice, "pos": (x * TILE_SIZE + 5, y * TILE_SIZE + TOP_MARGIN + 5)})
    return words

# --- Start game ---
title_screen()
running = True
final_win = False
start_ticks = pygame.time.get_ticks()
words = spawn_words(maze, current_question["choices"])

# --- Main Game Loop ---
while running:
    screen.fill(BLACK)
    draw_maze()

    elapsed = (pygame.time.get_ticks() - start_ticks) // 1000
    remaining = max(0, TIMER_LIMIT - elapsed)

    # --- Question bar ---
    pygame.draw.rect(screen, GRAY, (10, 10, WIDTH - 20, 60), border_radius=8)
    screen.blit(font_small.render(current_question["question"], True, YELLOW), (20, 30))
    screen.blit(font_small.render(f"Lives: {lives}", True, RED), (WIDTH - 150, 20))
    screen.blit(font_small.render(f"Time: {remaining}", True, WHITE), (WIDTH - 280, 20))
    screen.blit(font_small.render(f"Score: {score}", True, GREEN), (WIDTH - 420, 20))

    # --- Enemy Movement ---
    current_time = pygame.time.get_ticks()
    if current_time - last_enemy_move > 500:
        move_x, move_y = 0, 0
        if enemy_dir == "left": move_x = -enemy_speed
        elif enemy_dir == "right": move_x = enemy_speed
        elif enemy_dir == "up": move_y = -enemy_speed
        elif enemy_dir == "down": move_y = enemy_speed

        new_ex = enemy_pos[0] + move_x
        new_ey = enemy_pos[1] + move_y
        if can_move(new_ex, new_ey):
            enemy_pos = [new_ex, new_ey]
        else:
            enemy_dir = random.choice(["left", "right", "up", "down"])
        last_enemy_move = current_time

    screen.blit(enemy_img, enemy_pos)

    # --- Words ---
    for word in words:
        text_surface = font.render(word["text"], True, BLUE)
        bg_rect = text_surface.get_rect(topleft=word["pos"])
        pygame.draw.rect(screen, WHITE, bg_rect.inflate(10, 5), border_radius=6)
        screen.blit(text_surface, word["pos"])

    # --- Player Movement ---
    keys = pygame.key.get_pressed()
    new_x, new_y = player_pos
    if keys[pygame.K_LEFT] and can_move(new_x - player_speed, new_y): new_x -= player_speed
    if keys[pygame.K_RIGHT] and can_move(new_x + player_speed, new_y): new_x += player_speed
    if keys[pygame.K_UP] and can_move(new_x, new_y - player_speed): new_y -= player_speed
    if keys[pygame.K_DOWN] and can_move(new_x, new_y + player_speed): new_y += player_speed
    player_pos = [new_x, new_y]

    screen.blit(player_img, player_pos)

    # --- Collisions ---
    player_rect = pygame.Rect(player_pos[0], player_pos[1], TILE_SIZE-10, TILE_SIZE-10)
    enemy_rect = pygame.Rect(enemy_pos[0], enemy_pos[1], TILE_SIZE-10, TILE_SIZE-10)
    if player_rect.colliderect(enemy_rect):
        lives -= 1
        player_pos = reset_player()
        if lives <= 0:
            running = False

    for word in words[:]:
        text_rect = pygame.Rect(word["pos"][0], word["pos"][1], 80, 40)
        if player_rect.colliderect(text_rect):
            if word["text"] == current_question["correct"]:
                score += 10
                question_index += 1
                if question_index < len(questions):
                    current_question = questions[question_index]
                    player_pos = reset_player()
                    start_ticks = pygame.time.get_ticks()
                    words = spawn_words(maze, current_question["choices"])
                else:
                    final_win = True
                    running = False
                break
            else:
                lives -= 1
                words.remove(word)
                if lives <= 0:
                    running = False

    if remaining <= 0 and not final_win:
        running = False

    pygame.display.flip()
    clock.tick(60)

# --- End screen ---
screen.fill(BLACK)
if final_win:
    msg = font_big.render(f"🎉 MASID Complete! Score: {score} 🏆", True, GREEN)
else:
    msg = font_big.render(f"💀 MASID Failed! Final Score: {score}", True, RED)
msg_rect = msg.get_rect(center=(WIDTH // 2, HEIGHT // 2))
screen.blit(msg, msg_rect)
pygame.display.flip()
pygame.time.wait(3500)
pygame.quit()
