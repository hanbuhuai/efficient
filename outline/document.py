# -*- coding: UTF-8 -*-
from .desc import LetDesc
import re
import pandas as pd
from os import path
import time
import numpy as np
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
    
    def get_row_by_pks(self,pk_list):
        pass
    def to_dense(self):
        #转化为密集阵
        df = pd.DataFrame(self.df) 
        shape_df = df.groupby(['indent'],as_index=False).count()
        columns = [f"c_{k}" for k in shape_df.indent.values] 
        res_data = []
        for k,row in df.iterrows():
            x_path = []
            row_array = np.ones(shape=(len(columns)),dtype=np.int64) * -1
            
            if row.x_path!="/":
                x_path = row.x_path.split("/")[1:]
            x_path.append(str(row.pk))
            for idx,dk in enumerate(x_path) :
                row_array[idx] = int(dk)
            res_data.append(row_array)
        res_array = np.stack(res_data,axis=0)
        res_df = pd.DataFrame(data=res_array,columns=[ f"{k}_pk" for k in columns])
        right_df = df.loc[:,['pk','content']]
        for col in columns:
            left_k = f"{col}_pk"
            res_df = pd.merge(res_df,right_df,left_on=left_k,right_on='pk',how='left')
            res_df[left_k] = res_df['content']
            res_df = res_df.drop(columns=['content','pk'])
        rname_map = {f"{col}_pk":col for col in columns}
        return res_df.rename(rname_map,axis=1)
    