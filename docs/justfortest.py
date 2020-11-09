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

行情数据文件 = '300024' + ".csv"
df = pd.read_csv(行情数据文件, usecols=[交易日, 开, 收, 低, 高], encoding='gb2312')

收盘价序列 = df[收盘价字段名]

均线1 = talib.MA(收盘价序列, timeperiod=日均线周期1)
反转均线1 = -均线1
均线2 = talib.MA(收盘价序列, timeperiod=日均线周期2)

去掉空数据的均线1 = np.asarray(收盘价序列[日均线周期1:len(均线1)])
波峰索引序列 = signal.find_peaks(均线1, distance=distance)
波谷索引序列 = signal.find_peaks(反转均线1, distance=distance)

# 波峰对应的标志列都赋值1，波谷对应的赋值-1,找到对应的日期赋值给日期列
波峰df = pd.DataFrame(波峰索引序列[0])
波谷df = pd.DataFrame(波谷索引序列[0])

# 波峰df.insert(loc=1, column='日期', value='-1')        #找到对应的日期
波峰df.insert(loc=1, column='波峰波谷标志', value='1')  # 所有波峰的标志字段置为1

# 波谷df.insert(loc=1, column='日期', value='-1')        #找到对应的日期
波谷df.insert(loc=1, column='波峰波谷标志', value='-1')  # 所有波谷的标志字段置为-1

frames = [波峰df, 波谷df]
result = pd.concat(frames)
result.rename(columns={0:'波峰波谷索引'},inplace=True)
# print(result)
result = result.sort_values(by='波峰波谷索引')
result.reset_index(drop=True, inplace=True)
print(result)

# 最高最低价索引 = pd.DataFrame(columns=['最高最低价索引', '最高最低价值', '最高最低价标志'],dtype = {'最高最低价索引' : str}
最高最低价索引 = pd.DataFrame(columns=['最高最低价索引', '最高最低价值', '最高最低价标志'],dtype = np.int8)
# for row in df.itertuples(index=True, name='Pandas'):
for index, row in result.iterrows():
    if index != 0:
        前一波峰波谷索引 = result.iat[index - 1, 0]
        当前波峰波谷索引 = row['波峰波谷索引']
        if row["波峰波谷标志"] == '1':
            max = df.loc[前一波峰波谷索引:当前波峰波谷索引, '收盘'].max()
            maxindex = df.loc[前一波峰波谷索引:当前波峰波谷索引, '收盘'].idxmax()
            new_line = [maxindex, max, '1']
            最高最低价索引.loc[index] = new_line
        else:
            min = df.loc[前一波峰波谷索引:当前波峰波谷索引, '收盘'].min()
            minindex = df.loc[前一波峰波谷索引:当前波峰波谷索引, '收盘'].idxmin()
            print (minindex)
            new_line = [minindex, min, '-1']
            最高最低价索引.loc[index] = new_line

print (最高最低价索引)