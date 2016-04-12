#menu.py
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

"""this module helps to build up menus"""

import pygame
from location import Background

PATH = "gfx/menu/"

class Moon(object):
   """image of the moon"""
   def __init__(self, position):
       self.image = pygame.image.load(PATH + "moon.png")
       self.rect = pygame.Rect(position, self.image.get_size())
       

class Button(object):
    """A simple button for menus, use it with ButtonGroup

       Args: position -> Position of the button on the screen
    """
    def __init__(self, position):
        self.position = position
        self.rect = None
        self.image = None
        self.active_image = None
        self.passive_image = None

    def add_text(self, font, text, colour_passive, colour_active):
        """Add a text to this button

           Args: font          -> path to an font-file               (string)
                 text          -> text on the button                 (string)
                 colour_passive -> colour of the button in idle mode   (tuple)
                 colour_active  -> colour of the button, when selected (tuple)
        """
        self.active_image = font.render(text, 8, colour_active)
        self.passive_image = font.render(text, 8, colour_passive)
        self.rect = pygame.Rect(self.position, self.active_image.get_size())

    def update(self, state):
        """Render the current state of the button

           Args: state -> string, could be 'active' or 'passive'
        """
        self.image = self.passive_image if state == 'passive' else self.active_image

class SimpleText(object):
    """Textobject"""
    def __init__(self, font, text, color, position):
        self.image = font.render(text, 8, color)
        self.rect = pygame.Rect(position, self.image.get_size())


class InfoText(object):
    """Text over several lines"""
    def __init__(self, text, position):
        self.position = position
        self.text = []
        self.images = []
        self.image = None
        for line in text.split("\n"):
            self.text.append(line)

    def render_text(self, color, font):
        """render every single line"""
        for line in self.text:
            self.images.append(font.render(line, 8, color))

    def generate_image(self):
        """put all lines together to one image"""
        height = 0
        width = 0
        for image in self.images:
            width = image.get_size()[0] if image.get_size()[0] > width else width
            height += image.get_size()[1] * 1.1
        self.image = pygame.Surface((width, height), flags = pygame.SRCALPHA)
        y = 0
        for image in self.images:
            self.image.blit(image, (0, y))
            y += image.get_size()[1] * 1.1
        self.rect = pygame.Rect(self.position, (width,height))
        
         
        

