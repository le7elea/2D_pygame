import pygame
import random
import sys
from collections import deque
import os

# --- Initialize Pygame ---
pygame.init()
pygame.mixer.init()

# --- Screen setup ---
WIDTH, HEIGHT = 1000, 700
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
PURPLE = (150, 60, 200)
GRAY = (100, 100, 100)

# --- Font ---
font = pygame.font.SysFont("arial", 28)
title_font = pygame.font.SysFont("arial", 48, bold=True)

# --- Directions ---
DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]

# --- Global variables ---
total_coins = 0
current_map = 1  # Default map
# Track completed levels for each map: {map_number: [completed_levels]}
level_completion = {1: [False]*5, 2: [False]*5, 3: [False]*5, 4: [False]*5}
# Track which maps are unlocked
map_unlocked = {1: True, 2: False, 3: False, 4: False}

# --- Maps Configuration ---
MAPS = {
    1: {"theme": "Enchanted Groove Maze", "color": GREEN, "image": "map1.png"},
    2: {"theme": "Pharaoh's Sunstone Maze", "color": YELLOW, "image": "map2.png"},
    3: {"theme": "Frostfire Labyrinth", "color": LIGHT_BLUE, "image": "map3.png"},
    4: {"theme": "Crimson Caldera Maze", "color": RED, "image": "map4.png"}
}

# --- Quiz configuration ---
QUIZ_LEVELS = {3, 5, 7, 9, 13, 16, 19, 20}
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
]

# --- Load Sprites ---
def load_sprite(name, size):
    try:
        img = pygame.image.load(f"assets/{name}").convert_alpha()
        return pygame.transform.scale(img, (size, size))
    except:
        surf = pygame.Surface((size, size))
        surf.fill((100, 100, 100))
        return surf

