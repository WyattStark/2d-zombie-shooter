import pygame
import random
import math
import sys

# Initialize pygame
pygame.init()

# Screen
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Zombie Shooter")

# Clock
clock = pygame.time.Clock()

# Colors
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
WHITE = (255, 255, 255)

# Player
player_size = 50
player_speed = 5
player_jump = -12
gravity = 0.5

# Zombies
zombie_size = 40
zombie_speed = 1.5
SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_EVENT, 2000)

# Bullets
bullet_speed = 10

# Ground
GROUND_HEIGHT = 75
GROUND_Y = HEIGHT - GROUND_HEIGHT

# Background
background = pygame.image.load('night_city.png').convert()

# Fonts
font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 72)

def draw_ground():
    pygame.draw.rect(screen, BROWN, (0, GROUND_Y, WIDTH, GROUND_HEIGHT))

def draw_player(player_pos):
    pygame.draw.rect(screen, GREEN, (player_pos[0]-player_size//2, player_pos[1]-player_size//2, player_size, player_size))

def draw_bullets(bullets):
    for bullet in bullets:
        pygame.draw.circle(screen, RED, (int(bullet[0]), int(bullet[1])), 5)

def draw_zombies(zombies):
    for zombie in zombies:
        pygame.draw.rect(screen, BLACK, (zombie[0]-zombie_size//2, zombie[1]-zombie_size//2, zombie_size, zombie_size))

def show_score(score):
    img = font.render(f"Score: {score}", True, WHITE)
    screen.blit(img, (10, 10))

def game_over_screen(score):
    while True:
        screen.fill(BLACK)
        text1 = big_font.render("GAME OVER", True, RED)
        text2 = font.render(f"Final Score: {score}", True, WHITE)
        text3 = font.render("Press R to Restart or ESC to Quit", True, WHITE)

        screen.blit(text1, (WIDTH//2 - text1.get_width()//2, HEIGHT//2 - 100))
        screen.blit(text2, (WIDTH//2 - text2.get_width()//2, HEIGHT//2))
        screen.blit(text3, (WIDTH//2 - text3.get_width()//2, HEIGHT//2 + 50))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    main()  # restart
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

def main():
    # Game state
    player_pos = [WIDTH // 2, GROUND_Y - player_size // 2]
    velocity_y = 0
    on_ground = True
    bullets = []
    zombies = []
    score = 0

    running = True
    while running:
        screen.blit(background, (0, 0))
        draw_ground()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == SPAWN_EVENT:
                side = random.choice(['left', 'right'])
                y_pos = GROUND_Y - zombie_size // 2
                if side == 'left':
                    zombies.append([0, y_pos])
                else:
                    zombies.append([WIDTH, y_pos])
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                angle = math.atan2(my - player_pos[1], mx - player_pos[0])
                dx = math.cos(angle) * bullet_speed
                dy = math.sin(angle) * bullet_speed
                bullets.append([player_pos[0], player_pos[1], dx, dy])

        keys = pygame.key.get_pressed()

        # Move left/right
        if keys[pygame.K_a] and player_pos[0] - player_size // 2 > 0:
            player_pos[0] -= player_speed
        if keys[pygame.K_d] and player_pos[0] + player_size // 2 < WIDTH:
            player_pos[0] += player_speed

        # Jump
        if keys[pygame.K_SPACE] and on_ground:
            velocity_y = player_jump
            on_ground = False

        # Apply gravity
        player_pos[1] += velocity_y
        velocity_y += gravity

        # Stay on ground
        if player_pos[1] >= GROUND_Y - player_size // 2:
            player_pos[1] = GROUND_Y - player_size // 2
            velocity_y = 0
            on_ground = True

        # Update bullets
        bullets = [
            [b[0]+b[2], b[1]+b[3], b[2], b[3]]
            for b in bullets
            if 0 <= b[0] <= WIDTH and 0 <= b[1] <= HEIGHT
        ]

        # Move zombies toward player
        for zombie in zombies:
            if zombie[0] < player_pos[0]:
                zombie[0] += zombie_speed
            else:
                zombie[0] -= zombie_speed

        # Check bullet-zombie collisions
        hit_zombies = []
        for bullet in bullets:
            for zombie in zombies:
                dist = math.hypot(bullet[0] - zombie[0], bullet[1] - zombie[1])
                if dist < zombie_size // 2:
                    hit_zombies.append(zombie)
                    score += 1
        for zombie in hit_zombies:
            if zombie in zombies:
                zombies.remove(zombie)

        # Check zombie-player collision
        for zombie in zombies:
            dist = math.hypot(player_pos[0] - zombie[0], player_pos[1] - zombie[1])
            if dist < (player_size + zombie_size) // 2:
                game_over_screen(score)

        draw_player(player_pos)
        draw_bullets(bullets)
        draw_zombies(zombies)
        show_score(score)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
