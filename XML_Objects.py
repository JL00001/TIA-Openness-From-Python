from fb_block import fb_block

class AbbAcs380Drive(fb_block):
    def __init__(self,unitNumber,ObjectList,scl=None,zone=""):
        super().__init__(ObjectList)
        unitName = unitNumber + zone
        self.addCall()
        self.addEN(self.CallId,"en")
        self.Component.set("Name","Inst" + unitName + "_Drive1")
        unitName = unitName + " FMD"
        self.CallInfo.set("Name","AbbAcs380Drive")
        self.loadParameterStr('<Parameter Name="inoutGlobalData" Section="InOut" Type="&quot;typeInOutGlobalData&quot;" />',"GlobalData.inoutGlobalData")
        self.loadParameterStr('<Parameter Name="inoutLoggingDB" Section="InOut" Type="&quot;typeLoggingDB&quot;" />',"LoggingOptimizedDB.loggingDB")
        self.loadParameterStr('<Parameter Name="inGlobalData" Section="Input" Type="&quot;typeInGlobalData&quot;" />',"GlobalData.inGlobalData")
        self.loadParameterStr('<Parameter Name="inDriveStatus" Section="Input" Type="&quot;typeABBACS380InputsPP04&quot;" />',unitName + "_In")
        self.loadParameterStr('<Parameter Name="inConveyorStatus" Section="Input" Type="&quot;typePortStatus1Unit&quot;" />',"Inst" + unitNumber + ".outStatus")
        self.loadParameterStr('<Parameter Name="inDriveFlags" Section="Input" Type="&quot;typeDriveFlags&quot;" />',"Inst" + unitNumber + ".outPort12Motor")
        self.loadParameterStr('<Parameter Name="outDriveCommand" Section="Output" Type="&quot;typeABBACS380OutputsPP04&quot;" />',unitName + "_Out")
        
        if scl != None:
            #SCL ConFig
            pass
        
class AsiABBDriveNAType01(fb_block):
    def __init__(self,unitNumber,ObjectList,scl = None,zone=""):
        super().__init__(ObjectList)
        unitName = unitNumber + zone
        self.addCall()
        self.addEN(self.CallId,"en")
        self.Component.set("Name","Inst" + unitName + "_Drive1")
        self.CallInfo.set("Name","AsiABBDriveNAType01")
        self.loadParameterStr('<Parameter Name="inoutGlobalData" Section="InOut" Type="&quot;typeInOutGlobalData&quot;" />',"GlobalData.inoutGlobalData")
        self.loadParameterStr('<Parameter Name="inoutLoggingDB" Section="InOut" Type="&quot;typeLoggingDB&quot;" />',"LoggingOptimizedDB.loggingDB")
        self.loadParameterStr('<Parameter Name="inAlarmSignals" Section="Input" Type="&quot;typeSystemAlarms&quot;"/>',"GlobalData.inGlobalData.alarms")
        self.loadParameterStr('<Parameter Name="inGlobalData" Section="Input" Type="&quot;typeInGlobalData&quot;" />',"GlobalData.inGlobalData")
        self.loadParameterStr('<Parameter Name="inChecksumPulse" Section="Input" Type="Bool"/>',"GlobalData.inGlobalData.checksumPulse")
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
            
class MoviMot(fb_block):
    def __init__(self,unitNumber,ObjectList,scl = None,zone=""):
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
        
