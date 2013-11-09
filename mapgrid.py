from objimporter import *

class MapGridCell(object):
    # types
    TYPE_BUILDING = "BD"
    TYPE_ROAD = "RD"

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

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        string = "%s%s" % (self.type, self.pos)
        if len(string) == 3:
            string += "_"
        string += self.dir

        return string

class MapGrid(object):
    EMPTY = "_" * 5

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
        self.grid = [[MapGrid.EMPTY for x in range(maxWidth)] for x in range(maxHeight)]

        # for now just differentiate between types
        for obj in objList:
            # handle buldings
            if obj.type == "building":
                self._fillGridForBuilding(obj)
            if obj.type == "road":
                self._fillGridForRoad(obj)

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

        # TODO: handle overlapping case


    def _fillGridForRoad(self, obj):
        left = obj.pos.x
        right = obj.pos.x + obj.dim.w - 1
        top = obj.pos.y
        bot = obj.pos.y + obj.dim.h - 1 

        isVert = obj.dim.w < obj.dim.h

        for x in range(left, right + 1):
            for y in range(top, bot + 1):
                cell = MapGridCell()
                cell.type = MapGridCell.TYPE_ROAD

                if isVert:
                    if (x - left) == 0:
                        cell.pos = MapGridCell.POS_LEFT
                        cell.dir = MapGridCell.DIR_VERT
                    elif (x - left) == right:
                        cell.pos = MapGridCell.POS_RIGHT
                        cell.dir = MapGridCell.DIR_VERT
                    elif (x - left) % MapGrid.R_LINE_SEP_NUM == 0:
                        cell.pos = MapGridCell.POS_CENTER
                        cell.dir = MapGridCell.DIR_VERT
                    else:
                        cell.pos = MapGridCell.POS_CENTER
                else:
                    if (y - top) == 0:
                        cell.pos = MapGridCell.POS_TOP
                        cell.dir = MapGridCell.DIR_HOR
                    elif (y - top) == bot:
                        cell.pos = MapGridCell.POS_BOT
                        cell.dir = MapGridCell.DIR_HOR
                    elif (y - bot) % MapGrid.R_LINE_SEP_NUM == 0:
                        cell.pos = MapGridCell.POS_CENTER
                        cell.dir = MapGridCell.DIR_HOR
                    else:
                        cell.pos = MapGridCell.POS_CENTER

                self._setGrid(cell, x, y)


    def _fillGridForBuilding(self, obj):
        left = obj.pos.x
        right = obj.pos.x + obj.dim.w - 1
        top = obj.pos.y
        bot = obj.pos.y + obj.dim.h - 1 

        for x in range(left, right + 1):
            for y in range(top, bot + 1):
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
