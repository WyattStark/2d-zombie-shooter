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
DARK_GRAY = (64, 64, 64)
BOSS_GREEN = (0, 100, 0)
BOSS_PURPLE = (128, 0, 128)

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

# Bosses
boss_size = 30
boss_speeds = {2: 0.8, 3: 1.2, 4: [1.0, 1.4]}
boss_max_healths = {2: 100, 3: 150, 4: [200, 250]}
boss_damage = {'pistol': 2, 'ar': 5, 'shotgun': 25}

# Bullets
bullet_speeds = {'pistol': 10, 'ar': 15, 'shotgun': 12}
fire_rates = {'pistol': 0, 'ar': 100, 'shotgun': 1000}

# Weapon pickups
pickup_range = 100
weapon_pickups = [
    {'type': 'ar', 'pos': [WIDTH * 0.75, HEIGHT - 20], 'size': [30, 10]},
    {'type': 'shotgun', 'pos': [WIDTH * 0.25, HEIGHT - 20], 'size': [30, 10]}
]

# Ground
GROUND_HEIGHT = 75

# Background
background = pygame.image.load('night_city.png').convert()

# Load sounds
pistol_sound = pygame.mixer.Sound('pistol_shot.wav')
ar_sound = pygame.mixer.Sound('ar_shot.wav')
shotgun_sound = pygame.mixer.Sound('shotgun_shot.wav')

# Fonts
font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 72)

# Game state
high_score = 0
god_mode = False
noclip = False
level3_unlocked = False
level4_unlocked = False

# Create 8-bit AR sprite
def create_ar_sprite():
    ar_surface = pygame.Surface((32, 16), pygame.SRCALPHA)
    pygame.draw.rect(ar_surface, GRAY, (16, 4, 12, 4))
    pygame.draw.rect(ar_surface, DARK_GRAY, (8, 4, 8, 8))
    pygame.draw.rect(ar_surface, BLACK, (8, 12, 4, 4))
    pygame.draw.rect(ar_surface, DARK_GRAY, (12, 8, 4, 8))
    return ar_surface

# Create 8-bit shotgun sprite
def create_shotgun_sprite():
    shotgun_surface = pygame.Surface((32, 16), pygame.SRCALPHA)
    pygame.draw.rect(shotgun_surface, GRAY, (16, 4, 12, 6))  # Barrel
    pygame.draw.rect(shotgun_surface, DARK_GRAY, (8, 4, 8, 10))  # Body
    pygame.draw.rect(shotgun_surface, BLACK, (8, 14, 4, 2))  # Trigger
    return shotgun_surface

ar_sprite = create_ar_sprite()
shotgun_sprite = create_shotgun_sprite()

def draw_ground():
    pygame.draw.rect(screen, BROWN, (0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT))