class ScannerSickCLV6xx(fb_block):
    def __init__(self,unitNumber,ObjectList,scl = None,zone=""):
        super().__init__(ObjectList)
        unitName = unitNumber + zone
        self.addCall()
        self.addEN(self.CallId,"en")
        self.Component.set("Name","Inst" + unitNumber + "_Scanner")
        self.CallInfo.set("Name","ScannerSickCLV6xx")
        
        
        self.loadParameterStr('<Parameter Name="inoutGlobalData" Section="InOut" Type="&quot;typeInOutGlobalData&quot;" />',"GlobalData.inoutGlobalData")
        self.loadParameterStr('<Parameter Name="inoutLoggingDB" Section="InOut" Type="&quot;typeLoggingDB&quot;" />',"LoggingOptimizedDB.loggingDB")
        self.loadParameterStr('<Parameter Name="inGlobalData" Section="Input" Type="&quot;typeInGlobalData&quot;" />',"GlobalData.inGlobalData")
        self.loadParameterStr('<Parameter Name="inoutFaultBuffer" Section="InOut" Type="Array[*] of &quot;typeAlarmBufferEntry&quot;" />',"Alarms.faultBuffer")
        self.loadParameterStr('<Parameter Name="inoutWarningBuffer" Section="InOut" Type="Array[*] of &quot;typeAlarmBufferEntry&quot;" />',"Alarms.warningBuffer")
        
        
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
            scl.GlobalVariableEqualLiteralConstant(self.Component.get("Name") + ".inConfig.noReadBarcode","NOREAD")
            scl.GlobalVariableEqualTypedConstant(self.Component.get("Name") + ".inConfig.noDataTimeout","T#10s")
            scl.GlobalVariableEqualLiteralConstant(self.Component.get("Name") + ".inConfig.readDualBarcodes","FALSE")
            scl.GlobalVariableEqualLiteralConstant(self.Component.get("Name") + ".inConfig.configuration.noReadFaultLimit","1")
            scl.GlobalVariableEqualLiteralConstant(self.Component.get("Name") + ".inConfig.configuration.successfulReadThreshold","80")
            scl.GlobalVariableEqualTypedConstant(self.Component.get("Name") + ".inConfig.earlyTriggerEnd","T#10s")
            scl.endRegion()
        
class FortressGate(fb_block):
    def __init__(self,unitNumber,Failsafe_FIODBName,ObjectList,scl=None,zone=""):
        FortressGateSwitch(unitNumber,ObjectList,scl,zone)
        FortressGateSwitchSafety(unitNumber,ObjectList,Failsafe_FIODBName,scl,zone)
        FortressGateSwitchVis(unitNumber,ObjectList,scl,zone)
        
class FortressGateSwitch(fb_block):
    def __init__(self,unitNumber,ObjectList,scl=None,zone=""):
        super().__init__(ObjectList)
        unitName = unitNumber + zone + "_GS"
        self.addCall()
        self.Comment.text = unitName.split("_")[0] + " Gate Switch"
        self.addEN(self.CallId,"en")
        self.Component.set("Name","Inst" + unitName)
        self.CallInfo.set("Name","FortressGateSwitch")
        self.loadParameterStr('<Parameter Name="inGlobalData" Section="Input" Type="&quot;typeInGlobalData&quot;" />',"GlobalData.inGlobalData")
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
           
class FortressGateSwitchSafety(fb_block):
    def __init__(self,unitNumber,ObjectList,Failsafe_FIODBName,scl=None,zone=""):
        super().__init__(ObjectList)
        self.addCall()
        unitName = unitNumber + zone + "_GS"
        self.Comment.text = unitName.split("_")[0] + " Safety"
        self.addEN(self.CallId,"en")
        self.Component.set("Name","Inst" + unitNumber + " Gate Switch Safety")
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
        
class FortressGateSwitchVis(fb_block):
    def __init__(self,unitNumber,ObjectList,scl=None,zone=""):
        super().__init__(ObjectList)
        self.addCall()
        unitName = unitNumber + zone + "_GS"
        self.Comment.text = unitName + " Vis"
        self.addEN(self.CallId,"en")
        self.Component.set("Name","Inst" + unitName + " Vis")
        
        self.CallInfo.set("Name","EmergencyStop")
        self.loadParameterStr('<Parameter Name="inoutGlobalData" Section="InOut" Type="&quot;typeInOutGlobalData&quot;" />',"GlobalData.inoutGlobalData")
        self.loadParameterStr('<Parameter Name="inoutLoggingDB" Section="InOut" Type="&quot;typeLoggingDB&quot;" />',"LoggingOptimizedDB.loggingDB")
        self.loadParameterStr('<Parameter Name="inGlobalData" Section="Input" Type="&quot;typeInGlobalData&quot;" />',"GlobalData.inGlobalData")
        self.loadParameterStr('<Parameter Name="inoutFaultBuffer" Section="InOut" Type="Array[*] of &quot;typeAlarmBufferEntry&quot;" />',"Alarms.faultBuffer")
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
        
