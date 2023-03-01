from swBlock import swBlock

"""
class AbbAcs380Drive(swBlock):
    def __init__(self,unitNumber,ObjectList,zone="",scl=None,software=None):
        super().__init__(ObjectList)
        unitName = unitNumber + zone
        self.addCall()
        self.addEN(self.CallId,"en")
        self.Component.set("Name","Inst" + unitName + "_Drive1")
        self.CallInfo.set("Name","AbbAcs380Drive")
        self.Comment.text = unitName + "_Drive1"
        
        self.loadParameterStr('<Parameter Name="inDriveStatus" Section="Input" Type="&quot;typeABBACS380InputsPP04&quot;" />',unitName + "_FMD_In")
        self.loadParameterStr('<Parameter Name="inConveyorStatus" Section="Input" Type="&quot;typePortStatus1Unit&quot;" />',"Inst" + unitName + ".outStatus")
        self.loadParameterStr('<Parameter Name="inDriveFlags" Section="Input" Type="&quot;typeDriveFlags&quot;" />',"Inst" + unitName + ".outPort12Motor")
        self.loadParameterStr('<Parameter Name="outDriveCommand" Section="Output" Type="&quot;typeABBACS380OutputsPP04&quot;" />',unitName + "_FMD_Out")
        
        if scl != None:
            #SCL ConFig
            pass
            
        if software != None:
            software.Blocks.CreateInstanceDB(self.Component.get('Name'),True,1,self.CallInfo.get("Name"))
        

class AsiABBDriveNAType01(swBlock):
    def __init__(self,unitNumber,ObjectList,zone="",scl=None,software=None):
        super().__init__(ObjectList)
        unitName = unitNumber + zone
        self.addCall()
        self.addEN(self.CallId,"en")
        self.Component.set("Name","Inst" + unitName + "_Drive1")
        self.CallInfo.set("Name","AsiABBDriveNAType01")
        self.loadParameterStr('<Parameter Name="inDriveFlags" Section="Input" Type="&quot;typeDriveFlags&quot;"/>',"Inst" + unitName + ".outPort12Motor")
        self.loadParameterStr('<Parameter Name="inAutoManSw" Section="Input" Type="Bool"/>',"Inst" + unitName + "_SS_AUT")
        self.loadParameterStr('<Parameter Name="inDriveRunning" Section="Input" Type="Bool"/>',"Inst" + unitName + "_RNG")
        self.loadParameterStr('<Parameter Name="inDriveFault" Section="Input" Type="Bool"/>',"Inst" + unitName + "_FLTD")
        self.loadParameterStr('<Parameter Name="outMotorFwd" Section="Output" Type="Bool"/>',"Inst" + unitName + "_RUN_FWD")
        self.loadParameterStr('<Parameter Name="outMotorRev" Section="Output" Type="Bool"/>',"Inst" + unitName + "_RUN_REV")
        self.loadParameterStr('<Parameter Name="outMotorFast" Section="Output" Type="Bool"/>',"Inst" + unitName + "_REF_1")
        self.loadParameterStr('<Parameter Name="outMotorFaultReset" Section="Output" Type="Bool"/>',"Inst" + unitName + "_CLR_FLT")
        
        if scl != None:
            #SCL ConFig
            scl.addRegion(self.Component.get("Name"))
            scl.GlobalVariableEqualLiteralConstant(self.Component.get("Name") + ".inConfig.driveIndex","1")
            scl.endRegion()
            
        if software != None:
            software.Blocks.CreateInstanceDB(self.Component.get('Name'),True,1,self.CallInfo.get("Name"))
            
class MoviMot(swBlock):
    def __init__(self,unitNumber,ObjectList,zone="",scl=None,software=None):
        super().__init__(ObjectList)
        unitName = unitNumber + zone
        self.addCall()
        self.addEN(self.CallId,"en")
        self.Component.set("Name","Inst" + unitName + "_Drive1")
        self.CallInfo.set("Name","ProfinetMoviMot")
        
        self.loadParameterStr('<Parameter Name="inIsolatorSwitchOk" Section="Input" Type="Bool"/>','',"LiteralConstant","Bool","true")
        self.loadParameterStr('<Parameter Name="inDriveStatus" Section="Input" Type="&quot;typeProfinetMoviMotInputs&quot;" />',unitName + "_MMD_In")
        self.loadParameterStr('<Parameter Name="inDriveFlags" Section="Input" Type="&quot;typeDriveFlags&quot;"/>',"Inst" + unitName + ".outPort12Motor")
        
        self.loadParameterStr('<Parameter Name="outDriveControl" Section="Output" Type="&quot;typeProfinetMoviMotOutputs&quot;" />',unitName + "_MMD_Out")
        
        if scl != None:
            #SCL ConFig
            scl.addRegion(self.Component.get("Name"))
            scl.GlobalVariableEqualLiteralConstant(self.Component.get("Name") + ".inConfig.driveIndex","1")
            scl.endRegion()
            
        if software != None:
            software.Blocks.CreateInstanceDB(self.Component.get('Name'),True,1,self.CallInfo.get("Name"))
        
        
class ScannerSickCLV6xx(swBlock):
    def __init__(self,unitNumber,ObjectList,zone="",scl=None,software=None):
        super().__init__(ObjectList)
        unitName = unitNumber + zone
        self.addCall()
        self.addEN(self.CallId,"en")
        self.Component.set("Name","Inst" + unitName + "_Scanner")
        self.CallInfo.set("Name","ScannerSickCLV6xx")
        self.Comment.text = unitName + "_Scanner"      
        
        self.loadParameterStr('<Parameter Name="inScannerStatusWord" Section="Input" Type="&quot;typeScannerSickStatusInput&quot;" />',unitNumber + "_Scanner_StatusWord")
        self.loadParameterStr('<Parameter Name="inScannerData" Section="Input" Type="&quot;typeScannerSickDataInput&quot;" />',unitNumber + "_Scanner_Data_IN")
        self.loadParameterStr('<Parameter Name="inConveyorStatus" Section="Input" Type="&quot;typePortStatus1Unit&quot;" />',"Inst" + unitName + ".outStatus.place")
        self.addParameter("inReadEnable","Input","Bool")
        x = self.spawnPart(unitName + "_PE_P","Contact",True)
        self.addEN(x,"in")
        self.addConnection(x,"out",self.CallId,"inReadEnable")
        self.loadParameterStr('<Parameter Name="inResetFault" Section="Input" Type="Bool" />',"Inst" + unitName + ".outResetFault")
        self.loadParameterStr('<Parameter Name="inConveyorRunning" Section="Input" Type="Bool" />',"Inst" + unitName + ".outPort12Motor.running")
        
        self.loadParameterStr('<Parameter Name="outScannerCtrlWord" Section="Output" Type="Bool" />',unitNumber + "_Scanner_CtrlWord")
        self.loadParameterStr('<Parameter Name="outScannerData" Section="Output" Type="&quot;typeScannerSickDataOutput&quot;" />',unitNumber + "_Scanner_Data_OUT")
        
        if scl != None:
            #SCL ConFig
            scl.addRegion(self.Component.get("Name"))
            scl.GlobalVariableEqualLiteralConstant(self.Component.get("Name") + ".inConfig.scannerId",'0')
            scl.GlobalVariableEqualConstant(self.Component.get("Name") + ".inConfig.dataLength","10")
            scl.GlobalVariableEqualTypedConstant(self.Component.get("Name") + ".inConfig.noReadTimeout","T#4S")
            scl.GlobalVariableEqualTypedConstant(self.Component.get("Name") + ".inConfig.retainTime","T#0s")
            scl.GlobalVariableEqualBool(self.Component.get("Name") + ".inConfig.triggerControl",True)            
            scl.GlobalVariableEqualBool(self.Component.get("Name") + ".inConfig.canBusEnabled",False)
            scl.GlobalVariableEqualLiteralConstant(self.Component.get("Name") + ".inConfig.noReadFaultLimit","3")
            scl.GlobalVariableEqualConstant(self.Component.get("Name") + ".inConfig.successfulReadThreshold","80")
            scl.GlobalVariableEqualTypedConstant(self.Component.get("Name") + ".inConfig.hmiControlZones.controlMask","2#0000_0000_0000_0000_0000_0000_0000_0001")
            scl.GlobalVariableEqualTypedConstant(self.Component.get("Name") + ".inConfig.panelMask","2#0000_0000_0000_0000_0000_0000_0000_0001")
            scl.GlobalVariableEqualBool(self.Component.get("Name") + ".inConfig.jamPresets.autoResetEnable",False)
            scl.GlobalVariableEqualTypedConstant(self.Component.get("Name") + ".inConfig.jamPresets.jamTime","T#3S")
            scl.GlobalVariableEqualTypedConstant(self.Component.get("Name") + ".inConfig.jamPresets.autoResetTime","T#5S")
            scl.endRegion()
            
        if software != None:
            software.Blocks.CreateInstanceDB(self.Component.get('Name'),True,1,self.CallInfo.get("Name"))
        
class FortressGate(swBlock):
    def __init__(self,unitNumber,Failsafe_FIODBName,ObjectList,zone="",scl=None,software=None):
        FortressGateSwitch(unitNumber,ObjectList,zone,scl,software)
        FortressGateSwitchSafety(unitNumber,ObjectList,Failsafe_FIODBName,zone,scl,software)
        FortressGateSwitchVis(unitNumber,ObjectList,zone,scl,software)
        
class FortressGateSwitch(swBlock):
    def __init__(self,unitNumber,ObjectList,zone="",scl=None,software=None):
        super().__init__(ObjectList)
        unitName = unitNumber + zone + "_GS"
        self.addCall()
        self.Comment.text = unitName.split("_")[0] + "_GS"
        self.addEN(self.CallId,"en")
        self.Component.set("Name","Inst" + unitName)
        self.CallInfo.set("Name","FortressGateSwitch")
        self.loadParameterStr('<Parameter Name="inRequestAccess" Section="Input" Type="Bool"/>',unitName + "_RQ_PB")
        self.loadParameterStr('<Parameter Name="inAccessGranted" Section="Input" Type="Bool"/>','',"LiteralConstant","Bool","true")
        self.loadParameterStr('<Parameter Name="inUnlockSwitch" Section="Input" Type="Bool"/>',unitName + "_G_SW")
        self.loadParameterStr('<Parameter Name="inGateMonitor" Section="Input" Type="Bool"/>',unitName + "_GateMon")
        self.loadParameterStr('<Parameter Name="inResetRequest" Section="Input" Type="Bool"/>',unitName + "_RS_PB")
        self.loadParameterStr('<Parameter Name="outGateSolenoid" Section="Output" Type="Bool"/>',unitName + "_Sol_Drive")
        self.loadParameterStr('<Parameter Name="outGateSwitchLamp" Section="Output" Type="Bool"/>',unitName + "_G_LT")
        self.loadParameterStr('<Parameter Name="outResetLamp" Section="Output" Type="Bool"/>',unitName + "_RS_LT")
        self.loadParameterStr('<Parameter Name="outRequestLamp" Section="Output" Type="Bool"/>',unitName + "_RQ_LT")
        
        if scl != None:
            #SCL ConFig
            pass
            
        if software != None:
            software.Blocks.CreateInstanceDB(self.Component.get('Name'),True,1,self.CallInfo.get("Name"))
           
class FortressGateSwitchSafety(swBlock):
    def __init__(self,unitNumber,ObjectList,Failsafe_FIODBName,zone="",scl=None,software=None):
        super().__init__(ObjectList)
        self.addCall()
        unitName = unitNumber + zone + "_GS"
        self.Comment.text = unitName + "_FS"
        self.addEN(self.CallId,"en")
        self.Component.set("Name","Inst" + unitName + " Gate Switch Safety")
        self.CallInfo.set("Name","FortressGateSwitchSafety")
        self.loadParameterStr('<Parameter Name="inEstopPB1" Section="Input" Type="Bool"/>',unitName + "_Estop_1")
        self.loadParameterStr('<Parameter Name="inEstopPB2" Section="Input" Type="Bool"/>',unitName + "_Estop_2")
        self.loadParameterStr('<Parameter Name="inHead1" Section="Input" Type="Bool"/>',unitName + "_Sol_1")
        self.loadParameterStr('<Parameter Name="inHead2" Section="Input" Type="Bool"/>',unitName + "_Sol_2")
        self.loadParameterStr('<Parameter Name="inAck" Section="Input" Type="Bool"/>',"tempEstopReset","LocalVariable")
        self.loadParameterStr('<Parameter Name="inQbad" Section="Input" Type="Bool"/>',Failsafe_FIODBName + ".QBAD")
        self.loadParameterStr('<Parameter Name="inAccessGranted" Section="Input" Type="Bool"/>','',"LiteralConstant","Bool","true")
        
        if scl != None:
            #SCL ConFig
            pass
            
        if software != None:
            software.Blocks.CreateInstanceDB(self.Component.get('Name'),True,1,self.CallInfo.get("Name"))
        
class FortressGateSwitchVis(swBlock):
    def __init__(self,unitNumber,ObjectList,zone="",scl=None,software=None):
        super().__init__(ObjectList)
        self.addCall()
        unitName = unitNumber + zone + "_GS"
        self.Comment.text = unitName + "_Vis"
        self.addEN(self.CallId,"en")
        self.Component.set("Name","Inst" + unitName + "_Vis")
        
        self.CallInfo.set("Name","EmergencyStop")
        self.addParameter("inEStopStatus","Input","Bool")
        self.loadParameterStr('<Parameter Name="inZoneStatus" Section="Input" Type="Bool"/>','',"LiteralConstant","Bool","false")
        self.loadParameterStr('<Parameter Name="inLocation" Section="Input" Type="String[14]"/>','',"LiteralConstant","String",unitNumber)
        self.loadParameterStr('<Parameter Name="inConfigContactType" Section="Input" Type="Bool"/>','',"LiteralConstant","Bool","false")
        self.loadParameterStr('<Parameter Name="inAsiBusFault" Section="Input" Type="Bool"/>','',"LiteralConstant","Bool","false")
        
        x = self.spawnPart(unitName + "_Estop_1","Contact")
        self.addEN(x,"in")
        y = self.spawnPart(unitName + "_Estop_2","Contact")
        self.addEN(y,"in")
        z = self.addOR("2")
        self.addConnection(x,"out",z,"in1")
        self.addConnection(y,"out",z,"in2")
        self.addConnection(z,"out",self.CallId,"inEStopStatus")
        
        if scl != None:
            #SCL ConFig
            pass
            
        if software != None:
            software.Blocks.CreateInstanceDB(self.Component.get('Name'),True,1,self.CallInfo.get("Name"))
        
        
        
class EStopVis(swBlock):
    def __init__(self,ControlArea,Pnag,Ezc,unitName,ObjectList,scl=None,software=None):
        super().__init__(ObjectList)
        
        self.addCall()
        self.addEN(self.CallId,"en")
        self.Component.set("Name","Inst" + unitName + "_Vis")
        
        self.CallInfo.set("Name","EmergencyStop")
        self.Comment.text = unitName + "_Vis"
        self.addParameter("inEStopStatus","Input","Bool")
        self.loadParameterStr('<Parameter Name="inZoneStatus" Section="Input" Type="Bool"/>','Inst' + ControlArea + Ezc + '_FC.outEStopHealthy')
        self.loadParameterStr('<Parameter Name="inLocation" Section="Input" Type="String[14]"/>','',"LiteralConstant","String",unitName.split("_")[0])
        self.loadParameterStr('<Parameter Name="inConfigContactType" Section="Input" Type="Bool"/>','',"LiteralConstant","Bool","false")
        self.loadParameterStr('<Parameter Name="inAsiBusFault" Section="Input" Type="Bool"/>','Inst' + Pnag + '.outVisuInterface.status.summary')
        
        x = self.spawnPart(unitName,"Contact")
        self.addEN(x,"in")
        y = self.spawnPart(unitName + "_NONSAFE","Contact")
        self.addEN(y,"in")
        z = self.addOR("2")
        self.addConnection(x,"out",z,"in1")
        self.addConnection(y,"out",z,"in2")
        self.addConnection(z,"out",self.CallId,"inEStopStatus")
        
        a = self.spawnPart(self.Component.get("Name") + ".outEstopLamp","Contact")
        self.addEN(a,"in")
        b = self.spawnPart(unitName + "_LT_R","Coil")
        self.addConnection(a,"out",b,"in")
        
        c = self.spawnPart(self.Component.get("Name") + ".outEstopLamp","Contact",True)
        self.addEN(c,"in")
        d = self.spawnPart(unitName + "_NONSAFE","Contact")
        e = self.spawnPart(unitName + "_LT_G","Coil")
        self.addConnection(c,"out",d,"in")
        self.addConnection(d,"out",e,"in")
        
        if scl != None:
            #SCL ConFig
            pass
        
        if software != None:
            software.Blocks.CreateInstanceDB(self.Component.get('Name'),True,1,self.CallInfo.get("Name"))
        
class CallSetConfig(swBlock):
    def __init__(self,Name,ObjectList):
        super().__init__(ObjectList)
        Call = self.createSubElement(self.Parts,"Call","UId")
        self.CallId = Call.get("UId")
        self.CallInfo = self.createSubElement(Call,"CallInfo")
        self.CallInfo.set("BlockType","FC")
        self.CallInfo.set("Name",Name)
        id = self.spawnPart("GlobalData.inGlobalData.checksumPulse","Contact")
        self.addEN(id,"in")
        self.addConnection(id,"out",self.CallId,"en")
        self.Comment.text = "Call " + Name
        
        
class Plc(swBlock):
    def __init__(self,CabnetNumber,EZCName,ObjectList,scl=None,software=None):
        super().__init__(ObjectList)
        self.addCall()
        self.Comment.text = CabnetNumber
        self.addEN(self.CallId,"en")
        self.Component.set("Name","Inst" + CabnetNumber)
        self.CallInfo.set("Name","Plc")
        
        self.loadParameterStr('<Parameter Name="inWcsCommsHealthy" Section="Input" Type="Bool" />',"InstDciManager.outConnected")
        self.loadParameterStr('<Parameter Name="inSafetyStatusToPlc" Section="Input" Type="&quot;typeSafetyStatusToMainPanel&quot;" />',"DataFromSafety.SafetyStatusToPLC")
        
        if scl != None:
            #SCL ConFig
            scl.addRegion(self.Component.get("Name"))
            scl.GlobalVariableEqualBool(self.Component.get("Name") + ".inConfig.resetConveyorsFromPanel",True)
            scl.GlobalVariableEqualBool(self.Component.get("Name") + ".inConfig.disableCompressedAirAlarm",False)
            for x in range(len(EZCName)):
                scl.GlobalVariableEqualBool("{0}.inConfig.enableEzc[{1}]".format(self.Component.get("Name"),str(x + 1)),True)
            scl.endRegion()
            
        if software != None:
            software.Blocks.CreateInstanceDB(self.Component.get('Name'),True,1,self.CallInfo.get("Name"))
        
        
class PnagBox(swBlock):
    def __init__(self,CabnetNumber,PnagName,ObjectList,scl=None,software=None):
        super().__init__(ObjectList)
        self.addCall()
        blockA = self.CallId
        self.Comment.text = PnagName
        self.addEN(self.CallId,"en")
        self.Component.set("Name","Inst" + PnagName + "_Health")
        self.CallInfo.set("Name","ProfinetDeviceHealthSelector")
        self.loadParameterStr('<Parameter Name="inData" Section="Input" Type="&quot;typeProfinetDeviceHealth&quot;"/>',"ProfinetDeviceHealth_DB.outData")
        self.loadParameterStr('<Parameter Name="inLADDR" Section="Input" Type="HW_INTERFACE"/>',PnagName + "~PN-IO")
        if software != None:
            software.Blocks.CreateInstanceDB(self.Component.get('Name'),True,1,self.CallInfo.get("Name"))
        
        self.addCall()
        self.Component.set("Name","Inst" + PnagName)
        self.CallInfo.set("Name","PnagBox")
        self.addParameter("inAsiGatewayBusFault","Input","Bool")
        self.loadParameterStr('<Parameter Name="inMainPanelToPnag" Section="Input" Type="Bool"/>','Inst' + CabnetNumber + '.outPlcStatus')
        self.loadParameterStr('<Parameter Name="inAsiCmdReceive" Section="Input" Type="&quot;typeAsiCommandReceive&quot;"/>',PnagName + 'CommandIn')
        self.loadParameterStr('<Parameter Name="inFlagsChn0" Section="Input" Type="&quot;typeAsiChannelFlags&quot;"/>',PnagName + 'FlagsChn0')
        self.loadParameterStr('<Parameter Name="inFlagsChn1" Section="Input" Type="&quot;typeAsiChannelFlags&quot;"/>',PnagName + 'FlagsChn1')
        self.loadParameterStr('<Parameter Name="outAsiCmdSend" Section="Output" Type="&quot;typeAsiCommandSend&quot;"/>',PnagName + 'CommandOut')
        self.loadParameterStr('<Parameter Name="outGlobalFaultReset" Section="Output" Type="Bool"/>', PnagName + "GlobalFaultReset")
        self.addConnection(blockA,"eno",self.CallId,"en")
        
        a = self.spawnPart("Inst" + PnagName + "_Health.outFaulty","Contact")
        self.addEN(a,"in")
        
        OR = self.addOR("2")
        self.addConnection(a,"out",OR,"in1")
        
        b = self.spawnPart("Inst" + PnagName + "_Health.outDisabled","Contact",True)
        self.addConnection(OR,"out",b,"in")
        self.addConnection(b,"out",self.CallId,"inAsiGatewayBusFault")
        
        c = self.spawnPart("Inst" + PnagName + "_Health.outProblem","Contact")
        self.addEN(c,"in")
        self.addConnection(c,"out",OR,"in2")
        
        if scl != None:
            #SCL ConFig
            scl.addRegion(self.Component.get("Name"))
            scl.GlobalVariableEqualLiteralConstant(self.Component.get("Name") + ".inConfig.pnagName", PnagName[-6:])
            scl.GlobalVariableEqualBool(self.Component.get("Name") + ".inConfig.asiGatewayDiag.enableChn0",True)
            scl.GlobalVariableEqualBool(self.Component.get("Name") + ".inConfig.asiGatewayDiag.enableChn1",True)
            scl.endRegion()
            
        if software != None:
            software.Blocks.CreateInstanceDB(self.Component.get('Name'),True,1,self.CallInfo.get("Name"))
    
class EzcBox(swBlock):
    def __init__(self,CabnetNumber,ControlArea,EZCName,PnagName,Dps,Aux,ObjectList,scl=None,software=None):
        super().__init__(ObjectList)
        import re
        self.CabnetNumber = CabnetNumber
        self.ControlArea = ControlArea
        self.EZCName = EZCName
        self.Dps = Dps
        self.Aux = Aux
        self.ObjectList = ObjectList
        self.software = software
        self.scl = scl
        if re.search("^CA[0-9]{1,3}EZC[0-9]{1,3}$",EZCName):
            self.EZCNumber = re.findall("[0-9]{1,3}$", EZCName)[0]
        self.addCall()
        self.addEN(self.CallId,"en")
        self.Component.set("Name","Inst" + self.EZCName)
        self.CallInfo.set("Name","EzcBox")
        self.Comment.text = self.EZCName
        
        if len(self.Dps) > 0:
            self.addParameter("inPowerSupplyGroupStarted","Input","Bool")
            self.addParameter("inPowerSupplyGroupAllStarted","Input","Bool")
            if len(self.Dps) > 1:
                list = []
                for x in self.Dps:
                    list.append("Inst" + x + ".outDpsToZca.started")
                self.OR(list,self.CallId,"inPowerSupplyGroupStarted")
                list = []
                for x in self.Dps:
                    list.append("Inst" + x + ".outDpsToZca.AllStarted")
                self.AND(list,self.CallId,"inPowerSupplyGroupAllStarted")
            else:
                id = self.spawnPart("Inst" + self.Dps[0] + ".outDpsToZca.started","Contact")
                self.addEN(id,"in")
                self.addConnection(id,"out",self.CallId,"inPowerSupplyGroupStarted")
                
                id = self.spawnPart("Inst" + self.Dps[0] + ".outDpsToZca.AllStarted","Contact")
                self.addEN(id,"in")
                self.addConnection(id,"out",self.CallId,"inPowerSupplyGroupAllStarted")
        else:
            self.loadParameterStr('<Parameter Name="inPowerSupplyGroupStarted" Section="Input" Type="Bool"/>','',"LiteralConstant","Bool","true")
            self.loadParameterStr('<Parameter Name="inPowerSupplyGroupAllStarted" Section="Input" Type="Bool"/>','',"LiteralConstant","Bool","true")
        if len(self.Aux) > 0:
            self.addParameter("inSupplyAuxOk","Input","Bool")
            list = []
            for x in range(len(self.Aux)):
                id = self.spawnPart("Inst" + self.Aux[x] + ".outFault","Contact")
                list.append(id)
                if x == 0:
                    self.addEN(id,"in")
                else:
                    self.addConnection(list[x-1],"out",id,"in")
            self.addConnection(list[-1],"out",self.CallId,"inSupplyAuxOk")
        else:
            self.loadParameterStr('<Parameter Name="inSupplyAuxOk" Section="Input" Type="Bool"/>','',"LiteralConstant","Bool","true")
        self.loadParameterStr('<Parameter Name="inSupplyEzcDCOk" Section="Input" Type="Bool"/>',EZCName + "_CR_ESM")
        self.loadParameterStr('<Parameter Name="inAsiBusFault" Section="Input" Type="Bool"/>',"Inst" + PnagName + ".outVisuInterface.status.summary")
        self.loadParameterStr('<Parameter Name="inMainPanelToEzc" Section="Input" Type="&quot;typeAreaToZoneControl&quot;"/>','Inst' + self.CabnetNumber + '.outPlcStatus')
        self.loadParameterStr('<Parameter Name="inPowerGroupSafetyStatusToEzc" Section="Input" Type="&quot;typeSafetyStatusToPowerGroup&quot;"/>','DataFromSafety.' + ControlArea +'EZCxSafetyStatusToPowerGroup[' + self.EZCNumber + ']')
        self.loadParameterStr('<Parameter Name="inConvStartWarning" Section="Input" Type="Bool"/>','',"LiteralConstant","Bool","true")
        self.loadParameterStr('<Parameter Name="outEzcToMainPanel" Section="Output" Type="&quot;typeZoneToAreaControl&quot;"/>','Inst' + self.CabnetNumber + '.inEzcToPlc[' + self.EZCNumber + ']')
        self.loadParameterStr('<Parameter Name="outEzcStatusToSafety" Section="Output" Type="&quot;typePowerGroupStatusToSafety&quot;"/>','DataToSafety.' + ControlArea +'EZCxPowerGroupToSafetyStatus[' + self.EZCNumber + ']')
        
        if self.scl != None:
            #SCL ConFig
            scl.addRegion(self.Component.get("Name"))
            scl.GlobalVariableEqualLiteralConstant(self.Component.get("Name") + ".inConfig.ezcName",re.findall("EZC[0-9]{1,3}$", self.EZCName)[0])
            scl.GlobalVariableEqualConstant(self.Component.get("Name") + ".inConfig.panelNumber","1")
            scl.endRegion()
        
        if software != None:
            software.Blocks.CreateInstanceDB(self.Component.get('Name'),True,1,self.CallInfo.get("Name"))
    
    def createDps(self):
        for x in self.Dps:
            DpsBox(self.CabnetNumber,self.ControlArea,self.EZCNumber,x,self.EZCName,self.ObjectList,self.scl,self.software)
            
            
    def createAux(self): 
        for x in self.Aux:
            AuxBox(self.CabnetNumber,self.ControlArea,self.EZCName,x,self.ObjectList,self.scl,self.software)
            
    

class DpsBox(swBlock):
    def __init__(self,CabnetNumber,ControlArea,EZCName,DpsName,PnagName,ObjectList,scl=None,software=None):
        super().__init__(ObjectList)
        self.addCall()
        self.addEN(self.CallId,"en")
        self.Comment.text = DpsName
        self.Component.set("Name","Inst" + DpsName)
        self.CallInfo.set("Name","DpsBox")
        self.loadParameterStr('<Parameter Name="inField48VSupply1Ok" Section="Input" Type="Bool"/>', DpsName + '_CR_ESM')
        self.loadParameterStr('<Parameter Name="inZcaToDps" Section="Input" Type="&quot;typeZcaToDpsMpsEsz&quot;"/>','Inst' + EZCName +'.outEzcToPowerSupply')
        self.loadParameterStr('<Parameter Name="inPncgZone1Ready" Section="Input" Type="Bool"/>','',"LiteralConstant","Bool","false")
        self.loadParameterStr('<Parameter Name="inAsiBusFault" Section="Input" Type="Bool"/>',"Inst" + PnagName + ".outVisuInterface.status.summary")
        self.loadParameterStr('<Parameter Name="inPncgZone1Active" Section="Input" Type="Bool"/>','',"LiteralConstant","Bool","false")
        self.loadParameterStr('<Parameter Name="inPncgZone2Ready" Section="Input" Type="Bool"/>','',"LiteralConstant","Bool","false")
        self.loadParameterStr('<Parameter Name="inPncgZone2Active" Section="Input" Type="Bool"/>','',"LiteralConstant","Bool","false")
        
        if scl != None:
            #SCL ConFig
            scl.addRegion(self.Component.get("Name"))
            scl.GlobalVariableEqualBool(self.Component.get("Name") + ".inConfig.splitPowergroupCommandZones",False)
            scl.GlobalVariableEqualLiteralConstant(self.Component.get("Name") + ".inConfig.panelName", DpsName)
            scl.GlobalVariableEqualTypedConstant(self.Component.get("Name") + ".inConfig.panelMask", '2#0000_0000_0000_0000_0000_0000_0000_0001')
            scl.endRegion()
            
        if software != None:
            software.Blocks.CreateInstanceDB(self.Component.get('Name'),True,1,self.CallInfo.get("Name"))
        
       
class PncgBox(swBlock):
    def __init__(self,CabnetNumber,PncgName,ObjectList,scl=None,software=None):
        super().__init__(ObjectList)
        self.addCall()
        blockA = self.CallId
        self.Comment.text = PncgName
        self.addEN(self.CallId,"en")
        self.Component.set("Name","Inst" + PncgName + "_Health")
        self.CallInfo.set("Name","ProfinetDeviceHealthSelector")
        self.loadParameterStr('<Parameter Name="inData" Section="Input" Type="&quot;typeProfinetDeviceHealth&quot;"/>',"ProfinetDeviceHealth_DB.outData")
        self.loadParameterStr('<Parameter Name="inLADDR" Section="Input" Type="HW_INTERFACE"/>',PncgName + "~PNCG")
        
        if software != None:
            software.Blocks.CreateInstanceDB(self.Component.get('Name'),True,1,self.CallInfo.get("Name"))
        
        self.addCall()
        self.Component.set("Name","Inst" + PncgName)
        self.CallInfo.set("Name","Pncg")
        
        self.loadParameterStr('<Parameter Name="inoutGlobalData" Section="InOut" Type="&quot;typeInOutGlobalData&quot;"/>',"GlobalData.inoutGlobalData")
        
        self.loadParameterStr('<Parameter Name="inMandatoryStatus" Section="Input" Type="&quot;typeMandatoryInput&quot;"/>',PncgName + "ManStatus")
        self.loadParameterStr('<Parameter Name="inMandatoryHandshake" Section="Input" Type="&quot;typeMandatoryHandShake&quot;"/>',PncgName + "ManHSin")
        self.loadParameterStr('<Parameter Name="inVisuNodeIndex" Section="Input" Type="Byte"/>',PncgName + "VisuNode")
        self.loadParameterStr('<Parameter Name="inVisuZoneIndex" Section="Input" Type="Byte"/>',PncgName + "VisuZoneIndex")
        self.loadParameterStr('<Parameter Name="inStatusInfo" Section="Input" Type="&quot;typeEccStatus&quot;"/>',PncgName + "VisuStatus")
        self.loadParameterStr('<Parameter Name="inWarningsInfo" Section="Input" Type="&quot;typeEccWarning&quot;"/>',PncgName + "VisuWarnings")
        self.loadParameterStr('<Parameter Name="inFaultsInfo" Section="Input" Type="&quot;typeEccFault&quot;"/>',PncgName + "VisuFaults")
        self.loadParameterStr('<Parameter Name="inCommandArea1" Section="Input" Type="&quot;typeCommandAreaInput&quot;"/>',PncgName + 'CmdArea1In')
        self.loadParameterStr('<Parameter Name="inCommandArea2" Section="Input" Type="&quot;typeCommandAreaInput&quot;"/>',PncgName + 'CmdArea2In')
        self.loadParameterStr('<Parameter Name="inCommandArea3" Section="Input" Type="&quot;typeCommandAreaInput&quot;"/>',PncgName + 'CmdArea3In')
        self.loadParameterStr('<Parameter Name="inCommandArea4" Section="Input" Type="&quot;typeCommandAreaInput&quot;"/>',PncgName + 'CmdArea4In')
        self.loadParameterStr('<Parameter Name="inCommandArea5" Section="Input" Type="&quot;typeCommandAreaInput&quot;"/>',PncgName + 'CmdArea5In')
        self.loadParameterStr('<Parameter Name="inCommandArea6" Section="Input" Type="&quot;typeCommandAreaInput&quot;"/>',PncgName + 'CmdArea6In')
        self.loadParameterStr('<Parameter Name="inResetFault" Section="Input" Type="Bool"/>','Inst' + CabnetNumber + '.outPlcStatus.resetZoneFault')
        self.loadParameterStr('<Parameter Name="inCanChannel" Section="Input" Type="&quot;typeCANChannelInput&quot;"/>',PncgName + "CANChannelIn")
        self.addParameter("inBusSlaveOk","Input","Bool")
        
        self.addConnection(blockA,"eno",self.CallId,"en")
        
        a = self.spawnPart("Inst" + PncgName + "_Health.outFaulty","Contact",True)
        self.addEN(a,"in")
        
        b = self.spawnPart("Inst" + PncgName + "_Health.outProblem","Contact",True)
        self.addConnection(a,"out",b,"in")
        
        OR = self.addOR("2")
        self.addConnection(b,"out",OR,"in1")
        self.addConnection(OR,"out",self.CallId,"inBusSlaveOk")
        
        c = self.spawnPart("Inst" + PncgName + "_Health.outDisabled","Contact")
        self.addEN(c,"in")
        self.addConnection(c,"out",OR,"in2")
        
        self.loadParameterStr('<Parameter Name="outCanChannel" Section="Output" Type="&quot;typeCANChannelOutput&quot;"/>',PncgName + "CANChannelOut")
        self.loadParameterStr('<Parameter Name="outMandatoryCmd" Section="Output" Type="&quot;typeMandatoryOutput&quot;"/>',PncgName + "ManCommand")
        self.loadParameterStr('<Parameter Name="outMandatoryHandshake" Section="Output" Type="&quot;typeMandatoryHandShake&quot;"/>',PncgName + "ManHSOut")
        self.loadParameterStr('<Parameter Name="outCommandArea1" Section="Output" Type="&quot;typeCommandAreaOutput&quot;"/>',PncgName + 'CmdArea1Out')
        self.loadParameterStr('<Parameter Name="outCommandArea2" Section="Output" Type="&quot;typeCommandAreaOutput&quot;"/>',PncgName + 'CmdArea2Out')
        self.loadParameterStr('<Parameter Name="outCommandArea3" Section="Output" Type="&quot;typeCommandAreaOutput&quot;"/>',PncgName + 'CmdArea3Out')
        self.loadParameterStr('<Parameter Name="outCommandArea4" Section="Output" Type="&quot;typeCommandAreaOutput&quot;"/>',PncgName + 'CmdArea4Out')
        self.loadParameterStr('<Parameter Name="outCommandArea5" Section="Output" Type="&quot;typeCommandAreaOutput&quot;"/>',PncgName + 'CmdArea5Out')
        self.loadParameterStr('<Parameter Name="outCommandArea6" Section="Output" Type="&quot;typeCommandAreaOutput&quot;"/>',PncgName + 'CmdArea6Out')
        self.loadParameterStr('<Parameter Name="inoutParameterData" Section="InOut" Type="&quot;typeNodeParameters&quot;"/>',"dbPncgParameterData." + PncgName)
        
        if scl != None:
            #SCL ConFig
            scl.addRegion(self.Component.get("Name"))
            scl.GlobalVariableEqualLiteralConstant(self.Component.get("Name") + ".inConfig.name", PncgName[8:])
            scl.GlobalVariableEqualConstant(self.Component.get("Name") + ".inConfig.numberOfEccs", "0")
            scl.GlobalVariableEqualTypedConstant(self.Component.get("Name") + ".inConfig.panelMaskPncg", '2#0000_0000_0000_0000_0000_0000_0000_0001')
            scl.GlobalVariableEqualTypedConstant(self.Component.get("Name") + ".inConfig.panelMaskCommandArea1", '2#0000_0000_0000_0000_0000_0000_0000_0001')
            scl.GlobalVariableEqualTypedConstant(self.Component.get("Name") + ".inConfig.panelMaskCommandArea2", '2#0000_0000_0000_0000_0000_0000_0000_0001')
            scl.GlobalVariableEqualTypedConstant(self.Component.get("Name") + ".inConfig.panelMaskCommandArea3", '2#0000_0000_0000_0000_0000_0000_0000_0001')
            scl.GlobalVariableEqualTypedConstant(self.Component.get("Name") + ".inConfig.panelMaskCommandArea4", '2#0000_0000_0000_0000_0000_0000_0000_0001')
            scl.GlobalVariableEqualTypedConstant(self.Component.get("Name") + ".inConfig.panelMaskCommandArea5", '2#0000_0000_0000_0000_0000_0000_0000_0001')
            scl.GlobalVariableEqualTypedConstant(self.Component.get("Name") + ".inConfig.panelMaskCommandArea6", '2#0000_0000_0000_0000_0000_0000_0000_0001')
            scl.endRegion()
        
        if software != None:
            software.Blocks.CreateInstanceDB(self.Component.get('Name'),True,1,self.CallInfo.get("Name"))
        
       
class RptrBox(swBlock):
    def __init__(self,RptrName,PncgName,ObjectList,scl=None,software=None):
        super().__init__(ObjectList)
        self.addCall()
        self.Comment.text = RptrName
        self.addEN(self.CallId,"en")
        self.Component.set("Name","Inst" + RptrName)
        self.CallInfo.set("Name","RptrBox")
        
        self.loadParameterStr('<Parameter Name="inTemperatureRptrOk" Section="Input" Type="Bool"/>','',"LiteralConstant","Bool","true")
        self.loadParameterStr('<Parameter Name="inPnagToRptr" Section="Input" Type="&quot;typePnagToRptr;"/>',"Inst" + PncgName + ".outPnagToRptr")
        self.loadParameterStr('<Parameter Name="inAsiBusFault" Section="Input" Type="Bool"/>',"Inst" + PncgName + ".outVisuInterface.status.summary")
        
        if scl != None:
            #SCL ConFig
            scl.addRegion(self.Component.get("Name"))
            scl.GlobalVariableEqualLiteralConstant(self.Component.get("Name") + ".inConfig.rptrName", RptrName.replace("_", ""))
            scl.GlobalVariableEqualTypedConstant(self.Component.get("Name") + ".inConfig.panelMask", '2#0000_0000_0000_0000_0000_0000_0000_0001')
            scl.endRegion()
        
        if software != None:
            software.Blocks.CreateInstanceDB(self.Component.get('Name'),True,1,self.CallInfo.get("Name"))
        
class AuxBox(swBlock):
    def __init__(self,CabnetNumber,ControlArea,EZCName,AuxBoxName,PnagName,ObjectList,scl=None,software=None):
        super().__init__(ObjectList)
        self.addCall()
        self.Comment.text = AuxBoxName
        self.addEN(self.CallId,"en")
        self.Component.set("Name","Inst" + AuxBoxName)
        self.CallInfo.set("Name","AuxBox")
        
        self.loadParameterStr('<Parameter Name="inSupplyAuxDCOk" Section="Input" Type="Bool"/>',AuxBoxName +'_CR_ESM')
        self.loadParameterStr('<Parameter Name="inEzcToAux" Section="Input" Type="&quot;typeZoneControlToAux&quot;"/>',"Inst" + EZCName +'.outEzcToAux')
        self.loadParameterStr('<Parameter Name="inAsiBusFault" Section="Input" Type="Bool"/>',"Inst" + PnagName + ".outVisuInterface.status.summary")
        
        
        if scl != None:
            scl.addRegion(self.Component.get("Name"))
            scl.GlobalVariableEqualBool(self.Component.get("Name") + ".inConfig.auxName",self.Component.get("Name"))
            scl.GlobalVariableEqualTypedConstant(self.Component.get("Name") + ".inConfig.panelMask", '2#0000_0000_0000_0000_0000_0000_0000_0001')
            scl.endRegion()
        
        if software != None:
            software.Blocks.CreateInstanceDB(self.Component.get('Name'),True,1,self.CallInfo.get("Name"))
         """
