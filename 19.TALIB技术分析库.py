import tushare as ts
ts.set_token('你的token')
pro = ts.pro_api()

import pandas as pd
import matplotlib; matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = 'SimHei'  #让matplotlib支持微软雅黑中文
plt.rcParams['axes.unicode_minus'] = False  #解决负号无法正常使用的问题

data = pro.daily(ts_code='601988.SH', start_date='20190501', end_date='20200508')
data = data.sort_values('trade_date', ascending = True)
data = data.set_index('trade_date')
data.index = pd.to_datetime(data.index)
close = data.close
volume = data.vol
high = data.high
low = data.low

import talib as ta
# 中文文档：https://github.com/HuaRongSAO/talib-document
# 中文文档：https://www.bookstack.cn/read/talib-zh/README.md
# 英文文档：https://mrjbq7.github.io/ta-lib/

# K线形态识别：参考02.识别K线图的形态

# 移动平均线
# ta.MA(close,timeperiod=30,matype=0)
# matype分别对应：0=SMA, 1=EMA, 2=WMA, 3=DEMA, 4=TEMA, 5=TRIMA, 6=KAMA, 7=MAMA, 8=T3 (Default=SMA)
sma10_talib = ta.MA(close, timeperiod = 10, matype = 0)

# 异同移动平均线MACD
#macd, macdsignal, macdhist = ta.MACD(close, fastperiod = 12, slowperiod = 26)
macdDIFF, macdDEA, macd = ta.MACDEXT(close, fastperiod=12, fastmatype=1, slowperiod=26, slowmatype=1, signalperiod=9, signalmatype=1)
macd = macd * 2

# 布林带
upper, middle, lower = ta.BBANDS(close, timeperiod = 20, nbdevup=2, nbdevdn=2, matype = 0)

# 相对强弱指数RSI，采用RSI = 100 - 100 / (1 + RS)计算
rsi = ta.RSI(close, timeperiod = 6)

# 计算收盘价的动量
m = ta.MOM(close, timeperiod = 5)

# OBV能量潮(累积OBV)
OBV = ta.OBV(close, volume)

# KD指标
# ta.STOCH算出来和主流平台不一样
