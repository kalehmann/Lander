#! /usr/bin/python

# lander.py
#(c) 2015 by Karsten Lehmann

###############################################################################
#                                                                             #
#    This file is a part of Lander                                            #
#                                                                             #
#    Lander is free software: you can redistribute it and/or modify           #
#    it under the terms of the GNU General Public License as published by     #
#    the Free Software Foundation, either version 3 of the License, or        #
#    any later version.                                      		      #
#                                                                             #
#    This program is distributed in the hope that it will be useful,          #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#    GNU General Public License for more details.                             #
#                                                                             #
#    You should have received a copy of the GNU General Public License        #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.    #
###############################################################################


"""This module contains the main functions of the game lander. start the game
   by launching mmenu() with an instance of pygame.display.init() as first
   argument.
"""

import pygame
import sys
import random
import time
import json
import math
import location
import menu
from lunar_module import LunarModule
from ui import Score, ControllPanel

pygame.mixer.pre_init(22050, -16, 2, 512)
pygame.init()

SIGNS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 "

C_WHITE = (255, 255, 255)
C_GREY = (100, 100, 100)

def read_scores():
    """this function returns a the high scores stored in the score file

       The return-object is a list of 5 tuples with the name and score.
    """
    dummy_score = [("", 0) for i in range(5)]
    try:
        score_file = open(".scores", "r")
        scores = json.load(score_file)
        score_file.close()
    except IOError:
        return dummy_score
    if len(scores) != 5:
        return dummy_score
    for score in scores:
        if (type(score[0]) != unicode) or (type(score[1]) != int):
            return dummy_score
    return scores

def write_scores(scores):
    """this function writes the scores in the score file"""
    try:
        score_file = open(".scores", "w")
        json.dump(scores, score_file, indent=4)
        score_file.close()
    except IOError as e:
        print "Error while writing score : %s" % e

def ask_name(SCREEN):
    """this menu asks the user to enter his name and returns it"""
    show_fps = True if '--fps' in sys.argv else False
    show_rects = True if '--show_rects' in sys.argv else False
    fps = 60 if '--no_limit' in sys.argv else 240
    running = True
    font = pygame.font.Font("gfx/ui/Game_font.ttf", 50)
    nscore = font.render("New Highscore", 8, C_WHITE)
    yname = font.render("Your name :", 8, C_WHITE)
    fps_clock = pygame.time.Clock()
    background = menu.Background()
    name = ""

    while running:
        pygame.event.pump()
        events = pygame.event.get()
        keys_pressed = pygame.key.get_pressed()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if SOUND: MENU_SOUND.play()
                    return name
                elif event.key == pygame.K_ESCAPE:
                    if SOUND: MENU_SOUND.play()
                    return ""
                elif event.key == pygame.K_BACKSPACE:
                    if SOUND: MENU_SOUND.play()
                    name = name[:-1]
                elif ((event.unicode in SIGNS)
                      and event.unicode):
                    if SOUND: MENU_SOUND.play()
                    if len(name) < 15:
                        name += event.unicode
            elif event.type == pygame.QUIT:
                sys.exit()
        advanced_draw(SCREEN, background.image, background.rect, show_rects)
        advanced_draw(SCREEN, nscore, pygame.Rect((200, 50), nscore.get_size()),
                      show_rects)
        advanced_draw(SCREEN, yname, pygame.Rect((20, 150), yname.get_size()),
                      show_rects)
        name_image = font.render(name, 8, C_WHITE)
        advanced_draw(SCREEN, name_image, pygame.Rect((320, 150),
                      name_image.get_size()), show_rects)
        deltat = fps_clock.tick(fps) / 1000.0
        if show_fps:
            print 1 / deltat
        pygame.display.update()

def check_score(score, SCREEN):
    """this function checks, if the score is a new high score.

       If so, it gets the name of the user an stores the scores.
    """
    scores = read_scores()
    if score > scores[4][1]:
        name = ask_name(SCREEN)
        scores.append([name, score])
        scores = sorted(scores,key=lambda f: f[1], reverse=True)
        del scores[5]
        write_scores(scores)
    

class Timer(object):
    """this object helps to manage time in the game

       You initialize it with the duration in milliseconds, you want to
       count/wait. The you could call .has_expired() to check if the time is up,
       or get state, to get the progress as float (0.0 to 1.0)
    """
    def __init__(self, duration):
        self.started = time.time()
        self.duration = duration

    def has_expired(self):
        """returns true if time is up"""
        if time.time() > self.started + self.duration:
            return True

    def get_state(self):
        """get the progress of the counter. For example, if the counter has
           started just now, it will return 0.0
           If it is over now, it returns 1.0
        """
        return (time.time() - self.started) / float(self.duration)

