import tushare as ts
ts.set_token('你的token')
pro = ts.pro_api()

import pandas as pd
import numpy as np
import matplotlib; matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = 'SimHei'  #让matplotlib支持微软雅黑中文
plt.rcParams['axes.unicode_minus'] = False  #解决负号无法正常使用的问题

data = pro.daily(ts_code='002673.SZ', start_date='20190501', end_date='20200430')
data = data.sort_values('trade_date', ascending = True)
data = data.set_index('trade_date')
data.index = pd.to_datetime(data.index)
close = data.close
high = data.high
low = data.low

# 唐奇安通道
# 寻找一定时间内出现的最高价和最低价，将最高价和最低价分布作为通道的上下轨道
# 当价格突破通道的上轨道时，说明股价运动较为强势，释放买入信号
# 当价格突破通道的下轨道时，空头市场较为强势，市场下跌趋势较为明显，释放卖出信号
# 假如采用20日
# 通道上界由20日蜡烛图的最高点构成：通道上界 = 过去20日内的最高价
# 通道下界由20日蜡烛图的最低点构成：通道下界 = 过去20日内的最低价
# 中轨道= (通道上界 + 通道下界)/2

# 设定上中下通道线的初始值
upbound = pd.Series(0.0, index = close.index)
downbound = pd.Series(0.0, index = close.index)
midbound = pd.Series(0.0, index = close.index)

# 求三条通道
for i in range (20, len(close)):
        upbound[i] = max(high[(i - 20) : i])
        downbound[i] = min(low[(i - 20) : i])
        midbound[i] = 0.5 * (upbound[i] + downbound[i])
upbound = upbound[20:]
downbound = downbound[20:]
midbound = midbound[20:]

plt.plot(close, label = 'close')
plt.plot(upbound, label = 'upbound', color = 'b')
plt.plot(downbound, label = 'downbound', color = 'b')
plt.plot(midbound, label = 'midbound', color = 'r')
plt.title('收盘价与唐奇安通道')
plt.legend()
plt.show()

# 收盘价基本在唐奇安上下通道之内运动，只有个别日期突破上下通道
# 收盘价穿过中轨道线次数较多
# 从上下通道的间距情况可以大致看出股价的震荡情况

# 在K线图中绘制唐奇安通道上下通道线
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mdates

ax1 = plt.subplot()
ax1.xaxis_date()
df_ohlc = data[['open','high','low','close']]
df_ohlc = df_ohlc.reset_index()
df_ohlc['trade_date'] = df_ohlc['trade_date'].map(mdates.date2num)
candlestick_ohlc(ax1, df_ohlc.values, width = 1, colordown = 'green', colorup = 'red', alpha = 0.75)
plt.plot(upbound, label = 'upbound', color = 'b')
plt.plot(downbound, label = 'downbound', color = 'b')
plt.legend()
plt.title('历史股价K线图与唐奇安通道')
plt.show()

# 捕捉唐奇安通道突破
# 当价格线走强而突破前n期的最高价时做多；下跌而低于前n期的最低价时最空；
def upbreak(price, bound):
    n = min(len(price), len(bound))
    price = price[-n:] # 从倒数第n个位置开始往后取数据
    bound = bound[-n:]
    signal = pd.Series(0, index = price.index)
    for i in range(1, len(price)):
        if all([price[i] > bound[i], price[i - 1] < bound[i - 1]]):
            signal[i] = 1
    return(signal)

def downbreak(price, bound):
    n = min(len(price), len(bound))
    price = price[-n:]
    bound = bound[-n:]
    signal = pd.Series(0, index = price.index)
    for i in range(1, len(price)):
        if all([price[i] < bound[i], price[i - 1] > bound[i - 1]]):
            signal[i] = 1
    return(signal)

UpBreak = upbreak(close[upbound.index[0]:], upbound) # 设置开始计算的时间并按照时间提取收盘价
DownBreak = downbreak(close[downbound.index[0]:], downbound)
# 合并信号，上穿为1，下穿为-1，所以这里用减号而不是加号
BreakSig = UpBreak - DownBreak