class EStopVis(fb_block):
    def __init__(self,Pnag,Ezc,unitName,ObjectList,scl=None):
        super().__init__(ObjectList)
        
        inAsiBusFault = 'Inst{0}.outVisuInterface.status.summary'.format(Pnag)
        
        self.addCall()
        self.addEN(self.CallId,"en")
        self.Component.set("Name","Inst" + unitName + "_Vis")
        
        self.CallInfo.set("Name","EmergencyStop")
        self.Comment.text = unitName + "_Vis"
        self.loadParameterStr('<Parameter Name="inoutGlobalData" Section="InOut" Type="&quot;typeInOutGlobalData&quot;" />',"GlobalData.inoutGlobalData")
        self.loadParameterStr('<Parameter Name="inoutLoggingDB" Section="InOut" Type="&quot;typeLoggingDB&quot;" />',"LoggingOptimizedDB.loggingDB")
        self.loadParameterStr('<Parameter Name="inGlobalData" Section="Input" Type="&quot;typeInGlobalData&quot;" />',"GlobalData.inGlobalData")
        self.loadParameterStr('<Parameter Name="inoutFaultBuffer" Section="InOut" Type="Array[*] of &quot;typeAlarmBufferEntry&quot;" />',"Alarms.faultBuffer")
        self.addParameter("inEStopStatus","Input","Bool")
        self.loadParameterStr('<Parameter Name="inZoneStatus" Section="Input" Type="Bool"/>','Inst' + Ezc + '.outEStopHealthy')
        self.loadParameterStr('<Parameter Name="inLocation" Section="Input" Type="String[14]"/>','',"LiteralConstant","String",unitName.split("_")[0])
        self.loadParameterStr('<Parameter Name="inConfigContactType" Section="Input" Type="Bool"/>','',"LiteralConstant","Bool","false")
        self.loadParameterStr('<Parameter Name="inAsiBusFault" Section="Input" Type="Bool"/>',inAsiBusFault)
        
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
        d = self.spawnPart(unitName + "_LT_R","Contact")
        e = self.spawnPart(unitName + "_LT_G","Coil")
        self.addConnection(c,"out",d,"in")
        self.addConnection(d,"out",e,"in")
        
        if scl != None:
            #SCL ConFig
            pass
        
class CallSetConfig(fb_block):
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
        
class Area(fb_block):
    def __init__(self,CabnetNumber,ControlArea,EZCName,Dps,Aux,Pnag,Pncg,Estops,EstopsAsi,ObjectList,scl=None):
        #super().__init__(ObjectList)
        Plc(CabnetNumber,ObjectList,scl)
        
        for x in Pncg:
            PncgBox(CabnetNumber,x,ObjectList,scl)
        
        for x in Pnag:
            PnagBox(CabnetNumber,ControlArea,x,ObjectList,scl)
        
        list = []
        for x in range(len(EZCName)):
            list.append(EzcBox(CabnetNumber,ControlArea,EZCName[x],Dps[x],Aux[x],Estops[x],EstopsAsi[x],Pnag,ObjectList,scl))
            
        for x in list:
            x.createDps()
            
        for x in list:
            x.createAux()
            
        for x in list:
            x.createEstop()
        
class Plc(fb_block):
    def __init__(self,CabnetNumber,ObjectList,scl=None):
        super().__init__(ObjectList)
        self.addCall()
        self.Comment.text = CabnetNumber
        self.addEN(self.CallId,"en")
        self.Component.set("Name","Inst" + CabnetNumber)
        self.CallInfo.set("Name","Plc")
        
        self.loadParameterStr('<Parameter Name="inWcsCommsHealthy" Section="Input" Type="Bool" />',"InstDciManager.outConnected")
        self.loadParameterStr('<Parameter Name="inSafetyStatusToPlc" Section="Input" Type="&quot;typeSafetyStatusToMainPanel&quot;" />',"DataFromSafety.SafetyStatusToPLC")
        
