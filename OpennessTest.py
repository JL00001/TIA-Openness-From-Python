import clr
clr.AddReference('C:\\Program Files\\Siemens\\Automation\\Portal V17\PublicAPI\\V17\\Siemens.Engineering.dll')
import Siemens.Engineering
import System
import ipaddress
import anytree
import XML_Objects
from xmlHeader import xmlHeader
from SclObject import SclObject
import os
import ctypes
        
class GsdDevice():
    def __init__(self,Device):
        super().__init__()
        self.Device = Device
        self.startDiscovery()
            
    def addModule(self,TypeIdentifier,Name,Slot):
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
        if self.Device.DeviceItems[0].CanPlugNew(TypeIdentifier,Name,Slot):
            newModule = self.Device.DeviceItems[0].PlugNew(TypeIdentifier,Name,Slot)
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
        self.networkInterface = Siemens.Engineering.IEngineeringServiceProvider(object).GetService[Siemens.Engineering.HW.Features.NetworkInterface]()
        return self.networkInterface
    
    def setIp(self,ip,subnet,connectIoSystem = True,networkInterface = None):
        list_of_IPs = []
        for x in subnet.Nodes:
            list_of_IPs.append(x.GetAttribute("Address"))
        if ip not in list_of_IPs:
            if networkInterface == None:
                self.networkInterface.Nodes[0].SetAttribute('Address',str(ip))
                self.networkInterface.Nodes[0].ConnectToSubnet(subnet)
                if connectIoSystem:
                    self.networkInterface.IoConnectors[0].ConnectToIoSystem(subnet.IoSystems[0])
                return
            else:
                networkInterface.Nodes[0].SetAttribute('Address',str(ip))
                networkInterface.Nodes[0].ConnectToSubnet(subnet)
                if connectIoSystem:
                    networkInterface.IoConnectors[0].ConnectToIoSystem(subnet.IoSystems[0])
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
        
    def setAttribute(self,name,value,thing):
        if thing.GetAttribute(name) != value:
            print("Updating {name} with {value}".format(name=name,value=value))
            thing.SetAttribute(name,value)
    
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
        Device = project.UngroupedDevicesGroup.Devices.CreateWithItem(typeIdentifier,name,deviceName)
        super().__init__(Device)
        
class groupedDevice(GsdDevice):
    """
    Creates and Service Grouped Devices. Inherits all methods from the GsdDevice class but sets the creation method 
    """
    def __init__(self,project,typeIdentifier,name,deviceName = None):
        if deviceName == None:
            deviceName = name
        Device = project.Devices.CreateWithItem(typeIdentifier,name,deviceName)
        super().__init__(Device)

class tagManager():
    def __init__(self,software):
        self.TagTables = software.TagTableGroup.TagTables
        self.data = {}
        self.data["name"] = {}
        self.data["address"] = {}
        
        for x in self.TagTables:
            for y in x.Tags:
                self.data["name"][str(y.Name)] = y.LogicalAddress
                self.data["address"][str(y.LogicalAddress)] = str(y.Name)
        
    def addTag(self,name,inOrOut,logicalAddress,dataType,comment = None,tagTable = "Default tag table"):
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

class createAbbAcs380Drive():
    def __init__(self,project,tagManager,unitName,ip,subnet):
        Name = unitName + " FMD"
        #Set Type Identifier
        typeIdentifier = "GSD:GSDML-V2.33-ABB-FPNO-20180516.XML"
        #Spawn The Device Object
        Object = ungroupedDevice(project,typeIdentifier + "/DAP",Name)
        
        #Add Another Submodule for this drive
        PPO4 = Object.addModule(typeIdentifier + "/M/ID_MODULE_PPO4","PPO Type 4_1",1)
        
        #Get The Network Interface For Setting IP Addresses
        Object.getNetworkInterface(Object.Objects[Name]["Interface"]["Object"])
        
        #set Ip And Connect To The IoSystem
        Object.setIp(ip,subnet)
        
        #Get The Memory Addresses Of The PPO Modules
        inStart = Object.Objects["PPO Type 4_1"]["PPO4 Data Object"]["Object"].Addresses[0].StartAddress
        outStart = Object.Objects["PPO Type 4_1"]["PPO4 Data Object"]["Object"].Addresses[1].StartAddress
        
        #Create Two Tags For The Drive IN and OUT From Thoses Addresses
        tagManager.addTag(Name+"_In","In","{0}.0".format(inStart),"typeABBACS380InputsPP04","PP04 Inputs For Drive Flags","FMD PPO Tags")
        tagManager.addTag(Name+"_Out","Out","{0}.0".format(outStart),"typeABBACS380OutputsPP04","PP04 Outputs For Drive Control","FMD PPO Tags")
        
        #set values for other things
        self.LAD = True
        self.SCL = False
  
