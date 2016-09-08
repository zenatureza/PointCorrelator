#!/usr/bin/env python

import sys, os
import pygame
import operator
from operator import itemgetter
from pygame.locals import *

# Constants
BACKGROUND_COLOR = (250,250,250)
WIDTH, HEIGHT = 640, 480
POINT_COLOR = (0, 150, 0)
HIGHLIGHT_COLOR = (150, 0, 0)
POINT_RADIUS = 3
HIGHLIGHT_RADIUS = 5
HIGHLIGHT_WIDTH = 2
CLICK_PRECISION = 5

class PointCorrelator(object):
    def __init__(self, pointsFile, imageFile):
        pygame.init()               # initializes pygame modules
        self.pointsFile = pointsFile
        self.imageFile = imageFile
        self.points_list = list()
        self.highlighted_points = list()                                    # stores highlighted points

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), RESIZABLE)   # set screen mode
        self.loadPoints()                                                   # loads file with point data
        self.loadImage()                                                    # loads image that the points will be connected to
    
    def loadPoints(self):
        pts = open(self.pointsFile, 'r')                    # opens file with points read-only
        for string in pts.readlines():                      # reads file line by line, getting x and y information
            x, y = [int(x) for x in string.split(',')]      # evil string manipulation
            self.points_list.append((x,y))                  # appends new points to points list
        pts.close()                                         # close file (good programming!)        
        
        self.ptsSurface = pygame.Surface((max(self.points_list, key=itemgetter(0))[0], \
                        max(self.points_list, key=itemgetter(1))[1]))   # creates surface for drawing the points
                                                                        # of the size max(x), max(y)

#       self.ptsSurface = pygame.transform.scale(self.ptsSurface, (300, 300))       # resize the surface (only resizes the actual
                                                                                    # surface, not what's drawn in it)
        
        self.highlightSurface = pygame.Surface(self.ptsSurface.get_size())          # creates new surface with same size as ptsSurface
                                                                                    # this will be used for highlighting points
        self.highlightSurface.set_colorkey((0, 0, 0))                               # set transparency color to black

    def loadImage(self):
        self.imgSurface = pygame.image.load(self.imageFile)

    def resize(self, new_width, new_height):
        self.screen = pygame.display.set_mode((new_width, new_height), RESIZABLE)   # set new mode for the screen when the window 
                                                                                    # is resized

    # This method tests if a point clicked on the screen is in the points_list
    # loaded from the file. This ensures that only points present in the list
    # can be selected
    def checkPoint(self, point_clicked):
        print point_clicked
        is_in = False
        for point in self.points_list:
            if point_clicked[0] < point[0] + CLICK_PRECISION and point_clicked[1] < point[1]\
            + CLICK_PRECISION and point_clicked[0] > point[0] - CLICK_PRECISION \
            and point_clicked[1] > point[1] - CLICK_PRECISION:                      # yeah, this is pretty fucking ugly
                is_in = True
                break
        if is_in is True: return point        # returns point where the click happened
        else: return None
    
    def highlightCircle(self, point_to_highlight):
        if point_to_highlight is None:                          # checks if there's a point to highlight
            return

        already_highlighted = 0
        for tup in self.highlighted_points:
            if point_to_highlight == tup:
                already_highlighted = 1
                break

        self.highlighted_points.append(point_to_highlight)      # adds point to the list of already highlighted points

        if(already_highlighted == 0):
            print "Highlighting %s" % (point_to_highlight, )
            pygame.draw.circle(self.highlightSurface, HIGHLIGHT_COLOR, \
                                point_to_highlight, HIGHLIGHT_RADIUS, HIGHLIGHT_WIDTH)
    
    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        for point in self.points_list:
            pygame.draw.circle(self.ptsSurface, POINT_COLOR, \
                        point, POINT_RADIUS)                    # draw point by point points in self.points_list (confusing)    
        self.screen.blit(self.ptsSurface, (0, 0))               # blits ptsSurface
        offsetX = self.ptsSurface.get_rect()[2]                 # gets X offset for drawing the image
        self.screen.blit(self.imgSurface, (offsetX, 0))         # blits imgSurface to the right of ptsSurface
        self.screen.blit(self.highlightSurface, (0,0))          # blits highlightSurface on the screen
        pygame.display.flip()                                   # actually shows shit on screen

    def events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            elif event.type == KEYUP:
                if event.key == K_ESCAPE: return False
            elif event.type == VIDEORESIZE:
                self.resize(event.w, event.h)
            elif event.type == MOUSEBUTTONUP:
                self.highlightCircle(self.checkPoint(event.pos)) # this actually works

        return True

   
    def mainLoop(self):
        while self.events():
            self.draw()
    
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "Usage: %s pointsFile.pts imageFile.img" % sys.argv[0]
        sys.exit()
    
    pc = PointCorrelator(sys.argv[1], sys.argv[2])
    pc.mainLoop()
