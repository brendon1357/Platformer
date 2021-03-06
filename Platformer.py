import pygame
import random
import time
import math
"""
##############################################################
PLATFORMER GAME
##############################################################
Version number: 2021-10-30
##############################################################
Fully completed version of the game.
- Features pixel perfect collision
- Gravity
- Jump mechanic
- Shooting mechanic
- Player animations
- Scrolling platforms and floor
##############################################################
"""
pygame.font.init()

WIN_WIDTH = 900
WIN_HEIGHT = 750
WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
FONT = pygame.font.Font("Marlboro.ttf", 50)
PAUSE_FONT = pygame.font.Font("Marlboro.ttf", 75)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
pygame.display.set_caption("Platformer")

REFERENCEPLAYERIMG = pygame.image.load("Images/player1.png")
BACKGROUND = pygame.image.load("Images/LavaBackground.jpeg")
FLOOR_IMG = pygame.image.load("Images/Lava_3_1_1432x50.png")
PLATFORM_IMG = pygame.image.load("Images/Platform.png")
ENEMY_IMG = pygame.image.load("Images/fireball.png")
PROJECTILE_IMG = pygame.image.load("Images/sphere-14.png")
CURSOR_IMG = pygame.Surface((20, 20), pygame.SRCALPHA)
CURSOR_RECT = CURSOR_IMG.get_rect()


