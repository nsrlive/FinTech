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
close = data.close

# 简单移动平均
sma5 = data['close'].rolling(window = 5).mean()

plt.plot(close[4:], label = 'close', color = 'b')
plt.plot(sma5[4:], label = 'sma5', color = 'r', linestyle = 'dashed')
plt.title('收盘价与简单移动平均线')
plt.legend()
plt.show()

# 要确定移动平均的期数，一般要从以下三个方面考虑
# 1.事件发展的周期性。比如研究每天平均气温变化趋势，则选用12期
# 2.对趋势平均性的要求。一般来说，期数越多，修匀效果越平均，表现出的趋势越清晰
# 3.对趋势反映近期变化敏感程度的要求。期数越多，滞后性越大，期数越小，对近期变化的反应就越敏感。因此关注长期趋势则选用期数较大，短期则期数较小

# 加权移动平均
# 昨天的价格比10天前的价格更能反映今天的股价，也就是说离当前时间越近的数据越有代表性
# 为了表示不同时期股价代表性的高低，可以先对股价赋予一定的权重，再求平均值
# WMA5 = w1p1 + w2p2 + w3p3 + w4p4 + w5p5，其中∑wi = 1
# 加权移动平均比简单移动平均对近期的变化更加敏感，尤其是在牛熊市转换的时候，加权移动平均的滞后性小于简单移动平均，但仍然存在滞后性

# pandas无法计算加权平均
# 定义权重
b = np.array([1, 2, 3, 4, 5])
w = b / sum(b)

wma5 = pd.Series(0.0, index = close.index)
for i in range(4, len(close)):
    wma5[i] = sum(w * close[(i - 4) : (i + 1)])

plt.plot(close[4:], label = 'close', color = 'b')
plt.plot(wma5[4:], label = 'wma5', color = 'r', linestyle = 'dashed')
plt.title('收盘价与加权移动平均线')
plt.legend()
plt.show()

# 定义加权移动平均函数
def wamcal(price, day):
    import pandas as pd
    import numpy as np
    b = np.arange(1, day + 1, 1)
    w = b / sum(b)
    k = len(w)
    wma = pd.Series(0.0, index = price.index)
    for i in range(k - 1, len(price)):
        wma[i] = sum(w * price[(i - k + 1) : (i + 1)])
    return(wma)

wma5_ = wamcal(close, 5)

# 指数加权平均
# 各数值的加权而随时间而指数式递减，越近期的数据加权越重，但较旧的数据也给予一定的加权
ewma5 = pd.DataFrame.ewm(close, span = 5).mean()

plt.plot(close, label = 'close', color = 'b')
plt.plot(ewma5, label = 'ewma5', color = 'r', linestyle = 'dashed')
plt.title('收盘价与指数加权移动平均线')
plt.legend()
plt.show()

# 当价格线突破短期均线时，价格短期处于向下趋势，反之。
# 如果价格先向下没有突破短期均线，则价格未来有上涨的趋势

# 简单移动平均线制定股票的买卖点
sma10 = data['close'].rolling(window = 10).mean()

smasignal = pd.Series(0, index = close.index)
for i in range(10, len(close)):
    if all([close[i] > sma10[i], close[i - 1] < sma10[i - 1]]):
        smasignal[i] = 1
    elif all ([close[i] < sma10[i], close[i - 1] > sma10[i - 1]]):
        smasignal[i] = -1
smatrading = smasignal.shift(1).dropna()

# 向上突破10日均线释放买入信号，向下反之，评价交易策略的好坏
smabuy = smasignal[smasignal == 1]
smasell = smasignal[smasignal == -1]
# 单期日收益率
close_return = close.pct_change()
sma_return = (close_return * smatrading).dropna()
# 累积收益率
# close_return比sma_return序列长度长了1，因此要匹配后再计算累积收益率
cumclose = np.cumprod(1 + close_return[sma_return.index[0]:]) - 1
cumtrading = np.cumprod(1 + sma_return) - 1
cumdata = pd.DataFrame({'cumclose':cumclose, 'cumtrading':cumtrading})

plt.plot(cumclose, label = 'cumclose', color = 'b')
plt.plot(cumtrading, label = 'cumtrading', color = 'r', linestyle = 'dashed')
plt.title('收盘价累积收益率与均线策略累积收益率')
plt.legend()
plt.show()

# 求买卖点预测准确率
sma_return[sma_return == (-0)] = 0
smawinrate = len(sma_return[sma_return>0]) / len(sma_return[sma_return != 0])
smawinrate
# 仅从本次选区的股票来看，准确率较低

# 双均线交叉捕捉买卖点
# 当短期均线从下向上穿过长期均线，释放买入信号
# 当短期均线从上向下穿过长期均线，释放卖出信号
sma5 = data['close'].rolling(window = 5).mean()
sma30 = data['close'].rolling(window = 30).mean()
# 寻找买卖交易信号并指定交易执行日期
double_signal = pd.Series(0, index = sma30.index)
for i in range(1, len(sma30)):
    if all([sma5[i] > sma30[i], sma5[i - 1] < sma30[i - 1]]):
        double_signal[i] = 1
    elif all([sma5[i] < sma30[i], sma5[i - 1] > sma30[i - 1]]):
        double_signal[i] = -1

