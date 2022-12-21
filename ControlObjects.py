import clr
clr.AddReference('C:\\Program Files\\Siemens\\Automation\\Portal V17\PublicAPI\\V17\\Siemens.Engineering.dll')
import Siemens.Engineering
import System
import os

import OpennessTest
import xmlHeader
import sclObject
import xmlObjects

class father():
    def __init__(self,name,parent=None):
        self.name = name
        self.data = {}
        if parent != None:
            self.parent = parent
            self.data = parent.data
            self.updateParent(name,self)
        
    def __str__(self):
        return str(self.data.keys())
        
    def __getitem__(self, name):
        return self.data[name]
        
    def updateParent(self,name,thing):
        try:
            self.parent.data[name] = thing
            self.parent.updateParent(name, thing)
        except AttributeError:
            pass
            
    def keys(self):
        return vars(self).keys()

class controlCabnetObject(father):
    def __init__(self, name):
        super().__init__(name)
        self.networkDevices = {}
        self.__getProjectVariables()
        self.__setUpImportVariables()
        
    def __getProjectVariables(self):
        #Project
        self.project = self.project = Siemens.Engineering.TiaPortal.GetProcesses()[0].Attach().Projects[0]
        
        #Software
        for x in self.project.Devices:
            if x.TypeIdentifier != None and 'S71500' in x.TypeIdentifier:
                GsdDevice = OpennessTest.GsdDevice(x)
                break
        self.software = Siemens.Engineering.IEngineeringServiceProvider(GsdDevice.Device.DeviceItems[1]).GetService[Siemens.Engineering.HW.Features.SoftwareContainer]().Software
        
        #Tags
        self.tags = OpennessTest.tags(self.software)
        
        #Network Devices
        for x in self.project.Devices:
            if x.TypeIdentifier != None:
                if "BIHL UND WIEDEMANN-ASI GATEWAY" in x.TypeIdentifier:
                    self.networkDevices[x.Name] = OpennessTest.Pnag(x,self.tags)
                    
                elif "DEMATIC-PNCG" in x.TypeIdentifier:
                    self.networkDevices[x.Name] = OpennessTest.Pncg(x,self.tags)
                    
                    
        #Subnets + IO Systems
        if self.project.Subnets.Count > 0:
            self.subnet = self.project.Subnets[0]
            if self.subnet.IoSystems.Count == 0:
                print("ERROR: No IO Systems Detected")
                networkInterface = self.PLC.getNetworkInterface(self.PLC.Objects["Systems"]["PROFINET interface_1"]["Object"])
                networkInterface.IoControllers[0].CreateIoSystem("PROFINET IO-System")
                print("IO System Created")
        else:
            raise ValueError("ERROR: No Subnet Detected")
        
    def __setUpImportVariables(self):
        self.xml = xmlHeader.xmlHeader("Jacob's Magic")
        self.scl = sclObject.sclObject("Jacob's Magic_SetConfigs")
        self.blockGroupSw = self.software.BlockGroup.Groups.Find("Project").Groups.Find("Jacob's Magic")
        if self.blockGroupSw != None:
            self.blockGroupSw.Delete()
        self.blockGroupSw = self.software.BlockGroup.Groups.Find("Project").Groups.Create("Jacob's Magic")
        DefaultDBsSw = self.software.BlockGroup.Groups.Find("Project").Groups.Find("DefaultDBs")
        if DefaultDBsSw != None:
            DefaultDBsSw.Delete()
        self.DefaultDBsSw = self.software.BlockGroup.Groups.Find("Project").Groups.Create("DefaultDBs")
        
    def save(self):
        self.xml.save()
        self.scl.save()
        
        self.blockGroupSw.Blocks.Import(System.IO.FileInfo("{0}/{1}.xml".format(os.getcwd(),self.xml.Name)),Siemens.Engineering.ImportOptions.Override)
        self.blockGroupSw.Blocks.Import(System.IO.FileInfo("{0}/{1}.xml".format(os.getcwd(),self.scl.Name)),Siemens.Engineering.ImportOptions.Override)
        
    def createControlArea(self,name):
        if name not in self.data.keys():
            object = controlAreaObject(name,self)
            self.data[name] = object
            return object
        else:
            raise KeyError
            
    def addPlc(self):
        for x in self.project.Devices:
            if x.TypeIdentifier != None and 'S71500' in x.TypeIdentifier:
                OpennessTest.createPlc(x).setConfig()
                break
            
    def addAbbAcs380Drive(self,unitNumber,ip,zone=""):
        if unitNumber not in self.data.keys():
            OpennessTest.createAbbAcs380Drive(self.project,self.tags,unitNumber,ip,self.subnet,zone)
            xmlObjects.AbbAcs380Drive(unitNumber,self.xml.ObjectList,zone,self.scl,self.blockGroupSw)
            
        else:
            raise NameError("A Device Already Has That Name")
            
    def addScannerSickCLV6xx(self,unitNumber,ip,zone=""):
        if unitNumber not in self.data.keys():
            OpennessTest.createScannerSickCLV6xx(self.project,self.tags,unitNumber,ip,self.subnet,zone)
            xmlObjects.ScannerSickCLV6xx(unitNumber,self.xml.ObjectList,zone,self.scl,self.blockGroupSw)
            
        else:
            raise NameError("A Device Already Has That Name")
            
    def addPnpn(self,unitNumber,ip,zone=""):
        if unitNumber not in self.data.keys():
            OpennessTest.createPnpn(self.project,self.tags,unitNumber,ip,self.subnet,zone)
            
        else:
            raise NameError("A Device Already Has That Name")
            
    def addConnectionBox(self,unitNumber,ip,zone=""):
        if unitNumber not in self.data.keys():
            OpennessTest.createConnectionBox(self.project,self.tags,unitNumber,ip,self.subnet,zone)
            
        else:
            raise NameError("A Device Already Has That Name")
            
    def addHmi(self,unitNumber,ip,zone=""):
        if unitNumber not in self.data.keys():
            OpennessTest.createHmi(self.project,self.tags,unitNumber,ip,self.subnet,zone)
            
        else:
            raise NameError("A Device Already Has That Name")
        
    def addMoviMot(self,unitNumber,ip,zone=""):
        if unitNumber not in self.data.keys():
            OpennessTest.createMoviMot(self.project,self.tags,unitNumber,ip,self.subnet,zone)
            xmlObjects.MoviMot(unitNumber,self.xml.ObjectList,zone,self.scl,self.blockGroupSw)
            
        else:
            raise NameError("A Device Already Has That Name")
            
    def addFortressGate(self,unitNumber,ip,zone=""):
        if unitNumber not in self.data.keys():
            gate = OpennessTest.createFortressGate(self.project,self.tags,unitNumber,ip,self.subnet,zone)
            xmlObjects.FortressGate(unitNumber,gate.Failsafe_FIODBName,self.xml.ObjectList,zone,self.scl,self.blockGroupSw)
            
        else:
            raise NameError("A Device Already Has That Name")
            
    def spawnTest(self):
        self.addAbbAcs380Drive("U000000","172.16.210.66")
        self.addScannerSickCLV6xx("U000010","172.16.210.67")
        self.addPnpn("U000020","172.16.210.68")
        self.addConnectionBox("U000030","172.16.210.69")
        self.addHmi("U000040","172.16.210.70")
        self.addMoviMot("U000050","172.16.210.71")
        self.addFortressGate("U000060","172.16.210.72")
            
