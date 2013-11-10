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
    def __init__(self, name, type, pos, dim, direc):
        self.name = name
        self.type = type
        self.pos = pos
        self.dim = dim
        self.direc = direc

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return ("<MapObject name:%s type:%s pos:%s dim:%s>"
                % (self.name, self.type, self.pos, self.dim))
