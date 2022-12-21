from xml.dom import minidom
import os
import Siemens.Engineering
import System.IO
import xml.etree.cElementTree as ET

global id
id = 0
"""
class fbObject():
    def __init__(self,plcSoftwareContainer,Name):
        self.fileName = Name
        blockGroup = plcSoftwareContainer.BlockGroup.Groups.Find("Project").Groups.Find(self.fileName)
        if blockGroup != None:
            blockGroup.Delete()
        plcSoftwareContainer.BlockGroup.Groups.Find("Project").Groups.Create(self.fileName)
        self.softwareContainer = plcSoftwareContainer.BlockGroup.Groups.Find("Project").Groups.Find(self.fileName)
        self.xml = xmlDocument(self.fileName)
    
    def addAbbAcs380Drive(self,unitName):
        block = self.xml.addAbbAcs380Drive(unitName)
        instanceDB = self.softwareContainer.Blocks.CreateInstanceDB(block.Component.get('Name'),True,1,block.CallInfo.get("Name"))
        
    def addAsiABBDriveNAType01(self,unitName):
        block =  self.xml.addAsiABBDriveNAType01(unitName)
        instanceDB = self.softwareContainer.Blocks.CreateInstanceDB(block.Component.get('Name'),True,1,block.CallInfo.get("Name"))
        
    def addScannerSickCLV62x(self,unitName,zone = ""):
        block =  self.xml.addScannerSickCLV62x(unitName,zone)
        instanceDB = self.softwareContainer.Blocks.CreateInstanceDB(block.Component.get('Name'),True,1,block.CallInfo.get("Name"))
        
    def importRoutine(self):
        with open(self.fileName, "w") as file:
            file.write(minidom.parseString(ET.tostring(self.xml.root)).toprettyxml(indent = "\t"))
        fileStr = os.getcwd() + "/" + self.fileName
        self.softwareContainer.Blocks.Import(System.IO.FileInfo(fileStr),Siemens.Engineering.ImportOptions.Override)
        fcImport = self.softwareContainer.Blocks.Find(self.fileName)
        ICompilable = Siemens.Engineering.IEngineeringServiceProvider(fcImport).GetService[Siemens.Engineering.Compiler.ICompilable]()
        ICompilable.Compile()
        

        
class xmlDocument():
    def __init__(self,fileName):
        self.root = ET.Element("Document")
        SWBlocksFC = self.createSubElement(self.root, "SW.Blocks.FC","ID")
        AttributeList = self.createSubElement(SWBlocksFC,"AttributeList")
        self.createSubElement(AttributeList,"AutoNumber").text = "true"
        self.createSubElement(AttributeList,"MemoryLayout").text = "Optimized"
        self.createSubElement(AttributeList,"Name").text = str(fileName)
        self.ProgrammingLanguage = self.createSubElement(AttributeList,"ProgrammingLanguage").text = "LAD"
        self.ObjectList = self.createSubElement(SWBlocksFC,"ObjectList")
        self.addLine()
        
    def createSubElement(self,parent,name,type = None):
        global id
        child = ET.SubElement(parent,name)
        if type != None:
            child.set(type, str(id))
            id = id + 1
        return child
        
    def returnChildNode(self,parent,childNodeName):
        y = 0
        for x in parent.childNodes:
            if x.nodeName == childNodeName:
                return parent.childNodes[y]
            y = y + 1
        return None
            
    def addAbbAcs380Drive(self,unitName):
        block = AbbAcs380Drive(unitName)
        return block
        
    def addAsiABBDriveNAType01(self,unitName):
        block = AsiABBDriveNAType01(unitName)
        return block
        
    def addScannerSickCLV62x(self,unitName,zone):
        block = ScannerSickCLV62x(unitName,zone)
        return block
        
    def __str__(self):
        with open('Test', "w") as file:
            file.write(minidom.parseString(ET.tostring(self.root)).toprettyxml(indent = "\t"))
        return minidom.parseString(ET.tostring(self.root)).toprettyxml(indent = "\t")
        
    def returnRoot(self):
        return self.root.childNodes[0]
        
    def addLine(self):
        SWBlocksCompileUnit = self.createSubElement(self.ObjectList, "SW.Blocks.CompileUnit","ID")
        SWBlocksCompileUnit.set("CompositionName", "CompileUnits")
        AttributeList = self.createSubElement(SWBlocksCompileUnit,"AttributeList")
        NetworkSource = self.createSubElement(AttributeList,"NetworkSource")
        FlgNet = self.createSubElement(NetworkSource,"FlgNet")
        FlgNet.set("xmlns","http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v4")
        self.Parts = self.createSubElement(FlgNet,"Parts")
        self.Wires = self.createSubElement(FlgNet,"Wires")
        Call = self.createSubElement(self.Parts,"Call","UId")
        self.CallId = Call.get("UId")
        self.CallInfo = self.createSubElement(Call,"CallInfo")
        self.CallInfo.set("BlockType","FB")
        Instance = self.createSubElement(self.CallInfo,"Instance","UId")
        Instance.set("Scope","GlobalVariable")
        self.Component = self.createSubElement(Instance,"Component")
        self.addEn()
        
    def addEn(self):
        Wire = self.createSubElement(self.Wires,"Wire","UId")
        Powerrail = self.createSubElement(Wire,"Powerrail")
        NameCon = self.createSubElement(Wire,"NameCon")
        NameCon.set("UId",str(self.CallId))
        NameCon.set("Name","en") 
        
class fcBlock(xmlDocument):
    def __init__(self):
        self.loadParameterStr('<Parameter Name="inGlobalData" Section="Input" Type="&quot;typeInGlobalData&quot;" />',"GlobalData.inGlobalData")
        self.loadParameterStr('<Parameter Name="inoutGlobalData" Section="InOut" Type="&quot;typeInOutGlobalData&quot;" />',"GlobalData.inoutGlobalData")
        self.loadParameterStr('<Parameter Name="inoutLoggingDB" Section="InOut" Type="&quot;typeLoggingDB&quot;" />',"LoggingOptimizedDB.loggingDB")
        
    def addParameter(self,parameterName,inOutType,dataType):
        Parameter = self.createSubElement(self.CallInfo,"Parameter")
        Parameter.set("Name",parameterName)
        Parameter.set("Section",inOutType)
        Parameter.set("Type",dataType)
        
    def addAccess(self,string,parameterName):
        Access = self.createSubElement(self.Parts,"Access","UId")
        Access.set("Scope","GlobalVariable")
        Symbol = self.createSubElement(Access,"Symbol")
        list = string.split(".")
        for x in list:
            Component = self.createSubElement(Symbol,"Component")
            Component.set("Name",x)
        return Access.get("UId")
        
    def addIdentCon(self,linkedId,parameterName):
        Wire = self.createSubElement(self.Wires,"Wire","UId")
        IdentCon = self.createSubElement(Wire,"IdentCon")
        IdentCon.set("UId",str(linkedId))
        NameCon = self.createSubElement(Wire,"NameCon")
        NameCon.set("UId",str(self.CallId))
        NameCon.set("Name",parameterName)
        
    def addOpenCon(self,parameterName):
        Wire = self.createSubElement(self.Wires,"Wire","UId")
        OpenCon = self.createSubElement(Wire,"OpenCon","UId")
        NameCon = self.createSubElement(Wire,"NameCon")
        NameCon.set("UId",str(self.CallId))
        NameCon.set("Name",parameterName)
        
    def addParameterAccessWire(self,connectionName,parameterName,inOutType,dataType):
        self.addParameter(parameterName,inOutType,dataType)
        accessId = self.addAccess(connectionName,parameterName)
        self.addIdentCon(accessId,parameterName)
        
    def addParameterWire(self,parameterName,inOutType,dataType):
        self.addParameter(parameterName,inOutType,dataType)
        self.addOpenCon(parameterName)
        
    def loadParameterStr(self,strParameter,connectionName = None):
        document = ET.fromstring(strParameter)
        if connectionName == None:
            self.addParameterWire(document.get("Name"),document.get("Section"),document.get("Type"))
        else:
            self.addParameterAccessWire(connectionName,document.get("Name"),document.get("Section"),document.get("Type"))
 

class AbbAcs380Drive(fcBlock):
     def __init__(self,unitName):
        super().__init__()
        #Set Name
        self.Component.set("Name","Inst" + unitName + "_Drive1")
        
        #Set type of block
        self.CallInfo.set("Name","AbbAcs380Drive")
        
        #Add Connections-Parameters relationships
        self.loadParameterStr('<Parameter Name="inDriveStatus" Section="Input" Type="&quot;typeABBACS380InputsPP04&quot;" />',unitName + "_IN")
        self.loadParameterStr('<Parameter Name="inConveyorStatus" Section="Input" Type="&quot;typePortStatus1Unit&quot;" />',"Inst" + unitName + ".outStatus")
        self.loadParameterStr('<Parameter Name="inDriveFlags" Section="Input" Type="&quot;typeDriveFlags&quot;" />',"Inst" + unitName + ".outPort12Motor")
        self.loadParameterStr('<Parameter Name="outDriveCommand" Section="Output" Type="&quot;typeABBACS380OutputsPP04&quot;" />',unitName + "_OUT")
        

class AsiABBDriveNAType01(fcBlock):
    def __init__(self,unitName):
        super().__init__()
        self.Component.set("Name","Inst" + unitName + "_Drive1")
        
        self.CallInfo.set("Name","AsiABBDriveNAType01")
        
        self.addParameterAccessWire("GlobalData.inGlobalData.alarms","inAlarmSignals","Input","&quot;typeSystemAlarms&quot;")
        self.addParameterAccessWire("GlobalData.inGlobalData.checksumPulse","inChecksumPulse","Input","Bool")
        self.addParameterAccessWire("Inst" + unitName + ".outPort12Motor","inDriveFlags","Input","&quot;typeDriveFlags&quot;")
        self.addParameterAccessWire("Inst" + unitName + "_SS_AUT","inAutoManSw","Input","Bool;")
        self.addParameterAccessWire("Inst" + unitName + "_RNG","inDriveRunning","Input","Bool;")
        self.addParameterAccessWire("Inst" + unitName + "_FLTD","inDriveFault","Input","Bool;")
        self.addParameterAccessWire("Inst" + unitName + "_RUN_FWD","outMotorFwd","Output","Bool;")
        self.addParameterAccessWire("Inst" + unitName + "_RUN_REV","outMotorRev","Output","Bool;")
        self.addParameterAccessWire("Inst" + unitName + "_REF_1","outMotorFast","Output","Bool;")
        self.addParameterAccessWire("Inst" + unitName + "_CLR_FLT","outMotorFaultReset","Output","Bool;")
        

class ScannerSickCLV62x(fcBlock):
    def __init__(self,unitName,zone):
        super().__init__()
        unitName = unitName + zone
        
        self.Component.set("Name","Inst" + unitName + "Scanner")
        
        self.CallInfo.set("Name","ScannerSickCLV62x")
        
        self.loadParameterStr('<Parameter Name="inScannerInput" Section="Input" Type="&quot;typeScannerInputsSickCLV62x&quot;" />',unitName + "_Scanner_IN")
        self.loadParameterStr('<Parameter Name="inReadEnable" Section="Input" Type="Bool" />', unitName + "_PE_P")
        self.loadParameterStr('<Parameter Name="inConveyorStatus" Section="Input" Type="&quot;typePortStatus1Unit&quot;" />',"Inst" + unitName + ".outStatus")
        self.loadParameterStr('<Parameter Name="inResetFault" Section="Input" Type="Bool" />',"Inst" + unitName + ".outResetFault")
        self.loadParameterStr('<Parameter Name="outScannerTrigger" Section="Output" Type="Bool" />',unitName + "_ScannerTrigger")
        self.loadParameterStr('<Parameter Name="inoutFaultBuffer" Section="InOut" Type="Array[*] of &quot;typeAlarmBufferEntry&quot;" />',"Alarms.faultBuffer")
        self.loadParameterStr('<Parameter Name="inoutWarningBuffer" Section="InOut" Type="Array[*] of &quot;typeAlarmBufferEntry&quot;" />',"Alarms.warningBuffer")
        
        REGION SB253510_Z4Scanner
         "InstSB253510_Z4Scanner".inConfig.dataLength := 10;
         "InstSB253510_Z4Scanner".inConfig.noReadBarcode := '00000000';
         "InstSB253510_Z4Scanner".inConfig.noDataTimeout := T#4S;
         "InstSB253510_Z4Scanner".inConfig.configuration.noReadFaultLimit := 3;
         "InstSB253510_Z4Scanner".inConfig.configuration.successfulReadThreshold := 80;
      END_REGION


#test = xmlDocument("Test")
#print(test)
"""