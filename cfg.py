import pygame


HIGHSCORE_FILE = 'highscore.txt'
SPRITESHEET_JUMPER = 'spritesheet_jumper.png'
UI_SPRITESHEEP = 'Iconic2048x2048.png'
UI_SPRITESHEEP_PRESSED = 'Iconic2048x2048dark.png'
UI_SPRITE2 = 'greySheet.png'

# dimensions
TITLE = "Givi The Adventurer"
WIDTH = 480
HEIGHT = 600
FPS = 60
DIMENSIONS = (WIDTH, HEIGHT)
FONT_NAME = 'arial'

# colors & fonts
WHITE = (255, 255, 255)
YELLOW = (255, 255, 102)
BLACK = (0, 0, 0)
RED = (213, 50, 80)
GREEN = (59, 168, 96)
BLUE = (50, 153, 213)
GRAY = (239, 239, 239)
LBLUE = (0, 155, 155)
LL = (51, 153, 255)
BGCOLOR = LL

score_color = (255, 209, 103)
title_color = (119, 0, 21)

# player
PLAYER_ACC = 0.5
PLAYER_FRICTION = -0.12
PLAYER_GRAV = 0.8
PLAYER_JUMP = 20

# game properties
BOOST_POWER = 60
COIN_POWERUP = 100
JUMP_BOOST = 7
POW_SPAWN_PCT = 12
MOB_FREQ = 5000
PLAYER_LAYER = 2
PLAT_LAYER = 1
POW_LAYER = 1
MOB_LAYER = 2
CLOUD_LAYER = 0

# starting platforms
PLATFORM_LIST = [(0, HEIGHT - 60),
                 (WIDTH / 2 - 50, HEIGHT * 3 / 4),
                 (125, HEIGHT - 350),
                 (125, HEIGHT - 250),
                 (125, HEIGHT - 150),
                 (350, 200),
                 (175, 100)]

# mouse events
LEFT = 1
SCROLL = 2
RIGHT = 3

# location
x_change = 0
y_change = 0
mouse_list = []

# global vars
TILESIZE = 32
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE
