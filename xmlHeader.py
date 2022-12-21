from xml.dom import minidom
import xml.etree.cElementTree as ET

global id
id = 0

class father():
    def createSubElement(self,parent,name,type = None):
        global id
        child = ET.SubElement(parent,name)
        if type != None:
            child.set(type, str(id))
            id = id + 1
        return child
        
    def save(self):
        with open(self.Name + ".xml", "w") as file:
            file.write(minidom.parseString(ET.tostring(self.root)).toprettyxml(indent = "\t"))
        
    def __str__(self):
        return minidom.parseString(ET.tostring(self.root)).toprettyxml(indent = "\t")

class xmlHeader(father):
    def __init__(self,Name):
        self.Name = Name
        self.root = ET.Element("Document")
        SWBlocksFC = self.createSubElement(self.root, "SW.Blocks.FC","ID")
        AttributeList = self.createSubElement(SWBlocksFC,"AttributeList")
        self.createSubElement(AttributeList,"AutoNumber").text = "true"
        self.createSubElement(AttributeList,"MemoryLayout").text = "Optimized"
        self.createSubElement(AttributeList,"Name").text = str(self.Name)
        self.ProgrammingLanguage = self.createSubElement(AttributeList,"ProgrammingLanguage")
        self.ProgrammingLanguage.text = "LAD"
        self.ObjectList = self.createSubElement(SWBlocksFC,"ObjectList")