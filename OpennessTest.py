import clr
clr.AddReference('C:\\Program Files\\Siemens\\Automation\\Portal V17\PublicAPI\\V17\\Siemens.Engineering.dll')
import Siemens.Engineering
import System
import ipaddress
import anytree
import xmlObjects
from xmlHeader import xmlHeader
from sclObject import sclObject
from globalDB import globalDB
import os
import ctypes
        
class GsdDevice():
    def __init__(self,Device):
        super().__init__()
        self.Device = Device
        self.startDiscovery()
            
    def addModule(self,TypeIdentifier,Name,Slot=None):
        """
        Can add new Modules with this command
        self.Rack.PlugNew(TypeIdentifier,Name,Slot)
        With the TypeIdentifier being
                GSD:GSDML-V2.33-ABB-FPNO-20180516.XML   /   M   /   ID_MODULE_PPO4
                First part being the GSDML or GSD File (all caps)
                Second part being the module type (See 5.8.2 "Get type identifier of devices and device items")
                Third part being the module name
        """
        #TypeIdentifier = "{GsdName}/{GsdType}/{GsdId}".format(GsdName=self.GsdName,GsdType=GsdType,GsdId=GsdId)
        if Slot != None:
            if self.Device.DeviceItems[0].CanPlugNew(TypeIdentifier,Name,Slot):
                newModule = self.Device.DeviceItems[0].PlugNew(TypeIdentifier,Name,Slot)
            else:
                print("Failed To Create Device: {0} At Slot: {1}".format(TypeIdentifier,Slot))
                
        else:
            plugLocations = self.Device.DeviceItems[0].GetPlugLocations()
            plugLocationsList = []
            for x in plugLocations:
                plugLocationsList.append(x.PositionNumber)
            if len(plugLocationsList) > 0:
                if self.Device.DeviceItems[0].CanPlugNew(TypeIdentifier,Name,plugLocationsList[0]):
                    newModule = self.Device.DeviceItems[0].PlugNew(TypeIdentifier,Name,plugLocationsList[0])
                    
            else:
                print("Device:{0} Is Full And Can Not Support More Submodules".format(self.Device.Name))
        self.startDiscovery()
        return newModule
        
    def moveModule(self,deviceItem,newSlot):
        if self.Device.DeviceItems[0].CanPlugMove(deviceItem,newSlot):
            self.Device.DeviceItems[0].PlugMove(TypeIdentifier,newSlot)
        else:
            print("Failed To Move Device: {0} To Slot: {1}".format(deviceItem.Name,newSlot))
        self.startDiscovery()
        return newModule
        
    def insertModule(self,TypeIdentifier,Name,Slot):
        if self.Device.DeviceItems[0].CanPlugMove(deviceItem,newSlot):
            self.Device.DeviceItems[0].PlugMove(TypeIdentifier,newSlot)
        else:
            print("Failed To Move Device: {0} To Slot: {1}".format(deviceItem.Name,newSlot))
        self.startDiscovery()
        return newModule
            
    def deleteModule(self,name):
        for x in self.Device.DeviceItems:
            if x.Name == name:
                x.Delete()
                self.startDiscovery()
                return
        return
            
    def getNetworkInterface(self,object):
        self.checkIECV22LLDPMode(object)
        #self.checkMediaRedundancyRole(object)
        self.networkInterface = Siemens.Engineering.IEngineeringServiceProvider(object).GetService[Siemens.Engineering.HW.Features.NetworkInterface]()
        return self.networkInterface
        
    def checkIECV22LLDPMode(self,object):
        try:
            self.testThenSetAttribute("IECV22LLDPMode",System.Boolean(True),object,False)
        except Siemens.Engineering.EngineeringNotSupportedException:
            pass
            
    def checkMediaRedundancyRole(self,object):
        try:
            self.testThenSetAttribute("MediaRedundancyRole",Siemens.Engineering.HW.MediaRedundancyRole.Client,object,False)
        except Siemens.Engineering.EngineeringNotSupportedException:
            pass
    
    def setIp(self,ip,subnet,connectIoSystem = True,networkInterface = None):
        list_of_IPs = []
        for x in subnet.Nodes:
            list_of_IPs.append(x.GetAttribute("Address"))
        if ip not in list_of_IPs:
            if networkInterface != None:
                self.networkInterface = networkInterface
            self.networkInterface.Nodes[0].SetAttribute('Address',str(ip))
            self.networkInterface.Nodes[0].ConnectToSubnet(subnet)
            if connectIoSystem:
                self.networkInterface.IoConnectors[0].ConnectToIoSystem(subnet.IoSystems[0])
            return
        else:
            print("There Is A Device Detected At {0}".format(ip))
            print("{0} Will Not Be Attached To Subnet {1}".format(self.Device.Name,subnet.Name))
            return
        
    def returnDevice(self):
        return self.Device
        
    def delete(self):
        self.Device.Delete()

    def startDiscovery(self):
        try:
            del(self.Tree)
        except AttributeError:
            pass
        try:
            del(self.Objects)
        except AttributeError:
            pass
        self.Tree = anytree.Node(self.Device.Name)
        self.Objects = {}
        self.Objects = self.__discovery(self.Tree,self.Device)
        
    def __discovery(self,parentNode,thing):
        dic = {}
        for x in thing.DeviceItems:
            node = anytree.Node(x.Name,parent=parentNode)
            dic[x.Name] = self.__discovery(node,x)
            dic[x.Name]["Object"] = x
            dic[x.Name]["Name"] = x.Name
        return dic
        
    def __str__(self):
        string = ""
        for pre, fill, node in anytree.RenderTree(self.Tree):
            string = string + "{0}{1}\n".format(pre, node.name)
        return string
        
    def setAttribute(self,name,value,thing,printLog=True):
        if thing.GetAttribute(name) != value:
            if printLog:
                print("Updating {name} with {value}".format(name=name,value=value))
            thing.SetAttribute(name,value)
            
    def getAttribute(self,name,value,thing):
        return thing.GetAttribute(name)
        
    def testThenSetAttribute(self,name,value,thing,printLog=True):
        #print(name,value,thing.GetAttribute(name),str(value) != str(thing.GetAttribute(name)))
        if str(thing.GetAttribute(name)) != str(value):
            self.setAttribute(name,value,thing,printLog)
            return True
        return False
    
