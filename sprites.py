from cfg import *
import pygame as pg
from random import choice, randrange

vec = pg.math.Vector2


class Spritesheet:
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()

    def get_image(self, x, y, width, height):
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        image = pg.transform.scale(image, (width // 3, height // 3))
        return image

    def get_image_unscaled(self, x, y, width, height):
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        # image = pg.transform.scale(image, (width // 3, height // 3))
        return image


class Player(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.walking = False
        self.jumping = False
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.image = self.standing_frames[0]

        self.rect = self.image.get_rect()
        self.rect.center = (40, HEIGHT - 100)

        self.powerup_left = 0
        self.powerup_addition = 0
        self.pos = vec(40, HEIGHT - 100)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

    def load_images(self):
        self.standing_frames = [self.game.spritesheet.get_image(614, 1063, 120, 191),
                                self.game.spritesheet.get_image(690, 406, 120, 201)]
        for frame in self.standing_frames:
            frame.set_colorkey(BLACK)
        self.walk_frames_r = [self.game.spritesheet.get_image(678, 860, 120, 201),
                              self.game.spritesheet.get_image(692, 1458, 120, 207)]
        for frame in self.walk_frames_r:
            frame.set_colorkey(BLACK)
        self.walk_frames_l = []
        for frame in self.walk_frames_r:
            self.walk_frames_l.append(pg.transform.flip(frame, True, False))
        for frame in self.walk_frames_l:
            frame.set_colorkey(BLACK)
        self.jump_frame = self.game.spritesheet.get_image(382, 763, 150, 181)
        self.jump_frame.set_colorkey(BLACK)

    def jump_cut(self):
        if self.jumping and self.vel.y < 0:
            self.vel.y *= 0.5

    def update(self):
        self.animate()
        self.acc = vec(0, PLAYER_GRAV)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.acc.x = -PLAYER_ACC
        if keys[pg.K_RIGHT]:
            self.acc.x = PLAYER_ACC

        # apply friction, calc motion
        self.acc.x += self.vel.x * PLAYER_FRICTION
        self.vel += self.acc
        if abs(self.vel.x) < 0.1:
            self.vel.x = 0
        self.pos += self.vel + 0.5 * self.acc

        # CHECK BOUNDARIES
        if self.pos.x > WIDTH + self.rect.width / 2:
            self.pos.x = 0 - self.rect.width / 2
        if self.pos.x < 0 - self.rect.width / 2:
            self.pos.x = WIDTH + self.rect.width / 2

        self.rect.midbottom = self.pos

    def animate(self):
        now = pg.time.get_ticks()
        if self.vel.x != 0:
            self.walking = True
        else:
            self.walking = False

        if not self.jumping and not self.walking:
            if now - self.last_update > 350:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames)
                bottom = self.rect.bottom
                self.image = self.standing_frames[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        if self.walking:
            if now - self.last_update > 200:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.walk_frames_l)
                bottom = self.rect.bottom
                if self.vel.x > 0:
                    self.image = self.walk_frames_r[self.current_frame]
                else:
                    self.image = self.walk_frames_l[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        if self.jumping:
            self.image = self.jump_frame
        self.mask = pg.mask.from_surface(self.image)

    def jump(self):
        self.rect.y += 2
        # check if player is on a platform - only if falling
        hits = pg.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.y -= 2
        if hits and not self.jumping:
            self.jumping = True
            self.game.jump_sound.play()
            self.vel.y = -PLAYER_JUMP
            if self.powerup_left > 0:
                self.vel.y = -PLAYER_JUMP + self.powerup_addition
                self.powerup_left -= 1


class Cloud(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = CLOUD_LAYER
        self.groups = game.all_sprites, game.clouds
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = choice(self.game.cloud_images)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        sc = randrange(50, 101) / 100
        self.image = pg.transform.scale(self.image, (int(self.rect.width * sc), int(self.rect.height * sc)))
        self.rect.x = randrange(WIDTH - self.rect.width)
        self.rect.y = randrange(-500, -50)

    def update(self):
        if self.rect.top > HEIGHT * 2:
            self.kill()


class Platform(pg.sprite.Sprite):
    def __init__(self, game, x, y):

        self._layer = PLAT_LAYER
        self.groups = game.all_sprites, game.platforms
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        images = [self.game.spritesheet.get_image(0, 288, 380, 94),
                  self.game.spritesheet.get_image(213, 1662, 201, 100)]
        if self.game.score > 290:
            images = [self.game.spritesheet.get_image(0, 384, 380, 94),
                      self.game.spritesheet.get_image(382, 204, 200, 100)]
        if self.game.score > 490:
            images = [self.game.spritesheet.get_image(0, 576, 380, 94),
                      self.game.spritesheet.get_image(218, 1456, 201, 100)]
        if self.game.score > 990:
            images = [self.game.spritesheet.get_image(0, 0, 380, 94),
                      self.game.spritesheet.get_image(262, 1152, 200, 100)]

        self.image = choice(images)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        if randrange(100) < POW_SPAWN_PCT:
            Pow(self.game, self)


class Pow(pg.sprite.Sprite):
    def __init__(self, game, plat):
        self._layer = POW_LAYER
        self.groups = game.all_sprites, game.powerups
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.plat = plat
        self.type = choice(['boost', 'coin', 'mushroom_good', 'mushroom_bad'])
        if self.type == 'boost':
            self.image = self.game.spritesheet.get_image(820, 1805, 71, 70)
        if self.type == 'coin':
            self.images = [self.game.spritesheet.get_image(698, 1931, 84, 84),
                           self.game.spritesheet.get_image(829, 0, 66, 84),
                           self.game.spritesheet.get_image(897, 1574, 50, 84),
                           self.game.spritesheet.get_image(645, 651, 15, 84), ]
            self.image = self.game.spritesheet.get_image(698, 1931, 84, 84)
        if self.type == 'mushroom_bad':
            self.image = self.game.spritesheet.get_image(814, 1574, 81, 85)
        if self.type == 'mushroom_good':
            self.image = self.game.spritesheet.get_image(812, 453, 81, 99)

        self.last_update = 0
        self.current_frame = 0
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.plat.rect.centerx
        self.rect.bottom = self.plat.rect.top - 5

    def update(self):
        self.rect.bottom = self.plat.rect.top - 5
        if not self.game.platforms.has(self.plat):
            self.kill()
        self.animate()

    def animate(self):
        now = pg.time.get_ticks()
        if self.type == 'coin':
            if self.images:
                if now - self.last_update > 200:
                    self.last_update = now
                    self.current_frame = (self.current_frame + 1) % len(self.images)
                    center = self.rect.center
                    self.image = self.images[self.current_frame]
                    self.image.set_colorkey(BLACK)
                    self.rect = self.image.get_rect()
                    self.rect.center = center


class Mob(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        self.image_up = self.game.spritesheet.get_image(566, 510, 122, 139)
        self.image_up.set_colorkey(BLACK)
        self.image_down = self.game.spritesheet.get_image(568, 1534, 122, 135)
        self.image_down.set_colorkey(BLACK)

        self.image = self.image_up
        self.rect = self.image.get_rect()
        self.rect.centerx = choice([-100, WIDTH + 100])
        self.vx = randrange(1, 4)
        if self.rect.centerx > WIDTH:
            self.vx *= -1
        self.rect.y = randrange(HEIGHT / 2)
        self.vy = 0
        self.dy = 0.5

    def update(self):
        self.rect.x += self.vx
        self.vy += self.dy
        if self.vy > 3 or self.vy < -3:
            self.dy *= -1
        center = self.rect.center
        if self.dy < 0:
            self.image = self.image_up
        else:
            self.image = self.image_down

        self.mask = pg.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.rect.y += self.vy
        if self.rect.left > WIDTH + 100 or self.rect.right < -100:
            self.kill()


class UI(pg.sprite.Sprite):
    def __init__(self, game, name, x, y, w, h, pos=(0, 0)):
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites, game.ui
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = self.game.ui_spritesheet.get_image_unscaled(x, y, w, h)
        self.image.set_colorkey((76, 105, 113))
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.name = name
        self.dim = (x, y, w, h)
        self.pressed = False

    def update(self):
        if self.pressed:
            self.image = self.game.ui_spritesheet_pressed.get_image(self.dim[0], self.dim[1], self.dim[2], self.dim[3])
        if self.game.running:
            self.kill()


class UI_KENNEY(pg.sprite.Sprite):
    def __init__(self, game, name, x, y, w, h, pos=(0, 0)):
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites, game.ui
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = self.game.ui_spritesheet_kenney.get_image_unscaled(x, y, w, h)
        self.name = name
        if self.name == 'box':
            self.image = pg.transform.scale(self.image, (300, 150))
            # self.font = pg.font.Font('kenvector_future_thin.ttf', 28)
            # self.draw_text("Givi The Adventurer", BLACK, WIDTH // 2 - 50, HEIGHT // 3)

        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.dim = (x, y, w, h)
        self.pressed = False

    def update(self):
        if self.pressed:
            self.image = self.game.ui_spritesheet_pressed.get_image(self.dim[0], self.dim[1], self.dim[2], self.dim[3])
        if self.game.running:
            self.kill()

    def draw_text(self, text, color, x, y):
        text_surface = self.font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.game.screen.blit(text_surface, text_rect)


class Text(pg.sprite.Sprite):
    def __init__(self, game, text, color, x, y, w, h):
        self._layer = 5
        self.groups = game.all_sprites, game.texts
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.color = color
        self.x = x
        self.y = y
        self.text = text
        self.text_surface = self.game.font.render(self.text, True,self.color)
        self.image = pg.Surface((w,h))
        W = self.text_surface.get_width()
        H = self.text_surface.get_height()
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
        self.image.blit(self.text_surface, [w/2 - W/2, h/2 - H/2])

        # self.draw_text()

    def draw_text(self):
        self.text_surface = self.game.font.render(self.text, True, self.color)
        text_rect = self.text_surface.get_rect()
        text_rect.midtop = (self.x, self.y)
        self.game.screen.blit(self.text_surface, text_rect)

    def update(self):
        if self.game.running:
            self.kill()