import clr
clr.AddReference('C:\\Program Files\\Siemens\\Automation\\Portal V17\PublicAPI\\V17\\Siemens.Engineering.dll')
import Siemens.Engineering
import System
import os

import OpennessTest
import xmlHeader
import sclObject
import xmlObjects
import globalDB
import swBlock

class father():
    def __init__(self,name,parent=None):
        super(father,self).__init__()
        self.name = name
        self.data = {}
        self.dataSorted = {}
        if parent != None:
            self.parent = parent
            self.data = parent.data
            self.dataSorted = parent.dataSorted
        
    def __str__(self):
        return str(self.data.keys())
        
    def __getitem__(self, name):
        return self.data[name]
            
    def keys(self):
        return vars(self).keys()
        
    def __del__(self):
        pass
        #print("Destructor called, {0} deleted.".format(self.name))

class controlCabnetObject(father):
    def __init__(self, name):
        super(controlCabnetObject,self).__init__(name)
        self.networkDevices = {}
        self.dataSorted = {
                            "controlAreaObject":[],
                            "ezcObject":[],
                            "asiEstopObject":[],
                            "auxBoxObject":[],
                            "dpsBoxObject":[],
                            "Pnag":[],
                            "Pncg":[],
                            "rptrObject":[],
                            "AbbAcs380DriveObject":[],
                            "FortressGateobject":[]
                            }
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
                    self.networkDevices[x.Name] = x
                    
                elif "DEMATIC-PNCG" in x.TypeIdentifier:
                    self.networkDevices[x.Name] = x
                    
                    
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
        self.DefaultDBsSw = self.software.BlockGroup.Groups.Find("Project").Groups.Find("DefaultDBs")

        self.DataFromSafety = self.DefaultDBsSw.Blocks.Find("DataFromSafety")
        if self.DataFromSafety != None:
            self.DataFromSafety.Delete()
        self.DataFromSafety = globalDB.globalDB("DataFromSafety",self.DefaultDBsSw)
        self.DataFromSafety.addMember("SafetyStatusToPLC",'"typeSafetyStatusToMainPanel"')
            
        self.DataToSafety = self.DefaultDBsSw .Blocks.Find("DataToSafety")
        if self.DataToSafety != None:
            self.DataToSafety.Delete()
        self.DataToSafety = globalDB.globalDB("DataToSafety",self.DefaultDBsSw)
        self.DataToSafety.addMember("PLCToSafety",'"typeZoneToAreaControl"')
        
        self.dbPncgParameterData = self.DefaultDBsSw .Blocks.Find("dbPncgParameterData")
        if self.dbPncgParameterData != None:
            self.dbPncgParameterData.Delete()
        self.dbPncgParameterData = globalDB.globalDB("dbPncgParameterData",self.DefaultDBsSw)
        
    def save(self):
        xmlObjects.Plc(self.name,self.dataSorted.keys(),self.xml.ObjectList,self.scl,self.blockGroupSw)
        for x in self.dataSorted.keys():
            for y in self.dataSorted[x]:
                y.export()
        xmlObjects.CallSetConfig(self.scl.Name,self.xml.ObjectList)
        self.xml.save()
        self.blockGroupSw.Blocks.Import(System.IO.FileInfo("{0}/{1}.xml".format(os.getcwd(),self.xml.Name)),Siemens.Engineering.ImportOptions.Override)
        
        self.scl.save()
        self.blockGroupSw.Blocks.Import(System.IO.FileInfo("{0}/{1}.xml".format(os.getcwd(),self.scl.Name)),Siemens.Engineering.ImportOptions.Override)
        
        self._genDefaultDBs()
        
        self.DataToSafety.save()
        self.DataFromSafety.save()        
        self.dbPncgParameterData.save()
        
        ICompilable = Siemens.Engineering.IEngineeringServiceProvider(self.software.BlockGroup.Groups.Find("Project").Groups.Find("DefaultDBs")).GetService[Siemens.Engineering.Compiler.ICompilable]()
        ICompilable.Compile()
        
    def _genDefaultDBs(self):
        for x in self.dataSorted["controlAreaObject"]:
            if len(x.controlAreaDataSorted["EZCs"]) > 0 :
                self.DataToSafety.addMember(x.name + "EZCxPowerGroupToSafetyStatus",'Array[1..{0}] of "typePowerGroupStatusToSafety"'.format(len(x.controlAreaDataSorted["EZCs"])))
                self.DataFromSafety.addMember(x.name + "EZCxSafetyStatusToPowerGroup",'Array[1..{0}] of "typeSafetyStatusToPowerGroup"'.format(len(x.controlAreaDataSorted["EZCs"])))
            if len(x.controlAreaDataSorted["Estops"]) > 0 :
                self.DataFromSafety.addMember(x.name + "EStopHealthy","Array[1..{0}] of Bool".format(len(x.controlAreaDataSorted["Estops"])))
                

        for x in self.dataSorted["Pncg"]:
            self.dbPncgParameterData.addMember(x.Device.Name,'"typeNodeParameters"')
        
    def createControlArea(self,name):
        if name not in self.data.keys():
            object = controlAreaObject(name,self)
            self.data[name] = object
            self.dataSorted["controlAreaObject"].append(object)
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
            #OpennessTest.createAbbAcs380Drive(self.project,self.tags,unitNumber,ip,self.subnet,zone)
            #xmlObjects.AbbAcs380Drive(unitNumber,self.xml.ObjectList,zone,self.scl,self.blockGroupSw)
            name = unitNumber + zone + "_FMD"
            object = AbbAcs380DriveObject(unitNumber,name,self,ip,zone)
            self.data[name] = object
            self.dataSorted["AbbAcs380DriveObject"].append(object)
            
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
            #gate = OpennessTest.createFortressGate(self.project,self.tags,unitNumber,ip,self.subnet,zone)
            #xmlObjects.FortressGate(unitNumber,gate.Failsafe_FIODBName,self.xml.ObjectList,zone,self.scl,self.blockGroupSw)
            name = unitNumber + zone + "_GS"
            object = FortressGateobject(unitNumber,name,self,ip,zone)
            self.data[name] = object
            self.dataSorted["FortressGateobject"].append(object)
            
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
        super(controlAreaObject,self).__init__(name,parent)
        self.networkDevices = {}
        self.controlAreaData = {}
        self.controlAreaDataSorted =    {
                                        "EZCs":[],
                                        "Estops":[],
                                        "DpsBoxs":[],
                                        "AuxBoxs":[],
                                        "Pnag":[],
                                        "Pncg":[],
                                        "RPTRs":[]
                                        }
        self.project = parent.project
        self.software = parent.blockGroupSw
        self.subnet = parent.subnet
        self.contolCabnet = parent.name
        self.xml = parent.xml
        self.scl = parent.scl
        self.tags = parent.tags
                
    def adoptNetworkDevice(self,objectName):
        if objectName not in self.networkDevices.keys() and objectName in self.parent.networkDevices.keys():
            Device = self.parent.networkDevices[objectName]
            if "BIHL UND WIEDEMANN-ASI GATEWAY" in Device.TypeIdentifier:
                object = Pnag(Device,self)
                self.dataSorted["Pnag"].append(object)
                self.controlAreaDataSorted["Pnag"].append(object)
                    
            elif "DEMATIC-PNCG" in Device.TypeIdentifier:
                object = Pncg(Device,self)
                self.dataSorted["Pncg"].append(object)
                self.controlAreaDataSorted["Pncg"].append(object)
            
            self.networkDevices[objectName[-1]] = object
            self.data[object.name] = object
            
            self.controlAreaData[object.name] = object
            
            
            return object
        else:
            raise KeyError
        
    def addEzc(self,asiAddress):
        import re
        name = "{0}EZC{1}".format(self.name,str(len(self.controlAreaDataSorted["EZCs"]) + 1))
        if re.search("^ASI_[A-Z][1-2]_([0-9]|[0-2][0-9]|3[01])[A-B]$",asiAddress) != None:
            if name not in self.data.keys():
                object = ezcObject(name,self,asiAddress)
                self.data[name] = object
                self.dataSorted["ezcObject"].append(object)
                self.controlAreaData[name] = object
                self.controlAreaDataSorted["EZCs"].append(object)
                return object
            else:
                raise KeyError
        else:
            raise ValueError("Malformed ASI Address")
        
    def addRptrBox(self,asiNetwork):
        import re
        if re.search("^ASI_[A-Z][1-2]$",asiNetwork) != None:
            name = "{0}RPTR{1}".format(self.name,re.findall("_[A-Z][0-9]{1,3}$",asiNetwork)[0])
            if name not in self.data.keys():
                object = rptrObject(name,self,asiNetwork)
                self.data[name] = object
                self.dataSorted["rptrObject"].append(object)
                self.controlAreaData[name] = object
                self.controlAreaDataSorted["RPTRs"].append(object)
                return object
            else:
                raise KeyError
        else:
            raise ValueError("Malformed ASI Address")
        
    def export(self):
        pass
        
class Pnag(OpennessTest.GsdDevice):
    def __init__(self,Device,parent):
        super().__init__(Device)
        self.tags = parent.tags
        self.contolCabnet = parent.contolCabnet
        self.name = self.Device.Name
        self.xml = parent.xml
        self.scl = parent.scl
        self.software = parent.software
        
        self.tags = parent.tags
        self.Circuit1AInAddress = self.Objects["C1: 16 Bytes DIO (0-31)"]["C1: 16 Bytes DIO (0-31)"]["Object"].Addresses[0].StartAddress
        self.Circuit1AOutAddress = self.Objects["C1: 16 Bytes DIO (0-31)"]["C1: 16 Bytes DIO (0-31)"]["Object"].Addresses[1].StartAddress
        self.Circuit1BInAddress = self.Objects["C1: 16 Bytes DIO (0B-31B)"]["C1: 16 Bytes DIO (0-31)"]["Object"].Addresses[0].StartAddress
        self.Circuit1BOutAddress = self.Objects["C1: 16 Bytes DIO (0B-31B)"]["C1: 16 Bytes DIO (0-31)"]["Object"].Addresses[1].StartAddress
        self.Circuit1Flags = self.Objects["C1: Flags + Fault Det."]["C1: Flags + Fault Det."]["Object"].Addresses[0].StartAddress
                
        self.Circuit2AInAddress = self.Objects["C2: 16 Bytes DIO (0-31)"]["C2: 16 Bytes DIO (0-31)"]["Object"].Addresses[0].StartAddress
        self.Circuit2AOutAddress = self.Objects["C2: 16 Bytes DIO (0-31)"]["C2: 16 Bytes DIO (0-31)"]["Object"].Addresses[1].StartAddress
        self.Circuit2BInAddress = self.Objects["C2: 16 Bytes DIO (0B-31B)"]["C2: 16 Bytes DIO (0-31)"]["Object"].Addresses[0].StartAddress
        self.Circuit2BOutAddress = self.Objects["C2: 16 Bytes DIO (0B-31B)"]["C2: 16 Bytes DIO (0-31)"]["Object"].Addresses[1].StartAddress
        self.Circuit2Flags = self.Objects["C2: Flags + Fault Det."]["C2: Flags + Fault Det."]["Object"].Addresses[0].StartAddress
        
        self.FieldBusBitsAddress = self.Objects["2 Byte Fieldbus Bits"]["2 Byte Fieldbus Bits"]["Object"].Addresses[1].StartAddress
        
        self.CommandIfIn = self.Objects["34 Bytes Command If"]["34 Bytes Command If"]["Object"].Addresses[0].StartAddress
        self.CommandIfOut = self.Objects["34 Bytes Command If"]["34 Bytes Command If"]["Object"].Addresses[1].StartAddress
        self.createTags()
        
    def createTags(self):
        if self.Circuit1AInAddress != -1 and self.Circuit1AOutAddress != -1 and self.Circuit1BInAddress != -1 and self.Circuit1BInAddress != -1:
            self.tags.addTag(self.Device.Name+"1_A_In","In","{0}.0".format(self.Circuit1AInAddress),"typeAsiAIn","{0} Circuit 1A Inputs".format(self.Device.Name),self.Device.Name,True)
            self.tags.addTag(self.Device.Name+"1_A_Out","Out","{0}.0".format(self.Circuit1AOutAddress),"typeAsiAOut","{0} Circuit 1A Outputs".format(self.Device.Name),self.Device.Name,True)
            self.tags.addTag(self.Device.Name+"1_B_In","In","{0}.0".format(self.Circuit1BInAddress),"typeAsiBIn","{0} Circuit 1B Inputs".format(self.Device.Name),self.Device.Name,True)
            self.tags.addTag(self.Device.Name+"1_B_Out","Out","{0}.0".format(self.Circuit1BOutAddress),"typeAsiBOut","{0} Circuit 1B Outputs".format(self.Device.Name),self.Device.Name,True)
            
        if self.Circuit2AInAddress != -1 and self.Circuit2AOutAddress != -1 and self.Circuit2BInAddress != -1 and self.Circuit2BOutAddress != -1:
            self.tags.addTag(self.Device.Name+"2_A_In","In","{0}.0".format(self.Circuit2AInAddress),"typeAsiAIn","{0} Circuit 2A Inputs".format(self.Device.Name),self.Device.Name,True)
            self.tags.addTag(self.Device.Name+"2_A_Out","Out","{0}.0".format(self.Circuit2AOutAddress),"typeAsiAOut","{0} Circuit 2A Outputs".format(self.Device.Name),self.Device.Name,True)
            self.tags.addTag(self.Device.Name+"2_B_In","In","{0}.0".format(self.Circuit2BInAddress),"typeAsiBIn","{0} Circuit 2B Inputs".format(self.Device.Name),self.Device.Name,True)
            self.tags.addTag(self.Device.Name+"2_B_Out","Out","{0}.0".format(self.Circuit2BOutAddress),"typeAsiBOut","{0} Circuit 2B Outputs".format(self.Device.Name),self.Device.Name,True)
            
        if self.FieldBusBitsAddress != -1:
            self.tags.addTag(self.Device.Name+"GlobalFaultReset","Out","{0}.4".format(self.FieldBusBitsAddress),"Bool","{0} ASi Gateway Global Fault Reset".format(self.Device.Name),self.Device.Name,True)
            
    def addHalfNodeASI(self,tagName,address):
        import re
        if re.search("^ASI_[A-Z][1-2]_([0-9]|[0-2][0-9]|3[01])[A-B]_(I|O)[1-4]$",address) != None:
            split = address.split("_")
            circuit = split[1][-1:]
            node = split[2][:-1]
            AorB = split[2][-1:]
            bitOffSet = split[3][-1:]
            InOrOut = split[3][:-1]
            if InOrOut == "I":
                InOrOut = "In"
            if InOrOut == "O":
                InOrOut = "Out"
            
            self._addHalfNode(tagName,circuit,node,AorB,bitOffSet,InOrOut)
        else:
            raise ValueError("Malformed ASI Address")
            
    def _addHalfNode(self,name,circuit,node,AorB,bitOffSet,InOrOut):
        """
        Circuit is 1 or 2
        Node is Node
        AorB is A or B
        bitOffSet is 1-4
        
        This function will add a tag given the node address
        (name,logicalAddress,dataType,comment,tagTable):
        """
        if self.Circuit1AInAddress != 1 and self.Circuit1AOutAddress != 1 and self.Circuit1BInAddress != 1 and self.Circuit1BInAddress != 1 and self.Circuit2AInAddress != 1 and self.Circuit2AOutAddress != 1 and self.Circuit2BInAddress != 1 and self.Circuit2BOutAddress != 1:
            try:
                memorybitOffSet = bitOffSet - 1
            except:
                memorybitOffSet = int(bitOffSet) - 1
            try:
                node = int(node)
            except:
                pass
            if node%2 == 0:
                memorybitOffSet = memorybitOffSet + 4
                
            if circuit == "1" and AorB == "A" and InOrOut == "In":
                moduleAddress = self.Circuit1AInAddress
            elif circuit == "1" and AorB == "A" and InOrOut == "Out":
                moduleAddress = self.Circuit1AOutAddress
            elif circuit == "1" and AorB == "B" and InOrOut == "In":
                moduleAddress = self.Circuit1BInAddress
            elif circuit == "1" and AorB == "B" and InOrOut == "Out":
                moduleAddress = self.Circuit1BOutAddress
            elif circuit == "2" and AorB == "A" and InOrOut == "In":
                moduleAddress = self.Circuit2AInAddress
            elif circuit == "2" and AorB == "A" and InOrOut == "Out":
                moduleAddress = self.Circuit2AOutAddress
            elif circuit == "2" and AorB == "B" and InOrOut == "In":
                moduleAddress = self.Circuit2BInAddress
            elif circuit == "2" and AorB == "B" and InOrOut == "Out":
                moduleAddress = self.Circuit2BOutAddress
                
            comment = "ASI_{0}{1}_{2}{3}_{4}{5}".format(self.Device.Name[-1:],circuit, str(node).zfill(2), AorB, InOrOut[:1],bitOffSet)
            if node%2 == 1:
                memoryLocation = str(moduleAddress + int((node-1)/2))
            elif node%2 == 0:
                memoryLocation = str(moduleAddress + int(node/2))
            logicalAddress = "{memoryLocation}.{memorybitOffSet}".format(memoryLocation=memoryLocation,memorybitOffSet=memorybitOffSet)
            
            self.tags.addTag(name,InOrOut,logicalAddress,"Bool",comment,"AS-i I/O")
            
    def export(self):
        xmlObjects.PnagBox(self.contolCabnet,self.name,self.xml.ObjectList,self.scl,self.software)
        
