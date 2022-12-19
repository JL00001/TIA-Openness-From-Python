
class father():
    def __init__(self,name,parentData = {}):
        self.name = name
        self.data = parentData
        
    def __str__(self):
        returnDir = {}
        returnDir["vars"] = vars(self)
        return str(returnDir)
        
    def __getitem__(self, name):
        return self.data[name]

class controlCabnetObject(father):
    def __init__(self, name,project):
        super().__init__(name,{})
        self.data["project"] = project
        
    def createControlArea(self,name):
        if name not in self.data.keys():
            object = controlAreaObject(name,self.data)
            self.data[name] = object
            return object
        else:
            raise KeyError
            
    def setCPU(self):
        pass
            
class controlAreaObject(father):
    def __init__(self,name,project):
        super().__init__(name,project)
        self.networkDevices  = {}
        
    def adoptNetworkDevice(self,objectDevice):
        if name not in self.networkDevices.keys():
            object = objectDevice
            self.data["networkDevices"][name] = object
            return object
        else:
            raise KeyError
        
    def addEzc(self,name):
        if name not in self.data.keys():
            object = ezcObject(name,self.data)
            self.data[name] = object
            return object
        else:
            raise KeyError
        
class ezcObject(father):
    def __init__(self,name,parentData):
        super().__init__(name,parentData)
        
    def addAsiEstop(self,name,asiAddress):
        import re
        if name not in self.data.keys():
            if re.search("^ASI_[A-Z][1-2]_([0-9]|[0-2][0-9]|3[01])$",asiAddress) != None:
                    object = asiEstopObject(name,asiAddress,self.data)
                    self.data[name] = object
                    return object
            else:
                raise ValueError
        else:
            raise KeyError
        
class asiEstopObject(father):
    def __init__(self,name,asiAddress,parentData):
        super().__init__(name,parentData)
        self.data["asiAddress"] = asiAddress
        self.createAsiTags(asiAddress)
        
    def createAsiTags(self,asiAddress):
        pass
        


CC = controlCabnetObject("Test","")
area = CC.createControlArea("Area1")
CC.createControlArea("Area2")
CC.createControlArea("Area3")
CC.createControlArea("Area4")

EZC = area.addEzc("EZC01")

CC["Area1"]['EZC01'].addAsiEstop("EStop","ASI_A1_28")

print(area)
print(CC["Area1"]['EZC01'])