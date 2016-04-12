# data/lander/launarmodule.py
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

"""module-docstring"""

import pygame
import sys
import math
import os

PATH = "gfx/lunarmodule/"
PPM = 7 #pixels per meter

def kinetic_energy(mass, velocity):
    """Calculate the kinetic energy from the mass and the velocity of an
       object.
       Args: mass     -> mass of the object in kg (int/float)
             velocity -> velocity of the object in m/s (int/float)

       Returns: energy -> kinetic energy of the object in joule (int/float)"""
    ekin = mass * 0.5 * velocity ** 2 * (-1 if velocity < 0 else 1)
    return ekin

def v_from_e(energy, mass):
    """Calculate the velocity from the kinetic energy and the mass of an
       object.
       Args: energy     -> kinetic energy of the object in joule (int/float)
             mass       -> mass of the object in kg (int/float)

       Returns: velocity -> velocity of the object in m/s (int/float)"""
    if mass <= 0:
        raise ValueError("Mass should not be negative")

    velocity = math.sqrt((2 * math.fabs(energy)) / mass)
    velocity *= -1 if energy < 0 else 1
    return velocity

def blit_at_center(dest, source):
    """This function blits one surface centered to another surface.
       Args: dest     -> destination-surface, where the source-surface will be
                         blitted to
             source   -> source-surface, will be blitted to the dest-surface

       Returns: surface
    """
    src_pos = ((dest.get_size()[0] - source.get_size()[0]) / 2,
               (dest.get_size()[1] - source.get_size()[1]) / 2)
    dest.blit(source, src_pos)
    return dest

def get_vector(angle, force_abs):
    """This function builds a 2D vector of the angle and the absolute
       value of the vector"""
    angle = math.radians(angle)
    x = math.sin(angle)
    y = math.cos(angle)
    x = int(force_abs * x)
    y = int(force_abs * y)
    return [x, y]

class Shadow(pygame.sprite.Sprite):
    """Shadow of the lunarmodule

       Initialize it with the y-coordinate of the ground and update it with the
       x-coordinate of the lunarmodule
    """
    def __init__(self, ground):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(PATH + "shadow.png")
        self.rect = pygame.Rect((0, 0), self.image.get_size())
        self.rect.bottom = ground

    def update(self, x_pos):
        """follow the lunarmodule"""
        self.rect.center = x_pos, self.rect.center[1]

class Fire(pygame.sprite.Sprite):
    """Flame of the lunarmodule"""
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((32, 32), flags=pygame.SRCALPHA)
        self.rect = pygame.Rect((0, 0), self.image.get_size())
        self.rect.center = center
        self.index = 0
        self.sound = pygame.mixer.Sound("sound/schub.ogg")
        self.channel = pygame.mixer.Channel(5)

        self.images = []
        for i in range(5):
            self.images.append([])
            for j in range(100):
                i_file = PATH + "fire/%d_%02d.png" % (i + 1, j)
                if os.path.isfile(i_file):
                    img = pygame.image.load(i_file)
                    img.convert_alpha()
                    self.images[i].append(img)
                else:
                    break
                    

    def update(self, size, sound):
        """size  : strength of the flame
           sound : decide wether to play sound or not"""
        size -= 1
        self.image = self.images[size][self.index]
        self.index = self.index + 1 if self.index + 1 < len(self.images[size]) else 0
        if not self.channel.get_busy() and sound:
            self.channel.play(self.sound)

class LunarModule(pygame.sprite.Sprite):
    """LunarModule

       g        : falling acceleration on the planet/moon
    """
    def __init__(self, position, g, fuel):
        pygame.sprite.Sprite.__init__(self)
        self.lander_image = pygame.image.load(PATH + "lunarmodule.png")
        self.defect_image = pygame.image.load(PATH + "lunarmodule_d.png")
        self.image = pygame.Surface((128, 128), flags=pygame.SRCALPHA)
        self.g = g
        self.fuel = fuel
        self.rect = pygame.Rect((0, 0), self.lander_image.get_size())
        self.rect.center = position
        self.mask = pygame.mask.from_surface(self.lander_image)
        self.float_pos = [float(position[0]), float(position[1])]
        self.velocity = [0.0, 0.0]
        self.mass = 4000
        self.direction = 0 #degrees
        self.fire = False
        self.altitude = 0
        self.shadow = None
        self.flame = Fire((65, 100))
        self.box = None
        self.landed = False
        self.l_velocity = 0.0
        self.power = 0
        self.game_over = False

    def set_box(self, rect):
        """set rect of the outer box, limiting the movement of the lunarmodule
        """
        self.box = rect
        self.shadow = Shadow(self.box.bottom)

    def thrust(self, deltat, sound):
        """update the velocity based on the power of the thrust"""
        if self.power != 0:
            if self.power == 1:
                fuelforce = 2000
            elif self.power == 2:
                fuelforce = 5000
            elif self.power == 3:
                fuelforce = 8000
            elif self.power == 4:
                fuelforce = 12000
            elif self.power == 5:
                fuelforce = 16000

