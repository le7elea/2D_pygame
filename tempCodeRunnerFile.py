import pygame
import random
import sys
from collections import deque
import os

# --- Initialize Pygame ---
pygame.init()
pygame.mixer.init()

# --- Screen setup ---
WIDTH, HEIGHT = 800, 640
HUD_HEIGHT = 80
GAME_HEIGHT = HEIGHT - HUD_HEIGHT
TILE_SIZE = 40
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("MASID: Maze")

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (10, 10, 20)
RED = (220, 20, 60)
YELLOW = (255, 215, 0)
GREEN = (0, 200, 0)
BLUE = (0, 120, 255)
LIGHT_BLUE = (100, 180, 255)
DARK = (30, 30, 40)
PURPLE = (180, 70, 220)
ORANGE = (255, 165, 0)

# --- Font ---
font = pygame.font.SysFont("arial", 28)

# --- Directions ---
DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]

# --- Global variable for total coins ---
total_coins = 0

# --- Character Selection ---
selected_character = "character01"  # Default character
character_frames = {
    "character01": "frame1.png",
    "character02": "frame2.png",
    "character03": "frame3.png",
    "character04": "frame4.png",
    "character05": "frame5.png",
    "character06": "frame6.png",
    "character07": "frame7.png",
    "character08": "frame8.png",
    
}
character_names = {
    "character01": "Aetherius",
    "character02": "Solara",
    "character03": "Dino",
    "character04": "Orion",
    "character05": "Santa",
    "character06": "Luna",
    "character07": "Zephyr",
    "character08": "Nebula",
}

# --- Quiz configuration ---
# Changed to quiz every 2 levels starting from level 2
def should_quiz(level):
    return level >= 2 and level % 2 == 0

quiz_questions = [
    {"question": "What is the main purpose of Pygame?",
     "choices": ["Web development", "Game development", "Database management", "Data analysis"],
     "answer": 1},
    {"question": "Which function initializes all Pygame modules?",
     "choices": ["pygame.start()", "pygame.init()", "pygame.run()", "pygame.load()"],
     "answer": 1},
    {"question": "Which Pygame method is used to create the game window?",
     "choices": ["pygame.display.set_mode()", "pygame.window()", "pygame.screen()", "pygame.create_window()"],
     "answer": 0},
    {"question": "Which Pygame module handles sounds?",
     "choices": ["pygame.display", "pygame.mixer", "pygame.sprite", "pygame.event"],
     "answer": 1},
    {"question": "How do you detect key presses in Pygame?",
     "choices": ["pygame.key.get_pressed()", "pygame.mouse.get_pos()", "pygame.event.detect()", "pygame.key.down()"],
     "answer": 0},
    {"question": "Which method updates the full display in Pygame?",
     "choices": ["pygame.flip()", "pygame.update()", "pygame.draw()", "pygame.refresh()"],
     "answer": 0},
    {"question": "Which object is used to manage game framerate in Pygame?",
     "choices": ["pygame.Clock()", "pygame.Timer()", "pygame.FPS()", "pygame.Loop()"],
     "answer": 0},
    {"question": "What is the purpose of pygame.Surface?",
     "choices": ["Store images and graphics", "Handle sound playback", "Manage input events", "Control game clock"],
     "answer": 0},
    {"question": "Which Pygame method draws a rectangle?",
     "choices": ["pygame.draw.rect()", "pygame.rect.draw()", "pygame.make.rect()", "pygame.rect()"],
     "answer": 0},
    {"question": "How do you play a sound in Pygame?",
     "choices": ["sound.play()", "pygame.sound()", "pygame.mixer.play()", "sound.start()"],
     "answer": 0},
    {"question": "What does blit() do in Pygame?",
     "choices": ["Play a sound", "Draw one image onto another", "Detect collisions", "Handle events"],
     "answer": 1},
    {"question": "Which event type is used for quitting the game?",
     "choices": ["pygame.QUIT", "pygame.EXIT", "pygame.CLOSE", "pygame.END"],
     "answer": 0},
    {"question": "How do you set the caption of the game window?",
     "choices": ["pygame.set_caption()", "pygame.display.set_caption()", "pygame.window.set_title()", "pygame.title()"],
     "answer": 1},
    {"question": "What is the purpose of pygame.Rect?",
     "choices": ["Store sound data", "Represent rectangular areas", "Manage game states", "Handle file I/O"],
     "answer": 1},
    {"question": "Which method checks for collision between two rectangles?",
     "choices": ["rect.collide()", "rect.colliderect()", "rect.intersect()", "rect.overlap()"],
     "answer": 1},
]

# --- Load Sprites ---
def load_sprite(name, size):
    try:
        img = pygame.image.load(f"assets/{name}").convert_alpha()
        return pygame.transform.scale(img, (size, size))
    except Exception:
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        surf.fill((100, 100, 100))
        return surf

# --- Load walking animation frames ---
def load_walk_sprites(sheet_name, frame_count, size):
    try:
        sheet = pygame.image.load(f"assets/{sheet_name}").convert_alpha()
        frames = []
        frame_width = sheet.get_width() // frame_count
        frame_height = sheet.get_height()
        for i in range(frame_count):
            frame = sheet.subsurface(i * frame_width, 0, frame_width, frame_height)
            frames.append(pygame.transform.scale(frame, (size, size)))
        return frames
    except Exception:
        # fallback single frame if sheet missing
        return [pygame.Surface((size, size))]

# --- Load character preview with animation ---
def load_character_preview(character_name, size, frame_index=0):
    """Load a specific frame from character's sprite sheet for preview"""
    frame_sheet = character_frames[character_name]
    try:
        sheet = pygame.image.load(f"assets/{frame_sheet}").convert_alpha()
        frame_width = sheet.get_width() // 8  # Assuming 8 frames per sheet
        frame_height = sheet.get_height()
        frame = sheet.subsurface(frame_index * frame_width, 0, frame_width, frame_height)
        return pygame.transform.scale(frame, (size, size))
    except Exception:
        # fallback if sheet missing
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        color = GREEN if character_name == "character01" else PURPLE
        surf.fill(color)
        return surf

