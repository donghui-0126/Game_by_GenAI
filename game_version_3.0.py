import pygame
import sys
import random

# Initialization
pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Plane Shooting Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Load images
background_img = pygame.image.load('picture/background.png')
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
player_img = pygame.image.load('picture/player.png')
player_img = pygame.transform.scale(player_img, (50, 50))
enemy_img = pygame.image.load('picture/enemy.png')
enemy_img = pygame.transform.scale(enemy_img, (50, 50))
boss_img = pygame.image.load('picture/boss.png')
boss_img = pygame.transform.scale(boss_img, (100, 100))
bullet_img = pygame.Surface((9, 15))
bullet_img.fill(RED)

# Player setup
player_rect = player_img.get_rect(centerx=WIDTH//2, bottom=HEIGHT-10)
player_speed = 5
player_health = 10  # Initial player health
player_shoot_cooldown = 100
player_last_shot = pygame.time.get_ticks()
player_max_bullets = 1000  # Maximum number of bullets that can be fired in a row
player_remaining_bullets = player_max_bullets  # Initialize remaining bullets
player_invincible_duration = 2000
player_invincible_end_time = 0
player_bullet_damage = 10  # Default attack power
player_boss_bullet_damage = 2  # Increased damage against boss

# Item setup
item_img = pygame.image.load('picture/item.png')
item_img = pygame.transform.scale(item_img, (30, 30))
item_rect = item_img.get_rect(midbottom=(random.randint(0, WIDTH), 0))

# Boss Damage item setup
boss_damage_item_img = pygame.image.load('picture/item.png')
boss_damage_item_img = pygame.transform.scale(boss_damage_item_img, (30, 30))
boss_damage_item_rect = boss_damage_item_img.get_rect(midbottom=(random.randint(0, WIDTH), 0))

# Bullet setup
bullets = []
bullet_speed = 8

# Enemy setup
enemies = []
enemy_speed = 2
enemy_spawn_delay = 1500
last_enemy_spawn = pygame.time.get_ticks()


# Boss setup
boss_rect = boss_img.get_rect(midbottom=(WIDTH//2, 0))
boss_speed = 2
boss_health = 300  # Reduced boss health
boss_active = False
boss_attack_delay = 3000
last_boss_attack = pygame.time.get_ticks()
boss_bullets = []  # List to store boss bullets
boss_vulnerable_zone = pygame.Rect(boss_rect.left + 20, boss_rect.top + 20, 60, 60)  # Boss vulnerable zone

# Score setup
score = 0
font = pygame.font.Font(None, 36)

# Difficulty level setup
difficulty_level = 1
max_difficulty_level = 5
difficulty_increase_score = 1  # Score required to increase difficulty level

# Game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Item collision check
    if player_rect.colliderect(item_rect):
        player_bullet_damage += 1
        item_rect.bottom = 0
        item_rect.centerx = random.randint(0, WIDTH)

    # Boss Damage item collision check
    if player_rect.colliderect(boss_damage_item_rect):
        player_boss_bullet_damage += 1  # Increase damage against boss
        boss_damage_item_rect.bottom = 0
        boss_damage_item_rect.centerx = random.randint(0, WIDTH)

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_rect.left > 0:
        player_rect.x -= player_speed
    if keys[pygame.K_RIGHT] and player_rect.right < WIDTH:
        player_rect.x += player_speed

    # Shoot bullets
    now = pygame.time.get_ticks()
    if keys[pygame.K_SPACE] and now - player_last_shot > player_shoot_cooldown and player_remaining_bullets > 0:
        player_last_shot = now
        bullet = bullet_img.get_rect(midtop=player_rect.midtop)
        bullets.append(bullet)
        player_remaining_bullets -= 1  # Decrement remaining bullets

    # Move bullets and check collisions
    for bullet in bullets[:]:  # Iterate over a copy of the list to avoid modifying the original list
        bullet.y -= bullet_speed
        if bullet.bottom < 0:
            bullets.remove(bullet)
            player_remaining_bullets = player_max_bullets  # Reset remaining bullets when all bullets go off-screen

        # Bullet and enemy collision check
        for enemy in enemies:
            if bullet.colliderect(enemy[0]):
                bullets.remove(bullet)  # Remove bullet
                enemies.remove(enemy)  # Remove enemy
                score += 1  # Increase score for enemy kill
                player_remaining_bullets = player_max_bullets  # Reset remaining bullets when all bullets hit enemies
                break  # Stop checking collision with other enemies

        # Bullet and boss collision check
        if boss_active:
            if bullet.colliderect(boss_rect):
                bullets.remove(bullet)  # Remove bullet
                if bullet.colliderect(boss_vulnerable_zone):
                    boss_health -= player_boss_bullet_damage  # Increased damage in vulnerable zone
                else:
                    boss_health -= player_bullet_damage  # Regular damage
            if boss_health <= 0:
                boss_active = False
                running = False  # Game over condition after defeating the boss


    # Spawn enemies
    now = pygame.time.get_ticks()
    if now - last_enemy_spawn > enemy_spawn_delay / (difficulty_level + 1):  # Increase enemy spawn rate with difficulty level
        last_enemy_spawn = now
        enemy_rect = enemy_img.get_rect(midbottom=(random.randint(0, WIDTH), 0))
        enemies.append([enemy_rect, random.choice([-1, 1]) * (enemy_speed + difficulty_level)])  # Increase enemy speed with difficulty level

    # Move enemies
    for enemy in enemies:
        enemy[0].y += enemy[1]
        if enemy[0].top > HEIGHT:
            enemies.remove(enemy)
            score += 1  # Increase score for enemy kill

    # Increase difficulty level
    if score >= difficulty_increase_score * difficulty_level:
        difficulty_level += 1
        if difficulty_level > max_difficulty_level:
            difficulty_level = max_difficulty_level

    # Spawn boss
    if not boss_active and difficulty_level == max_difficulty_level:
        now = pygame.time.get_ticks()
        if now - last_boss_attack > boss_attack_delay:
            last_boss_attack = now
            boss_active = True
            # Create boss bullets
            boss_bullet_rect = bullet_img.get_rect(midbottom=boss_rect.midbottom)
            boss_bullets.append(boss_bullet_rect)

    # Move boss
    if boss_active:
        if boss_rect.top < HEIGHT / 4:
            boss_rect.y += boss_speed
        else:
            if player_rect.centerx < boss_rect.centerx:
                boss_rect.x -= boss_speed
            elif player_rect.centerx > boss_rect.centerx:
                boss_rect.x += boss_speed
        if boss_rect.left < 0 or boss_rect.right > WIDTH:
            boss_speed *= -1
        if boss_rect.top > HEIGHT:
            boss_active = False

        # Boss firing bullets
        now = pygame.time.get_ticks()
        if now - last_boss_attack > boss_attack_delay:
            last_boss_attack = now
            boss_bullet_rect = bullet_img.get_rect(midbottom=boss_rect.midbottom)
            boss_bullets.append(boss_bullet_rect)

    # Move boss bullets
    for boss_bullet in boss_bullets[:]:
        boss_bullet.y += bullet_speed
        if boss_bullet.top > HEIGHT:
            boss_bullets.remove(boss_bullet)

        # Check boss bullet and player collision
        if boss_bullet.colliderect(player_rect):
            if now - player_invincible_end_time > player_invincible_duration:
                player_health -= 1
                player_invincible_end_time = now

    # Player health check
    if player_health <= 0:
        running = False  # End game loop

    # Draw everything
    screen.blit(background_img, (0, 0))
    screen.blit(player_img, player_rect)
    screen.blit(item_img, item_rect)
    screen.blit(boss_damage_item_img, boss_damage_item_rect)

    for bullet in bullets:
        screen.blit(bullet_img, bullet)

    for enemy in enemies:
        screen.blit(enemy_img, enemy[0])

    if boss_active:
        screen.blit(boss_img, boss_rect)
        for boss_bullet in boss_bullets:
            screen.blit(bullet_img, boss_bullet)

        pygame.draw.rect(screen, RED, (boss_vulnerable_zone.left, boss_vulnerable_zone.top, boss_vulnerable_zone.width, boss_vulnerable_zone.height), 2)  # Draw boss vulnerable zone

    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    health_text = font.render(f"Health: {player_health}", True, WHITE)
    screen.blit(health_text, (10, 50))

    difficulty_text = font.render(f"Difficulty Level: {difficulty_level}", True, WHITE)
    screen.blit(difficulty_text, (10, 90))

    boss_health_text = font.render("Boss Health: " + str(boss_health), True, WHITE)
    screen.blit(boss_health_text, (10, 70))

    pygame.display.flip()

# Quit the game
pygame.quit()
sys.exit()