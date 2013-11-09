import pygame
from pygame import display
from pygame import draw
from pygame import Color
import sys
from Box2D.b2 import world
from car import TDCar

PPM = 1.0

TDC_LEFT = int('0001', 2)
TDC_RIGHT = int('0010', 2)
TDC_UP = int('0100', 2)
TDC_DOWN = int('1000', 2)

FUD_CAR_TIRE = 0
FUD_GROUND_AREA = 1


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
            "WWWWWWWWWWWWWWWWWWWWWW",
            "WWWWWWWWWWWWWWWWWWWWWW"]
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


def handleContact(contact, began):
    a = contact.GetFixtureA()
    b = contact.GetFixtureB()
    fudA = a.userData
    fudB = b.userData

    if (fudA is None or fudB is None):
        return

    if (fudA.getType() == FUD_CAR_TIRE or
            fudB.getType() == FUD_GROUND_AREA):
        tire_vs_groundArea(a, b, began)
    elif (fudA.getType() == FUD_GROUND_AREA or
            fudB.getType() == FUD_CAR_TIRE):
        tire_vs_groundArea(b, a, began)


def BeginContact(contact):
    handleContact(contact, True)


def EndContact(contact):
    handleContact(contact, False)


def tire_vs_groundArea(tireFixture, groundAreaFixture, began):
    tire = tireFixture.body.userData
    gaFud = groundAreaFixture.userData
    if (began):
        tire.addGroundArea(gaFud)
    else:
        tire.removeGroundArea(gaFud)


global breaking
breaking = False


def Step(car, m_controlState):
    global breaking
    direction = car.GetDirection()
    if ((controlState & TDC_UP and direction == -1) or
            (controlState & TDC_DOWN and direction == 1)):
        breaking = True

    car.update(m_controlState, breaking)

pygame.init()
clock = pygame.time.Clock()

world = world(gravity=(0, 0), doSleep=True)

car = TDCar(world)
controlState = 0

size = (160, 144)
scaledSize = (size[0] * 4, size[1] * 4)
window = display.set_mode(scaledSize)
gbScreen = pygame.Surface(size)
display.set_caption('CabLife')
display.init()

textSystem = TextSystem()

while True:
    diff = (1000.0 / 59.7)
    gbScreen.fill(Palette.DARK)

    textSystem.update(diff)
    textSystem.drawText(gbScreen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                pygame.quit()
                sys.exit()
            elif event.key == pygame.K_a:
                controlState |= TDC_LEFT
            elif event.key == pygame.K_d:
                controlState |= TDC_RIGHT
            elif event.key == pygame.K_w:
                controlState |= TDC_UP
            elif event.key == pygame.K_s:
                controlState |= TDC_DOWN
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                controlState &= ~TDC_LEFT
            elif event.key == pygame.K_d:
                controlState &= ~TDC_RIGHT
            elif event.key == pygame.K_w:
                controlState &= ~TDC_UP
                breaking = False
            elif event.key == pygame.K_s:
                controlState &= ~TDC_DOWN
                breaking = False

    Step(car, controlState)
    world.Step(diff, 10, 10)

    '''
    rect = [car.m_body.position.x, -car.m_body.position.y, 20, 20]
    rect[0] += 40
    rect[1] += 40
    draw.rect(gbScreen, Palette.LIGHT, rect)
    '''

    for body in (car.GetAllBodies()):  # or: world.bodies
        # The body gives us the position and angle of its shapes
        for fixture in body.fixtures:
            # The fixture holds information like density and friction,
            # and also the shape.
            shape = fixture.shape

            # Naively assume that this is a polygon shape. (not good normally!)
            # We take the body's transform and multiply it with each
            # vertex, and then convert from meters to pixels with the scale
            # factor.
            vertices = [(body.transform * v) * PPM for v in shape.vertices]

            # But wait! It's upside-down! Pygame and Box2D orient their
            # axes in different ways. Box2D is just like how you learned
            # in high school, with positive x and y directions going
            # right and up. Pygame, on the other hand, increases in the
            # right and downward directions. This means we must flip
            # the y components.
            vertices = [(v[0] + 50, 144 - v[1] - 50) for v in vertices]

            pygame.draw.polygon(gbScreen, Palette.NORM, vertices)

    pygame.transform.scale(gbScreen, scaledSize, window)
    display.flip()
    clock.tick(59.7)
