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

# 买方和卖方力量的消长会影响股票的价格。如果买入力量大于卖出力量，则股票的价格会上涨；
# 如果股票的卖出力量大于买入力量，则股票的价格会下跌。
# RSI1 = 100 - 100/(1+RS)
# RSI2 = 100 * RS/(1+RS)
# RSI3 = UP / DOWN
# RSI4 = 100 * UP / (UP + DOWN)
# RSI表示相对强弱指标值，t表示参考数据的期数，
# UP表示t期内股价上涨幅度的平均值，DOWN表示t期内股价下跌幅度的平均值，RS = UP / DOWN
# RSI的取值范围为0~100
# 当RSI取值接近于0时， 由RSI = 100 * UP / (UP + DOWN)可得 UP << DOWN
# 当RSI取值接近于100时， 由RSI = 100 * UP / (UP + DOWN)可得 UP >> DOWN
# 当RSI取值为50时，由RS = UP /DOWN得 UP = DOWN
# RSI取值大于50越多，上涨力量超过下跌力量越多。反之，下跌力量超过上涨力量越多

price_change = close - close.shift(1) # 第二天相对于前一天价格的变化
price_change = price_change.dropna()

dataindex = price_change.index
upprice = pd.Series(0, index = dataindex)
upprice[price_change > 0] = price_change[price_change > 0] # upprice[price_change>0]是为了保持行对应
downprice = pd.Series(0, index = dataindex)
downprice[price_change < 0] = -price_change[price_change < 0] # 注意负号

# 合并index相同的Series用concat
rsidata = pd.concat([close, price_change, upprice, downprice], axis = 1)
rsidata = rsidata.dropna() # 只有close有第一天的数据，其它的是NaN
rsidata.columns = ['close', 'price_change', 'upprice', 'downprice']

# 计算收盘价6日得上涨均值和下跌均值（其实就是移动平均）
rise = []
decline = []
for i in range(6, len(upprice) + 1):
    rise.append(np.mean(upprice.values[(i - 6) : i], dtype = np.float32))
    decline.append(np.mean(downprice.values[(i - 6) : i], dtype = np.float32))
# 计算6日RSI值
rsi6index = dataindex[5:]
rsi6 = [100 * rise[i] / (rise[i] + decline[i]) for i in range(0, len(rise))]
rsi6 = pd.Series(rsi6, index = rsi6index)
rsi6.describe()

# 如果不能理解上面的for循环，可以思考如何使用rolling函数实现相同结果
#rise_mean = pd.DataFrame(upprice)
#rise_mean = rise_mean.rolling(window=6).mean()
#rise_mean = rise_mean.dropna()
#decline_mean = pd.DataFrame(downprice)
#decline_mean = decline_mean.rolling(window=6).mean()
#decline_mean = decline_mean.dropna()
#
#rsi6index_ = dataindex[5:]
#rsi6_ = [100 * rise_mean.values[i] / (rise_mean.values[i] + decline_mean.values[i]) for i in range(0, len(rise_mean))]
#rsi6_ = pd.Series(rsi6, index = rsi6index_)
######

rise_series = pd.Series(rise, index = rsi6index)
decline_series = pd.Series(decline, index = rsi6index)

plt.subplot(411)
plt.plot(close)
plt.xlabel('date')
plt.ylabel('close')
plt.title('RSI分析')

plt.subplot(412)
plt.plot(rise_series)
plt.xlabel('date')
plt.ylabel('rise_mean')

plt.subplot(413)
plt.plot(decline_series)
plt.xlabel('date')
plt.ylabel('decline_mean')

plt.subplot(414)
plt.plot(rsi6)
plt.xlabel('date')
plt.ylabel('RSI')

# 短期RSI对于价格的变化反应较为灵敏，RSI波动较大；长期RSI对于价格的变化反应较为迟钝，RSI波动较小

###############################################################################

# 为便于计算，定义RSI函数，使用函数前先熟练不使用函数时的计算步骤

def rsi(price,period = 6):
    import pandas as pd
    clprcChange = price - price.shift(1)
    clprcChange = clprcChange.dropna()
    indexprc = clprcChange.index
    upPrc = pd.Series(0, index = indexprc)
    upPrc[clprcChange > 0] = clprcChange[clprcChange > 0]
    downPrc = pd.Series(0,index = indexprc)
    downPrc[clprcChange < 0] = -clprcChange[clprcChange < 0]
    rsidata = pd.concat([price, clprcChange, upPrc, downPrc], axis = 1)
    rsidata.columns=['price', 'PrcChange', 'upPrc', 'downPrc']
    rsidata = rsidata.dropna();
    
    SMUP=[]
    SMDOWN=[]
    for i in range(period, len(upPrc) + 1):
        SMUP.append(np.mean(upPrc.values[(i - period) : i], dtype = np.float32))
        SMDOWN.append(np.mean(downPrc.values[(i - period) : i], dtype = np.float32))
        rsi = [100 * SMUP[i] / (SMUP[i] + SMDOWN[i]) for i in range(0, len(SMUP))]
    
