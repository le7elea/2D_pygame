import pygame
import sys
import os
import random

# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 640, 600  # Extra space at bottom for text
TILE_SIZE = 40
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Quiz Adventure")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 20, 60)
GREEN = (50, 205, 50)
BLUE = (70, 130, 180)
GRAY = (200, 200, 200)

# Load images
ASSET_PATH = os.path.join(os.path.dirname(__file__), "assets")
player_img = pygame.image.load(os.path.join(ASSET_PATH, "player.png"))
wall_img = pygame.image.load(os.path.join(ASSET_PATH, "floor.jpg"))
floor_img = pygame.image.load(os.path.join(ASSET_PATH, "wall.jpg"))
goal_img = pygame.image.load(os.path.join(ASSET_PATH, "goal.png"))

# Scale images
player_img = pygame.transform.scale(player_img, (TILE_SIZE - 10, TILE_SIZE - 10))
wall_img = pygame.transform.scale(wall_img, (TILE_SIZE, TILE_SIZE))
floor_img = pygame.transform.scale(floor_img, (TILE_SIZE, TILE_SIZE))
goal_img = pygame.transform.scale(goal_img, (TILE_SIZE, TILE_SIZE))

# Maze layouts
mazes = [
    [
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1],
        [1,0,1,0,1,0,1,0,1,1,1,1,1,1,0,1],
        [1,0,1,0,0,0,1,0,0,0,0,1,0,1,0,1],
        [1,0,1,1,1,0,1,1,1,1,0,0,0,1,0,1],
        [1,0,0,0,0,0,0,0,1,0,0,1,0,1,0,1],
        [1,1,1,1,1,1,1,0,1,1,0,1,0,1,0,1],
        [1,0,0,0,0,0,1,0,0,0,0,1,0,0,0,1],
        [1,0,1,1,1,0,1,1,1,1,1,1,1,1,0,1],
        [1,0,0,0,1,0,0,0,0,0,0,0,0,2,0,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    ],
    [
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,0,0,0,1,0,1,0,0,0,1,0,0,0,0,1],
        [1,1,1,0,1,0,1,1,1,0,1,1,1,0,1,1],
        [1,0,0,0,0,0,0,0,1,0,0,0,1,0,0,1],
        [1,0,1,1,1,1,1,0,1,1,1,0,1,1,0,1],
        [1,0,0,0,0,0,1,0,0,0,0,0,1,0,0,1],
        [1,1,1,1,1,0,1,1,1,1,1,0,1,0,1,1],
        [1,0,0,0,1,0,0,0,0,0,1,0,0,0,2,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    ]
]

# Quiz per level
questions = [
    ("What is the capital of France?", ["Paris", "Rome", "Madrid", "London"], 0),
    ("What planet is known as the Red Planet?", ["Venus", "Earth", "Mars", "Jupiter"], 2),
]

# Player setup
player_radius = TILE_SIZE // 3
player_speed = 4

def reset_player():
    return [TILE_SIZE + player_radius, TILE_SIZE + player_radius]

def draw_maze(maze):
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if cell == 1:
                screen.blit(wall_img, rect)
            elif cell == 0:
                screen.blit(floor_img, rect)
            elif cell == 2:
                screen.blit(goal_img, rect)

def can_move(maze, new_x, new_y):
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

clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 24)

level = 0
player_pos = reset_player()
lives = 3
timer = 45
time_left = timer
start_ticks = pygame.time.get_ticks()
game_over = False
won = False

while True:
    screen.fill(BLACK)
    maze = mazes[level]
    draw_maze(maze)

    # Draw player
    if not won and not game_over:
        player_rect = player_img.get_rect(center=(int(player_pos[0]), int(player_pos[1])))
        screen.blit(player_img, player_rect)

    # Timer logic
    seconds = (pygame.time.get_ticks() - start_ticks) // 1000
    time_left = max(0, timer - seconds)

    if time_left == 0:
        game_over = True

    # Movement
    keys = pygame.key.get_pressed()
    if not won and not game_over:
        new_x, new_y = player_pos
        if keys[pygame.K_LEFT] and can_move(maze, new_x - player_speed, new_y):
            new_x -= player_speed
        if keys[pygame.K_RIGHT] and can_move(maze, new_x + player_speed, new_y):
            new_x += player_speed
        if keys[pygame.K_UP] and can_move(maze, new_x, new_y - player_speed):
            new_y -= player_speed
        if keys[pygame.K_DOWN] and can_move(maze, new_x, new_y + player_speed):
            new_y += player_speed
        player_pos = [new_x, new_y]

    # Check goal
    grid_x = int(player_pos[0] // TILE_SIZE)
    grid_y = int(player_pos[1] // TILE_SIZE)
    if not won and maze[grid_y][grid_x] == 2:
        won = True

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if won and event.type == pygame.KEYDOWN:
            question, choices, correct = questions[level]
            if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                ans = int(event.key - pygame.K_1)
                if ans == correct:
                    level += 1
                    if level >= len(mazes):
                        game_over = True
                    else:
                        player_pos = reset_player()
                        won = False
                        start_ticks = pygame.time.get_ticks()
                        timer = 45
                else:
                    lives -= 1
                    if lives == 0:
                        game_over = True
                    else:
                        player_pos = reset_player()
                        won = False
                        start_ticks = pygame.time.get_ticks()

    # UI area (below maze)
    pygame.draw.rect(screen, GRAY, (0, 480, WIDTH, 120))
    pygame.draw.line(screen, BLACK, (0, 480), (WIDTH, 480), 3)

    if game_over:
        msg = "You Win!" if level >= len(mazes) and lives > 0 else "Game Over!"
        text = font.render(msg, True, RED)
        screen.blit(text, (WIDTH // 2 - 60, 500))
    elif won:
        question, choices, correct = questions[level]
        screen.blit(font.render(f"Q: {question}", True, BLUE), (20, 490))
        for i, choice in enumerate(choices):
            screen.blit(font.render(f"{i+1}. {choice}", True, WHITE), (40, 520 + i * 20))
    else:
        screen.blit(font.render(f"Lives: {lives}", True, WHITE), (20, 490))
        screen.blit(font.render(f"Time Left: {time_left}s", True, WHITE), (180, 490))
        screen.blit(font.render(f"Level: {level+1}", True, WHITE), (380, 490))

    pygame.display.flip()
    clock.tick(30)
