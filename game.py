import pygame
import sys
import random

# 초기화
pygame.init()

# 화면 설정
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("비행기 슈팅 게임")

# 색상
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# 이미지 로드
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

# 플레이어 설정
player_rect = player_img.get_rect(centerx=WIDTH//2, bottom=HEIGHT-10)
player_speed = 5
player_health = 10
player_shoot_cooldown = 100
player_last_shot = pygame.time.get_ticks()
player_shoot_limit = 5
player_shoot_count = 0
player_invincible_duration = 2000
player_invincible_end_time = 0
player_bullet_damage = 1  # 기본 공격력

# 아이템 설정
item_img = pygame.image.load('picture/item.png')
item_img = pygame.transform.scale(item_img, (30, 30))
item_rect = item_img.get_rect(midbottom=(random.randint(0, WIDTH), 0))

# 총알 설정
bullets = []
bullet_speed = 8
bullet_reload_time = 3000  # 3초로 변경
last_reload_time = pygame.time.get_ticks()
bullet_magazine_capacity = 10000000000000000000000000000000
bullet_magazine = bullet_magazine_capacity

# 적 설정
enemies = []
enemy_speed = 2
enemy_spawn_delay = 100
last_enemy_spawn = pygame.time.get_ticks()

# 보스 설정
boss_rect = boss_img.get_rect(midbottom=(WIDTH//2, 0))
boss_speed = 2
boss_health = 500
boss_active = False
boss_attack_delay = 3000
last_boss_attack = pygame.time.get_ticks()

# 스코어 설정
score = 0
font = pygame.font.Font(None, 36)

# 게임 루프
running = True
while running:
    # 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:  # R 키를 누르면 재장전
                if pygame.time.get_ticks() - last_reload_time > bullet_reload_time:
                    bullet_magazine = bullet_magazine_capacity
                    last_reload_time = pygame.time.get_ticks()

    # 아이템 충돌 체크
    if player_rect.colliderect(item_rect):
        player_bullet_damage += 1
        item_rect.bottom = 0
        item_rect.centerx = random.randint(0, WIDTH)

    # 플레이어 이동
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_rect.left > 0:
        player_rect.x -= player_speed
    if keys[pygame.K_RIGHT] and player_rect.right < WIDTH:
        player_rect.x += player_speed
    
    # 총알 발사
    now = pygame.time.get_ticks()
    if keys[pygame.K_SPACE] and now - player_last_shot > player_shoot_cooldown and player_shoot_count < player_shoot_limit:
        if bullet_magazine > 0:
            player_last_shot = now
            bullet = bullet_img.get_rect(midtop=player_rect.midtop)
            bullets.append(bullet)
            player_shoot_count += 1
            bullet_magazine -= 0
    
    # 총알 이동 및 충돌 체크
    for bullet in bullets:
        bullet.y -= bullet_speed
        if bullet.bottom < 0:
            bullets.remove(bullet)
    
    # 총알과 적의 충돌 체크
    for bullet in bullets:
        for enemy in enemies:
            if bullet.colliderect(enemy[0]):
                bullets.remove(bullet)  # 총알 제거
                enemies.remove(enemy)  # 적 제거
                score += 1  # 적 처치 시 스코어 증가
                break  # 다른 적과의 충돌 체크를 하지 않도록 중단
    
    # 총알 이동
    for bullet in bullets:
        bullet.y -= bullet_speed
        if bullet.bottom < 0:
            bullets.remove(bullet)
    
    # 적 비행기 생성
    now = pygame.time.get_ticks()
    if now - last_enemy_spawn > enemy_spawn_delay:
        last_enemy_spawn = now
        enemy_rect = enemy_img.get_rect(midbottom=(random.randint(0, WIDTH), 0))
        enemies.append([enemy_rect, random.choice([-1, 1]) * enemy_speed])
    
    # 적 비행기 이동
    for enemy in enemies:
        enemy[0].y += enemy[1]
        if enemy[0].top > HEIGHT:
            enemies.remove(enemy)
            score += 1  # 적 처치 시 스코어 증가
    
    # 보스 비행기 등장
    if not boss_active:
        now = pygame.time.get_ticks()
        if now - last_boss_attack > boss_attack_delay:
            last_boss_attack = now
            boss_active = True
    
    # 보스 비행기 이동
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
    
    # 충돌 체크
    for enemy in enemies:
        if player_rect.colliderect(enemy[0]):
            player_health -= 10
            enemies.remove(enemy)
            if player_health <= 0:
                running = False
    
    # 보스와 플레이어 충돌 체크
    if boss_active and player_rect.colliderect(boss_rect):
        player_health -= 20
        if player_health <= 0:
            running = False
    
    # 화면 그리기
    screen.blit(background_img, (0, 0))
    screen.blit(player_img, player_rect)
    for bullet in bullets:
        pygame.draw.rect(screen, RED, bullet)
    for enemy in enemies:
        screen.blit(enemy_img, enemy[0])
    if boss_active:
        screen.blit(boss_img, boss_rect)
    
    # 아이템 그리기
    screen.blit(item_img, item_rect)
    
    # 스코어 표시
    score_text = font.render("Score: " + str(score), True, WHITE)
    screen.blit(score_text, (10, 10))
    
    pygame.display.flip()
    pygame.time.Clock().tick(60)

# 종료
pygame.quit()
sys.exit()
