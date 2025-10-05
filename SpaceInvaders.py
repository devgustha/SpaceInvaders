import pygame as pg
import random

# Initialization
pg.init()
pg.font.init()
font = pg.font.Font(None, 36)

# Colors
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
MAGENTA = (255, 0, 255)

COLORS = [
    WHITE, RED, YELLOW, GREEN, CYAN, BLUE, MAGENTA
]

# Screen
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 600
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
SCREEN_CENTER_X, SCREEN_CENTER_Y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
pg.display.set_caption("Space Invaders")

def draw_text(surface: pg.surface.Surface = screen, cords: tuple[int, int] = (0, 0), text: str = "", color: tuple[int, int, int] = WHITE):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, cords)

# Settings
SHIP_SIZE = 100
ENEMY_SIZE = 70
ACCELERATION = 0.3
FRICTION = 0.98

BULLET_SPEED = 20
BULLET_WIDTH = 10
BULLET_HEIGHT = 15

# Images
bg_image = pg.image.load("Images/SpaceInvadersBackground.png").convert()
bg_image = pg.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
enemy_images = [
    pg.image.load("Images/SpaceInvader1.png"),
    pg.image.load("Images/SpaceInvader2.png"),
    pg.image.load("Images/SpaceInvader3.png"),
    pg.image.load("Images/SpaceInvader4.png")
]

ship_image = pg.image.load("Images/SpaceInvadersShip.png")
ship_image = pg.transform.scale(ship_image, (SHIP_SIZE, SHIP_SIZE))

# Classes
class Bullet:
    _counter = 0
    def __init__(self, is_player: bool = False, x: int = 0, y: int = 0):
        self.direction = -1 if is_player else 1
        self.x = x
        self.y = y
        self.id = Bullet._counter
        self.is_player_shot = is_player
        self.rect = None
        Bullet._counter += 1

    def move(self):
        self.y += (BULLET_SPEED * self.direction)

    def draw(self, surface: pg.surface.Surface = screen):
        self.rect = pg.draw.rect(surface, YELLOW, (self.x, self.y, BULLET_WIDTH, BULLET_HEIGHT))

    def __str__(self):
        return f"Bullet id: {self.id} Is shot by player {self.is_player_shot}"

class Enemy:
    _counter = 0
    def __init__(self, type: int = 0, x: int = 0, y: int = 0, color: tuple[int, int, int] = WHITE):
        try:
            self.image = enemy_images[type]
        except IndexError:
            self.image = enemy_images[0]

        self.image = pg.transform.scale(self.image, (ENEMY_SIZE, ENEMY_SIZE)).convert_alpha()
        tint = pg.Surface(self.image.get_size(), pg.SRCALPHA)
        tint.fill((*color, 255))

        self.image.blit(tint, (0, 0), special_flags=pg.BLEND_RGBA_MULT)

        self.image = self.image.copy()
        self.x, self.y = x, y
        self.vel_x, self.vel_y = 0, 0
        self.rect: pg.Rect = pg.Rect(self.x, self.y, ENEMY_SIZE, ENEMY_SIZE)
        self.id = Enemy._counter
        Enemy._counter += 1

    def attack(self):
        new_bullet = Bullet(x=self.x + ENEMY_SIZE / 2, y=self.y)
        return new_bullet

    def move(self):
        pass

    def check_collision(self, bullet: Bullet):
        if self.rect.colliderect(bullet.rect) and bullet.is_player_shot:
            return True

        return False

    def draw(self, surface: pg.surface.Surface = screen):
        surface.blit(self.image, (self.x, self.y))
        self.rect: pg.Rect = pg.Rect(self.x, self.y, ENEMY_SIZE, ENEMY_SIZE)

    def __str__(self):
        return f"Enemy: X: {self.x} Y: {self.y}"

