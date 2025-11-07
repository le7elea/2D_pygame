import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 900, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pharaoh's Sunstone Maze")

# Colors
BACKGROUND = (20, 12, 36)  # Deep purple/night sky
SAND_COLOR = (194, 178, 128)  # Desert sand
PYRAMID_COLOR = (227, 201, 107)  # Golden pyramid
TITLE_COLOR = (255, 215, 0)  # Gold
SUBTITLE_COLOR = (255, 165, 0)  # Orange
LEVEL_BG = (139, 69, 19)  # Brown
LEVEL_HOVER = (205, 133, 63)  # Lighter brown
LEVEL_TEXT = (255, 255, 255)  # White
BUTTON_COLOR = (184, 134, 11)  # Dark goldenrod
BUTTON_HOVER = (218, 165, 32)  # Goldenrod
TEXT_COLOR = (255, 255, 255)  # White
LINK_COLOR = (100, 149, 237)  # Cornflower blue
STAR_COLOR = (255, 215, 0)  # Gold

# Fonts
title_font = pygame.font.SysFont('Arial', 48, bold=True)
subtitle_font = pygame.font.SysFont('Arial', 36, bold=True)
level_font = pygame.font.SysFont('Arial', 32, bold=True)
button_font = pygame.font.SysFont('Arial', 28)
footer_font = pygame.font.SysFont('Arial', 18)

# Level data
levels = [1, 2, 3, 4, 5]

# Level completion status (0 = not completed, 1 = completed)
level_status = [1, 1, 1, 0, 0]  # First 3 completed, last 2 not

# Level button dimensions
level_width = 120
level_height = 120
level_margin = 30

# Calculate grid position to center it
grid_width = 5 * level_width + 4 * level_margin
grid_x = (WIDTH - grid_width) // 2
grid_y = 300

# Back button dimensions
back_button_width = 200
back_button_height = 50
back_button_x = (WIDTH - back_button_width) // 2
back_button_y = 500

# Function to draw a star
def draw_star(surface, color, center, size):
    points = []
    for i in range(5):
        # Outer points
        angle = pygame.math.Vector2(1, 0).rotate(72 * i - 90)
        points.append(center + angle * size)
        # Inner points
        angle = pygame.math.Vector2(1, 0).rotate(72 * i + 36 - 90)
        points.append(center + angle * (size * 0.4))
    
    pygame.draw.polygon(surface, color, points)

