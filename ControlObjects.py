import clr
clr.AddReference('C:\\Program Files\\Siemens\\Automation\\Portal V17\PublicAPI\\V17\\Siemens.Engineering.dll')
import Siemens.Engineering
import System
import os
import re

import device
import xmlHeader
import sclObject
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
                            "Pnag":[],
                            "Pncg":[],
                            "dpsBoxObject":[],
                            "auxBoxObject":[],
                            "asiEstopObject":[],
                            "rptrObject":[],
                            "AbbAcs380DriveObject":[],
                            "MoviMotObject":[],
                            "FortressGateobject":[],
                            "ScannerSickCLV6xxObject":[],
                            "ConnectionBoxObject":[],
                            "PnpnObject":[],
                            "HmiObject":[],
                            }
        self.__getProjectVariables()
        self.__setUpImportVariables()
        
    def __getProjectVariables(self):
        #Project
        self.project = self.project = Siemens.Engineering.TiaPortal.GetProcesses()[0].Attach().Projects[0]
        
        #Software
        for x in self.project.Devices:
            if x.TypeIdentifier != None and 'S71500' in x.TypeIdentifier:
                GsdDevice = device.GsdDevice(x)
                break
        self.software = Siemens.Engineering.IEngineeringServiceProvider(GsdDevice.Device.DeviceItems[1]).GetService[Siemens.Engineering.HW.Features.SoftwareContainer]().Software
        
        #Tags
        self.tags = device.tags(self.software)
        
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
        self.export()
        for x in self.dataSorted.keys():
            if len(self.dataSorted[x]) > 0:
                for y in sorted(self.dataSorted[x], key=lambda x: x.name.lower()):
                    y.export()
        CallSetConfigObject(self.scl.Name,self.xml.ObjectList)
        self.xml.save()
        self.blockGroupSw.Blocks.Import(System.IO.FileInfo("{0}/{1}.xml".format(os.getcwd(),self.xml.Name)),Siemens.Engineering.ImportOptions.Override)
        
        self.scl.save()
        self.blockGroupSw.Blocks.Import(System.IO.FileInfo("{0}/{1}.xml".format(os.getcwd(),self.scl.Name)),Siemens.Engineering.ImportOptions.Override)
        self._genDefaultDBs()
        
        self.DataToSafety.save()
        self.DataFromSafety.save()        
        self.dbPncgParameterData.save()
        
        ICompilable = Siemens.Engineering.IEngineeringServiceProvider(self.software.BlockGroup.Groups.Find("Project").Groups.Find("DefaultDBs")).GetService[Siemens.Engineering.Compiler.ICompilable]()
        #ICompilable.Compile()
            
    def export(self):
        XmlExport = swBlock.swBlock(self.xml.ObjectList)
        
        XmlExport.addCall()
        XmlExport.Comment.text = self.name
        XmlExport.addEN(XmlExport.CallId,"en")
        XmlExport.Component.set("Name","Inst" + self.name)
        XmlExport.CallInfo.set("Name","PlcNA")
        
        XmlExport.loadParameterStr('<Parameter Name="inWcsCommsHealthy" Section="Input" Type="Bool" />',"InstDciManager.outConnected")
        XmlExport.loadParameterStr('<Parameter Name="inSafetyStatusToPlc" Section="Input" Type="&quot;typeSafetyStatusToMainPanel&quot;" />',"DataFromSafety.SafetyStatusToPLC")
        XmlExport.loadParameterStr('<Parameter Name="inInternal24VOk" Section="Input" Type="Bool" />',"{0}_PWR_ON".format(self.name))
        XmlExport.loadParameterStr('<Parameter Name="inPBLampTest" Section="Input" Type="Bool" />',"{0}_PWR_ON".format(self.name))
        XmlExport.loadParameterStr('<Parameter Name="outLampStarted" Section="Output" Type="Bool" />',"{0}_LT_ST".format(self.name))
        XmlExport.loadParameterStr('<Parameter Name="outLampGeneralFault" Section="Output" Type="Bool" />',"{0}_LT_J".format(self.name))
        XmlExport.loadParameterStr('<Parameter Name="outLampEmergencyStop" Section="Output" Type="Bool" />',"{0}_LT_ES".format(self.name))
        XmlExport.loadParameterStr('<Parameter Name="outLampMotorFault" Section="Output" Type="Bool" />',"{0}_LT_MF".format(self.name))
        XmlExport.loadParameterStr('<Parameter Name="outLampHostCommFault" Section="Output" Type="Bool" />',"{0}_LT_HOST".format(self.name))
        XmlExport.loadParameterStr('<Parameter Name="outLampLowAirFault" Section="Output" Type="Bool" />',"{0}_LT_AIR".format(self.name))
        
        if len(self.dataSorted['ezcObject']) > 0:
            listAllPowerGroupsZoneStarted = []
            listFault = []
            listPowerGroupZoneStarted = []
            listStartWarning = []
            for x in self.dataSorted['ezcObject']:
                listAllPowerGroupsZoneStarted.append("Inst{0}.outEzcToMainPanel.allPowerGroupsZoneStarted".format(x.name))
                listFault.append("Inst{0}.outEzcToMainPanel.fault".format(x.name))
                listPowerGroupZoneStarted.append("Inst{0}.outEzcToMainPanel.powerGroupZoneStarted".format(x.name))
                listStartWarning.append("Inst{0}.outEzcToMainPanel.startWarning".format(x.name))
                
            XmlExport.ANDspawn(listAllPowerGroupsZoneStarted,"Inst{0}.inEzcToPlc.allPowerGroupsZoneStarted".format(self.name))
            XmlExport.NANDspawn(listFault,"Inst{0}.inEzcToPlc.fault".format(self.name))
            XmlExport.NANDspawn(listPowerGroupZoneStarted,"Inst{0}.inEzcToPlc.powerGroupZoneStarted".format(self.name))
            XmlExport.NANDspawn(listStartWarning,"Inst{0}.inEzcToPlc.startWarning".format(self.name))
            
        if len(self.dataSorted['Pnag']) > 0:
            listPnagFault = []
            for x in self.dataSorted['Pnag']:
                listPnagFault.append("Inst{0}.outPnagFaultToPlc".format(x.name))
                
            XmlExport.NANDspawn(listPnagFault,"Inst{0}.inPnagFaultToPlc".format(self.name))
        
        if self.scl != None:
            #SCL ConFig
            self.scl.addRegion(XmlExport.Component.get("Name"))
            self.scl.GlobalVariableEqualBool(XmlExport.Component.get("Name") + ".inConfig.resetConveyorsFromPanel",True)
            self.scl.GlobalVariableEqualBool(XmlExport.Component.get("Name") + ".inConfig.disableCompressedAirAlarm",False)
            self.scl.endRegion()
            
        if self.blockGroupSw != None:
            self.blockGroupSw.Blocks.CreateInstanceDB(XmlExport.Component.get('Name'),True,1,XmlExport.CallInfo.get("Name"))
            
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
                self.plcObject = plcObject(x,self)
                #self.plcObject.setConfig()
                break
            
    def addAbbAcs380Drive(self,unitNumber,ip,zone=""):
        if unitNumber not in self.data.keys():
            object = AbbAcs380DriveObject(unitNumber,self,ip,zone)
            self.data[object.name] = object.name
            self.dataSorted["AbbAcs380DriveObject"].append(object)
            return object
            
        else:
            raise NameError("A Device Already Has That Name")
            
    def addScannerSickCLV6xx(self,unitNumber,ip,zone="",genHardware=True):
        if unitNumber not in self.data.keys():
            object = ScannerSickCLV6xxObject(unitNumber,self,ip,zone,genHardware)
            self.data[object.name] = object.name
            self.dataSorted["ScannerSickCLV6xxObject"].append(object)
            return object
            
        else:
            raise NameError("A Device Already Has That Name")
            
    def addPnpn(self,unitNumber,ip,zone=""):
        if unitNumber not in self.data.keys():
            object = PnpnObject(unitNumber,self,ip,zone)
            self.data[object.name] = object.name
            self.dataSorted["PnpnObject"].append(object)
            return object
            
        else:
            raise NameError("A Device Already Has That Name")
            
    def addConnectionBox(self,unitNumber,ip,zone=""):
        if unitNumber not in self.data.keys():
            if re.search("U[0-9]{6}_Conn_Box_[0-9]{1}",unitNumber) != None:
                object = ConnectionBoxObject(unitNumber,self,ip,zone)
                self.data[object.name] = object.name
                self.dataSorted["ConnectionBoxObject"].append(object)
                return object
                
            else:
                raise NameError("Improper Connection Box Name Format")
            
        else:
            raise NameError("A Device Already Has That Name")
            
    def addHmi(self,name,ip,zone=""):
        if name not in self.data.keys():
            object = HmiObject(name,self,ip,zone)
            self.data[object.name] = object.name
            self.dataSorted["HmiObject"].append(object)
            return object
            
        else:
            raise NameError("A Device Already Has That Name")
        
    def addMoviMot(self,unitNumber,ip,zone=""):
        if unitNumber not in self.data.keys():
            object = MoviMotObject(unitNumber,self,ip,zone)
            self.data[object.name] = object.name
            self.dataSorted["MoviMotObject"].append(object)
            return object
            
        else:
            raise NameError("A Device Already Has That Name")
            
    def addFortressGate(self,unitNumber,ip,zone=""):
        if unitNumber not in self.data.keys():
            object = FortressGateObject(unitNumber,self,ip,zone)
            self.data[object.name] = object
            self.dataSorted["FortressGateobject"].append(object)
            return object
            
        else:
            raise NameError("A Device Already Has That Name")
            
    def spawnTestDevices(self):
        try:
            self.project.UngroupedDevicesGroup.Devices.Find("U000000_FMD").Delete()
        except:
            pass
        try:
            self.project.UngroupedDevicesGroup.Devices.Find("U000010_SC").Delete()
        except:
            pass
        try:
            self.project.UngroupedDevicesGroup.Devices.Find("U000020_PNPN").Delete()
        except:
            pass
        try:
            self.project.UngroupedDevicesGroup.Devices.Find("U000030_Conn_Box_1").Delete()
        except:
            pass
        try:
            self.project.UngroupedDevicesGroup.Devices.Find("U000050_MMD").Delete()
        except:
            pass
        try:
            self.project.UngroupedDevicesGroup.Devices.Find("U000060_GS").Delete()
        except:
            pass
        self.addAbbAcs380Drive("U000000","172.16.210.66")
        self.addScannerSickCLV6xx("U000010","172.16.210.67")
        self.addPnpn("U000020","172.16.210.68")
        self.addConnectionBox("U000030_Conn_Box_1","172.16.210.69")
        #self.addHmi("U000040","172.16.210.70")
        self.addMoviMot("U000050","172.16.210.71")
        self.addFortressGate("U000060","172.16.210.72")
        
    def spawnTestPanels(self):
        ca = self.createControlArea("CA121")
        ca.adoptNetworkDevice("U251910_PNAG_C")
        ca.adoptNetworkDevice("U251845_PNCG_03")
        ezc = ca.addEzc("ASI_C1_01A")
        estop1 = ezc.addAsiEstop("EStop1","ASI_C1_29")
        aux1 = ezc.addAuxBox("ASI_C1_01A_I2")
        dps1 = ezc.addDpsBox("ASI_C1_01A_I4")
        rptr1 = ezc.addRptrBox("ASI_C1")
            
    def testAll(self):
        self.spawnTestDevices()
        self.spawnTestPanels()
            
class controlAreaObject(father):
    def __init__(self,name,parent):
        super(controlAreaObject,self).__init__(name,parent)
        self.allNetworkDevices = parent.networkDevices
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
            print("Device : {0} Not Found. \nAvailable options are \n {1}".format(objectName,"\n ".join(list(self.parent.networkDevices.keys()))))
            raise KeyError("See Above Printout")
        
    def addEzc(self,asiAddress):
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
        
    def export(self):
        pass
        
