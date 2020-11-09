import numpy as np
import pandas as pd
# from scipy import signal
# from scipy import signal   #滤波等
from scipy import signal

import talib
from talib import MA_Type
#常量定义
交易日 = 0
开 = 1
收 = 4
低 = 3
高 = 2
成交量 = 0
收盘价字段名 = '收盘'
日均线周期1 = 50
日均线周期2 = 200
distance = 100 #相邻峰之间的最小水平距离, 先移除较小的峰，直到所有剩余峰的条件都满足为止

class Stock:
    '股票类'
    # 行情数据 = pd.DataFrame()
    def __init__(self, 股票代码):
        行情数据文件 = 股票代码 + ".csv"
        self.行情数据 = pd.read_csv(行情数据文件, usecols=[交易日, 开, 收, 低, 高], encoding='gb2312')
        self.获取波峰波谷对应索引序列()

    def 获取波峰波谷对应索引序列(self):
        df = self.行情数据
        收盘价序列 = df[收盘价字段名]

        均线1 = talib.MA(收盘价序列, timeperiod=日均线周期1)
        反转均线1 = -均线1
        均线2 = talib.MA(收盘价序列, timeperiod=日均线周期2)

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
                    minindex = self.行情数据.loc[前一波峰波谷索引:当前波峰波谷索引, '收盘'].idxmix()
                    new_line = [minindex, min, -1]
                    最高最低价索引.loc[index] = new_line

