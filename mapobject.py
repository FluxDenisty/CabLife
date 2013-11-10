from Box2D import b2Vec2, b2BodyDef, b2FixtureDef
from Box2D import b2PolygonShape, b2CircleShape, b2_staticBody


class ObjTypeEnum(object):
    OBJ_TYPE_PASSABLE = 'p'
    OBJ_TYPE_IMPASSABLE = 'i'
    OBJ_TYPE_SEMIPASSABLE = 's'


class Position(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "<Position x:%s y:%s>" % (self.x, self.y)


class Dimension(object):
    def __init__(self, w, h):
        self.w = w
        self.h = h

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "<Dimension w:%s h:%s>" % (self.w, self.h)


class MapObject(object):
    def __init__(self, name, kind, pos, dim, direc):
        self.name = name
        self.kind = kind
        self.pos = pos
        self.dim = dim
        self.direc = direc

    def CreateBody(self, world, TILE_SIZE):
        pos = b2Vec2(self.pos.x * TILE_SIZE, -self.pos.y * TILE_SIZE)
        dim = b2Vec2(self.dim.w * TILE_SIZE, self.dim.h * TILE_SIZE)
        bodyDef = b2BodyDef()
        bodyDef.type = b2_staticBody
        bodyDef.userData = self
        bodyDef.position = pos
        body = world.CreateBody(bodyDef)
        fixture = None
        if (self.name == "building"):
            dim.x /= 2.0
            dim.y /= 2.0
            pos.x += self.dim.w * TILE_SIZE / 2.0
            pos.y -= self.dim.h * TILE_SIZE / 2.0
            body.position = pos
            polygonShape = b2PolygonShape()
            polygonShape.SetAsBox(dim.x, dim.y)
            fixture = body.CreateFixture(shape=polygonShape)
        elif (self.name == "pickup"):
            circleShape = b2CircleShape()
            circleShape.radius = dim.x
            fixtureDef = b2FixtureDef()
            fixtureDef.shape = circleShape
            fixtureDef.isSensor = True
            fixture = body.CreateFixture(fixtureDef)
            self.done = False

        fixture.userData = self
        body.userData = self
        self.m_body = body
        return body

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return ("<MapObject name:%s kind:%s pos:%s dim:%s>"
                % (self.name, self.kind, self.pos, self.dim))
