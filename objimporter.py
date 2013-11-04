import json

class ObjImporter(object):
    @staticmethod
    def readFile(fileName):
        json_file = open(fileName)
        data = json.load(json_file)
        json_file.close()
        return data

if __name__ == "__main__":
    data = ObjImporter.readFile("objdefines.json")
    print data
