import pygame
import random
import os

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shooter Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Load images
PLAYER_IMG = pygame.image.load(os.path.join("assets", "player.png"))
ENEMY_IMG = pygame.image.load(os.path.join("assets", "enemy.png"))
BULLET_IMG = pygame.image.load(os.path.join("assets", "bullet.png"))

# Fonts
FONT = pygame.font.SysFont("comicsans", 40)

# Game settings
FPS = 60
PLAYER_VEL = 5
BULLET_VEL = 7
ENEMY_VEL = 3
MAX_ENEMIES = 5

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = PLAYER_IMG
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT - 50)
        self.speed = PLAYER_VEL

    def move(self, dx=0, dy=0):
        self.rect.x += dx
        self.rect.y += dy
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = ENEMY_IMG
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed = ENEMY_VEL

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.x = random.randint(0, WIDTH - self.rect.width)
            self.rect.y = random.randint(-100, -40)

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = BULLET_IMG
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speed = BULLET_VEL

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()

# Main menu
def main_menu():
    run = True
    while run:
        WIN.fill(BLUE)
        title_text = FONT.render("Shooter Game", True, WHITE)
        WIN.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - title_text.get_height() // 2))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    run = False

    game_loop()

# Game loop
def game_loop():
    run = True
    clock = pygame.time.Clock()
    player = Player()
    all_sprites.add(player)

    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.shoot()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.move(dx=-player.speed)
        if keys[pygame.K_RIGHT]:
            player.move(dx=player.speed)
        if keys[pygame.K_UP]:
            player.move(dy=-player.speed)
        if keys[pygame.K_DOWN]:
            player.move(dy=player.speed)

        all_sprites.update()

        WIN.fill(BLACK)
        all_sprites.draw(WIN)
        pygame.display.update()

    pygame.quit()

# Initialize sprite groups
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()

# Start the game
main_menu()