# -*- coding: UTF-8 -*-
from .document import Document
import pandas as pd
from os import path
import json
class JsonDocument():
    def __init__(self,x_path_df,cur_pk=0,root='root'):
        self.__df =x_path_df
        self.__tar_row = self.__load_tar_row(cur_pk,root)
    def __load_tar_row(self,cur_pk,root):
        if cur_pk==0:
            resp = pd.Series({
                'pk':0,
                'content':root,
                'x_path':None,
                'indent':None,
            })
        else:
            df = self.__df.copy()
            resp = df.loc[df.pk==cur_pk].iloc[0]
        return resp

    @classmethod
    def read_txt(cls,fpath,**kw):
        dom = Document.read_txt(fpath)
        return cls(dom.df,**kw)
    @property
    def childs(self):
        df = self.__df.copy()
        child_xpath = self.child_xpath
        return [self.__class__(self.__df.copy(),cur_pk=row.pk) for k,row in df.loc[df.x_path==child_xpath,:].iterrows()]
    @property
    def x_path(self):
        if self.__tar_row.pk==0:
            x_path = ""
        else:
            x_path =  self.__tar_row.x_path
        return x_path
    @property
    def pk(self):
        return int(self.__tar_row.pk) 
    @property
    def content(self):
        return self.__tar_row.content
    @property
    def child_xpath(self):
        if self.__tar_row.pk==0:
            x_path = "/"
        else:
            x_path = path.join(self.x_path,str(self.pk) )
        return str(x_path)

    def __repr__(self):
        return f"<{self.__class__.__name__} pk={self.pk} content={self.content}>"
    def to_dict(self):
        content_ar = self.content.split("|")
        
        resp = {
            'pk':self.pk,
            'key':content_ar[0]
        }
        if len(content_ar)>1:
            resp['value'] = content_ar[1]
        childs = self.childs
        if len(childs)==0:
            return resp
        resp['childs'] = []
        for cm in childs:
            resp['childs'].append(cm.to_dict())
        return resp

    def to_json(self):
        return json.dumps(self.to_dict())
    def save(self,fname):
        with open(fname,"w") as fp:
            json.dump(self.to_dict(),fp)
    @property
    def df(self):
        return self.__df.copy()