class ungroupedDevice(GsdDevice):
    """
    Creates and Service UnGrouped Devices. Inherits all methods from the GsdDevice class but sets the creation method
    CreateWithItem("GSD:GSDML-V2.33-ABB-FPNO-20180516.XML/DAP",Drive_Name,Drive_Name)
        Needs To Be UpperCase
        Need to Have "/DAP" appended after 
        Save GsdName for other functions
        Save Device for other functions
    """
    def __init__(self,project,typeIdentifier,name,deviceName = None):
        if deviceName == None:
            deviceName = name
        control = True
        while(control):
            try:
                Device = project.UngroupedDevicesGroup.Devices.CreateWithItem(typeIdentifier,name,deviceName)
                control = False
            except Exception as error:
                print(error)
                print("Fix Error And Press Any Key:")
                input()
        super().__init__(Device)
        
class groupedDevice(GsdDevice):
    """
    Creates and Service Grouped Devices. Inherits all methods from the GsdDevice class but sets the creation method 
    """
    def __init__(self,project,typeIdentifier,name,deviceName = None):
        if deviceName == None:
            deviceName = name
        control = True
        while(control):
            try:
                Device = project.Devices.CreateWithItem(typeIdentifier,name,deviceName)
                control = False
            except Exception as error:
                print(error)
                print("Fix Error And Press Any Key:")
                input()
                
        super().__init__(Device)

class tags():
    def __init__(self,software):
        self.TagTables = software.TagTableGroup.TagTables
        self.data = {}
        self.data["name"] = {}
        self.data["address"] = {}
        
        for x in self.TagTables:
            for y in x.Tags:
                self.data["name"][str(y.Name)] = y.LogicalAddress
                self.data["address"][str(y.LogicalAddress)] = str(y.Name)
        
    def addTag(self,name,inOrOut,logicalAddress,dataType,comment = None,tagTable = "Default tag table",force = False):
        Table = self.TagTables.Find(tagTable)
        try:
            Table.Name
        except AttributeError:
            Table = self.TagTables.Create(tagTable)
        if inOrOut not in ["In","Out"]:
            raise MemoryError
        if inOrOut == "In":
            logicalAddress = "%I" + logicalAddress
        if inOrOut == "Out":
            logicalAddress = "%Q" + logicalAddress
        if force:
            try:
                tag = Table.Tags.Create(name, dataType, logicalAddress)
                tag.ExternalAccessible = False
                if comment != None:
                    tag.Comment.Items[0].Text = comment
            except Siemens.Engineering.EngineeringTargetInvocationException:
                pass
            self.data["name"][name] = logicalAddress
            self.data["address"][logicalAddress] = name
            return
        if name in self.data["name"].keys() and logicalAddress in self.data["address"].keys():
            if self.data["name"][name] == logicalAddress and self.data["address"][logicalAddress] == name:
                #print("Found Matching Address:Name Pair [{0:7}]:[{1:25}]".format(logicalAddress,name))
                return
        if name in self.data["name"].keys():
            print("ERROR: Matching Name '{0:25}' At This Address : {1}".format(name,self.data["name"][name]))
            return
        if logicalAddress in self.data["address"].keys():
            print("ERROR: Found Matching Address '{0:7}' With This Name : {1}".format(logicalAddress,self.data["address"][logicalAddress]))
            return
        if name not in self.data["name"].keys():
            if logicalAddress not in self.data["address"].keys():
                tag = Table.Tags.Create(name, dataType, logicalAddress)
                tag.ExternalAccessible = False
                if comment != None:
                    tag.Comment.Items[0].Text = comment
                self.data["name"][name] = logicalAddress
                self.data["address"][logicalAddress] = name
                return
            else:
                print("Address '{0}' Already In Use By This Tag '{1}'".format(logicalAddress,self.data["name"][logicalAddress]))
        else:
            print("Name '{0}' Already In Use At This Address '{1}'".format(name,self.data["name"][name]))        

"""
class createAbbAcs380Drive():
    def __init__(self,project,tags,unitNumber,ip,subnet,zone = ""):
        unitName = unitNumber + zone + "_FMD"
        #Set Type Identifier
        typeIdentifier = "GSD:GSDML-V2.33-ABB-FPNO-20180516.XML"
        
        #Spawn The Device Object
        Object = ungroupedDevice(project,typeIdentifier + "/DAP",unitName)

        #Add Another Submodule for this drive
        PPO4 = Object.addModule(typeIdentifier + "/M/ID_MODULE_PPO4","PPO Type 4_1",1)
        
        #Get The Network Interface For Setting IP Addresses
        Object.getNetworkInterface(Object.Objects[unitName]["Interface"]["Object"])
        
        #set Ip And Connect To The IoSystem
        Object.setIp(ip,subnet)
        
        #Get The Memory Addresses Of The PPO Modules
        inStart = Object.Objects["PPO Type 4_1"]["PPO4 Data Object"]["Object"].Addresses[0].StartAddress
        outStart = Object.Objects["PPO Type 4_1"]["PPO4 Data Object"]["Object"].Addresses[1].StartAddress
        
        #Create Two Tags For The Drive IN and OUT From Thoses Addresses
        tags.addTag(unitName+"_In","In","{0}.0".format(inStart),"typeABBACS380InputsPP04","PP04 Inputs For Drive Flags","FMD PPO Tags")
        tags.addTag(unitName+"_Out","Out","{0}.0".format(outStart),"typeABBACS380OutputsPP04","PP04 Outputs For Drive Control","FMD PPO Tags")
        
"""
  