class Pncg(OpennessTest.GsdDevice):
    def __init__(self,Device,parent):
        super().__init__(Device)
        self.tags = parent.tags
        self.contolCabnet = parent.contolCabnet
        self.name = self.Device.Name
        self.xml = parent.xml
        self.scl = parent.scl
        self.software = parent.software
        self.createTags()
        
    def createTags(self):
        self.CANChannelIn = self.Objects["CAN Channel Module_1"]["CAN Channel Submodule"]["Object"].Addresses[0].StartAddress
        self.CANChannelOut = self.Objects["CAN Channel Module_1"]["CAN Channel Submodule"]["Object"].Addresses[1].StartAddress
        self.tags.addTag(self.Device.Name+"CANChannelIn","In","{0}.0".format(self.CANChannelIn),"Bool","{0} PNCG CAN Channel Input".format(self.Device.Name),self.Device.Name,True)
        self.tags.addTag(self.Device.Name+"CANChannelOut","Out","{0}.0".format(self.CANChannelOut),"Bool","{0} PNCG CAN Channel Output".format(self.Device.Name),self.Device.Name,True)
        for x in range(1,7):
            if "Command Module_{0}".format(x) not in self.Objects:
                newSlot = self.addModule("GSD:GSDML-V2.33-DEMATIC-PNCG-20171211.XML/M/Command","Command Module_{0}".format(str(x)))
                inAddress = newSlot.DeviceItems[0].Addresses[0].StartAddress
                outAddress = newSlot.DeviceItems[0].Addresses[1].StartAddress
                self.tags.addTag("{0}CmdArea{1}In".format(self.Device.Name,str(x)),"In","{0}.0".format(inAddress),"typeCommandAreaInput","{0} PNCG Command Area {1} Input".format(self.Device.Name,str(x)),self.Device.Name,True)
                self.tags.addTag("{0}CmdArea{1}Out".format(self.Device.Name,str(x)),"Out","{0}.0".format(outAddress),"typeCommandAreaOutput","{0} PNCG Command Area {1} Output".format(self.Device.Name,str(x)),self.Device.Name,True)
        
    def export(self):
        xmlObjects.PncgBox(self.contolCabnet,self.name,self.xml.ObjectList,self.scl,self.software)
        