class Ship:
    def __init__(self) -> None:
        self.vel_x = 0
        self.vel_y = 0
        self.x, self.y = SCREEN_CENTER_X, SCREEN_HEIGHT - 100
        self.rect: pg.Rect = pg.Rect(self.x, self.y, SHIP_SIZE, SHIP_SIZE)

    def draw(self, surface: pg.surface.Surface = screen) -> None:
        surface.blit(ship_image, (self.x - SHIP_SIZE / 2, self.y - SHIP_SIZE // 2))
        self.rect = pg.Rect(self.x - SHIP_SIZE // 5.5, self.y - SHIP_SIZE // 5.5, SHIP_SIZE // 3, SHIP_SIZE // 3)

    def move(self) -> None:
        self.x += self.vel_x
        self.y += self.vel_y

        self.vel_x *= FRICTION
        self.vel_y *= FRICTION

        if self.x > SCREEN_WIDTH:
            self.x = 0
        elif self.x < 0 - SHIP_SIZE:
            self.x = SCREEN_WIDTH

        if self.y > SCREEN_HEIGHT + SHIP_SIZE:
            self.y = 0
        elif self.y < 0 - SHIP_SIZE:
            self.y = SCREEN_HEIGHT

    def attack(self) -> Bullet:
        new_bullet = Bullet(is_player=True, x=self.x, y=self.y)
        return new_bullet

    def check_keybinds(self) -> None | Bullet:
        k = pg.key.get_pressed()
        if k[pg.K_w]:
            self.vel_y -= ACCELERATION
        if k[pg.K_s]:
            self.vel_y += ACCELERATION

        if k[pg.K_a]:
            self.vel_x -= ACCELERATION
        if k[pg.K_d]:
            self.vel_x += ACCELERATION

        self.move()

    def check_collision(self, obj: Bullet | Enemy):
        if not isinstance(obj, Bullet):
            if not isinstance(obj, Enemy):
                return False

        if isinstance(obj, Bullet):
            if obj.is_player_shot:
                return False
            
        if self.rect.colliderect(obj.rect):
            return True
        
        return False

    def __str__(self) -> str:
        return f"X: {self.x} Y: {self.y}"

running = True
score = 0
level = 1
def game_over_loop():
    global running, score, level
    while running:
        screen.fill(BLACK)

        for ev in pg.event.get():
            if ev.type == pg.QUIT:
                running = False
            if ev.type == pg.KEYDOWN:
                if ev.key == pg.K_r:
                    score = 0
                    level = 0
                    main_loop()

        draw_text(screen, (10, 10), f"Score: {score}", GREEN)
        draw_text(screen, (SCREEN_WIDTH - 105, 10), f"Level: {level}", GREEN)
        draw_text(screen, (SCREEN_CENTER_X - 50, SCREEN_CENTER_Y - 50), "Game over!")
        draw_text(screen, (SCREEN_CENTER_X - 85, SCREEN_CENTER_Y), "Press R to restart!", GRAY)

        pg.display.flip()

def main_loop():
    global running, score, level
    ship = Ship()
    bullets: list[Bullet] = []
    enemys: list[Enemy] = []

    rows = 10
    rows_proportion = SCREEN_HEIGHT // rows + ENEMY_SIZE // 5

    max_enemy_per_row = 10
    max_enemy_per_column = 4

    enemy = Enemy(type=0, x=SCREEN_CENTER_X - ENEMY_SIZE / 2, y=50)
    enemys.append(enemy)
        
    clock = pg.time.Clock()
    while running:
        ship_died = False
        screen.fill(BLACK)

        ship.check_keybinds()

        new_player_bullet = None

        for ev in pg.event.get():
            if ev.type == pg.QUIT:
                running = False
            if ev.type == pg.KEYDOWN:
                if ev.key == pg.K_SPACE:
                    new_player_bullet = ship.attack()

        if not new_player_bullet is None:
            bullets.append(new_player_bullet)

        if len(enemys) == 0:
            level += 1
            for i in range(1, min(random.randint(1, level), random.randint(1, max_enemy_per_column)) + 1):
                quant_enemy_row = min(random.randint(1, level), random.randint(1, max_enemy_per_row))
                sum_quant_enemy_row = quant_enemy_row * ENEMY_SIZE
                free_space = SCREEN_WIDTH - sum_quant_enemy_row

                if quant_enemy_row > 0:
                    margin = free_space / (2 * quant_enemy_row)
                    space_between = margin * 2
                else:
                    margin = space_between = 0

                for j in range(quant_enemy_row):
                    x_pos = margin + j * (ENEMY_SIZE + space_between)
                    y_pos = i * rows_proportion
                    new_enemy = Enemy(random.randint(0, min(level, len(enemy_images) - 1)), x_pos, y_pos, random.choice(COLORS))
                    enemys.append(new_enemy)

        for enemy in enemys:
            ship_died = ship.check_collision(enemy)
            if ship_died:
                game_over_loop()
            enemy.draw()

            if random.randint(0, 200) == 0:
                new_enemy_bullet = enemy.attack()
                bullets.append(new_enemy_bullet)

        for bullet in bullets:
            bullet.draw()
            bullet.move()
            ship_died = ship.check_collision(bullet)
            if ship_died:
                game_over_loop()
            for enemy in enemys:
                hit = enemy.check_collision(bullet)
                if hit:
                    enemys.remove(enemy)
                    try:
                        bullets.remove(bullet)
                    except ValueError:
                        pass
                    score += 1

            if bullet.y > SCREEN_HEIGHT or bullet.y < 0 - BULLET_HEIGHT:
                try:
                    bullets.remove(bullet)
                except ValueError:
                    pass
            
        clock.tick(60)
        ship.draw()

        draw_text(cords=(10, 10), text=f"Score: {score}")
        draw_text(screen, (SCREEN_WIDTH - 105, 10), f"Level: {level}")
        pg.display.flip()


if __name__ == '__main__':
    game_over_loop()
    pg.quit()