import os
class ResultWritter:
    def __init__(self, resultPath):
        self.file = open(resultPath, "w")

    def __del__(self):
        self.file.close()

    def writeResult(self, s):
        self.file.write(s + "\n")

    def saveDic(self, dic):
        print(type(dic))
        for k, v in dic.items():
            line = str(k) + "      "
            if type(v) is list:
                for item in v:
                    line += "," + str(item)
            else:
                line += str(v)
            print(line)
            self.writeResult(line)

    def saveList(self, dic):
        print(type(dic))
        line = ""
        for item in dic:
            line += "," + str(item)
        print(line)
        self.writeResult(line)
        
    def saveListLine(self, dic):
        for item in dic:
            self.writeResult(str(item))