from xmlHeader import father
import xml.etree.cElementTree as ET

class Global_DB(father):
    def __init__(self,Name):
        self.Name = Name
        self.folder = "DefaultDBs"
        self.root = ET.Element("Document")
        SWBlocksGlobalDB = self.createSubElement(self.root, "SW.Blocks.GlobalDB","ID")
        AttributeList = self.createSubElement(SWBlocksGlobalDB,"AttributeList")
        Interface = self.createSubElement(AttributeList,"Interface")
        Sections = self.createSubElement(Interface,"Sections")
        Sections.set('xmlns',"http://www.siemens.com/automation/Openness/SW/Interface/v5")
        self.Section = self.createSubElement(Sections,"Section")
        self.Section.set("Name","Static")
        Name = self.createSubElement(AttributeList,"Name").text = Name
        ProgrammingLanguage = self.createSubElement(AttributeList,"ProgrammingLanguage").text = "DB"
    
    def addMember(self,name,dataType):
        Member = self.createSubElement(self.Section,"Member")
        Member.set("Name",name)
        Member.set("Datatype",dataType)
        AttributeList = self.createSubElement(Member,"AttributeList")
        BooleanAttribute = self.createSubElement(AttributeList,"BooleanAttribute")
        BooleanAttribute.text = "false"
        BooleanAttribute.set("Name","ExternalAccessible")
        BooleanAttribute.set("SystemDefined","true")
        
        BooleanAttribute = self.createSubElement(AttributeList,"BooleanAttribute")
        BooleanAttribute.text = "false"
        BooleanAttribute.set("Name","ExternalVisible")
        BooleanAttribute.set("SystemDefined","true")
        
        BooleanAttribute = self.createSubElement(AttributeList,"BooleanAttribute")
        BooleanAttribute.text = "false"
        BooleanAttribute.set("Name","ExternalWritable")
        BooleanAttribute.set("SystemDefined","true")
        
        BooleanAttribute = self.createSubElement(AttributeList,"BooleanAttribute")
        BooleanAttribute.text = "false"
        BooleanAttribute.set("Name","SetPoint")
        BooleanAttribute.set("SystemDefined","true")