# 计算获胜率
tradeSig = BreakSig.shift(1)
ret=close / close.shift(1) - 1
tradeRet = (ret * tradeSig).dropna()
tradeRet[tradeRet == -0] = 0
winRate=len(tradeRet[tradeRet > 0]) / len(tradeRet[tradeRet != 0])
winRate

###############################################################################

# 布林带通道
# 中轨道线为股价的平均线
# 上通道为股价的均线加上一定倍数的标准差，下通道为股价的均线减去一定倍数的标准差
# 布林带通道的趋势主要由中轨道平均线决定，带宽由股价的标准差决定，而标准差刻画了股价波动范围的大小
# 一般天数取20，倍数取2

def bbands(price, period = 20, times = 2):
    upBBand = pd.Series(0.0, index = price.index)
    midBBand = pd.Series(0.0, index = price.index)
    downBBand = pd.Series(0.0, index = price.index)
    sigma = pd.Series(0.0, index = price.index)
    for i in range(period - 1, len(price)):
        midBBand[i] = np.nanmean(price[i - (period - 1) : (i + 1)])
        sigma[i] = np.nanstd(price[i - (period - 1) : (i + 1)])
        upBBand[i] = midBBand[i] + times * sigma[i]
        downBBand[i] = midBBand[i] - times * sigma[i]
    BBands = pd.DataFrame({'upBBand':upBBand[(period-1):], 'midBBand':midBBand[(period-1):], 'downBBand':downBBand[(period-1):], 'sigma':sigma[(period-1):]})
    return(BBands)

stockBBands = bbands(close, 20, 2)

stockupBBand = stockBBands['upBBand']
stockdownBBand = stockBBands['downBBand']
stockmidBBand = stockBBands['midBBand']

# 绘制收盘价与布林带通道
plt.plot(close, label = 'close')
plt.plot(stockupBBand, label = 'upbound', color = 'b')
plt.plot(stockdownBBand, label = 'downbound', color = 'b')
plt.plot(stockmidBBand, label = 'midbound', color = 'r')
plt.title('收盘价与布林带通道')
plt.legend()
plt.show()

# 在K线图中绘制布林带通道上下通道线
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mdates

ax1 = plt.subplot()
ax1.xaxis_date()
df_ohlc = data[['open','high','low','close']]
df_ohlc = df_ohlc.reset_index()
df_ohlc['trade_date'] = df_ohlc['trade_date'].map(mdates.date2num)
candlestick_ohlc(ax1, df_ohlc.values, width = 1, colordown = 'green', colorup = 'red', alpha = 0.75)
plt.plot(stockupBBand, label = 'upbound', color = 'b')
plt.plot(stockdownBBand, label = 'downbound', color = 'b')
plt.legend()
plt.title('历史股价K线图与布林带通道')
plt.show()

## 布林带通道与市场风险
## 大部分情况下股票价格应该在布林带通道内部运动
## 当价格线超出布林带通道的上下线时，可以认为价格线有偏离，未来价格很有可能回落到布林带通道内部
## 定义布林带通道风险计算函数
#def CalBollRisk(tsPrice,multiplier):
#    k=len(multiplier)
#    overUp=[]
#    belowDown=[]
#    BollRisk=[]
#    for i in range(k):
#        BBands=bbands(tsPrice,20,multiplier[i])
#        a=0
#        b=0
#        for j in range(len(BBands)):
#            tsPrice=tsPrice[-(len(BBands)):]
#            if tsPrice[j]>BBands.upBBand[j]:
#                a+=1
#            elif tsPrice[j]<BBands.downBBand[j]:
#                b+=1
#        overUp.append(a)
#        belowDown.append(b)
#        BollRisk.append(100*(a+b)/len(tsPrice))
#    return(BollRisk)
#
#multiplier = [1, 1.65, 1.96, 2, 2.58] # 标准差的倍数向量
#price = close['2019-12-01':'2020-03-31'] # 指定计算的时间段
#CalBollRisk(price, multiplier)