class controlAreaObject(father):
    def __init__(self,name,parent):
        super().__init__(name,parent)
        self.networkDevices = {}
        self.controlAreaData = {}
        self.project = parent.project
        self.software = parent.blockGroupSw
        self.subnet = parent.subnet
        self.contolCabnet = parent.name
        self.xml = parent.xml
        self.scl = parent.scl
                
    def adoptNetworkDevice(self,objectName):
        if objectName not in self.networkDevices.keys() and objectName in self.parent.networkDevices.keys():
            self.networkDevices[objectName[-1]] = self.parent.networkDevices[objectName]
            
            return object
        else:
            raise KeyError
        
    def addEzc(self,name):
        if name not in self.data.keys():
            object = ezcObject(name,self)
            self.data[name] = object
            self.controlAreaData[name] = object
            xmlObjects.EzcBox(self.contolCabnet,self.name,name,[],[],self.xml.ObjectList,self.scl,self.software)
            return object
        else:
            raise KeyError
        
class ezcObject(father):
    def __init__(self,name,parent):
        super().__init__(name,parent)
        self.project = parent.project
        self.software = parent.software
        self.networkDevices = parent.networkDevices
        self.contolCabnet = parent.contolCabnet
        self.xml = parent.xml
        self.scl = parent.scl
        self.controlAreaData = parent.controlAreaData
        self.controlArea = parent.name
        
    def addAsiEstop(self,name,asiAddress):
        import re
        if name not in self.data.keys():
            if re.search("^ASI_[A-Z][1-2]_([0-9]|[0-2][0-9]|3[01])$",asiAddress) != None:
                    object = asiEstopObject(name,asiAddress,self)
                    self.data[name] = object
                    self.controlAreaData[name] = object
                    return object
            else:
                raise ValueError("Malformed ASI Address")
        else:
            raise KeyError
        