class ezcObject(father):
    def __init__(self,name,parent,asiAddress):
        super().__init__(name,parent)
        self.ezcData = {}
        self.ezcDataSorted =    {
                                "DpsBoxs":[],
                                "AuxBoxs":[],
                                "Estops":[],
                                }
        self.project = parent.project
        self.software = parent.software
        self.networkDevices = parent.networkDevices
        self.networkName = asiAddress.split("_")[1][:1]
        self.pnagName =  self.networkDevices[self.networkName].Device.Name
        self.contolCabnet = parent.contolCabnet
        self.xml = parent.xml
        self.scl = parent.scl
        self.controlAreaData = parent.controlAreaData
        self.controlAreaDataSorted = parent.controlAreaDataSorted
        self.controlArea = parent.name
        self.asiAddress = asiAddress
        self.createAsiTags()
        
    def addAsiEstop(self,name,asiAddress):
        import re
        if name not in self.data.keys():
            #Expecting Saftey Address ASI_B2_28
            if re.search("^ASI_[A-Z][1-2]_([0-9]|[0-2][0-9]|3[0-1])$",asiAddress) != None:
                    object = asiEstopObject(name,asiAddress,self)
                    self.data[name] = object
                    self.dataSorted["asiEstopObject"].append(object)
                    self.controlAreaData[name] = object
                    self.controlAreaDataSorted["Estops"].append(object)
                    self.ezcData[name] = object
                    self.ezcDataSorted["Estops"].append(object)
                    return object
            else:
                raise ValueError("Malformed ASI Address")
        else:
            raise KeyError
            
    def addAuxBox(self,asiAddress):
        import re
        name = "{0}AUX{1}".format(self.controlArea,str(len(self.controlAreaDataSorted["AuxBoxs"]) + 1))
        if name not in self.data.keys():
            #Expecting Normal Half Nodes ASI_B2_01A or B
            if re.search("^ASI_[A-Z][1-2]_([0-9]|[0-2][0-9]|3[01])[A-B]_I[1-4]$",asiAddress) != None:
                    object = auxBoxObject(name,asiAddress,self)
                    self.data[name] = object
                    self.dataSorted["auxBoxObject"].append(object)
                    self.controlAreaData[name] = object
                    self.controlAreaDataSorted["AuxBoxs"].append(object)
                    self.ezcData[name] = object
                    self.ezcDataSorted["AuxBoxs"].append(object)
                    return object
            else:
                raise ValueError("Malformed ASI Address")
        else:
            raise KeyError
        
    def addDpsBox(self,asiAddress):
        import re
        name = "{0}DPS{1}".format(self.controlArea,str(len(self.controlAreaDataSorted["DpsBoxs"]) + 1))
        if name not in self.data.keys():
            #Expecting Normal Half Nodes ASI_B2_01A or B
            if re.search("^ASI_[A-Z][1-2]_([0-9]|[0-2][0-9]|3[01])[A-B]_I[1-4]$",asiAddress) != None:
                    object = dpsBoxObject(name,asiAddress,self)
                    self.data[name] = object
                    self.dataSorted["dpsBoxObject"].append(object)
                    self.controlAreaData[name] = object
                    self.controlAreaDataSorted["DpsBoxs"].append(object)
                    self.ezcData[name] = object
                    self.ezcDataSorted["DpsBoxs"].append(object)
                    return object
            else:
                raise ValueError("Malformed ASI Address")
        else:
            raise KeyError
        
    def createAsiTags(self):
        if self.networkName in self.networkDevices:
            self.pnag = self.networkDevices[self.networkName]
            self.pnag.addHalfNodeASI(self.name + "_CR_ESM",self.asiAddress + "_I3")
        else:
            raise KeyError("ASI Network Not Found In This Area")
        
    def export(self):
        dpsNames = []
        auxNames = []
        for x in self.ezcDataSorted["DpsBoxs"]:
            dpsNames.append(x.name)
        for x in self.ezcDataSorted["AuxBoxs"]:
            auxNames.append(x.name)
        xmlObjects.EzcBox(self.contolCabnet,self.controlArea,self.name,self.pnagName,dpsNames,auxNames,self.xml.ObjectList,self.scl,self.software)
        
