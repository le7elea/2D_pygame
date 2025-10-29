import pygame
import sys
import os
import random
import time

# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 40
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Quiz Game")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 60, 60)
GREEN = (0, 220, 0)
BLUE = (80, 150, 255)
YELLOW = (255, 220, 50)
GRAY = (50, 50, 50)

# Load images
ASSET_PATH = os.path.join(os.path.dirname(__file__), "assets")
player_img = pygame.image.load(os.path.join(ASSET_PATH, "player.png"))
wall_img = pygame.image.load(os.path.join(ASSET_PATH, "wall.jpg"))
floor_img = pygame.image.load(os.path.join(ASSET_PATH, "floor.jpg"))

player_img = pygame.transform.scale(player_img, (TILE_SIZE - 10, TILE_SIZE - 10))
wall_img = pygame.transform.scale(wall_img, (TILE_SIZE, TILE_SIZE))
floor_img = pygame.transform.scale(floor_img, (TILE_SIZE, TILE_SIZE))

# Maze levels
levels = [
    [  # Level 1
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
    ],
    [  # Level 2
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,0,0,1,0,0,0,0,1,0,0,0,0,1,0,1],
        [1,0,1,0,1,1,1,0,1,0,1,1,0,1,0,1],
        [1,0,1,0,0,0,1,0,1,0,0,0,0,1,0,1],
        [1,0,1,1,1,0,1,1,1,1,1,1,0,1,0,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1],
        [1,1,1,1,1,1,1,0,1,1,1,1,0,1,0,1],
        [1,0,0,0,0,0,1,0,0,0,0,1,0,0,0,1],
        [1,0,1,1,1,0,1,1,1,1,1,1,1,1,0,1],
        [1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    ]
]

# Questions per level
questions = [
    {
        "question": "What is the output of: print(2 + 3 * 2)?",
        "choices": ["10", "8", "12", "5"],
        "correct": "8"
    },
    {
        "question": "Which data type is immutable in Python?",
        "choices": ["list", "set", "tuple", "dict"],
        "correct": "tuple"
    }
]

current_level = 0
maze = levels[current_level]

# Player setup
player_radius = TILE_SIZE // 3
player_pos = [TILE_SIZE + player_radius, TILE_SIZE + player_radius]
player_speed = 4
font_big = pygame.font.SysFont("arial", 36, bold=True)
font = pygame.font.SysFont("arial", 28, bold=True)
font_small = pygame.font.SysFont("arial", 22)

# Game variables
lives = 3
TIMER_LIMIT = 30
clock = pygame.time.Clock()

# Helper: Draw maze
def draw_maze():
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if cell == 1:
                screen.blit(wall_img, rect)
            else:
                screen.blit(floor_img, rect)

# Movement checker
def can_move(new_x, new_y):
    points = [
        (new_x - player_radius, new_y - player_radius),
        (new_x + player_radius, new_y - player_radius),
        (new_x - player_radius, new_y + player_radius),
        (new_x + player_radius, new_y + player_radius),
    ]
    for px, py in points:
        grid_x = int(px // TILE_SIZE)
        grid_y = int(py // TILE_SIZE)
        if grid_x < 0 or grid_y < 0 or grid_y >= len(maze) or grid_x >= len(maze[0]):
            return False
        if maze[grid_y][grid_x] == 1:
            return False
    return True

# Reset player
def reset_player():
    return [TILE_SIZE + player_radius, TILE_SIZE + player_radius]

# Spawn answers randomly
def spawn_words(level_data, choices):
    open_tiles = [(x, y) for y, row in enumerate(level_data) for x, v in enumerate(row) if v == 0]
    random.shuffle(open_tiles)
    words = []
    for i, choice in enumerate(choices):
        if i < len(open_tiles):
            x, y = open_tiles[i]
            words.append({"text": choice, "pos": (x * TILE_SIZE + 5, y * TILE_SIZE + 5)})
    return words

# Main game loop
running = True
final_win = False
start_ticks = pygame.time.get_ticks()
words = spawn_words(maze, questions[current_level]["choices"])

while running:
    screen.fill(BLACK)
    draw_maze()

    # Timer
    elapsed = (pygame.time.get_ticks() - start_ticks) // 1000
    remaining = max(0, TIMER_LIMIT - elapsed)

    # Question box
    pygame.draw.rect(screen, GRAY, (10, 5, WIDTH - 20, 60), border_radius=8)
    screen.blit(font_small.render(questions[current_level]["question"], True, YELLOW), (20, 20))

    # UI
    screen.blit(font_small.render(f"Lives: {lives}", True, RED), (WIDTH - 150, 15))
    screen.blit(font_small.render(f"Time: {remaining}", True, WHITE), (WIDTH - 280, 15))

    # Draw answers
    for word in words:
        text_surface = font.render(word["text"], True, BLUE)
        bg_rect = text_surface.get_rect(topleft=word["pos"])
        pygame.draw.rect(screen, WHITE, bg_rect.inflate(10, 5), border_radius=6)
        screen.blit(text_surface, word["pos"])

    # Player
    player_rect = player_img.get_rect(center=(int(player_pos[0]), int(player_pos[1])))
    screen.blit(player_img, player_rect)

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Movement
    keys = pygame.key.get_pressed()
    new_x, new_y = player_pos
    if keys[pygame.K_LEFT] and can_move(new_x - player_speed, new_y):
        new_x -= player_speed
    if keys[pygame.K_RIGHT] and can_move(new_x + player_speed, new_y):
        new_x += player_speed
    if keys[pygame.K_UP] and can_move(new_x, new_y - player_speed):
        new_y -= player_speed
    if keys[pygame.K_DOWN] and can_move(new_x, new_y + player_speed):
        new_y += player_speed
    player_pos = [new_x, new_y]

    # Word collision check
    player_rect = pygame.Rect(player_pos[0]-15, player_pos[1]-15, 30, 30)
    for word in words[:]:
        text_rect = pygame.Rect(word["pos"][0], word["pos"][1], 80, 40)
        if player_rect.colliderect(text_rect):
            if word["text"] == questions[current_level]["correct"]:
                current_level += 1
                if current_level < len(levels):
                    maze = levels[current_level]
                    player_pos = reset_player()
                    start_ticks = pygame.time.get_ticks()
                    words = spawn_words(maze, questions[current_level]["choices"])
                else:
                    final_win = True
                    running = False
                break
            else:
                lives -= 1
                words.remove(word)
                if lives <= 0:
                    running = False

    # Time out = Game over
    if remaining <= 0 and not final_win:
        running = False

    pygame.display.flip()
    clock.tick(30)

# --- End screen ---
screen.fill(BLACK)
if final_win:
    msg = font_big.render("🎉 You finished all coding challenges! 🏆", True, GREEN)
else:
    msg = font_big.render("💀 Time’s Up or Out of Lives! Game Over!", True, RED)

msg_rect = msg.get_rect(center=(WIDTH // 2, HEIGHT // 2))
screen.blit(msg, msg_rect)
pygame.display.flip()
pygame.time.wait(3500)
pygame.quit()