class asiEstopObject(father):
    def __init__(self,name,asiAddress,parent):
        super().__init__(name,parent)
        self.project = parent.project
        self.software = parent.software
        self.networkDevices = parent.networkDevices
        self.controlArea = parent.controlArea
        self.contolCabnet = parent.contolCabnet
        self.contolCabnet = parent.contolCabnet
        self.xml = parent.xml
        self.scl = parent.scl
        self.asiAddress = asiAddress
        self.ezcName = parent.name
        self.createAsiTags(asiAddress)
        self.export()
        
    def createAsiTags(self,asiAddress):
        networkName = asiAddress.split("_")[1][:1]
        if networkName in self.networkDevices:
            self.pnag = self.networkDevices[networkName]
            self.pnag.addHalfNodeASI(self.name + "_NONSAFE",self.asiAddress + "A_I1")
            self.pnag.addHalfNodeASI(self.name + "_LT_R",self.asiAddress + "A_O1")
            self.pnag.addHalfNodeASI(self.name + "_LT_G",self.asiAddress + "A_O2")
            
        else:
            raise KeyError("ASI Network Not Found In This Area")
    
    def export(self):
        xmlObjects.EStopVis(self.controlArea,self.pnag.Device.Name,self.ezcName,self.name,self.xml.ObjectList,self.scl,self.software)
        


CC = controlCabnetObject("CC120")
CC.createControlArea("CA121")
CC.createControlArea("CA122")

CC["CA121"].adoptNetworkDevice("U251910_PNAG_C")
CC["CA121"].adoptNetworkDevice("U252310_PNAG_B")
CC["CA121"].adoptNetworkDevice("U253110_PNAG_A")

CC["CA121"].addEzc("CA121EZC1")
CC["CA121"].addEzc("CA121EZC2")
CC["CA121"].addEzc("CA121EZC3")
CC["CA121"].addEzc("CA121EZC4")

CC["CA121"]['CA121EZC1'].addAsiEstop("EStop1","ASI_C1_28")
CC["CA121"]['CA121EZC1'].addAsiEstop("EStop2","ASI_A1_05")
CC["CA121"]['CA121EZC1'].addAsiEstop("EStop3","ASI_A1_28")



CC.save()


print(CC["CA121"]['CA121EZC3'])