class createScannerSickCLV6xx():
    def __init__(self,project,tagManager,unitName,ip,subnet,zone = ""):
        Name = unitName + " Scanner"
        unitName = unitName + zone
        typeIdentifier = "GSD:GSDML-V2.3-SICK-CLV62XCLV65X_VIA_CDF600-20150312.XML"
        Object = ungroupedDevice(project,typeIdentifier + "/DAP",Name)
        Object.getNetworkInterface(Object.Objects[Name]["Interface"]["Object"])
        Object.setIp(ip,subnet)
        #print(Object)
        Ctrl_Bits_in_1 = Object.Objects["Ctrl Bits in_1"]["Ctrl Bits in"]["Object"].Addresses[0].StartAddress
        Ctrl_Bits_out_1 = Object.Objects["Ctrl Bits out_1"]["Ctrl Bits out"]["Object"].Addresses[0].StartAddress
        Byte_Input_1 = Object.Objects[" 32 Byte Input_1"][" 32 Byte Input"]["Object"].Addresses[0].StartAddress
        Byte_Output_1 = Object.Objects[" 32 Byte Output_1"][" 32 Byte Output"]["Object"].Addresses[0].StartAddress
        if Ctrl_Bits_in_1 != -1 and Ctrl_Bits_out_1 != -1 and Byte_Input_1 != -1 and Byte_Output_1 != -1:
            tagManager.addTag(unitName + "_Scanner_StatusWord","In","{0}.0".format(Ctrl_Bits_in_1),"typeScannerSickStatusInput","Scanner Status Signals","Scanner Tags")
            tagManager.addTag(unitName + "_Scanner_CtrlWord","Out","{0}.0".format(Ctrl_Bits_out_1),"typeScannerSickCtrlOutput","Scanner Ctrl Signals","Scanner Tags")
            tagManager.addTag(unitName + "_Scanner_Data_IN","In","{0}.0".format(Byte_Input_1),"typeScannerSickDataInput","Scanner Data Input","Scanner Tags")
            tagManager.addTag(unitName + "_Scanner_Data_OUT","Out","{0}.0".format(Byte_Output_1),"typeScannerSickDataOutput","Scanner Data Output","Scanner Tags")
        self.LAD = True
        self.SCL = True
        
class createPNPN():
    def __init__(self,project,tagManager,unitName,ip,subnet):
        Name = unitName + " PNPN"
        typeIdentifier = "OrderNumber:6ES7 158-3AD10-0XA0"
        Object = ungroupedDevice(project,typeIdentifier + "/V4.2","PNPN Coupler.X1",Name)
        Object.getNetworkInterface(Object.Objects["PNPN Coupler.X1"]["PROFINET interface X1"]["Object"])
        Object.setIp(ip,subnet)
        self.LAD = False
        self.SCL = False
        
class createConnectionBox():
    def __init__(self,project,tagManager,unitName,ip,subnet):
        Name = unitName + " Connection Box"
        typeIdentifier = "OrderNumber:6AV2 125-2AE23-0AX0"
        Object = ungroupedDevice(project,typeIdentifier + "/V5.2",Name)
        Object.getNetworkInterface(Object.Objects[Name]["SCALANCE interface_1"]["Object"])
        Object.setIp(ip,subnet)
        self.LAD = False
        self.SCL = False
        
class createHMI():
    def __init__(self,project,tagManager,Name,ip,subnet):
        typeIdentifier = "OrderNumber:6AV2 125-2GB23-0AX0"
        Object = groupedDevice(project,typeIdentifier + "/17.0.0.0",Name)
        Object.getNetworkInterface(Object.Objects[Name + ".IE_CP_1"]["PROFINET Interface_1"]["Object"])
        Object.setIp(ip,subnet,False)
        self.LAD = False
        self.SCL = False

class createMOVIMOT():
    def __init__(self,project,tagManager,unitName,ip,subnet):
        Name = unitName + "_MMD"
        typeIdentifier = "GSD:GSDML-V2.25-SEW-MFE52A-20161017-102525.XML"
        Object = ungroupedDevice(project,typeIdentifier + "/DAP/MFE PDEV MRP 3MM",Name)
        Object.deleteModule("Slot not used_3")
        Slot3 = Object.addModule(typeIdentifier + "/M/11","4/6 DI_1",3)
        Object.getNetworkInterface(Object.Objects[Name]["Ethernet Interface"]["Object"])
        Object.setIp(ip,subnet)
        IOin = Object.Objects["4/6 DI_1"]["4/6 DI"]["Object"].Addresses[0].StartAddress
        MM3PDin = Object.Objects["MOVIMOT 3PD_1"]["MOVIMOT 3PD"]["Object"].Addresses[0].StartAddress
        MM3PDout = Object.Objects["MOVIMOT 3PD_1"]["MOVIMOT 3PD"]["Object"].Addresses[1].StartAddress
        if IOin != -1 and MM3PDin != -1 and MM3PDout != -1:
            tagManager.addTag(Name+"_PE","In","{0}.0".format(IOin),"Bool","4/6 DI Input 1","MMD Tags")
            tagManager.addTag(Name+"_In","In","{0}.0".format(MM3PDin),"typeProfinetMoviMotInputs","Input Commands","MMD Tags")
            tagManager.addTag(Name+"_Out","Out","{0}.0".format(MM3PDout),"typeProfinetMoviMotOutputs","Output Flags","MMD Tags")
        self.LAD = False
        self.SCL = False

