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
player_shoot_limit = 5
player_shoot_count = 0
player_invincible_duration = 2000
player_invincible_end_time = 0
player_bullet_damage = 1  # Default attack power

# Item setup
item_img = pygame.image.load('picture/item.png')
item_img = pygame.transform.scale(item_img, (30, 30))
item_rect = item_img.get_rect(midbottom=(random.randint(0, WIDTH), 0))

# Bullet setup
bullets = []
bullet_speed = 8
bullet_magazine_capacity = 10000000000000000000000000000000
bullet_magazine = bullet_magazine_capacity

# Enemy setup
enemies = []
enemy_speed = 2
enemy_spawn_delay = 100
last_enemy_spawn = pygame.time.get_ticks()

# Boss setup
boss_rect = boss_img.get_rect(midbottom=(WIDTH//2, 0))
boss_speed = 2
boss_health = 500
boss_active = False
boss_attack_delay = 3000
last_boss_attack = pygame.time.get_ticks()
boss_bullets = []  # List to store boss bullets

# Score setup
score = 0
font = pygame.font.Font(None, 36)

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

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_rect.left > 0:
        player_rect.x -= player_speed
    if keys[pygame.K_RIGHT] and player_rect.right < WIDTH:
        player_rect.x += player_speed

    # Shoot bullets
    now = pygame.time.get_ticks()
    if keys[pygame.K_SPACE] and now - player_last_shot > player_shoot_cooldown and player_shoot_count < player_shoot_limit:
        player_last_shot = now
        bullet = bullet_img.get_rect(midtop=player_rect.midtop)
        bullets.append(bullet)
        player_shoot_count += 1

    # Move bullets and check collisions
    for bullet in bullets:
        bullet.y -= bullet_speed
        if bullet.bottom < 0:
            bullets.remove(bullet)

    # Bullet and enemy collision check
    for bullet in bullets:
        for enemy in enemies:
            if bullet.colliderect(enemy[0]):
                bullets.remove(bullet)  # Remove bullet
                enemies.remove(enemy)  # Remove enemy
                score += 1  # Increase score for enemy kill
                break  # Stop checking collision with other enemies

    # Spawn enemies
    now = pygame.time.get_ticks()
    if now - last_enemy_spawn > enemy_spawn_delay:
        last_enemy_spawn = now
        enemy_rect = enemy_img.get_rect(midbottom=(random.randint(0, WIDTH), 0))
        enemies.append([enemy_rect, random.choice([-1, 1]) * enemy_speed])

    # Move enemies
    for enemy in enemies:
        enemy[0].y += enemy[1]
        if enemy[0].top > HEIGHT:
            enemies.remove(enemy)
            score += 1  # Increase score for enemy kill

    # Spawn boss
    if not boss_active:
        now = pygame.time.get_ticks()
        if now - last_boss_attack > boss_attack_delay:
            last_boss_attack = now
            boss_active = True

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
            boss_bullet = boss_img.get_rect(midbottom=boss_rect.midbottom)
            boss_bullets.append(boss_bullet)

    # Move boss bullets
    for boss_bullet in boss_bullets:
        boss_bullet.y += bullet_speed
        if boss_bullet.top > HEIGHT:
            boss_bullets.remove(boss_bullet)

    # Collision check
    for enemy in enemies:
        if player_rect.colliderect(enemy[0]):
            player_health -= 10
            enemies.remove(enemy)
            if player_health <= 0:
                running = False

    # Player and boss collision check
    if boss_active and player_rect.colliderect(boss_rect):
        player_health -= 20
        if player_health <= 0:
            running = False

    # Player and boss bullet collision check
    for boss_bullet in boss_bullets:
        if player_rect.colliderect(boss_bullet):
            player_health -= 20
            boss_bullets.remove(boss_bullet)
            if player_health <= 0:
                running = False

    # Draw everything on the screen
    screen.blit(background_img, (0, 0))
    screen.blit(player_img, player_rect)
    for bullet in bullets:
        pygame.draw.rect(screen, RED, bullet)
    for enemy in enemies:
        screen.blit(enemy_img, enemy[0])
    if boss_active:
        screen.blit(boss_img, boss_rect)
        for boss_bullet in boss_bullets:
            pygame.draw.rect(screen, RED, boss_bullet)

    # Draw items
    screen.blit(item_img, item_rect)

    # Display score and player health
    score_text = font.render("Score: " + str(score), True, WHITE)
    health_text = font.render("Health: " + str(player_health), True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(health_text, (10, 40))

    pygame.display.flip()
    pygame.time.Clock().tick(60)

    # Exit
pygame.quit()
sys.exit()  