# --- Load Map Preview Images ---
def load_map_preview(map_num):
    """Load map preview image with fallback to colored surface"""
    map_info = MAPS[map_num]
    try:
        img = pygame.image.load(f"assets/{map_info['image']}").convert()
        # Scale to fit our button size (160x160)
        img = pygame.transform.scale(img, (160, 160))
        return img
    except:
        # Fallback: create a colored surface with theme text
        surf = pygame.Surface((160, 160))
        surf.fill(map_info["color"])
        # Add theme text
        font_small = pygame.font.SysFont("arial", 18, bold=True)
        theme_text = font_small.render(map_info["theme"].upper(), True, WHITE)
        surf.blit(theme_text, (80 - theme_text.get_width()//2, 80 - theme_text.get_height()//2))
        return surf

# --- Load Background ---
def load_background(name):
    """Load background image with fallback to dark surface"""
    try:
        bg = pygame.image.load(f"assets/{name}").convert()
        return pygame.transform.scale(bg, (WIDTH, HEIGHT))
    except:
        surf = pygame.Surface((WIDTH, HEIGHT))
        surf.fill(DARK)
        return surf

# --- Load Map Background ---
def load_map_background(map_num):
    """Load map-specific background image"""
    map_info = MAPS[map_num]
    try:
        bg = pygame.image.load(f"assets/{map_info['image']}").convert()
        return pygame.transform.scale(bg, (WIDTH, HEIGHT))
    except:
        # Fallback: create a colored surface
        surf = pygame.Surface((WIDTH, HEIGHT))
        surf.fill(map_info["color"])
        # Add theme text in the center
        theme_font = pygame.font.SysFont("arial", 36, bold=True)
        theme_text = theme_font.render(map_info["theme"], True, WHITE)
        surf.blit(theme_text, (WIDTH//2 - theme_text.get_width()//2, HEIGHT//2 - theme_text.get_height()//2))
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
    except:
        return [pygame.Surface((size, size))]

# --- Maze Generation ---
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

# --- Draw Maze ---
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

# --- Pause Menu ---
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

# --- Quiz Screen ---
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

    while True:
        screen.fill(DARK)
        title = font.render(f"🧩 Quiz — Level {level}", True, LIGHT_BLUE)
        q_font = pygame.font.SysFont("arial", 24)
        q_text = q_font.render(question["question"], True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 60))
        screen.blit(q_text, (WIDTH//2 - q_text.get_width()//2, 140))

        mx, my = pygame.mouse.get_pos()
        for i, rect in enumerate(buttons):
            hovered = rect.collidepoint((mx, my))
            color = (60, 60, 80) if not hovered else (80, 110, 160)
            pygame.draw.rect(screen, color, rect, border_radius=10)
            ans_text = q_font.render(f"{chr(65+i)}. {choices[i]}", True, WHITE)
            screen.blit(ans_text, (rect.x + 16, rect.centery - ans_text.get_height()//2))

        info = font.render("Click an answer or press A/B/C/D (or 1/2/3/4). Wrong = -1 life", True, (200, 200, 200))
        screen.blit(info, (WIDTH//2 - info.get_width()//2, HEIGHT - 60))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(buttons):
                    if rect.collidepoint(event.pos):
                        if i == correct_idx:
                            ok = font.render("✅ Correct!", True, GREEN)
                            screen.blit(ok, (WIDTH//2 - ok.get_width()//2, HEIGHT - 120))
                            pygame.display.flip()
                            pygame.time.delay(800)
                            return lives, True
                        else:
                            lives -= 1
                            wrong = font.render("❌ Wrong! -1 Life", True, RED)
                            screen.blit(wrong, (WIDTH//2 - wrong.get_width()//2, HEIGHT - 120))
                            pygame.display.flip()
                            pygame.time.delay(800)
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
                            ok = font.render("✅ Correct!", True, GREEN)
                            screen.blit(ok, (WIDTH//2 - ok.get_width()//2, HEIGHT - 120))
                            pygame.display.flip()
                            pygame.time.delay(800)
                            return lives, True
                        else:
                            lives -= 1
                            wrong = font.render("❌ Wrong! -1 Life", True, RED)
                            screen.blit(wrong, (WIDTH//2 - wrong.get_width()//2, HEIGHT - 120))
                            pygame.display.flip()
                            pygame.time.delay(800)
                            return lives, False

        clock.tick(30)

# --- Save/Load Progress ---
def save_progress():
    try:
        with open("progress.txt", "w") as f:
            # Save level completion status for each map
            for map_num, levels in level_completion.items():
                level_str = ",".join(["1" if completed else "0" for completed in levels])
                f.write(f"{map_num}:{level_str}\n")
            # Save map unlocked status
            unlocked_str = ",".join(["1" if unlocked else "0" for unlocked in map_unlocked.values()])
            f.write(f"unlocked:{unlocked_str}\n")
    except:
        pass

def load_progress():
    global level_completion, map_unlocked
    if os.path.exists("progress.txt"):
        try:
            with open("progress.txt", "r") as f:
                for line in f:
                    parts = line.strip().split(":")
                    if len(parts) == 2:
                        if parts[0] == "unlocked":
                            # Load map unlocked status
                            unlocked_list = parts[1].split(",")
                            for i, unlocked in enumerate(unlocked_list):
                                if i+1 in map_unlocked:
                                    map_unlocked[i+1] = (unlocked == "1")
                        else:
                            # Load level completion status
                            map_num = int(parts[0])
                            level_list = parts[1].split(",")
                            for i, completed in enumerate(level_list):
                                if i < len(level_completion[map_num]):
                                    level_completion[map_num][i] = (completed == "1")
        except:
            pass

def play_level(level, lives, map_num):
    global total_coins
    clock = pygame.time.Clock()
    tile_size = max(20, TILE_SIZE - (level - 1) * 3)
    rows, cols = GAME_HEIGHT // tile_size, WIDTH // tile_size

    # --- Background & Sprites ---
    try:
        background = pygame.image.load(f"assets/level{(level - 1) % 4 + 5}.png").convert()
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    except:
        background = pygame.Surface((WIDTH, HEIGHT))
        background.fill(DARK)
    
    player_walk_frames = load_walk_sprites("wa.png", 4, tile_size)
    player_frame_index = 0
    player_last_update = pygame.time.get_ticks()
    animation_speed = 150
    current_player_img = player_walk_frames[0]

    coin_img = load_sprite("coinss.png", tile_size)
    exit_img = load_sprite("goal.png", tile_size)
    exit_img = pygame.transform.scale(exit_img, (int(tile_size * 2.5), int(tile_size * 2.5)))
    enemy_img = load_sprite("enemy.png", tile_size)
    item_img = load_sprite("key.png", tile_size)

    coin_sound = pygame.mixer.Sound("assets/coin.mp3")
    bump_sound = pygame.mixer.Sound("assets/bump.mp3")
    item_sound = pygame.mixer.Sound("assets/item.mp3") 

    # --- Maze ---
    maze = generate_maze(rows, cols)
    player_pos = [1, 1]
    exit_pos = [cols - 3, rows - 3]
    maze[exit_pos[1]][exit_pos[0]] = 0

    # --- Enemies (scale with level) ---
    enemies = []
    # Start with 2 enemies at level 1, increase with level
    base_enemies = 2
    enemy_count = base_enemies + (level // 2)  # Add 1 enemy every 2 levels
    enemy_count = min(enemy_count, 10)  # Cap at 10 enemies
    
    for _ in range(enemy_count):
        ex, ey = random.randint(3, cols - 3), random.randint(3, rows - 3)
        if maze[ey][ex] == 0:
            enemies.append([ex, ey])

    # --- Coins ---
    coins = random.sample([(x, y) for y in range(rows) for x in range(cols) if maze[y][x] == 0],
                          min(level + 3, 20))

    # --- Items (scale with level) ---
    # Start with 3 items at level 1, increase with level
    base_items = 3
    collectible_count = base_items + (level // 2)  # Add 1 item every 2 levels
    collectible_count = min(collectible_count, 10)  # Cap at 10 items
    
    required_items = random.sample([(x, y) for y in range(rows) for x in range(cols) if maze[y][x] == 0],
                                   collectible_count)
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
    "Tip: Play a sound with sound.play()."
    ]
    collected_items = 0

    # --- Tip queue system ---
    tips_to_show = []
    tip_index = 0
    tip_display_time = 0
    tip_duration = 3000

    enemy_timer = 0
    start_ticks = pygame.time.get_ticks()
    time_limit = 90

    player_speed = 10
    enemy_speed = max(3, 12 - level)
    running = True

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
        screen.blit(font.render(f"🗺️ Map: {map_num}", True, PURPLE), (WIDTH - 300, 20))
        
        if level >= 5:
            timer_text = font.render(f"⏱ {time_left}s", True, (255, 255, 255) if time_left > 10 else RED)
            screen.blit(timer_text, (WIDTH - 140, HUD_HEIGHT + 10))

        draw_maze(maze, tile_size)
        screen.blit(exit_img, (exit_pos[0]*tile_size, exit_pos[1]*tile_size + HUD_HEIGHT))
        for c in coins:
            screen.blit(coin_img, (c[0]*tile_size, c[1]*tile_size + HUD_HEIGHT))
        for item in required_items:
            screen.blit(item_img, (item[0]*tile_size, item[1]*tile_size + HUD_HEIGHT))
        for e in enemies:
            screen.blit(enemy_img, (e[0]*tile_size, e[1]*tile_size + HUD_HEIGHT))

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
        if keys[pygame.K_UP]: new_pos[1] -= 1
        elif keys[pygame.K_DOWN]: new_pos[1] += 1
        elif keys[pygame.K_LEFT]: new_pos[0] -= 1
        elif keys[pygame.K_RIGHT]: new_pos[0] += 1

        if 0 <= new_pos[1] < rows and 0 <= new_pos[0] < cols and maze[new_pos[1]][new_pos[0]] != 1:
            player_pos = new_pos
        else:
            bump_sound.play()

        # --- Animate Player ---
        moving = any([keys[pygame.K_UP], keys[pygame.K_DOWN], keys[pygame.K_LEFT], keys[pygame.K_RIGHT]])
        if moving:
            now = pygame.time.get_ticks()
            if now - player_last_update > animation_speed:
                player_frame_index = (player_frame_index + 1) % len(player_walk_frames)
                player_last_update = now
        current_player_img = player_walk_frames[player_frame_index] if moving else player_walk_frames[0]
        screen.blit(current_player_img, (player_pos[0]*tile_size, player_pos[1]*tile_size + HUD_HEIGHT))

        # --- Coins ---
        for c in coins[:]:
            if player_pos == list(c):
                coins.remove(c)
                total_coins += 1
                coin_sound.play()

        # --- Items & Tips ---
        for idx, item in enumerate(required_items[:]):
            if player_pos == list(item):
                required_items.remove(item)
                collected_items += 1
                item_sound.play()
                tip_count = random.randint(2, 3)
                new_tips = random.sample(item_tips, tip_count)
                tips_to_show.extend(new_tips)
                tip_index = 0
                tip_display_time = pygame.time.get_ticks()

        # --- Draw queued tips ---
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
        for e in enemies:
            if player_pos == e:
                lives -= 1
                if lives <= 0:
                    game_over()
                    return False, 3
                else:
                    player_pos = [1, 1]

        # --- Exit Condition ---
        if player_pos == list(exit_pos):
            if collected_items < collectible_count:
                msg = font.render(f"Collect all {collectible_count - collected_items} items first!", True, RED)
                screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT - 50))
                pygame.display.flip()
                pygame.time.delay(1000)
            else:
                level_complete(level)
                return True, lives

        # --- Move Enemies ---
        enemy_timer += 1
        if enemy_timer >= enemy_speed:
            enemy_timer = 0
            for e in enemies:
                e[0] += random.choice([-1, 1])
                e[1] += random.choice([-1, 1])
                e[0] = max(1, min(cols - 2, e[0]))
                e[1] = max(1, min(rows - 2, e[1]))

        pygame.display.flip()
        clock.tick(player_speed)

# --- Screens ---
def level_complete(level):
    screen.fill(BLACK)
    title_font = pygame.font.Font(None, 80)
    sub_font = pygame.font.Font(None, 40)
    
    title_text = title_font.render(f"LEVEL {level} COMPLETE!", True, (0, 255, 100))
    sub_text = sub_font.render("Get ready for the next challenge...", True, (200, 200, 200))
    
    for alpha in range(0, 255, 5):
        screen.fill(BLACK)
        title_surface = title_text.copy()
        sub_surface = sub_text.copy()
        title_surface.set_alpha(alpha)
        sub_surface.set_alpha(alpha)
        
        screen.blit(title_surface, (WIDTH//2 - title_surface.get_width()//2, HEIGHT//2 - 60))
        screen.blit(sub_surface, (WIDTH//2 - sub_surface.get_width()//2, HEIGHT//2 + 20))
        try:
            complete_sound = pygame.mixer.Sound("assets/nextlevel.mp3")
            complete_sound.play()
        except:
            pass

        pygame.display.flip()
        pygame.time.delay(20)
    
    pygame.time.delay(1200)

def game_over():
    screen.fill(BLACK)
    msg = font.render("GAME OVER!", True, RED)
    screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2))
    pygame.display.flip()
    pygame.time.delay(2000)

# --- Start Screen ---
def start_screen():
    bg = load_background("startback.png")
    button_w, button_h = 220, 50
    start_btn = pygame.Rect(WIDTH//2 - button_w//2, HEIGHT//2 - 30, button_w, button_h)
    quit_btn = pygame.Rect(WIDTH//2 - button_w//2, HEIGHT//2 + 50, button_w, button_h)

    while True:
        screen.blit(bg, (0, 0))
        mouse = pygame.mouse.get_pos()

        # Draw buttons
        for rect, text, color in [
            (start_btn, "Start Game", BLUE if not start_btn.collidepoint(mouse) else LIGHT_BLUE),
            (quit_btn, "Quit Game", RED if not quit_btn.collidepoint(mouse) else (255, 120, 120))
        ]:
            pygame.draw.rect(screen, color, rect, border_radius=12)
            label = font.render(text, True, WHITE)
            screen.blit(label, (rect.centerx - label.get_width()//2, rect.centery - label.get_height()//2))

        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_btn.collidepoint(mouse):
                    return
                elif quit_btn.collidepoint(mouse):
                    pygame.quit(); sys.exit()

        pygame.display.flip()

# --- Map Selection Screen ---
def map_selection_screen():
    global current_map
    # Load maze background for map selection
    bg = load_background("mazebg.png")
    
    # Create a semi-transparent overlay for better text readability
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))  # Semi-transparent black
    
    title = title_font.render("SELECT MAZE", True, LIGHT_BLUE)
    
    # Load map preview images
    map_previews = {}
    for map_num in range(1, 5):
        map_previews[map_num] = load_map_preview(map_num)
    
    # Button dimensions - optimized for horizontal arrangement
    button_w, button_h = 170, 220  # Same as before
    
    # Calculate positions for horizontal arrangement (1-2-3-4)
    total_width = 4 * button_w + 3 * 30  # 4 buttons with 30px spacing
    start_x = (WIDTH - total_width) // 2
    y_position = 250  # Fixed vertical position
    
    buttons = {}
    
    for i in range(4):
        map_num = i + 1
        x_position = start_x + i * (button_w + 30)
        buttons[map_num] = pygame.Rect(x_position, y_position, button_w, button_h)

    while True:
        # Draw background and overlay
        screen.blit(bg, (0, 0))
        screen.blit(overlay, (0, 0))
        
        mouse = pygame.mouse.get_pos()
        
        # Draw title with shadow effect
        title_shadow = title_font.render("SELECT MAZE", True, (0, 0, 0))
        screen.blit(title_shadow, (WIDTH//2 - title_shadow.get_width()//2 + 2, 82))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
        
        for map_num, rect in buttons.items():
            # Check if map is unlocked
            unlocked = map_unlocked[map_num]
            completed = all(level_completion[map_num])  # Check if all levels are completed
            
            # Create a surface for the map button with transparency
            button_surface = pygame.Surface((button_w, button_h), pygame.SRCALPHA)
            
            if not unlocked:
                # Draw locked state
                pygame.draw.rect(button_surface, (40, 40, 40, 200), (0, 0, button_w, button_h), border_radius=12)
                pygame.draw.rect(button_surface, (80, 80, 80, 255), (0, 0, button_w, button_h), width=3, border_radius=12)
                
                # Darken the preview image
                dark_preview = map_previews[map_num].copy()
                dark_preview.fill((50, 50, 50, 180), special_flags=pygame.BLEND_RGBA_MULT)
                button_surface.blit(dark_preview, (5, 5))
                
                # Large lock icon in center of preview
                lock_font = pygame.font.SysFont("arial", 48, bold=True)
                lock_icon = lock_font.render("🔒", True, WHITE)
                button_surface.blit(lock_icon, (button_w//2 - lock_icon.get_width()//2, 70))
                
                # "LOCKED" text at bottom
                status_text = font.render("LOCKED", True, RED)
                button_surface.blit(status_text, (button_w//2 - status_text.get_width()//2, 180))
            else:
                # Draw normal state
                if rect.collidepoint(mouse):
                    # Hover effect - brighter background
                    pygame.draw.rect(button_surface, (255, 255, 255, 50), (0, 0, button_w, button_h), border_radius=12)
                    pygame.draw.rect(button_surface, LIGHT_BLUE, (0, 0, button_w, button_h), width=3, border_radius=12)
                else:
                    pygame.draw.rect(button_surface, (255, 255, 255, 30), (0, 0, button_w, button_h), border_radius=12)
                    pygame.draw.rect(button_surface, MAPS[map_num]["color"], (0, 0, button_w, button_h), width=3, border_radius=12)
                
                # Draw the preview image
                button_surface.blit(map_previews[map_num], (5, 5))
                
                # Show "COMPLETED" text if all levels are done
                if completed:
                    completed_font = pygame.font.SysFont("arial", 20, bold=True)
                    completed_text = completed_font.render("COMPLETED", True, GREEN)
                    button_surface.blit(completed_text, (button_w//2 - completed_text.get_width()//2, 180))
            
            # Draw the button surface to screen
            screen.blit(button_surface, rect)
            
            # Theme name (drawn directly to screen for better visibility)
            map_info = MAPS[map_num]
            theme_font = pygame.font.SysFont("arial", 16, bold=True)
            
            # Display map number above the theme name
            map_num_text = font.render(f"Map {map_num}", True, WHITE)
            screen.blit(map_num_text, (rect.centerx - map_num_text.get_width()//2, rect.y - 30))
            
            # Wrap long theme names if needed
            if len(map_info["theme"]) > 20:
                # Split into two lines
                words = map_info["theme"].split()
                line1 = " ".join(words[:len(words)//2])
                line2 = " ".join(words[len(words)//2:])
                line1_text = theme_font.render(line1, True, WHITE)
                line2_text = theme_font.render(line2, True, WHITE)
                screen.blit(line1_text, (rect.centerx - line1_text.get_width()//2, rect.y + 170))
                screen.blit(line2_text, (rect.centerx - line2_text.get_width()//2, rect.y + 190))
            else:
                theme_text = theme_font.render(map_info["theme"], True, WHITE)
                screen.blit(theme_text, (rect.centerx - theme_text.get_width()//2, rect.y + 180))

        # Back button
        back_btn = pygame.Rect(WIDTH//2 - 100, HEIGHT - 70, 200, 50)
        back_color = LIGHT_BLUE if back_btn.collidepoint(mouse) else BLUE
        pygame.draw.rect(screen, back_color, back_btn, border_radius=12)
        back_text = font.render("Back to Menu", True, WHITE)
        screen.blit(back_text, (back_btn.centerx - back_text.get_width()//2, back_btn.centery - back_text.get_height()//2))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for map_num, rect in buttons.items():
                    # Check if map is unlocked and can be selected
                    if rect.collidepoint(mouse) and map_unlocked[map_num]:
                        current_map = map_num
                        return
                if back_btn.collidepoint(mouse):
                    return "back"

        pygame.display.flip()

# --- Level Selection Screen ---
def level_selection_screen(map_num):
    # Load map-specific background
    bg = load_map_background(map_num)
    
    # Create a semi-transparent overlay for better text readability
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))  # Semi-transparent black
    
    button_w, button_h = 100, 100
    buttons = {}
    
    # Create 5 level buttons in a row
    for i in range(5):
        buttons[i+1] = pygame.Rect(150 + i*(button_w + 50), 300, button_w, button_h)

    while True:
        # Draw background and overlay
        screen.blit(bg, (0, 0))
        screen.blit(overlay, (0, 0))
        
        mouse = pygame.mouse.get_pos()
        
       
        for level_num, rect in buttons.items():
            # Check if level is unlocked
            # Level 1 is always unlocked if map is unlocked
            # Other levels are unlocked if previous level is completed
            unlocked = (level_num == 1) or (level_num > 1 and level_completion[map_num][level_num-2])
            completed = level_completion[map_num][level_num-1]
            
            # Create button surface with transparency
            button_surface = pygame.Surface((button_w, button_h), pygame.SRCALPHA)
            
            if completed:
                pygame.draw.rect(button_surface, (0, 200, 0, 200), (0, 0, button_w, button_h), border_radius=12)
                pygame.draw.rect(button_surface, GREEN, (0, 0, button_w, button_h), width=3, border_radius=12)
            elif unlocked:
                if rect.collidepoint(mouse):
                    pygame.draw.rect(button_surface, (100, 180, 255, 200), (0, 0, button_w, button_h), border_radius=12)
                    pygame.draw.rect(button_surface, LIGHT_BLUE, (0, 0, button_w, button_h), width=3, border_radius=12)
                else:
                    pygame.draw.rect(button_surface, (0, 120, 255, 200), (0, 0, button_w, button_h), border_radius=12)
                    pygame.draw.rect(button_surface, BLUE, (0, 0, button_w, button_h), width=3, border_radius=12)
            else:
                pygame.draw.rect(button_surface, (100, 100, 100, 200), (0, 0, button_w, button_h), border_radius=12)
                pygame.draw.rect(button_surface, GRAY, (0, 0, button_w, button_h), width=3, border_radius=12)
            
            # Draw the button surface to screen
            screen.blit(button_surface, rect)
            
            # Level number
            level_text = title_font.render(str(level_num), True, WHITE)
            screen.blit(level_text, (rect.centerx - level_text.get_width()//2, rect.centery - level_text.get_height()//2))
            
            # Status - show lock for locked levels, checkmark for completed
            if completed:
                status_text = font.render("✓", True, WHITE)
                screen.blit(status_text, (rect.centerx - status_text.get_width()//2, rect.bottom + 10))
            elif not unlocked:
                # Show lock icon for locked levels
                lock_font = pygame.font.SysFont("arial", 24)
                lock_icon = lock_font.render("🔒", True, WHITE)
                screen.blit(lock_icon, (rect.centerx - lock_icon.get_width()//2, rect.bottom + 10))

        # Back button
        back_btn = pygame.Rect(WIDTH//2 - 100, HEIGHT - 80, 200, 50)
        back_color = LIGHT_BLUE if back_btn.collidepoint(mouse) else BLUE
        pygame.draw.rect(screen, back_color, back_btn, border_radius=12)
        back_text = font.render("Back to Maps", True, WHITE)
        screen.blit(back_text, (back_btn.centerx - back_text.get_width()//2, back_btn.centery - back_text.get_height()//2))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for level_num, rect in buttons.items():
                    # Check if level is unlocked and can be selected
                    unlocked = (level_num == 1) or (level_num > 1 and level_completion[map_num][level_num-2])
                    if rect.collidepoint(mouse) and unlocked:
                        return level_num
                if back_btn.collidepoint(mouse):
                    return "back"

        pygame.display.flip()

# --- Run Screen (Play a single level) ---
def run_screen(map_num, level_num):
    global level_completion, map_unlocked
    
    # Calculate global level number
    global_level = (map_num - 1) * 5 + level_num
    
    lives = 3
    
    # Quiz Section (if this level has a quiz)
    if global_level in QUIZ_LEVELS:
        while True:
            lives, passed = quiz_screen(global_level, lives)
            if lives <= 0:
                game_over()
                return False
            if passed:
                break

    # Maze Gameplay Section
    next_level, lives = play_level(global_level, lives, map_num)
    
    if next_level:
        # Mark this level as completed
        level_completion[map_num][level_num-1] = True
        
        # If this was the last level of the map, unlock the next map
        if level_num == 5 and map_num < 4:
            map_unlocked[map_num + 1] = True
        
        save_progress()
        return True
    else:
        return False

# --- Map Complete Screen ---
def map_complete_screen(map_num):
    screen.fill(BLACK)
    title_font = pygame.font.Font(None, 80)
    sub_font = pygame.font.Font(None, 40)
    
    map_info = MAPS[map_num]
    title_text = title_font.render(f"{map_info['theme']} COMPLETED!", True, MAPS[map_num]["color"])
    
    if map_num < 4:
        next_map_info = MAPS[map_num + 1]
        sub_text = sub_font.render(f"Next map unlocked: {next_map_info['theme']}", True, (200, 200, 200))
    else:
        sub_text = sub_font.render("All maps completed! You are a maze master!", True, (200, 200, 200))
    
    for alpha in range(0, 255, 5):
        screen.fill(BLACK)
        title_surface = title_text.copy()
        sub_surface = sub_text.copy()
        title_surface.set_alpha(alpha)
        sub_surface.set_alpha(alpha)
        
        screen.blit(title_surface, (WIDTH//2 - title_surface.get_width()//2, HEIGHT//2 - 60))
        screen.blit(sub_surface, (WIDTH//2 - sub_surface.get_width()//2, HEIGHT//2 + 20))
        
        pygame.display.flip()
        pygame.time.delay(20)
    
    pygame.time.delay(2000)

# --- All Levels Completed Screen ---
def all_levels_completed_screen():
    screen.fill((0, 0, 0))
    font_large = pygame.font.Font(None, 80)
    sub_font = pygame.font.Font(None, 40)

    text = font_large.render("🎉 All Maps Completed!", True, (255, 215, 0))
    sub_text = sub_font.render("You mastered MASID: Maze!", True, (255, 255, 255))

    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 60))
    screen.blit(sub_text, (WIDTH // 2 - sub_text.get_width() // 2, HEIGHT // 2 + 20))
    pygame.display.flip()

    try:
        pygame.mixer.Sound("assets/victory.wav").play()
    except:
        pass

    pygame.time.wait(5000)

# --- NPC Intro ---
def npc_intro_all_tips():
    clock = pygame.time.Clock()
    try:
        npc_img = load_sprite("npc.png", 150)
    except:
        npc_img = pygame.Surface((150, 150))
        npc_img.fill(LIGHT_BLUE)
    
    tips = [
        "Hi there, adventurer!",
        "Welcome to MASID: Maze Adventure!",
        "Complete levels in order to unlock the next ones.",
        "Each map has 5 levels that must be completed sequentially.",
        "Collect all items to proceed to the next level.",
        "Avoid enemies — they cost lives.",
        "Higher levels have more enemies and items to collect!",
        "Some levels have timed challenges.",
        "Answer quizzes to test your knowledge.",
        "Complete a map to unlock the next one!",
        "Good luck and have fun exploring!",
    ]

    bubble_width, bubble_height = 500, 100
    bubble_x, bubble_y = 200, HEIGHT//2 - bubble_height//2
    font_small = pygame.font.SysFont("arial", 24)
    
    current_tip = 0
    total_tips = len(tips)

    try:
        bg = load_background("backk.png")
    except:
        bg = None

    while current_tip < total_tips:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                current_tip += 1

        if bg:
            screen.blit(bg, (0, 0))
        else:
            screen.fill(DARK)

        screen.blit(npc_img, (50, HEIGHT//2 - npc_img.get_height()//2))

        if current_tip < total_tips:
            pygame.draw.rect(screen, (255, 255, 255), (bubble_x, bubble_y, bubble_width, bubble_height), border_radius=16)
            pygame.draw.rect(screen, LIGHT_BLUE, (bubble_x, bubble_y, bubble_width, bubble_height), 3, border_radius=16)

            tail_points = [(bubble_x - 10, bubble_y + 20), (bubble_x, bubble_y + 40), (bubble_x, bubble_y + 20)]
            pygame.draw.polygon(screen, (255, 255, 255), tail_points)
            pygame.draw.polygon(screen, LIGHT_BLUE, tail_points, 2)

            tip_text = font_small.render(tips[current_tip], True, BLACK)
            screen.blit(tip_text, (bubble_x + 20, bubble_y + bubble_height//2 - tip_text.get_height()//2))

        pygame.display.flip()
        clock.tick(30)

# --- Main Game Flow ---
def main():
    try:
        pygame.mixer.music.load("assets/background music.wav")
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.5)
    except:
        pass
    
    # Load progress at start
    load_progress()

    while True:
        start_screen()
        npc_intro_all_tips()
        
        # Map selection loop
        while True:
            result = map_selection_screen()
            if result == "back":
                break
            
            # Level selection loop for the selected map
            while True:
                selected_level = level_selection_screen(current_map)
                if selected_level == "back":
                    break
                
                # Play the selected level
                success = run_screen(current_map, selected_level)
                
                # If player completed the level and it was the last level of the map
                if success and selected_level == 5:
                    map_complete_screen(current_map)
                    break

if __name__ == "__main__":
    main()