class createFortressGate():
    def __init__(self,project,tagManager,unitName,ip,subnet):
        Name = unitName + "_GS"
        typeIdentifier = "GSD:GSDML-V2.35-FORTRESS-PROLOK-20190704.XML"
        self.Object = ungroupedDevice(project,typeIdentifier + "/DAP",Name)
        safetyModule = self.Object.addModule(typeIdentifier + "/M/ID_MODULE_F_IO_3DIN1DOUT","Safety Module_1",1)
        io = self.Object.addModule(typeIdentifier + "/M/ID_MODULE_IO","Unsafe IO Data_1",2)
        self.Object.getNetworkInterface(self.Object.Objects[Name]["Interface"]["Object"])
        self.Object.setIp(ip,subnet)
        safetyModuleIn = self.Object.Objects["Safety Module_1"]["Safety Module"]["Object"].Addresses[0].StartAddress
        if safetyModuleIn != -1:
            tagManager.addTag(Name+"_Sol_1","In","{0}.0".format(safetyModuleIn),"Bool","","E Stop Devices")
            tagManager.addTag(Name+"_Sol_2","In","{0}.1".format(safetyModuleIn),"Bool","","E Stop Devices")
            tagManager.addTag(Name+"_Estop_1","In","{0}.4".format(safetyModuleIn),"Bool","","E Stop Devices")
            tagManager.addTag(Name+"_Estop_2","In","{0}.5".format(safetyModuleIn),"Bool","","E Stop Devices")
            
        lampsOut = self.Object.Objects["Unsafe IO Data_1"]["IO Lamps"]["Object"].Addresses[0].StartAddress
        if lampsOut != -1:
            tagManager.addTag(Name+"_ST_LT","Out","{0}.0".format(lampsOut),"Bool","","E Stop Devices")
            tagManager.addTag(Name+"_G_LT","Out","{0}.1".format(lampsOut),"Bool","","E Stop Devices")
            tagManager.addTag(Name+"_ES_LT","Out","{0}.3".format(lampsOut),"Bool","","E Stop Devices")
            tagManager.addTag(Name+"_RQ_LT","Out","{0}.4".format(lampsOut),"Bool","","E Stop Devices")
            tagManager.addTag(Name+"_RS_LT","Out","{0}.5".format(lampsOut),"Bool","","E Stop Devices")
            
        switchesIn = self.Object.Objects["Unsafe IO Data_1"]["IO Switches"]["Object"].Addresses[0].StartAddress
        if switchesIn != -1:
            tagManager.addTag(Name+"_ST_PVB","In","{0}.0".format(switchesIn),"Bool","","E Stop Devices")
            tagManager.addTag(Name+"_G_SW","In","{0}.1".format(switchesIn),"Bool","","E Stop Devices")
            tagManager.addTag(Name+"_RQ_PB","In","{0}.4".format(switchesIn),"Bool","","E Stop Devices")
            tagManager.addTag(Name+"_RS_PB","In","{0}.5".format(switchesIn),"Bool","","E Stop Devices")
            
        solenoidOut = self.Object.Objects["Unsafe IO Data_1"]["Solenoid Drive"]["Object"].Addresses[0].StartAddress
        if solenoidOut != -1:
            tagManager.addTag(Name+"_Sol_Drive","Out","{0}.0".format(solenoidOut),"Bool","","E Stop Devices")
            
        gateIn = self.Object.Objects["Unsafe IO Data_1"]["Gate Monitor"]["Object"].Addresses[0].StartAddress
        if gateIn != -1:
            tagManager.addTag(Name+"_GateMon","In","{0}.0".format(gateIn),"Bool","","E Stop Devices")
            
        solenoidIn = self.Object.Objects["Unsafe IO Data_1"]["Solenoid Monitor"]["Object"].Addresses[0].StartAddress
        if solenoidIn != -1:
            tagManager.addTag(Name+"_SolMon","In","{0}.0".format(solenoidIn),"Bool","","E Stop Devices")
        self.LAD = True
        self.SCL = False
        self.Failsafe_FIODBName = self.Object.Objects["Safety Module_1"]["Safety Module"]["Object"].GetAttribute("Failsafe_FIODBName")