#    rise_mean = pd.DataFrame(upPrc)
#    rise_mean = rise_mean.rolling(window=period).mean()
#    rise_mean = rise_mean.dropna()
#    decline_mean = pd.DataFrame(downPrc)
#    decline_mean = decline_mean.rolling(window=period).mean()
#    decline_mean = decline_mean.dropna()
#
#    rsiindex_ = indexprc[(period-1):]
#    rsi = [100 * rise_mean.values[i] / (rise_mean.values[i] + decline_mean.values[i]) for i in range(0, len(rise_mean))]
#    rsi = pd.Series(rsi, index = rsiindex_)
        
    indexRsi=indexprc[(period-1):]
    rsi=pd.Series(rsi,index=indexRsi)
    return(rsi)

# 示例
rsi12 = rsi(close, 12)
rsi12.tail()

###############################################################################
# 采用如下公式计算RSI = 100 - 100 / (1 + RS)
def RSI(array_list, periods = 6):
    length = len(array_list)
    rsies = [np.nan] * length # 生成和价格序列长度相同，但值全为空的列表
    if length <= periods: # 时间序列的长度要大于RSI计算的天数
        return rsies
    up_avg = 0 # 初始化均值
    down_avg = 0 # 初始化均值

    first_t = array_list[:periods + 1] # 选中第0到第七（第一个交易日到第七个交易日）
    for i in range(1, len(first_t)):
        if first_t[i] >= first_t[i - 1]: # 如果当天价格大于前一天的价格
            up_avg = up_avg + (first_t[i] - first_t[i - 1]) # 上涨的部分
        else:
            down_avg = down_avg + (first_t[i - 1] - first_t[i]) # 下跌的部分
    up_avg = up_avg / periods
    down_avg = down_avg / periods
    rs = up_avg / down_avg
    rsies[periods] = 100 - 100 / (1 + rs)

    for j in range(periods + 1, length): # 从7到最后（从第八个交易日）
        up = 0
        down = 0
        if array_list[j] >= array_list[j - 1]: 
            up = array_list[j] - array_list[j - 1]
            down = 0
        else:
            up = 0
            down = array_list[j - 1] - array_list[j]
        # 类似移动平均的计算公式
        up_avg = (up_avg * (periods - 1) + up) / periods
        down_avg = (down_avg * (periods - 1) + down) / periods
        rs = up_avg / down_avg
        rsies[j] = 100 - 100 / (1 + rs)
    return rsies

rsi6 = RSI(close, 6)
rsi6 = pd.Series(rsi6, index = close.index)

###############################################################################

# 较常用的取值：RSI取80为股票超买的临界点，RSI取20为超卖的临界点，RSI取50为中心线
# 当RSI大于80时，股票出现超买信号。股票买入力量过大，买入力量在未来可能会减小，所以股票未来价格可能会下跌，此时卖出股票，未来下跌后再买入股票
# 当RSI小于20时，股票出现超卖信号。股票卖出力量多大，卖出力量在未来可能变正常，所以股票未来价格可能会上涨，此时买入股票，未来上涨后再卖出股票
# 70和30可能也是不错的取值

# 黄金交叉：当短期RSI线向上穿过长期RSI线时，股票近期买入的力量较强，价格上涨的力量很大，释放出一个较强的买入信号
# 死亡交叉：当短期RSI线向下跌破长期RSI线时，股票近期卖出的力量较强，价格下跌的力量很大，释放出一个较强的卖出信号

# 实例
# 当RSI6 > 80 或者RSI6向下穿过RSI24时，为卖出信号
# 当RSI6 < 20 或者RSI6向上穿过RSI24时，为买入信号

rsi6 = rsi(close, 6)
rsi24 = rsi(close, 24)

# 交易信号1：RSI6捕捉买卖点
Sig1=[]
for i in rsi6:
    if i>80:
        Sig1.append(-1)
    elif i<20:
        Sig1.append(1)
    else:
        Sig1.append(0)

date1 = rsi6.index
Signal1 = pd.Series(Sig1,index=date1)
#Signal1[Signal1==1]
#Signal1[Signal1==-1]
# Signal1为1表示RSI6低于超卖线，预测未来价格要回升，释放买入信号
# Signal1为-1表示RSI6高于超买线，预测价格有回落趋势，释放卖出信号

