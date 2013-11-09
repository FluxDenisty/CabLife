from objimporter import *


class MapGrid(object):
    B_TL = "B_TL"
    B_T = "B__T"
    B_TR = "B_TR"
    B_L = "B__L"
    B_R = "B__R"
    B_BL = "B_BL"
    B_BR = "B_BR"
    B_B = "B__B"
    B_C = "B__C"

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
        self.grid = [["____" for x in range(maxWidth)] for x in range(maxHeight)]

        # for now just differentiate between types
        # TODO: later set for each type of sprite
        for obj in objList:
            # handle buldings
            if obj.type == "building":
                self._fillGridForBuilding(obj)

    def printGrid(self):
        for l in self.grid:
            for cell in l:
                print cell,
            print 

    def _fillGridForBuilding(self, obj):
        left = obj.pos.x
        right = obj.pos.x + obj.dim.w - 1
        top = obj.pos.y
        bot = obj.pos.y + obj.dim.h - 1 

        for x in range(left, right + 1):
            for y in range(top, bot + 1):
                if x == left:
                    if y == top:
                        self.grid[y][x] = MapGrid.B_TL
                    elif y == bot:
                        self.grid[y][x] = MapGrid.B_BL
                    else:
                        self.grid[y][x] = MapGrid.B_L

                elif x == right:
                    if y == top:
                        self.grid[y][x] = MapGrid.B_TR
                    elif y == bot:
                        self.grid[y][x] = MapGrid.B_BR
                    else:
                        self.grid[y][x] = MapGrid.B_R

                elif y == top:
                    self.grid[y][x] = MapGrid.B_T

                elif y == bot:
                    self.grid[y][x] = MapGrid.B_B

                else:
                    self.grid[y][x] = MapGrid.B_C


if __name__ == "__main__":
    data = ObjImporter.readFile("objdefines.json")
    grid = MapGrid()
    grid.createGrid(data)
    grid.printGrid()