class createScannerSickCLV6xx():
    def __init__(self,project,tags,unitNumber,ip,subnet,zone = ""):
        unitName = unitNumber + zone
        typeIdentifier = "GSD:GSDML-V2.3-SICK-CLV62XCLV65X_VIA_CDF600-20150312.XML"
        Object = ungroupedDevice(project,typeIdentifier + "/DAP",unitNumber + "_SC")
        Object.getNetworkInterface(Object.Objects[unitNumber + "_SC"]["Interface"]["Object"])
        Object.setIp(ip,subnet)
        Ctrl_Bits_in_1 = Object.Objects["Ctrl Bits in_1"]["Ctrl Bits in"]["Object"].Addresses[0].StartAddress
        Ctrl_Bits_out_1 = Object.Objects["Ctrl Bits out_1"]["Ctrl Bits out"]["Object"].Addresses[0].StartAddress
        Byte_Input_1 = Object.Objects[" 32 Byte Input_1"][" 32 Byte Input"]["Object"].Addresses[0].StartAddress
        Byte_Output_1 = Object.Objects[" 32 Byte Output_1"][" 32 Byte Output"]["Object"].Addresses[0].StartAddress
        if Ctrl_Bits_in_1 != -1 and Ctrl_Bits_out_1 != -1 and Byte_Input_1 != -1 and Byte_Output_1 != -1:
            tags.addTag(unitName + "_Scanner_StatusWord","In","{0}.0".format(Ctrl_Bits_in_1),"typeScannerSickStatusInput","Scanner Status Signals","Scanner Tags")
            tags.addTag(unitName + "_Scanner_CtrlWord","Out","{0}.0".format(Ctrl_Bits_out_1),"typeScannerSickCtrlOutput","Scanner Ctrl Signals","Scanner Tags")
            tags.addTag(unitName + "_Scanner_Data_IN","In","{0}.0".format(Byte_Input_1),"typeScannerSickDataInput","Scanner Data Input","Scanner Tags")
            tags.addTag(unitName + "_Scanner_Data_OUT","Out","{0}.0".format(Byte_Output_1),"typeScannerSickDataOutput","Scanner Data Output","Scanner Tags")
        
class createPnpn():
    def __init__(self,project,tags,unitNumber,ip,subnet,zone = ""):
        unitName = unitNumber + "_PNPN"
        typeIdentifier = "OrderNumber:6ES7 158-3AD10-0XA0"
        Object = ungroupedDevice(project,typeIdentifier + "/V4.2",unitName,unitName)
        Object.getNetworkInterface(Object.Objects[unitName]["PROFINET interface X1"]["Object"])
        Object.setIp(ip,subnet)
        
class createConnectionBox():
    def __init__(self,project,tags,unitName,ip,subnet,zone = ""):
        typeIdentifier = "OrderNumber:6AV2 125-2AE23-0AX0"
        Object = ungroupedDevice(project,typeIdentifier + "/V5.2",unitName)
        Object.getNetworkInterface(Object.Objects[unitName]["SCALANCE interface_1"]["Object"])
        Object.setIp(ip,subnet)
        
class createHmi():
    def __init__(self,project,tags,Name,ip,subnet,zone = ""):
        Object = GsdDevice(project.Devices.CreateFrom(project.ProjectLibrary.MasterCopyFolder.MasterCopies.Find("Systems-HMI1")))
        Object.Device.SetAttribute("Name",Name)
        Object.startDiscovery()
        Object.getNetworkInterface(Object.Objects[Name + ".IE_CP_1"]["PROFINET Interface_1"]["Object"])
        Object.networkInterface.SetAttribute("InterfaceOperatingMode",2)
        Object.setIp(ip,subnet)
        
class createMoviMot():
    def __init__(self,project,tags,unitNumber,ip,subnet,zone = ""):
        unitName = unitNumber + "_MMD"
        typeIdentifier = "GSD:GSDML-V2.25-SEW-MFE52A-20161017-102525.XML"
        Object = ungroupedDevice(project,typeIdentifier + "/DAP/MFE PDEV MRP 3MM",unitName)
        Object.deleteModule("Slot not used_3")
        Slot3 = Object.addModule(typeIdentifier + "/M/11","4/6 DI_1",3)
        Object.getNetworkInterface(Object.Objects[unitName]["Ethernet Interface"]["Object"])
        Object.setIp(ip,subnet)
        IOin = Object.Objects["4/6 DI_1"]["4/6 DI"]["Object"].Addresses[0].StartAddress
        MM3PDin = Object.Objects["MOVIMOT 3PD_1"]["MOVIMOT 3PD"]["Object"].Addresses[0].StartAddress
        MM3PDout = Object.Objects["MOVIMOT 3PD_1"]["MOVIMOT 3PD"]["Object"].Addresses[1].StartAddress
        if IOin != -1 and MM3PDin != -1 and MM3PDout != -1:
            tags.addTag(unitNumber + "_PE_P","In","{0}.0".format(IOin),"Bool","4/6 DI Input 1","MMD Tags")
            tags.addTag(unitName + "_In","In","{0}.0".format(MM3PDin),"typeProfinetMoviMotInputs","Input Commands","MMD Tags")
            tags.addTag(unitName + "_Out","Out","{0}.0".format(MM3PDout),"typeProfinetMoviMotOutputs","Output Flags","MMD Tags")
        self.LAD = False
        self.SCL = False