class GameOverText(pygame.sprite.Sprite):
    def __init__(self):
        font = pygame.font.Font("gfx/ui/Game_font.ttf", 90)
        self.o_image = font.render("GAME OVER", 8, (150,50,50))        
        self.rect = self.o_image.get_rect(center=(400,300))
        self.size = self.rect.width, self.rect.height

    def update(self, scaling):
        new_size = (int(self.size[0] * scaling),
                    int(self.size[1] * scaling))
        self.image = pygame.transform.scale(self.o_image, new_size)
        self.rect = self.image.get_rect(center=(400,300))

def local_rect(rect, camera_rect):
    """This function tests, if a given position is in the view of the camera
       and draws the surface on the screen

       Args: rect        -> rect of a game object
             camera_rect -> rect of the camera-view

       Returns: new rect if the surface is on the screen, else None"""
    if rect.colliderect(camera_rect):
        new_pos = (rect.left - camera_rect.left,
                   rect.top - camera_rect.top)
        new_rect = pygame.Rect(new_pos, rect.size)
        return new_rect
    else:
        return None

def draw(screen, image, rect, show_rect):
    """draw an image on the screen. If show_rect is true, the rectangle of the
       image will also be drawn
    """
    screen.blit(image, rect)
    if show_rect:
        pygame.draw.rect(screen,
          #Random color
          (random.randint(0,255), random.randint(0,255), random.randint(0,255)),
          rect, 2)

def advanced_draw(screen, image, rect, show_rect, camera_rect=None):
    """same as draw, but draws object a its relative position to the camera on
       the screen
    """
    if camera_rect:
        rect = local_rect(rect, camera_rect)
        if rect:
            draw(screen, image, rect, show_rect)
    else:
        draw(screen, image, rect, show_rect)

def draw_group(group, screen, camera_rect, show_rect):
    """same as advanced draw, but with a whole bunch of images"""
    for sprite in group.sprites():
        sprite_rect = local_rect(sprite.rect, camera_rect)
        if sprite_rect:
            draw(screen, sprite.image, sprite_rect, show_rect)

def gen_landscape(g_y, boulder_class, width):
    """Place some boulders on the ground.

       g_y           : y-coordinate of the ground
       boulder_class : class of the boulders
       width         : tuple, range to place boulders in

       returns       : pygame.sprite.Group with all boulders
    """
    latitude = width[1] - width[0]
    latitude /= 64
    number = random.randint(latitude / 4, latitude / 2)
    boulders = pygame.sprite.Group()
    for _ in range(number):
        overlapping = True
        while overlapping:
            overlapping = False
            pos = random.randint(width[0], width[1])
            for sprite in boulders.sprites():
                if sprite.rect.x - 100 <= pos <= sprite.rect.x + 100:
                    overlapping = True
        boulder = boulder_class((pos, 0))
        boulder.rect.bottom = g_y
        boulders.add(boulder)
    return boulders

def setup_screen():
    """setup a new window and return a image, which references to it"""
    screen_size = 800, 600
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption("Lander")
    return screen

def update_lm(lunar_module, events, keys_pressed):
    """manage the user input to the lunarmodule"""
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and lunar_module.power < 5:
                lunar_module.power += 1
            if event.key == pygame.K_DOWN and lunar_module.power > 0:
                lunar_module.power -= 1
            if event.key == pygame.K_SPACE:
                lunar_module.power = 0 if lunar_module.power > 0 else 5
        elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
            lunar_module.power = 0

    if keys_pressed[pygame.K_LEFT]:
        lunar_module.rotate('left')
    elif keys_pressed[pygame.K_RIGHT]:
        lunar_module.rotate('right')

def manage_lps(lunar_module, landing_points):
    """check if the lunarmodule has landed at a new place"""
    if lunar_module.landed and not lunar_module.game_over:
        landing_zone = location.LandingZone(lunar_module.rect.center)
        if not pygame.sprite.spritecollideany(landing_zone, landing_points):
            print "Landed, velocity : %f m/s" % lunar_module.l_velocity
            landing_points.add(landing_zone)
            return 1
    return 0