class rptrObject(father):
    def __init__(self,name,parent,asiNetwork):
        super(rptrObject,self).__init__(name,parent)
        self.project = parent.project
        self.software = parent.software
        self.xml = parent.xml
        self.scl = parent.scl
        self.controlArea = parent.name
        self.contolCabnet = parent.contolCabnet
        self.networkDevices = parent.networkDevices
        self.networkName = asiNetwork.split("_")[1][:1]
        self.pnagName =  self.networkDevices[self.networkName].Device.Name
        
    def export(self):
        xmlObjects.RptrBox(self.name,self.pnagName,self.xml.ObjectList,self.scl,self.software)
        
class auxBoxObject(father):
    def __init__(self,name,asiAddress,parent):
        super(auxBoxObject,self).__init__(name,parent)
        self.project = parent.project
        self.software = parent.software
        self.networkDevices = parent.networkDevices
        self.controlArea = parent.controlArea
        self.contolCabnet = parent.contolCabnet
        self.xml = parent.xml
        self.scl = parent.scl
        self.asiAddress = asiAddress
        self.ezcName = parent.name
        self.networkName = asiAddress.split("_")[1][:1]
        self.pnagName =  self.networkDevices[self.networkName].Device.Name
        self.controlAreaDataSorted = parent.controlAreaDataSorted
        self.createAsiTags(asiAddress)
        
    def createAsiTags(self,asiAddress):
        if self.networkName in self.networkDevices:
            self.pnag = self.networkDevices[self.networkName]
            self.pnag.addHalfNodeASI(self.name + "_CR_ESM",self.asiAddress)
        else:
            raise KeyError("ASI Network Not Found In This Area")
    
    def export(self):
        xmlObjects.AuxBox(self.contolCabnet,self.controlArea,self.ezcName,self.name,self.pnagName,self.xml.ObjectList,self.scl,self.software)
        
