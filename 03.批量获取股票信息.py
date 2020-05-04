import pickle # 可以将对象以文件的形式存放在磁盘上
import os
import tushare as ts
ts.set_token('你的token')
pro = ts.pro_api()

# 以批量获取沪深300股票为例
def find_and_save_CSI_300():
    CSI_300_DF = ts.get_hs300s()
    tickers = CSI_300_DF['code'].values
    tickers_mod = []
    for ticker in tickers:
        if ticker[0] == '6':
            ticker = ticker + '.SH'
            tickers_mod.append(ticker)
        else:
            ticker = ticker + '.SZ'
            tickers_mod.append(ticker)
    # 储存文件，CSI_tickers.pickle为储存后的文件名，后缀为pickle
    # 将数据dump进文件中
    # 'wb'以二进制格式打开一个文件只用于写入
    # dump将数据通过特殊的形式转换为只有python语言认识的字符串，并写入文件
    with open('CSI_tickers.pickle','wb') as f:
        pickle.dump(tickers_mod, f)
    return tickers_mod

# USE CSI_300 LIST TO GET DATA FROM TUSHARE PRO
# 因为批量获取经常会发生超时，所以需要设置“断点续传”
# reload_CSI_300 = False一开始不重新加载，而是直接从pickle调取，如果没有数据则加载
def get_data_from_tushare(reload_CSI_300 = False):
    if reload_CSI_300:
        tickers_mod = find_and_save_CSI_300()
    else:
        with open('CSI_tickers.pickle','rb') as f:
            tickers_mod = pickle.load(f)
    # 创建文件夹，并命名为stock_dfs
    if not os.path.exists('stock_dfs'):
        os.makedirs('stock_dfs')
    for ticker_mod in tickers_mod:
        if not os.path.exists('stock_dfs/{}.csv'.format(ticker_mod)):
            df = pro.daily(ts_code = str(ticker_mod), start_date = '20200101',end_date = '20200131')
            df.reset_index(inplace = True)
            df.set_index('trade_date',inplace = True)
            df.to_csv('stock_dfs/{}.csv'.format(ticker_mod))
        else:
            print('We already have {}'.format(ticker_mod))

find_and_save_CSI_300()
get_data_from_tushare()

# 汇总收盘价到一张表中
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
style.use('ggplot')

def put_all_stock_price_into_one_df():
    with open('CSI_tickers.pickle','rb') as f:
        tickers = pickle.load(f)
    all_stock_price_df = pd.DataFrame() # 创建空DataFrame
    for count, ticker in enumerate(tickers):
        df = pd.read_csv('stock_dfs/{}.csv'.format(ticker))
        df.set_index('trade_date', inplace = True)
        # 将每列的列名更换为股票的代码
        df.rename(columns = {'close':ticker}, inplace = True)
        # drop参数1表示drop的是列
        df.drop(['index','ts_code','open','high','low','pre_close','change','pct_chg','vol','amount'], 1 ,inplace = True)
        if all_stock_price_df.empty:
            all_stock_price_df = df
        else: #outer断点续传，合入尚未存在的数据
            all_stock_price_df = all_stock_price_df.join(df, how = 'outer')
    all_stock_price_df.to_csv('CSI_300_Joined_closes.csv')
    
put_all_stock_price_into_one_df()

# Pandas相关性分析
# .corr(method = '')  kendall pearson spearman