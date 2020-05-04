import tushare as ts
ts.set_token('你的token')
pro = ts.pro_api()

import pandas as pd
import matplotlib; matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import numpy as np
plt.rcParams['font.sans-serif'] = 'SimHei'  #让matplotlib支持微软雅黑中文
plt.rcParams['axes.unicode_minus'] = False  #解决负号无法正常使用的问题

# 安装Ta-Lib，使用whl文件安装而非pip
import talib
# 技术文档：https://github.com/HuaRongSAO/talib-document

data = pro.daily(ts_code='600000.SH', start_date='20180101', end_date='20200331')
data = data.sort_values('trade_date', ascending = True)
data = data.set_index('trade_date')
data.index = pd.to_datetime(data.index)

Open = np.array(data['open'])
High = np.array(data['high'])
Low = np.array(data['low'])
Close = np.array(data['close'])

# “早晨之星”释出下跌趋势的反转信号
# “黄昏之星”释出上升趋势的反转信号

# “早晨之星”一般由连续3根蜡烛图组成
# 第一个蜡烛图具有较长的绿色实体
# 第二个是价格振幅较小
# 第三个具有红色实体且实体长度大于第一个蜡烛图实体长度较多
# 此外第二个蜡烛图的 实体部分一般落在第一个和第三个蜡烛图实体的【下】方
#
# 第一天的收盘价<开盘价（绿），第二天收盘价与开盘价接近，第三天收盘价>开盘价且差值大于第一天差值的一半
# 第二天的收盘价和开盘价均小于第一天的收盘价和第三天的开盘价
#
# 如果在下跌行情中出现早晨之星，股票的买方市场的力量在逐渐增大，股价可能有利好的趋势

# “黄昏之星”一般出现在上涨行情中，并释出上升趋势的反转信号，即未来有可能下跌
# “黄昏之星”一般由连续3根蜡烛图组成
# 第一个蜡烛图具有较长的红色实体
# 第二个是价格振幅较小
# 第三个具有绿色实体且实体长度大于第一个蜡烛图实体长度较多
# 此外第二个蜡烛图的 实体部分一般落在第一个和第三个蜡烛图实体的【上】方
# 黄昏之星的出现预示着股票市场由买方市场逐渐转变为卖方市场，股票未来可能有下跌的趋势

# 乌云压顶
# 前一期红色蜡烛实体，当期绿色蜡烛实体；当期开盘价高于前一期收盘价，当期收盘价位于前一期实体下半部分
# 前期连续两期的收益率为正
# 乌云盖顶预示着市场中空头力量强势，市场可能要处于下跌行情
# 如果发生乌云压顶的第二天的收盘价低于或者等于前一天的开盘价时，乌云压顶就会变成空头吞噬信号

# 不同的人在K线图中找出的形态的日期可能不同，由计算机找出可减少主观性
# penetration = 0这个参数很有可能导致给出的结果不正确

# 早晨之星   函数名：CDLMORNINGSTAR
data['MorningStar']=talib.CDLMORNINGSTAR(Open, High, Low, Close)
data[data['MorningStar']==100] # 正100

# 黄昏之星   函数名：CDLEVENINGSTAR
data['EveningStar']=talib.CDLEVENINGSTAR(Open, High, Low, Close)
data[data['EveningStar']==-100] # 负100

# 乌云压顶   函数名：CDLDARKCLOUDCOVER
data['DarkCloud'] = talib.CDLDARKCLOUDCOVER(Open, High, Low, Close)
data[data['DarkCloud']==-100] # 负100

from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mdates

date_wewannaanalyse = data['2018-05-10':'2018-06-05']

ax1 = plt.subplot()
ax1.xaxis_date()
df_ohlc = date_wewannaanalyse[['open','high','low','close']]
df_ohlc = df_ohlc.reset_index()
df_ohlc['trade_date'] = df_ohlc['trade_date'].map(mdates.date2num)
candlestick_ohlc(ax1, df_ohlc.values, width = 1, colordown = 'green', colorup = 'red', alpha = 0.75)
plt.title('浦发银行历史股价K线图')
plt.show()

# 预测信号并不一定正确，不能只靠信号判断，要综合各种信息
# 尝试使用别的形态识别函数