class asiEstopObject(father):
    def __init__(self,name,asiAddress,parent):
        super(asiEstopObject,self).__init__(name,parent)
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
        self.controlAreaDataSorted = parent.controlAreaDataSorted
        self.createAsiTags(asiAddress)
        
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
        
class dpsBoxObject(father):
    def __init__(self,name,asiAddress,parent):
        super(dpsBoxObject,self).__init__(name,parent)
        self.project = parent.project
        self.software = parent.software
        self.networkDevices = parent.networkDevices
        self.controlArea = parent.controlArea
        self.contolCabnet = parent.contolCabnet
        self.xml = parent.xml
        self.scl = parent.scl
        self.asiAddress = asiAddress
        self.ezcName = parent.name
        self.networkName = asiAddress.split("_")[1][:1]
        self.pnagName =  self.networkDevices[self.networkName].Device.Name
        self.controlAreaDataSorted = parent.controlAreaDataSorted
        self.createAsiTags(asiAddress)
        
    def createAsiTags(self,asiAddress):
        if self.networkName in self.networkDevices:
            self.pnag = self.networkDevices[self.networkName]
            self.pnag.addHalfNodeASI(self.name + "_CR_ESM",self.asiAddress)
        else:
            raise KeyError("ASI Network Not Found In This Area")
    
    def export(self):
        xmlObjects.DpsBox(self.contolCabnet,self.controlArea,self.ezcName,self.name,self.pnagName,self.xml.ObjectList,self.scl,self.software)
        
