import pandas as pd
import csv
import os

def convert_path(path: str) -> str:
    seps = r'\/'
    sep_other = seps.replace(os.sep, '')
    return path.replace(sep_other, os.sep) if sep_other in path else path

#data = pd.read_csv("./300024.csv", encoding="gbk", sep=None)
# new_path = os.path.abspath(r'D:\Feena\pythonProject1\csv_new_files') #获取文件夹的路径
# domain = os.path.abspath(r'D:\Feena\pythonProject1\csv_files') #获取文件夹的路径
for info in os.listdir('.\\cyb_old\\'):
    filename = info
    info = os.path.join('.\\cyb_old\\',info) #将路径与文件名结合起来就是每个文件的完整路径
    info = convert_path(info)
    data=[]

#    with open('300024.csv', 'r',encoding='gbk') as f_input:
    with open(info, 'r', encoding='gbk') as f_input:
        for line in f_input:
            data.append(list(line.strip().split(',')))
    dataset=pd.DataFrame(data)

    dataset.columns = ['日期','开盘','最高','最低','收盘','成交量','成交额']
    dataset.drop([len(dataset)-1],inplace=True)
    dataset.drop(dataset.index[[0,1]],inplace=True)

    info_new = os.path.join('.\\cyb\\',filename)
    dataset.to_csv(info_new, encoding="gb2312",index=0)
