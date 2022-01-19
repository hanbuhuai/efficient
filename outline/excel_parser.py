# -*- coding: UTF-8 -*-
from .document import Document
from os import path
import pandas as pd
import numpy as np
import xlwt
from collections import Iterable
class ExcelParser():
    def __init__(self,dense_df):
        self.__dense_df  = dense_df
        self.out_put_df  = self.make_out_put_df(dense_df)
    
    @classmethod
    def read_txt(cls,fpath):
        df = Document.read_txt(fpath).to_dense() 
        return cls(df)
    def make_out_put_df(self,df):
        df = df.fillna(value="<span>")
        for col in df.columns:
            col_obj = getattr(df,col)
            split_cmd = col_obj.str.contains("\|").values
            if True in split_cmd:
                expand_df = df[col].str.rsplit("|",expand=True)
                rename_map = {k:f"{col}_{k}" for k in expand_df.columns}
                df = pd.merge(df,expand_df.rename(rename_map,axis=1),how='left',left_index=True,right_index=True)
                df = df.drop(columns=[col])
        
        columns = sorted(df.columns) 
        df = df[columns]
        df = df.apply(lambda ds: ds.map(lambda x: x if not x is None else pd.NA))
        rename_map = {col_name:f"c_{k}" for k,col_name in enumerate(columns) }
        df = df.rename(rename_map,axis=1)
        return df
    def __transColumns(self,df):
        df = pd.DataFrame(df)
        columns = df.columns
        # if len(columns)
    def transColumns(self,prem):
        df = self.out_put_df.copy()
        columns = df.columns
        resp_columns = [ columns[k] for k in prem]
        df = df[resp_columns]
        self.out_put_df = df
    def __write_filter(self,df):
        columns = list(df.columns)
        __writeable__ = []
        for k,row in df.iterrows():
            r_dt = row.to_dict()
            r_dt_value =  r_dt.values()
            if "<span>" in r_dt_value:
                r_dt_set =set([ va  for va in r_dt.values() if pd.notnull(va) and not va=="<span>" ] ) 
                next_row = df.iloc[k+1]
                calcu_set =set(r_dt_set) & set(next_row.to_dict().values())
                if calcu_set == r_dt_set:
                    __writeable__.append(0)
                else:
                    __writeable__.append(1)
            else:
                __writeable__.append(1)
        df['__writeable__'] = __writeable__
        df = df.loc[df['__writeable__']==1,:].fillna(value="")
        # print(df)
        return df.reset_index(drop=True)
    def save(self,fname,columns=None):
        df = self.out_put_df.copy()
        index_columns = list(df.columns)
        if isinstance(columns,Iterable):
            rename_map = dict(zip(index_columns,columns))
            df = df.rename(rename_map,axis=1)
            index_columns = list(df.columns)
        df = self.__write_filter(df)
        df = pd.pivot_table(df,index=index_columns,fill_value="")
        df.to_excel(fname,sheet_name="sheet")
        return fname
if __name__ == "__main__":
    m  = ExcelParser.read_txt('test.txt')
    m.transColumns([2,1,0,3,4,5])
    # m.save(opt.xls)
    m.save("opt.xls",['module','client','role','sp','desc'])