class PnagBox(fb_block):
    def __init__(self,CabnetNumber,ControlArea,PnagName,ObjectList,scl=None):
        super().__init__(ObjectList)
        self.addCall()
        blockA = self.CallId
        self.Comment.text = ControlArea + ' ' + PnagName
        self.addEN(self.CallId,"en")
        self.Component.set("Name","Inst" + PnagName + "_Health")
        self.CallInfo.set("Name","ProfinetDeviceHealthSelector")
        self.loadParameterStr('<Parameter Name="inData" Section="Input" Type="&quot;typeProfinetDeviceHealth&quot;"/>',"ProfinetDeviceHealth_DB.outData")
        self.loadParameterStr('<Parameter Name="inLADDR" Section="Input" Type="HW_INTERFACE"/>',PnagName + "~PN-IO")
        
        self.addCall()
        self.Component.set("Name","Inst" + PnagName)
        self.CallInfo.set("Name","PnagBox")
        self.loadParameterStr('<Parameter Name="inoutGlobalData" Section="InOut" Type="&quot;typeInOutGlobalData&quot;" />',"GlobalData.inoutGlobalData")
        self.loadParameterStr('<Parameter Name="inoutLoggingDB" Section="InOut" Type="&quot;typeLoggingDB&quot;" />',"LoggingOptimizedDB.loggingDB")
        self.loadParameterStr('<Parameter Name="inGlobalData" Section="Input" Type="&quot;typeInGlobalData&quot;" />',"GlobalData.inGlobalData")
        self.loadParameterStr('<Parameter Name="inoutFaultBuffer" Section="InOut" Type="Array[*] of &quot;typeAlarmBufferEntry&quot;"/>',"Alarms.faultBuffer")
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
    
