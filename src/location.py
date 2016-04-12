# data/locations/moon.py
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

"""This module contains classes for objects on the moon"""

import pygame
import os
import random

path = "gfx/moon/"

class LandingZone(pygame.sprite.Sprite):
    """point, where the lunarmodule has landed"""
    def __init__(self, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(path + "landing_zone.png").convert_alpha()
        self.rect = pygame.Rect((0,0), self.image.get_size())
        self.rect.center = position

class Ground(pygame.sprite.Sprite):
    """ground of the moon"""
    def __init__(self, height):
        image = pygame.image.load(path + "ground.png").convert_alpha()
        self.image = pygame.Surface((image.get_size()[0]*2,
                                     image.get_size()[1]),
                                    flags=pygame.SRCALPHA)
        self.image.blit(image, (0,0))
        self.image.blit(image, (image.get_size()[0],0))
        self.rect = pygame.Rect((0, height - 100),
                                self.image.get_size())

    def update(self, camera_rect):
        """function-docstring"""
        self.rect.x = (self.image.get_size()[0] *
                      int(camera_rect.x / camera_rect.width) * 0.5)

class Background(pygame.sprite.Sprite):
    """The sky"""
    def __init__(self):
        self.image = pygame.image.load(path + "background.png")
        self.rect = pygame.Rect((0, 0), self.image.get_size())

def get_image(path):
    """load random image from folder"""
    random.seed()
    images = []
    for f in os.listdir(path):
        if f.endswith('.png'):
            images.append(path + f)
    image = random.choice(images)
    return image

class Boulder(pygame.sprite.Sprite):
    """stone/rock on the moon"""
    def __init__(self, position):
        pygame.sprite.Sprite.__init__(self)
        self.path = path + "boulders/"
        self.image = pygame.image.load(get_image(self.path))
        self.rect = pygame.Rect(position, self.image.get_size())
        self.mask = pygame.mask.from_surface(self.image)