# 布林带通道突破策略的制定
# 当股价向上突破布林带上通道时，股票可能产生了异常上涨，此时宜做空
# 当股价向下突破布林带下通道时，股票可能产生了异常下跌，此时宜做多

stockBBands = bbands(close, 20, 2)
upbreakBB1 = upbreak(close,stockBBands.upBBand)
downbreakBB1 = downbreak(close,stockBBands.downBBand)

upBBSig1 = -upbreakBB1.shift(2) # 注意负号
downBBSig1 = downbreakBB1.shift(2)

tradSignal1 = upBBSig1 + downBBSig1
tradSignal1[tradSignal1 == -0] = 0

def perform(price, tsTradSig):
    ret = price/price.shift(1) - 1
    tradRet = (ret * tsTradSig).dropna()
    ret = ret[-len(tradRet):] # 从倒数第len(tradRet)个位置开始往后取数据
    winRate = [len(ret[ret>0]) / len(ret[ret != 0]), len(tradRet[tradRet > 0]) / len(tradRet[tradRet != 0])]
    meanWin = [np.mean(ret[ret > 0]), np.mean(tradRet[tradRet > 0])]
    meanLoss = [np.mean(ret[ret < 0]), np.mean(tradRet[tradRet < 0])]
    Performance=pd.DataFrame({'winRate':winRate, 'meanWin':meanWin, 'meanLoss':meanLoss})
    Performance.index=['Stock','Trade']
    return(Performance)

Performance1= perform(close, tradSignal1)
Performance1
# 第一行表示股票本身的表现，第二行表示布林带交易策略的表现

# 特殊布林带通道突破策略
# 当价格由布林带通道线的上方穿到布林带通道内部时，说明股价从异常上升行情将要回到正常波动行情，股票短期有下跌趋势
# 当价格由布林带通道线的下方穿到布林带通道内部时，说明股价从异常下跌行情将要回到正常波动行情，股票短期有上升趋势

upbreakBB2 = upbreak(close,stockBBands.downBBand) # 注意这里用了downBBand，与普通策略相反
downbreakBB2 = downbreak(close,stockBBands.upBBand) # 同上，从线外回到内部

upBBSig2 = upbreakBB2.shift(2)
downBBSig2 = -downbreakBB2.shift(2) # 注意负号

tradSignal2 = upBBSig2 + downBBSig2
tradSignal2[tradSignal2== -0] = 0

Performance2= perform(close, tradSignal2)
Performance2

###############################################################################

#%b指标
#刻画收盘价曲线在布林带通道中的位置
# b = (收盘价 - 布林带下轨道值) / (布林带上轨道值 - 布林带下轨道值)
# 当b取值在0-1之间，收盘价在布林带内部波动
# 当b取值为0.5，收盘价在布林带中间位置
# 当b取值大于1，收盘价在布林带上方
# 当b取值小于1，收盘价在布林带下方
bounds = bbands(close, 20, 2)
bvalue = (close - bounds.downBBand)/(bounds.upBBand - bounds.downBBand)
bvalue.plot(title = '%b指标')

# 多空布林线 (暂时不确定对错)
# 中轨道BBI = (3日SMA + 6日SMA +12日SMA + 24日SMA) / 4
# 上轨道UPR = BBI + M * BBI的N日估算标准差
# 下轨道DWN = BBI - M * BBI的N日估算标准差
# M一般取值为6，N一般取值为11
        
SMA3 = data['close'].rolling(window = 3).mean()
SMA6 = data['close'].rolling(window = 6).mean()
SMA12 = data['close'].rolling(window = 12).mean()
SMA24 = data['close'].rolling(window = 24).mean()

midbound = (SMA3 + SMA6 + SMA12 +SMA24) / 4
std = midbound.rolling(window = 11).std()

upbound = midbound + 6 * std
lowbound = midbound - 6 * std
bounds = pd.concat([upbound,lowbound,midbound],1)
bounds.columns=['upbound','lowbound','midbound']
bounds.dropna().plot()