class EzcBox(fb_block):
    def __init__(self,CabnetNumber,ControlArea,EZCName,Dps,Aux,Estops,EstopsAsi,Pnag,ObjectList,scl=None):
        super().__init__(ObjectList)
        self.CabnetNumber = CabnetNumber
        self.ControlArea = ControlArea
        self.EZCName = EZCName
        self.Dps = Dps
        self.Aux = Aux
        self.Estops = Estops
        self.EstopsAsi = EstopsAsi
        self.Pnag = Pnag
        self.ObjectList = ObjectList
        self.scl = scl
        self.EZCNumber = str(int(self.EZCName[3:]))
        self.addCall()
        self.addEN(self.CallId,"en")
        self.Component.set("Name","Inst" + self.ControlArea + self.EZCName)
        self.CallInfo.set("Name","EzcBox")
        self.Comment.text = self.ControlArea + ' ' + self.EZCName
        
        self.loadParameterStr('<Parameter Name="inoutGlobalData" Section="InOut" Type="&quot;typeInOutGlobalData&quot;" />',"GlobalData.inoutGlobalData")
        self.loadParameterStr('<Parameter Name="inoutLoggingDB" Section="InOut" Type="&quot;typeLoggingDB&quot;" />',"LoggingOptimizedDB.loggingDB")
        self.loadParameterStr('<Parameter Name="inGlobalData" Section="Input" Type="&quot;typeInGlobalData&quot;" />',"GlobalData.inGlobalData")
        
        if len(self.Dps) > 0:
            self.addParameter("inPowerSupplyGroupStarted","Input","Bool")
            self.addParameter("inPowerSupplyGroupAllStarted","Input","Bool")
            list = []
            for x in range(len(self.Dps)):
                list.append("Inst" + self.ControlArea + self.Dps[x] + ".outDpsToZca.started")
            self.OR(list,self.CallId,"inPowerSupplyGroupStarted")
            list = []
            for x in range(len(self.Dps)):
                list.append("Inst" + self.ControlArea + self.Dps[x] + ".outDpsToZca.AllStarted")
            self.AND(list,self.CallId,"inPowerSupplyGroupAllStarted")
        else:
            self.loadParameterStr('<Parameter Name="inPowerSupplyGroupStarted" Section="Input" Type="Bool"/>','',"LiteralConstant","Bool","true")
            self.loadParameterStr('<Parameter Name="inPowerSupplyGroupAllStarted" Section="Input" Type="Bool"/>','',"LiteralConstant","Bool","true")
        if len(self.Aux) > 0:
            self.addParameter("inSupplyAuxOk","Input","Bool")
            list = []
            for x in range(len(self.Aux)):
                id = self.spawnPart("Inst" + self.ControlArea + self.Aux[x] + ".outDpsToZca.AllStarted","Contact")
                list.append(id)
                if x == 0:
                    self.addEN(id,"in")
                else:
                    self.addConnection(list[x-1],"out",id,"in")
            self.addConnection(list[-1],"out",self.CallId,"inSupplyAuxOk")
        else:
            self.loadParameterStr('<Parameter Name="inSupplyAuxOk" Section="Input" Type="Bool"/>','',"LiteralConstant","Bool","true")
        self.loadParameterStr('<Parameter Name="inSupplyEzcDCOk" Section="Input" Type="Bool"/>','',"LiteralConstant","Bool","true")
        self.loadParameterStr('<Parameter Name="inMainPanelToEzc" Section="Input" Type="&quot;typeAreaToZoneControl&quot;"/>','Inst' + self.CabnetNumber + '.outPlcStatus')
        self.loadParameterStr('<Parameter Name="inPowerGroupSafetyStatusToEzc" Section="Input" Type="&quot;typeSafetyStatusToPowerGroup&quot;"/>','DataFromSafety.EZCxSafetyStatusToPowerGroup[' + self.EZCNumber + ']')
        self.loadParameterStr('<Parameter Name="inConvStartWarning" Section="Input" Type="Bool"/>','',"LiteralConstant","Bool","true")
        self.loadParameterStr('<Parameter Name="outEzcToMainPanel" Section="Output" Type="&quot;typeZoneToAreaControl&quot;"/>','Inst' + self.CabnetNumber + '.inEzcToPlc[' + self.EZCNumber + ']')
        self.loadParameterStr('<Parameter Name="outEzcStatusToSafety" Section="Output" Type="&quot;typePowerGroupStatusToSafety&quot;"/>','DataToSafety.EZCxPowerGroupToSafetyStatus[' + self.EZCNumber + ']')
        
        if self.scl != None:
            #SCL ConFig
            scl.addRegion(self.Component.get("Name"))
            scl.GlobalVariableEqualLiteralConstant(self.Component.get("Name") + ".inConfig.ezcName",self.EZCName)
            scl.GlobalVariableEqualConstant(self.Component.get("Name") + ".inConfig.panelNumber","1")
            scl.endRegion()
    
    def createDps(self):
        for x in self.Dps:
            DpsBox(self.CabnetNumber,self.ControlArea,self.EZCNumber,x,self.EZCName,self.ObjectList,self.scl)
            
    def createAux(self): 
        for x in self.Aux:
            #Add support for Aux
            pass
            
    def createEstop(self):
        for x in range(len(self.Estops)):
            address = self.EstopsAsi[x]
            split = address.split("_")
            networkLetter = split[1][:1]
            for y in self.Pnag:
                if networkLetter == y.split("_")[2]:
                    EStopVis(y,self.EZCName,self.Estops[x],self.ObjectList,self.scl)

