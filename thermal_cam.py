import adafruit_amg88xx
import pygame
import os
import math
import time
import busio
import board
import numpy as np
from scipy.interpolate import griddata

from colour import Color

i2c_bus = busio.I2C(board.SCL, board.SDA)

#low range of the sensor (this will be blue on the screen)
MINTEMP = 26

#high range of the sensor (this will be red on the screen)
MAXTEMP = 32

#how many color values we can have
COLORDEPTH = 1024

os.putenv('SDL_FBDEV', '/dev/fb1')
pygame.init()

#initialize the sensor
sensor = adafruit_amg88xx.AMG88XX(i2c_bus)

points = [(math.floor(ix / 8), (ix % 8)) for ix in range(0, 64)]
grid_x, grid_y = np.mgrid[0:7:32j, 0:7:32j]
grid_x_no_interpolation, grid_y_no_interpolation = np.mgrid[0:7, 0:7]

#sensor is an 8x8 grid so lets do a square
height = 240
width = 240

#the list of colors we can choose from
blue = Color("indigo")
colors = list(blue.range_to(Color("red"), COLORDEPTH))

#create the array of colors
colors = [(int(c.red * 255), int(c.green * 255), int(c.blue * 255)) for c in colors]
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREY = (200, 200, 200)
BLACK = (0, 0, 0)
isInterpolationOn = True

displayPixelWidth = width / 30
displayPixelHeight = height / 30

lcd = pygame.display.set_mode((320, height), pygame.FULLSCREEN)

lcd.fill((255,0,0))

pygame.display.update()
pygame.mouse.set_visible(True)

lcd.fill((0,0,0))
pygame.display.update()

def exit_window():
    pygame.quit()

def switch_interpolation():
    not isInterpolationOn

def screenshot():
    pygame.image.save(lcd, 'pic.png')	

#some utility functions
def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))

def map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def mousebuttondown():
    pos = pygame.mouse.get_pos()
    if exit_button.rect.collidepoint(pos):
        exit_button.call_back()
    if screenshot_button.rect.collidepoint(pos):
        screenshot_button.call_back()
    if interpolation_button.rect.collidepoint(pos):
        interpolation_button.call_back()


class Button():
    def __init__(self, txt, location, action, bg=WHITE, fg = BLACK, size = (50,20), font_name="Segoe Print", font_size = 10):
        self.color = bg
        self.bg = bg
        self.fg =fg
        self.size = size

        self.font = pygame.font.SysFont(font_name, font_size)

        self.txt = txt

        self.txt_surf = self.font.render(self.txt, 1, self.fg)
        self.txt_rect = self.txt_surf.get_rect(center=[s//2 for s in self.size])

        self.surface = pygame.surface.Surface(size)

        self.rect = self.surface.get_rect(center=location)

        self.call_back_ = action

    def mouseover(self):
        self.bg = self.color
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            self.bg = GREY  # mouseover color


    def draw(self):
        self.mouseover()
        self.surface.fill(self.bg)
        self.surface.blit(self.txt_surf, self.txt_rect)
        lcd.blit(self.surface, self.rect)

    def call_back(self):
        self.call_back_()


interpolation_button = Button("Interpolation", (290, 20), switch_interpolation)

exit_button = Button("Exit", (290, 60), exit_window)

screenshot_button = Button("Screenshot", (290, 100), screenshot)

#let the sensor initialize
time.sleep(.1)

while(1):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
                mousebuttondown()

    #read the pixels
    pixels = []
    for row in sensor.pixels:
        pixels = pixels + row
    pixels = [map(p, MINTEMP, MAXTEMP, 0, COLORDEPTH - 1) for p in pixels]

    #perform interpolation
    if isInterpolationOn == True:
        bicubic = griddata(points, pixels, (grid_x, grid_y), method='cubic')
    else:
        bicubic = griddata(points, pixels, (grid_x_no_interpolation, grid_y_no_interpolation))
        displayPixelWidth = width / 8
        displayPixelHeight = height / 8

    #draw everything
    for ix, row in enumerate(bicubic):
        for jx, pixel in enumerate(row):
            pygame.draw.rect(lcd, colors[constrain(int(pixel), 0, COLORDEPTH- 1)], (displayPixelHeight * ix, displayPixelWidth * jx, displayPixelHeight, displayPixelWidth))
    interpolation_button.draw()
    exit_button.draw()
    screenshot_button.draw()
    pygame.display.update()
