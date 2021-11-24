# -*- coding: UTF-8 -*-
from .desc import LetDesc
import re
import pandas as pd
from os import path
class LetTextDesc(LetDesc):
    def __init__(self,default=None,name=None):
        super().__init__()
        self._writable = True
    def __set__(self,instance,value):
        assert self._writable ,EOFError("attempt to recover LetTextDesc")
        super().__set__(instance,value)
        self._writable = False

class Document():
    text = LetTextDesc("",'text')
    def __init__(self,text):
        self.text = text
        self._x_path_df = self.__init_xpath()
    def __init_xpath(self):
        text = self.text
        resp = {
            'pk':[],
            'indent':[],
            'content':[],
        }
        for pk,row in enumerate(text.split("\n")):
            tmp = self.__parse_indent(pk,row)
            if tmp is None:
                continue
            indent,content = tmp
            resp['pk'].append(pk+1)
            resp['indent'].append(indent)
            resp['content'].append(content)
        df = pd.DataFrame(resp)
        df['x_path'] = self.__calcu_x_path(df)
        return df.loc[:,['pk','indent', 'x_path','content'  ]]
    def __calcu_x_path(self,df):
        df = df.copy()
        df['indent_baise'] = df['indent'] - df['indent'].shift(1)
        df = df.fillna(value=0)
        df['x_path'] = pd.NaT
        for k,row in df.iterrows():
            indent = int(row.indent)
            bs = int(row.indent_baise)
            if indent==0:
                row.x_path = "/"
                df.iloc[k] = row
                continue
            last_row = df.iloc[k-1]
            # assert bs<2,ValueError(f"row {k}：{row.content} indent error")
            if bs>=1:
                last_row = df.iloc[k-1]
                row.x_path = path.join(str(last_row.x_path),str(last_row.pk))
                df.iloc[k] = row
                continue
            else:
                last_row = df.iloc[k-1]
                last_x_path = last_row.x_path
                if bs==0:
                    row.x_path = last_x_path
                else:
                    for i in range(-bs):
                        last_x_path = path.dirname(last_x_path)
                    row.x_path = last_x_path
                df.iloc[k] = row
                continue
            
        return df.x_path
    def __parse_indent(self,pk,row):
        pk+=1
        if len(row)==0:
            return None
        row = str(row)
        if row[0] == "#":
            return None
        
        indent = re.match("^ *",row).end()
        assert indent%4==0,EOFError(f"第{pk}行锁进错误:{row}")
        row = row[indent:]
        if len(re.search("\S*",row).string)==0:
            return None
        indent = indent//4
        return indent,row
    @classmethod
    def read_txt(cls,fpath):
        with open(fpath,'r') as fp:
            text = fp.read()
        return cls(text)
    @property
    def df(self):
        return self._x_path_df.copy()


    
    