class plcObject(device.GsdDevice):
    def __init__(self,Plc,parent):
        super().__init__(Plc)
        self.name = parent.name
        self.tags = parent.tags
        self.cpu = Plc.DeviceItems[1]
        if "20000PLC" in self.Objects.keys():
            self.localInputAddress = self.Objects["20000PLC"]["20000PLC"]["Object"].Addresses[0].StartAddress
        else:
            print("line399")
            quit()
        self.localOutputAddress = self.Objects["21000PLC"]["21000PLC"]["Object"].Addresses[0].StartAddress
        
        self.tags.addTag("{0}_PB_TEST".format(self.name),"In","{0}.0".format(self.localInputAddress),"Bool","Lamp Test","Control Panel IO")
        self.tags.addTag("{0}_PWR_ON".format(self.name),"In","{0}.1".format(self.localInputAddress),"Bool","Control Cabinet Power On","Control Panel IO")
        self.tags.addTag("{0}_DC_OK".format(self.name),"In","{0}.2".format(self.localInputAddress),"Bool","Control Cabinet DC Power OK","Control Panel IO")
        self.tags.addTag("{0}_FIRE".format(self.name),"In","{0}.3".format(self.localInputAddress),"Bool","Fire Alarm OK","Control Panel IO")
        
        self.tags.addTag("{0}_LT_ST".format(self.name),"Out","{0}.0".format(self.localOutputAddress),"Bool","Started Light","Control Panel IO")
        self.tags.addTag("{0}_LT_MF".format(self.name),"Out","{0}.1".format(self.localOutputAddress),"Bool","Motor Fault Light","Control Panel IO")
        self.tags.addTag("{0}_LT_J".format(self.name),"Out","{0}.2".format(self.localOutputAddress),"Bool","Jam Fault Light","Control Panel IO")
        self.tags.addTag("{0}_LT_AIR".format(self.name),"Out","{0}.3".format(self.localOutputAddress),"Bool","Low Air Light","Control Panel IO")
        self.tags.addTag("{0}_LT_ES".format(self.name),"Out","{0}.4".format(self.localOutputAddress),"Bool","E-Stop Actuated Light","Control Panel IO")
        self.tags.addTag("{0}_LT_HOST".format(self.name),"Out","{0}.5".format(self.localOutputAddress),"Bool","Host Communication Fault Light","Control Panel IO")
        
    def setConfig(self):
        self.checkIECV22LLDPMode(self.Objects[self.cpu.Name]["PROFINET interface_1"]["Object"])
        self.checkIECV22LLDPMode(self.Objects[self.cpu.Name]["PROFINET interface_2"]["Object"])
        
        cpuHardware = Siemens.Engineering.IEngineeringServiceProvider(self.cpu).GetService[Siemens.Engineering.HW.Features.PlcAccessLevelProvider]()
        
        self.CentralFSourceAddress = self.cpu.GetAttribute("Failsafe_CentralFSourceAddress")
        self.testThenSetAttribute("Failsafe_CentralFSourceAddress",System.UInt64(1),cpuHardware)
        self.testThenSetAttribute("Failsafe_LowerBoundForFDestinationAddresses",System.UInt64(100),cpuHardware)
        self.testThenSetAttribute("Failsafe_UpperBoundForFDestinationAddresses",System.UInt64(199),cpuHardware)
        self.testThenSetAttribute("CycleMaximumCycleTime",System.UInt64(1000),cpuHardware)
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
        
class Pnag(device.GsdDevice):
    def __init__(self,Device,parent):
        super().__init__(Device)
        self.tags = parent.tags
        self.contolCabnet = parent.contolCabnet
        self.name = self.Device.Name
        self.xml = parent.xml
        self.scl = parent.scl
        self.software = parent.software
        self.allNetworkDevices = parent.allNetworkDevices
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
        
        self.PROFIsafeAdress = str(self.Objects["8 Byte PROFIsafe data"]["8 Byte PROFIsafe data"]["Object"].Addresses[0].StartAddress)
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
        XmlExport = swBlock.swBlock(self.xml.ObjectList)
        XmlExport.addCall()
        blockA = XmlExport.CallId
        XmlExport.Comment.text = self.name
        XmlExport.addEN(XmlExport.CallId,"en")
        XmlExport.Component.set("Name","Inst" + self.name + "_Health")
        XmlExport.CallInfo.set("Name","ProfinetDeviceHealthSelector")
        XmlExport.loadParameterStr('<Parameter Name="inData" Section="Input" Type="&quot;typeProfinetDeviceHealth&quot;"/>',"ProfinetDeviceHealth_DB.outData")
        XmlExport.loadParameterStr('<Parameter Name="inLADDR" Section="Input" Type="HW_INTERFACE"/>',self.name + "~PN-IO")
        if self.software != None:
            self.software.Blocks.CreateInstanceDB(XmlExport.Component.get('Name'),True,1,XmlExport.CallInfo.get("Name"))
        
        XmlExport.addCall()
        XmlExport.Component.set("Name","Inst" + self.name)
        XmlExport.CallInfo.set("Name","PnagBox")
        XmlExport.addParameter("inAsiGatewayBusFault","Input","Bool")
        XmlExport.loadParameterStr('<Parameter Name="inMainPanelToPnag" Section="Input" Type="Bool"/>','Inst' + self.contolCabnet + '.outPlcStatus')
        XmlExport.loadParameterStr('<Parameter Name="inAsiCmdReceive" Section="Input" Type="&quot;typeAsiCommandReceive&quot;"/>',self.name + 'CommandIn')
        XmlExport.loadParameterStr('<Parameter Name="inFlagsChn0" Section="Input" Type="&quot;typeAsiChannelFlags&quot;"/>',self.name + 'FlagsChn0')
        XmlExport.loadParameterStr('<Parameter Name="inFlagsChn1" Section="Input" Type="&quot;typeAsiChannelFlags&quot;"/>',self.name + 'FlagsChn1')
        XmlExport.loadParameterStr('<Parameter Name="outAsiCmdSend" Section="Output" Type="&quot;typeAsiCommandSend&quot;"/>',self.name + 'CommandOut')
        XmlExport.loadParameterStr('<Parameter Name="outGlobalFaultReset" Section="Output" Type="Bool"/>', self.name + "GlobalFaultReset")
                
        XmlExport.addConnection(blockA,"eno",XmlExport.CallId,"en")
        
        listConnected = []
        listConnected.append("Inst" + self.name + "_Health.outFaultSumm")
        listConnected.append("{0}FlagsChn0.noNormalOperation".format(self.name))
        listConnected.append("{0}FlagsChn1.noNormalOperation".format(self.name))
        
        XmlExport.OR(listConnected,XmlExport.CallId,"inAsiGatewayBusFault")
        
        if self.scl != None:
            #SCL ConFig
            self.scl.addRegion(XmlExport.Component.get("Name"))
            self.scl.GlobalVariableEqualLiteralConstant(XmlExport.Component.get("Name") + ".inConfig.pnagName", self.name[-6:])
            self.scl.GlobalVariableEqualBool(XmlExport.Component.get("Name") + ".inConfig.asiGatewayDiag.enableChn0",True)
            self.scl.GlobalVariableEqualBool(XmlExport.Component.get("Name") + ".inConfig.asiGatewayDiag.enableChn1",True)
            self.scl.GlobalVariableEqualBool(XmlExport.Component.get("Name") + ".inConfig.panelMask", '2#0000_0000_0000_0000_0000_0000_0000_0001')
            self.scl.endRegion()
            
        if self.software != None:
            self.software.Blocks.CreateInstanceDB(XmlExport.Component.get('Name'),True,1,XmlExport.CallInfo.get("Name"))
        
