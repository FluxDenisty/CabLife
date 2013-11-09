import json
from mapobject import *


class ObjImporter(object):
    @staticmethod
    def readFile(fileName):
        json_file = open(fileName)
        json_data = json.load(json_file)
        json_file.close()
        objList = []

        for data in json_data:
            name = data["name"]
            pos = Position(data["pos"]["x"], data["pos"]["y"])
            dim = Dimension(data["dim"]["w"], data["dim"]["h"])
            type = data["type"]
            dir = 1
            if "dir" in data:
                dir = data["dir"]

            obj = MapObject(name, type, pos, dim, dir)
            objList.append(obj)

        return objList

if __name__ == "__main__":
    data = ObjImporter.readFile("objdefines.json")
    print data
