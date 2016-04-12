# data/ui/controll_panel.py
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

"""this module contains classes for the userinterface"""

import pygame

PATH = "gfx/ui/"

def render_bar(surface, factor):
    """returns only a part of the image.
       factor defines how much to return
    """
    rect = surface.get_rect()
    rect.width = int(rect.width * factor)
    surface = surface.subsurface(rect)
    return surface

class Score(pygame.sprite.Sprite):
    """Text with the number of landings"""
    def __init__(self, position):
        pygame.sprite.Sprite.__init__(self)
        self.position = position
        self.font = pygame.font.Font(PATH + "Game_font.ttf", 30)
        self.image = None

    def update(self, score):
        """function_docstring"""
        self.image = self.font.render(str(score), 8, (255, 255, 255))

class Arrow(pygame.sprite.Sprite):
    """arrow, shows the current direction of the lunarmodule"""
    def __init__(self, location):
        self.base_image = pygame.image.load(PATH + "arrow.png")
        self.base_image.convert_alpha()
        self.base_rect = self.base_image.get_rect(x=location[0], y=location[1])
        self.image = None
        self.rect = None

    def update(self, direction):
        self.image = pygame.transform.rotate(self.base_image, direction)
        self.rect = self.image.get_rect(center=self.base_rect.center)

class ControllPanel(pygame.sprite.Sprite):
    """Shows the velocity, direction and amount of fuel"""
    def __init__(self, location):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((100, 100), pygame.SRCALPHA)
        self.rect = pygame.Rect(location, self.image.get_size())
        self.font = pygame.font.Font(PATH + "Game_font.ttf", 20)
        self.fuel_image = pygame.image.load(PATH + "fuel_tank.png")
        self.fuel_back = pygame.image.load(PATH + "fuel_tank_back.png")
        self.arrow = Arrow((0,30))

    def update(self, altitude, velocity, direction, fuel_stand):
        """function-docstring"""
        self.image.fill((0, 0, 0, 0))
        altitude = self.font.render(str(altitude)+ " m", 8, (255, 255, 255))
        velocity = self.font.render("%3.0f" % velocity + " m/s", 8,
                                    (255, 255, 255))
        self.arrow.update(direction)
        self.image.blit(altitude, (0, 0))
        self.image.blit(velocity, (15, 30))
        self.image.blit(self.arrow.image, self.arrow.rect)
        self.image.blit(self.fuel_back, (0, 60))
        self.image.blit(render_bar(self.fuel_image, fuel_stand), (0, 60))
