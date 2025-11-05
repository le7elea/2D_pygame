import pygame
import sys

# --- Initialize Pygame ---
pygame.init()

# --- Screen settings ---
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple Pygame Example")

# --- Colors ---
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

# --- Player setup ---
player = pygame.Rect(WIDTH//2 - 25, HEIGHT//2 - 25, 50, 50)
player_speed = 5

# --- Clock ---
clock = pygame.time.Clock()
FPS = 60

# --- Main game loop ---
while True:
    # --- Event handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # --- Move player ---
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        player.y -= player_speed
    if keys[pygame.K_DOWN]:
        player.y += player_speed
    if keys[pygame.K_LEFT]:
        player.x -= player_speed
    if keys[pygame.K_RIGHT]:
        player.x += player_speed

    # --- Keep player inside screen ---
    if player.left < 0:
        player.left = 0
    if player.right > WIDTH:
        player.right = WIDTH
    if player.top < 0:
        player.top = 0
    if player.bottom > HEIGHT:
        player.bottom = HEIGHT

    # --- Draw everything ---
    screen.fill(WHITE)
    pygame.draw.rect(screen, BLUE, player)

    pygame.display.flip()
    clock.tick(FPS)