# --- Global variables to preserve maze state ---
level1_maze = None
level1_coins = None
level1_items = None
level1_enemies = None
level1_exit_pos = None

# --- Create actual level 1 maze backdrop for NPC intro ---
def create_level1_maze_backdrop():
    """Create the exact same maze that will be used in level 1 as backdrop"""
    global level1_maze, level1_coins, level1_items, level1_enemies, level1_exit_pos
    
    # Use the same parameters as level 1
    tile_size = TILE_SIZE
    rows, cols = GAME_HEIGHT // tile_size, WIDTH // tile_size
    
    # Generate the exact same maze that will be used in play_level(1, lives)
    maze = generate_maze(rows, cols)
    player_pos = [1, 1]
    exit_pos = [cols - 3, rows - 3]
    maze[exit_pos[1]][exit_pos[0]] = 0
    
    # Store the maze and game elements globally so they can be reused
    level1_maze = maze
    level1_exit_pos = exit_pos
    
    # Generate coins for level 1
    level1_coins = random.sample([(x, y) for y in range(rows) for x in range(cols) if maze[y][x] == 0],
                                min(1 + 3, 20))  # level 1: min(level + 3, 20)
    
    # Generate items for level 1
    collectible_count = min(3 + 1, 8)  # level 1: min(3 + level, 8)
    level1_items = random.sample([(x, y) for y in range(rows) for x in range(cols) if maze[y][x] == 0],
                                collectible_count)
    
    # Generate enemies for level 1
    level1_enemies = []
    for _ in range(min(1 + 1, 6)):  # level 1: min(level + 1, 6)
        ex, ey = random.randint(3, cols - 3), random.randint(3, rows - 3)
        if maze[ey][ex] == 0:
            level1_enemies.append([ex, ey])
    
    # Create a surface for the maze backdrop
    backdrop = pygame.Surface((WIDTH, HEIGHT))
    
    # Fill with level 1 background
    try:
        background = pygame.image.load("assets/level5.png").convert()  # level1 background
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
        backdrop.blit(background, (0, 0))
    except Exception:
        backdrop.fill((20, 20, 40))
    
    # Draw the exact same maze that will appear in level 1
    glow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for y in range(rows):
        for x in range(cols):
            if maze[y][x] == 1:
                cx = x * tile_size + tile_size // 2
                cy = y * tile_size + tile_size // 2 + HUD_HEIGHT
                for dx, dy in [(1, 0), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < cols and 0 <= ny < rows and maze[ny][nx] == 1:
                        nx_pos = nx * tile_size + tile_size // 2
                        ny_pos = ny * tile_size + tile_size // 2 + HUD_HEIGHT
                        pygame.draw.line(glow_surface, (0, 180, 255, 80), (cx, cy), (nx_pos, ny_pos), 6)
                        pygame.draw.line(glow_surface, (0, 220, 255, 150), (cx, cy), (nx_pos, ny_pos), 2)
    
    backdrop.blit(glow_surface, (0, 0))
    
    # Add the exact same game elements that will appear in level 1
    # Draw exit (faded)
    try:
        exit_img = load_sprite("gameDoor1.png", tile_size)
        exit_img.set_alpha(150)
        backdrop.blit(exit_img, (exit_pos[0]*tile_size, exit_pos[1]*tile_size + HUD_HEIGHT))
    except: pass
    
    # Draw player starting position (faded)
    try:
        player_img = load_character_preview(selected_character, tile_size)
        player_img.set_alpha(120)
        backdrop.blit(player_img, (player_pos[0]*tile_size, player_pos[1]*tile_size + HUD_HEIGHT))
    except: pass
    
    # Draw coins (faded)
    try:
        coin_img = load_sprite("coinss.png", tile_size)
        coin_img.set_alpha(100)
        for coin in level1_coins:
            backdrop.blit(coin_img, (coin[0]*tile_size, coin[1]*tile_size + HUD_HEIGHT))
    except: pass
    
    # Draw items (faded)
    try:
        item_img = load_sprite("key.png", tile_size)
        item_img.set_alpha(100)
        for item in level1_items:
            backdrop.blit(item_img, (item[0]*tile_size, item[1]*tile_size + HUD_HEIGHT))
    except: pass
    
    # Draw enemies (faded)
    try:
        enemy_img = load_sprite("enemy.png", tile_size)
        enemy_img.set_alpha(100)
        for enemy in level1_enemies:
            backdrop.blit(enemy_img, (enemy[0]*tile_size, enemy[1]*tile_size + HUD_HEIGHT))
    except: pass
    
    # Apply dark overlay for blur effect
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(100)  # Less dark so maze is more visible
    backdrop.blit(overlay, (0, 0))
    
    return backdrop

# --- NPC Intro at Level 1 with actual level 1 maze backdrop ---
def npc_intro_level1():
    clock = pygame.time.Clock()
    npc_img = load_sprite("npc.png", 150)
    
    # Create the exact level 1 maze backdrop
    maze_backdrop = create_level1_maze_backdrop()
    
    tips = [
        "Hi there, adventurer! Welcome to MASID: MIND MAZE!",
        "This is the actual maze you'll be exploring.",
        "Find your way from the start to the exit door.",
        "Collect all the keys to unlock the exit.",
        "Grab coins along the way for extra points.",
        "Use arrow keys to move through the maze.",
        "Avoid enemies - they'll cost you lives!",
        "Press A/S/W/D to shoot projectiles at enemies.",
        "Keep your mind sharp for Pygame tips that help with quizzes.",
        "Quizzes appear every 2 levels starting from level 2!",
        "Timer starts from Level 5 - be quick!",
        "Good luck! This is the real Level 1 maze ahead!"
    ]

    bubble_width, bubble_height = 500, 100
    bubble_x, bubble_y = 200, HEIGHT//2 - bubble_height//2
    font_small = pygame.font.SysFont("arial", 24)

    current_tip = 0
    total_tips = len(tips)

    while current_tip < total_tips:
        # Draw the actual level 1 maze backdrop
        screen.blit(maze_backdrop, (0, 0))
        
        # Add title
        title_font = pygame.font.SysFont("arial", 36, bold=True)
        title = title_font.render("Quick  Tutorial", True, LIGHT_BLUE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))
        

        # Draw NPC
        screen.blit(npc_img, (50, HEIGHT//2 - npc_img.get_height()//2))

        if current_tip < total_tips:
            # Speech bubble
            pygame.draw.rect(screen, (255, 255, 255), (bubble_x, bubble_y, bubble_width, bubble_height), border_radius=16)
            pygame.draw.rect(screen, LIGHT_BLUE, (bubble_x, bubble_y, bubble_width, bubble_height), 3, border_radius=16)

            # Speech bubble tail
            tail_points = [(bubble_x - 10, bubble_y + 20), (bubble_x, bubble_y + 40), (bubble_x, bubble_y + 20)]
            pygame.draw.polygon(screen, (255, 255, 255), tail_points)
            pygame.draw.polygon(screen, LIGHT_BLUE, tail_points, 2)

            # Tip text
            tip_text = font_small.render(tips[current_tip], True, BLACK)
            screen.blit(tip_text, (bubble_x + 20, bubble_y + bubble_height//2 - tip_text.get_height()//2))

            # Continue prompt
            continue_font = pygame.font.SysFont("arial", 20)
            continue_text = continue_font.render("Press any key or click to continue...", True, YELLOW)
            screen.blit(continue_text, (WIDTH//2 - continue_text.get_width()//2, HEIGHT - 80))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                current_tip += 1

        clock.tick(30)

# --- Start Menu with Character Selection ---
def start_menu():
    global selected_character
    
    try:
        bg = pygame.image.load("assets/startback.png").convert()
        bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
    except Exception:
        bg = pygame.Surface((WIDTH, HEIGHT))
        bg.fill(DARK)

    # Character list and current index
    character_list = list(character_frames.keys())
    current_char_index = 0
    
    # Buttons - positioned lower
    start_btn = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 100, 200, 50)  # Moved down
    quit_btn = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 170, 200, 50)   # Moved down
    left_arrow = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 40, 50, 50)   # Positioned lower
    right_arrow = pygame.Rect(WIDTH//2 + 100, HEIGHT//2 - 40, 50, 50)  # Positioned lower
    
    high_level = load_highscore()
    high_font = pygame.font.SysFont("arial", 28, bold=True)
    
    # Animation variables
    animation_timer = 0
    frame_index = 0
    
    clock = pygame.time.Clock()
    
    while True:
        screen.blit(bg, (0, 0))
        mouse = pygame.mouse.get_pos()
        
        # Update animation
        animation_timer += 1
        if animation_timer >= 10:  # Change frame every 10 frames
            frame_index = (frame_index + 1) % 8
            animation_timer = 0
        
        current_character = character_list[current_char_index]
        selected_character = current_character
        
        # Character display area - smaller and positioned lower
        char_display_rect = pygame.Rect(WIDTH//2 - 70, HEIGHT//2 - 120, 140, 140)  # Smaller: 140x140, positioned lower
        pygame.draw.rect(screen, DARK, char_display_rect, border_radius=10)
        pygame.draw.rect(screen, LIGHT_BLUE, char_display_rect, 3, border_radius=10)
        
        # Character preview - smaller size
        char_preview = load_character_preview(current_character, 90, frame_index)  # 90px instead of 100px
        screen.blit(char_preview, (char_display_rect.centerx - char_preview.get_width()//2, 
                                 char_display_rect.centery - char_preview.get_height()//2))
        
        # Character name - PERFECTLY CENTERED IN RECTANGLE
        name_bg_width = 200
        name_bg_height = 40
        name_bg_rect = pygame.Rect(WIDTH//2 - name_bg_width//2, char_display_rect.bottom + 5, name_bg_width, name_bg_height)
        pygame.draw.rect(screen, DARK, name_bg_rect, border_radius=8)
        pygame.draw.rect(screen, LIGHT_BLUE, name_bg_rect, 2, border_radius=8)
        
        char_name = font.render(character_names[current_character], True, YELLOW)
        # Center the text both horizontally and vertically within the name_bg_rect
        name_x = name_bg_rect.centerx - char_name.get_width()//2
        name_y = name_bg_rect.centery - char_name.get_height()//2
        screen.blit(char_name, (name_x, name_y))
        
        # Navigation arrows - positioned around the smaller box
        left_color = GREEN if left_arrow.collidepoint(mouse) else BLUE
        right_color = GREEN if right_arrow.collidepoint(mouse) else BLUE
        
        pygame.draw.rect(screen, left_color, left_arrow, border_radius=8)
        pygame.draw.rect(screen, right_color, right_arrow, border_radius=8)
        
        left_text = font.render("←", True, WHITE)
        right_text = font.render("→", True, WHITE)
        screen.blit(left_text, (left_arrow.centerx - left_text.get_width()//2, left_arrow.centery - left_text.get_height()//2))
        screen.blit(right_text, (right_arrow.centerx - right_text.get_width()//2, right_arrow.centery - right_text.get_height()//2))
        
        # Navigation hint - MOVED UPWARD (from +10 to -5)
        nav_hint = font.render("Use arrows to change character", True, YELLOW)
        screen.blit(nav_hint, (WIDTH//2 - nav_hint.get_width()//2, name_bg_rect.bottom - 5))
        
        # Start button - positioned lower
        start_color = GREEN if start_btn.collidepoint(mouse) else BLUE
        pygame.draw.rect(screen, start_color, start_btn, border_radius=12)
        start_text = font.render("Start Game", True, WHITE)
        screen.blit(start_text, (start_btn.centerx - start_text.get_width()//2, start_btn.centery - start_text.get_height()//2))
        
        # Quit button - positioned lower
        quit_color = RED if quit_btn.collidepoint(mouse) else (200, 60, 60)
        pygame.draw.rect(screen, quit_color, quit_btn, border_radius=12)
        quit_text = font.render("Quit Game", True, WHITE)
        screen.blit(quit_text, (quit_btn.centerx - quit_text.get_width()//2, quit_btn.centery - quit_text.get_height()//2))
        
        # High score - adjusted position
        high_text = high_font.render(f"🏆 Highest Level: {high_level}", True, YELLOW)
        shadow = high_font.render(f"🏆 Highest Level: {high_level}", True, (150, 120, 0))
        screen.blit(shadow, (WIDTH//2 - shadow.get_width()//2, quit_btn.bottom + 22))
        screen.blit(high_text, (WIDTH//2 - high_text.get_width()//2, quit_btn.bottom + 20))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_btn.collidepoint(mouse):
                    return  # Start the game
                elif quit_btn.collidepoint(mouse):
                    pygame.quit(); sys.exit()
                elif left_arrow.collidepoint(mouse):
                    current_char_index = (current_char_index - 1) % len(character_list)
                elif right_arrow.collidepoint(mouse):
                    current_char_index = (current_char_index + 1) % len(character_list)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_char_index = (current_char_index - 1) % len(character_list)
                elif event.key == pygame.K_RIGHT:
                    current_char_index = (current_char_index + 1) % len(character_list)
                elif event.key == pygame.K_RETURN:
                    return  # Start the game
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
        
        pygame.display.flip()
        clock.tick(30)

def generate_maze(rows, cols):
    maze = [[1 for _ in range(cols)] for _ in range(rows)]
    stack = [(1, 1)]
    maze[1][1] = 0
    while stack:
        x, y = stack[-1]
        neighbors = []
        for dx, dy in DIRS:
            nx, ny = x + dx * 2, y + dy * 2
            if 1 <= nx < cols - 1 and 1 <= ny < rows - 1 and maze[ny][nx] == 1:
                neighbors.append((nx, ny))
        if neighbors:
            nx, ny = random.choice(neighbors)
            maze[y + (ny - y)//2][x + (nx - x)//2] = 0
            maze[ny][nx] = 0
            stack.append((nx, ny))
        else:
            stack.pop()
    return maze

def draw_maze(maze, tile_size):
    glow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    rows, cols = len(maze), len(maze[0])
    for y in range(rows):
        for x in range(cols):
            if maze[y][x] == 1:
                cx = x * tile_size + tile_size // 2
                cy = y * tile_size + tile_size // 2 + HUD_HEIGHT
                for dx, dy in [(1, 0), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < cols and 0 <= ny < rows and maze[ny][nx] == 1:
                        nx_pos = nx * tile_size + tile_size // 2
                        ny_pos = ny * tile_size + tile_size // 2 + HUD_HEIGHT
                        pygame.draw.line(glow_surface, (0, 180, 255, 100), (cx, cy), (nx_pos, ny_pos), 6)
                        pygame.draw.line(glow_surface, (0, 220, 255, 255), (cx, cy), (nx_pos, ny_pos), 2)
    screen.blit(glow_surface, (0, 0))

def pause_menu():
    paused = True
    action = "resume"
    while paused:
        screen.fill((20, 20, 20))
        label = font.render("⏸ Game Paused", True, LIGHT_BLUE)
        resume_text = font.render("▶ Resume (ESC/R)", True, GREEN)
        quit_text = font.render("❌ Quit to Menu (Q)", True, RED)
        screen.blit(label, (WIDTH//2 - label.get_width()//2, HEIGHT//2 - 100))
        screen.blit(resume_text, (WIDTH//2 - resume_text.get_width()//2, HEIGHT//2))
        screen.blit(quit_text, (WIDTH//2 - quit_text.get_width()//2, HEIGHT//2 + 60))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_r):
                    paused = False
                    action = "resume"
                elif event.key == pygame.K_q:
                    paused = False
                    action = "quit"
    return action

def quiz_screen(level, lives):
    clock = pygame.time.Clock()
    question = random.choice(quiz_questions)
    choices = question["choices"]
    correct_idx = question["answer"]

    button_w = 560
    button_h = 56
    start_x = WIDTH//2 - button_w//2
    start_y = 220
    buttons = [pygame.Rect(start_x, start_y + i*(button_h + 16), button_w, button_h) for i in range(len(choices))]

    # Load startback.png as background
    try:
        bg = pygame.image.load("assets/startback.png").convert()
        bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
    except Exception:
        bg = pygame.Surface((WIDTH, HEIGHT))
        bg.fill(DARK)

    # Timer setup
    quiz_time_limit = 60 
    start_ticks = pygame.time.get_ticks()
    
    while True:
        # Calculate remaining time
        elapsed_seconds = (pygame.time.get_ticks() - start_ticks) // 1000
        time_remaining = max(0, quiz_time_limit - elapsed_seconds)
        
        # Check if time's up
        if time_remaining <= 0:
            lives -= 1
            # Time's up feedback
            feedback_bg = pygame.Surface((500, 80), pygame.SRCALPHA)
            feedback_bg.fill((80, 40, 0, 200))
            screen.blit(feedback_bg, (WIDTH//2 - 250, HEIGHT//2 - 40))
            timeout_msg = font.render("⏰ Time's up! -1 Life", True, ORANGE)
            screen.blit(timeout_msg, (WIDTH//2 - timeout_msg.get_width()//2, HEIGHT//2 - 10))
            pygame.display.flip()
            pygame.time.delay(1500)
            return lives, False

        # Use startback.png as background
        screen.blit(bg, (0, 0))
        
        # Add a darker overlay to make content more visible
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)  # Darker overlay for better contrast
        screen.blit(overlay, (0, 0))
        
        # Main content container with semi-transparent background
        content_rect = pygame.Rect(WIDTH//2 - 300, 40, 600, HEIGHT - 120)
        content_bg = pygame.Surface((content_rect.width, content_rect.height), pygame.SRCALPHA)
        content_bg.fill((30, 30, 40, 220))  # Semi-transparent dark background
        screen.blit(content_bg, content_rect)
        
        # Add border to content area
        pygame.draw.rect(screen, LIGHT_BLUE, content_rect, 3, border_radius=12)
        
        # Timer display (color changes as time runs out)
        timer_color = GREEN if time_remaining > 30 else YELLOW if time_remaining > 10 else RED
        timer_text = font.render(f"⏱ {time_remaining}s", True, timer_color)
        screen.blit(timer_text, (WIDTH - 120, 60))
        
        title = font.render(f"🧩 Quiz — Level {level}", True, YELLOW)
        q_font = pygame.font.SysFont("arial", 24)
        q_text = q_font.render(question["question"], True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 60))
        screen.blit(q_text, (WIDTH//2 - q_text.get_width()//2, 140))

        mx, my = pygame.mouse.get_pos()
        for i, rect in enumerate(buttons):
            hovered = rect.collidepoint((mx, my))
            # More opaque buttons for better visibility
            color = (40, 60, 100, 240) if not hovered else (60, 100, 180, 240)
            
            # Create button surface with shadow
            button_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(button_surface, color, (0, 0, rect.width, rect.height), border_radius=10)
            
            # Add button border
            border_color = LIGHT_BLUE if hovered else BLUE
            pygame.draw.rect(button_surface, border_color, (0, 0, rect.width, rect.height), 2, border_radius=10)
            
            screen.blit(button_surface, rect)
            
            ans_text = q_font.render(f"{chr(65+i)}. {choices[i]}", True, WHITE)
            screen.blit(ans_text, (rect.x + 20, rect.centery - ans_text.get_height()//2))

        # Instruction text with better visibility
        info_bg = pygame.Surface((WIDTH - 100, 40), pygame.SRCALPHA)
        info_bg.fill((0, 0, 0, 150))
        screen.blit(info_bg, (50, HEIGHT - 70))
        
        info = font.render("Click an answer or press A/B/C/D (or 1/2/3/4). Time limit: 60s", True, YELLOW)
        screen.blit(info, (WIDTH//2 - info.get_width()//2, HEIGHT - 60))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(buttons):
                    if rect.collidepoint(event.pos):
                        if i == correct_idx:
                            # Success feedback with better visibility
                            feedback_bg = pygame.Surface((400, 80), pygame.SRCALPHA)
                            feedback_bg.fill((0, 50, 0, 200))
                            screen.blit(feedback_bg, (WIDTH//2 - 200, HEIGHT//2 - 40))
                            ok = font.render("✅ Correct! Proceeding to next level...", True, GREEN)
                            screen.blit(ok, (WIDTH//2 - ok.get_width()//2, HEIGHT//2 - 10))
                            pygame.display.flip()
                            pygame.time.delay(1200)
                            return lives, True
                        else:
                            lives -= 1
                            # Error feedback with better visibility
                            feedback_bg = pygame.Surface((400, 80), pygame.SRCALPHA)
                            feedback_bg.fill((50, 0, 0, 200))
                            screen.blit(feedback_bg, (WIDTH//2 - 200, HEIGHT//2 - 40))
                            wrong = font.render("❌ Wrong! -1 Life", True, RED)
                            screen.blit(wrong, (WIDTH//2 - wrong.get_width()//2, HEIGHT//2 - 10))
                            pygame.display.flip()
                            pygame.time.delay(1200)
                            return lives, False
            if event.type == pygame.KEYDOWN:
                key_to_idx = {
                    pygame.K_a: 0, pygame.K_b: 1, pygame.K_c: 2, pygame.K_d: 3,
                    pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2, pygame.K_4: 3,
                    pygame.K_KP1: 0, pygame.K_KP2: 1, pygame.K_KP3: 2, pygame.K_KP4: 3
                }
                if event.key in key_to_idx:
                    i = key_to_idx[event.key]
                    if i < len(choices):
                        if i == correct_idx:
                            feedback_bg = pygame.Surface((400, 80), pygame.SRCALPHA)
                            feedback_bg.fill((0, 50, 0, 200))
                            screen.blit(feedback_bg, (WIDTH//2 - 200, HEIGHT//2 - 40))
                            ok = font.render("✅ Correct! Proceeding to next level...", True, GREEN)
                            screen.blit(ok, (WIDTH//2 - ok.get_width()//2, HEIGHT//2 - 10))
                            pygame.display.flip()
                            pygame.time.delay(1200)
                            return lives, True
                        else:
                            lives -= 1
                            feedback_bg = pygame.Surface((400, 80), pygame.SRCALPHA)
                            feedback_bg.fill((50, 0, 0, 200))
                            screen.blit(feedback_bg, (WIDTH//2 - 200, HEIGHT//2 - 40))
                            wrong = font.render("❌ Wrong! -1 Life", True, RED)
                            screen.blit(wrong, (WIDTH//2 - wrong.get_width()//2, HEIGHT//2 - 10))
                            pygame.display.flip()
                            pygame.time.delay(1200)
                            return lives, False

        clock.tick(30)

def save_highscore(level):
    try:
        with open("highscore.txt", "r") as f:
            current = int(f.read())
        if level > current:
            with open("highscore.txt", "w") as f:
                f.write(str(level))
    except Exception:
        with open("highscore.txt", "w") as f:
            f.write(str(level))

def load_highscore():
    if os.path.exists("highscore.txt"):
        try:
            with open("highscore.txt", "r") as f:
                return int(f.read())
        except Exception:
            return 1
    return 1

def play_level(level, lives):
    global total_coins, selected_character
    global level1_maze, level1_coins, level1_items, level1_enemies, level1_exit_pos
    
    clock = pygame.time.Clock()
    tile_size = max(20, TILE_SIZE - (level - 1) * 3)
    rows, cols = GAME_HEIGHT // tile_size, WIDTH // tile_size

    # --- Background & Sprites ---
    background = pygame.image.load(f"assets/level{(level - 1) % 4 + 5}.png").convert()
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    
    # Load character-specific animation frames using the same method
    frame_sheet = character_frames[selected_character]
    player_walk_frames = load_walk_sprites(frame_sheet, 8, tile_size)
    player_frame_index = 0
    player_last_update = pygame.time.get_ticks()
    animation_speed = 150
    current_player_img = player_walk_frames[0]

    coin_img = load_sprite("coinss.png", tile_size)
    exit_img = load_sprite("gameDoor1.png", tile_size)
    exit_img = pygame.transform.scale(exit_img, (int(tile_size * 1.0), int(tile_size * 1.0)))
    enemy_img = load_sprite("enemy.png", tile_size)
    item_img = load_sprite("key.png", tile_size)

    # --- Projectile Setup ---
    projectile_img = load_sprite("projectile01.png", int(tile_size * 0.6))
    projectiles = []  # list of [pixel_x, pixel_y, dir_x, dir_y]
    last_shot_time = 0
    shot_cooldown = 400  # milliseconds

    # --- Sounds (safe load) ---
    try:
        coin_sound = pygame.mixer.Sound("assets/coin.mp3")
    except Exception:
        coin_sound = None
    try:
        bump_sound = pygame.mixer.Sound("assets/bump.mp3")
    except Exception:
        bump_sound = None
    try:
        item_sound = pygame.mixer.Sound("assets/item.mp3")
    except Exception:
        item_sound = None
    try:
        shoot_sound = pygame.mixer.Sound("assets/shoot.wav")
    except Exception:
        shoot_sound = None

    # --- Items & Tips ---
    item_tips = [
        "Tip: Pygame is used for game development.",
        "Tip: Initialize Pygame with pygame.init().",
        "Tip: Create a window using pygame.display.set_mode().",
        "Tip: Play sounds using pygame.mixer module.",
        "Tip: Detect key presses with pygame.key.get_pressed().",
        "Tip: Update the display with pygame.display.flip().",
        "Tip: Control framerate using pygame.Clock().",
        "Tip: pygame.Surface stores images and graphics.",
        "Tip: Draw rectangles with pygame.draw.rect().",
        "Tip: Play a sound with sound.play().",
        "Tip: Use blit() to draw images onto surfaces.",
        "Tip: pygame.QUIT event is used for quitting the game.",
        "Tip: Set window caption with pygame.display.set_caption().",
        "Tip: pygame.Rect represents rectangular areas.",
        "Tip: Use colliderect() to check rectangle collisions.",
    ]

    # --- Maze ---
    # For level 1, use the preserved maze from NPC intro
    if level == 1 and level1_maze is not None:
        maze = level1_maze
        exit_pos = level1_exit_pos
        coins = level1_coins.copy() if level1_coins else []
        required_items = level1_items.copy() if level1_items else []
        enemies = [enemy.copy() for enemy in level1_enemies] if level1_enemies else []
        collectible_count = len(required_items)
    else:
        # For other levels, generate new maze
        maze = generate_maze(rows, cols)
        player_pos = [1, 1]
        exit_pos = [cols - 3, rows - 3]
        maze[exit_pos[1]][exit_pos[0]] = 0

        # --- Enemies ---
        enemies = []
        for _ in range(min(level + 1, 6)):
            ex, ey = random.randint(3, cols - 3), random.randint(3, rows - 3)
            if maze[ey][ex] == 0:
                enemies.append([ex, ey])

        # --- Coins ---
        coins = random.sample([(x, y) for y in range(rows) for x in range(cols) if maze[y][x] == 0],
                            min(level + 3, 20))

        # --- Items & Tips ---
        collectible_count = min(3 + level, 8)
        required_items = random.sample([(x, y) for y in range(rows) for x in range(cols) if maze[y][x] == 0],
                                    collectible_count)

    player_pos = [1, 1]  # Always start at position [1, 1]
    collected_items = 0

    # --- Enemy movement directions ---
    # Store current direction for each enemy: (dx, dy)
    enemy_directions = []
    for enemy in enemies:
        # Start with a random valid direction
        possible_dirs = []
        for dx, dy in DIRS:
            nx, ny = enemy[0] + dx, enemy[1] + dy
            if 0 <= nx < cols and 0 <= ny < rows and maze[ny][nx] == 0:
                possible_dirs.append((dx, dy))
        if possible_dirs:
            enemy_directions.append(random.choice(possible_dirs))
        else:
            enemy_directions.append((0, 0))  # No movement if stuck

    # --- Tip queue system ---
    tips_to_show = []
    tip_index = 0
    tip_display_time = 0
    tip_duration = 2000  # 2 seconds per tip

    enemy_timer = 0
    start_ticks = pygame.time.get_ticks()
    time_limit = 120

    player_speed = 10
    enemy_speed = max(3, 12 - level)
    running = True
    
    # Timer notification variables
    timer_notification_time = 0
    show_timer_notification = level >= 5

    while running:
        seconds_passed = (pygame.time.get_ticks() - start_ticks) / 1000
        time_left = max(0, time_limit - int(seconds_passed)) if level >= 5 else None

        if level >= 5 and time_left == 0:
            lives -= 1
            if lives <= 0:
                game_over()
                return False, 3
            else:
                return False, lives

        screen.blit(background, (0, 0))

        # --- HUD Background ---
        for i in range(HUD_HEIGHT):
            color_value = 40 + int((i / HUD_HEIGHT) * 40)
            pygame.draw.line(screen, (color_value, color_value, color_value + 20), (0, i), (WIDTH, i))
        pygame.draw.line(screen, LIGHT_BLUE, (0, HUD_HEIGHT - 2), (WIDTH, HUD_HEIGHT - 2), 3)

        # --- HUD Info ---
        screen.blit(font.render(f"🏁 Level: {level}", True, LIGHT_BLUE), (20, 20))
        screen.blit(font.render(f"❤️ Lives: {lives}", True, RED), (280, 20))
        screen.blit(font.render(f"💰 Coins: {total_coins}", True, YELLOW), (520, 20))
        screen.blit(font.render(f"🔑 Items: {collected_items}/{collectible_count}", True, GREEN), (670, 20))
        if level >= 5:
            timer_text = font.render(f"⏱ {time_left}s", True, (255, 255, 255) if time_left > 30 else YELLOW if time_left > 10 else RED)
            screen.blit(timer_text, (WIDTH - 140, HUD_HEIGHT + 10))
        else:
            # Show timer status for levels below 5
            timer_status = font.render("⏱ Timer: Level 5+", True, LIGHT_BLUE)
            screen.blit(timer_status, (WIDTH - 180, HUD_HEIGHT + 10))

        draw_maze(maze, tile_size)
        screen.blit(exit_img, (exit_pos[0]*tile_size, exit_pos[1]*tile_size + HUD_HEIGHT))
        for c in coins:
            screen.blit(coin_img, (c[0]*tile_size, c[1]*tile_size + HUD_HEIGHT))
        for item in required_items:
            screen.blit(item_img, (item[0]*tile_size, item[1]*tile_size + HUD_HEIGHT))
        for e in enemies:
            screen.blit(enemy_img, (e[0]*tile_size, e[1]*tile_size + HUD_HEIGHT))

        # --- Show timer notification for first few seconds ---
        if show_timer_notification and seconds_passed < 3:
            notification_alpha = 200 - (seconds_passed / 3.0) * 150  # Fade out
            notification_bg = pygame.Surface((400, 60), pygame.SRCALPHA)
            notification_bg.fill((0, 0, 0, int(notification_alpha)))
            screen.blit(notification_bg, (WIDTH//2 - 200, HEIGHT//2 - 30))
            
            notification_text = font.render("⏰ TIMER STARTED! Be quick!", True, YELLOW)
            screen.blit(notification_text, (WIDTH//2 - notification_text.get_width()//2, HEIGHT//2 - 10))

        # --- Player Input ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                result = pause_menu()
                if result == "quit":
                    return False, lives

        keys = pygame.key.get_pressed()
        new_pos = player_pos.copy()
        moved = False
        
        # Movement with arrow keys
        if keys[pygame.K_UP]:
            new_pos[1] -= 1
            moved = True
        elif keys[pygame.K_DOWN]:
            new_pos[1] += 1
            moved = True
        elif keys[pygame.K_LEFT]:
            new_pos[0] -= 1
            moved = True
        elif keys[pygame.K_RIGHT]:
            new_pos[0] += 1
            moved = True

        # Allow player to pass through exit door without completing items
        # The exit door is now just a visual element, not a blocking tile
        if 0 <= new_pos[1] < rows and 0 <= new_pos[0] < cols and maze[new_pos[1]][new_pos[0]] != 1:
            player_pos = new_pos
        else:
            if bump_sound:
                bump_sound.play()

        # --- Firing projectile with A/W/S/D keys ---
        now = pygame.time.get_ticks()
        shoot_direction = None
        
        # Check for shooting inputs (A/W/S/D)
        if keys[pygame.K_a] and now - last_shot_time > shot_cooldown:  # A - Left
            shoot_direction = (-1, 0)
        elif keys[pygame.K_d] and now - last_shot_time > shot_cooldown:  # D - Right
            shoot_direction = (1, 0)
        elif keys[pygame.K_w] and now - last_shot_time > shot_cooldown:  # W - Up
            shoot_direction = (0, -1)
        elif keys[pygame.K_s] and now - last_shot_time > shot_cooldown:  # S - Down
            shoot_direction = (0, 1)

        # Create projectile if shooting direction is set
        if shoot_direction is not None:
            px, py = player_pos
            dx, dy = shoot_direction
            
            proj_x = px * tile_size + tile_size // 2
            proj_y = py * tile_size + tile_size // 2 + HUD_HEIGHT
            projectiles.append([proj_x, proj_y, dx, dy])
            last_shot_time = now
            
            if shoot_sound:
                shoot_sound.play()

        # --- Animate Player ---
        moving = any([keys[pygame.K_UP], keys[pygame.K_DOWN], keys[pygame.K_LEFT], keys[pygame.K_RIGHT]])
        if moving:
            now = pygame.time.get_ticks()
            if now - player_last_update > animation_speed:
                player_frame_index = (player_frame_index + 1) % len(player_walk_frames)
                player_last_update = now
        current_player_img = player_walk_frames[player_frame_index] if moving else player_walk_frames[0]
        
        # Flip sprite based on last horizontal movement
        if moved:
            if new_pos[0] < player_pos[0]:  # Moving left
                current_player_img = pygame.transform.flip(current_player_img, True, False)
            elif new_pos[0] > player_pos[0]:  # Moving right
                current_player_img = player_walk_frames[player_frame_index] if moving else player_walk_frames[0]
        
        screen.blit(current_player_img, (player_pos[0]*tile_size, player_pos[1]*tile_size + HUD_HEIGHT))

        # --- Coins ---
        for c in coins[:]:
            if player_pos == list(c):
                coins.remove(c)
                total_coins += 1
                if coin_sound:
                    coin_sound.play()

        # --- Items & Tips (queue multiple tips) ---
        for idx, item in enumerate(required_items[:]):
            if player_pos == list(item):
                required_items.remove(item)
                collected_items += 1
                if item_sound:
                    item_sound.play()
                # Pick 2–3 random tips
                tip_count = random.randint(2, 3)
                new_tips = random.sample(item_tips, tip_count)
                tips_to_show.extend(new_tips)
                tip_index = 0
                tip_display_time = pygame.time.get_ticks()

        # --- Draw queued tips with fade ---
        if tips_to_show:
            current_tip = tips_to_show[tip_index]
            elapsed = pygame.time.get_ticks() - tip_display_time
            if elapsed > tip_duration:
                tip_index += 1
                tip_display_time = pygame.time.get_ticks()
                if tip_index >= len(tips_to_show):
                    tips_to_show = []
                    tip_index = 0
                    current_tip = ""
            if current_tip:
                tip_font = pygame.font.SysFont("arial", 22, bold=True)
                tip_surf = tip_font.render(current_tip, True, LIGHT_BLUE)
                tip_bg = pygame.Surface((tip_surf.get_width()+20, tip_surf.get_height()+10))
                tip_bg.fill(DARK)
                tip_bg.set_alpha(180)
                tip_x = WIDTH//2 - tip_surf.get_width()//2 - 10
                tip_y = HEIGHT - 50
                screen.blit(tip_bg, (tip_x, tip_y))
                screen.blit(tip_surf, (WIDTH//2 - tip_surf.get_width()//2, tip_y + 5))

        # --- Enemy Collision ---
        for i, e in enumerate(enemies):
            if player_pos == e:
                lives -= 1
                if lives <= 0:
                    game_over()
                    return False, 3
                else:
                    player_pos = [1, 1]

        # --- Exit Condition ---
        # Player can now pass through the exit door freely
        # The level only completes when ALL items are collected
        if player_pos == list(exit_pos):
            if collected_items < collectible_count:
                # Show reminder message but don't block movement
                msg = font.render(f"Need {collectible_count - collected_items} more items to complete level!", True, YELLOW)
                screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT - 50))
                # Player can still move freely through the exit
            else:
                save_highscore(level)
                level_complete(level)
                return True, lives

        # --- Move Enemies (Pacman-style maze following) ---
        enemy_timer += 1
        if enemy_timer >= enemy_speed:
            enemy_timer = 0
            for i, e in enumerate(enemies):
                dx, dy = enemy_directions[i]
                
                # Try to continue in current direction
                new_x, new_y = e[0] + dx, e[1] + dy
                
                # If current direction is blocked, find new valid directions
                if (new_x < 0 or new_x >= cols or new_y < 0 or new_y >= rows or 
                    maze[new_y][new_x] == 1):
                    
                    # Find all possible directions (excluding opposite direction to prevent 180° turns)
                    possible_dirs = []
                    opposite_dir = (-dx, -dy)  # Don't allow immediate U-turns
                    
                    for dir_x, dir_y in DIRS:
                        if (dir_x, dir_y) != opposite_dir:  # Avoid going back the same way
                            nx, ny = e[0] + dir_x, e[1] + dir_y
                            if 0 <= nx < cols and 0 <= ny < rows and maze[ny][nx] == 0:
                                possible_dirs.append((dir_x, dir_y))
                    
                    # If no valid directions (dead end), allow opposite direction
                    if not possible_dirs:
                        possible_dirs = [(-dx, -dy)]
                    
                    # Choose a random new direction
                    if possible_dirs:
                        dx, dy = random.choice(possible_dirs)
                        enemy_directions[i] = (dx, dy)
                        new_x, new_y = e[0] + dx, e[1] + dy
                
                # Move enemy
                e[0] = new_x
                e[1] = new_y

        # --- Update & Draw Projectiles ---
        proj_speed = 8  # pixels per frame
        for proj in projectiles[:]:
            proj[0] += proj[2] * proj_speed
            proj[1] += proj[3] * proj_speed
            grid_x = int(proj[0] // tile_size)
            grid_y = int((proj[1] - HUD_HEIGHT) // tile_size)

            # Remove projectile if it hits a wall or goes offscreen
            if (grid_y < 0 or grid_y >= rows or grid_x < 0 or grid_x >= cols or
                    maze[grid_y][grid_x] == 1):
                try:
                    projectiles.remove(proj)
                except ValueError:
                    pass
                continue

            # Draw projectile
            screen.blit(projectile_img, (proj[0] - projectile_img.get_width()//2,
                                         proj[1] - projectile_img.get_height()//2))

            # Check enemy collisions (simple distance check)
            for e in enemies[:]:
                ex = e[0] * tile_size + tile_size // 2
                ey = e[1] * tile_size + tile_size // 2 + HUD_HEIGHT
                if abs(proj[0] - ex) < tile_size//2 and abs(proj[1] - ey) < tile_size//2:
                    try:
                        enemies.remove(e)
                    except ValueError:
                        pass
                    try:
                        projectiles.remove(proj)
                    except ValueError:
                        pass
                    total_coins += 2  # reward for kill
                    break

        pygame.display.flip()
        clock.tick(player_speed)

def level_complete(level):
    try:
        bg_path = f"assets/level{level}BG.png"
        if os.path.exists(bg_path):
            img = pygame.image.load(bg_path).convert()
            img = pygame.transform.scale(img, (WIDTH, HEIGHT))
            screen.blit(img, (0, 0))
        else:
            screen.fill(BLACK)
            msg = font.render(f"Level {level} Complete!", True, GREEN)
            screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2))
    except Exception as e:
        screen.fill(BLACK)
        msg = font.render(f"Level {level} Complete!", True, GREEN)
        screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2))

    pygame.display.flip()
    pygame.time.delay(2500)

def game_over():
    screen.fill(BLACK)
    msg = font.render("GAME OVER!", True, RED)
    screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2))
    pygame.display.flip()
    pygame.time.delay(2000)

def main():
    global selected_character
    
    try:
        pygame.mixer.music.load("assets/background music.wav")
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.5)
    except Exception:
        pass

    start_menu()

    # Show NPC intro at level 1 with the actual level 1 maze backdrop
    npc_intro_level1()

    level, lives = 1, 3
    while True:
        # Check if current level should trigger a quiz (every 2 levels starting from level 2)
        if should_quiz(level):
            while True:
                lives, passed = quiz_screen(level, lives)
                if lives <= 0:
                    game_over()
                    start_menu()
                    level, lives = 1, 3
                    break
                if passed:
                    break
            if lives <= 0:
                continue

        next_level, lives = play_level(level, lives)
        if next_level:
            level += 1 
        else:
            start_menu()
            level, lives = 1, 3

if __name__ == "__main__":
    main()