class AbbAcs380DriveObject(father):
    def __init__(self,unitNumber,name,parent,ip,zone=""):
        super(AbbAcs380DriveObject,self).__init__(name,parent)
        self.project = parent.project
        self.software = parent.blockGroupSw
        self.xml = parent.xml
        self.scl = parent.scl
        self.tags = parent.tags
        self.subnet = parent.subnet
        self.name = name
        self.unitNumber = unitNumber
        self.ip = ip
        self.zone = zone
        self.hardwareSetup()
        
    def hardwareSetup(self):
        typeIdentifier = "GSD:GSDML-V2.33-ABB-FPNO-20180516.XML"
        Object = OpennessTest.ungroupedDevice(self.project,typeIdentifier + "/DAP",self.name)
        PPO4 = Object.addModule(typeIdentifier + "/M/ID_MODULE_PPO4","PPO Type 4_1",1)
        Object.getNetworkInterface(Object.Objects[self.name]["Interface"]["Object"])
        Object.setIp(self.ip,self.subnet)
        inStart = Object.Objects["PPO Type 4_1"]["PPO4 Data Object"]["Object"].Addresses[0].StartAddress
        outStart = Object.Objects["PPO Type 4_1"]["PPO4 Data Object"]["Object"].Addresses[1].StartAddress
        self.tags.addTag(self.name+"_In","In","{0}.0".format(inStart),"typeABBACS380InputsPP04","PP04 Inputs For Drive Flags","FMD PPO Tags")
        self.tags.addTag(self.name+"_Out","Out","{0}.0".format(outStart),"typeABBACS380OutputsPP04","PP04 Outputs For Drive Control","FMD PPO Tags")
        
    def export(self):
        xmlObjects.AbbAcs380Drive(self.unitNumber,self.xml.ObjectList,self.zone,self.scl,self.software)
        
