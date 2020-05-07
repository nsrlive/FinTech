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
volume = data.vol
high = data.high
low = data.low

# OBV能量潮
# 将成交量指标化，制成趋势线，配合股价趋势线，通过价格的变动及成交量的增减关系来推测股价变动趋势
# 累积OBV、移动OBV、修正型OBV净额

# 累积OBV
# 将股价上涨时的成交量进行正累加，股价下跌时的成交量进行负累加
# OBVn = +-Vn + OBVn-1
# OBVn为本期OBV值，OBVn-1为前一期OBV值，Vn时当日成交量
# 本期股价上涨时，Vn符号为+，下跌时Vn为-
clo = np.array(close)
vol = np.array(volume)
# 为了判断计算中成交量前的正负号，我们先使用diff函数计算收盘价的变化量。
change = np.diff(close)
# 使用sign函数返回数组中每个元素的正负符号，为负时返回-1，为正时返回1，为0返回0
signs = np.sign(change)
# OBV值的计算依赖于前一日的收盘价
vols = np.concatenate(([vol[0]], vol[1:] * signs )) # np 拼接
# 求OBV值 := 计算累加之和
obv = np.cumsum(vols)
obvdata = pd.DataFrame(columns=['OBV'], data = obv, index = close.index)


# 移动型OBV
# 由累积OBV进行简单移动平均，一般选择0日或者12日时间为跨度
# smOBVt = (OBVt + OBVt-1 + ... + OBVt-8) / 9
smOBV = pd.DataFrame(obvdata).rolling(window = 9).mean()

# 修正型OBV
# 在计算累积成交量时无论股价变化幅度与趋势如何，档期的成交量的权重是一样的
# 为了将股价这些因素考虑进去，人们一般用多空比率净额来替代单纯的成交量
# 多空比率净额 = V * [(close - low) - (high - low)] / (high - low)
# 收盘价与最低价的差值表示多头力量的强度，最高价与收盘价的差值表示空头力量的强度
# 两者之差表示多头的净力量幅度，Hn-Ln最高价与最低价的差值
# 分式表示多头相对力量对于成交量的空闲程度
AdjOBV = ((close - low)-(high - close)) / (low) * volume
AdjOBV.name = 'AdjOBV'

# 绘制能量潮
ax1 = plt.subplot2grid((11,11),(0,0), rowspan = 3, colspan = 10)
ax2 = plt.subplot2grid((11,11),(4,0), rowspan = 3, colspan = 10, sharex = ax1)
ax3 = plt.subplot2grid((11,11),(8,0), rowspan = 3, colspan = 10, sharex = ax1)
ax1.plot(close.index, close)
ax2.plot(obvdata)
ax2.plot(smOBV)
ax3.plot(AdjOBV)
plt.show()

# 当使用OBV指标时，单期的OBV值对于股价分析来说并没有太大愈义
# 根据OBV指标的原理，股价的趋势是通过成交量的多少来体现的。但是，多与少是通过比较得到的，不是一个 OBV 值所能体现的
# 因此，我们而要将OBV值与过去的OBV值进行比较，才能对成交量的多少做出判断
# 对于OBV值之间的比较，可以通过绘制OBV曲线来进行
# 将每一日计算所得的 OBV值连接起来得到OBV曲线
# 通过观察 OBV曲线与股价的趋势，可以对未来的价格变动做出预测

# OBV曲线上升股价下降：表明在股价下跌时成交量却在上升，暗示有越来越多的投资者在承接。在这种情况下，逐渐提高的成交量表明投资者对该股的信心不断增强，释放出买入的信号
# OBV曲线下降而股价上涨：这种情况与第一种情况刚好相反。虽然股价仍在上升，但是成交量却在缩小，表明投资者对其逐渐丧失信心，不愿接盘。因此，该股很可能己接近顶点，即将下跌
# OBV曲线稳步上升，同时股价上涨：这种情况表明行情稳步向上，股价仍有上涨空间，中长期走势良好
# OBV曲线缓慢下降，同时股价下跌：这种情况则表明行情不佳，股价仍会继续卜跌，投资者应卖出股票或暂时观望
# 两种极端情况： OBV曲线快速上升的现象表明买盘迅速涌入，持续性不强，股价在短暂的拉升后可能会迅速下跌： OBV 曲线快速下降的现象则表明卖盘迅速涌入，但是随后仍有可能会有一段较长的下跌，投资者应以观望为主