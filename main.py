import pygame
from pygame import display
# from pygame import draw
from pygame import Color
import sys


class Palette(object):
    '''
    A convience object for the 4 available colours
    '''
    DARK = Color(15, 56, 15)
    NORM = Color(48, 98, 48)
    LIGHT = Color(139, 172, 15)
    BRIGHT = Color(155, 188, 15)


class TextSystem(object):

    def __init__(self):
        self.timer = 0
        self.animTime = 3000
        self.font = pygame.font.SysFont("monospace", 12)

    def update(self, diff):
        self.timer += diff

    def getText(self):
        text = [
            "WWWWWWWWWWWWWWWWWWWW",
            "WWWWWWWWWWWWWWWWWWWW"]
        length = (len(text[0]) + len(text[1]))
        progress = int((self.timer / self.animTime) * length)
        if (progress < len(text[0])):
            text[0] = text[0][:progress]
            text[1] = ""
        elif (progress < length):
            text[1] = text[1][:progress - len(text[0])]

        return text

    def drawText(self, window):
        text = self.getText()
        label = self.font.render(text[0], False, Palette.LIGHT)
        window.blit(label, (10, 120))
        label = self.font.render(text[1], False, Palette.LIGHT)
        window.blit(label, (10, 130))

global window

pygame.init()
clock = pygame.time.Clock()

window = display.set_mode(
    (160, 144))
display.set_caption('CabLife')
display.init()

textSystem = TextSystem()


while True:
    diff = (1000.0 / 59.7)
    window.fill(Palette.DARK)

    textSystem.update(diff)
    textSystem.drawText(window)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                pygame.quit()
                sys.exit()

    display.flip()
    clock.tick(59.7)