class FortressGateobject(father):
    def __init__(self,unitNumber,name,parent,ip,zone=""):
        super(FortressGateobject,self).__init__(name,parent)
        self.project = parent.project
        self.software = parent.blockGroupSw
        self.xml = parent.xml
        self.scl = parent.scl
        self.tags = parent.tags
        self.subnet = parent.subnet
        self.name = name
        self.unitNumber = unitNumber
        self.ip = ip
        self.zone = zone
        
        self.hardwareSetup()
        
    def hardwareSetup(self):
        typeIdentifier = "GSD:GSDML-V2.35-FORTRESS-PROLOK-20190704.XML"
        self.Object = OpennessTest.ungroupedDevice(self.project,typeIdentifier + "/DAP",self.name)
        safetyModule = self.Object.addModule(typeIdentifier + "/M/ID_MODULE_F_IO_3DIN1DOUT","Safety Module_1",1)
        io = self.Object.addModule(typeIdentifier + "/M/ID_MODULE_IO","Unsafe IO Data_1",2)
        self.Object.getNetworkInterface(self.Object.Objects[self.name]["Interface"]["Object"])
        self.Object.setIp(self.ip,self.subnet)
        safetyModuleIn = self.Object.Objects["Safety Module_1"]["Safety Module"]["Object"].Addresses[0].StartAddress
        if safetyModuleIn != -1:
            self.tags.addTag(self.name+"_Sol_1","In","{0}.0".format(safetyModuleIn),"Bool","","E Stop Devices")
            self.tags.addTag(self.name+"_Sol_2","In","{0}.1".format(safetyModuleIn),"Bool","","E Stop Devices")
            self.tags.addTag(self.name+"_Estop_1","In","{0}.4".format(safetyModuleIn),"Bool","","E Stop Devices")
            self.tags.addTag(self.name+"_Estop_2","In","{0}.5".format(safetyModuleIn),"Bool","","E Stop Devices")
            
        lampsOut = self.Object.Objects["Unsafe IO Data_1"]["IO Lamps"]["Object"].Addresses[0].StartAddress
        if lampsOut != -1:
            self.tags.addTag(self.name+"_ST_LT","Out","{0}.0".format(lampsOut),"Bool","","E Stop Devices")
            self.tags.addTag(self.name+"_G_LT","Out","{0}.1".format(lampsOut),"Bool","","E Stop Devices")
            self.tags.addTag(self.name+"_ES_LT","Out","{0}.3".format(lampsOut),"Bool","","E Stop Devices")
            self.tags.addTag(self.name+"_RQ_LT","Out","{0}.4".format(lampsOut),"Bool","","E Stop Devices")
            self.tags.addTag(self.name+"_RS_LT","Out","{0}.5".format(lampsOut),"Bool","","E Stop Devices")
            
        switchesIn = self.Object.Objects["Unsafe IO Data_1"]["IO Switches"]["Object"].Addresses[0].StartAddress
        if switchesIn != -1:
            self.tags.addTag(self.name+"_ST_PVB","In","{0}.0".format(switchesIn),"Bool","","E Stop Devices")
            self.tags.addTag(self.name+"_G_SW","In","{0}.1".format(switchesIn),"Bool","","E Stop Devices")
            self.tags.addTag(self.name+"_RQ_PB","In","{0}.4".format(switchesIn),"Bool","","E Stop Devices")
            self.tags.addTag(self.name+"_RS_PB","In","{0}.5".format(switchesIn),"Bool","","E Stop Devices")
            
        solenoidOut = self.Object.Objects["Unsafe IO Data_1"]["Solenoid Drive"]["Object"].Addresses[0].StartAddress
        if solenoidOut != -1:
            self.tags.addTag(self.name+"_Sol_Drive","Out","{0}.0".format(solenoidOut),"Bool","","E Stop Devices")
            
        gateIn = self.Object.Objects["Unsafe IO Data_1"]["Gate Monitor"]["Object"].Addresses[0].StartAddress
        if gateIn != -1:
            self.tags.addTag(self.name+"_GateMon","In","{0}.0".format(gateIn),"Bool","","E Stop Devices")
            
        solenoidIn = self.Object.Objects["Unsafe IO Data_1"]["Solenoid Monitor"]["Object"].Addresses[0].StartAddress
        if solenoidIn != -1:
            self.tags.addTag(self.name+"_SolMon","In","{0}.0".format(solenoidIn),"Bool","","E Stop Devices")
        self.Failsafe_FIODBName = self.Object.Objects["Safety Module_1"]["Safety Module"]["Object"].GetAttribute("Failsafe_FIODBName")
        
    def export(self):
        xmlObjects.FortressGate(self.unitNumber,self.Failsafe_FIODBName,self.xml.ObjectList,self.zone,self.scl,self.software)

CC = controlCabnetObject("CC110")
CC.createControlArea("CA121")

CC["CA121"].adoptNetworkDevice("U251910_PNAG_C")
CC["CA121"].adoptNetworkDevice("U252310_PNAG_B")
CC["CA121"].adoptNetworkDevice("U253110_PNAG_A")

CC["CA121"].adoptNetworkDevice("U251845_ECG_03")
CC["CA121"].adoptNetworkDevice("U252245_ECG_02")
CC["CA121"].adoptNetworkDevice("U253045_ECG_01")

CA111EZC1 = CC["CA121"].addEzc("ASI_B2_01A")
CA111EZC2 = CC["CA121"].addEzc("ASI_A2_01A")
CA111EZC3 = CC["CA121"].addEzc("ASI_C2_01A")
CA111EZC4 = CC["CA121"].addEzc("ASI_A2_02A")

#CA111EZC1.addAsiEstop("EStop1","ASI_C1_28")
#CA111EZC1.addAsiEstop("EStop2","ASI_A1_05")
#CA111EZC1.addAsiEstop("EStop3","ASI_A1_28")
CA111EZC1.addAuxBox("ASI_C1_15A_I3")
CA111EZC1.addDpsBox("ASI_C1_15A_I2")

CC["CA121"].addRptrBox("ASI_C1")

CA111EZC2.addAuxBox("ASI_C1_16A_I3")
CA111EZC2.addDpsBox("ASI_C1_16A_I2")

CA111EZC3.addAuxBox("ASI_C1_17A_I3")
CA111EZC3.addAuxBox("ASI_C1_17A_I4")
CA111EZC3.addAuxBox("ASI_C1_18A_I3")
CA111EZC3.addDpsBox("ASI_C1_18A_I4")



#CC.addAbbAcs380Drive("U000000","172.16.110.66")
CC.addFortressGate("000010","172.16.110.67")



CC.save()


#print(CC.dataSorted)



