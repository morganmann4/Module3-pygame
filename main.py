import pygame
import os
import time
import random
pygame.font.init()

WIDTH, HEIGHT = 750, 650
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Seas speed run")

# Load images
IMAGE_WIDTH, IMAGE_HEIGHT = 100, 100
BUOY = pygame.image.load(os.path.join("assets", "buoy2.webp"))
BUOY_2 = pygame.image.load(os.path.join("assets", "buoy2.webp"))
BUOY_3 = pygame.image.load(os.path.join("assets", "buoy2.webp"))

# BUOY = pygame.image.load(os.path.join("assets", "buoy.png"))
BUOY = pygame.transform.scale(BUOY, (IMAGE_WIDTH, IMAGE_HEIGHT))
BUOY.set_colorkey((255, 255, 255))
WIN.blit(BUOY, (200, 100))

BUOY_2 = pygame.transform.scale(BUOY_2, (IMAGE_WIDTH, IMAGE_HEIGHT))
BUOY_2.set_colorkey((255, 255, 255))
WIN.blit(BUOY_2, (200, 100))

BUOY_3 = pygame.transform.scale(BUOY_3, (IMAGE_WIDTH, IMAGE_HEIGHT))
BUOY_3.set_colorkey((255, 255, 255))
WIN.blit(BUOY_3, (200, 100))


# Player player
PLAYER_IMAGE_HEIGHT, PLAYER_IMAGE_WIDTH = 160, 160
PLAYER_BOAT = pygame.image.load(os.path.join("assets", "boat.webp")).convert_alpha()
PLAYER_BOAT = pygame.transform.scale(PLAYER_BOAT, (PLAYER_IMAGE_WIDTH, PLAYER_IMAGE_HEIGHT))
PLAYER_BOAT.set_colorkey((255, 255, 255))
WIN.blit(PLAYER_BOAT, (200, 100))

# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-blue.jfif")), (WIDTH, HEIGHT))

class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = PLAYER_BOAT
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))


class Enemy(Ship):
    COLOR_MAP = {
                "red": (BUOY, RED_LASER),
                "green": (BUOY_2, GREEN_LASER),
                "blue": (BUOY_3, BLUE_LASER)
                }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)

    enemies = []
    wave_length = 5
    enemy_vel = 1

    player_vel = 5

    player = Player(300, 500)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    # Draw the window 
    def redraw_window():
        WIN.blit(BG, (0,0))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))


        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("You Lost!!", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        # Wave lengths and level increase
        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        # Get the keys pressed by the player
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0: # left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: # right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0: # up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT: # down
            player.y += player_vel
       
        # Remove enemies 
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y > HEIGHT:
                enemies.remove(enemy)



def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label = title_font.render("Click to begin", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 250))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()