class PLC(GsdDevice):
    def __init__(self,plc):
        super().__init__(plc)
        cpu = plc.DeviceItems[1]
        
        self.software = Siemens.Engineering.IEngineeringServiceProvider(cpu).GetService[Siemens.Engineering.HW.Features.SoftwareContainer]().Software
        
    def setConfig(self):
        cpuHardware = Siemens.Engineering.IEngineeringServiceProvider(cpu).GetService[Siemens.Engineering.HW.Features.PlcAccessLevelProvider]()
        secret = Siemens.Engineering.IEngineeringServiceProvider(cpu).GetService[Siemens.Engineering.HW.Features.PlcMasterSecretConfigurator]()
        secret.Unprotect(System.Security.SecureString("dematic"))
        
        self.CentralFSourceAddress = cpu.GetAttribute("Failsafe_CentralFSourceAddress")
        self.setAttribute("Failsafe_CentralFSourceAddress",System.UInt64(1),cpuHardware)
        self.setAttribute("Failsafe_LowerBoundForFDestinationAddresses",System.UInt64(100),cpuHardware)
        self.setAttribute("Failsafe_UpperBoundForFDestinationAddresses",System.UInt64(199),cpuHardware)
        self.setAttribute("Failsafe_UpperBoundForFDestinationAddresses",System.UInt64(199),cpuHardware)
        self.setAttribute("CycleEnableMinimumCycleTime",System.Boolean(False),cpuHardware)
        self.setAttribute("WebserverActivate",System.Boolean(False),cpuHardware)
        self.setAttribute("ProtectionEnablePutGetCommunication",System.Boolean(False),cpuHardware)
        #Sets Up EST Time Zone
        #self.setAttribute("TimeOfDayActivateDaylightSavingTime",System.Boolean(True),cpuHardware)
        #self.setAttribute("TimeOfDayDaylightSavingTimeOffset",System.UInt64(60),cpuHardware)
        #self.setAttribute("TimeOfDayDaylightSavingTimeStartHour",System.UInt64(2),cpuHardware)
        #self.setAttribute("TimeOfDayDaylightSavingTimeStartMonth",System.UInt64(3),cpuHardware)
        #self.setAttribute("TimeOfDayDaylightSavingTimeStartWeek",System.UInt64(2),cpuHardware)
        #self.setAttribute("TimeOfDayDaylightSavingTimeStartWeekday",System.UInt64(1),cpuHardware)
        self.setAttribute("TimeOfDayLocalTimeZone",System.UInt64(11),cpuHardware)
        #self.setAttribute("TimeOfDayStandardTimeStartHour",System.UInt64(2),cpuHardware)
        #self.setAttribute("TimeOfDayStandardTimeStartMonth",System.UInt64(11),cpuHardware)
        #self.setAttribute("TimeOfDayStandardTimeStartWeek",System.UInt64(1),cpuHardware)
        #self.setAttribute("TimeOfDayStandardTimeStartWeekday",System.UInt64(1),cpuHardware)
        
        opc = cpu.DeviceItems[2]
        opcUaUserManagement = Siemens.Engineering.IEngineeringServiceProvider(opc).GetService[Siemens.Engineering.HW.Features.OpcUaUserManagement]()
        
        
        
        #self.setAttribute("OpcUaMaxMonitoredItems",System.UInt64(50000),opc)
        self.setAttribute("OpcUaSecurityPolicies",System.UInt64(120),opc)
        self.setAttribute("OpcUaGuestAuthentication",System.Boolean(False),opc)
        self.setAttribute("OpcUaPasswordAuthentication",System.Boolean(True),opc)
        
        if opcUaUserManagement.OpcUaUsers.Find("VizUser") == None:
            opcUaUserManagement.OpcUaUsers.Create("VizUser",System.Security.SecureString("&Iconics2022"))
            print("Creating OPC UA User 'VizUser'")
            
        if opcUaUserManagement.OpcUaUsers.Find("LoggingUser") == None:
            opcUaUserManagement.OpcUaUsers.Create("LoggingUser",System.Security.SecureString("&Dematic17"))
            print("Creating OPC UA User 'LoggingUser'")
            
        in1 = cpu.DeviceItems[4]
        #enable NTP
        self.setAttribute("TimeSynchronizationNtp",System.Boolean(True),in1)
        self.setAttribute("TimeSynchronizationServer1",System.String("time.windows.com"),cpuHardware)
        self.setAttribute("TimeSynchronizationUpdateInterval",System.UInt64(3600),cpuHardware)
        
