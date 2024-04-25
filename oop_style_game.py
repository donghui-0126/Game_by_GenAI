import pygame
import sys
import random

# Initialization
pygame.init()

# Screen setup
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Plane Shooting Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Load images
background_img = pygame.image.load('picture/background.png')
background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('picture/player.png')
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect(centerx=SCREEN_WIDTH//2, bottom=SCREEN_HEIGHT-10)
        self.speed = 5
        self.health = 10
        self.shoot_cooldown = 100
        self.last_shot = pygame.time.get_ticks()
        self.max_bullets = 1000
        self.remaining_bullets = self.max_bullets
        self.invincible_duration = 2000
        self.invincible_end_time = 0
        self.bullet_damage = 10
        self.boss_bullet_damage = 2

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed

    def shoot(self, bullets):
        now = pygame.time.get_ticks()
        if pygame.key.get_pressed()[pygame.K_SPACE] and now - self.last_shot > self.shoot_cooldown and self.remaining_bullets > 0:
            self.last_shot = now
            bullet = Bullet(self.rect.midtop)
            bullets.add(bullet)
            self.remaining_bullets -= 1

    def reset_bullets(self):
        self.remaining_bullets = self.max_bullets

    def draw(self):
        screen.blit(self.image, self.rect)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.image = pygame.image.load('picture/enemy.png')
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.speed = speed

    def move(self):
        self.rect.y += self.speed

    def draw(self):
        screen.blit(self.image, self.rect)


class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('picture/boss.png')
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect(midbottom=(SCREEN_WIDTH//2, 0))
        self.speed = 2
        self.health = 300
        self.active = False
        self.attack_delay = 3000
        self.last_attack = pygame.time.get_ticks()
        self.bullets = pygame.sprite.Group()
        self.vulnerable_zone = pygame.Rect(self.rect.left + 20, self.rect.top + 20, 60, 60)

    def move(self, player):
        if self.rect.top < SCREEN_HEIGHT / 4:
            self.rect.y += self.speed
        else:
            if player.rect.centerx < self.rect.centerx:
                self.rect.x -= self.speed
            elif player.rect.centerx > self.rect.centerx:
                self.rect.x += self.speed
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.speed *= -1
        if self.rect.top > SCREEN_HEIGHT:
            self.active = False

    def attack(self):
        now = pygame.time.get_ticks()
        if now - self.last_attack > self.attack_delay:
            self.last_attack = now
            boss_bullet = Bullet(self.rect.midbottom, True)
            self.bullets.add(boss_bullet)

    def check_collision(self, bullets, player):
        for bullet in bullets:
            if self.rect.colliderect(bullet.rect):
                bullets.remove(bullet)
                if bullet.rect.colliderect(self.vulnerable_zone):
                    self.health -= player.boss_bullet_damage
                else:
                    self.health -= player.bullet_damage
            if self.health <= 0:
                self.active = False

    def draw(self):
        screen.blit(self.image, self.rect)
        for bullet in self.bullets:
            bullet.draw()
        pygame.draw.rect(screen, RED, (self.vulnerable_zone.left, self.vulnerable_zone.top, self.vulnerable_zone.width, self.vulnerable_zone.height), 2)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, position, is_boss_bullet=False):
        super().__init__()
        self.image = pygame.Surface((9, 15))
        self.image.fill(RED)
        self.rect = self.image.get_rect(midbottom=position)
        self.speed = 8 if not is_boss_bullet else -8

    def move(self):
        self.rect.y += self.speed

    def draw(self):
        screen.blit(self.image, self.rect)


class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        super().__init__()
        self.image = pygame.image.load('picture/item.png')
        self.image = pygame.transform.scale(self.image, (30, 30))
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.type = type  # 0 for regular item, 1 for boss damage item

    def draw(self):
        screen.blit(self.image, self.rect)


class Game:
    def __init__(self):
        self.player = Player()
        self.enemies = pygame.sprite.Group()
        self.boss = Boss()
        self.bullets = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.score = 0
        self.font = pygame.font.Font(None, 36)
        self.difficulty_level = 1
        self.max_difficulty_level = 5
        self.difficulty_increase_score = 1
        self.enemy_spawn_delay = 1500
        self.last_enemy_spawn = pygame.time.get_ticks()

    def spawn_enemies(self):
        now = pygame.time.get_ticks()
        if now - self.last_enemy_spawn > self.enemy_spawn_delay / (self.difficulty_level + 1):
            self.last_enemy_spawn = now
            enemy_x = random.randint(0, SCREEN_WIDTH)
            enemy_speed = random.choice([-1, 1]) * (2 + self.difficulty_level)
            enemy = Enemy(enemy_x, 0, enemy_speed)
            self.enemies.add(enemy)

    def spawn_items(self):
        if len(self.items) < 2:
            item_type = random.randint(0, 1)
            item_x = random.randint(0, SCREEN_WIDTH)
            item = Item(item_x, 0, item_type)
            self.items.add(item)
            
    def check_collisions(self):
    # Item collision check
        for item in self.items:
            if self.player.rect.colliderect(item.rect):
                if item.type == 0:
                    self.player.bullet_damage += 1
                else:
                    self.player.boss_bullet_damage += 1
                self.items.remove(item)

        # Bullet and enemy collision check
        for bullet in self.bullets:
            for enemy in self.enemies:
                if bullet.rect.colliderect(enemy.rect):
                    self.bullets.remove(bullet)
                    self.enemies.remove(enemy)
                    self.score += 1
                    self.player.reset_bullets()
                    break

        # Bullet and boss collision check
        if self.boss.active:    
            self.boss.check_collision(self.bullets, self.player)

        # Boss bullet and player collision check
        for boss_bullet in self.boss.bullets:
            if boss_bullet.rect.colliderect(self.player.rect):
                now = pygame.time.get_ticks()
                if now - self.player.invincible_end_time > self.player.invincible_duration:
                    self.player.health -= 1
                    self.player.invincible_end_time = now

    def update(self):
        self.player.move()
        self.player.shoot(self.bullets)
        self.spawn_enemies()
        self.spawn_items()
        self.bullets.update(move=lambda sprite: sprite.move())
        self.enemies.update(move=lambda sprite: sprite.move())
        self.items.update()
        self.check_collisions()

        if not self.boss.active and self.difficulty_level == self.max_difficulty_level:
            self.boss.active = True

        if self.boss.active:
            self.boss.move(self.player)
            self.boss.attack()
            self.boss.bullets.update(move=lambda sprite: sprite.move())

        # Increase difficulty level
        if self.score >= self.difficulty_increase_score * self.difficulty_level:
            self.difficulty_level += 1
            if self.difficulty_level > self.max_difficulty_level:
                self.difficulty_level = self.max_difficulty_level

        # Player health check
        if self.player.health <= 0:
            self.running = False

    def draw(self):
        screen.blit(background_img, (0, 0))
        self.player.draw()
        self.bullets.draw(screen)
        self.enemies.draw(screen)
        self.items.draw(screen)
        if self.boss.active:
            self.boss.draw()

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        health_text = self.font.render(f"Health: {self.player.health}", True, WHITE)
        screen.blit(health_text, (10, 50))

        difficulty_text = self.font.render(f"Difficulty Level: {self.difficulty_level}", True, WHITE)
        screen.blit(difficulty_text, (10, 90))

        boss_health_text = self.font.render("Boss Health: " + str(self.boss.health), True, WHITE)
        screen.blit(boss_health_text, (10, 70))

        pygame.display.flip()

    def run(self):
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.update()
            self.draw()

        pygame.quit()
        sys.exit()
        
if __name__ == "__main__":
    game = Game()
    game.run()