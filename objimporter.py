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
            type = None

            if data["type"] == "passable":
                type = ObjTypeEnum.OBJ_TYPE_PASSABLE
            elif data["type"] == "impassable":
                type = ObjTypeEnum.OBJ_TYPE_IMPASSABLE
            elif data["type"] == "semipassable":
                type = ObjTypeEnum.OBJ_TYPE_SEMIPASSABLE
            else:
                print "Invalid type in Json file"
                return None

            obj = MapObject(name, type, pos, dim)
            objList.append(obj)

        return objList

if __name__ == "__main__":
    data = ObjImporter.readFile("objdefines.json")
    print data