class Pncg(device.GsdDevice):
    def __init__(self,Device,parent):
        super().__init__(Device)
        self.tags = parent.tags
        self.contolCabnet = parent.contolCabnet
        self.name = self.Device.Name
        self.xml = parent.xml
        self.scl = parent.scl
        self.software = parent.software
        self.allNetworkDevices = parent.allNetworkDevices
        self.connectedDps = {
                                "1":[],
                                "2":[],
                                "3":[],
                                "4":[],
                                "5":[],
                                "6":[]
                            }
        self.createTags()
        
    def createTags(self):
        self.CANChannelIn = self.Objects["CAN Channel Module_1"]["CAN Channel Submodule"]["Object"].Addresses[0].StartAddress
        self.CANChannelOut = self.Objects["CAN Channel Module_1"]["CAN Channel Submodule"]["Object"].Addresses[1].StartAddress
        self.tags.addTag(self.Device.Name+"CANChannelIn","In","{0}.0".format(self.CANChannelIn),"Bool","{0} CAN Channel Input".format(self.Device.Name),self.Device.Name,True)
        self.tags.addTag(self.Device.Name+"CANChannelOut","Out","{0}.0".format(self.CANChannelOut),"Bool","{0} CAN Channel Output".format(self.Device.Name),self.Device.Name,True)
        for x in range(1,7):
            if "Command Module_{0}".format(x) not in self.Objects:
                newSlot = self.addModule("GSD:GSDML-V2.33-DEMATIC-PNCG-20171211.XML/M/Command","Command Module_{0}".format(str(x)))
                inAddress = newSlot.DeviceItems[0].Addresses[0].StartAddress
                outAddress = newSlot.DeviceItems[0].Addresses[1].StartAddress
                self.tags.addTag("{0}CmdArea{1}In".format(self.Device.Name,str(x)),"In","{0}.0".format(inAddress),"typeCommandAreaInput","{0} Command Area {1} Input".format(self.Device.Name,str(x)),self.Device.Name,True)
                self.tags.addTag("{0}CmdArea{1}Out".format(self.Device.Name,str(x)),"Out","{0}.0".format(outAddress),"typeCommandAreaOutput","{0} Command Area {1} Output".format(self.Device.Name,str(x)),self.Device.Name,True)
        
    def adoptDps(self,dps,cmdAreaNumber):
        if cmdAreaNumber in self.connectedDps.keys():
            self.connectedDps[cmdAreaNumber].append(dps)
        else:
            raise KeyError("DPS CmdArea Number Not Valid")
            
    def export(self):
        XmlExport = swBlock.swBlock(self.xml.ObjectList)
        
        XmlExport.addCall()
        blockA = XmlExport.CallId
        XmlExport.Comment.text = self.name
        XmlExport.addEN(XmlExport.CallId,"en")
        XmlExport.Component.set("Name","Inst" + self.name + "_Health")
        XmlExport.CallInfo.set("Name","ProfinetDeviceHealthSelector")
        XmlExport.loadParameterStr('<Parameter Name="inData" Section="Input" Type="&quot;typeProfinetDeviceHealth&quot;"/>',"ProfinetDeviceHealth_DB.outData")
        XmlExport.loadParameterStr('<Parameter Name="inLADDR" Section="Input" Type="HW_INTERFACE"/>',self.name + "~PNCG")
        
        if self.software != None:
            self.software.Blocks.CreateInstanceDB(XmlExport.Component.get('Name'),True,1,XmlExport.CallInfo.get("Name"))
        
        XmlExport.addCall()
        XmlExport.Component.set("Name","Inst" + self.name)
        XmlExport.CallInfo.set("Name","Pncg")
        
        XmlExport.loadParameterStr('<Parameter Name="inoutGlobalData" Section="InOut" Type="&quot;typeInOutGlobalData&quot;"/>',"GlobalData.inoutGlobalData")
        
        XmlExport.loadParameterStr('<Parameter Name="inMandatoryStatus" Section="Input" Type="&quot;typeMandatoryInput&quot;"/>',self.name + "ManStatus")
        XmlExport.loadParameterStr('<Parameter Name="inMandatoryHandshake" Section="Input" Type="&quot;typeMandatoryHandShake&quot;"/>',self.name + "ManHSin")
        XmlExport.loadParameterStr('<Parameter Name="inVisuNodeIndex" Section="Input" Type="Byte"/>',self.name + "VisuNode")
        XmlExport.loadParameterStr('<Parameter Name="inVisuZoneIndex" Section="Input" Type="Byte"/>',self.name + "VisuZoneIndex")
        XmlExport.loadParameterStr('<Parameter Name="inStatusInfo" Section="Input" Type="&quot;typeEccStatus&quot;"/>',self.name + "VisuStatus")
        XmlExport.loadParameterStr('<Parameter Name="inWarningsInfo" Section="Input" Type="&quot;typeEccWarning&quot;"/>',self.name + "VisuWarnings")
        XmlExport.loadParameterStr('<Parameter Name="inFaultsInfo" Section="Input" Type="&quot;typeEccFault&quot;"/>',self.name + "VisuFaults")
        XmlExport.loadParameterStr('<Parameter Name="inCommandArea1" Section="Input" Type="&quot;typeCommandAreaInput&quot;"/>',self.name + 'CmdArea1In')
        XmlExport.loadParameterStr('<Parameter Name="inCommandArea2" Section="Input" Type="&quot;typeCommandAreaInput&quot;"/>',self.name + 'CmdArea2In')
        XmlExport.loadParameterStr('<Parameter Name="inCommandArea3" Section="Input" Type="&quot;typeCommandAreaInput&quot;"/>',self.name + 'CmdArea3In')
        XmlExport.loadParameterStr('<Parameter Name="inCommandArea4" Section="Input" Type="&quot;typeCommandAreaInput&quot;"/>',self.name + 'CmdArea4In')
        XmlExport.loadParameterStr('<Parameter Name="inCommandArea5" Section="Input" Type="&quot;typeCommandAreaInput&quot;"/>',self.name + 'CmdArea5In')
        XmlExport.loadParameterStr('<Parameter Name="inCommandArea6" Section="Input" Type="&quot;typeCommandAreaInput&quot;"/>',self.name + 'CmdArea6In')
        XmlExport.loadParameterStr('<Parameter Name="inResetFault" Section="Input" Type="Bool"/>','Inst' + self.contolCabnet + '.outPlcStatus.resetZoneFault')
        XmlExport.loadParameterStr('<Parameter Name="inCanChannel" Section="Input" Type="&quot;typeCANChannelInput&quot;"/>',self.name + "CANChannelIn")
        
        XmlExport.addParameter("inBusSlaveOk","Input","Bool")
        
        XmlExport.addConnection(blockA,"eno",XmlExport.CallId,"en")
        
        a = XmlExport.spawnPart("Inst" + self.name + "_Health.outFaultSumm","Contact",True)
        XmlExport.addEN(a,"in")
        
        XmlExport.addConnection(a,"out",XmlExport.CallId,"inBusSlaveOk")
        
        XmlExport.loadParameterStr('<Parameter Name="outCanChannel" Section="Output" Type="&quot;typeCANChannelOutput&quot;"/>',self.name + "CANChannelOut")
        XmlExport.loadParameterStr('<Parameter Name="outMandatoryCmd" Section="Output" Type="&quot;typeMandatoryOutput&quot;"/>',self.name + "ManCommand")
        XmlExport.loadParameterStr('<Parameter Name="outMandatoryHandshake" Section="Output" Type="&quot;typeMandatoryHandShake&quot;"/>',self.name + "ManHSOut")
        XmlExport.loadParameterStr('<Parameter Name="outCommandArea1" Section="Output" Type="&quot;typeCommandAreaOutput&quot;"/>',self.name + 'CmdArea1Out')
        XmlExport.loadParameterStr('<Parameter Name="outCommandArea2" Section="Output" Type="&quot;typeCommandAreaOutput&quot;"/>',self.name + 'CmdArea2Out')
        XmlExport.loadParameterStr('<Parameter Name="outCommandArea3" Section="Output" Type="&quot;typeCommandAreaOutput&quot;"/>',self.name + 'CmdArea3Out')
        XmlExport.loadParameterStr('<Parameter Name="outCommandArea4" Section="Output" Type="&quot;typeCommandAreaOutput&quot;"/>',self.name + 'CmdArea4Out')
        XmlExport.loadParameterStr('<Parameter Name="outCommandArea5" Section="Output" Type="&quot;typeCommandAreaOutput&quot;"/>',self.name + 'CmdArea5Out')
        XmlExport.loadParameterStr('<Parameter Name="outCommandArea6" Section="Output" Type="&quot;typeCommandAreaOutput&quot;"/>',self.name + 'CmdArea6Out')
        XmlExport.loadParameterStr('<Parameter Name="inoutParameterData" Section="InOut" Type="&quot;typeNodeParameters&quot;"/>',"dbPncgParameterData." + self.name)
        
        if self.scl != None:
            #SCL ConFig
            self.scl.addRegion(XmlExport.Component.get("Name"))
            self.scl.GlobalVariableEqualLiteralConstant(XmlExport.Component.get("Name") + ".inConfig.name", self.name[8:])
            self.scl.GlobalVariableEqualConstant(XmlExport.Component.get("Name") + ".inConfig.numberOfEccs", "0")
            self.scl.GlobalVariableEqualTypedConstant(XmlExport.Component.get("Name") + ".inConfig.panelMaskPncg", '2#0000_0000_0000_0000_0000_0000_0000_0001')
            self.scl.GlobalVariableEqualTypedConstant(XmlExport.Component.get("Name") + ".inConfig.panelMaskCommandArea1", '2#0000_0000_0000_0000_0000_0000_0000_0001')
            self.scl.GlobalVariableEqualTypedConstant(XmlExport.Component.get("Name") + ".inConfig.panelMaskCommandArea2", '2#0000_0000_0000_0000_0000_0000_0000_0001')
            self.scl.GlobalVariableEqualTypedConstant(XmlExport.Component.get("Name") + ".inConfig.panelMaskCommandArea3", '2#0000_0000_0000_0000_0000_0000_0000_0001')
            self.scl.GlobalVariableEqualTypedConstant(XmlExport.Component.get("Name") + ".inConfig.panelMaskCommandArea4", '2#0000_0000_0000_0000_0000_0000_0000_0001')
            self.scl.GlobalVariableEqualTypedConstant(XmlExport.Component.get("Name") + ".inConfig.panelMaskCommandArea5", '2#0000_0000_0000_0000_0000_0000_0000_0001')
            self.scl.GlobalVariableEqualTypedConstant(XmlExport.Component.get("Name") + ".inConfig.panelMaskCommandArea6", '2#0000_0000_0000_0000_0000_0000_0000_0001')
            self.scl.endRegion()
        
        if self.software != None:
            self.software.Blocks.CreateInstanceDB(XmlExport.Component.get('Name'),True,1,XmlExport.CallInfo.get("Name"))
        
        self.dpsLogic("1",XmlExport)
        self.dpsLogic("2",XmlExport)
        self.dpsLogic("3",XmlExport)
        self.dpsLogic("4",XmlExport)
        self.dpsLogic("5",XmlExport)
        self.dpsLogic("6",XmlExport)
            
    def dpsLogic(self,DpsToCmdArea,XmlExport):
        if len(self.connectedDps[DpsToCmdArea]) >= 1:
            if len(self.connectedDps[DpsToCmdArea]) == 1:
                XmlExport.loadParameterStr('<Parameter Name="inDpsToCmdArea{0}" Section="Input" Type="&quot;typePowerSupplyToPncg&quot;"/>'.format(DpsToCmdArea),"Inst{0}.outDpsZone{1}ToPncg".format(self.connectedDps["1"][0].name,DpsToCmdArea))
            else:
                listConnected = []
                listEnable = []
                listReset = []
                listWakeUp = []
                for x in self.connectedDps[DpsToCmdArea]:
                    listConnected.append("Inst{0}.outDpsZone1ToPncg.connected".format(x.name))
                    listEnable.append("Inst{0}.outDpsZone1ToPncg.requestEnable".format(x.name))
                    listReset.append("Inst{0}.outDpsZone1ToPncg.requestReset".format(x.name))
                    listWakeUp.append("Inst{0}.outDpsZone1ToPncg.requestWakeUp".format(x.name))
                XmlExport.ANDspawn(listConnected,"Inst{0}.inDpsToCmdArea{1}.requestEnable".format(self.name,DpsToCmdArea))
                XmlExport.ORspawn(listEnable,"Inst{0}.inDpsToCmdArea{1}.requestReset".format(self.name,DpsToCmdArea))
                XmlExport.ORspawn(listReset,"Inst{0}.inDpsToCmdArea{1}.requestWakeUp".format(self.name,DpsToCmdArea))
                XmlExport.ORspawn(listWakeUp,"Inst{0}.inDpsToCmdArea{1}.requestWakeUp".format(self.name,DpsToCmdArea))
        
