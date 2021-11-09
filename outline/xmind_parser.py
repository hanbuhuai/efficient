from .json_document import JsonDocument
from .document import Document
import xmind
from xmind.core.topic import TopicElement
from os import path,unlink
class XMindParser(JsonDocument):
    work_book = None
    sheet = None
    
    def __init__(self,x_path_df,**kw):
        super().__init__(x_path_df,**kw)
        self.__topic = self.create_topic()
    def create_topic(self):
        if self.pk==0:
            topic = self.sheet.getRootTopic()
        else:
            topic = TopicElement(ownerWorkbook=self.__class__.work_book)
        content_ar = self.content.split("|")
        topic.setTitle(content_ar[0])
        if len(content_ar)>1:
            topic.addLabel(content_ar[1])
        return topic
    
    def get_topic(self):
        childs = self.childs
        if len(childs)==0:
            return self.__topic
        for cm in self.childs:
            self.__topic.addSubTopic(cm.get_topic())
        return self.__topic

    @classmethod
    def parse(cls,text_fp,xmind_fp,title="default"):
        if path.isfile(xmind_fp):
            unlink(xmind_fp)
        cls.work_book = xmind.load(xmind_fp)
        cls.sheet = cls.work_book.getPrimarySheet()
        cls.sheet.setTitle(title)
        return cls.read_txt(text_fp,root=title)
    def save(self):
        cls = self.__class__
        self.get_topic()
        xmind.save(cls.work_book)
        
 