class Enemy:
    def __init__(self, win, x, y):
        self.win = win
        self.img = ENEMY_IMG
        self.width = self.img.get_width()
        self.x = x
        self.y = y
        self.passed = False

    def draw(self, win):
        win.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Platform:
    def __init__(self, win, x):
        self.reset(win, x)

    def draw(self, win):
        win.blit(self.img, (self.rect.x, self.rect.y))

    def reset(self, win, x):
        self.win = win
        self.transformed_img = pygame.transform.smoothscale(PLATFORM_IMG, (random.randrange(350, 550), 25))
        self.img = self.transformed_img
        self.width = self.img.get_width()
        self.rect = self.img.get_rect()
        self.rect.x = x
        self.rect.y = random.randrange(450, 550)
        self.passed = False

    def move(self, vel):
        self.rect.x -= vel

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Projectile:
    SPEED = 25

    def __init__(self, win, x, y, mouse_pos):
        self.win = win
        self.img = PROJECTILE_IMG
        self.x = x
        self.y = y
        self.mouse_pos = mouse_pos
        self.pos = pygame.math.Vector2(self.x, self.y)
        self.dir = pygame.math.Vector2(self.mouse_pos[0], self.mouse_pos[1]) - self.pos
        self.dir = self.dir.normalize()

    def draw(self, win):
        win.blit(self.img, (self.x, self.y))

    def move(self):
        self.pos += self.dir * self.SPEED
        self.x, self.y = (round(self.pos.x), round(self.pos.y))

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Player:
    score = 0

    def __init__(self, win, x, y):
        self.reset(win, x, y)

    def draw(self, win):
        win.blit(self.img, (self.rect.x, self.rect.y))

    def update(self, end_by_fall, platforms):
        dx = 0
        dy = 0
        walk_cooldown = 8

        if end_by_fall == 0:
            key_input = pygame.key.get_pressed()
            if key_input[pygame.K_d]:
                self.direction = 1
                if not self.jumped and not self.falling:
                    self.counter += 1
                if self.rect.x >= 850:
                    self.rect.x = 850
                else:
                    dx += (self.score//10 + 14)

            if key_input[pygame.K_a]:
                self.direction = -1
                if not self.jumped and not self.falling:
                    self.counter += 1
                if self.rect.x <= 0:
                    self.rect.x = 0
                else:
                    dx -= (self.score//10 + 9)

            if key_input[pygame.K_SPACE] and not self.jumped and not self.falling:
                if self.vel_y <= 1:
                    self.vel_y = -21
                    self.jumped = True
                    self.falling = True

            if not key_input[pygame.K_d] and not key_input[pygame.K_a]:
                self.index = 0
                dx = 0

            elif key_input[pygame.K_d] and key_input[pygame.K_a]:
                self.index = 0
                self.counter = 0
                self.direction = 1
                dx = 0

            # updating images for animation
            if self.counter >= walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0

            if self.direction == 1:
                self.img = self.images_right[self.index]
            if self.direction == -1:
                self.img = self.images_left[self.index]

            # gravity
            self.vel_y += 1
            # terminal velocity
            if self.vel_y >= 15:
                self.vel_y = 15
            dy += self.vel_y

            add_platform = False
            for platform in platforms:
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height) and \
                        platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    dx = -9
                    self.vel_y = 10

                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0

                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if self.vel_y < 0:
                        dy = platform.rect.bottom - self.rect.top
                        self.vel_y = 0
                    elif self.vel_y >= 0:
                        dy = platform.rect.top - self.rect.bottom
                        self.vel_y = 0
                        self.falling = False
                        self.jumped = False

                if platform.rect.x + platform.width <= 0:
                    del platforms[:1]
                    self.score += 1

                if not platform.passed and platform.rect.x <= 0:
                    platform.passed = True
                    add_platform = True

                platform.move(self.score//10 + 5)

            if add_platform:
                platforms.append(Platform(WIN, 900))

            self.rect.x += dx
            self.rect.y += dy

            if self.rect.bottom > WIN_HEIGHT - 50:
                self.falling = False
                self.rect.bottom = WIN_HEIGHT - 50
                dy = 0
                end_by_fall = -1

        return end_by_fall

    def move(self, vel):
        if self.rect.x <= 0:
            self.rect.x = 0
        else:
            self.rect.x -= vel

    def reset(self, win, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for i in range(1, 5):
            img_right = pygame.image.load(f"Images/player{i}.png")
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)

        self.img = self.images_right[self.index]
        self.win = win
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.rect = self.img.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_y = 0
        self.jumped = False
        self.falling = True
        self.direction = 0

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Floor:
    def __init__(self, win):
        self.win = win
        self.img = FLOOR_IMG
        self.width = self.img.get_width()
        self.x1 = 0
        self.x2 = self.width
        self.y = 675

    def draw(self, win):
        win.blit(self.img, (self.x1, self.y))
        win.blit(self.img, (self.x2, self.y))

    def move(self, vel):
        self.x1 -= vel
        self.x2 -= vel
        if self.x1 + self.width < 0:
            self.x1 = self.x2 + self.width

        if self.x2 + self.width < 0:
            self.x2 = self.x1 + self.width


# checking for collision between two objects
def is_collision(object_one, object_two):
    object_one_mask = object_one.get_mask()
    object_two_mask = object_two.get_mask()
    offset = None

    if hasattr(object_one, "rect"):
        offset = (round(object_two.x - object_one.rect.x), round(object_two.y -object_one.rect.y))
    elif hasattr(object_two, "rect"):
        offset = (round(object_two.rect.x - object_one.x), round(object_two.rect.y - object_one.y))
    else:
        offset = (round(object_two.x - object_one.x), round(object_two.y - object_one.y))

    point = object_one_mask.overlap(object_two_mask, offset)

    if point:
        return True
    return False


def draw_window(win, floor, player, platforms, enemies, score, projectiles):
    floor.draw(WIN)
    player.draw(WIN)

    for enemy in enemies:
        enemy.draw(win)
    for platform in platforms:
        platform.draw(WIN)
    for projectile in projectiles:
        projectile.draw(WIN)

    score_label = FONT.render("Score: " + str(player.score), 1, (255,255,255))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    pygame.draw.circle(CURSOR_IMG, RED, (10, 10), 10, 2)
    pygame.draw.circle(CURSOR_IMG, RED, (10, 10), 2)
    win.blit(CURSOR_IMG, CURSOR_RECT)

    pygame.display.update()


def game_over_display(win, score):
    container = pygame.draw.rect(win, BLACK, ((WIN_WIDTH // 2) - 300, (WIN_HEIGHT // 2) - 225, 600, 250), 0, 20)
    game_over_label = FONT.render("GAME OVER", 1, RED)
    restart_label = FONT.render("PRESS ANY KEY TO RESTART", 1, RED)
    score_label = FONT.render("SCORE: " + str(score), 1, RED)

    win.blit(game_over_label, ((WIN_WIDTH//2) - (game_over_label.get_width()//2), (WIN_HEIGHT//2) - (game_over_label.get_height()//2) - 175))
    win.blit(restart_label, ((WIN_WIDTH//2) - (restart_label.get_width()//2), (WIN_HEIGHT//2) - (restart_label.get_height()//2) - 100))
    win.blit(score_label, ((WIN_WIDTH//2) - (score_label.get_width()//2), (WIN_HEIGHT//2) - (score_label.get_height()//2) - 25))

def pause(player, platforms, floor, enemies, win):
    for platform in platforms:
        platform.move(0)
    for enemy in enemies:
        enemy.move(0)
    player.move(0)
    floor.move(0)

    pause_label = PAUSE_FONT.render("GAME PAUSED", 1, BLACK)
    instruct_label = PAUSE_FONT.render("ESC - UNPAUSE", 1, BLACK)
    win.blit(pause_label, ((WIN_WIDTH//2) - (pause_label.get_width()//2), (WIN_HEIGHT//2) - (pause_label.get_height()//2) - 100))
    win.blit(instruct_label, ((WIN_WIDTH//2) - (instruct_label.get_width()//2), (WIN_HEIGHT//2) - (instruct_label.get_height()//2) - 25))


def handle_projectiles(projectiles, platforms, enemies, score):
    for projectile in projectiles:
        for platform in platforms:
            if is_collision(platform, projectile):
                projectiles.clear()
        for enemy in enemies:
            if is_collision(enemy, projectile):
                projectiles.clear()
                enemies.remove(enemy)
                score += 1
        # 740 = screen height - height of projectile
        if projectile.y >= 740 or projectile.y <= 0:
            projectiles.clear()
        # 890 = screen width - width of projectile
        if projectile.x >= 890 or projectile.x <= 0:
            projectiles.clear()
        projectile.move()
    return score


def handle_enemies(enemies, player, end_by_enemy, area, gap):
    add_enemy = False
    for enemy in enemies:
        if is_collision(enemy, player):
            end_by_enemy = -1
        # At or past bottom of screen
        if not enemy.passed and enemy.y >= 750:
            enemy.passed = True
            add_enemy = True
            enemies.clear()
        # increase move speed of enemies by 1 every 10 score
        if player.score < 60:
            # initial move speed is 6 and is incremented by 1 every 10 score
            enemy.move((player.score//10) + 6)
        else:
            enemy.move(12) # 60//10 + 6 setting maximum enemy move speed
    # either all of the enemies have been destroyed or they have reached bottom of screen
    if len(enemies) == 0 or add_enemy:
        create_enemies(enemies, 4)
    return end_by_enemy


def reset(platforms, player, projectiles, score):
    platforms[0].reset(WIN, 0)
    platform_y = platforms[0].rect.y
    player.reset(WIN, platforms[0].rect.width//2 - REFERENCEPLAYERIMG.get_width()//2, platforms[0].rect.y - REFERENCEPLAYERIMG.get_height())
    player.score = 0
    projectiles.clear()


def create_enemies(enemies, num_of_enemies):
    area = 0
    gap = 120
    for i in range(num_of_enemies):
        enemies.append(Enemy(WIN, random.randrange(area, gap), -400))
        area += 240
        gap += 240


def main():
    start_time = 0
    end_by_enemy = 0
    end_by_fall = 0
    end_score = 0
    platforms = [Platform(WIN, 0)]
    enemies = []
    create_enemies(enemies, 4)
    floor = Floor(WIN)
    projectiles = []
    CURSOR_RECT.center = (-10, -10) # drawing crosshair out of frame
    pygame.mouse.set_visible(False)

    player = Player(WIN, platforms[0].rect.width//2 - REFERENCEPLAYERIMG.get_width()//2, platforms[0].rect.y - REFERENCEPLAYERIMG.get_height())

    clock = pygame.time.Clock()
    run = True
    start = False
    lost = False
    paused = False
    wait = False
    while run:
        WIN.blit(BACKGROUND, (0, 0))
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if not wait:
                    if event.key != pygame.K_ESCAPE and not paused:
                        start = True
                    elif event.key == pygame.K_ESCAPE and not paused and not lost:
                        paused = True
                        start = False
                    elif event.key == pygame.K_ESCAPE and paused:
                        paused = False
                        start = True
            if event.type == pygame.MOUSEMOTION:
                CURSOR_RECT.center = event.pos
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not paused and start:
                pos = CURSOR_RECT.x, CURSOR_RECT.y
                if len(projectiles) == 0:
                    # 20 and 65 used to place projectile near player's hand
                    projectiles.append(Projectile(WIN, player.rect.x + 20, player.rect.y + 65, pos))
        if lost:
            wait = True 
            CURSOR_RECT.center = (-10, -10)
            game_over_display(WIN, end_score)
            if pygame.time.get_ticks() - start_time >= 500:
                wait = False
        if paused and not start:
            pause(player, platforms, floor, enemies, WIN) # stops all movement
        if start:
            start_time = pygame.time.get_ticks()
            lost = False
            end_by_fall = player.update(end_by_fall, platforms)
            area = 0
            gap = 120
            end_by_enemy = handle_enemies(enemies, player, end_by_enemy, area, gap)
            player.score = handle_projectiles(projectiles, platforms, enemies, player.score)

            player.move(player.score//10 + 5)
            floor.move(player.score//10 + 5)

            if end_by_fall == -1 or end_by_enemy == -1:
                end_score = player.score
                end_by_fall = 0
                end_by_enemy = 0
                lost = True
                start = False
                del platforms[1:]
                enemies.clear()
                create_enemies(enemies, 4)
                reset(platforms, player, projectiles, player.score)

        draw_window(WIN, floor, player, platforms, enemies, player.score, projectiles)


if __name__ == "__main__":
    main()
