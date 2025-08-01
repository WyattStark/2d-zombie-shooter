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
GRAY = (128, 128, 128)

# Player settings
player_size = 50
player_speed = 5
player_jump = -12
gravity = 0.5

# Zombies
zombie_size = 40
zombie_speed = 1.0
SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_EVENT, 2000)

# Bullets
bullet_speed = 10

# Ground
GROUND_HEIGHT = 75
GROUND_Y = HEIGHT - GROUND_HEIGHT

# Background
background = pygame.image.load('night_city.png').convert()

# Load sound
pistol_sound = pygame.mixer.Sound('pistol_shot.wav')

# Fonts
font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 72)

def draw_ground():
    pygame.draw.rect(screen, BROWN, (0, GROUND_Y, WIDTH, GROUND_HEIGHT))

def draw_player_with_gun(player_pos, walk_cycle):
    head_radius = 15
    body_length = 40
    arm_length = 25
    leg_length = 30
    color = BLACK

    x, y = player_pos

    # Head
    pygame.draw.circle(screen, color, (int(x), int(y - body_length // 2 - head_radius)), head_radius, 2)

    # Body
    pygame.draw.line(screen, color, (x, y - body_length // 2), (x, y + body_length // 2), 2)

    # Arms
    pygame.draw.line(screen, color, (x, y - 10), (x + arm_length, y), 2)
    pygame.draw.line(screen, color, (x, y - 10), (x - arm_length, y), 2)

    # Legs swing with walk_cycle
    leg_offset = math.sin(walk_cycle) * 10
    pygame.draw.line(screen, color, (x, y + body_length // 2),
                     (x - arm_length + leg_offset, y + body_length // 2 + leg_length), 2)
    pygame.draw.line(screen, color, (x, y + body_length // 2),
                     (x + arm_length - leg_offset, y + body_length // 2 + leg_length), 2)

    # Pistol
    gun_width = 10
    gun_height = 4
    gun_x = x + arm_length
    gun_y = y - gun_height // 2
    pygame.draw.rect(screen, BLACK, (gun_x, gun_y, gun_width, gun_height))

def draw_zombie_stickman(zombie_pos, walk_cycle):
    head_radius = 12
    body_length = 30
    arm_length = 20
    leg_length = 25
    color = RED

    x, y = zombie_pos

    # Slouched posture
    head_y_offset = 5
    body_angle = math.radians(10)
    body_start_y = y - body_length // 2 + head_y_offset
    body_end_x = x + math.sin(body_angle) * body_length
    body_end_y = y + body_length // 2 + head_y_offset

    # Head
    pygame.draw.circle(screen, color, (int(x), int(body_start_y - head_radius)), head_radius, 2)

    # Body
    pygame.draw.line(screen, color, (x, body_start_y), (body_end_x, body_end_y), 2)

    # Arms
    arm_start_y = body_start_y + 8
    pygame.draw.line(screen, color, (x, arm_start_y), (x + arm_length, arm_start_y + 5), 2)
    pygame.draw.line(screen, color, (x, arm_start_y), (x - arm_length, arm_start_y + 5), 2)

    # Legs
    leg_offset = math.sin(walk_cycle) * 8
    leg_start_y = body_end_y
    pygame.draw.line(screen, color, (body_end_x, leg_start_y),
                     (body_end_x - arm_length + leg_offset, leg_start_y + leg_length), 2)
    pygame.draw.line(screen, color, (body_end_x, leg_start_y),
                     (body_end_x + arm_length - leg_offset, leg_start_y + leg_length), 2)

def draw_bullets(bullets):
    for bullet in bullets:
        pygame.draw.circle(screen, RED, (int(bullet[0]), int(bullet[1])), 5)

def show_score(score, player_name):
    img = font.render(f"Player: {player_name}  Score: {score}", True, WHITE)
    screen.blit(img, (10, 10))

def game_over_screen(score, player_name):
    while True:
        screen.fill(BLACK)
        text1 = big_font.render("GAME OVER", True, RED)
        text2 = font.render(f"Player: {player_name}  Final Score: {score}", True, WHITE)
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
                    return True  # Signal to restart
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
    return False

def menu_screen():
    player_name = ""
    input_active = False
    input_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 50, 300, 40)
    play_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 20, 200, 50)
    title_text = big_font.render("Zombie Shooter", True, WHITE)
    instruction_text = font.render("Enter Name and Click Play", True, WHITE)
    input_prompt = font.render("Player Name:", True, WHITE)

    while True:
        screen.fill(BLACK)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//2 - 150))
        screen.blit(instruction_text, (WIDTH//2 - instruction_text.get_width()//2, HEIGHT//2 - 80))
        screen.blit(input_prompt, (WIDTH//2 - 150, HEIGHT//2 - 80))

        # Draw input box
        pygame.draw.rect(screen, WHITE if input_active else GRAY, input_rect, 2)
        name_surface = font.render(player_name, True, WHITE)
        screen.blit(name_surface, (input_rect.x + 5, input_rect.y + 5))

        # Draw play button
        pygame.draw.rect(screen, GREEN, play_button)
        play_text = font.render("Play", True, BLACK)
        screen.blit(play_text, (play_button.x + play_button.width//2 - play_text.get_width()//2,
                                play_button.y + play_button.height//2 - play_text.get_height()//2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if input_rect.collidepoint(event.pos):
                    input_active = True
                else:
                    input_active = False
                if play_button.collidepoint(event.pos) and player_name.strip():
                    return player_name.strip()
            elif event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_RETURN and player_name.strip():
                    return player_name.strip()
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif event.unicode.isprintable() and len(player_name) < 20:
                    player_name += event.unicode

        clock.tick(60)

def main():
    while True:
        player_name = menu_screen()
        player_pos = [WIDTH // 2, GROUND_Y - player_size // 2]
        velocity_y = 0
        on_ground = True
        bullets = []
        zombies = []
        score = 0
        walk_cycle = 0

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
                    z_walk = random.uniform(0, math.pi * 2)
                    if side == 'left':
                        zombies.append([0, y_pos, z_walk])
                    else:
                        zombies.append([WIDTH, y_pos, z_walk])
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    angle = math.atan2(my - player_pos[1], mx - player_pos[0])
                    dx = math.cos(angle) * bullet_speed
                    dy = math.sin(angle) * bullet_speed
                    bullets.append([player_pos[0], player_pos[1], dx, dy])
                    pistol_sound.play()

            keys = pygame.key.get_pressed()

            # Move left/right
            if keys[pygame.K_a] and player_pos[0] - player_size // 2 > 0:
                player_pos[0] -= player_speed
                walk_cycle += 0.2
            elif keys[pygame.K_d] and player_pos[0] + player_size // 2 < WIDTH:
                player_pos[0] += player_speed
                walk_cycle += 0.2
            else:
                walk_cycle = 0

            # Jump
            if keys[pygame.K_SPACE] and on_ground:
                velocity_y = player_jump
                on_ground = False

            # Gravity
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

            # Move zombies
            for zombie in zombies:
                if zombie[0] < player_pos[0]:
                    zombie[0] += zombie_speed
                else:
                    zombie[0] -= zombie_speed
                zombie[2] += 0.2

            # Bullet-zombie collisions
            hit_zombies = []
            for bullet in bullets:
                for zombie in zombies:
                    dist = math.hypot(bullet[0]-zombie[0], bullet[1]-zombie[1])
                    if dist < zombie_size // 2:
                        hit_zombies.append(zombie)
                        score += 1
            for zombie in hit_zombies:
                if zombie in zombies:
                    zombies.remove(zombie)

            # Zombie-player collision
            for zombie in zombies:
                dist = math.hypot(player_pos[0]-zombie[0], player_pos[1]-zombie[1])
                if dist < (player_size + zombie_size) // 2:
                    if not game_over_screen(score, player_name):
                        running = False

            draw_player_with_gun(player_pos, walk_cycle)
            for zombie in zombies:
                draw_zombie_stickman((zombie[0], zombie[1]), zombie[2])
            draw_bullets(bullets)
            show_score(score, player_name)

            pygame.display.flip()
            clock.tick(60)

        if not game_over_screen(score, player_name):
            break

if __name__ == "__main__":
    main()
