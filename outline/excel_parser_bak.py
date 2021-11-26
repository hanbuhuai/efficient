# -*- coding: UTF-8 -*-
from .document import Document
from os import path
import pandas as pd
import numpy as np
import xlwt
class ExcelParser():
    def __init__(self,x_path_df):
        self.__df =self.__update_x_path(x_path_df) 
        self.workbook = xlwt.Workbook()
        self.worksheet = self.workbook.add_sheet('My sheet')
    @classmethod
    def read_txt(cls,fpath):
        dom = Document.read_txt(fpath)
        return cls(dom.df)
    def format_df_columns(self,df):
        column = list(df.columns) 
        column.remove('content')
        column.append('content')
        return df[column]
    def __calcu_row_span(self,pk,df):
        
        sub_df = self.sub_childs(pk,df)
        if len(sub_df)==0:
            return 1
        calcu_df = sub_df.groupby(['indent'],as_index=False).count()
        return calcu_df.pk.max()
    def __update_x_path(self,df):
        df = df.copy()
        df["col_span"] = df.content.map(lambda item: len(item.split("|")))
        df['row_span'] = df.pk.map(lambda pk: self.__calcu_row_span(pk,df=df))
        df = self.__calcu_col_start(df)
        df = self.__calcu_row_start(df)
        return self.format_df_columns(df) 

    def sub_childs(self,pk,df=None):
        #先找到目标行
        df = df.copy() if not df is None else self.__df.copy()
        tar_row = df.loc[df.pk==pk,:]
        if len(tar_row)==0:
            return False
        tar_row = tar_row.iloc[0]
        tar_x_path = tar_row.x_path
        df['hit'] = df.x_path.map(lambda x_path: self.is_sub_xpath(
            x_path,
            path.join(tar_x_path,str(tar_row.pk))
        ))
        
        
        df = df.loc[df.hit==True,:].drop(columns=['hit'])
        return df
    
    def is_sub_xpath(self,child_path,parent_path):
        child_parents = [child_path]
        d = child_path
        while not d=='/':
            d = path.dirname(d)
            child_parents.append(d)
        return parent_path in child_parents
    def __calcu_col_start(self,df):
        df =df.copy()
        columns = df.groupby(['indent'],as_index=False)
        col_start = 0
        right =pd.DataFrame(columns=df.columns)
        for col_k ,col_df in columns:
            col_df = col_df.copy()
            col_df['col_start'] = col_start
            right =pd.concat([right,col_df])
            col_start += col_df.col_span.max()
        df = pd.merge(df,right.loc[:,['pk','col_start']],on="pk",how="left")
        
        df['col_start'] =df['col_start'].astype('int')
        return df

    def __calcu_row_start(self,df):
        df = df.copy()
        df.row_start= pd.NaT
        #计算同级目录row_baise
        dir_dfs = df.groupby(['x_path'])
        right =pd.DataFrame(columns=df.columns)
        for dir_k,dir_df in dir_dfs:
            dir_df = dir_df.copy()
            dir_df['sibling_row_baise'] = dir_df.shift(1).row_span.cumsum()
            dir_df = dir_df.fillna(value=0)
            right =pd.concat([right,dir_df])
        df = pd.merge(df,right.loc[:,['pk','sibling_row_baise']],on="pk",how="left")
        df['sibling_row_baise'] =df['sibling_row_baise'].astype('int')
        #计算row start
        df['row_start']=pd.NaT
        for k,row in df.iterrows():
            
            #找爸爸
            parent_id = path.split(row.x_path)[-1]
            if len(parent_id) ==0:
                row.row_start = row.sibling_row_baise
                df.iloc[k] = row
                continue
            parent_df = df.loc[df.pk==int(parent_id),:]
            parent_row= parent_df.iloc[0]
            row.row_start = parent_row.row_start + row.sibling_row_baise
            df.iloc[k] = row
        return df

    def draw_row(self,k,row,row_baise=0,col_baise=0):
        y = int(row.row_start) + row_baise
        x = int(row.col_start) + col_baise
        row_span = int(row.row_span) 
        col_span = int(row.col_span) 
        contents = str(row.content).split("|")
        for b, text in enumerate(contents):
            try:
                
                if row_span==1:
                    self.worksheet.write(y,x+b, label = text)
                else:
                    self.worksheet.write_merge(y, y+row_span-1, x+b, x+b,text)
            except Exception as err:
                print(err)
                print(row)
                exit()
            
    def save(self,fname,row_baise=0,col_baise=0):
        df = self.__df.copy()
        
        for k,row in df.iterrows():
            self.draw_row(k,row,row_baise=row_baise,col_baise=col_baise)
        self.workbook.save(fname)
        return fname
    def dev(self):
        df = self.__df.copy()
        shape_df = df.groupby(['indent'],as_index=False).count()
        print(shape_df)
    @property
    def df(self):
        return self.__df
    @df.setter
    def df(self,value):
        self.__df = value
if __name__ == "__main__":
    m  = ExcelParser.read_txt('test.txt')
    m.dev()
# m.save("opt.xls")