class DpsBox(fb_block):
    def __init__(self,CabnetNumber,ControlArea,EZCNumber,DpsName,EZCName,ObjectList,scl=None):
        super().__init__(ObjectList)
        self.addCall()
        self.addEN(self.CallId,"en")
        self.Comment.text = ControlArea + ' ' + DpsName
        self.Component.set("Name","Inst" + ControlArea + DpsName)
        self.CallInfo.set("Name","DpsBox")
        self.loadParameterStr('<Parameter Name="inoutGlobalData" Section="InOut" Type="&quot;typeInOutGlobalData&quot;" />',"GlobalData.inoutGlobalData")
        self.loadParameterStr('<Parameter Name="inoutLoggingDB" Section="InOut" Type="&quot;typeLoggingDB&quot;" />',"LoggingOptimizedDB.loggingDB")
        self.loadParameterStr('<Parameter Name="inGlobalData" Section="Input" Type="&quot;typeInGlobalData&quot;" />',"GlobalData.inGlobalData")
        self.loadParameterStr('<Parameter Name="inField48VSupply1Ok" Section="Input" Type="Bool"/>',ControlArea + DpsName + '_CR_ESM')
        self.loadParameterStr('<Parameter Name="inZcaToDps" Section="Input" Type="&quot;typeZcaToDpsMpsEsz&quot;"/>','Inst' + ControlArea + EZCName +'.outEzcToPowerSupply')
        
        if scl != None:
            #SCL ConFig
            scl.addRegion(self.Component.get("Name"))
            scl.GlobalVariableEqualBool(self.Component.get("Name") + ".inConfig.splitPowergroupCommandZones",False)
            scl.GlobalVariableEqualLiteralConstant(self.Component.get("Name") + ".inConfig.panelName", DpsName)
            scl.endRegion()
        
class PncgBox(fb_block):
    def __init__(self,ControlArea,PncgName,ObjectList,scl=None):
        super().__init__(ObjectList)
        self.addCall()
        blockA = self.CallId
        self.Comment.text = ControlArea + ' ' + PncgName
        self.addEN(self.CallId,"en")
        self.Component.set("Name","Inst" + PncgName + "_Health")
        self.CallInfo.set("Name","ProfinetDeviceHealthSelector")
        self.loadParameterStr('<Parameter Name="inData" Section="Input" Type="&quot;typeProfinetDeviceHealth&quot;"/>',"ProfinetDeviceHealth_DB.outData")
        self.loadParameterStr('<Parameter Name="inLADDR" Section="Input" Type="HW_INTERFACE"/>',PncgName + "~PNCG")
        
        self.addCall()
        self.Component.set("Name","Inst" + PncgName)
        self.CallInfo.set("Name","Pncg")
        
        self.loadParameterStr('<Parameter Name="inoutGlobalData" Section="InOut" Type="&quot;typeInOutGlobalData&quot;"/>',"GlobalData.inoutGlobalData")
        self.loadParameterStr('<Parameter Name="inoutLoggingDB" Section="InOut" Type="&quot;typeLoggingDB&quot;"/>',"LoggingOptimizedDB.loggingDB")
        self.loadParameterStr('<Parameter Name="inGlobalData" Section="Input" Type="&quot;typeInGlobalData&quot;"/>',"GlobalData.inGlobalData")
        self.loadParameterStr('<Parameter Name="inoutFaultBuffer" Section="InOut" Type="Array[*] of &quot;typeAlarmBufferEntry&quot;"/>',"Alarms.faultBuffer")
        
        self.loadParameterStr('<Parameter Name="inMandatoryStatus" Section="Input" Type="&quot;typeMandatoryInput&quot;"/>',PncgName + "ManStatus")
        self.loadParameterStr('<Parameter Name="inMandatoryHandshake" Section="Input" Type="&quot;typeMandatoryHandShake&quot;"/>',PncgName + "ManHSin")
        self.loadParameterStr('<Parameter Name="inVisuNodeIndex" Section="Input" Type="Byte"/>',PncgName + "VisuNode")
        self.loadParameterStr('<Parameter Name="inVisuZoneIndex" Section="Input" Type="Byte"/>',PncgName + "VisuZoneIndex")
        self.loadParameterStr('<Parameter Name="inStatusInfo" Section="Input" Type="&quot;typeEccStatus&quot;"/>',PncgName + "VisuStatus")
        self.loadParameterStr('<Parameter Name="inWarningsInfo" Section="Input" Type="&quot;typeEccWarning&quot;"/>',PncgName + "VisuWarnings")
        self.loadParameterStr('<Parameter Name="inFaultsInfo" Section="Input" Type="&quot;typeEccFault&quot;"/>',PncgName + "VisuFaults")
        self.loadParameterStr('<Parameter Name="inCommandArea1" Section="Input" Type="&quot;typeCommandAreaInput&quot;"/>',PncgName + "CmdArea1In")
        self.loadParameterStr('<Parameter Name="inResetFault" Section="Input" Type="Bool"/>','Inst' + ControlArea + '.outPlcStatus.resetZoneFault')
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
        self.loadParameterStr('<Parameter Name="outCommandArea1" Section="Output" Type="&quot;typeCommandAreaOutput&quot;"/>',PncgName + "CmdArea1Out")
        self.loadParameterStr('<Parameter Name="inoutParameterData" Section="InOut" Type="&quot;typeNodeParameters&quot;"/>',"dbPncgParameterData." + PncgName)
        
        if scl != None:
            #SCL ConFig
            scl.addRegion(self.Component.get("Name"))
            scl.GlobalVariableEqualLiteralConstant(self.Component.get("Name") + ".inConfig.name", PncgName[8:])
            scl.GlobalVariableEqualConstant(self.Component.get("Name") + ".inConfig.numberOfEccs", "0")
            scl.endRegion()
        
