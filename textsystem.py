import pygame
from pygame import draw
from pygame import Color


class Palette(object):
    '''
    A convience object for the 4 available colours
    '''
    DARK = Color(15, 56, 15)
    NORM = Color(48, 98, 48)
    LIGHT = Color(139, 172, 15)
    BRIGHT = Color(155, 188, 15)


class TextSystem(object):

    text = [
        "WWWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWWW"]

    FIND_TEXT = [
        "FIND A PASSENGER AND",
        "PICK THEM UP"]

    PICKUP_TEXT = [
        "HELLO! CAN YOU TAKE ME",
        "TO THE STORE PLEASE?"]

    DROPOFF_TEXT = [
        "THANK YOU VERY MUCH!",
        "HAVE A NICE DAY!"]

    def __init__(self):
        self.timer = 0
        self.animTime = 3000
        self.font = pygame.font.SysFont("monospace", 12)
        self.state = "find"
        self.currentText = self.FIND_TEXT
        self.passenger = None
        self.ignore = None

    def update(self, diff):
        self.timer += diff

    def pickup(self, passenger):
        if (self.ignore != passenger and passenger.done is False):
            passenger.done = True
            self.passenger = passenger
            self.timer = 0
            self.state = "driving"
            self.currentText = self.PICKUP_TEXT

    def dropoff(self, dropoff):
        if (self.passenger.dest == dropoff):
            self.passenger = None
            self.ignore = dropoff
            self.timer = 0
            self.state = "find"
            self.currentText = self.DROPOFF_TEXT

    def getText(self):
        text = [self.currentText[0], self.currentText[1]]
        length = (len(text[0]) + len(text[1]))
        progress = int((self.timer / self.animTime) * length)
        if (progress < len(text[0])):
            text[0] = text[0][:progress]
            text[1] = ""
        elif (progress < length):
            text[1] = text[1][:progress - len(text[0])]

        return text

    def drawText(self, window):
        rect = (0, 118, 160, 144 - 118)
        draw.rect(window, Palette.NORM, rect)

        text = self.getText()
        label = self.font.render(text[0], False, Palette.LIGHT)
        window.blit(label, (3, 120))
        label = self.font.render(text[1], False, Palette.LIGHT)
        window.blit(label, (3, 130))
