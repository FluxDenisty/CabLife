import pygame
from pygame import display
import sys
from Box2D.b2 import world
from objimporter import ObjImporter
from Box2D import b2Vec2
from Box2D import b2BodyDef, b2PolygonShape, b2_staticBody, b2CircleShape
from Box2D import b2FixtureDef, b2ContactListener
from car import TDCar, CarTireFUD
from textsystem import Palette, TextSystem
from mapgrid import MapGrid
from mapobject import MapObject
import math

PPM = 1

TILE_SIZE = 6

TDC_LEFT = int('0001', 2)
TDC_RIGHT = int('0010', 2)
TDC_UP = int('0100', 2)
TDC_DOWN = int('1000', 2)

FUD_CAR_TIRE = 0
FUD_GROUND_AREA = 1


class ContactListener(b2ContactListener):

    def __init__(self, textSystem, car):
        b2ContactListener.__init__(self)
        self.textSystem = textSystem
        self.playerCar = car

    def handleContact(self, contact, began):
        if (not began):
            return
        a = contact.fixtureA
        b = contact.fixtureB
        fudA = a.userData
        fudB = b.userData

        player = None
        other = None
        if (type(fudA) == CarTireFUD):
            player = fudA
            other = fudB
        elif (type(fudB) == CarTireFUD):
            player = fudB
            other = fudA

        if (player is None or other is None or player.car is not self.playerCar):
            return

        if (type(other) == MapObject):
            if (textSystem.state == "find" and other.name == "pickup"):
                self.textSystem.pickup(other)
            if (textSystem.state == "driving" and other.name == "pickup"):
                self.textSystem.dropoff(other)

    def BeginContact(self, contact):
        self.handleContact(contact, True)

    def EndContact(self, contact):
        self.handleContact(contact, False)

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

textSystem = TextSystem()

car = TDCar(world)

world.contactListener = ContactListener(textSystem, car)

objects = []
pickups = []
otherCars = []

data = ObjImporter.readFile("objdefines.json")
for o in data:
    if o.name == "building":
        pos = b2Vec2(o.pos.x * TILE_SIZE + o.dim.w * TILE_SIZE / 2, -o.pos.y * TILE_SIZE - o.dim.h * TILE_SIZE / 2)
        dim = b2Vec2(o.dim.w * TILE_SIZE / 2, o.dim.h * TILE_SIZE / 2)
        bodyDef = b2BodyDef()
        bodyDef.type = b2_staticBody
        bodyDef.userData = o
        bodyDef.position = pos
        body = world.CreateBody(bodyDef)
        polygonShape = b2PolygonShape()
        polygonShape.SetAsBox(dim.x, dim.y)
        fixture = body.CreateFixture(shape=polygonShape)
        fixture.userData = o
        body.userData = o
        o.m_body = body
        objects.append(body)
    elif o.name == "pickup":
        pos = b2Vec2(o.pos.x * TILE_SIZE, -o.pos.y * TILE_SIZE)
        dim = b2Vec2(o.dim.w * TILE_SIZE, o.dim.h * TILE_SIZE)
        bodyDef = b2BodyDef()
        bodyDef.type = b2_staticBody
        bodyDef.userData = o
        bodyDef.position = pos
        body = world.CreateBody(bodyDef)
        circleShape = b2CircleShape()
        circleShape.radius = dim.x
        fixtureDef = b2FixtureDef()
        fixtureDef.shape = circleShape
        fixtureDef.isSensor = True
        fixture = body.CreateFixture(fixtureDef)
        fixture.userData = o
        body.userData = o
        o.m_body = body
        o.done = False
        pickups.append(body)
    elif o.name == "car":
        pos = b2Vec2(o.pos.x * TILE_SIZE, -o.pos.y * TILE_SIZE)
        dim = b2Vec2(o.dim.w * TILE_SIZE, o.dim.h * TILE_SIZE)
        otherCar = TDCar(world, pos)
        angle = 0
        if (o.dim.h == 1):
            angle = math.pi
        else:
            angle = -o.dim.w * math.pi / 2.0
        otherCar.m_body.__SetTransform(pos, angle)
        otherCars.append(otherCar)

