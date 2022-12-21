from xmlHeader import xmlHeader
import xml.etree.cElementTree as ET

class swBlock(xmlHeader):
    def __init__(self,ObjectList):
        SWBlocksCompileUnit = self.createSubElement(ObjectList, "SW.Blocks.CompileUnit","ID")
        SWBlocksCompileUnit.set("CompositionName", "CompileUnits")
        AttributeList = self.createSubElement(SWBlocksCompileUnit,"AttributeList")
        
        NetworkSource = self.createSubElement(AttributeList,"NetworkSource")
        FlgNet = self.createSubElement(NetworkSource,"FlgNet")
        FlgNet.set("xmlns","http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v4")
        self.Parts = self.createSubElement(FlgNet,"Parts")
        self.Wires = self.createSubElement(FlgNet,"Wires")
        
        #Add enWire
        self.Powerrail = self.createSubElement(self.Wires,"Wire","UId")
        Powerrail = self.createSubElement(self.Powerrail,"Powerrail")
        
        
        #Add Support for Comments
        ObjectList = self.createSubElement(SWBlocksCompileUnit,"ObjectList")
        MultilingualText = self.createSubElement(ObjectList,"MultilingualText","ID")
        MultilingualText.set("CompositionName","Title")
        ObjectList = self.createSubElement(MultilingualText,"ObjectList")
        MultilingualTextItem = self.createSubElement(ObjectList,"MultilingualTextItem","ID")
        MultilingualTextItem.set("CompositionName","Items")
        AttributeList = self.createSubElement(MultilingualTextItem,"AttributeList")
        self.createSubElement(AttributeList,"Culture").text = "en-US"
        self.Comment =  self.createSubElement(AttributeList,"Text")
        
    def addCall(self):
        Call = self.createSubElement(self.Parts,"Call","UId")
        self.CallId = Call.get("UId")
        self.CallInfo = self.createSubElement(Call,"CallInfo")
        self.CallInfo.set("BlockType","FB")
        Instance = self.createSubElement(self.CallInfo,"Instance","UId")
        Instance.set("Scope","GlobalVariable")
        self.Component = self.createSubElement(Instance,"Component")  
        
    def addParameter(self,parameterName,inOutType,dataType):
        Parameter = self.createSubElement(self.CallInfo,"Parameter")
        Parameter.set("Name",parameterName)
        Parameter.set("Section",inOutType)
        Parameter.set("Type",dataType)
        
    def addAccess(self,string,Scope,literalType="",literalValue=""):
        import re
        Access = self.createSubElement(self.Parts,"Access","UId")
        Access.set("Scope",Scope)
        if Scope == "LiteralConstant":
            Constant = self.createSubElement(Access,"Constant")
            self.createSubElement(Constant,"ConstantType").text = literalType
            if literalType == "String":
                self.createSubElement(Constant,"ConstantValue").text = "'" + literalValue + "'"
            else:
                self.createSubElement(Constant,"ConstantValue").text = literalValue
        elif Scope == "GlobalVariable" or Scope == "LocalVariable":
            Symbol = self.createSubElement(Access,"Symbol")
            for x in string.split("."):
                Component = self.createSubElement(Symbol,"Component")
                result = re.split('\[|\]',x)            #Looking for [num]
                Component.set("Name",result[0])
                if len(result) > 1:
                    Component.set("AccessModifier","Array")
                    ArrayAccess = self.createSubElement(Component,"Access")
                    ArrayAccess.set("Scope","LiteralConstant")
                    ArrayConstant = self.createSubElement(ArrayAccess,"Constant")
                    self.createSubElement(ArrayConstant,"ConstantType").text = "DInt"
                    self.createSubElement(ArrayConstant,"ConstantValue").text = result[1]
                    
        return Access.get("UId")
        
    def addIdentCon(self,accessId,PartId,Name):
        Wire = self.createSubElement(self.Wires,"Wire","UId")
        IdentCon = self.createSubElement(Wire,"IdentCon")
        IdentCon.set("UId",accessId)
        NameCon = self.createSubElement(Wire,"NameCon")
        NameCon.set("UId",PartId)
        NameCon.set("Name",Name)
        
    def addOR(self,size):
        part = self.createSubElement(self.Parts,"Part","UId")
        part.set("Name","O")
        partId = part.get("UId")
        TemplateValue = self.createSubElement(part,"TemplateValue")
        TemplateValue.set("Name","Card")
        TemplateValue.set("Type","Cardinality")
        TemplateValue.text = size
        return partId
        
    def spawnPart(self,name,type,negated=False):
        part = self.createSubElement(self.Parts,"Part","UId")
        part.set("Name",type)
        if negated and type == "Contact":
            Negated = self.createSubElement(part,"Negated")
            Negated.set("Name","operand")
        partId = part.get("UId")
        AccessId = self.addAccess(name,"GlobalVariable")
        self.addIdentCon(AccessId,partId,"operand")
        return partId
        
    def OR(self,operands,destinationCallId,destinationName):
        OR = self.addOR(str(len(operands)))
        for x in range(len(operands)):
            id = self.spawnPart(operands[x],"Contact")
            self.addEN(id,"in")
            self.addConnection(id,"out",OR,"in" + str(x + 1))
        self.addConnection(OR,"out",destinationCallId,destinationName)
        
    def AND(self,operands,destinationCallId,destinationName):
        list = [] 
        for x in range(len(operands)):
            id = self.spawnPart(operands[x],"Contact")
            list.append(id)
            if x == 0:
                self.addEN(id,"in")
            else:
                self.addConnection(list[x-1],"out",id,"in")
        self.addConnection(list[-1],"out",destinationCallId,destinationName)
        
    def addConnection(self,AccessIdOut,AccessIdOutName,AccessIdIn,AccessIdInName):
        Wire = self.createSubElement(self.Wires,"Wire","UId")
        Out = self.createSubElement(Wire,"NameCon")
        Out.set("UId",AccessIdOut)
        Out.set("Name",AccessIdOutName)
        In = self.createSubElement(Wire,"NameCon")
        In.set("UId",AccessIdIn)
        In.set("Name",AccessIdInName)
        
    def addEN(self,partId,connectionName):
        NameCon = self.createSubElement(self.Powerrail,"NameCon")
        NameCon.set("UId",partId)
        NameCon.set("Name",connectionName)
  
    def loadParameterStr(self,strParameter,connectionName,Scope="GlobalVariable",literalType = "Bool",literalValue = "true"):
        document = ET.fromstring(strParameter)
        self.addParameter(document.get("Name"),document.get("Section"),document.get("Type"))
        accessId = self.addAccess(connectionName,Scope,literalType,literalValue)
        self.addIdentCon(accessId,str(self.CallId),document.get("Name"))