def run(screen):
    """main game"""
    show_fps = True if '--fps' in sys.argv else False
    show_rects = True if '--show_rects' in sys.argv else False
    fps = 60 if '--no_limit' in sys.argv else 240
    fuel = 10000
    ground = location.Ground(450)
    background = location.Background()
    box = pygame.Rect((-100, 10), (1100, 600))
    lunar_module = LunarModule((400, 100), 1.62, fuel)
    lunar_module.set_box(box)
    controll_panel = ControllPanel((700, 20))
    ui_score = Score((10, 10))
    cm_rect = pygame.Rect((0, 0), screen.get_size())
    running = True
    boulders = gen_landscape(box.bottom, location.Boulder,
                             (box.left, box.right))
    fps_clock = pygame.time.Clock()
    deltat = 0
    score = 0
    stop_timer = None
    landing_points = pygame.sprite.Group()
    game_over_text = GameOverText()
    game_over_sound = pygame.mixer.Sound("sound/game_over.ogg")
        
    while running:
        pygame.event.pump()
        events = pygame.event.get()
        keys_pressed = pygame.key.get_pressed()
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.QUIT:
                sys.exit()
        if stop_timer and stop_timer.has_expired():
            running = False
        #update lunarmodule and camera_position
        update_lm(lunar_module, events, keys_pressed)
        lunar_module.update(deltat, boulders, SOUND)
        cm_rect.center = lunar_module.rect.center

        #location
        screen.blit(background.image, background.rect)
        ground.update(cm_rect)
        advanced_draw(screen, ground.image, ground.rect, show_rects, cm_rect)
        #landing points
        score += manage_lps(lunar_module, landing_points)
        draw_group(landing_points, screen, cm_rect, show_rects)
        #draw boulders
        draw_group(boulders, screen, cm_rect, show_rects)
        #draw lunar module
        advanced_draw(screen, lunar_module.shadow.image,
                      lunar_module.shadow.rect, show_rects, cm_rect)
        draw(screen, lunar_module.image,
             lunar_module.image.get_rect(center=(400, 300)), show_rects)
        if show_rects:
            box_rect = local_rect(lunar_module.box, cm_rect)
            pygame.draw.rect(screen, (255, 255, 255), box_rect, 2)
            lm_rect = local_rect(lunar_module.rect, cm_rect)
            pygame.draw.rect(screen, (255, 255, 255), lm_rect, 2)
        #controllpanel
        velocity = math.sqrt(lunar_module.velocity[0] ** 2 +
                             lunar_module.velocity[1] ** 2)
        direction = math.degrees(math.atan2(lunar_module.velocity[1],
                                 lunar_module.velocity[0]))
        direction = 270 - direction
        if lunar_module.velocity[1] == lunar_module.velocity[0] == 0:
            direction = 0
        controll_panel.update(lunar_module.altitude, velocity, direction,
                              lunar_module.fuel / float(fuel))
        draw(screen, controll_panel.image, controll_panel.rect, show_rects)
        ui_score.update(score)
        screen.blit(ui_score.image, ui_score.position)
        if lunar_module.game_over:
            if not stop_timer:
                stop_timer = Timer(5)
                pygame.mixer.Channel(0).fadeout(2)
                if SOUND: game_over_sound.play()
            game_over_text.update(1 + stop_timer.get_state())
            advanced_draw(screen, game_over_text.image, game_over_text.rect,
                     show_rects)
        deltat = fps_clock.tick(fps) / 1000.0
        if show_fps:
            print 1 / deltat
        pygame.display.update()
    check_score(score, SCREEN)

def minfo(SCREEN):
    """this menu shows a little info text about the game"""
    show_fps = True if '--fps' in sys.argv else False
    show_rects = True if '--show_rects' in sys.argv else False
    fps = 60 if '--no_limit' in sys.argv else 240
    running = True
    fps_clock = pygame.time.Clock()
    background = menu.Background()
    font = pygame.font.Font("gfx/ui/Game_font.ttf", 30)
    text =(
"""
Das Ziel des Spiels ist es, sooft wie moeglich auf dem
Mond zu landen, um Proben zu sammeln. Mit den Pfeiltasten
Links / Rechts laesst sich die Landefaehre rotieren.
Mit Hoch / Runter laesst sich die Schubkraft des
Triebwerks bestimmen - aber mehr Schub bedeutet auch
einen hoeheren Treibstoffverbrauch.
Mit der Leertaste laesst sich der Schub auf Maximum /
Nichts schalten und mit der Escape-Taste kann man
wieder in das Hauptmenue zurueckkehren.
""")
    text = menu.InfoText(text, (50, 50))
    text.render_text(C_WHITE, font)
    text.generate_image()

    while running:
        pygame.event.pump()
        events = pygame.event.get()
        keys_pressed = pygame.key.get_pressed()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if SOUND: MENU_SOUND.play()
                    running = False                        
            elif event.type == pygame.QUIT:
                sys.exit()    
        advanced_draw(SCREEN, background.image, background.rect, show_rects)
        advanced_draw(SCREEN, text.image, text.rect, show_rects)
        deltat = fps_clock.tick(fps) / 1000.0
        if show_fps:
            print 1 / deltat
        pygame.display.update()

