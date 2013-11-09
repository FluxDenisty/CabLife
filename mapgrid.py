from objimporter import *
import copy

class MapGridCell(object):
    # types
    TYPE_BUILDING = "BD"
    TYPE_ROAD = "RD"
    TYPE_SIDEWALK = "SW"

    # positions
    POS_TOP = "T"
    POS_BOT = "B"
    POS_LEFT = "L"
    POS_RIGHT = "R"
    POS_TOPLEFT = "TL"
    POS_TOPRIGHT = "TR"
    POS_BOTLEFT = "BL"
    POS_BOTRIGHT = "BR"
    POS_CENTER = "C"

    # directions
    DIR_HOR = "H"
    DIR_VERT = "V"
    DIR_NEUTRAL = "N"

    def __init__(self, type="", pos="", dir=DIR_NEUTRAL):
        self.type = type
        self.pos = pos
        self.dir = dir
        self.overlap = False

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        string = "%s%s" % (self.type, self.pos)
        if len(string) == 3:
            string += "_"
        string += self.dir
        c = 1 if self.overlap else 0
        string += str(c)

        return string

class MapGrid(object):
    EMPTY = "_" * 6

    R_LINE_SEP_NUM = 3

    def __init__(self):
        self.grid = []

    def createGrid(self, objList):
        # first get the max width and max height
        # also pivot for objects are bottom left
        maxWidth = 0
        maxHeight = 0
        for obj in objList:
            maxWidth = max(obj.pos.x + obj.dim.w, maxWidth)
            maxHeight = max(obj.pos.y + obj.dim.h, maxHeight)

        # initialize grid
        self.grid = [[MapGrid.EMPTY for x in xrange(maxWidth)] for x in xrange(maxHeight)]

        # for now just differentiate between types
        for obj in objList:
            # handle buldings
            if obj.type == "building":
                self._fillGridForBuilding(obj)
            elif obj.type == "road":
                if obj.dir == 2:
                    self._handleTwoDirRoad(obj)
                else:
                    self._fillGridForRoad(obj)
            elif obj.type == "sidewalk":
                self._fillGridForSidewalk(obj)

    def _handleTwoDirRoad(self, obj):
        isVert = obj.dim.w < obj.dim.h
        obj.dir = 1

        newObj = copy.deepcopy(obj)

        if isVert:
            width = (obj.dim.w + 1) / 2
            obj.dim.w = width

            newObj.dim.w = width
            newObj.pos.x = obj.pos.x + obj.dim.w - 1
        else:
            height = (obj.dim.h + 1) / 2
            obj.dim.h = height

            newObj.dim.h = height
            newObj.pos.y = obj.pos.y + obj.dim.h - 1

        self._fillGridForRoad(obj)
        self._fillGridForRoad(newObj)

    def printGrid(self):
        for l in self.grid:
            for cell in l:
                print cell,
            print 

    def _setGrid(self, cell, x, y):
        # if there's no overlap, just set it
        if self.grid[y][x] == MapGrid.EMPTY:
            self.grid[y][x] = cell
            return

        # Buildings should never overlap
        if cell.type == MapGridCell.TYPE_BUILDING:
            return

        # Sidewalks take precedence over roads
        if cell.type == MapGridCell.TYPE_SIDEWALK:
            self.grid[y][x] = cell
            return
        
        # handle roads overlapping
        if cell.dir == self.grid[y][x].dir:
            self.grid[y][x].pos = MapGridCell.POS_CENTER
            self.grid[y][x].overlap = True
        else:
            self.grid[y][x].dir = MapGridCell.DIR_NEUTRAL
            self.grid[y][x].pos = MapGridCell.POS_CENTER
            self.grid[y][x].overlap = True


    def _fillGridForRoad(self, obj):
        left = obj.pos.x
        right = obj.pos.x + obj.dim.w - 1
        top = obj.pos.y
        bot = obj.pos.y + obj.dim.h - 1 

        isVert = obj.dim.w < obj.dim.h

        for x in xrange(left, right + 1):
            for y in xrange(top, bot + 1):
                cell = MapGridCell()
                cell.type = MapGridCell.TYPE_ROAD

                if isVert:
                    if x == left:
                        cell.pos = MapGridCell.POS_LEFT
                        cell.dir = MapGridCell.DIR_VERT
                    elif x == right:
                        cell.pos = MapGridCell.POS_RIGHT
                        cell.dir = MapGridCell.DIR_VERT
                    elif (x - left) % MapGrid.R_LINE_SEP_NUM == 0:
                        cell.pos = MapGridCell.POS_CENTER
                        cell.dir = MapGridCell.DIR_VERT
                    else:
                        cell.pos = MapGridCell.POS_CENTER
                else:
                    if y == top:
                        cell.pos = MapGridCell.POS_TOP
                        cell.dir = MapGridCell.DIR_HOR
                    elif y == bot:
                        cell.pos = MapGridCell.POS_BOT
                        cell.dir = MapGridCell.DIR_HOR
                    elif (y - bot) % MapGrid.R_LINE_SEP_NUM == 0:
                        cell.pos = MapGridCell.POS_CENTER
                        cell.dir = MapGridCell.DIR_HOR
                    else:
                        cell.pos = MapGridCell.POS_CENTER

                self._setGrid(cell, x, y)

    def _fillGridForSidewalk(self, obj):
        left = obj.pos.x
        right = obj.pos.x + obj.dim.w - 1
        top = obj.pos.y
        bot = obj.pos.y + obj.dim.h - 1 

        for x in xrange(left, right + 1):
            for y in xrange(top, bot + 1):
                cell = MapGridCell()
                cell.type = MapGridCell.TYPE_SIDEWALK

                if x == left:
                    if y == top:
                        cell.pos = MapGridCell.POS_TOPLEFT
                    elif y == bot:
                        cell.pos = MapGridCell.POS_BOTLEFT
                    else:
                        cell.pos = MapGridCell.POS_LEFT
                elif x == right:
                    if y == top:
                        cell.pos = MapGridCell.POS_TOPRIGHT
                    elif y == bot:
                        cell.pos = MapGridCell.POS_BOTRIGHT
                    else:
                        cell.pos = MapGridCell.POS_RIGHT
                elif y == top:
                    cell.pos = MapGridCell.POS_TOP
                elif y == bot:
                    cell.pos = MapGridCell.POS_BOT
                else:
                    cell.pos = MapGridCell.POS_CENTER

                self._setGrid(cell, x, y)

    def _fillGridForBuilding(self, obj):
        left = obj.pos.x
        right = obj.pos.x + obj.dim.w - 1
        top = obj.pos.y
        bot = obj.pos.y + obj.dim.h - 1 

        for x in xrange(left, right + 1):
            for y in xrange(top, bot + 1):
                cell = MapGridCell()
                cell.type = MapGridCell.TYPE_BUILDING

                if x == left:
                    if y == top:
                        cell.pos = MapGridCell.POS_TOPLEFT
                    elif y == bot:
                        cell.pos = MapGridCell.POS_BOTLEFT
                    else:
                        cell.pos = MapGridCell.POS_LEFT
                elif x == right:
                    if y == top:
                        cell.pos = MapGridCell.POS_TOPRIGHT
                    elif y == bot:
                        cell.pos = MapGridCell.POS_BOTRIGHT
                    else:
                        cell.pos = MapGridCell.POS_RIGHT
                elif y == top:
                    cell.pos = MapGridCell.POS_TOP
                elif y == bot:
                    cell.pos = MapGridCell.POS_BOT
                else:
                    cell.pos = MapGridCell.POS_CENTER

                self._setGrid(cell, x, y)


if __name__ == "__main__":
    data = ObjImporter.readFile("objdefines.json")
    grid = MapGrid()
    grid.createGrid(data)
    grid.printGrid()