class ResetPanelBox(swBlock):
    def __init__(self,ControlArea,LineName,ASiNetwork,PBs,BCs,ObjectList,scl=None,software=None):
        super().__init__(ObjectList)
        self.addCall()
        self.Comment.text = ControlArea + ' ' + LineName + ' ' + 'Reset'
        self.addEN(self.CallId,"en")
        self.Component.set("Name","InstResetPanel_" + LineName)
        self.CallInfo.set("Name","ResetPanelBox")
        
        network  = {"A":"U253110_PNAG_A","B":"U252310_PNAG_B","C":"U251910_PNAG_C"}
        
        
        if len(PBs) > 0:
            self.addParameter("inResetButton","Input","Bool")
            self.OR(PBs,self.CallId,"inPowerSupplyGroupStarted")
        else:
            self.loadParameterStr('<Parameter Name="inResetButton" Section="Input" Type="Bool"/>','',"LiteralConstant","Bool","false")
        
        self.addParameter("inAsiGatewayConnected","Input","Bool")
        x = self.spawnPart("Inst" + network[ASiNetwork[:1]] + "outVisuInterface.faults.asiGatewayBus","Contact",True)
        self.addEN(x,"in")
        y = self.spawnPart(network[ASiNetwork[:1]] + "FlagsChn" + str(int(ASiNetwork[1:])-1) + ".noNormalOperation","Contact",True)
        self.addConnection(x,"out",y,"in")
        self.addConnection(y,"out",self.CallId,"inAsiGatewayConnected")
        
        self.loadParameterStr('<Parameter Name="inAsiBusFault" Section="Input" Type="Bool"/>',"Inst" + network[ASiNetwork[:1]] + "outVisuInterface.status.summary")
        
        BCs.insert(0, self.Component.get("Name") + ".outIndicatorLight")
        """
        
class ConnectionBox(swBlock):
    def __init__(self,Name,ConnectionNumber,ObjectList,zone="",scl=None,software=None):
        super().__init__(ObjectList)
        x = self.spawnPart("DeleteMe","Contact")
        self.addEN(x,"in")
        y = self.spawnPart("DeleteMe","Coil")
        self.addConnection(x,"out",y,"in")
        if scl != None:
            #SCL ConFig
            scl.addRegion(Name)
            scl.GlobalVariableEqualConstant('HMI.ConnectionPoints[{0}].connectionId'.format(ConnectionNumber),ConnectionNumber)
            scl.GlobalVariableEqualConstant('HMI.ConnectionPoints[{0}].controlZone.controlMask'.format(ConnectionNumber),"2#0000_0000_0000_0000_0000_0000_0000_0001")
            scl.endRegion()
        
        if software != None:
            pass
        
class Test(swBlock):
    def __init__(self,ObjectList,scl=None):
        super().__init__(ObjectList)
        dps = 1
        for x in ["InstU253045_ECG_01","InstU252245_ECG_02","InstU251845_ECG_03"]:
            for CmdArea in range(1,5):
                self.Comment.text = x + ' CmdArea Mapping'
                for tail in ['connected','requestEnable','requestReset','requestWakeUp']:
                    list = []
                    list.append('InstCA111Dps{0}.outDpsZone1ToPncg.{1}'.format(str(dps).zfill(2),tail))
                    list.append('InstCA111Dps{0}.outDpsZone1ToPncg.{1}'.format(str(dps + 1).zfill(2),tail))
                    resultCoilName = '{0}.inDpsToCmdArea{1}.{2}'.format(x,CmdArea,tail)
                    id = self.spawnPart(resultCoilName,'Coil')
                    self.OR(list,id,"in")
                dps = dps + 2
            if x != "InstU251845_ECG_03":
                super().__init__(ObjectList)
                """