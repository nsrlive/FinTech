import tushare as ts
ts.set_token('你的token')
pro = ts.pro_api()

import pandas as pd
import numpy as np
import matplotlib; matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = 'SimHei'  #让matplotlib支持微软雅黑中文
plt.rcParams['axes.unicode_minus'] = False  #解决负号无法正常使用的问题

data = pro.daily(ts_code='601988.SH', start_date='20190501', end_date='20200430')
data = data.sort_values('trade_date', ascending = True)
data = data.set_index('trade_date')
data.index = pd.to_datetime(data.index)

# 价涨量增
# 价格与成交量同时增加，或者价格随着成交量的增加而增加
# 主要出现在上涨行情中，成交量的增加预示着股票价格上升的动能增强，股票价格会继续走高

from mplfinance.original_flavor import candlestick_ohlc
# matplotlib和pandas时间格式不一样，需要转换，先引入dates
import matplotlib.dates as mdates

ax1 = plt.subplot2grid((9,10),(0,0), rowspan = 4, colspan = 10)
ax2 = plt.subplot2grid((9,10),(5,0), rowspan = 4, colspan = 10, sharex = ax1)
ax1.xaxis_date()

df_ohlc = data[['open','high','low','close']]
df_ohlc = df_ohlc.reset_index()
df_ohlc['trade_date'] = df_ohlc['trade_date'].map(mdates.date2num)
candlestick_ohlc(ax1, df_ohlc.values, width = 1, colordown = 'green', colorup = 'red', alpha = 0.75)
ax1.plot(data.index, data['close'])
ax2.bar(data.index, data['vol'])
plt.show()

# 价涨量平
# 当价格在持续上涨时，股票的成交量却不再上涨而是保持持平的状态
# 量价背离释放出市场可能反转的信号
# 上涨行情中价格持续上涨，成交量变化不大，可能预示着价格即将到达顶部
# 也有可能是因为市场处于调整期，或者价格上涨过猛，买盘多而卖盘少，成交量呈现温和状态，失去反映市场动能的意义

# 价涨量缩
# 市场横盘调整完有可能会出现价涨量缩的情形
# 一些投资者被洗盘出局，市场参与者减少。洗盘结束初期市场行情看好，价格上涨，但是获利的卖盘较少

# 价平量增
# 出现在下跌行情的底部可能反转的情形中
# 在下跌行情中，价格不再下跌而是持平，但是成交量增大，说明多方力量可能进行了低位布局
# 预测未来行情可能出现向上走势，在低位进场推动成交量上涨
# 高位滞涨，价格处在高位时，价格不再上涨，而成交量却在增加，股票市场可能在更换“庄家”

# 价平量缩
# 一般出现在新一轮的上涨行情初期，价格保持稳定而成交量在减少
# 当市场进行调整洗盘时，可能会出现

# 价跌量增
# 一般出现在市场高价位下跌行情的初期，价格下跌表明投资者不看好市场 卖方力量较大，投资者大量卖出股票
# 另一种可能是，在市场下跌末期市场中做多力量慢慢增强时，成交量会增加，但是多空力量的较量还不至于抬高股价，价格依旧下跌

# 价跌量平
# 在下跌行情中，价跌量平释放出趋势回稳的信号，但是还没有办法预测后市的价格走势
# 如果价跌量平跟随在价平量平后面，则表示市场已经开始下跌行情

# 价跌量缩
# 当市场处于盘整阶段，市场价格下跌，一部分投资者逃离市场
# 另外，在单边下跌行情阶段，价跌量跌形态体现出市场即将出现止跌的情形
# 另外，在单边下跌行情阶段，买方力量弱，市场中接盘了小，也会出现

###############################################################################

# 成交量与均线思想结合制定交易策略
# 1. 获取成交量数据，计算成交量的5日移动平均和10日移动平均和成交量均值VolSMA = (5日VolSMA + 10日VolSMA) / 2
# 2. 获取价格数据，计算价格的5日简单移动平均和20日简单移动平均
# 3. 当成交量 > VolSMA时，释放买入信号，当成交量 <= VolSMA时，释放出卖出信号
# 4. 当5日SMA上穿20日SMA时，释放买入信号，当5日SMA下穿20日SMA时，释放卖出信号
# 5. 合并交易信号，当成交量与价格的SMA都释放出买入信号时，才进行买入操作，卖出同

volume = data.vol
VolSMA5 = pd.Series(volume).rolling(window = 5).mean()
VolSMA10 = pd.Series(volume).rolling(window = 10).mean()
VolSMA = ((VolSMA5 + VolSMA10) / 2).dropna()

VolSignal = (volume[-len(VolSMA): ] > VolSMA) * 1
# -len(VolSMA)为-235，volume[-235: ]为了与VolSMA日期相匹配
# *1将True变为1，False变为0
VolSignal[VolSignal == 0] = -1

close = data.close
PriceSMA5=pd.Series(close).rolling(window = 5).mean().dropna()
PriceSMA20=pd.Series(close).rolling(window = 20).mean().dropna()

def upbreak(Line, RefLine): # 短SMA、长SMA
    signal = np.all([Line > RefLine, Line.shift(1) < RefLine.shift(1)], axis = 0)
    return(pd.Series(signal[1:], index = Line.index[1:]))
def downbreak(Line,RefLine):
    signal = np.all([Line < RefLine, Line.shift(1) > RefLine.shift(1)], axis = 0)
    return(pd.Series(signal[1:], index = Line.index[1:]))

UpSMA = upbreak(PriceSMA5[-len(PriceSMA20):], PriceSMA20) * 1
DownSMA = downbreak(PriceSMA5[-len(PriceSMA20): ], PriceSMA20) * 1
SMAsignal = UpSMA - DownSMA # 为了将DownSMA的+1变为-1
VolSignal = VolSignal[-len(SMAsignal): ]
signal = VolSignal + SMAsignal

trade = signal.replace([2,-2,1,-1,0],[1,-1,0,0,0])
# 合并交易信号后，如果两个信号都显示买入，相加就会变成2，这时要替换为1
# 如果相加等于1，说明有一个信号没让买入，不满足两个信号都为1的条件，所以替换为0
# 如果两个信号都显示卖出，相加就会等于-2，所以改为-1
# 如果相加等于-1，说明有一个信号没让卖出，不满足两个信号都为-1的条件，所以替换为0
trade = trade.shift(1)[1:] # 不要反复执行这行代码

ret = data.pct_chg['2019-06-04':] # 匹配序列开始日期
ret.name = 'stockRet'
tradeRet = trade * ret
tradeRet.name = 'tradeRet'
winRate = len(tradeRet[tradeRet > 0]) / len(tradeRet[tradeRet != 0])
winRate

# 绘制绩效表现图
cumstock = (1 + ret).cumprod()
cumtrading = np.cumprod(1+ tradeRet) - 1
plt.plot(cumstock, label = 'stockRet')
plt.plot(cumtrading, label = 'tradeRet')
plt.legend()
plt.show()