double_signal_trading = double_signal.shift(1)
# 计算买入点的预测获胜率
long = pd.Series(0, index = sma30.index)
long[double_signal_trading == 1] = 1
close_return = close.pct_change()
long_return = (long * close_return).dropna()
winrate_long = len(long_return[long_return > 0]) / len(long_return[long_return != 0 ])
winrate_long
# 计算卖出点的预测获胜率
short = pd.Series(0, index = sma30.index)
short[double_signal_trading == -1] = -1
short_return = (short * close_return).dropna()
winrate_short = len(short_return[short_return > 0]) / len(short_return[short_return != 0 ])
winrate_short
# 计算所有买卖点的预测获胜率
tradingreturn = (double_signal_trading * close_return).dropna()
winrate_double = len(tradingreturn[tradingreturn > 0]) / len(tradingreturn[tradingreturn != 0])
winrate_double

cumlong = np.cumprod(1 + long_return) - 1
cumshort = np.cumprod(1 + short_return) - 1
cumtrading_double = np.cumprod(1 + tradingreturn) - 1 

plt.plot(cumlong, label = '买入点', color = 'b')
plt.plot(cumshort, label = '卖出点', color = 'r')
plt.plot(cumtrading_double, label = '所有买卖点', color = 'k')
plt.legend(loc = 'best')
plt.show()

###############################################################################

# 异同移动平均线(MACD)
# MACD由两线一柱组合起来，快速线为DIF，慢速线为DEA，柱状图为MACD
# 快速线DIF一般由12日指数加权移动平均值减去26日指数加权移动平均值得到
# 慢速线DEA是DIF的9日指数加权移动平均值
# 柱状图MACD由DIF和DEA做差得到
# MACD指标可以反映出股票近期价格走势的能量和变化强度
# 默认MACD参数为12、26和9，可以自己调整

# DIF = 12日指数移动平均值 - 26日指数移动平均值
# DEA = DIF的9日指数移动平均值
# MACD = 2 * (DIF - DEA)

DIF = pd.DataFrame.ewm(close, span = 12).mean() - pd.DataFrame.ewm(close, span = 26).mean()
DEA = pd.Series.ewm(DIF, span = 9).mean()
MACD = 2 * (DIF - DEA)

plt.subplot(211)
plt.plot(DIF, label = 'DIF', color = 'k')
plt.plot(DEA, label = 'DEA', color = 'b')
plt.legend(loc = 'best')
plt.subplot(212)
plt.bar(MACD.index, height = MACD, label = 'MACD')
plt.legend(loc = 'best')
plt.suptitle('DIF、DEA和MACD')
plt.show()

# 捕捉股票买卖点

# 当DIF和DEA都在零刻度线上方时，表明市场可能是多头行情；反之，当DIF和DEA都在零刻度下方时，表明市场可能处于空头行情
# DIF和DEA均为正，DIF向上突破DEA，买入信号
# DIF和DEA均为负，DIF向下跌破DEA，卖出信号

# 零上金叉为买入信号
# 零上双金叉：DIF和DEA都在零刻度线上方，在一段时间内，DIF先上穿DEA线，不久DIF下跌到DEA线的下方，然后DIF又上穿DEA线，此时，说明股票价格上升趋势较强，市场处于上涨行情中

# MACD中的柱形图表示DIF与DEA的差值。柱形图的高低表示DIF与DEA差值的大小。
# 柱形图在零刻度附近时，释放出买卖信号。柱形图在零刻度线上方，表示DIF大于DEA，市场走势较强；柱形图在零刻度下方，表示DIF小于DEA，市场走势较弱

macdsignal = pd.Series(0, index = DIF.index[1:])
for i in range(1, len(DIF)):
    if all([DIF[i] > DEA[i]>0.0, DIF[i - 1] < DEA[i - 1]]):
        macdsignal[i] = 1
    elif all([DIF[i] < DEA[i]<0.0, DIF[i - 1] > DEA[i - 1]]):
        macdsignal[i] = -1

macdtrading = macdsignal.shift(1)
# close_return 写过了
macd_return = (close_return * macdtrading).dropna()
macd_return[macd_return == -0] = 0
macdwinrate = len(macd_return[macd_return > 0]) / len(macd_return[macd_return != 0])
macdwinrate

# 多种均线指标综合运用模拟实测
allsignal = smasignal + double_signal + macdsignal
# 要求三个信号里至少有两个信号给出同一预测
for i in allsignal.index:
    if allsignal[i] > 1:
        allsignal[i] = 1
    elif allsignal[i] < -1:
        allsignal[i] = -1
    else:
        allsignal[i] = 0

allsignal[allsignal == 1]
allsignal[allsignal == -1]

allsigtrading = allsignal.shift(1).dropna()
allsig_return = (close_return * allsigtrading).dropna()
allsig_return[allsig_return == -0] = 0
allsigwinrate = len(allsig_return[allsig_return > 0]) / len(allsig_return[allsig_return != 0])
allsigwinrate