class Pnag(GsdDevice):
    def __init__(self,Device,tagManager):
        super().__init__(Device)
        self.tagManager = tagManager
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
                    
    def createTags(self):
        if self.Circuit1AInAddress != -1 and self.Circuit1AOutAddress != -1 and self.Circuit1BInAddress != -1 and self.Circuit1BInAddress != -1:
            self.tagManager.addTag(self.Device.Name+"1_A_In","In","{0}.0".format(self.Circuit1AInAddress),"typeAsiAIn","{0} Circuit 1A Inputs".format(self.Device.Name),self.Device.Name)
            self.tagManager.addTag(self.Device.Name+"1_A_Out","Out","{0}.0".format(self.Circuit1AOutAddress),"typeAsiAOut","{0} Circuit 1A Outputs".format(self.Device.Name),self.Device.Name)
            self.tagManager.addTag(self.Device.Name+"1_B_In","In","{0}.0".format(self.Circuit1BInAddress),"typeAsiBIn","{0} Circuit 1B Inputs".format(self.Device.Name),self.Device.Name)
            self.tagManager.addTag(self.Device.Name+"1_B_Out","Out","{0}.0".format(self.Circuit1BOutAddress),"typeAsiBOut","{0} Circuit 1B Outputs".format(self.Device.Name),self.Device.Name)
            
        if self.Circuit2AInAddress != -1 and self.Circuit2AOutAddress != -1 and self.Circuit2BInAddress != -1 and self.Circuit2BOutAddress != -1:
            self.tagManager.addTag(self.Device.Name+"2_A_In","In","{0}.0".format(self.Circuit2AInAddress),"typeAsiAIn","{0} Circuit 2A Inputs".format(self.Device.Name),self.Device.Name)
            self.tagManager.addTag(self.Device.Name+"2_A_Out","Out","{0}.0".format(self.Circuit2AOutAddress),"typeAsiAOut","{0} Circuit 2A Outputs".format(self.Device.Name),self.Device.Name)
            self.tagManager.addTag(self.Device.Name+"2_B_In","In","{0}.0".format(self.Circuit2BInAddress),"typeAsiBIn","{0} Circuit 2B Inputs".format(self.Device.Name),self.Device.Name)
            self.tagManager.addTag(self.Device.Name+"2_B_Out","Out","{0}.0".format(self.Circuit2BOutAddress),"typeAsiBOut","{0} Circuit 2B Outputs".format(self.Device.Name),self.Device.Name)
            
        if self.FieldBusBitsAddress != -1:
            self.tagManager.addTag(self.Device.Name+"GlobalFaultReset","Out","{0}.4".format(self.FieldBusBitsAddress),"Bool","{0} ASi Gateway Global Fault Reset".format(self.Device.Name),self.Device.Name)
            
    def addHalfNodeASI(self,name,string):
        split = string.split("_")
        circuit = split[1][-1:]
        node = split[2][:-1]
        AorB = split[2][-1:]
        bitOffSet = split[3][-1:]
        InOrOut = split[3][:-1]
        if InOrOut == "I":
            InOrOut = "In"
        if InOrOut == "O":
            InOrOut = "Out"
        
        self.addHalfNode(name,circuit,node,AorB,bitOffSet,InOrOut)
            
    def addHalfNode(self,name,circuit,node,AorB,bitOffSet,InOrOut):
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
            
            self.tagManager.addTag(name,InOrOut,logicalAddress,"Bool",comment,"AS-i I/O")
        