prev = pickups[len(pickups) - 1].userData
for body in pickups:
    body.userData.dest = prev
    prev = body.userData

controlState = 0

size = (160, 144)
scale = 2
scaledSize = (size[0] * scale, size[1] * scale)
window = display.set_mode(scaledSize)
gbScreen = pygame.Surface(size)
display.set_caption('CabLife')
display.init()

mapGrid = MapGrid()
mapGrid.createGrid(data)
grid = mapGrid.grid
sprites = mapGrid.getUsedSpritesDict()
for key in sprites.keys():
    sprite_dir = "./sprite/"
    sprite_dir += key
    sprites[key] = pygame.image.load(sprite_dir).convert()

#car.m_body.position = b2Vec2(25 * TILE_SIZE, -25 * TILE_SIZE)

while True:
    diff = (1000.0 / 59.7)
    gbScreen.fill(Palette.DARK)

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

    position = car.m_body.worldCenter
    offset = [-position.x * PPM, position.y * PPM]

    offset[0] += size[0] / 2
    offset[1] += size[1] / 2 - 13

    topLeft = [0, 0]
    topLeft[0] = int(position.x / TILE_SIZE - 15)
    topLeft[1] = int(-position.y / TILE_SIZE - 15)

    for x in xrange(topLeft[0], topLeft[0] + 30):
        for y in xrange(topLeft[1], topLeft[1] + 27):
            if (y < 0 or x < 0 or len(grid) <= y or len(grid[y]) <= x):
                continue
            if isinstance(grid[y][x], str):
                continue

            sprite = pygame.sprite.Sprite()
            sprite.image = sprites[grid[y][x].getSpriteName()]
            drawPos = [x * TILE_SIZE * PPM, y * TILE_SIZE * PPM,
                       TILE_SIZE * PPM, TILE_SIZE * PPM]
            drawPos[0] += offset[0]
            drawPos[1] += offset[1]
            sprite.rect = sprite.image.get_rect()
            sprite.rect.topleft = [drawPos[0], drawPos[1]]
            gbScreen.blit(sprite.image, sprite.rect)

    #sprite = pygame.sprite.Sprite()
    #sprite.image = sprites["car.png"]
    #sprite.rect = sprite.image.get_rect()
    #sprite.rect.topleft = [position[0] + offset[0] - 12, -position[1] + offset[1] - 15]
    #gbScreen.blit(sprite.image, sprite.rect)

    for drawCar in ([car] + otherCars):
        for body in (drawCar.GetAllBodies()):
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

                ## But wait! It's upside-down! Pygame and Box2D orient their
                # axes in different ways. Box2D is just like how you learned
                # in high school, with positive x and y directions going
                # right and up. Pygame, on the other hand, increases in the
                # right and downward directions. This means we must flip
                # the y components.
                vertices = [
                    (v[0] + offset[0],
                     - v[1] + offset[1]) for v in vertices]

                pygame.draw.polygon(gbScreen, Palette.NORM, vertices)

    for body in pickups:
        if (
                (textSystem.state == "find" and
                 textSystem.ignore != body.userData and
                 body.userData.done is False) or
                (textSystem.state == "driving" and
                 textSystem.passenger.dest == body.userData)):
            pos = body.worldCenter.copy()
            pos.x *= PPM
            pos.y *= -PPM
            pos.x += offset[0]
            pos.y += offset[1]
            pygame.draw.circle(
                gbScreen,
                Palette.BRIGHT,
                (int(pos.x), int(pos.y)),
                int(body.fixtures[0].shape.radius * PPM))

    textSystem.update(diff)
    textSystem.drawText(gbScreen)

    pygame.transform.scale(gbScreen, scaledSize, window)
    display.flip()
    clock.tick(59.7)
