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
RED = (220, 50, 50)
GREEN = (0, 200, 0)
BLUE = (50, 100, 255)

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

# Questions and answers per level
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
font = pygame.font.SysFont(None, 32)

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

# Check movement
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

# Spawn answer words in open tiles
def spawn_words(level_data, choices):
    open_tiles = [(x, y) for y, row in enumerate(level_data) for x, v in enumerate(row) if v == 0]
    random.shuffle(open_tiles)
    words = []
    for i, choice in enumerate(choices):
        if i < len(open_tiles):
            x, y = open_tiles[i]
            words.append({"text": choice, "pos": (x * TILE_SIZE + 10, y * TILE_SIZE + 10)})
    return words

# Main game loop
running = True
final_win = False
start_ticks = pygame.time.get_ticks()
words = spawn_words(maze, questions[current_level]["choices"])

while running:
    screen.fill(BLACK)
    draw_maze()

    # Draw words
    for word in words:
        text_surf = font.render(word["text"], True, BLUE)
        screen.blit(text_surf, word["pos"])

    # Timer logic
    elapsed = (pygame.time.get_ticks() - start_ticks) // 1000
    remaining = max(0, TIMER_LIMIT - elapsed)

    # UI elements
    question_text = questions[current_level]["question"]
    screen.blit(font.render(question_text, True, WHITE), (20, 10))
    screen.blit(font.render(f"Lives: {lives}", True, RED), (WIDTH - 150, 10))
    screen.blit(font.render(f"Time: {remaining}", True, WHITE), (WIDTH - 280, 10))

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
        text_rect = pygame.Rect(word["pos"][0], word["pos"][1], 60, 30)
        if player_rect.colliderect(text_rect):
            if word["text"] == questions[current_level]["correct"]:
                # Correct answer → next level
                current_level += 1
                if current_level < len(levels):
                    maze = levels[current_level]
                    player_pos = reset_player()
                    start_ticks = pygame.time.get_ticks()
                    words = spawn_words(maze, questions[current_level]["choices"])
                else:
                    final_win = True
                    running = False  # Stop main loop if all levels are completed
                break
            else:
                # Wrong answer → lose life
                lives -= 1
                words.remove(word)
                if lives <= 0:
                    running = False

    # If time runs out → instant game over
    if remaining <= 0 and not final_win:
        running = False

    pygame.display.flip()
    clock.tick(30)

# --- Final screen ---
screen.fill(BLACK)

if final_win:
    # 🏆 Win screen
    win_text = font.render("🎉 You finished all coding challenges! 🏆", True, GREEN)
    screen.blit(win_text, (120, HEIGHT // 2))
else:
    # 💀 Game over screen
    over_text = font.render("⏰ Time Over or Out of Lives! Game Over!", True, RED)
    screen.blit(over_text, (120, HEIGHT // 2))

pygame.display.flip()
pygame.time.wait(3000)
pygame.quit()