class object():
    def __init__(self,File = None, WithUserInterface = False):
        if File == None:
            #If no file is given, find a running process and mount it
            self.project = Siemens.Engineering.TiaPortal.GetProcesses()[0].Attach().Projects[0]
        else:
            #If a file is given but the second value is not or is False; Run without UI
            if WithUserInterface == False:
                self.project = Siemens.Engineering.TiaPortal(Siemens.Engineering.TiaPortalMode.WithoutUserInterface).Projects.Open(System.IO.FileInfo(File))
            else:
                self.project = Siemens.Engineering.TiaPortal(Siemens.Engineering.TiaPortalMode.WithUserInterface).Projects.Open(System.IO.FileInfo(File))
                        
        #Get PLC and create the software interface
        for x in self.project.Devices:
            if x.TypeIdentifier != None:
                if 'S71500' in x.TypeIdentifier:
                    self.PLC = PLC(x)
                    break
                    
        try:
            self.PLC
        except AttributeError:
            print("No PLC Detected")
            quit()
                    
        #Get Subnet for PLC Network
        if self.project.Subnets.Count > 0:
            self.subnet = self.project.Subnets[0]
        else:
            print("ERROR: No Subnet Detected")
            quit()
            
        #Create Tag Manager
        self.tags = tagManager(self.PLC.software)
        
        #Fine All AS-i Gateways
        self.networkDevice = {}
        for x in self.project.Devices:
            if x.TypeIdentifier != None:
                if "BIHL UND WIEDEMANN-ASI GATEWAY" in x.TypeIdentifier:
                    self.networkDevice[x.Name[-1:]] = Pnag(x,self.tags)
        """
        for x in self.project.UngroupedDevicesGroup.Devices:
            if x.TypeIdentifier != None:
                if "FORTRESS" in x.TypeIdentifier:
                    gate = GsdDevice(x)
                    print(gate)
                    print(gate.Name)
                    print(gate.Objects["Safety Module_1"]["Safety Module"]["Object"].GetAttribute("Failsafe_FIODBName"))
                    
        """
        
        
        #name = ["U253510","U253310","U253110","U252910","U252710","U252510","U252310","U252110","U251910"]
        #ip = ["172.16.111.201","172.16.111.202","172.16.111.203","172.16.111.204","172.16.111.205","172.16.111.206","172.16.111.207","172.16.111.208","172.16.111.209"]
        #type = ["FortressGate","FortressGate","FortressGate","FortressGate","FortressGate","FortressGate","FortressGate","FortressGate","FortressGate"]
        #self.spawnUngroupedDevice(name,type,ip)
        
        #name = ["U253510","U253430","U253310","U253230","U253110","U253030","U252910","U252830","U252710","U252630","U252510","U252430","U252310","U252230","U252110","U252030","U251910","U251830"]
        #ip = ["172.16.111.51","172.16.111.52","172.16.111.53","172.16.111.54","172.16.111.55","172.16.111.56","172.16.111.57","172.16.111.58","172.16.111.59","172.16.111.60","172.16.111.61","172.16.111.62","172.16.111.63","172.16.111.64","172.16.111.65","172.16.111.66","172.16.111.67","172.16.111.68"]
        #type = []
        #for x in name:
        #    type.append("ScannerSickCLV6xx")
        #self.spawnDevice("Import",name,type,ip)
        
        #name = ["BT253500","BT253505","BT253300","BT253305","BT253100","BT253105","BT252900","BT252905","BT252700","BT252705","BT252500","BT252505","BT252300","BT252305","BT252100","BT252105","BT251900","BT251905"]
        #ip = ["172.16.111.151","172.16.111.152","172.16.111.153","172.16.111.154","172.16.111.155","172.16.111.156","172.16.111.157","172.16.111.158","172.16.111.159","172.16.111.160","172.16.111.161","172.16.111.162","172.16.111.163","172.16.111.164","172.16.111.165","172.16.111.166","172.16.111.167","172.16.111.168"]
        #type = []
        #for x in name:
        #    type.append("MOVIMOT")
        #self.spawnDevice("Import",name,type,ip)
        
        
        #self.PLC.software
        """
        import re
        for x in sw.BlockGroup.Groups.Find("Project").Groups:
            if "CA111_Line" in x.Name:
                for y in x.Blocks:
                    if y.ToString() == "Siemens.Engineering.SW.Blocks.FC":
                        if y.GetAttribute("ProgrammingLanguage") == Siemens.Engineering.SW.Blocks.ProgrammingLanguage.LAD:
                            y.Export(System.IO.FileInfo("C:/Users/leonarjd/OneDrive - dematic.com/Desktop/New folder/" + y.Name),Siemens.Engineering.ImportOptions.Override)
        """
        
        #print(minidom.parseString(ET.tostring(y)).toprettyxml(indent = "\t"))
        #y.SetAttribute("Name","{0}U{1}_E_{2}".format(split[0],split[1],split[2]))
        #match = re.search("^InstOR[0-9]{6}|^InstSB[0-9]{6}",y.Name)
        #split = re.split("[A-Z]{2}|_",y.Name)
        self.spawnAsiDevice([],[],[])
        #self.test()
        #self.addHalfNodeASI("CA111_EZC01_CR_ESM","ASI_A1_12A_I2")
        #networkDevice["C"].addHalfNode("BT251855_PE_P",1,8,"A",1,"In") 
        
    def addHalfNodeASI(self,name,string):
        split = string.split("_")
        self.networkDevice[split[1][0:1]].addHalfNodeASI(name,string)
        
    def spawnDevice(self,Line,Name,Type,Address):
        import shutil
        import re
        import ipaddress
        fileStr = os.getcwd() + "/" + Line
        if os.path.exists(Line):
            shutil.rmtree(fileStr)
        os.mkdir(Line)
        xml = xmlHeader(Line,Line)
        ObjectList = xml.ObjectList
        scl = SclObject(Line + "_SetConfigs",Line)
        blockGroup = self.PLC.software.BlockGroup.Groups.Find("Project").Groups.Find(Line)
        if blockGroup != None:
            blockGroup.Delete()
        software = self.PLC.software.BlockGroup.Groups.Find("Project").Groups.Create(Line)
        """
        for x in Address:
            try:
                ipaddress.ip_address(x)
            except ValueError:
                if not(re.search(""))
        """
        
        for x in range(len(Name)):
            if Type[x] == "AbbAcs380Drive":
                #createAbbAcs380Drive(self.project,self.tags,Name[x],Address[x],self.subnet)
                XML_Objects.AbbAcs380Drive(Name[x],ObjectList,scl)
                
            elif Type[x] == "AsiABBDriveNAType01":
                XML_Objects.AsiABBDriveNAType01(Name[x],ObjectList,scl)
                
            elif Type[x] == "ScannerSickCLV6xx":
                createScannerSickCLV6xx(self.project,self.tags,Name[x],Address[x],self.subnet)
                if Name[x][-2:] == "10":
                    XML_Objects.ScannerSickCLV6xx(Name[x],ObjectList,scl,"_E_Z4")
                    
                if Name[x][-2:] == "30":
                    XML_Objects.ScannerSickCLV6xx(Name[x],ObjectList,scl,"_E_Z2")
                
            elif Type[x] == "FortressGate":
                gate = createFortressGate(self.project,self.tags,Name[x],Address[x],self.subnet)
                XML_Objects.FortressGate(Name[x],gate.Failsafe_FIODBName,ObjectList,scl)
                
            elif Type[x] == "MOVIMOT":
                #createMOVIMOT(self.project,self.tags,Name[x],Address[x],self.subnet)
                XML_Objects.MoviMot(Name[x],ObjectList,scl)
                #Find and create block for this
                
            elif Type[x] == "HMI":
                createHMI(self.project,self.tags,Name[x],Ip[x],self.subnet)
                #Find and create block for this
                
            elif Type[x] == "ConnectionBox":
                createConnectionBox(self.project,self.tags,Name[x],Ip[x],self.subnet)
                #Find and create block for thiscreate
                
            elif Type[x] == "PNPN":
                createPNPN(self.project,self.tags,Name[x],Ip[x],self.subnet)
                #Find and create block for thiscreate
                
        XML_Objects.CallSetConfig(Line + "_SetConfigs", ObjectList)
        xml.save()
        scl.save()
        for x in os.listdir(fileStr):
            software.Blocks.Import(System.IO.FileInfo(fileStr + "/" +x),Siemens.Engineering.ImportOptions.Override) 
    
    def spawnAsiDevice(self,Name,Type,Asi):
        import shutil
        Line = "Import"
        fileStr = os.getcwd() + "/" + Line
        if os.path.exists(Line):
            shutil.rmtree(fileStr)
        os.mkdir(Line)
        xml = xmlHeader(Line,Line)
        ObjectList = xml.ObjectList
        scl = SclObject(Line + "_SetConfigs",Line)
        blockGroup = self.PLC.software.BlockGroup.Groups.Find("Project").Groups.Find(Line)
        if blockGroup != None:
            blockGroup.Delete()
        software = self.PLC.software.BlockGroup.Groups.Find("Project").Groups.Create(Line)
        
        CabnetNumber = "CC110"
        ControlArea = "CA111"
        EZCName = ["EZC01","EZC02","EZC03","EZC04","EZC05","EZC06","EZC07","EZC08","EZC09"]
        Dps = [["DPS01","DPS02"],["DPS03","DPS04"],["DPS05","DPS06"],["DPS07","DPS08"],["DPS09","DPS10"],["DPS11","DPS12"],["DPS13","DPS14"],["DPS15","DPS16"],["DPS17","DPS18"]]
        Aux = [[],[],[],[],[],[],[],[],[]]
        Pnag = ["U253110_PNAG_A","U252310_PNAG_B","U251910_PNAG_C"]
        Pncg = ["U253045_ECG_01","U252245_ECG_02","U251845_ECG_03"]
        Estops = [["U253430_PC_ES","U253450_PC_ES","U253530_PB_ES1","U253530_PB_ES2","U253530_PC_ES"],["U253230_PC_ES","U253250_PC_ES","U253330_PB_ES1","U253330_PB_ES2"],["U253030_PC_ES","U253050_PC_ES","U253130_PB_ES1","U253130_PB_ES2"],["U252830_PC_ES","U252850_PC_ES","U252930_PB_ES1","U252930_PB_ES2"],["U252630_PC_ES","U252650_PC_ES","U252730_PB_ES1","U252730_PB_ES2"],["U252430_PC_ES","U252450_PC_ES","U252530_PB_ES1","U252530_PB_ES2"],["U252230_PC_ES","U252250_PC_ES","U252330_PB_ES1","U252330_PB_ES2"],["U252030_PC_ES","U252050_PC_ES","U252130_PB_ES1","U252130_PB_ES2"],["U251830_PC_ES","U251850_PC_ES","U251930_PB_ES1","U251930_PB_ES2"]]
        EstopsAsi = [["ASI_A1_22","ASI_A1_23","ASI_A1_27","ASI_A1_26","ASI_A1_19"],["ASI_A1_21","ASI_A1_20","ASI_A1_25","ASI_A1_24"],["ASI_A2_20","ASI_A2_23","ASI_A2_27","ASI_A2_26"],["ASI_A2_22","ASI_A2_21","ASI_A2_25","ASI_A2_24"],["ASI_B1_22","ASI_B1_23","ASI_B1_27","ASI_B1_26"],["ASI_B1_20","ASI_B1_21","ASI_B1_25","ASI_B1_24"],["ASI_B2_22","ASI_B2_23","ASI_B2_27","ASI_B2_26"],["ASI_B2_20","ASI_B2_21","ASI_B2_25","ASI_B2_24"],["ASI_C1_25","ASI_C1_26","ASI_C1_28","ASI_C1_27"]]

        
        
        XML_Objects.Area(CabnetNumber,ControlArea,EZCName,Dps,Aux,Pnag,Pncg,Estops,EstopsAsi,ObjectList,scl)
        #XML_Objects.Test(ObjectList)
        
        for x in range(len(Name)):
            networkDevice = Asi[x].split("_")[1][:1]
            circuit = Asi[x].split("_")[1][1:]
            node = Asi[x].split("_")[2][:-1]
            AorB = Asi[x].split("_")[2][-1:]
            inAsiBusFault = 'Inst{0}.outFaultGWChn{1}{2}[{3}]'.format(self.networkDevice[networkDevice].Device.Name,str(int(circuit) - 1),AorB,node)
            if Type[x] == "EStopVis":
                node = Asi[x].split("_")[2]
                #inAsiBusFault = 'Inst{0}.outVisuInterface.status.summary'.format(self.networkDevice[networkDevice].Device.Name)
                block = XML_Objects.EStopVis(self.networkDevice[networkDevice].Device.Name,Name[x],ObjectList,scl)
                instanceDB = software.Blocks.CreateInstanceDB(block.Component.get('Name'),True,1,block.CallInfo.get("Name"))
                self.networkDevice[networkDevice].addHalfNode(Name[x] + "_NONSAFE",circuit,node,"A",1,"In")
                self.networkDevice[networkDevice].addHalfNode(Name[x] + "_LT_R",circuit,node,"A",1,"Out")
                self.networkDevice[networkDevice].addHalfNode(Name[x] + "_LT_G",circuit,node,"A",2,"Out")
        
        XML_Objects.CallSetConfig(Line + "_SetConfigs", ObjectList)
        xml.save()
        scl.save()
        for x in os.listdir(fileStr):
            software.Blocks.Import(System.IO.FileInfo(fileStr + "/" +x),Siemens.Engineering.ImportOptions.Override)
    
    def UpdateUngroupedDevicesGroupsDic(self):
        self.UngroupedDevicesGroupsDic = {}
        for x in self.project.UngroupedDevicesGroup.Devices:
            self.UngroupedDevicesGroupsDic[x.Name] = x
        print(self.UngroupedDevicesGroupsDic)
        
    def test(self):
        name = ["U000000","U000010","U000020","U000030","U000040","U000050","U000060"]
        type = ["AbbAcs380Drive","ScannerSickCLV62x","PNPN","ConnectionBox","HMI","MOVIMOT","FortressGateSwitch"]
        ip = ["172.16.111.254","172.16.111.253","172.16.111.252","172.16.111.251","172.16.111.250","172.16.111.239","172.16.111.238"]
        self.spawnUngroupedDevice(name,type,ip)
        
    def Cax(self):
        self.cax = Siemens.Engineering.IEngineeringServiceProvider(self.project).GetService[Siemens.Engineering.Cax.CaxProvider]()
        #self.cax.Export(self.project,System.IO.FileInfo("C:/Users/leonarjd/OneDrive - dematic.com/Desktop/Test.aml"),System.IO.FileInfo("C:/Users/leonarjd/OneDrive - dematic.com/Desktop/log.log"))
        device = self.project.UngroupedDevicesGroup.Devices.Find("U000000_FMD")
        self.cax.Export(device,System.IO.FileInfo("C:/Users/leonarjd/OneDrive - dematic.com/Desktop/Test.aml"),System.IO.FileInfo("C:/Users/leonarjd/OneDrive - dematic.com/Desktop/log.log"))
    
    
    
def main():
    #File = "C:/Users/leonarjd/OneDrive - dematic.com/Desktop/Blank Slate/Blank Slate.ap17"
    test = object()
    
main()
quit()

"""
import clr
import System
clr.AddReference('C:\\Program Files\\Siemens\\Automation\\Portal V17\PublicAPI\\V17\\Siemens.Engineering.dll')
import Siemens.Engineering
project = Siemens.Engineering.TiaPortal.GetProcesses()[0].Attach().Projects[0]
for x in project.Devices:
    if x.TypeIdentifier != None:
            if 'S71500' in x.TypeIdentifier:
                    cpu = x.DeviceItems[1]
sw = Siemens.Engineering.IEngineeringServiceProvider(cpu).GetService[Siemens.Engineering.HW.Features.SoftwareContainer]().Software
line_1 = SW.BlockGroup.Groups.Find("Project").Groups.Find("CA111_Line_1")
line_1_FC = line_1.Blocks.Find("CA111_Line_1")

"""