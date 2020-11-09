import baostock as bs
import pandas as pd
import csv
import os

def download_data(code):
    #### 登陆系统 ####
    lg = bs.login()
    # 显示登陆返回信息
    print('login respond error_code:' + lg.error_code)
    print('login respond  error_msg:' + lg.error_msg)

    #### 获取沪深A股历史K线数据 ####
    # 详细指标参数，参见“历史行情指标参数”章节；“分钟线”参数与“日线”参数不同。“分钟线”不包含指数。
    # 分钟线指标：date,time,code,open,high,low,close,volume,amount,adjustflag
    # 周月线指标：date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg
    rs = bs.query_history_k_data_plus(code,
                                      "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
                                      start_date='1990-12-19', end_date='2017-12-31',
                                      frequency="d", adjustflag="3")
    print('query_history_k_data_plus respond error_code:' + rs.error_code)
    print('query_history_k_data_plus respond  error_msg:' + rs.error_msg)

    #### 打印结果集 ####
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)

    #### 结果集输出到csv文件 ####
    csv_name = "D:\\" + code + ".csv"
    print(csv_name)
    result.to_csv(csv_name, index=False)
    print(result)

    #### 登出系统 ####
    bs.logout()

def get_stock_code():
    data = []

    with open('D:\\demo_assignDayData.csv', 'r', encoding='utf-8') as f_input:

        for line in f_input:
            data.append(list(line.strip().split(',')))

    dataset = pd.DataFrame(data)
    print(dataset)
    index = 1
    for row in dataset.iterrows():
        stock_index = dataset.iat[index, 1]
        print(stock_index)
        print(index)
        # 获取指定日期全部股票的日K线数据
        download_data(stock_index)
        if index > 10:
            break
        index = index + 1

if __name__ == '__main__':
    get_stock_code()