class createFortressGate():
    def __init__(self,project,tags,unitNumber,ip,subnet,zone = ""):
        unitName = unitNumber + zone + "_GS"
        typeIdentifier = "GSD:GSDML-V2.35-FORTRESS-PROLOK-20190704.XML"
        self.Object = ungroupedDevice(project,typeIdentifier + "/DAP",unitName)
        safetyModule = self.Object.addModule(typeIdentifier + "/M/ID_MODULE_F_IO_3DIN1DOUT","Safety Module_1",1)
        io = self.Object.addModule(typeIdentifier + "/M/ID_MODULE_IO","Unsafe IO Data_1",2)
        self.Object.getNetworkInterface(self.Object.Objects[unitName]["Interface"]["Object"])
        self.Object.setIp(ip,subnet)
        safetyModuleIn = self.Object.Objects["Safety Module_1"]["Safety Module"]["Object"].Addresses[0].StartAddress
        if safetyModuleIn != -1:
            tags.addTag(unitName+"_Sol_1","In","{0}.0".format(safetyModuleIn),"Bool","","E Stop Devices")
            tags.addTag(unitName+"_Sol_2","In","{0}.1".format(safetyModuleIn),"Bool","","E Stop Devices")
            tags.addTag(unitName+"_Estop_1","In","{0}.4".format(safetyModuleIn),"Bool","","E Stop Devices")
            tags.addTag(unitName+"_Estop_2","In","{0}.5".format(safetyModuleIn),"Bool","","E Stop Devices")
            
        lampsOut = self.Object.Objects["Unsafe IO Data_1"]["IO Lamps"]["Object"].Addresses[0].StartAddress
        if lampsOut != -1:
            tags.addTag(unitName+"_ST_LT","Out","{0}.0".format(lampsOut),"Bool","","E Stop Devices")
            tags.addTag(unitName+"_G_LT","Out","{0}.1".format(lampsOut),"Bool","","E Stop Devices")
            tags.addTag(unitName+"_ES_LT","Out","{0}.3".format(lampsOut),"Bool","","E Stop Devices")
            tags.addTag(unitName+"_RQ_LT","Out","{0}.4".format(lampsOut),"Bool","","E Stop Devices")
            tags.addTag(unitName+"_RS_LT","Out","{0}.5".format(lampsOut),"Bool","","E Stop Devices")
            
        switchesIn = self.Object.Objects["Unsafe IO Data_1"]["IO Switches"]["Object"].Addresses[0].StartAddress
        if switchesIn != -1:
            tags.addTag(unitName+"_ST_PVB","In","{0}.0".format(switchesIn),"Bool","","E Stop Devices")
            tags.addTag(unitName+"_G_SW","In","{0}.1".format(switchesIn),"Bool","","E Stop Devices")
            tags.addTag(unitName+"_RQ_PB","In","{0}.4".format(switchesIn),"Bool","","E Stop Devices")
            tags.addTag(unitName+"_RS_PB","In","{0}.5".format(switchesIn),"Bool","","E Stop Devices")
            
        solenoidOut = self.Object.Objects["Unsafe IO Data_1"]["Solenoid Drive"]["Object"].Addresses[0].StartAddress
        if solenoidOut != -1:
            tags.addTag(unitName+"_Sol_Drive","Out","{0}.0".format(solenoidOut),"Bool","","E Stop Devices")
            
        gateIn = self.Object.Objects["Unsafe IO Data_1"]["Gate Monitor"]["Object"].Addresses[0].StartAddress
        if gateIn != -1:
            tags.addTag(unitName+"_GateMon","In","{0}.0".format(gateIn),"Bool","","E Stop Devices")
            
        solenoidIn = self.Object.Objects["Unsafe IO Data_1"]["Solenoid Monitor"]["Object"].Addresses[0].StartAddress
        if solenoidIn != -1:
            tags.addTag(unitName+"_SolMon","In","{0}.0".format(solenoidIn),"Bool","","E Stop Devices")
        self.LAD = True
        self.SCL = False
        self.Failsafe_FIODBName = self.Object.Objects["Safety Module_1"]["Safety Module"]["Object"].GetAttribute("Failsafe_FIODBName")

class createPlc(GsdDevice):
    def __init__(self,plc):
        super().__init__(plc)
        self.cpu = plc.DeviceItems[1]
        self.software = Siemens.Engineering.IEngineeringServiceProvider(self.cpu).GetService[Siemens.Engineering.HW.Features.SoftwareContainer]().Software
        
        
    def setConfig(self):
        self.checkIECV22LLDPMode(self.Objects[self.cpu.Name]["PROFINET interface_1"]["Object"])
        self.checkIECV22LLDPMode(self.Objects[self.cpu.Name]["PROFINET interface_2"]["Object"])
        
        cpuHardware = Siemens.Engineering.IEngineeringServiceProvider(self.cpu).GetService[Siemens.Engineering.HW.Features.PlcAccessLevelProvider]()
        
        self.CentralFSourceAddress = self.cpu.GetAttribute("Failsafe_CentralFSourceAddress")
        self.testThenSetAttribute("Failsafe_CentralFSourceAddress",System.UInt64(1),cpuHardware)
        self.testThenSetAttribute("Failsafe_LowerBoundForFDestinationAddresses",System.UInt64(100),cpuHardware)
        self.testThenSetAttribute("Failsafe_UpperBoundForFDestinationAddresses",System.UInt64(199),cpuHardware)
        self.testThenSetAttribute("CycleEnableMinimumCycleTime",System.Boolean(False),cpuHardware)
        self.testThenSetAttribute("WebserverActivate",System.Boolean(False),cpuHardware)
        self.testThenSetAttribute("ProtectionEnablePutGetCommunication",System.Boolean(False),cpuHardware)
        self.testThenSetAttribute("TimeOfDayLocalTimeZone",System.UInt64(11),cpuHardware)
        
        self.Objects[self.cpu.Name]["PROFINET interface_1"]["Object"].SetAttribute("MediaRedundancyRole",Siemens.Engineering.HW.MediaRedundancyRole.Manager)
        
        #DNS
        if self.testThenSetAttribute("PnDnsConfigNameResolve",Siemens.Engineering.HW.PnDnsConfigNameResolve.Project,self.cpu):
            self.setAttribute("PnDnsConfiguration",System.Array[str]([System.String("8.8.8.8"),System.String("4.4.4.4")]),self.cpu)
        
        #OPC
        opc = self.cpu.DeviceItems[2]

        self.testThenSetAttribute("OpcUaSecurityPolicies",System.UInt64(120),opc)
        self.testThenSetAttribute("OpcUaGuestAuthentication",System.Boolean(False),opc)
        self.testThenSetAttribute("OpcUaPasswordAuthentication",System.Boolean(True),opc)
        
        opcUaUserManagement = Siemens.Engineering.IEngineeringServiceProvider(opc).GetService[Siemens.Engineering.HW.Features.OpcUaUserManagement]()
        if opcUaUserManagement.OpcUaUsers.Find("VizUser") == None:
            opcUaUserManagement.OpcUaUsers.Create("VizUser",System.Security.SecureString("&Iconics2022"))
            print("Creating OPC UA User 'VizUser'")
            
        if opcUaUserManagement.OpcUaUsers.Find("LoggingUser") == None:
            opcUaUserManagement.OpcUaUsers.Create("LoggingUser",System.Security.SecureString("&Dematic17"))
            print("Creating OPC UA User 'LoggingUser'")
            
        self.testThenSetAttribute("OpcUaMaxMonitoredItems",System.UInt32(50000),opcUaUserManagement)
        in1 = self.cpu.DeviceItems[4]
        #enable NTP
        self.testThenSetAttribute("TimeSynchronizationNtp",System.Boolean(True),in1)
        self.testThenSetAttribute("TimeSynchronizationServer1",System.String("time.windows.com"),cpuHardware)
        self.testThenSetAttribute("TimeSynchronizationUpdateInterval",System.UInt64(3600),cpuHardware)
        
    def setName(self,name):
        self.cpu.SetAttribute("Name",System.String(name))
        
    def getName(self,name):
        self.cpu.GetAttribute("Name")
        
        """
class Pnag(GsdDevice):
    def __init__(self,Device,tags):
        super().__init__(Device)
        self.tags = tags
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
        #self.createTags()
        
    def createTags(self):
        print("Creating Needed Tags For {0}".format(self.Device.Name))
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
      
        Circuit is 1 or 2
        Node is Node
        AorB is A or B
        bitOffSet is 1-4
        
        This function will add a tag given the node address
        (name,logicalAddress,dataType,comment,tagTable):
 
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
        pass
        """
        
        """
class Pncg(GsdDevice):
    def __init__(self,Device,tags):
        super().__init__(Device)
        self.tags = tags
        #self.createTags()
        
    def createTags(self):
        print("Creating Needed Tags For {0}".format(self.Device.Name))
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
        pass
        """
