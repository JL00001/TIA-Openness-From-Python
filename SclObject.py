from xmlHeader import xmlHeader

class SclObject(xmlHeader):
    def __init__(self,unitName,folder):
        super().__init__(unitName,folder)
        SWBlocksCompileUnit = self.createSubElement(self.ObjectList, "SW.Blocks.CompileUnit","ID")
        self.ProgrammingLanguage.text = "SCL"
        SWBlocksCompileUnit.set("CompositionName", "CompileUnits")
        AttributeList = self.createSubElement(SWBlocksCompileUnit,"AttributeList")
        NetworkSource = self.createSubElement(AttributeList,"NetworkSource")
        self.StructuredText = self.createSubElement(NetworkSource,"StructuredText")
        self.StructuredText.set("xmlns","http://www.siemens.com/automation/Openness/SW/NetworkSource/StructuredText/v3")
        self.tab = 0
        
    def addRegion(self,Name):
        self.createSubElement(self.StructuredText,"Token","UId").set("Text","REGION")
        self.createSubElement(self.StructuredText,"Blank","UId")
        self.createSubElement(self.StructuredText,"Text","UId").text = Name
        self.tabRight()
        self.NewLine()
        
    def endRegion(self):
        self.tabLeft()
        self.NewLine()
        self.createSubElement(self.StructuredText,"Token","UId").set("Text","END_REGION")
        self.NewLine()

    def NewLine(self):
        self.createSubElement(self.StructuredText,"NewLine","UId")
        if self.tab > 0:
            self.createSubElement(self.StructuredText,"Blank","UId").set("Num",str(self.tab))
        
    def tabRight(self):
        self.tab = self.tab + 3
        self.createSubElement(self.StructuredText,"Blank","UId").set("Num",str(self.tab))
        
    def tabLeft(self):
        self.tab = self.tab - 3
        
    def addGlobalVariable(self,GlobalVariable):
        Access = self.createSubElement(self.StructuredText,"Access","UId")
        Access.set("Scope","GlobalVariable")
        Symbol = self.createSubElement(Access,"Symbol","UId")
        for x in GlobalVariable.split("."):
            self.createSubElement(Symbol,"Component","UId").set("Name",str(x))
            Token = self.createSubElement(Symbol,"Token","UId")
            Token.set("Text",'.')
        Symbol.remove(Token)
        
    def addLiteralConstant(self,LiteralConstant):
        Access = self.createSubElement(self.StructuredText,"Access","UId")
        Access.set("Scope","LiteralConstant")
        Constant = self.createSubElement(Access,"Constant","UId")
        self.createSubElement(Constant,"ConstantValue","UId").text = "'" + LiteralConstant + "'"
        
        
    def addConstant(self,Value):
        Access = self.createSubElement(self.StructuredText,"Access","UId")
        Access.set("Scope","LiteralConstant")
        Constant = self.createSubElement(Access,"Constant","UId")
        self.createSubElement(Constant,"ConstantValue","UId").text = Value
        
    def addTypedConstant(self,TypedConstant):
        Access = self.createSubElement(self.StructuredText,"Access","UId")
        Access.set("Scope","TypedConstant")
        Constant = self.createSubElement(Access,"Constant","UId")
        self.createSubElement(Constant,"ConstantValue","UId").text = TypedConstant
        
    def addLocalVariable(self,LocalVariable):
        Access = self.createSubElement(self.StructuredText,"Access","UId")
        Access.set("Scope","LocalVariable")
        Symbol = self.createSubElement(Access,"Symbol","UId")
        for x in LocalVariable.split("."):
            self.createSubElement(Symbol,"Component","UId").set("Name",str(x))
            Token = self.createSubElement(Symbol,"Token","UId")
            Token.set("Text",'.')
        Symbol.remove(Token)
        
        
    def GlobalVariableEqualLiteralConstant(self,GlobalVariable,LiteralConstant):
        self.addGlobalVariable(GlobalVariable)
        self.createSubElement(self.StructuredText,"Blank","UId")
        self.createSubElement(self.StructuredText,"Token","UId").set("Text",":=")
        self.createSubElement(self.StructuredText,"Blank","UId")
        self.addLiteralConstant(LiteralConstant)
        self.createSubElement(self.StructuredText,"Token","UId").set("Text",";")
        self.NewLine()
        
    def GlobalVariableEqualBool(self,GlobalVariable,Bool):
        self.addGlobalVariable(GlobalVariable)
        self.createSubElement(self.StructuredText,"Blank","UId")
        self.createSubElement(self.StructuredText,"Token","UId").set("Text",":=")
        self.createSubElement(self.StructuredText,"Blank","UId")
        if Bool:
            self.addConstant('true')
        else:
            self.addConstant('false')
        self.createSubElement(self.StructuredText,"Token","UId").set("Text",";")
        self.NewLine()
        
    def GlobalVariableEqualConstant(self,GlobalVariable,Constant):
        self.addGlobalVariable(GlobalVariable)
        self.createSubElement(self.StructuredText,"Blank","UId")
        self.createSubElement(self.StructuredText,"Token","UId").set("Text",":=")
        self.createSubElement(self.StructuredText,"Blank","UId")
        self.addConstant(Constant)
        self.createSubElement(self.StructuredText,"Token","UId").set("Text",";")
        self.NewLine()
        
    def GlobalVariableEqualLocalVariable(self,GlobalVariable,LocalVariable):
        self.addGlobalVariable(GlobalVariable)
        self.createSubElement(self.StructuredText,"Blank","UId")
        self.createSubElement(self.StructuredText,"Token","UId").set("Text",":=")
        self.createSubElement(self.StructuredText,"Blank","UId")
        self.addLocalVariable(LocalVariable)
        self.createSubElement(self.StructuredText,"Token","UId").set("Text",";")
        self.NewLine()
        
    def GlobalVariableEqualTypedConstant(self,GlobalVariable,TypedConstant):
        self.addGlobalVariable(GlobalVariable)
        self.createSubElement(self.StructuredText,"Blank","UId")
        self.createSubElement(self.StructuredText,"Token","UId").set("Text",":=")
        self.createSubElement(self.StructuredText,"Blank","UId")
        self.addTypedConstant(TypedConstant)
        self.createSubElement(self.StructuredText,"Token","UId").set("Text",";")
        self.NewLine()
        



