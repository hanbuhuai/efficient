# -*- coding: UTF-8 -*-
from outline import ExcelParser,XMindParser
import argparse
from os import path
parser = argparse.ArgumentParser()
parser.add_argument("-outline","--outline",help="大纲文件地址",type=str)
parser.add_argument("-to","--to",help="xls,xmind",type=str,default='xls')
parser.add_argument("-save","--save",help="输出文件名称")
parser.add_argument("-cs","--columns",help="输出的列名称 用|隔开")
args = {k:v for k,v in parser.parse_args()._get_kwargs() if not v is None}

'''
outline 支持
'''
if args.get("outline",None):
    f_src   = args['outline']
    f_dir   = path.dirname(f_src)
    f_name  = path.splitext(path.split(f_src)[-1])[0]
    parse_to= args.get('to','xls')

    if parse_to=='xls':
        f_dist  = args.get('save',path.join(
            f_dir,
            f"{f_name}.xls"
        ))
        m = ExcelParser.read_txt(f_src)
        if path.isfile(f_src):
            if input(f"文件{f_dist}.xls已存在是否覆盖？【Y/n】").lower()=='y':
                columns = args.get('columns',None)
                columns = columns.split("|") if columns else None
                save_path = m.save(f_dist,columns)
                print(f"文件转化完:{save_path}")
    if parse_to=='xmind':
        f_dist  = args.get('save',path.join(
            f_dir,
            f"{f_name}.xmind"
        ))
        m = XMindParser.parse(f_src,f_dist,title=f_name)
        if path.isfile(f_src):
            if input(f"文件{f_name}.xls已存在是否覆盖？【Y/n】").lower()=='y':
                save_path = m.save()
                print(f"文件转化完:{f_dist}")
    
    
        


    