def draw_player_with_gun(player_pos, walk_cycle, weapon_type):
    head_radius = 15
    body_length = 40
    arm_length = 25
    leg_length = 30
    color = BLACK

    x, y = player_pos
    mx, my = pygame.mouse.get_pos()
    angle = math.atan2(my - y, mx - x)

    # Head
    pygame.draw.circle(screen, color, (int(x), int(y - body_length // 2 - head_radius)), head_radius, 2)

    # Body
    pygame.draw.line(screen, color, (x, y - body_length // 2), (x, y + body_length // 2), 2)

    # Left arm
    pygame.draw.line(screen, color, (x, y - 10), (x - arm_length, y), 2)

    # Right arm
    arm_end_x = x + math.cos(angle) * arm_length
    arm_end_y = y + math.sin(angle) * arm_length
    pygame.draw.line(screen, color, (x, y - 10), (arm_end_x, arm_end_y), 2)

    # Legs
    leg_offset = math.sin(walk_cycle) * 10
    pygame.draw.line(screen, color, (x, y + body_length // 2),
                     (x - arm_length + leg_offset, y + body_length // 2 + leg_length), 2)
    pygame.draw.line(screen, color, (x, y + body_length // 2),
                     (x + arm_length - leg_offset, y + body_length // 2 + leg_length), 2)

    # Gun
    if weapon_type == 'pistol':
        gun_width = 10
        gun_height = 4
        gun_x = arm_end_x
        gun_y = arm_end_y - gun_height // 2
        pygame.draw.rect(screen, BLACK, (gun_x, gun_y, gun_width, gun_height))
    elif weapon_type == 'ar':
        rotated_ar = pygame.transform.rotate(ar_sprite, -math.degrees(angle))
        ar_rect = rotated_ar.get_rect(center=(arm_end_x + math.cos(angle) * 10, arm_end_y + math.sin(angle) * 10))
        screen.blit(rotated_ar, ar_rect.topleft)
    else:  # Shotgun
        rotated_shotgun = pygame.transform.rotate(shotgun_sprite, -math.degrees(angle))
        shotgun_rect = rotated_shotgun.get_rect(center=(arm_end_x + math.cos(angle) * 10, arm_end_y + math.sin(angle) * 10))
        screen.blit(rotated_shotgun, shotgun_rect.topleft)

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

def draw_boss(boss, walk_cycle, level, boss_index=0):
    head_radius = 10
    body_length = 25
    arm_length = 15
    leg_length = 20
    color = BOSS_GREEN if level == 2 or (level == 4 and boss_index == 0) else BOSS_PURPLE

    x, y = boss['pos']
    health = boss['health']

    # Slouched posture
    head_y_offset = 4
    body_angle = math.radians(10)
    body_start_y = y - body_length // 2 + head_y_offset
    body_end_x = x + math.sin(body_angle) * body_length
    body_end_y = y + body_length // 2 + head_y_offset

    # Head
    pygame.draw.circle(screen, color, (int(x), int(body_start_y - head_radius)), head_radius, 2)

    # Body
    pygame.draw.line(screen, color, (x, body_start_y), (body_end_x, body_end_y), 2)

    # Arms
    arm_start_y = body_start_y + 6
    pygame.draw.line(screen, color, (x, arm_start_y), (x + arm_length, arm_start_y + 4), 2)
    pygame.draw.line(screen, color, (x, arm_start_y), (x - arm_length, arm_start_y + 4), 2)

    # Legs
    leg_offset = math.sin(walk_cycle) * 6
    leg_start_y = body_end_y
    pygame.draw.line(screen, color, (body_end_x, leg_start_y),
                     (body_end_x - arm_length + leg_offset, leg_start_y + leg_length), 2)
    pygame.draw.line(screen, color, (body_end_x, leg_start_y),
                     (body_end_x + arm_length - leg_offset, leg_start_y + leg_length), 2)

    # Health bar
    health_bar_width = 50
    health_bar_height = 5
    max_health = boss_max_healths[level][boss_index] if level == 4 else boss_max_healths[level]
    health_ratio = health / max_health
    pygame.draw.rect(screen, WHITE, (x - health_bar_width // 2, body_start_y - head_radius - 20, health_bar_width, health_bar_height), 1)
    pygame.draw.rect(screen, RED, (x - health_bar_width // 2, body_start_y - head_radius - 20, health_bar_width * health_ratio, health_bar_height))

    # Boss name
    name_text = font.render(f"Boss {boss_index + 1}" if level == 4 else "Boss", True, WHITE)
    screen.blit(name_text, (x - name_text.get_width() // 2, body_start_y - head_radius - 35))

def draw_bullets(bullets):
    for bullet in bullets:
        pygame.draw.circle(screen, RED, (int(bullet[0]), int(bullet[1])), 5)

def draw_weapon_pickups(weapon_pickups, player_pos):
    for weapon in weapon_pickups:
        sprite = ar_sprite if weapon['type'] == 'ar' else shotgun_sprite
        pickup_rect = sprite.get_rect(center=weapon['pos'])
        screen.blit(sprite, pickup_rect.topleft)
        dist = math.hypot(player_pos[0] - weapon['pos'][0], player_pos[1] - weapon['pos'][1])
        if dist < pickup_range:
            prompt = font.render("Press E to Pick Up", True, WHITE)
            screen.blit(prompt, (weapon['pos'][0] - prompt.get_width()//2, weapon['pos'][1] - 30))

def draw_console(console_active, console_input):
    if console_active:
        console_rect = pygame.Rect(0, HEIGHT - 60, WIDTH, 60)
        pygame.draw.rect(screen, BLACK, console_rect)
        pygame.draw.rect(screen, WHITE, console_rect, 2)
        title_text = font.render("DEV Console", True, WHITE)
        screen.blit(title_text, (10, HEIGHT - 50))
        input_text = font.render("> " + console_input, True, WHITE)
        screen.blit(input_text, (10, HEIGHT - 30))

def draw_notifications(notifications, current_time):
    for i, notification in enumerate(notifications[:]):
        if current_time - notification['timestamp'] > 2000:  # 2 seconds
            notifications.remove(notification)
            continue
        text_surface = font.render(notification['text'], True, WHITE)
        screen.blit(text_surface, (WIDTH//2 - text_surface.get_width()//2, 50 + i * 30))

def show_score(score, player_name):
    img = font.render(f"Player: {player_name}  Score: {score}", True, WHITE)
    screen.blit(img, (10, 10))

def game_over_screen(score, player_name):
    global high_score
    high_score = max(high_score, score)
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
                    return True
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
    return False

def menu_screen():
    global high_score, level3_unlocked, level4_unlocked
    player_name = ""
    input_active = False
    in_level_select = False
    in_command_list = False
    input_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 50, 300, 40)
    play_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 20, 200, 50)
    level_select_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 80, 200, 50)
    command_list_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 140, 200, 50)
    level1_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 100, 200, 50)
    level2_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 40, 200, 50)
    level3_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 20, 200, 50)
    level4_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 80, 200, 50)
    back_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 140, 200, 50)
    title_text = big_font.render("Zombie Shooter", True, WHITE)
    instruction_text = font.render("Enter Name and Select Option", True, WHITE)
    level_select_title = big_font.render("Level Select", True, WHITE)
    command_list_title = big_font.render("Command List", True, WHITE)
    input_prompt = font.render("Player Name:", True, WHITE)
    play_text = font.render("Play", True, BLACK)
    level_select_text = font.render("Level Select", True, BLACK)
    command_list_text = font.render("Command List", True, BLACK)
    level1_text = font.render("Level 1", True, BLACK)
    level2_text = font.render("Level 2" + (" (Locked)" if high_score < 10 else ""), True, BLACK if high_score >= 10 else GRAY)
    level3_text = font.render("Level 3" + (" (Locked)" if not level3_unlocked else ""), True, BLACK if level3_unlocked else GRAY)
    level4_text = font.render("Level 4" + (" (Locked)" if not level4_unlocked else ""), True, BLACK if level4_unlocked else GRAY)
    back_text = font.render("Back", True, BLACK)
    commands_title = font.render("Available Commands:", True, WHITE)
    command1_text = font.render("god - Enables infinite health", True, WHITE)
    command2_text = font.render("noclip - Enables flying with W/A/S/D", True, WHITE)

    while True:
        screen.fill(BLACK)
        if not in_level_select and not in_command_list:
            # Main menu
            screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//2 - 150))
            screen.blit(instruction_text, (WIDTH//2 - instruction_text.get_width()//2, HEIGHT//2 - 80))
            screen.blit(input_prompt, (WIDTH//2 - 150, HEIGHT//2 - 80))

            pygame.draw.rect(screen, WHITE if input_active else GRAY, input_rect, 2)
            name_surface = font.render(player_name, True, WHITE)
            screen.blit(name_surface, (input_rect.x + 5, input_rect.y + 5))

            pygame.draw.rect(screen, GREEN, play_button)
            screen.blit(play_text, (play_button.x + play_button.width//2 - play_text.get_width()//2,
                                    play_button.y + play_button.height//2 - play_text.get_height()//2))

            pygame.draw.rect(screen, GREEN, level_select_button)
            screen.blit(level_select_text, (level_select_button.x + level_select_button.width//2 - level_select_text.get_width()//2,
                                           level_select_button.y + level_select_button.height//2 - level_select_text.get_height()//2))

            pygame.draw.rect(screen, GREEN, command_list_button)
            screen.blit(command_list_text, (command_list_button.x + command_list_button.width//2 - command_list_text.get_width()//2,
                                            command_list_button.y + command_list_button.height//2 - command_list_text.get_height()//2))
        elif in_level_select:
            # Level select tab
            screen.blit(level_select_title, (WIDTH//2 - level_select_title.get_width()//2, HEIGHT//2 - 150))

            pygame.draw.rect(screen, GREEN, level1_button)
            screen.blit(level1_text, (level1_button.x + level1_button.width//2 - level1_text.get_width()//2,
                                      level1_button.y + level1_button.height//2 - level1_text.get_height()//2))

            pygame.draw.rect(screen, GREEN if high_score >= 10 else GRAY, level2_button)
            screen.blit(level2_text, (level2_button.x + level2_button.width//2 - level2_text.get_width()//2,
                                      level2_button.y + level2_button.height//2 - level2_text.get_height()//2))

            pygame.draw.rect(screen, GREEN if level3_unlocked else GRAY, level3_button)
            screen.blit(level3_text, (level3_button.x + level3_button.width//2 - level3_text.get_width()//2,
                                      level3_button.y + level3_button.height//2 - level3_text.get_height()//2))

            pygame.draw.rect(screen, GREEN if level4_unlocked else GRAY, level4_button)
            screen.blit(level4_text, (level4_button.x + level4_button.width//2 - level4_text.get_width()//2,
                                      level4_button.y + level4_button.height//2 - level4_text.get_height()//2))

            pygame.draw.rect(screen, GREEN, back_button)
            screen.blit(back_text, (back_button.x + back_button.width//2 - back_text.get_width()//2,
                                    back_button.y + back_button.height//2 - back_text.get_height()//2))
        else:
            # Command list tab
            screen.blit(command_list_title, (WIDTH//2 - command_list_title.get_width()//2, HEIGHT//2 - 150))
            screen.blit(commands_title, (WIDTH//2 - commands_title.get_width()//2, HEIGHT//2 - 60))
            screen.blit(command1_text, (WIDTH//2 - command1_text.get_width()//2, HEIGHT//2 - 20))
            screen.blit(command2_text, (WIDTH//2 - command2_text.get_width()//2, HEIGHT//2 + 20))
            pygame.draw.rect(screen, GREEN, back_button)
            screen.blit(back_text, (back_button.x + back_button.width//2 - back_text.get_width()//2,
                                    back_button.y + back_button.height//2 - back_text.get_height()//2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not in_level_select and not in_command_list:
                    if input_rect.collidepoint(event.pos):
                        input_active = True
                    elif play_button.collidepoint(event.pos) and player_name.strip():
                        return player_name.strip(), 1
                    elif level_select_button.collidepoint(event.pos):
                        in_level_select = True
                        input_active = False
                    elif command_list_button.collidepoint(event.pos):
                        in_command_list = True
                        input_active = False
                    else:
                        input_active = False
                elif in_level_select:
                    if level1_button.collidepoint(event.pos) and player_name.strip():
                        return player_name.strip(), 1
                    elif level2_button.collidepoint(event.pos) and player_name.strip() and high_score >= 10:
                        return player_name.strip(), 2
                    elif level3_button.collidepoint(event.pos) and player_name.strip() and level3_unlocked:
                        return player_name.strip(), 3
                    elif level4_button.collidepoint(event.pos) and player_name.strip() and level4_unlocked:
                        return player_name.strip(), 4
                    elif back_button.collidepoint(event.pos):
                        in_level_select = False
                elif in_command_list:
                    if back_button.collidepoint(event.pos):
                        in_command_list = False
            elif event.type == pygame.KEYDOWN and not in_level_select and not in_command_list:
                if input_active:
                    if event.key == pygame.K_RETURN and player_name.strip():
                        return player_name.strip(), 1
                    elif event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    elif event.unicode.isprintable() and len(player_name) < 20:
                        player_name += event.unicode

        clock.tick(60)

def main():
    global god_mode, noclip, level3_unlocked, level4_unlocked
    ar_channel = pygame.mixer.Channel(0)
    was_mouse_pressed = False

    while True:
        player_name, start_level = menu_screen()
        player_pos = [WIDTH // 2, HEIGHT - GROUND_HEIGHT - player_size // 2]
        velocity_y = 0
        on_ground = True
        bullets = []
        zombies = []
        boss = None
        bosses = []
        score = 0
        walk_cycle = 0
        weapon_type = 'pistol'
        last_shot_time = 0
        weapon_pickups_reset = [
            {'type': 'ar', 'pos': [WIDTH * 0.75, HEIGHT - 20], 'size': [30, 10]},
            {'type': 'shotgun', 'pos': [WIDTH * 0.25, HEIGHT - 20], 'size': [30, 10]}
        ]
        weapon_pickups = weapon_pickups_reset.copy()
        level = start_level
        console_active = False
        console_input = ""
        notifications = []

        if level == 2:
            boss = {'pos': [WIDTH // 2, HEIGHT - GROUND_HEIGHT - boss_size // 2], 'health': boss_max_healths[2], 'walk_cycle': 0}
            zombies.clear()
        elif level == 3:
            boss = {'pos': [WIDTH // 2, HEIGHT - GROUND_HEIGHT - boss_size // 2], 'health': boss_max_healths[3], 'walk_cycle': 0}
            zombies.clear()
        elif level == 4:
            bosses = [
                {'pos': [WIDTH // 3, HEIGHT - GROUND_HEIGHT - boss_size // 2], 'health': boss_max_healths[4][0], 'walk_cycle': 0},
                {'pos': [2 * WIDTH // 3, HEIGHT - GROUND_HEIGHT - boss_size // 2], 'health': boss_max_healths[4][1], 'walk_cycle': 0}
            ]
            zombies.clear()

        running = True
        while running:
            current_time = pygame.time.get_ticks()
            screen.blit(background, (0, 0))
            draw_ground()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKQUOTE:
                        console_active = not console_active
                    elif console_active:
                        if event.key == pygame.K_RETURN:
                            if console_input.lower() == "god":
                                god_mode = True
                                notifications.append({'text': 'Enabled God', 'timestamp': current_time})
                            elif console_input.lower() == "noclip":
                                noclip = not noclip
                                notifications.append({'text': 'Enabled Noclip', 'timestamp': current_time})
                            console_input = ""
                        elif event.key == pygame.K_BACKSPACE:
                            console_input = console_input[:-1]
                        elif event.unicode.isprintable() and len(console_input) < 50:
                            console_input += event.unicode
                    elif event.key == pygame.K_e:
                        for weapon in weapon_pickups[:]:
                            dist = math.hypot(player_pos[0] - weapon['pos'][0], player_pos[1] - weapon['pos'][1])
                            if dist < pickup_range:
                                weapon_type = weapon['type']
                                weapon_pickups.remove(weapon)
                elif event.type == SPAWN_EVENT and not console_active:
                    if level == 1:
                        side = random.choice(['left', 'right'])
                        y_pos = HEIGHT - GROUND_HEIGHT - zombie_size // 2
                        z_walk = random.uniform(0, math.pi * 2)
                        if side == 'left':
                            zombies.append([0, y_pos, z_walk])
                        else:
                            zombies.append([WIDTH, y_pos, z_walk])
                    elif level in [2, 3, 4] and (boss or bosses):
                        min_distance = 200
                        while True:
                            x = random.uniform(0, WIDTH)
                            y = HEIGHT - GROUND_HEIGHT - zombie_size // 2
                            dist = math.hypot(player_pos[0] - x, player_pos[1] - y)
                            if dist >= min_distance:
                                z_walk = random.uniform(0, math.pi * 2)
                                zombies.append([x, y, z_walk])
                                break
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not console_active:
                    if weapon_type in ['pistol', 'shotgun'] and current_time - last_shot_time >= fire_rates[weapon_type]:
                        mx, my = pygame.mouse.get_pos()
                        angle = math.atan2(my - player_pos[1], mx - player_pos[0])
                        dx = math.cos(angle) * bullet_speeds[weapon_type]
                        dy = math.sin(angle) * bullet_speeds[weapon_type]
                        bullets.append([player_pos[0], player_pos[1], dx, dy, weapon_type])
                        if weapon_type == 'pistol':
                            pistol_sound.play()
                        elif weapon_type == 'shotgun':
                            shotgun_sound.play()
                        last_shot_time = current_time

            # Full-auto for AR
            mouse_pressed = pygame.mouse.get_pressed()[0]
            if mouse_pressed and weapon_type == 'ar' and current_time - last_shot_time >= fire_rates['ar'] and not console_active:
                mx, my = pygame.mouse.get_pos()
                angle = math.atan2(my - player_pos[1], mx - player_pos[0])
                dx = math.cos(angle) * bullet_speeds[weapon_type]
                dy = math.sin(angle) * bullet_speeds[weapon_type]
                bullets.append([player_pos[0], player_pos[1], dx, dy, weapon_type])
                if not was_mouse_pressed:
                    ar_channel.play(ar_sound, loops=-1)
                last_shot_time = current_time
            elif not mouse_pressed and was_mouse_pressed:
                ar_channel.stop()
            was_mouse_pressed = mouse_pressed

            keys = pygame.key.get_pressed()

            # Move left/right
            if keys[pygame.K_a] and player_pos[0] - player_size // 2 > 0 and not console_active:
                player_pos[0] -= player_speed
                walk_cycle += 0.2
            elif keys[pygame.K_d] and player_pos[0] + player_size // 2 < WIDTH and not console_active:
                player_pos[0] += player_speed
                walk_cycle += 0.2
            else:
                walk_cycle = 0

            # Move up/down in noclip mode
            if noclip and not console_active:
                if keys[pygame.K_w] and player_pos[1] - player_size // 2 > 0:
                    player_pos[1] -= player_speed
                if keys[pygame.K_s] and player_pos[1] + player_size // 2 < HEIGHT:
                    player_pos[1] += player_speed
            else:
                # Jump
                if keys[pygame.K_SPACE] and on_ground and not console_active:
                    velocity_y = player_jump
                    on_ground = False

                # Gravity
                player_pos[1] += velocity_y
                velocity_y += gravity

                # Stay on ground
                if player_pos[1] >= HEIGHT - GROUND_HEIGHT - player_size // 2:
                    player_pos[1] = HEIGHT - GROUND_HEIGHT - player_size // 2
                    velocity_y = 0
                    on_ground = True

            # Transition to next level
            if level == 1 and score >= 10:
                level = 2
                zombies.clear()
                boss = {'pos': [WIDTH // 2, HEIGHT - GROUND_HEIGHT - boss_size // 2], 'health': boss_max_healths[2], 'walk_cycle': 0}
            elif level == 2 and boss and boss['health'] <= 0:
                level3_unlocked = True
                level = 3
                zombies.clear()
                boss = {'pos': [WIDTH // 2, HEIGHT - GROUND_HEIGHT - boss_size // 2], 'health': boss_max_healths[3], 'walk_cycle': 0}
            elif level == 3 and boss and boss['health'] <= 0:
                level4_unlocked = True
                level = 4
                zombies.clear()
                boss = None
                bosses = [
                    {'pos': [WIDTH // 3, HEIGHT - GROUND_HEIGHT - boss_size // 2], 'health': boss_max_healths[4][0], 'walk_cycle': 0},
                    {'pos': [2 * WIDTH // 3, HEIGHT - GROUND_HEIGHT - boss_size // 2], 'health': boss_max_healths[4][1], 'walk_cycle': 0}
                ]

            # Move zombies
            for zombie in zombies:
                if zombie[0] < player_pos[0]:
                    zombie[0] += zombie_speed
                else:
                    zombie[0] -= zombie_speed
                zombie[2] += 0.2

            # Move boss(es)
            if boss:
                if boss['pos'][0] < player_pos[0]:
                    boss['pos'][0] += boss_speeds[level]
                else:
                    boss['pos'][0] -= boss_speeds[level]
                boss['walk_cycle'] += 0.2
            elif bosses:
                for i, b in enumerate(bosses):
                    if b['pos'][0] < player_pos[0]:
                        b['pos'][0] += boss_speeds[level][i]
                    else:
                        b['pos'][0] -= boss_speeds[level][i]
                    b['walk_cycle'] += 0.2

            # Update bullets
            updated_bullets = []
            for bullet in bullets:
                bullet[0] += bullet[2]
                bullet[1] += bullet[3]
                if 0 <= bullet[0] <= WIDTH and 0 <= bullet[1] <= HEIGHT:
                    updated_bullets.append(bullet)
            bullets = updated_bullets

            # Bullet collisions
            bullets_to_remove = []
            zombies_to_remove = []
            for bullet in bullets:
                bullet_x, bullet_y, _, _, bullet_weapon = bullet
                hit = False
                for zombie in zombies:
                    dist = math.hypot(bullet_x - zombie[0], bullet_y - zombie[1])
                    if dist < zombie_size // 2 and zombie not in zombies_to_remove:
                        zombies_to_remove.append(zombie)
                        bullets_to_remove.append(bullet)
                        score += 1
                        hit = True
                        break
                if not hit:
                    if boss:
                        dist = math.hypot(bullet_x - boss['pos'][0], bullet_y - boss['pos'][1])
                        if dist < boss_size // 2:
                            boss['health'] -= boss_damage[bullet_weapon]
                            bullets_to_remove.append(bullet)
                            if boss['health'] <= 0 and level in [2, 3]:
                                ar_channel.stop()
                                running = False
                    elif bosses:
                        for b in bosses:
                            dist = math.hypot(bullet_x - b['pos'][0], bullet_y - b['pos'][1])
                            if dist < boss_size // 2:
                                b['health'] -= boss_damage[bullet_weapon]
                                bullets_to_remove.append(bullet)
                                break
                        if all(b['health'] <= 0 for b in bosses):
                            ar_channel.stop()
                            running = False

            # Remove hit zombies and bullets
            for zombie in zombies_to_remove:
                if zombie in zombies:
                    zombies.remove(zombie)
            for bullet in bullets_to_remove:
                if bullet in bullets:
                    bullets.remove(bullet)

            # Zombie/boss-player collision
            if not god_mode:
                for zombie in zombies:
                    dist = math.hypot(player_pos[0] - zombie[0], player_pos[1] - zombie[1])
                    if dist < (player_size + zombie_size) // 2:
                        ar_channel.stop()
                        if not game_over_screen(score, player_name):
                            running = False
                if boss:
                    dist = math.hypot(player_pos[0] - boss['pos'][0], player_pos[1] - boss['pos'][1])
                    if dist < (player_size + boss_size) // 2:
                        ar_channel.stop()
                        if not game_over_screen(score, player_name):
                            running = False
                elif bosses:
                    for b in bosses:
                        dist = math.hypot(player_pos[0] - b['pos'][0], player_pos[1] - b['pos'][1])
                        if dist < (player_size + boss_size) // 2:
                            ar_channel.stop()
                            if not game_over_screen(score, player_name):
                                running = False

            draw_weapon_pickups(weapon_pickups, player_pos)
            draw_player_with_gun(player_pos, walk_cycle, weapon_type)
            for zombie in zombies:
                draw_zombie_stickman((zombie[0], zombie[1]), zombie[2])
            if boss:
                draw_boss(boss, boss['walk_cycle'], level)
            elif bosses:
                for i, b in enumerate(bosses):
                    draw_boss(b, b['walk_cycle'], level, i)
            draw_bullets(bullets)
            show_score(score, player_name)
            draw_console(console_active, console_input)
            draw_notifications(notifications, current_time)

            pygame.display.flip()
            clock.tick(60)

        ar_channel.stop()
        god_mode = False
        noclip = False
        if not game_over_screen(score, player_name):
            break

if __name__ == "__main__":
    main()