class object():
    def __init__(self):
        self.project = Siemens.Engineering.TiaPortal.GetProcesses()[0].Attach().Projects[0]
        for x in self.project.Devices:
            if x.TypeIdentifier != None and 'S71500' in x.TypeIdentifier:
                self.PLC = createPlc(x)
                break
                    
        try:
            self.PLC
        except AttributeError:
            print("No PLC Detected")
            quit()
        quit()
            
        if self.project.Subnets.Count > 0:
            self.subnet = self.project.Subnets[0]
            if self.subnet.IoSystems.Count == 0:
                print("ERROR: No IO Systems Detected")
                networkInterface = self.PLC.getNetworkInterface(self.PLC.Objects["Systems"]["PROFINET interface_1"]["Object"])
                networkInterface.IoControllers[0].CreateIoSystem("PROFINET IO-System")
                print("IO System Created")
        else:
            print("ERROR: No Subnet Detected")
            quit()
            
        self.tags = tags(self.PLC.software)
        
        self.networkDevice = {}
        for x in self.project.Devices:
            if x.TypeIdentifier != None:
                if "BIHL UND WIEDEMANN-ASI GATEWAY" in x.TypeIdentifier:
                    self.networkDevice[x.Name] = Pnag(x,self.tags)
                
                elif "DEMATIC-PNCG" in x.TypeIdentifier:
                    self.networkDevice[x.Name] = Pncg(x,self.tags)                
        name = ["U350000_Conn_Box_1","U350355_Conn_Box_1","U350755_Conn_Box_2","U351155_Conn_Box_3","U351555_Conn_Box_4","U370050","U350157","U350355","U350555","U350755","U350955","U351155","U351355","U351555","U351755","U350190","U350390","U350590","U350790","U350990","U351190","U351390","U351590","U351790","U350000","U350005","U340130","U340120","U340230","U340220","U340330","U340320","U340430","U340420","U340530","U340520","U340630","U340620","U340730","U340720","U340830","U340820","U350010","U350015","U350020","U350025","U350030","U350035","U350085","U350090","U350095","U370000","U351720","U351730","U351740","U351750","U350100","U350110","U350120","U350130","U350140","U350150","U350300","U350310","U350320","U350330","U350340","U350350","U350500","U350510","U350520","U350530","U350540","U350550","U350700","U350710","U350720","U350730","U350740","U350750","U350900","U350910","U350920","U350930","U350940","U350950","U351100","U351110","U351120","U351130","U351140","U351150","U351300","U351310","U351320","U351330","U351340","U351350","U351500","U351510","U351520","U351530","U351540","U351550","U351700","U351710"]
        address = ["172.16.211.32","172.16.212.32","172.16.212.34","172.16.212.36","172.16.212.38","172.16.211.51","172.16.212.51","172.16.212.52","172.16.212.53","172.16.212.54","172.16.212.55","172.16.212.56","172.16.212.57","172.16.212.58","172.16.212.59","172.16.212.81","172.16.212.82","172.16.212.83","172.16.212.84","172.16.212.85","172.16.212.86","172.16.212.87","172.16.212.88","172.16.212.89","172.16.211.101","172.16.211.102","172.16.211.103","172.16.211.104","172.16.211.105","172.16.211.106","172.16.211.107","172.16.211.108","172.16.211.109","172.16.211.110","172.16.211.111","172.16.211.112","172.16.211.113","172.16.211.114","172.16.211.115","172.16.211.116","172.16.211.117","172.16.211.118","172.16.211.119","172.16.211.120","172.16.211.121","172.16.211.122","172.16.211.123","172.16.211.124","172.16.211.125","172.16.211.126","172.16.211.127","172.16.211.128","172.16.212.211","172.16.212.212","172.16.212.213","172.16.212.214","172.16.212.101","172.16.212.102","172.16.212.103","172.16.212.104","172.16.212.105","172.16.212.106","172.16.212.107","172.16.212.108","172.16.212.109","172.16.212.110","172.16.212.111","172.16.212.112","172.16.212.113","172.16.212.114","172.16.212.115","172.16.212.116","172.16.212.117","172.16.212.118","172.16.212.119","172.16.212.120","172.16.212.121","172.16.212.122","172.16.212.123","172.16.212.124","172.16.212.125","172.16.212.126","172.16.212.127","172.16.212.128","172.16.212.129","172.16.212.130","172.16.212.131","172.16.212.132","172.16.212.133","172.16.212.134","172.16.212.135","172.16.212.136","172.16.212.137","172.16.212.138","172.16.212.139","172.16.212.140","172.16.212.141","172.16.212.142","172.16.212.143","172.16.212.144","172.16.212.145","172.16.212.146","172.16.212.147","172.16.212.148","172.16.212.149","172.16.212.150"]
        type = ["ConnectionBox","ConnectionBox","ConnectionBox","ConnectionBox","ConnectionBox","ScannerSickCLV6xx","ScannerSickCLV6xx","ScannerSickCLV6xx","ScannerSickCLV6xx","ScannerSickCLV6xx","ScannerSickCLV6xx","ScannerSickCLV6xx","ScannerSickCLV6xx","ScannerSickCLV6xx","ScannerSickCLV6xx","PNPN","PNPN","PNPN","PNPN","PNPN","PNPN","PNPN","PNPN","PNPN","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive","AbbAcs380Drive"]
        zone = ["","","","","","_E2_Z2","_E_Z2","_E2_Z2","_E2_Z2","_E2_Z2","_E2_Z2","_E2_Z2","_E2_Z2","_E2_Z2","_E2_Z2","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","",""]
        #self.spawnDevice("NetworkDevicesSAVE",name,type,address,zone)
        self.area()
        #self.test() 
        
    def addHalfNodeASI(self,tagName,address,devices):
        """
        ASI_A2_21A_I1
        ASI_B1_18A_O4
        """
        for x in devices:
            if x[-1:] == address.split("_")[1][:1]:
                #print(x[-1:]," ",x," ", address.split("_")[1][:1]," ",address)
                self.networkDevice[x].addHalfNodeASI(tagName,address)
        
    def spawnDevice(self,Line,Name,Type,Address,Zone):
        import shutil
        import re
        import ipaddress
        fileStr = os.getcwd() + "/" + Line
        if os.path.exists(Line):
            shutil.rmtree(fileStr)
        os.mkdir(Line)
        xml = xmlHeader(Line,Line)
        ObjectList = xml.ObjectList
        scl = sclObject(Line + "_SetConfigs",Line)
        blockGroup = self.PLC.software.BlockGroup.Groups.Find("Project").Groups.Find(Line)
        if blockGroup != None:
            blockGroup.Delete()
        software = self.PLC.software.BlockGroup.Groups.Find("Project").Groups.Create(Line)
        
        if "HMI" in Type:
            oldName = self.cpu.getName()
        
        for x in range(len(Name)):
            if Type[x] == "AbbAcs380Drive":
                createAbbAcs380Drive(self.project,self.tags,Name[x],Address[x],self.subnet)
                xmlObjects.AbbAcs380Drive(Name[x],ObjectList,Zone[x],scl,software)
                
            elif Type[x] == "AsiABBDriveNAType01":
                xmlObjects.AsiABBDriveNAType01(Name[x],ObjectList,Zone[x],scl,software)
                
            elif Type[x] == "ScannerSickCLV6xx":
                createScannerSickCLV6xx(self.project,self.tags,Name[x],Address[x],self.subnet)
                xmlObjects.ScannerSickCLV6xx(Name[x],ObjectList,Zone[x],scl,software)
                
            elif Type[x] == "FortressGate":
                gate = createFortressGate(self.project,self.tags,Name[x],Address[x],self.subnet)
                xmlObjects.FortressGate(Name[x],gate.Failsafe_FIODBName,ObjectList,Zone[x],scl,software)
                
            elif Type[x] == "MOVIMOT":
                createMOVIMOT(self.project,self.tags,Name[x],Address[x],self.subnet)
                xmlObjects.MoviMot(Name[x],ObjectList,Zone[x],scl,software)
                
            elif Type[x] == "HMI":
                createHmi(self.project,self.tags,Name[x],Address[x],self.subnet)
                #Find and create block for this
                
            elif Type[x] == "ConnectionBox":
                createConnectionBox(self.project,self.tags,Name[x],Address[x],self.subnet)
                connectionNumber = re.search("U[0-9]{6}_Conn_Box_[0-9]{1}",Name[x]).group()[-1:]
                xmlObjects.ConnectionBox(Name[x],connectionNumber,ObjectList,Zone[x],scl,software)
                
            elif Type[x] == "PNPN":
                createPnpn(self.project,self.tags,Name[x],Address[x],self.subnet,Zone[x])
                #Find and create block for this create
                
        xmlObjects.CallSetConfig(Line + "_SetConfigs", ObjectList)
        xml.save()
        scl.save()
        if "HMI" in Type:
            self.cpu.setName(oldName)
        for x in os.listdir(fileStr):
            software.Blocks.Import(System.IO.FileInfo(fileStr + "/" +x),Siemens.Engineering.ImportOptions.Override) 
            
    def list(self,int):
        return ([None] * int)
        
    def area(self):
        import shutil
        Line = "PanelFunctions"
        fileStr = os.getcwd() + "/" + Line
        for x in [Line,"DefaultDBs"]:
            if os.path.exists(x):
                shutil.rmtree(os.getcwd() + "\\" + x)
            os.mkdir(x)
        xml = xmlHeader(Line,Line)
        ObjectList = xml.ObjectList
        scl = sclObject(Line + "_SetConfigs",Line)
        
        
        CabnetNumber = "CC210"
        ControlArea = self.list(2)
        ControlArea[0] = "CA211"
        ControlArea[1] = "CA212"
        EZCName = self.list(2)
        EZCName[0] = ["EZC1","EZC2","EZC3"]
        EZCName[1] = ["EZC1","EZC2","EZC3","EZC4","EZC5","EZC6","EZC7","EZC8","EZC9"]
        Dps = self.list(2)
        Dps[0] = self.list(len(EZCName[0]))
        Dps[1] = self.list(len(EZCName[1]))
        
        Dps[0][0] = []
        Dps[0][1] = ["DPS1","DPS2","DPS3","DPS4","DPS5"]
        Dps[0][2] = ["DPS6","DPS7","DPS8"]
        Dps[1][0] = ["DPS1","DPS2","DPS3","DPS4","DPS5","DPS6"]
        Dps[1][1] = ["DPS7","DPS8","DPS9","DPS10","DPS11"]
        Dps[1][2] = ["DPS12","DPS13","DPS14","DPS15","DPS16"]
        Dps[1][3] = ["DPS17","DPS18","DPS19","DPS20","DPS21"]
        Dps[1][4] = ["DPS22","DPS23","DPS24","DPS25","DPS26"]
        Dps[1][5] = ["DPS27","DPS28","DPS29","DPS30","DPS31"]
        Dps[1][6] = ["DPS32","DPS33","DPS34","DPS35","DPS36"]
        Dps[1][7] = ["DPS37","DPS38","DPS39","DPS40","DPS41"]
        Dps[1][8] = ["DPS42","DPS43","DPS44","DPS45","DPS46"]
        
        
        Aux = self.list(2)
        Aux[0] = self.list(len(EZCName[0]))
        Aux[1] = self.list(len(EZCName[1]))
        Aux[0][0] = ["AUX1","AUX2","AUX3"]
        Aux[0][1] = []
        Aux[0][2] = []
        Aux[1][0] = ["AUX1"]
        Aux[1][1] = []
        Aux[1][2] = []
        Aux[1][3] = []
        Aux[1][4] = []
        Aux[1][5] = ["AUX2"]
        Aux[1][6] = []
        Aux[1][7] = []
        Aux[1][8] = ["AUX3"]
        
        
        Pnag = self.list(2)
        Pnag[0] = ["U350000_PNAG_A","U370045_PNAG_B","U370000_PNAG_C"]
        Pnag[1] = ["U350352_PNAG_A","U351352_PNAG_B"]
        
        Pncg = self.list(2)
        Pncg[0] = ["U370050_PNCG_01","U370575_PNCG_02"]
        Pncg[1] = ["U350160_PNCG_01","U350360_PNCG_02","U350560_PNCG_03","U350760_PNCG_04","U350960_PNCG_05","U351160_PNCG_06","U351360_PNCG_07","U351560_PNCG_08","U351760_PNCG_09"]
        
        Estops = self.list(2)
        Estops[0] = self.list(len(EZCName[0]))
        Estops[1] = self.list(len(EZCName[1]))
        
        EstopsAsi = self.list(2)
        EstopsAsi[0] = self.list(len(EZCName[0]))
        EstopsAsi[1] = self.list(len(EZCName[1]))
        
        Estops[0][0] = ["U340700_PC_ES","U350000_PC_ES","U350010_PC_ES1","U350010_PC_ES2","U340800_PC_ES1","U340800_PC_ES2","U350020_PC_ES1","U350020_PC_ES2","U370045_PC_ES1","U370045_PC_ES2"]
        EstopsAsi[0][0] = ["ASI_B1_27","ASI_A2_26","ASI_A1_20","ASI_A1_21","ASI_A2_24","ASI_A2_25","ASI_A1_22","ASI_A1_23","ASI_B2_28","ASI_B2_29"]
        
        Estops[0][1] = ["U350045_PC_ES1","U350045_PC_ES2","U370066_PC_ES"]
        EstopsAsi[0][1] = ["ASI_A1_24","ASI_A1_25","ASI_B1_28"]
        
        Estops[0][2] = ["U350075_PC_ES","U370000_PC_ES1"]
        EstopsAsi[0][2] = ["ASI_C1_28","ASI_C1_29"]
        
        
        
        Estops[1][0] = ["U350156_PC_ES","U350165_PC_ES1","U350165_PC_ES2",]
        EstopsAsi[1][0] = ["ASI_A1_23","ASI_A1_24","ASI_A1_25"]
        
        Estops[1][1] = ["U350355_PC_ES1","U350355_PC_ES2","U350365_PC_ES"]
        EstopsAsi[1][1] = ["ASI_A1_26","ASI_A1_27","ASI_A1_22"]
        
        Estops[1][2] = ["U350555_PC_ES1","U350555_PC_ES2","U350565_PC_ES"]
        EstopsAsi[1][2] = ["ASI_A2_19","ASI_A2_20","ASI_A2_21"]
        
        Estops[1][3] = ["U350755_PC_ES1","U350755_PC_ES2","U350765_PC_ES"]
        EstopsAsi[1][3] = ["ASI_A2_22","ASI_A2_23","ASI_A2_24"]
        
        Estops[1][4] = ["U350955_PC_ES1","U350955_PC_ES2","U350965_PC_ES"]
        EstopsAsi[1][4] = ["ASI_A2_25","ASI_A2_18","ASI_A2_26"]
        
        Estops[1][5] = ["U351155_PC_ES1","U351155_PC_ES2","U351165_PC_ES"]
        EstopsAsi[1][5] = ["ASI_B1_22","ASI_B1_23","ASI_B1_24"]
        
        Estops[1][6] = ["U351355_PC_ES1","U351355_PC_ES2","U351365_PC_ES"]
        EstopsAsi[1][6] = ["ASI_B1_25","ASI_B1_26","ASI_B1_27"]
        
        Estops[1][7] = ["U351555_PC_ES1","U351555_PC_ES2","U351565_PC_ES"]
        EstopsAsi[1][7] = ["ASI_B2_22","ASI_B2_23","ASI_B2_24"]
        
        Estops[1][8] = ["U351755_PC_ES1","U351755_PC_ES2","U351765_PC_ES"]
        EstopsAsi[1][8] = ["ASI_B2_25","ASI_B2_26","ASI_B2_27"]
               
        for x in range(len(Estops)):
            for y in range(len(Estops[x])):   
                if len(Estops[x][y]) == len(EstopsAsi[x][y]):
                    for z in range(len(Estops[x][y])):
                        self.addHalfNodeASI(Estops[x][y][z] + "_NONSAFE",EstopsAsi[x][y][z] + "A_I1",Pnag[x])
                        self.addHalfNodeASI(Estops[x][y][z] + "_LT_R",EstopsAsi[x][y][z] + "A_O1",Pnag[x])
                        self.addHalfNodeASI(Estops[x][y][z] + "_LT_G",EstopsAsi[x][y][z] + "A_O2",Pnag[x])
                else:
                    print("Missized Estop and EstopsAsi Array")
                    print(Estops[x][y])
                    print(EstopsAsi[x][y])
                    quit()
        
        blockGroup = self.PLC.software.BlockGroup.Groups.Find("Project").Groups.Find(Line)
        if blockGroup != None:
            blockGroup.Delete()
        LineSoftware = self.PLC.software.BlockGroup.Groups.Find("Project").Groups.Create(Line)
        
        xmlObjects.CC(CabnetNumber,ControlArea,EZCName,Dps,Aux,Pnag,Pncg,Estops,EstopsAsi,ObjectList,scl,LineSoftware)
        xmlObjects.CallSetConfig(Line + "_SetConfigs", ObjectList)
    
        DefaultDBs = self.PLC.software.BlockGroup.Groups.Find("Project").Groups.Find("DefaultDBs")
        if DefaultDBs == None:
            software.BlockGroup.Groups.Find("Project").Groups.Create("DefaultDBs")
            DefaultDBs = self.PLC.software.BlockGroup.Groups.Find("Project").Groups.Find("DefaultDBs")
        
        DataFromSafety = DefaultDBs.Blocks.Find("DataFromSafety")
        if DataFromSafety != None:
            DataFromSafety.Delete()
        DataFromSafety = Global_DB("DataFromSafety")
        DataFromSafety.addMember("SafetyStatusToPLC",'"typeSafetyStatusToMainPanel"')
            
        DataToSafety = DefaultDBs.Blocks.Find("DataToSafety")
        if DataToSafety != None:
            DataToSafety.Delete()
        DataToSafety = Global_DB("DataToSafety")
        DataToSafety.addMember("PLCToSafety",'"typeZoneToAreaControl"')
        
        for x in range(len(ControlArea)):
            DataToSafety.addMember(ControlArea[x] + "EZCxPowerGroupToSafetyStatus",'Array[1..{len}] of "typePowerGroupStatusToSafety"'.format(len = len(EZCName[x])))
            DataFromSafety.addMember(ControlArea[x] + "EStopHealthy","Array[1..{len}] of Bool".format(len = len([item for sublist in Estops[x] for item in sublist])))
            DataFromSafety.addMember(ControlArea[x] + "EZCxSafetyStatusToPowerGroup",'Array[1..{len}] of "typeSafetyStatusToPowerGroup"'.format(len = len(EZCName[x])))
        
        dbPncgParameterData = DefaultDBs.Blocks.Find("dbPncgParameterData")
        if dbPncgParameterData != None:
            dbPncgParameterData.Delete()
        dbPncgParameterData = Global_DB("dbPncgParameterData")
        for x in [item for sublist in Pncg for item in sublist]:
            dbPncgParameterData.addMember(x,'"typeNodeParameters"')
            
            
        DataToSafety.save()
        DataFromSafety.save()
        dbPncgParameterData.save()
        xml.save()
        scl.save()
        for x in os.listdir(fileStr):
            LineSoftware.Blocks.Import(System.IO.FileInfo(fileStr + "/" +x),Siemens.Engineering.ImportOptions.Override)
        for x in os.listdir(os.getcwd() + "/" + 'DefaultDBs'):
            DefaultDBs.Blocks.Import(System.IO.FileInfo(os.getcwd() + "/DefaultDBs/" + x),Siemens.Engineering.ImportOptions.Override)
    
    def spawnAsiDevice(self,Name,Type,Asi):
        import shutil
        Line = "Test"
        fileStr = os.getcwd() + "/" + Line
        if os.path.exists(Line):
            shutil.rmtree(fileStr)
        os.mkdir(Line)
        xml = xmlHeader(Line,Line)
        ObjectList = xml.ObjectList
        scl = sclObject(Line + "_SetConfigs",Line)
        blockGroup = self.PLC.software.BlockGroup.Groups.Find("Project").Groups.Find(Line)
        if blockGroup != None:
            blockGroup.Delete()
        software = self.PLC.software.BlockGroup.Groups.Find("Project").Groups.Create(Line)
        
        for x in range(len(Name)):
            networkDevice = Asi[x].split("_")[1][:1]
            circuit = Asi[x].split("_")[1][1:]
            node = Asi[x].split("_")[2][:-1]
            AorB = Asi[x].split("_")[2][-1:]
            inAsiBusFault = 'Inst{0}.outFaultGWChn{1}{2}[{3}]'.format(self.networkDevice[networkDevice].Device.Name,str(int(circuit) - 1),AorB,node)
            if Type[x] == "EStopVis":
                node = Asi[x].split("_")[2]
                #inAsiBusFault = 'Inst{0}.outVisuInterface.status.summary'.format(self.networkDevice[networkDevice].Device.Name)
                block = xmlObjects.EStopVis(self.networkDevice[networkDevice].Device.Name,Name[x],ObjectList,scl)
                instanceDB = software.Blocks.CreateInstanceDB(block.Component.get('Name'),True,1,block.CallInfo.get("Name"))
                self.networkDevice[networkDevice].addHalfNode(Name[x] + "_NONSAFE",circuit,node,"A",1,"In")
                self.networkDevice[networkDevice].addHalfNode(Name[x] + "_LT_R",circuit,node,"A",1,"Out")
                self.networkDevice[networkDevice].addHalfNode(Name[x] + "_LT_G",circuit,node,"A",2,"Out")
        
        xmlObjects.CallSetConfig(Line + "_SetConfigs", ObjectList)
        xml.save()
        scl.save()
        for x in os.listdir(fileStr):
            software.Blocks.Import(System.IO.FileInfo(fileStr + "/" +x),Siemens.Engineering.ImportOptions.Override)
        
    def test(self):
        name = ["U000000","U000010","U000020","U000030","U000040","U000050","U000060"]
        type = ["AbbAcs380Drive","ScannerSickCLV62x","PNPN","ConnectionBox","HMI","MOVIMOT","FortressGateSwitch"]
        ip = ["172.16.111.254","172.16.111.253","172.16.111.252","172.16.111.251","172.16.111.250","172.16.111.239","172.16.111.238"]
        zone = []
        for x in range(len(name)):
            zone.append("")
        self.spawnDevice("Test",name,type,ip,zone)
        
    def Cax(self):
        self.cax = Siemens.Engineering.IEngineeringServiceProvider(self.project).GetService[Siemens.Engineering.Cax.CaxProvider]()
        #self.cax.Export(self.project,System.IO.FileInfo("C:/Users/leonarjd/OneDrive - dematic.com/Desktop/Test.aml"),System.IO.FileInfo("C:/Users/leonarjd/OneDrive - dematic.com/Desktop/log.log"))
        device = self.project.UngroupedDevicesGroup.Devices.Find("U000000_FMD")
        self.cax.Export(device,System.IO.FileInfo("C:/Users/leonarjd/OneDrive - dematic.com/Desktop/Test.aml"),System.IO.FileInfo("C:/Users/leonarjd/OneDrive - dematic.com/Desktop/log.log"))
    
