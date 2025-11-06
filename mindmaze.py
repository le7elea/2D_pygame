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

# --- Font ---
font = pygame.font.SysFont("arial", 28)

# --- Directions ---
DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]

# --- Global variable for total coins ---
total_coins = 0

# --- Quiz configuration ---
QUIZ_LEVELS = {3, 5, 7, 9, 13, 16, 19, 20}  # set of levels that trigger a quiz
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
        # fallback single frame if sheet missing
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

# --- Save/Load Highscore ---
def save_highscore(level):
    try:
        with open("highscore.txt", "r") as f:
            current = int(f.read())
        if level > current:
            with open("highscore.txt", "w") as f:
                f.write(str(level))
    except:
        with open("highscore.txt", "w") as f:
            f.write(str(level))

def load_highscore():
    if os.path.exists("highscore.txt"):
        try:
            with open("highscore.txt", "r") as f:
                return int(f.read())
        except:
            return 1
    return 1

def play_level(level, lives):
    global total_coins
    clock = pygame.time.Clock()
    tile_size = max(20, TILE_SIZE - (level - 1) * 3)
    rows, cols = GAME_HEIGHT // tile_size, WIDTH // tile_size

    # --- Background & Sprites ---
    background = pygame.image.load(f"assets/level{(level - 1) % 4 + 5}.png").convert()
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    player_walk_frames = load_walk_sprites("wa.png", 4, tile_size)
    player_frame_index = 0
    player_last_update = pygame.time.get_ticks()
    animation_speed = 150
    current_player_img = player_walk_frames[0]

    coin_img = load_sprite("coinss.png", tile_size)
    exit_img = load_sprite("goal.png", tile_size)
    exit_img = pygame.transform.scale(exit_img, (int(tile_size * 1.0), int(tile_size * 1.0)))
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
    tip_duration = 2000  # 2 seconds per tip

    enemy_timer = 0
    start_ticks = pygame.time.get_ticks()
    time_limit = 60

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

        # --- Items & Tips (queue multiple tips) ---
        for idx, item in enumerate(required_items[:]):
            if player_pos == list(item):
                required_items.remove(item)
                collected_items += 1
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
                save_highscore(level)
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
    msg = font.render(f"Level {level} Complete!", True, GREEN)
    screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2))
    pygame.display.flip()
    pygame.time.delay(1500)

def game_over():
    screen.fill(BLACK)
    msg = font.render("GAME OVER!", True, RED)
    screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2))
    pygame.display.flip()
    pygame.time.delay(2000)

# --- Start Menu (show highest level automatically) ---
def start_menu():
    bg = pygame.image.load("assets/startback.png").convert()
    bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
    button_w, button_h = 220, 50
    start_btn = pygame.Rect(WIDTH//2 - button_w//2, HEIGHT//2 - 30, button_w, button_h)
    quit_btn = pygame.Rect(WIDTH//2 - button_w//2, HEIGHT//2 + 50, button_w, button_h)

    high_level = load_highscore()  # read highest level

    # Create a bold font slightly bigger for the high score
    high_font = pygame.font.SysFont("arial", 28, bold=True)

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

        # Display highest level reached below quit button with style
        high_text = high_font.render(f"🏆 Highest Level Reached: {high_level}", True, YELLOW)
        # Shadow effect
        shadow = high_font.render(f"🏆 Highest Level Reached: {high_level}", True, (150, 120, 0))
        screen.blit(shadow, (WIDTH//2 - shadow.get_width()//2 + 2, quit_btn.bottom + 22))
        screen.blit(high_text, (WIDTH//2 - high_text.get_width()//2, quit_btn.bottom + 20))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_btn.collidepoint(mouse):
                    return
                elif quit_btn.collidepoint(mouse):
                    pygame.quit(); sys.exit()

        pygame.display.flip()

def npc_intro_all_tips():
    clock = pygame.time.Clock()
    npc_img = load_sprite("npc.png", 150)  # NPC size
    tips = [
        "Hi there, adventurer!",
        "Welcome to MASID: Maze Adventure!",
        "Collect all items to proceed to the next level.",
        "Collecting items gives you hints for quizzes.",
        "Avoid enemies — they cost lives.",
        "Some levels are timed — hurry!",
        "Use arrow keys to move.",
        "Answer quizzes correctly to keep lives.",
        "Press ESC to pause the game anytime.",
        "Goodluck and have fun exploring the maze!",
    ]

    # Dialogue bubble settings
    bubble_width, bubble_height = 500, 100
    bubble_x, bubble_y = 200, HEIGHT//2 - bubble_height//2
    font_small = pygame.font.SysFont("arial", 24)
    
    current_tip = 0
    total_tips = len(tips)

    # Optional background image for the dialogue screen
    try:
        bg = pygame.image.load("assets/backk.png").convert()
        bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
    except:
        bg = None  # fallback to DARK background if image not found

    while current_tip < total_tips:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                # Move to next tip when player presses any key or clicks
                current_tip += 1

        # Draw background
        if bg:
            screen.blit(bg, (0, 0))
        else:
            screen.fill(DARK)

        # Draw NPC character
        screen.blit(npc_img, (50, HEIGHT//2 - npc_img.get_height()//2))

        if current_tip < total_tips:
            # Draw bubble
            pygame.draw.rect(screen, (255, 255, 255), (bubble_x, bubble_y, bubble_width, bubble_height), border_radius=16)
            pygame.draw.rect(screen, LIGHT_BLUE, (bubble_x, bubble_y, bubble_width, bubble_height), 3, border_radius=16)

            # Draw “tail” pointing to NPC
            tail_points = [(bubble_x - 10, bubble_y + 20), (bubble_x, bubble_y + 40), (bubble_x, bubble_y + 20)]
            pygame.draw.polygon(screen, (255, 255, 255), tail_points)
            pygame.draw.polygon(screen, LIGHT_BLUE, tail_points, 2)

            # Draw tip text
            tip_text = font_small.render(tips[current_tip], True, BLACK)
            screen.blit(tip_text, (bubble_x + 20, bubble_y + bubble_height//2 - tip_text.get_height()//2))

        pygame.display.flip()
        clock.tick(30)


def main():
    pygame.mixer.music.load("assets/background music.wav")
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.5)

    start_menu()

    # Show all tips at the start
    npc_intro_all_tips()

    level, lives = 1, 3
    while True:
        # quiz & level logic remains the same
        if level in QUIZ_LEVELS:
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

        # Start level
        next_level, lives = play_level(level, lives)
        if next_level:
            level += 1
        else:
            start_menu()
            level, lives = 1, 3



if __name__ == "__main__":
    main()