class ezcObject(father):
    def __init__(self,name,parent,asiAddress):
        super().__init__(name,parent)
        self.ezcData = {}
        self.ezcDataSorted =    {
                                "DpsBoxs":[],
                                "AuxBoxs":[],
                                "Estops":[],
                                "RPTRs":[]
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
        if re.search("^CA[0-9]{1,3}EZC[0-9]{1,3}$",self.name):
            self.ezcNumber = re.findall("[0-9]{1,3}$", self.name)[0]
        self.createAsiTags()
        
    def addAsiEstop(self,name,asiAddress):
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
            
    def addRptrBox(self,asiNetwork):
        #Expecting ASI_C1 or ASI_A2
        if re.search("^ASI_[A-Z][1-2]$",asiNetwork) != None:
            name = "{0}RPTR{1}".format(self.name,re.findall("_[A-Z][0-9]{1,3}$",asiNetwork)[0])
            if name not in self.data.keys():
                object = rptrObject(name,self,asiNetwork)
                self.data[name] = object
                self.dataSorted["rptrObject"].append(object)
                self.controlAreaData[name] = object
                self.controlAreaDataSorted["RPTRs"].append(object)
                self.ezcData[name] = object
                self.ezcDataSorted["RPTRs"].append(object)
                return object
            else:
                raise KeyError
        else:
            raise ValueError("Malformed ASI Address")
        
    def createAsiTags(self):
        if self.networkName in self.networkDevices:
            self.pnag = self.networkDevices[self.networkName]
            self.pnag.addHalfNodeASI(self.name + "_CR_ESM",self.asiAddress + "_I3")
        else:
            raise KeyError("ASI Network Not Found In This Area")
        
    def export(self):
        self.EzcBox()
        self.EzcBox_FS()
        
    def EzcBox_FS(self):
        XmlExport = swBlock.swBlock(self.xml.ObjectList)
        
        XmlExport.addCall()
        XmlExport.Comment.text = self.name + "_FS"
        XmlExport.addEN(XmlExport.CallId,"en")
        XmlExport.Component.set("Name","Inst" + self.name + "_FS")
        XmlExport.CallInfo.set("Name","EZC_FS")
        
        XmlExport.loadParameterStr('<Parameter Name="inZoneReset" Section="Input" Type="Bool"/>',"tempEstopReset","LocalVariable")
        XmlExport.loadParameterStr('<Parameter Name="inPowerGroupSafetyStatusToSafety" Section="Input" Type="&quot;typePowerGroupStatusToSafety&quot;"/>',"DataToSafety.{0}EZCxPowerGroupToSafetyStatus[{1}]".format(self.controlArea,self.ezcNumber))
        XmlExport.loadParameterStr('<Parameter Name="inContactorFeedBack" Section="Input" Type="Bool"/>',self.name + "_CR_ESM")
        XmlExport.loadParameterStr('<Parameter Name="inQBAD" Section="Input" Type="Bool"/>',"F{0}_8BytePROFIsafedata.QBAD".format(self.pnag.PROFIsafeAdress.zfill(5)))
        
        XmlExport.addParameter("inLocal","Input","Bool")
        
        id = XmlExport.spawnPart("AlwaysFALSE","Contact")
        XmlExport.addEN(id,"in")
        XmlExport.addConnection(id,"out",XmlExport.CallId,"inLocal")
        
        XmlExport.addParameter("inInterlocks","Input","Bool")
        
        id = XmlExport.spawnPart("AlwaysFALSE","Contact")
        XmlExport.addEN(id,"in")
        XmlExport.addConnection(id,"out",XmlExport.CallId,"inInterlocks")
        
        if self.scl != None:
            pass
        
        if self.software != None:
            self.software.Blocks.CreateInstanceDB(XmlExport.Component.get('Name'),True,1,XmlExport.CallInfo.get("Name"))
    
    def EzcBox(self):
        dpsNames = []
        auxNames = []
        for x in self.ezcDataSorted["DpsBoxs"]:
            dpsNames.append(x.name)
        for x in self.ezcDataSorted["AuxBoxs"]:
            auxNames.append(x.name)
        XmlExport = swBlock.swBlock(self.xml.ObjectList)
        
        XmlExport.addCall()
        XmlExport.addEN(XmlExport.CallId,"en")
        XmlExport.Component.set("Name","Inst" + self.name)
        XmlExport.CallInfo.set("Name","EzcBox")
        XmlExport.Comment.text = self.name
        
        if len(dpsNames) > 0:
            XmlExport.addParameter("inPowerSupplyGroupStarted","Input","Bool")
            XmlExport.addParameter("inPowerSupplyGroupAllStarted","Input","Bool")
            if len(dpsNames) > 1:
                list = []
                for x in dpsNames:
                    list.append("Inst" + x + ".outDpsToZca.started")
                XmlExport.OR(list,XmlExport.CallId,"inPowerSupplyGroupStarted")
                list = []
                for x in dpsNames:
                    list.append("Inst" + x + ".outDpsToZca.AllStarted")
                XmlExport.AND(list,XmlExport.CallId,"inPowerSupplyGroupAllStarted")
            else:
                id = XmlExport.spawnPart("Inst" + dpsNames[0] + ".outDpsToZca.started","Contact")
                XmlExport.addEN(id,"in")
                XmlExport.addConnection(id,"out",XmlExport.CallId,"inPowerSupplyGroupStarted")
                
                id = XmlExport.spawnPart("Inst" + dpsNames[0] + ".outDpsToZca.AllStarted","Contact")
                XmlExport.addEN(id,"in")
                XmlExport.addConnection(id,"out",XmlExport.CallId,"inPowerSupplyGroupAllStarted")
        else:
            XmlExport.loadParameterStr('<Parameter Name="inPowerSupplyGroupStarted" Section="Input" Type="Bool"/>','',"LiteralConstant","Bool","true")
            XmlExport.loadParameterStr('<Parameter Name="inPowerSupplyGroupAllStarted" Section="Input" Type="Bool"/>','',"LiteralConstant","Bool","true")
        if len(auxNames) > 0:
            XmlExport.addParameter("inSupplyAuxOk","Input","Bool")
            list = []
            for x in range(len(auxNames)):
                id = XmlExport.spawnPart("Inst" + auxNames[x] + ".outFault","Contact")
                list.append(id)
                if x == 0:
                    XmlExport.addEN(id,"in")
                else:
                    XmlExport.addConnection(list[x-1],"out",id,"in")
            XmlExport.addConnection(list[-1],"out",XmlExport.CallId,"inSupplyAuxOk")
        else:
            XmlExport.loadParameterStr('<Parameter Name="inSupplyAuxOk" Section="Input" Type="Bool"/>','',"LiteralConstant","Bool","true")
        XmlExport.loadParameterStr('<Parameter Name="inSupplyEzcDCOk" Section="Input" Type="Bool"/>',self.name + "_CR_ESM")
        XmlExport.loadParameterStr('<Parameter Name="inAsiBusFault" Section="Input" Type="Bool"/>',"Inst" + self.pnagName + ".outVisuInterface.status.summary")
        XmlExport.loadParameterStr('<Parameter Name="inConvStartWarning" Section="Input" Type="Bool"/>','',"LiteralConstant","Bool","true")
        XmlExport.loadParameterStr('<Parameter Name="inMainPanelToEzc" Section="Input" Type="&quot;typeAreaToZoneControl&quot;"/>','Inst' + self.contolCabnet + '.outPlcStatus')
        XmlExport.loadParameterStr('<Parameter Name="inPowerGroupSafetyStatusToEzc" Section="Input" Type="&quot;typeSafetyStatusToPowerGroup&quot;"/>','DataFromSafety.' + self.controlArea +'EZCxSafetyStatusToPowerGroup[' + self.ezcNumber + ']')
        XmlExport.loadParameterStr('<Parameter Name="outEzcStatusToSafety" Section="Output" Type="&quot;typePowerGroupStatusToSafety&quot;"/>','DataToSafety.' + self.controlArea +'EZCxPowerGroupToSafetyStatus[' + self.ezcNumber + ']')
        
        if self.scl != None:
            #SCL ConFig
            self.scl.addRegion(XmlExport.Component.get("Name"))
            self.scl.GlobalVariableEqualLiteralConstant(XmlExport.Component.get("Name") + ".inConfig.ezcName",re.findall("EZC[0-9]{1,3}$", self.name)[0])
            self.scl.GlobalVariableEqualConstant(XmlExport.Component.get("Name") + ".inConfig.panelNumber","1")
            self.scl.endRegion()
        
        if self.software != None:
            self.software.Blocks.CreateInstanceDB(XmlExport.Component.get('Name'),True,1,XmlExport.CallInfo.get("Name"))
    
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
        XmlExport = swBlock.swBlock(self.xml.ObjectList)
        
        XmlExport.addCall()
        XmlExport.Comment.text = self.name
        XmlExport.addEN(XmlExport.CallId,"en")
        XmlExport.Component.set("Name","Inst" + self.name)
        XmlExport.CallInfo.set("Name","RptrBox")
        
        XmlExport.loadParameterStr('<Parameter Name="inTemperatureRptrOk" Section="Input" Type="Bool"/>','',"LiteralConstant","Bool","true")
        XmlExport.loadParameterStr('<Parameter Name="inPnagToRptr" Section="Input" Type="&quot;typePnagToRptr;"/>',"Inst" + self.pnagName + ".outPnagToRptr")
        XmlExport.loadParameterStr('<Parameter Name="inAsiBusFault" Section="Input" Type="Bool"/>',"Inst" + self.pnagName + ".outVisuInterface.status.summary")
        
        if self.scl != None:
            #SCL ConFig
            self.scl.addRegion(XmlExport.Component.get("Name"))
            self.scl.GlobalVariableEqualLiteralConstant(XmlExport.Component.get("Name") + ".inConfig.rptrName", re.findall("RPTR_[A-Z][1-2]$", XmlExport.Component.get("Name"))[0].replace("_", ""))
            self.scl.GlobalVariableEqualTypedConstant(XmlExport.Component.get("Name") + ".inConfig.panelMask", '2#0000_0000_0000_0000_0000_0000_0000_0001')
            self.scl.endRegion()
        
        if self.software != None:
            self.software.Blocks.CreateInstanceDB(XmlExport.Component.get('Name'),True,1,XmlExport.CallInfo.get("Name"))
        
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
        XmlExport = swBlock.swBlock(self.xml.ObjectList)
        
        XmlExport.addCall()
        XmlExport.Comment.text = self.name
        XmlExport.addEN(XmlExport.CallId,"en")
        XmlExport.Component.set("Name","Inst" + self.name)
        XmlExport.CallInfo.set("Name","AuxBox")
        
        XmlExport.loadParameterStr('<Parameter Name="inSupplyAuxDCOk" Section="Input" Type="Bool"/>',self.name +'_CR_ESM')
        XmlExport.loadParameterStr('<Parameter Name="inEzcToAux" Section="Input" Type="&quot;typeZoneControlToAux&quot;"/>',"Inst" + self.ezcName +'.outEzcToAux')
        XmlExport.loadParameterStr('<Parameter Name="inAsiBusFault" Section="Input" Type="Bool"/>',"Inst" + self.pnagName + ".outVisuInterface.status.summary")
        
        
        if self.scl != None:
            self.scl.addRegion(XmlExport.Component.get("Name"))
            self.scl.GlobalVariableEqualLiteralConstant(XmlExport.Component.get("Name") + ".inConfig.auxName",re.findall("AUX[0-9]{1,3}$", XmlExport.Component.get("Name"))[0])
            self.scl.GlobalVariableEqualTypedConstant(XmlExport.Component.get("Name") + ".inConfig.panelMask", '2#0000_0000_0000_0000_0000_0000_0000_0001')
            self.scl.endRegion()
        
        if self.software != None:
            self.software.Blocks.CreateInstanceDB(XmlExport.Component.get('Name'),True,1,XmlExport.CallInfo.get("Name"))
        
class asiEstopObject(father):
    def __init__(self,name,asiAddress,parent):
        super(asiEstopObject,self).__init__(name,parent)
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
            self.pnag.addHalfNodeASI(self.name + "_NONSAFE",self.asiAddress + "A_I1")
            self.pnag.addHalfNodeASI(self.name + "_LT_R",self.asiAddress + "A_O1")
            self.pnag.addHalfNodeASI(self.name + "_LT_G",self.asiAddress + "A_O2")
            
        else:
            raise KeyError("ASI Network Not Found In This Area")
    
    def export(self):
        XmlExport = swBlock.swBlock(self.xml.ObjectList)
        
        XmlExport.addCall()
        XmlExport.addEN(XmlExport.CallId,"en")
        XmlExport.Component.set("Name","Inst" + self.name + "_Vis")
        
        XmlExport.CallInfo.set("Name","EmergencyStop")
        XmlExport.Comment.text = self.name + "_Vis"
        XmlExport.addParameter("inEStopStatus","Input","Bool")
        XmlExport.loadParameterStr('<Parameter Name="inZoneStatus" Section="Input" Type="Bool"/>','Inst' + self.controlArea + self.ezcName + '_FC.outEStopHealthy')
        XmlExport.loadParameterStr('<Parameter Name="inLocation" Section="Input" Type="String[14]"/>','',"LiteralConstant","String",self.name.split("_")[0])
        XmlExport.loadParameterStr('<Parameter Name="inConfigContactType" Section="Input" Type="Bool"/>','',"LiteralConstant","Bool","false")
        XmlExport.loadParameterStr('<Parameter Name="inAsiBusFault" Section="Input" Type="Bool"/>','Inst' + self.pnagName + '.outVisuInterface.status.summary')
        
        x = XmlExport.spawnPart(self.name,"Contact")
        XmlExport.addEN(x,"in")
        y = XmlExport.spawnPart(self.name + "_NONSAFE","Contact")
        XmlExport.addEN(y,"in")
        z = XmlExport.addOR("2")
        XmlExport.addConnection(x,"out",z,"in1")
        XmlExport.addConnection(y,"out",z,"in2")
        XmlExport.addConnection(z,"out",XmlExport.CallId,"inEStopStatus")
        
        a = XmlExport.spawnPart(XmlExport.Component.get("Name") + ".outEstopLamp","Contact")
        XmlExport.addEN(a,"in")
        b = XmlExport.spawnPart(self.name + "_LT_R","Coil")
        XmlExport.addConnection(a,"out",b,"in")
        
        c = XmlExport.spawnPart(XmlExport.Component.get("Name") + ".outEstopLamp","Contact",True)
        XmlExport.addEN(c,"in")
        d = XmlExport.spawnPart(self.name + "_NONSAFE","Contact")
        e = XmlExport.spawnPart(self.name + "_LT_G","Coil")
        XmlExport.addConnection(c,"out",d,"in")
        XmlExport.addConnection(d,"out",e,"in")
        
        if self.scl != None:
            #SCL ConFig
            pass
        
        if self.software != None:
            self.software.Blocks.CreateInstanceDB(XmlExport.Component.get('Name'),True,1,XmlExport.CallInfo.get("Name"))
        
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
        self.connectedPncg = None
        self.cmdAreaNumber = None
        self.createAsiTags(asiAddress)
        
    def adoptPncg(self,pncg,cmdAreaNumber):
        self.connectedPncg = pncg
        if cmdAreaNumber in self.connectedPncg.connectedDps.keys():
            self.connectedPncg.adoptDps(self,cmdAreaNumber)
            self.cmdAreaNumber = cmdAreaNumber
        else:
            raise KeyError("DPS CmdArea Number Not Valid")
        
    def createAsiTags(self,asiAddress):
        if self.networkName in self.networkDevices:
            self.pnag = self.networkDevices[self.networkName]
            self.pnag.addHalfNodeASI(self.name + "_CR_ESM",self.asiAddress)
        else:
            raise KeyError("ASI Network Not Found In This Area")
    
    def export(self):
        XmlExport = swBlock.swBlock(self.xml.ObjectList)
        
        XmlExport.addCall()
        XmlExport.addEN(XmlExport.CallId,"en")
        XmlExport.Comment.text = self.name
        XmlExport.Component.set("Name","Inst" + self.name)
        XmlExport.CallInfo.set("Name","DpsBox")
        XmlExport.loadParameterStr('<Parameter Name="in24VEpsSupplyOk" Section="Input" Type="Bool"/>','',"LiteralConstant","Bool","true")
        XmlExport.loadParameterStr('<Parameter Name="inField48VSupply1Ok" Section="Input" Type="Bool"/>',self.name + "_CR_ESM")
        XmlExport.loadParameterStr('<Parameter Name="inField48VSupply2Ok" Section="Input" Type="Bool"/>','',"LiteralConstant","Bool","true")
        XmlExport.loadParameterStr('<Parameter Name="inZcaToDps" Section="Input" Type="&quot;typeZcaToDpsMpsEsz&quot;"/>','Inst' + self.ezcName +'.outEzcToPowerSupply')
        XmlExport.loadParameterStr('<Parameter Name="inAsiBusFault" Section="Input" Type="Bool"/>',"Inst" + self.pnagName + ".outVisuInterface.status.summary")
        if self.connectedPncg != None and self.cmdAreaNumber != None:
            XmlExport.loadParameterStr('<Parameter Name="inPncgZone1Ready" Section="Input" Type="Bool"/>',"Inst{0}.outCommandAreaStatus[{1}].areaReady".format(self.connectedPncg.name,self.cmdAreaNumber))
            XmlExport.loadParameterStr('<Parameter Name="inPncgZone1Active" Section="Input" Type="Bool"/>',"Inst{0}.outCommandAreaStatus[{1}].areaEnabled".format(self.connectedPncg.name,self.cmdAreaNumber))
        else:
            XmlExport.loadParameterStr('<Parameter Name="inPncgZone1Ready" Section="Input" Type="Bool"/>','',"LiteralConstant","Bool","false")
            XmlExport.loadParameterStr('<Parameter Name="inPncgZone1Active" Section="Input" Type="Bool"/>','',"LiteralConstant","Bool","false")
        XmlExport.loadParameterStr('<Parameter Name="inPncgZone2Ready" Section="Input" Type="Bool"/>','',"LiteralConstant","Bool","false")
        XmlExport.loadParameterStr('<Parameter Name="inPncgZone2Active" Section="Input" Type="Bool"/>','',"LiteralConstant","Bool","false")
        
        if self.scl != None:
            #SCL ConFig
            self.scl.addRegion(XmlExport.Component.get("Name"))
            self.scl.GlobalVariableEqualBool(XmlExport.Component.get("Name") + ".inConfig.splitPowergroupCommandZones",False)
            self.scl.GlobalVariableEqualLiteralConstant(XmlExport.Component.get("Name") + ".inConfig.panelName", self.name)
            self.scl.GlobalVariableEqualTypedConstant(XmlExport.Component.get("Name") + ".inConfig.panelMask", '2#0000_0000_0000_0000_0000_0000_0000_0001')
            self.scl.endRegion()
            
        if self.software != None:
            self.software.Blocks.CreateInstanceDB(XmlExport.Component.get('Name'),True,1,XmlExport.CallInfo.get("Name"))
        
class AbbAcs380DriveObject(father):
    def __init__(self,unitNumber,parent,ip,zone=""):
        self.unitNumber = unitNumber
        if zone != "":
            self.zone = "_" + zone
        self.name = self.unitNumber + self.zone + "_FMD"
        super(AbbAcs380DriveObject,self).__init__(self.name,parent)
        self.project = parent.project
        self.software = parent.blockGroupSw
        self.xml = parent.xml
        self.scl = parent.scl
        self.tags = parent.tags
        self.subnet = parent.subnet
        self.ip = ip
        self.hardwareSetup()
        
    def hardwareSetup(self):
        typeIdentifier = "GSD:GSDML-V2.33-ABB-FPNO-20180516.XML"
        Object = device.ungroupedDevice(self.project,typeIdentifier + "/DAP",self.name)
        PPO4 = Object.addModule(typeIdentifier + "/M/ID_MODULE_PPO4","PPO Type 4_1",1)
        Object.getNetworkInterface(Object.Objects[self.name]["Interface"]["Object"])
        Object.setIp(self.ip,self.subnet)
        inStart = Object.Objects["PPO Type 4_1"]["PPO4 Data Object"]["Object"].Addresses[0].StartAddress
        outStart = Object.Objects["PPO Type 4_1"]["PPO4 Data Object"]["Object"].Addresses[1].StartAddress
        self.tags.addTag(self.name+"_In","In","{0}.0".format(inStart),"typeABBACS380InputsPP04","PP04 Inputs For Drive Flags","FMD PPO Tags")
        self.tags.addTag(self.name+"_Out","Out","{0}.0".format(outStart),"typeABBACS380OutputsPP04","PP04 Outputs For Drive Control","FMD PPO Tags")
        
    def export(self):
        XmlExport = swBlock.swBlock(self.xml.ObjectList)
        
        XmlExport.addCall()
        XmlExport.addEN(XmlExport.CallId,"en")
        XmlExport.Component.set("Name","Inst" + self.unitNumber + self.zone + "_Drive1")
        XmlExport.CallInfo.set("Name","AbbAcs380Drive")
        XmlExport.Comment.text = self.name
        
        XmlExport.loadParameterStr('<Parameter Name="inDriveStatus" Section="Input" Type="&quot;typeABBACS380InputsPP04&quot;" />',self.name + "_In")
        XmlExport.loadParameterStr('<Parameter Name="inConveyorStatus" Section="Input" Type="&quot;typePortStatus1Unit&quot;" />',"Inst" + self.unitNumber + self.zone + ".outStatus")
        XmlExport.loadParameterStr('<Parameter Name="inDriveFlags" Section="Input" Type="&quot;typeDriveFlags&quot;" />',"Inst" + self.unitNumber + self.zone + ".outPort12Motor")
        XmlExport.loadParameterStr('<Parameter Name="outDriveCommand" Section="Output" Type="&quot;typeABBACS380OutputsPP04&quot;" />',self.name + "_Out")
        
        if self.scl != None:
            self.scl.GlobalVariableEqualLiteralConstant(XmlExport.Component.get("Name") + ".inConfig.calibratedSpeed","0")
            
        if self.software != None:
            self.software.Blocks.CreateInstanceDB(XmlExport.Component.get('Name'),True,1,XmlExport.CallInfo.get("Name"))
       
class MoviMotObject(father):
    def __init__(self,unitNumber,parent,ip,zone=""):
        self.unitNumber = unitNumber
        if zone != "":
            self.zone = "_" + zone
        self.name = self.unitNumber + self.zone + "_MMD"
        super(MoviMotObject,self).__init__(self.name,parent)
        self.project = parent.project
        self.software = parent.blockGroupSw
        self.xml = parent.xml
        self.scl = parent.scl
        self.tags = parent.tags
        self.subnet = parent.subnet
        self.ip = ip
        self.hardwareSetup()
        
    def hardwareSetup(self):
        typeIdentifier = "GSD:GSDML-V2.25-SEW-MFE52A-20161017-102525.XML"
        Object = device.ungroupedDevice(self.project,typeIdentifier + "/DAP/MFE PDEV MRP 3MM",self.name)
        Object.deleteModule("Slot not used_3")
        Slot3 = Object.addModule(typeIdentifier + "/M/11","4/6 DI_1",3)
        Object.getNetworkInterface(Object.Objects[self.name]["Ethernet Interface"]["Object"])
        Object.setIp(self.ip,self.subnet)
        IOin = Object.Objects["4/6 DI_1"]["4/6 DI"]["Object"].Addresses[0].StartAddress
        MM3PDin = Object.Objects["MOVIMOT 3PD_1"]["MOVIMOT 3PD"]["Object"].Addresses[0].StartAddress
        MM3PDout = Object.Objects["MOVIMOT 3PD_1"]["MOVIMOT 3PD"]["Object"].Addresses[1].StartAddress
        if IOin != -1 and MM3PDin != -1 and MM3PDout != -1:
            self.tags.addTag(self.unitNumber + "_PE_P","In","{0}.0".format(IOin),"Bool","4/6 DI Input 1","MMD Tags")
            self.tags.addTag(self.name + "_In","In","{0}.0".format(MM3PDin),"typeProfinetMoviMotInputs","Input Commands","MMD Tags")
            self.tags.addTag(self.name + "_Out","Out","{0}.0".format(MM3PDout),"typeProfinetMoviMotOutputs","Output Flags","MMD Tags")
        
    def export(self):
        XmlExport = swBlock.swBlock(self.xml.ObjectList)
        
        XmlExport.addCall()
        XmlExport.addEN(XmlExport.CallId,"en")
        XmlExport.Component.set("Name","Inst" + self.unitNumber + self.zone + "_Drive1")
        XmlExport.CallInfo.set("Name","ProfinetMoviMot")
        XmlExport.Comment.text = self.name
        
        XmlExport.loadParameterStr('<Parameter Name="inIsolatorSwitchOk" Section="Input" Type="Bool"/>','',"LiteralConstant","Bool","true")
        XmlExport.loadParameterStr('<Parameter Name="inDriveStatus" Section="Input" Type="&quot;typeProfinetMoviMotInputs&quot;" />',self.unitNumber + self.zone+ "_MMD_In")
        XmlExport.loadParameterStr('<Parameter Name="inDriveFlags" Section="Input" Type="&quot;typeDriveFlags&quot;"/>',"Inst" + self.unitNumber + self.zone + ".outPort12Motor")
        
        XmlExport.loadParameterStr('<Parameter Name="outDriveControl" Section="Output" Type="&quot;typeProfinetMoviMotOutputs&quot;" />',self.unitNumber + self.zone + "_MMD_Out")
        
        if self.scl != None:
            #SCL ConFig
            self.scl.addRegion(XmlExport.Component.get("Name"))
            self.scl.GlobalVariableEqualLiteralConstant(XmlExport.Component.get("Name") + ".inConfig.driveIndex","1")
            self.scl.GlobalVariableEqualLiteralConstant(XmlExport.Component.get("Name") + ".inConfig.calibratedSpeed","0")
            self.scl.endRegion()
            
        if self.software != None:
            self.software.Blocks.CreateInstanceDB(XmlExport.Component.get('Name'),True,1,XmlExport.CallInfo.get("Name"))

class FortressGateObject(father):
    def __init__(self,unitNumber,parent,ip,zone=""):
        self.unitNumber = unitNumber
        if zone != "":
            self.zone = "_" + zone
        self.name = self.unitNumber + self.zone + "_GS"
        super(FortressGateObject,self).__init__(self.name,parent)
        self.project = parent.project
        self.software = parent.blockGroupSw
        self.xml = parent.xml
        self.scl = parent.scl
        self.tags = parent.tags
        self.subnet = parent.subnet
        self.ip = ip
        self.hardwareSetup()
        
    def hardwareSetup(self):
        typeIdentifier = "GSD:GSDML-V2.35-FORTRESS-PROLOK-20190704.XML"
        self.Object = device.ungroupedDevice(self.project,typeIdentifier + "/DAP",self.name)
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
        self.FortressGateSwitch()
        self.FortressGateSwitchSafety()
        self.FortressGateSwitchVis()
    
    def FortressGateSwitch(self):
        XmlExport = swBlock.swBlock(self.xml.ObjectList)
        
        XmlExport.addCall()
        XmlExport.Comment.text = self.name
        XmlExport.addEN(XmlExport.CallId,"en")
        XmlExport.Component.set("Name","Inst" + self.name)
        XmlExport.CallInfo.set("Name","FortressGateSwitch")
        XmlExport.loadParameterStr('<Parameter Name="inRequestAccess" Section="Input" Type="Bool"/>',self.name + "_RQ_PB")
        XmlExport.loadParameterStr('<Parameter Name="inAccessGranted" Section="Input" Type="Bool"/>','',"LiteralConstant","Bool","true")
        XmlExport.loadParameterStr('<Parameter Name="inUnlockSwitch" Section="Input" Type="Bool"/>',self.name + "_G_SW")
        XmlExport.loadParameterStr('<Parameter Name="inGateMonitor" Section="Input" Type="Bool"/>',self.name + "_GateMon")
        XmlExport.loadParameterStr('<Parameter Name="inResetRequest" Section="Input" Type="Bool"/>',self.name + "_RS_PB")
        XmlExport.loadParameterStr('<Parameter Name="outGateSolenoid" Section="Output" Type="Bool"/>',self.name + "_Sol_Drive")
        XmlExport.loadParameterStr('<Parameter Name="outGateSwitchLamp" Section="Output" Type="Bool"/>',self.name + "_G_LT")
        XmlExport.loadParameterStr('<Parameter Name="outResetLamp" Section="Output" Type="Bool"/>',self.name + "_RS_LT")
        XmlExport.loadParameterStr('<Parameter Name="outRequestLamp" Section="Output" Type="Bool"/>',self.name + "_RQ_LT")
        
        if self.scl != None:
            #SCL ConFig
            pass
            
        if self.software != None:
            self.software.Blocks.CreateInstanceDB(XmlExport.Component.get('Name'),True,1,XmlExport.CallInfo.get("Name"))
            
    def FortressGateSwitchSafety(self):
        XmlExport = swBlock.swBlock(self.xml.ObjectList)
        
        XmlExport.addCall()
        XmlExport.Comment.text = self.name
        XmlExport.addEN(XmlExport.CallId,"en")
        XmlExport.Component.set("Name","Inst" + self.name + "_FS")
        XmlExport.CallInfo.set("Name","FortressGateSwitchSafety")
        XmlExport.loadParameterStr('<Parameter Name="inEstopPB1" Section="Input" Type="Bool"/>',self.name + "_Estop_1")
        XmlExport.loadParameterStr('<Parameter Name="inEstopPB2" Section="Input" Type="Bool"/>',self.name + "_Estop_2")
        XmlExport.loadParameterStr('<Parameter Name="inHead1" Section="Input" Type="Bool"/>',self.name + "_Sol_1")
        XmlExport.loadParameterStr('<Parameter Name="inHead2" Section="Input" Type="Bool"/>',self.name + "_Sol_2")
        XmlExport.loadParameterStr('<Parameter Name="inAck" Section="Input" Type="Bool"/>',"tempEstopReset","LocalVariable")
        XmlExport.loadParameterStr('<Parameter Name="inQbad" Section="Input" Type="Bool"/>',self.Failsafe_FIODBName + ".QBAD")
        XmlExport.loadParameterStr('<Parameter Name="inAccessGranted" Section="Input" Type="Bool"/>','',"LiteralConstant","Bool","true")
        
        if self.scl != None:
            #SCL ConFig
            pass
            
        if self.software != None:
            self.software.Blocks.CreateInstanceDB(XmlExport.Component.get('Name'),True,1,XmlExport.CallInfo.get("Name"))
            
    def FortressGateSwitchVis(self):
        XmlExport = swBlock.swBlock(self.xml.ObjectList)
        
        XmlExport.addCall()
        XmlExport.Comment.text = self.name + "_Vis"
        XmlExport.addEN(XmlExport.CallId,"en")
        XmlExport.Component.set("Name","Inst" + self.name + "_Vis")
        
        XmlExport.CallInfo.set("Name","EmergencyStop")
        XmlExport.addParameter("inEStopStatus","Input","Bool")
        XmlExport.loadParameterStr('<Parameter Name="inZoneStatus" Section="Input" Type="Bool"/>','',"LiteralConstant","Bool","false")
        XmlExport.loadParameterStr('<Parameter Name="inLocation" Section="Input" Type="String[14]"/>','',"LiteralConstant","String",self.unitNumber)
        XmlExport.loadParameterStr('<Parameter Name="inConfigContactType" Section="Input" Type="Bool"/>','',"LiteralConstant","Bool","false")
        XmlExport.loadParameterStr('<Parameter Name="inAsiBusFault" Section="Input" Type="Bool"/>','',"LiteralConstant","Bool","false")
        
        x = XmlExport.spawnPart(self.name + "_Estop_1","Contact")
        XmlExport.addEN(x,"in")
        y = XmlExport.spawnPart(self.name + "_Estop_2","Contact")
        XmlExport.addEN(y,"in")
        z = XmlExport.addOR("2")
        XmlExport.addConnection(x,"out",z,"in1")
        XmlExport.addConnection(y,"out",z,"in2")
        XmlExport.addConnection(z,"out",XmlExport.CallId,"inEStopStatus")
        
        if self.scl != None:
            #SCL ConFig
            pass
            
        if self.software != None:
            self.software.Blocks.CreateInstanceDB(XmlExport.Component.get('Name'),True,1,XmlExport.CallInfo.get("Name"))
        
class ScannerSickCLV6xxObject(father):
    def __init__(self,unitNumber,parent,ip,zone="",genHardware=True):
        self.unitNumber = unitNumber
        if zone != "":
            self.zone = "_" + zone
        self.unitName = self.unitNumber + self.zone
        self.name = self.unitNumber + self.zone + "_SC"
        super(ScannerSickCLV6xxObject,self).__init__(self.name,parent)
        self.project = parent.project
        self.software = parent.blockGroupSw
        self.xml = parent.xml
        self.scl = parent.scl
        self.tags = parent.tags
        self.subnet = parent.subnet
        self.ip = ip
        if genHardware:
            self.hardwareSetup()
        
    def hardwareSetup(self):
        typeIdentifier = "GSD:GSDML-V2.3-SICK-CLV62XCLV65X_VIA_CDF600-20150312.XML"
        Object = device.ungroupedDevice(self.project,typeIdentifier + "/DAP",self.unitNumber + "_SC")
        Object.getNetworkInterface(Object.Objects[self.unitNumber + "_SC"]["Interface"]["Object"])
        Object.setIp(self.ip,self.subnet)
        Ctrl_Bits_in_1 = Object.Objects["Ctrl Bits in_1"]["Ctrl Bits in"]["Object"].Addresses[0].StartAddress
        Ctrl_Bits_out_1 = Object.Objects["Ctrl Bits out_1"]["Ctrl Bits out"]["Object"].Addresses[0].StartAddress
        Byte_Input_1 = Object.Objects[" 32 Byte Input_1"][" 32 Byte Input"]["Object"].Addresses[0].StartAddress
        Byte_Output_1 = Object.Objects[" 32 Byte Output_1"][" 32 Byte Output"]["Object"].Addresses[0].StartAddress
        self.tags.addTag(self.unitName + "_Scanner_StatusWord","In","{0}.0".format(Ctrl_Bits_in_1),"typeScannerSickStatusInput","Scanner Status Signals","Scanner Tags")
        self.tags.addTag(self.unitName + "_Scanner_CtrlWord","Out","{0}.0".format(Ctrl_Bits_out_1),"typeScannerSickCtrlOutput","Scanner Ctrl Signals","Scanner Tags")
        self.tags.addTag(self.unitName + "_Scanner_Data_IN","In","{0}.0".format(Byte_Input_1),"typeScannerSickDataInput","Scanner Data Input","Scanner Tags")
        self.tags.addTag(self.unitName + "_Scanner_Data_OUT","Out","{0}.0".format(Byte_Output_1),"typeScannerSickDataOutput","Scanner Data Output","Scanner Tags")
        
    def export(self):
        XmlExport = swBlock.swBlock(self.xml.ObjectList)
        
        blockA = XmlExport.spawnPart("Emulation_Bit","Contact",True)
        XmlExport.addEN(blockA,"in")
        
        XmlExport.addCall()
        Health = XmlExport.CallId
        
        XmlExport.Component.set("Name","Inst" + self.unitNumber + "_Scanner_Health")
        XmlExport.CallInfo.set("Name","ProfinetDeviceHealthSelector")
        XmlExport.loadParameterStr('<Parameter Name="inData" Section="Input" Type="&quot;typeProfinetDeviceHealth&quot;"/>',"ProfinetDeviceHealth_DB.outData")
        XmlExport.loadParameterStr('<Parameter Name="inLADDR" Section="Input" Type="HW_INTERFACE"/>',self.unitNumber + "_SC~Interface")
        if self.software != None:
            self.software.Blocks.CreateInstanceDB(XmlExport.Component.get('Name'),True,1,XmlExport.CallInfo.get("Name"))
        XmlExport.addConnection(blockA,"out",Health,"en")
        
        XmlExport.addCall()
        blockB = XmlExport.CallId
        XmlExport.Component.set("Name","Inst" + self.unitNumber + "_Scanner")
        XmlExport.CallInfo.set("Name","ScannerSickCLV6xx")
        XmlExport.Comment.text = self.unitNumber + "_Scanner - ScannerSickCLV6xx - WcsCnvTrackedInterfaceDci"      
        
        XmlExport.loadParameterStr('<Parameter Name="inScannerStatusWord" Section="Input" Type="&quot;typeScannerSickStatusInput&quot;" />',self.unitNumber + "_Scanner_StatusWord")
        XmlExport.loadParameterStr('<Parameter Name="inScannerData" Section="Input" Type="&quot;typeScannerSickDataInput&quot;" />',self.unitNumber + "_Scanner_Data_IN")
        XmlExport.loadParameterStr('<Parameter Name="inConveyorStatus" Section="Input" Type="&quot;typeStatus&quot;" />',"Inst" + self.unitName + ".outStatus.place")
        XmlExport.loadParameterStr('<Parameter Name="inBusFault" Section="Input" Type="Bool" />',"Inst" + self.unitNumber + "_Scanner_Health.outFaultSumm")
        XmlExport.addParameter("inReadEnable","Input","Bool")
        x = XmlExport.spawnPart(self.unitName + "_PE_P","Contact",True)
        XmlExport.addEN(x,"in")
        XmlExport.addConnection(x,"out",XmlExport.CallId,"inReadEnable")
        XmlExport.loadParameterStr('<Parameter Name="inResetFault" Section="Input" Type="Bool" />',"Inst" + self.unitName + ".outResetFault")
        XmlExport.loadParameterStr('<Parameter Name="inConveyorRunning" Section="Input" Type="Bool" />',"Inst" + self.unitName + ".outPort12Motor.running")
        
        XmlExport.loadParameterStr('<Parameter Name="outScannerCtrlWord" Section="Output" Type="Bool" />',self.unitNumber + "_Scanner_CtrlWord")
        XmlExport.loadParameterStr('<Parameter Name="outScannerData" Section="Output" Type="&quot;typeScannerSickDataOutput&quot;" />',self.unitNumber + "_Scanner_Data_OUT")
        
        XmlExport.addConnection(Health,"eno",blockB,"en")
        if self.scl != None:
            #SCL ConFig
            scannerName = XmlExport.Component.get("Name")
            self.scl.addRegion(XmlExport.Component.get("Name"))
            self.scl.GlobalVariableEqualLiteralConstant(XmlExport.Component.get("Name") + ".inConfig.scannerId",'0')
            self.scl.GlobalVariableEqualConstant(XmlExport.Component.get("Name") + ".inConfig.dataLength","10")
            self.scl.GlobalVariableEqualTypedConstant(XmlExport.Component.get("Name") + ".inConfig.noReadTimeout","T#4S")
            self.scl.GlobalVariableEqualTypedConstant(XmlExport.Component.get("Name") + ".inConfig.retainTime","T#0s")
            self.scl.GlobalVariableEqualBool(XmlExport.Component.get("Name") + ".inConfig.triggerControl",True)            
            self.scl.GlobalVariableEqualBool(XmlExport.Component.get("Name") + ".inConfig.canBusEnabled",False)
            self.scl.GlobalVariableEqualLiteralConstant(XmlExport.Component.get("Name") + ".inConfig.noReadFaultLimit","3")
            self.scl.GlobalVariableEqualConstant(XmlExport.Component.get("Name") + ".inConfig.successfulReadThreshold","80")
            self.scl.GlobalVariableEqualTypedConstant(XmlExport.Component.get("Name") + ".inConfig.hmiControlZones.controlMask","2#0000_0000_0000_0000_0000_0000_0000_0001")
            self.scl.GlobalVariableEqualTypedConstant(XmlExport.Component.get("Name") + ".inConfig.panelMask","2#0000_0000_0000_0000_0000_0000_0000_0001")
            self.scl.GlobalVariableEqualBool(XmlExport.Component.get("Name") + ".inConfig.jamPresets.autoResetEnable",False)
            self.scl.GlobalVariableEqualTypedConstant(XmlExport.Component.get("Name") + ".inConfig.jamPresets.jamTime","T#3S")
            self.scl.GlobalVariableEqualTypedConstant(XmlExport.Component.get("Name") + ".inConfig.jamPresets.autoResetTime","T#5S")
            self.scl.endRegion()
            
        if self.software != None:
            try:
                self.software.Blocks.CreateInstanceDB(XmlExport.Component.get('Name'),True,1,XmlExport.CallInfo.get("Name"))
            except:
                pass
        
        XmlExport.addCall(False)
        XmlExport.CallInfo.set("Name","ScannerTrackedDataAdaptor")
        XmlExport.loadParameterStr('<Parameter Name="inData" Section="Input" Type="&quot;typeScannerReadData&quot;" />',"Inst" + self.unitNumber + "_Scanner.outData")
        XmlExport.loadParameterStr('<Parameter Name="inConveyorStatus" Section="Input" Type="&quot;typePortStatus1Unit&quot;" />',"Inst" + self.unitName + ".outStatus")
        
        XmlExport.addConnection(blockB,"eno",XmlExport.CallId,"en")
        
        blockC = XmlExport.spawnPart("Emulation_Bit","Contact")
        XmlExport.addEN(blockC,"in")
        
        XmlExport.addCall()
        blockD = XmlExport.CallId
        XmlExport.Component.set("Name","Inst" + self.unitNumber + "_Scanner_Fake")
        XmlExport.CallInfo.set("Name","EmulationScanner")
        XmlExport.addParameter("inReadEnable","Input","Bool")
        x = XmlExport.spawnPart(self.unitName + "_PE_P","Contact",True)
        XmlExport.addEN(x,"in")
        XmlExport.addConnection(x,"out",XmlExport.CallId,"inReadEnable")
        XmlExport.loadParameterStr('<Parameter Name="inDataRequired" Section="Input" Type="Bool"/>','',"LiteralConstant","Bool","true")
        XmlExport.loadParameterStr('<Parameter Name="inConvName" Section="Input" Type="String[14]"/>',"Inst" + self.unitName + ".outStatus.place.name")
        XmlExport.loadParameterStr('<Parameter Name="inResetFault" Section="Input" Type="Bool" />',"Inst" + self.unitName + ".outResetFault")
        
        XmlExport.addConnection(blockC,"out",blockD,"en")
        if self.scl != None:
            #SCL ConFig
            self.scl.addRegion(XmlExport.Component.get("Name"))
            self.scl.GlobalVariableEqualGlobalVariable(XmlExport.Component.get("Name") + ".inConfig.hmiControlZones.controlMask",scannerName + ".inConfig.hmiControlZones.controlMask")
            self.scl.GlobalVariableEqualGlobalVariable(XmlExport.Component.get("Name") + ".inConfig.panelMask",scannerName + ".inConfig.panelMask")
            self.scl.endRegion()
            
        if self.software != None:
            self.software.Blocks.CreateInstanceDB(XmlExport.Component.get('Name'),True,1,XmlExport.CallInfo.get("Name"))
            
        XmlExport.addCall(False)
        XmlExport.CallInfo.set("Name","ScannerTrackedDataAdaptor")
        XmlExport.loadParameterStr('<Parameter Name="inData" Section="Input" Type="&quot;typeScannerReadData&quot;" />',"Inst" + self.unitNumber + "_Scanner.outData")
        XmlExport.loadParameterStr('<Parameter Name="inConveyorStatus" Section="Input" Type="&quot;typePortStatus1Unit&quot;" />',"Inst" + self.unitName + ".outStatus")
        
        XmlExport.addConnection(blockD,"eno",XmlExport.CallId,"en")
        
        
        XmlExport.addCall()
        XmlExport.addEN(XmlExport.CallId,"en")
        XmlExport.Component.set("Name","Inst" + self.unitName + "_WCS")
        XmlExport.CallInfo.set("Name","WcsCnvTrackedInterfaceDci")
        XmlExport.loadParameterStr('<Parameter Name="inConveyorStatus" Section="Input" Type="&quot;typePortStatus1Unit&quot;"/>',"Inst" + self.unitName + ".outStatus")
        
        if self.scl != None:
            #SCL ConFig
            self.scl.addRegion(XmlExport.Component.get("Name"))
            self.scl.endRegion()
            
        if self.software != None:
            self.software.Blocks.CreateInstanceDB(XmlExport.Component.get('Name'),True,1,XmlExport.CallInfo.get("Name"))

class ConnectionBoxObject(father):
    def __init__(self,unitNumber,parent,ip,zone=""):
        self.unitNumber = unitNumber
        if zone != "":
            self.zone = "_" + zone
        self.unitName = self.unitNumber + self.zone
        self.name = self.unitNumber + self.zone
        super(ConnectionBoxObject,self).__init__(self.name,parent)
        self.project = parent.project
        self.software = parent.blockGroupSw
        self.xml = parent.xml
        self.scl = parent.scl
        self.tags = parent.tags
        self.subnet = parent.subnet
        self.ip = ip
        self.connectionNumber = re.search("U[0-9]{6}_Conn_Box_[0-9]{1}",self.name).group()[-1:]
        self.hardwareSetup()
        
    def hardwareSetup(self):
        typeIdentifier = "OrderNumber:6AV2 125-2AE23-0AX0"
        Object = device.ungroupedDevice(self.project,typeIdentifier + "/V5.2",self.unitName)
        Object.getNetworkInterface(Object.Objects[self.unitName]["SCALANCE interface_1"]["Object"])
        Object.setIp(self.ip,self.subnet)
        
    def export(self):
        if self.scl != None:
            #SCL ConFig
            self.scl.addRegion(self.name)
            self.scl.GlobalVariableEqualConstant('HMI.ConnectionPoints[{0}].connectionId'.format(self.connectionNumber),self.connectionNumber)
            self.scl.GlobalVariableEqualConstant('HMI.ConnectionPoints[{0}].controlZone.controlMask'.format(self.connectionNumber),"2#0000_0000_0000_0000_0000_0000_0000_0001")
            self.scl.endRegion()

class AsiABBDriveNAType01Object(father):
    def __init__(self,unitNumber,asiAddress,parent,zone=""):
        self.unitNumber = unitNumber
        if zone != "":
            self.zone = "_" + zone
        self.unitName = self.unitNumber + self.zone
        self.name = self.unitNumber + self.zone + "_AMD"
        super(AsiABBDriveNAType01Object,self).__init__(self.name,parent)
        self.project = parent.project
        self.software = parent.blockGroupSw
        self.xml = parent.xml
        self.scl = parent.scl
        self.tags = parent.tags
        self.subnet = parent.subnet
        elf.asiAddress = asiAddress
        self.ezcName = parent.name
        self.networkName = asiAddress.split("_")[1][:1]
        self.createAsiTags()
        
    def createAsiTags(self):
        if networkName in self.networkDevices:
            self.pnag = self.networkDevices[networkName]
            #self.pnag.addHalfNodeASI(self.name + "_NONSAFE",self.asiAddress + "A_I1")
            #self.pnag.addHalfNodeASI(self.name + "_LT_R",self.asiAddress + "A_O1")
            #self.pnag.addHalfNodeASI(self.name + "_LT_G",self.asiAddress + "A_O2")
        
        
    def export(self):
        XmlExport = swBlock.swBlock(self.xml.ObjectList)
        
        XmlExport.addCall()
        XmlExport.addEN(XmlExport.CallId,"en")
        XmlExport.Component.set("Name","Inst" + self.unitName + "_Drive1")
        XmlExport.CallInfo.set("Name","AsiABBDriveNAType01")
        XmlExport.loadParameterStr('<Parameter Name="inDriveFlags" Section="Input" Type="&quot;typeDriveFlags&quot;"/>',"Inst" + self.unitName + ".outPort12Motor")
        XmlExport.loadParameterStr('<Parameter Name="inAutoManSw" Section="Input" Type="Bool"/>',"Inst" + self.unitName + "_SS_AUT")
        XmlExport.loadParameterStr('<Parameter Name="inDriveRunning" Section="Input" Type="Bool"/>',"Inst" + self.unitName + "_RNG")
        XmlExport.loadParameterStr('<Parameter Name="inDriveFault" Section="Input" Type="Bool"/>',"Inst" + self.unitName + "_FLTD")
        XmlExport.loadParameterStr('<Parameter Name="outMotorFwd" Section="Output" Type="Bool"/>',"Inst" + self.unitName + "_RUN_FWD")
        XmlExport.loadParameterStr('<Parameter Name="outMotorRev" Section="Output" Type="Bool"/>',"Inst" + self.unitName + "_RUN_REV")
        XmlExport.loadParameterStr('<Parameter Name="outMotorFast" Section="Output" Type="Bool"/>',"Inst" + self.unitName + "_REF_1")
        XmlExport.loadParameterStr('<Parameter Name="outMotorFaultReset" Section="Output" Type="Bool"/>',"Inst" + self.unitName + "_CLR_FLT")
        
        if self.scl != None:
            #SCL ConFig
            self.scl.addRegion(self.Component.get("Name"))
            self.scl.GlobalVariableEqualLiteralConstant(self.Component.get("Name") + ".inConfig.driveIndex","1")
            self.scl.endRegion()
            
        if self.software != None:
            self.software.Blocks.CreateInstanceDB(self.Component.get('Name'),True,1,self.CallInfo.get("Name"))

class HmiObject(father):
    def __init__(self,name,parent,ip,zone=""):
        if zone != "":
            self.zone = "_" + zone
        self.name = name + self.zone
        super(HmiObject,self).__init__(self.name,parent)
        self.project = parent.project
        self.software = parent.blockGroupSw
        self.xml = parent.xml
        self.scl = parent.scl
        self.tags = parent.tags
        self.subnet = parent.subnet
        self.ip = ip
        self.hardwareSetup()
        
    def hardwareSetup(self):
        Object = device.GsdDevice(self.project.Devices.CreateFrom(self.project.ProjectLibrary.MasterCopyFolder.MasterCopies.Find("Systems-HMI1")))
        Object.Device.SetAttribute("Name",self.name)
        Object.startDiscovery()
        Object.getNetworkInterface(Object.Objects[self.name + ".IE_CP_1"]["PROFINET Interface_1"]["Object"])
        Object.networkInterface.SetAttribute("InterfaceOperatingMode",2)
        Object.setIp(self.ip,self.subnet)
        
    def export(self):
        if self.scl != None:
            #SCL ConFig
            pass

class PnpnObject(father):
    def __init__(self,name,parent,ip,zone=""):
        if zone != "":
            self.zone = "_" + zone
        self.name = name + self.zone + "_PNPN"
        super(PnpnObject,self).__init__(self.name,parent)
        self.project = parent.project
        self.software = parent.blockGroupSw
        self.xml = parent.xml
        self.scl = parent.scl
        self.tags = parent.tags
        self.subnet = parent.subnet
        self.ip = ip
        self.hardwareSetup()
        
    def hardwareSetup(self):
        typeIdentifier = "OrderNumber:6ES7 158-3AD10-0XA0"
        Object = device.ungroupedDevice(self.project,typeIdentifier + "/V4.2",self.name,self.name)
        Object.getNetworkInterface(Object.Objects[self.name]["PROFINET interface X1"]["Object"])
        Object.setIp(self.ip,self.subnet)
        
    def export(self):
        if self.scl != None:
            #SCL ConFig
            pass

class CallSetConfigObject(swBlock.swBlock):
    def __init__(self,Name,ObjectList):
        super(CallSetConfigObject,self).__init__(ObjectList)
        Call = self.createSubElement(self.Parts,"Call","UId")
        self.CallId = Call.get("UId")
        self.CallInfo = self.createSubElement(Call,"CallInfo")
        self.CallInfo.set("BlockType","FC")
        self.CallInfo.set("Name",Name)
        id = self.spawnPart("GlobalData.inGlobalData.checksumPulse","Contact")
        self.addEN(id,"in")
        self.addConnection(id,"out",self.CallId,"en")
        self.Comment.text = "Call " + Name

CC = controlCabnetObject("CC120")
#CC.spawnTestDevices()

CA121 = CC.createControlArea("CA121")

for x in range(0,17,2):
    CC.addScannerSickCLV6xx(f'U25{str(x).zfill(2)}30',"192.168.1.1","Z2",False)
    CC.addScannerSickCLV6xx(f'U25{str(x+1).zfill(2)}10',"192.168.1.1","Z4",False)
    
for x in range(0,36,2):
    CC.addScannerSickCLV6xx(f'U25{str(x).zfill(2)}60',"192.168.1.1","Z3",False)
    CC.addScannerSickCLV6xx(f'U25{str(x).zfill(2)}95',"192.168.1.1","Z1",False)
CC.addScannerSickCLV6xx(f'U140025',"192.168.1.1","Z2",False)
CC.save()
quit()
CA121.adoptNetworkDevice("U250530_PNAG_A")
CA121.adoptNetworkDevice("U251330_PNAG_B")
CA121.adoptNetworkDevice("U251730_PNAG_C")
CA121.adoptNetworkDevice("U250445_PNCG_01")
CA121.adoptNetworkDevice("U251245_PNCG_02")
CA121.adoptNetworkDevice("U251645_PNCG_03")

CA121EZC1 = CA121.addEzc("ASI_A1_13A")

CA121EZC1.addAsiEstop("U250030_PC_ES","ASI_A1_20")

CA121EZC1.addAsiEstop("U250110_PC_ES","ASI_A1_21")
CA121EZC1.addAsiEstop("U250130_PB_ES1","ASI_A1_25")
CA121EZC1.addAsiEstop("U250130_PB_ES2","ASI_A1_24")

CA121EZC2 = CA121.addEzc("ASI_A1_13B")

CA121EZC2.addAsiEstop("U250230_PC_ES","ASI_A1_22")
CA121EZC2.addAsiEstop("U250310_PC_ES","ASI_A1_23")
CA121EZC2.addAsiEstop("U250330_PB_ES1","ASI_A1_27")
CA121EZC2.addAsiEstop("U250330_PB_ES2","ASI_A1_26")

CA121EZC3 = CA121.addEzc("ASI_A2_13A")

CA121EZC3.addAsiEstop("U250430_PC_ES","ASI_A2_20")
CA121EZC3.addAsiEstop("U250510_PC_ES","ASI_A2_21")
CA121EZC3.addAsiEstop("U250530_PB_ES1","ASI_A2_25")
CA121EZC3.addAsiEstop("U250530_PB_ES2","ASI_A2_24")

CA121EZC4 = CA121.addEzc("ASI_A2_13B")

CA121EZC4.addAsiEstop("U250630_PC_ES","ASI_A2_22")
CA121EZC4.addAsiEstop("U250710_PC_ES","ASI_A2_23")
CA121EZC4.addAsiEstop("U250730_PB_ES1","ASI_A2_27")
CA121EZC4.addAsiEstop("U250730_PB_ES2","ASI_A2_26")

CA121EZC5 = CA121.addEzc("ASI_B1_13A")

CA121EZC5.addAsiEstop("U250830_PC_ES","ASI_B1_20")
CA121EZC5.addAsiEstop("U250910_PC_ES","ASI_B1_21")
CA121EZC5.addAsiEstop("U250930_PB_ES1","ASI_B1_25")
CA121EZC5.addAsiEstop("U250930_PB_ES2","ASI_B1_24")

CA121EZC6 = CA121.addEzc("ASI_B1_13B")

CA121EZC6.addAsiEstop("U251030_PC_ES","ASI_B1_22")
CA121EZC6.addAsiEstop("U251110_PC_ES","ASI_B1_23")
CA121EZC6.addAsiEstop("U251130_PB_ES1","ASI_B1_27")
CA121EZC6.addAsiEstop("U251130_PB_ES2","ASI_B1_26")

CA121EZC7 = CA121.addEzc("ASI_B2_13A")

CA121EZC7.addAsiEstop("U251230_PC_ES","ASI_B2_20")
CA121EZC7.addAsiEstop("U251310_PC_ES","ASI_B2_21")
CA121EZC7.addAsiEstop("U251330_PB_ES1","ASI_B2_25")
CA121EZC7.addAsiEstop("U251330_PB_ES2","ASI_B2_24")

CA121EZC8 = CA121.addEzc("ASI_B2_13B")

CA121EZC8.addAsiEstop("U251430_PC_ES","ASI_B2_22")
CA121EZC8.addAsiEstop("U251510_PC_ES","ASI_B2_23")
CA121EZC8.addAsiEstop("U251530_PB_ES1","ASI_B2_27")
CA121EZC8.addAsiEstop("U251530_PB_ES2","ASI_B2_26")

CA121EZC9 = CA121.addEzc("ASI_C1_13A")

CA121EZC9.addAsiEstop("U251630_PC_ES","ASI_C1_25")
CA121EZC9.addAsiEstop("U251710_PC_ES","ASI_C1_26")
CA121EZC9.addAsiEstop("U251730_PB_ES1","ASI_C1_28")
CA121EZC9.addAsiEstop("U251730_PB_ES2","ASI_C1_27")

CA122 = CC.createControlArea("CA122")

CA122.adoptNetworkDevice("U253600_PNAG_A")
CA122.adoptNetworkDevice("U140000_PNAG_B")

CA122.adoptNetworkDevice("U253600_PNCG_01")
CA122.adoptNetworkDevice("U253600_PNCG_02")
CA122.adoptNetworkDevice("U253600_PNCG_03")
CA122.adoptNetworkDevice("U253620_PNCG_04")
CA122.adoptNetworkDevice("U140000_PNCG_05")
CA122.adoptNetworkDevice("U140035_PNCG_06")
CA122.adoptNetworkDevice("U253600_PNCG_07")

CA122EZC1 = CA122.addEzc("ASI_A1_05A")

CA122EZC1.addAsiEstop("U250095_PB_ES","ASI_A1_29")
CA122EZC1.addAsiEstop("U253600_PC_ES1","ASI_A1_19")
CA122EZC1.addAsiEstop("U253600_PC_ES10","ASI_A1_18")
CA122EZC1.addAsiEstop("U253600_PC_ES11","ASI_A1_17")
CA122EZC1.addAsiEstop("U253600_PC_ES12","ASI_A1_16")
CA122EZC1.addAsiEstop("U253600_PC_ES13","ASI_A2_21")
CA122EZC1.addAsiEstop("U253600_PC_ES14","ASI_A2_22")
CA122EZC1.addAsiEstop("U253600_PC_ES15","ASI_A2_23")
CA122EZC1.addAsiEstop("U253600_PC_ES16","ASI_A2_24")
CA122EZC1.addAsiEstop("U253600_PC_ES17","ASI_A2_25")
CA122EZC1.addAsiEstop("U253600_PC_ES18","ASI_A2_26")
CA122EZC1.addAsiEstop("U253600_PC_ES2","ASI_A1_28")
CA122EZC1.addAsiEstop("U253600_PC_ES3","ASI_A1_27")
CA122EZC1.addAsiEstop("U253600_PC_ES4","ASI_A1_26")
CA122EZC1.addAsiEstop("U253600_PC_ES5","ASI_A1_25")
CA122EZC1.addAsiEstop("U253600_PC_ES6","ASI_A1_24")
CA122EZC1.addAsiEstop("U253600_PC_ES7","ASI_A1_23")
CA122EZC1.addAsiEstop("U253600_PC_ES8","ASI_A1_22")
CA122EZC1.addAsiEstop("U253600_PC_ES9","ASI_A1_21")
CA122EZC1.addAsiEstop("U253610_PC_ES","ASI_A2_27")
CA122EZC1.addAsiEstop("U253650_PC_ES","ASI_A2_28")

CA122EZC2 = CA122.addEzc("ASI_B1_14A")

CA122EZC2.addAsiEstop("U140000_PC_ES1","ASI_B1_08")
CA122EZC2.addAsiEstop("U140000_PC_ES2","ASI_B1_01")
CA122EZC2.addAsiEstop("U140055_PC_ES","ASI_B1_11")



#EStop1 = CA121EZC1.addAsiEstop("EStop1","ASI_C1_28")
#EStop2 = CA121EZC1.addAsiEstop("EStop2","ASI_A1_05")
#EStop3 = CA121EZC1.addAsiEstop("EStop3","ASI_A1_28")
#AUX1 = CA121EZC1.addAuxBox("ASI_C1_15A_I3")
#AUX2 = CA121EZC1.addDpsBox("ASI_C1_15A_I2")

#RPTR1 = CA121EZC1.addRptrBox("ASI_C1")

#AUX3 = CA121EZC2.addAuxBox("ASI_C1_16A_I3")
#DPS1 = CA121EZC1.addDpsBox("ASI_C1_16A_I2")
#DPS2 = CA121EZC1.addDpsBox("ASI_C1_16A_I2")
#DPS3 = CA121EZC1.addDpsBox("ASI_C1_16A_I3")
#DPS4 = CA121EZC1.addDpsBox("ASI_C1_16A_I4")
#DPS1.adoptPncg(PNCG_03,"1")
#DPS2.adoptPncg(PNCG_03,"1")
#DPS3.adoptPncg(PNCG_03,"1")
#DPS4.adoptPncg(PNCG_03,"1")

#CA111EZC3.addAuxBox("ASI_C1_17A_I3")
#CA111EZC3.addAuxBox("ASI_C1_17A_I4")
#CA111EZC3.addAuxBox("ASI_C1_18A_I3")
#CA111EZC3.addDpsBox("ASI_C1_18A_I4")
CC.save()


#print(CC.dataSorted)



