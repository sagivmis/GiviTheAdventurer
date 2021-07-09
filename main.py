import pygame as pg
import random
import time
from cfg import *
from figures.player import Player
from sprites import *
from os import path


class Game:
    def __init__(self):
        pg.init()
        pg.mixer.init()
        icon = pg.image.load('sprites/rabbit-icon.png')
        pg.display.set_icon(icon)
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.running = True
        self.clock = pg.time.Clock()
        self.start_screen = False

        # font
        self.font = pg.font.Font('kenvector_future_thin.ttf', 28)

        self.load_data()

    def load_data(self):
        self.dir = path.dirname(__file__)
        img_dir = path.join(self.dir, 'sprites')
        try:
            # try to read the file
            with open(path.join(self.dir, HIGHSCORE_FILE), 'r+') as f:
                self.highscore = int(f.read())
        except:
            # create the file
            with open(path.join(self.dir, HIGHSCORE_FILE), 'w'):
                self.highscore = 0
        # load spritesheet
        self.spritesheet = Spritesheet(path.join(img_dir, SPRITESHEET_JUMPER))
        self.ui_spritesheet = Spritesheet(path.join(img_dir, UI_SPRITESHEEP))
        self.ui_spritesheet_pressed = Spritesheet(path.join(img_dir, UI_SPRITESHEEP_PRESSED))
        self.ui_spritesheet_kenney = Spritesheet(path.join(img_dir, UI_SPRITE2))

        #clouds
        self.cloud_images = []
        for i in range(1,4):
            self.cloud_images.append(pg.image.load(path.join(img_dir,f'cloud{i}.png')).convert())
        # load sounds
        self.snd_dir = path.join(self.dir, 'snd')
        self.jump_sound = pg.mixer.Sound(path.join(self.snd_dir, "Jump33.wav"))
        self.boost_sound = pg.mixer.Sound(path.join(self.snd_dir, "Powerup15.wav"))

    def new(self):
        # restart game
        self.score = 0
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.platforms = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.clouds = pg.sprite.Group()
        self.ui = pg.sprite.Group()
        self.texts = pg.sprite.Group()

        self.player = Player(self)
        for plat in PLATFORM_LIST:
            Platform(self, *plat)

        for cloud in range(10):
            c = Cloud(self)
            c.rect.y +=500
        self.mob_timer = 0
        # make char first layer
        pg.mixer.music.load(path.join(self.snd_dir, 'HappyTune.wav'))
        self.run()


    def run(self):
        # game loop
        pg.mixer.music.play(loops=-1)
        self.playing = True
        self.draw_start_screen()
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

            if not self.playing:
                self.draw_text("Givi The Adventurer", 28, BLACK, WIDTH // 2 - 50, HEIGHT // 2)
        pg.mixer.music.fadeout(500)

    def update(self):
        # game loop update
        self.all_sprites.update()

        # spawn a mob?
        now = pg.time.get_ticks()
        if now - self.mob_timer > 5000 + random.choice([-500,0,500-1000,1000]):
            self.mob_timer = now
            Mob(self)
        mob_hits = pg.sprite.spritecollide(self.player, self.mobs, False, pg.sprite.collide_mask)
        if mob_hits:
            self.playing = False

        if self.player.vel.y > 0:
            hits = pg.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                lowest = hits[0]
                for hit in hits:
                    if hit.rect.bottom < lowest.rect.bottom:
                        lowest = hit
                if lowest.rect.right + 10 > self.player.pos.x > lowest.rect.left - 10:
                    if self.player.pos.y < lowest.rect.bottom:
                        self.player.vel.y = 0
                        self.player.pos.y = lowest.rect.top
                        self.player.rect.midbottom = self.player.pos
                        self.player.jumping = False

        if self.player.rect.top <= HEIGHT / 4:
            if random.randrange(100)<10:
                Cloud(self)
            self.player.pos.y += max(abs(self.player.vel.y), 2)
            for cloud in self.clouds:
                cloud.rect.y += max(abs(self.player.vel.y/ random.randrange(1,4)), 2)
            for mob in self.mobs:
                mob.rect.y += max(abs(self.player.vel.y), 2)
            for plat in self.platforms:
                plat.rect.y += max(abs(self.player.vel.y), 2)
                if plat.rect.top >= HEIGHT:
                    plat.kill()
                    self.score += 10
        #  powerups
        pow_hits = pg.sprite.spritecollide(self.player, self.powerups, True)
        for pow in pow_hits:
            if pow.type == 'boost':
                self.boost_sound.play()
                self.player.vel.y = -BOOST_POWER
                self.player.jumping = False
            if pow.type == 'coin':
                self.boost_sound.play()
                self.score+=100
                self.draw_text("+100 POINTS", 22, WHITE, WIDTH / 2, HEIGHT / 2)
                pg.display.flip()
            if pow.type == 'mushroom_good':
                self.boost_sound.play()
                self.player.powerup_left = 7
                self.player.powerup_addition = -JUMP_BOOST
            if pow.type == 'mushroom_bad':
                self.boost_sound.play()
                self.player.powerup_left = 7
                self.player.powerup_addition = JUMP_BOOST
        # die
        if self.player.rect.bottom > HEIGHT:
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.vel.y, 10)
                if sprite.rect.bottom < 0:
                    sprite.kill()
        if len(self.platforms) == 0:
            self.playing = False
        # spawn new plats
        while len(self.platforms) < 8:
            highest = 0
            for plat in self.platforms:
                if plat.rect.y < highest:
                    highest = plat.rect.y
            choices = [-55,-60]
            Platform(self, random.randrange(0,WIDTH), random.choice(choices))

    def events(self):
        # events
        mouse_p = pg.mouse.get_pos()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
                pg.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.player.jump()
            if event.type == pg.KEYUP:
                if event.key == pg.K_SPACE:
                    self.player.jump_cut()
        return True  # remains in loop if didnt quit

    def draw(self):
        self.screen.fill(BGCOLOR)
        self.all_sprites.draw(self.screen)
        self.draw_text(str(self.score), 22, WHITE, WIDTH / 2, 15)
        pg.display.flip()

    def show_start_screen(self):
        # game start screen
        pg.mixer.music.load(path.join(self.snd_dir, 'Yippee.wav'))

        pg.mixer.music.play(loops=-1)
        self.screen.fill(BGCOLOR)
        self.draw_text(TITLE, 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Arrows to move,", 20, WHITE, WIDTH / 2-20, HEIGHT / 2)
        self.draw_text("space to jump", 20, WHITE, WIDTH / 2+50, HEIGHT / 2+50)
        self.draw_text("Press a key to play", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        self.draw_text(f"HIGH SCORE: {self.highscore}", 2, WHITE, WIDTH / 2, 15)
        pg.display.flip()
        self.wait_for_key()
        pg.mixer.music.fadeout(500)



    def draw_start_screen(self):
        pg.mixer.music.load(path.join(self.snd_dir, 'Yippee.wav'))
        self.start_screen = True
        pg.mixer.music.play(loops=-1)
        self.screen.fill(BGCOLOR)
        UI(self,'play',144,219,131,130, (WIDTH//2, HEIGHT//2+200))
        UI(self,'settings',145,1551,130,129, (WIDTH//2-150, HEIGHT//2+200))
        UI(self,'info',1328,367,130,129, (WIDTH//2+150, HEIGHT//2+200))
        UI_KENNEY(self, 'box', 190,98,100,100,(WIDTH//2, HEIGHT//5))
        Text(self, "Givi", (55,55,55), WIDTH // 2 - 220, HEIGHT // 4-120, 300, 100)
        Text(self, "The", (55,55,55), WIDTH // 2 - 130, HEIGHT // 4-100, 300, 100)
        Text(self, "Adventurer", (55,55,55), WIDTH // 2 - 130, HEIGHT // 4-60, 300, 100)

        for cloud in range(10):
            c = Cloud(self)
            c.rect.y +=500
        self.clouds.draw(self.screen)
        self.ui.draw(self.screen)
        self.texts.draw(self.screen)


        pg.display.flip()
        self.wait_for_key()
        pg.mixer.music.fadeout(500)

    def show_go_screen(self):
        # game over

        pg.mixer.music.load(path.join(self.snd_dir, 'Gameover.ogg'))

        pg.mixer.music.play()
        if not self.running:
            return
        self.screen.fill(BGCOLOR)
        self.draw_text("GAME OVER", 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text(f"Score {self.score}", 22, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Press a key to play again", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text(f"NEW HIGH SCORE {self.highscore}", 2, WHITE, WIDTH / 2, HEIGHT / 2 + 40)
            with open(path.join(self.dir, HIGHSCORE_FILE), 'r+') as f:
                f.write(str(self.score))
        else:
            self.draw_text(f"HIGH SCORE {self.highscore}", 2, WHITE, WIDTH / 2, HEIGHT / 2 + 40)

        pg.display.flip()
        self.wait_for_key()
        pg.mixer.music.fadeout(200)

    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if not self.start_screen:
                    if event.type == pg.KEYUP:
                        waiting = False
                mouse_p = pg.mouse.get_pos()
                if event.type == pg.MOUSEBUTTONDOWN and event.button == LEFT:
                    for sprite in self.ui:
                        if sprite.rect.collidepoint(mouse_p):
                            if sprite.name == 'play':
                                print('play')
                                waiting = False
                                self.start_screen=False
                            if sprite.name == 'settings':
                                print('settings')
                            if sprite.name == 'info':
                                print('info')


    def draw_text(self, text, size, color, x, y):
        text_surface = self.font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)


g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()

pg.quit()
quit()
