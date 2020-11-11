import numpy as np
import pandas as pd
# from scipy import signal
# from scipy import signal   #滤波等
from scipy import signal
import os
import talib
from talib import MA_Type

#常量定义
交易日 = 0
开 = 1
收 = 4
低 = 3
高 = 2
成交量 = 5
收盘价字段名 = '收盘'
日均线周期1 = 50
日均线周期2 = 200
distance = 100 #相邻峰之间的最小水平距离, 先移除较小的峰，直到所有剩余峰的条件都满足为止

class Stock:
    '股票类'
    # 行情数据 = pd.DataFrame()
    def __init__(self, 路径,股票代码):
        行情数据文件 = 路径 + 股票代码 + ".csv"
        self.股票代码 = 股票代码
        # self.行情数据 = pd.read_csv(行情数据文件, usecols=[交易日, 开, 收, 低, 高], encoding='gb2312')
        self.行情数据 = pd.read_csv(行情数据文件, usecols=[交易日, 开, 收, 低, 高, 成交量], encoding='gb2312')
        self.获取波峰波谷对应索引序列()
        self.获取波峰波谷之间最高最低价索引序列()
        self.获取放量跳空突破信号()


    def 获取波峰波谷对应索引序列(self):
        df = self.行情数据
        收盘价序列 = df[收盘价字段名]
        成交量序列 = df['成交量']

        均线1 = talib.MA(收盘价序列, timeperiod=日均线周期1)
        反转均线1 = -均线1
        均线2 = talib.MA(收盘价序列, timeperiod=日均线周期2)

        成交量均线 = talib.MA(成交量序列, timeperiod=日均线周期1)

        df.insert(6, '50MA', 均线1, allow_duplicates=True)
        df.insert(7, '200MA', 均线2, allow_duplicates=True)
        df.insert(8, 'VOLMA', 成交量均线, allow_duplicates=True)

        波峰索引序列 = signal.find_peaks(均线1, distance=distance)
        波谷索引序列 = signal.find_peaks(反转均线1, distance=distance)

        #波峰对应的标志列都赋值1，波谷对应的赋值-1,找到对应的日期赋值给日期列
        波峰df = pd.DataFrame(波峰索引序列[0])
        波谷df = pd.DataFrame(波谷索引序列[0])

        波峰df.insert(loc=1, column='波峰波谷标志', value='1') #所有波峰的标志字段置为1
        波谷df.insert(loc=1, column='波峰波谷标志', value='-1') #所有波谷的标志字段置为-1
        #两个df合并
        frames = [波峰df,波谷df]
        result = pd.concat(frames)
        result.rename(columns={0: '波峰波谷索引'}, inplace=True)
        result = result.sort_values(by='波峰波谷索引')
        result.reset_index(drop=True, inplace=True)
        self.波峰波谷索引 = result
        # print(result)

    def 获取波峰波谷之间最高最低价索引序列(self):
        #最高最低价标志为1代表该索引位置为波谷到波峰之间的最大值，如为-1则为波峰到波谷之间的最小值
        最高最低价索引 = pd.DataFrame(columns=['最高最低价索引', '最高最低价值', '最高最低价标志'])
        # for row in df.itertuples(index=True, name='Pandas'):
        for index, row in self.波峰波谷索引.iterrows():
            if index != 0:
                前一波峰波谷索引 = self.波峰波谷索引.iat[index - 1, 1]
                当前波峰波谷索引 = row['波峰波谷索引']
                if row["波峰波谷标志"] == '1':
                    max = self.行情数据.loc[前一波峰波谷索引:当前波峰波谷索引, '收盘'].max()
                    maxindex = self.行情数据.loc[前一波峰波谷索引:当前波峰波谷索引, '收盘'].idxmax()
                    new_line = [maxindex, max, 1]
                    最高最低价索引.loc[index] = new_line
                else:
                    min = self.行情数据.loc[前一波峰波谷索引:当前波峰波谷索引, '收盘'].min()
                    minindex = self.行情数据.loc[前一波峰波谷索引:当前波峰波谷索引, '收盘'].idxmin()
                    new_line = [minindex, min, -1]
                    最高最低价索引.loc[index] = new_line
        self.最高最低价索引 = 最高最低价索引
        # print(最高最低价索引)

    def 获取放量跳空突破信号(self):
        放量跳空信号索引 = pd.DataFrame(columns=['放量跳空信号索引', '日期','股票代码'])
        result = self.波峰波谷索引
        df = self.行情数据
        # print(len(result))
        for index, row in result.iterrows():
            if row['波峰波谷标志'] == '-1' and index < (len(result)-1):
                当前波谷索引 = row['波峰波谷索引']
                # print(index)
                下一波峰索引 = result.iat[index + 1, 0]

                波谷波峰间行情片段 = df.loc[当前波谷索引:下一波峰索引]  # 根据波谷索引及下一波峰索引对行情数据切片
                # print(波谷波峰间行情片段)
                for index, row in 波谷波峰间行情片段.iterrows():
                    多头 = False
                    跳空 = False
                    放量 = False
                    if row['50MA'] > row['200MA']:
                        多头 = True

                    if row['成交量'] > (row['VOLMA'] * 1.5):
                        放量 = True

                    if row['最低'] > df.iat[index + 1, 4]:  # 当天最低价大于前一天的最高价，为跳空
                        跳空 = True

                    if 多头 and 跳空 and 放量:
                        # new_line = [index]
                        new_line = {'放量跳空信号索引': index, '日期': df.iat[index, 0],'股票代码': self.股票代码}
                        # 放量跳空信号索引.loc[index] =
                        放量跳空信号索引 = 放量跳空信号索引.append(new_line, ignore_index=True)
            else:
                x = 1

        self.放量跳空信号索引 = 放量跳空信号索引

信号 = pd.DataFrame(columns=['放量跳空信号索引', '日期','股票代码'])
for info in os.listdir('.\\cyb\\'):
    xx=1
    code = info.split(".")[0]
    print(code)
    stock = Stock('.\\cyb\\',code)
    frames = [信号, stock.放量跳空信号索引]
    信号 = pd.concat(frames)
    # print(stock.放量跳空信号索引)

信号.to_csv('singal.csv', index=False, sep=',')