# Function to draw a pyramid
def draw_pyramid(surface, x, y, width, height):
    # Base
    base_rect = pygame.Rect(x, y + height - height//4, width, height//4)
    pygame.draw.rect(surface, PYRAMID_COLOR, base_rect)
    
    # Pyramid sides
    pygame.draw.polygon(surface, PYRAMID_COLOR, [
        (x, y + height - height//4),  # Bottom left
        (x + width//2, y),  # Top
        (x + width, y + height - height//4)  # Bottom right
    ])
    
    # Pyramid details
    pygame.draw.line(surface, (139, 69, 19), (x + width//2, y), (x + width//2, y + height - height//4), 2)
    for i in range(1, 4):
        y_pos = y + (height - height//4) * i // 4
        pygame.draw.line(surface, (139, 69, 19), (x + width//4, y_pos), (x + 3*width//4, y_pos), 2)

# Function to draw a sun
def draw_sun(surface, x, y, radius):
    pygame.draw.circle(surface, (255, 215, 0), (x, y), radius)
    
    # Sun rays
    for i in range(12):
        angle = math.radians(i * 30)
        start_x = x + math.cos(angle) * radius
        start_y = y + math.sin(angle) * radius
        end_x = x + math.cos(angle) * (radius + 20)
        end_y = y + math.sin(angle) * (radius + 20)
        pygame.draw.line(surface, (255, 215, 0), (start_x, start_y), (end_x, end_y), 3)

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check if a level was clicked
            mouse_pos = pygame.mouse.get_pos()
            for i in range(5):
                x = grid_x + i * (level_width + level_margin)
                level_rect = pygame.Rect(x, grid_y, level_width, level_height)
                
                if level_rect.collidepoint(mouse_pos):
                    # Toggle completion status for demo
                    level_status[i] = 1 - level_status[i]
                    print(f"Level {levels[i]} clicked! Status: {'Completed' if level_status[i] else 'Not Completed'}")
            
            # Check if back button was clicked
            back_button_rect = pygame.Rect(back_button_x, back_button_y, back_button_width, back_button_height)
            if back_button_rect.collidepoint(mouse_pos):
                print("Back to Maps clicked!")
    
    # Get mouse position
    mouse_pos = pygame.mouse.get_pos()
    
    # Fill background
    screen.fill(BACKGROUND)
    
    # Draw sand at the bottom
    pygame.draw.rect(screen, SAND_COLOR, (0, HEIGHT - 150, WIDTH, 150))
    
    # Draw pyramids in the background
    draw_pyramid(screen, 100, HEIGHT - 250, 150, 200)
    draw_pyramid(screen, WIDTH - 250, HEIGHT - 300, 200, 250)
    
    # Draw sun
    draw_sun(screen, WIDTH - 100, 100, 60)
    
    # Draw title
    title_text = title_font.render("Pharaoh's Sunstone Maze", True, TITLE_COLOR)
    title_rect = title_text.get_rect(center=(WIDTH//2, 100))
    screen.blit(title_text, title_rect)
    
    # Draw subtitle
    subtitle_text = subtitle_font.render("SELECT LEVEL", True, SUBTITLE_COLOR)
    subtitle_rect = subtitle_text.get_rect(center=(WIDTH//2, 170))
    screen.blit(subtitle_text, subtitle_rect)
    
    # Draw decorative elements
    pygame.draw.line(screen, (255, 215, 0), (WIDTH//2 - 150, 200), (WIDTH//2 + 150, 200), 3)
    
    # Draw level grid
    for i in range(5):
        # Calculate level position
        x = grid_x + i * (level_width + level_margin)
        
        # Create level rectangle
        level_rect = pygame.Rect(x, grid_y, level_width, level_height)
        
        # Check if mouse is hovering over level
        if level_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, LEVEL_HOVER, level_rect, border_radius=15)
            # Add glow effect
            pygame.draw.rect(screen, (255, 215, 0, 100), level_rect, 3, border_radius=15)
        else:
            pygame.draw.rect(screen, LEVEL_BG, level_rect, border_radius=15)
        
        # Draw level number
        level_text = level_font.render(str(levels[i]), True, LEVEL_TEXT)
        text_rect = level_text.get_rect(center=(level_rect.centerx, level_rect.centery - 20))
        screen.blit(level_text, text_rect)
        
        # Draw decorative sunstone in the level button
        pygame.draw.circle(screen, (255, 215, 0), (level_rect.centerx, level_rect.centery + 15), 15)
        
        # Draw stars based on completion status
        star_color = STAR_COLOR if level_status[i] else (100, 100, 100)
        star_size = 8
        
        # Draw three stars
        for j in range(3):
            star_x = level_rect.centerx - 15 + (j * 15)
            star_y = level_rect.centery + 40
            draw_star(screen, star_color, pygame.math.Vector2(star_x, star_y), star_size)
    
    # Draw back button
    back_button_rect = pygame.Rect(back_button_x, back_button_y, back_button_width, back_button_height)
    if back_button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, BUTTON_HOVER, back_button_rect, border_radius=10)
    else:
        pygame.draw.rect(screen, BUTTON_COLOR, back_button_rect, border_radius=10)
    
    back_text = button_font.render("Back to Maps", True, TEXT_COLOR)
    back_text_rect = back_text.get_rect(center=back_button_rect.center)
    screen.blit(back_text, back_text_rect)
    
    # Draw footer
    footer_text1 = footer_font.render("Hello from the twgame community —", True, TEXT_COLOR)
    footer_rect1 = footer_text1.get_rect(center=(WIDTH//2, HEIGHT - 50))
    screen.blit(footer_text1, footer_rect1)
    
    footer_text2 = footer_font.render("https://www.twgame.org/content.html", True, LINK_COLOR)
    footer_rect2 = footer_text2.get_rect(center=(WIDTH//2, HEIGHT - 25))
    screen.blit(footer_text2, footer_rect2)
    
    # Update display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()