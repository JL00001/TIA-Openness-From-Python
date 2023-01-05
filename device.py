
import anytree
import Siemens.Engineering
import System

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