#F = m*a = m * (Dv/Dt)
#Dv = (F * Dt) / m

            if self.fuel > 0:
                self.fuel -= self.power
                f_thrust = get_vector(self.direction, fuelforce)
                deltav = ((f_thrust[0] * deltat) / self.mass,
                          (f_thrust[1] * deltat) / self.mass)

                self.velocity[0] -= deltav[0]
                self.velocity[1] -= deltav[1]
                self.fire = True
                self.flame.update(self.power, sound)
        else:
            self.flame.channel.stop()

    def rotate(self, direction):
        """rotate the lunarmodule"""
        if self.game_over:
            return None
        if direction == 'left':
            self.direction += 5
            self.direction -= 360 if self.direction >= 360 else 0
        elif direction == 'right':
            self.direction -= 5
            self.direction += 360 if self.direction < 0 else 0

    def set_game_over(self):
        """set to game over, change image and stop accepting userinput"""
        self.game_over = True
        self.velocity[0] = 0
        self.lander_image = self.defect_image

    def stay_in_box(self):
        """This function prevents the LunarModule from leaving the game-area,
	   which is defined in self.box
	"""
        if self.rect.left <= self.box.left and self.velocity[0] < 0:
            self.velocity[0] = 0.0
            self.float_pos[0] += self.box.left - self.rect.left
        elif self.rect.right >= self.box.right and self.velocity[0] > 0:
            self.velocity[0] = 0.0
            self.float_pos[0] += self.box.right - self.rect.right
        if self.rect.top <= self.box.top and self.velocity[1] < 0:
            self.velocity[1] = 0.0
            self.float_pos[1] += self.box.top - self.rect.top
            self.landed = False
        elif self.rect.bottom >= self.box.bottom:
            self.landed = True
            # end the game if the LunarModule does not stand upside on the
            # ground
            if 30 < self.direction < 330:
                self.set_game_over()
            if self.velocity[1] > 0:
                self.power = False
                self.l_velocity = self.velocity[1]
                if self.l_velocity > 6: #End the game, if the landing velocity
                                        #is greater than 6 meters per second
                    self.set_game_over()
                self.velocity = [0.0, 0.0]
                self.float_pos[1] += self.box.bottom - self.rect.bottom
        else:
            self.landed = False

    def update(self, deltat, boulders, sound):
        """update position etc."""
        if not self.game_over:
            self.thrust(deltat, sound)

        #update shadow
        self.shadow.update(self.rect.center[0])
        #check for collision
        if pygame.sprite.spritecollide(self, boulders, False,
                                       pygame.sprite.collide_mask):
            self.set_game_over()
        #In the next few lines, self.image is cleared and a buffer is created.
        #The lander and flame get blitted at the buffer and then the buffer get
        #rotated. So self.image is not resized while the rotation.
        #Problem of this: self.image is much larger than self.lander_image.
        #Therefore I use two rects: one rect for blitting and another for
        #collision.
        self.image.fill((0, 0, 0, 0))
        buffer_img = self.image.copy()
        buffer_img = blit_at_center(buffer_img, self.lander_image)
        if self.fire:
            buffer_img.blit(self.flame.image, self.flame.rect)
            self.fire = False
        buffer_img = pygame.transform.rotate(buffer_img, self.direction)
        buffer_rect = buffer_img.get_rect(center=(64, 64))
        self.image.blit(buffer_img, buffer_rect)
        self.stay_in_box()
        #fly/move
        if not self.landed:
            self.velocity[1] += self.g * deltat
        self.float_pos[0] += self.velocity[0] * deltat * PPM
        self.float_pos[1] += self.velocity[1] * deltat * PPM
        self.altitude = (self.box.bottom - self.rect.bottom) / PPM
        self.rect[0] = int(self.float_pos[0])
        self.rect[1] = int(self.float_pos[1])