class RptrBox(fb_block):
    def __init__(self,CabnetNumber,ControlArea,RptrName,PncgName,ObjectList,scl=None):
        super().__init__(ObjectList)
        self.addCall()
        self.Comment.text = ControlArea + ' ' + RptrName
        self.addEN(self.CallId,"en")
        self.Component.set("Name","Inst" + RptrName)
        self.CallInfo.set("Name","RptrBox")
        
        self.loadParameterStr('<Parameter Name="inoutGlobalData" Section="InOut" Type="&quot;typeInOutGlobalData&quot;"/>',"GlobalData.inoutGlobalData")
        self.loadParameterStr('<Parameter Name="inoutLoggingDB" Section="InOut" Type="&quot;typeLoggingDB&quot;"/>',"LoggingOptimizedDB.loggingDB")
        self.loadParameterStr('<Parameter Name="inGlobalData" Section="Input" Type="&quot;typeInGlobalData&quot;"/>',"GlobalData.inGlobalData")
        self.loadParameterStr('<Parameter Name="inoutFaultBuffer" Section="InOut" Type="Array[*] of &quot;typeAlarmBufferEntry&quot;"/>',"Alarms.faultBuffer")
        self.loadParameterStr('<Parameter Name="inTemperatureRptrOk" Section="Input" Type="Bool"/>','',"LiteralConstant","Bool","true")
        self.loadParameterStr('<Parameter Name="inPnagToRptr" Section="Input" Type="&quot;typePnagToRptr;"/>',"Inst" + PncgName + ".outPnagToRptr")
        self.loadParameterStr('<Parameter Name="inAsiBusFault" Section="Input" Type="Bool"/>',"Inst" + PncgName + ".outVisuInterface.status.summary")
        
        if scl != None:
            #SCL ConFig
            scl.addRegion(self.Component.get("Name"))
            scl.GlobalVariableEqualLiteralConstant(self.Component.get("Name") + ".inConfig.rptrName", RptrName.replace("_", ""))
            scl.endRegion()
        
class AuxBox(fb_block):
    def __init__(self,CabnetNumber,ControlArea,RptrName,PncgName,ObjectList,scl=None):
        super().__init__(ObjectList)
        self.addCall()
        self.Comment.text = ControlArea + ' ' + RptrName
        self.addEN(self.CallId,"en")
        self.Component.set("Name","Inst" + RptrName)
        self.CallInfo.set("Name","AuxBox")
        
        self.loadParameterStr('<Parameter Name="inoutGlobalData" Section="InOut" Type="&quot;typeInOutGlobalData&quot;"/>',"GlobalData.inoutGlobalData")
        self.loadParameterStr('<Parameter Name="inoutLoggingDB" Section="InOut" Type="&quot;typeLoggingDB&quot;"/>',"LoggingOptimizedDB.loggingDB")
        self.loadParameterStr('<Parameter Name="inGlobalData" Section="Input" Type="&quot;typeInGlobalData&quot;"/>',"GlobalData.inGlobalData")
        self.loadParameterStr('<Parameter Name="inoutFaultBuffer" Section="InOut" Type="Array[*] of &quot;typeAlarmBufferEntry&quot;"/>',"Alarms.faultBuffer")
        
class Test(fb_block):
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