# 交易信号2： 黄金交叉与死亡交叉
Signal2 = pd.Series(0,index = rsi24.index)
lagrsi6 = rsi6.shift(1)
lagrsi24 = rsi24.shift(1)
for i in rsi24.index:
    if (rsi6[i] > rsi24[i]) & (lagrsi6[i] < lagrsi24[i]):
        Signal2[i] = 1
    elif (rsi6[i] < rsi24[i]) & (lagrsi6[i] > lagrsi24[i]):
        Signal2[i] = -1
# Signal2为1表示RSI6上穿RSI24，价格可能有上升的趋势，释放买入信号
# Signal2为-1表示RSI6跌破RSI24，价格可能有下跌的趋势，释放出卖出信号

# 合并交易信号（即结合两种交易信号），确定最终买卖信号
signal = Signal1 + Signal2
signal[signal >= 1] = 1
signal[signal <= -1] = -1
signal = signal.dropna()

###########################################
# RSI交易策略执行及回测
# 当天交易后，算第二天的回报
tradingsig = signal.shift(1)
return_ = close.pct_change()
return_ = return_[tradingsig.index] # 匹配时间段

# 求买入交易收益率
buy = tradingsig[tradingsig == 1]
buyreturn = return_[tradingsig == 1] * buy

# 求卖出交易收益率
sell = tradingsig[tradingsig == -1]
sellreturn = return_[tradingsig == -1] * sell

# 买卖交易合并的收益率
tradingreturn = return_ * tradingsig

# 绘制三种交易收益率的时序图
plt.subplot(211)
plt.plot(buyreturn, label = 'buyreturn')
plt.plot(sellreturn, label = 'sellreturn')
plt.title('RSI交易指标策略')
plt.ylabel('strategyreturn')
plt.legend()
plt.subplot(212)
plt.plot(return_)
plt.ylabel('stockreturn')

# 计算信号点预测准确率情况，求预测正确时的平均收益率与预测失败时的平均收益率
def strat(tradingsig, return_):
    indexDate = tradingsig.index
    return_ = return_[indexDate]
    tradingreturn = return_ * tradingsig
    tradingreturn[tradingreturn == (-0)] = 0
    winRate = len(tradingreturn[tradingreturn > 0]) / len(tradingreturn[tradingreturn != 0])
    meanWin = sum(tradingreturn[tradingreturn > 0]) / len(tradingreturn[tradingreturn > 0])
    meanLoss = sum(tradingreturn[tradingreturn < 0]) / len(tradingreturn[tradingreturn < 0])
    perform = {'winRate':winRate,'meanWin':meanWin,'meanLoss': meanLoss}
    return(perform)

# 预测获胜率、平均获胜收益率与平均损失收益率
buyonly = strat(buy, return_)
sellonly = strat(sell, return_)
trading = strat(tradingsig, return_)

test = pd.DataFrame({'buyonly':buyonly, 'sellonly':sellonly, 'trading':trading})
test

# 比较RSI策略的累积收益率
cumstock = np.cumprod(1 + return_) - 1
cumtrading = np.cumprod(1+ tradingreturn) - 1

plt.subplot(211)
plt.plot(cumstock)
plt.ylabel('cumstock')
plt.title('股票本身累积收益率')
plt.subplot(212)
plt.plot(cumtrading)
plt.ylabel('cumtrading')
plt.title('RSI策略累积收益率')

# 当策略不理想时，可以调整制定策略时所用的参数
# 之前设置的RSI指标释放出的买卖点信号1天后执行买卖操作
# 观察买卖点信号释出后，如果股票价格没有及时上涨或者下跌，就要修正买卖信号执行点
# 假设3天以后再进行买卖操作

tradingsig2 = signal.shift(3)
return_2 = return_[tradingsig2.index]
buy2 = tradingsig2[tradingsig2 == 1]
sell2 = tradingsig2[tradingsig2 == -1]
buyreturn2 = return_2[tradingsig2 == 1] * buy2
sellreturn2 = return_2[tradingsig2 == -1] * sell2
tradingreturn2 = return_2 * tradingsig2
buyonly2 = strat(buy2, return_2)
sellonly2 = strat(sell2, return_2)
trading2 = strat(tradingsig2, return_2)
test2 = pd.DataFrame({'buyonly2':buyonly2, 'sellonly2':sellonly2, 'trading2':trading2})
test2

cumstock2 = np.cumprod(1 + return_2) - 1
cumtrading2 = np.cumprod(1+ tradingreturn2) - 1

plt.subplot(211)
plt.plot(cumstock2)
plt.ylabel('cumstock2')
plt.title('股票本身累积收益率')
plt.subplot(212)
plt.plot(cumtrading2)
plt.ylabel('cumtrading2')
plt.title('RSI策略累积收益率')

# 修改策略后效果更差但仅为举例
# 当市场处于疯狂牛市时，RSI突破超买线所释放出的卖出信号没有太大意义