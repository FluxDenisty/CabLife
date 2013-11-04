from objimporter import *


class DrawGridGenerator(object):
    @staticmethod
    def createGrid(objList):
        # first get the max width and max height
        # also pivot for objects are bottom left
        maxWidth = 0
        maxHeight = 0
        for obj in objList:
            maxWidth = max(obj.pos.x + obj.dim.w, maxWidth)
            maxHeight = max(obj.pos.y + obj.dim.h, maxHeight)

        # initialize grid
        grid = [[0 for x in range(maxHeight)] for x in range(maxWidth)]

        return grid

if __name__ == "__main__":
    data = ObjImporter.readFile("objdefines.json")
    grid = DrawGridGenerator.createGrid(data)
    print grid