def main():
    test = object()
    
#main()

"""
import clr
import System
clr.AddReference('C:\\Program Files\\Siemens\\Automation\\Portal V17\PublicAPI\\V17\\Siemens.Engineering.dll')
import Siemens.Engineering
tia = Siemens.Engineering.TiaPortal.GetProcesses()[0].Attach()
project = tia.Projects[0]
for x in project.Devices:
    if x.TypeIdentifier != None:
            if 'S71500' in x.TypeIdentifier:
                    cpu = x.DeviceItems[1]
                    
sw = Siemens.Engineering.IEngineeringServiceProvider(cpu).GetService[Siemens.Engineering.HW.Features.SoftwareContainer]().Software
line_1 = sw.BlockGroup.Groups.Find("Project").Groups.Find("CA111_Line_1")
line_1_FC = line_1.Blocks.Find("CA111_Line_1")
globalLib = tia.GlobalLibraries.Open(System.IO.FileInfo("T:\\PROJECTS\\Dollar Tree\\Ocala, FL\\P151945\\Software\\Non Project Software\\P151945 (protected)\\P151945 (protected).al17"),Siemens.Engineering.OpenMode.ReadOnly)
globalLib.UpdateCheck(project,Siemens.Engineering.Library.Types.UpdateCheckMode.ReportOutOfDateOnly)

"""