def mhighscores(SCREEN):
    """this menu shows all high scores with names"""
    show_fps = True if '--fps' in sys.argv else False
    show_rects = True if '--show_rects' in sys.argv else False
    fps = 60 if '--no_limit' in sys.argv else 240
    running = True
    fps_clock = pygame.time.Clock()
    background = menu.Background()    
    font = pygame.font.Font("gfx/ui/Game_font.ttf", 60)
    scores = read_scores()
    score_images = []
    for i in range(5):
        pair = (
          menu.SimpleText(font, scores[i][0], C_WHITE, (50, 100 + i*70)),
          menu.SimpleText(font, ": %5d" % scores[i][1], C_GREY,
          (350, 100 + i*70))
        )
        score_images.append(pair)

    while running:
        pygame.event.pump()
        events = pygame.event.get()
        keys_pressed = pygame.key.get_pressed()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if SOUND: MENU_SOUND.play()
                    running = False
            elif event.type == pygame.QUIT:
                sys.exit()    
        advanced_draw(SCREEN, background.image, background.rect, show_rects)
        for pair in score_images:
            advanced_draw(SCREEN, pair[0].image, pair[0].rect, show_rects)
            advanced_draw(SCREEN, pair[1].image, pair[1].rect, show_rects)
  
        deltat = fps_clock.tick(fps) / 1000.0
        if show_fps:
            print 1 / deltat
        pygame.display.update()

def mmenu(SCREEN):
    """main menu"""
    show_fps = True if '--fps' in sys.argv else False
    show_rects = True if '--show_rects' in sys.argv else False
    fps = 60 if '--no_limit' in sys.argv else 240
    running = True
    fps_clock = pygame.time.Clock()

    background = menu.Background()
    moon = menu.Moon((240, 110))
    font = pygame.font.Font("gfx/ui/Game_font.ttf", 50)
    spielen = menu.Button((50, 75))
    info = menu.Button((50, 165))
    optionen = menu.Button((50, 255))
    sound_txt = menu.SimpleText(font, "Sound :", C_GREY, (50, 255))
    sound_val = menu.Button((250, 255))
    highscores = menu.Button((50, 345))
    beenden = menu.Button((50, 435))
    spielen.add_text(font, "Spielen", C_GREY, C_WHITE)
    info.add_text(font, "Info", C_GREY, C_WHITE)
    optionen.add_text(font, "Optionen", C_GREY, C_WHITE)
    sound_val.add_text(font, "Aus", C_GREY, C_WHITE)
    highscores.add_text(font, "Highscores", C_GREY, C_WHITE)
    beenden.add_text(font, "Beenden", C_GREY, C_WHITE)
    buttons = spielen, info, sound_val, highscores, beenden
    active_button = 0

    while running:
        pygame.event.pump()
        events = pygame.event.get()
        keys_pressed = pygame.key.get_pressed()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_UP:
                    if active_button > 0: active_button -= 1
                    else: active_button = len(buttons) - 1
                    if SOUND: MENU_SOUND.play()
                elif event.key == pygame.K_DOWN:
                    if active_button < len(buttons) - 1: active_button += 1
                    else: active_button = 0
                    if SOUND: MENU_SOUND.play()
                elif event.key == pygame.K_RETURN:
                    if SOUND: MENU_SOUND.play()
                    if active_button == 0:
                        run(SCREEN)
                    elif active_button == 1:
                        minfo(SCREEN)
                    elif active_button == 2:
                        global SOUND
                        sound_val.add_text(font, "Aus" if SOUND else "An",
                                           C_GREY, C_WHITE)
                        if SOUND:
                            SOUNDTRACK.stop()
                            SOUND = False
                        else:
                            SOUNDTRACK.play(-1)
                            SOUND = True
                    elif active_button == 3:
                        mhighscores(SCREEN)
                    elif active_button == 4:
                        running = False
            elif event.type == pygame.QUIT:
                sys.exit()

        advanced_draw(SCREEN, background.image, background.rect, show_rects)
        advanced_draw(SCREEN, moon.image, moon.rect, show_rects)
        advanced_draw(SCREEN, sound_txt.image, sound_txt.rect, show_rects)
        for button in buttons:
            if button == buttons[active_button]:
                button.update("active")
            else:
                button.update("passive")
            advanced_draw(SCREEN, button.image, button.rect, show_rects)

        deltat = fps_clock.tick(fps) / 1000.0
        if show_fps:
            print 1 / deltat
        pygame.display.update()

if __name__ == "__main__":
    #Change to the script's directory
    #abspath = os.path.abspath(__file__) <- Py2exe gives an error here,
    #__file__ is not defined :(
    #dname = os.path.dirname(abspath)
    #os.chdir(dname)

    SOUND = False
    SOUNDTRACK = pygame.mixer.Sound("sound/soundtrack.ogg")
    MENU_SOUND = pygame.mixer.Sound("sound/klick.ogg")

    SCREEN = setup_screen()
    mmenu(SCREEN)
