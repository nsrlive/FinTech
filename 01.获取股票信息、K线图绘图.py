import tushare as ts
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style
style.use('ggplot')

df = ts.get_hist_data('000001')
#df.to_csv('000001.csv')

df_read_from_csv = pd.read_csv('000001.csv', parse_dates = True, index_col = 'date')
# parse_dates=True，读出来的时间是年月日时分秒

# 对每天的收盘价进行绘图
df_read_from_csv['close'].plot()
# 开盘价+收盘价绘图
df_read_from_csv[['close','open']].plot()

# 自定义简单移动平均线
# 简单移动平均线（SMA），顾名思义，就只是求得某个周期内的平均价格，不做任何技术上的处理。我们设置某个参数就往前数几个周期，求得平均值，第二天去掉最前面那个价格，加上新的价格再求一个平均值，依次求值下去，再把这些平均值用线连接起来就得到我们的简单移动平均线。比如，我们假设设置周期为5 。
#举例说明：某股连续十个交易日收盘价分别为：（单位：元）
#8.15、 8.07、 8.84、 8.10、 8.40、 9.10、 9.20、 9.10、 8.95、 8.70
#以五天短期均线为例：
#第五天起均值=（8.15+8.07+8.84+8.10+8.40）/5=8.31
#第六天起均值=（8.07+8.84+8.10+8.40+9.10) /5=8.50
#第七天起均值=（8.84+8.10+8.40+9.10+9.20）/5=8.73
#第八天起均值=（8.10+8.40+9.10+9.20+9.10）/5=8.78
#第九天起均值=（8.40+9.10+9.20+9.10+8.95）/5=8.95
#第十天起均值=（9.10+9.20+9.10+8.95+8.70）/5=9.01
#我们把这计算出来的几天平均价格连接起来，得到的就是一条简单移动平均线。
#自定义简单移动平均线，tushare默认给出5天10天和20天的移动平均，如果我们想要7天或者15天等，需要自定义

#将数据排序改为从老到新排序（tushare默认从新到老）
df_read_from_csv_reverse_order = df_read_from_csv.sort_index(ascending = True)
#使用rolling函数
df_read_from_csv_reverse_order['ma7'] = df_read_from_csv_reverse_order['close'].rolling(window = 7).mean()
#画图
df_read_from_csv_reverse_order.dropna(inplace=True)  #剔除空值
df_read_from_csv_reverse_order['ma7'].plot()

#draw subplot画子图
#subplot2grid将子图变为网格格式 9x10的表,位置(0,0)，sharex横轴一致
ax1 = plt.subplot2grid((9,10),(0,0), rowspan = 7, colspan = 5)
ax2 = plt.subplot2grid((9,10),(7,0), rowspan = 2, colspan = 10, sharex = ax1)
plt.show()

#为画布添加数据画图
ax1.plot(df_read_from_csv_reverse_order.index,
		df_read_from_csv_reverse_order['close'])
ax1.plot(df_read_from_csv_reverse_order.index,
		df_read_from_csv_reverse_order['ma7'])
ax2.bar(df_read_from_csv_reverse_order.index,
		df_read_from_csv_reverse_order['volume'])
plt.show()

# draw candlestick(画股票的K线图)
# 首先手动安装mplfinance,注意安装后要通过original导入旧模块，基本功能可用
from mplfinance.original_flavor import candlestick_ohlc
# matplotlib和pandas时间格式不一样，需要转换，先引入dates
import matplotlib.dates as mdates

ax1 = plt.subplot2grid((9,10),(0,0), rowspan = 7, colspan = 5)
ax2 = plt.subplot2grid((9,10),(7,0), rowspan = 2, colspan = 10, sharex = ax1)
ax1.xaxis_date()

# k线图需要四个元素，开盘价最高价最低价收盘价
df_ohlc = df_read_from_csv_reverse_order[['open','high','low','close']]
# 之前在pandas中我们将date作为了index，但是在matplotlib中date不能作为index，因此要重置index，此时index变为0,1,2,3....
df_ohlc = df_ohlc.reset_index()
df_ohlc['date'] = df_ohlc['date'].map(mdates.date2num)
# 将date变成了number，这样matplotlib才能继续运行，注意对于CSV文件如果parse_date=True没设置会导致这里报错

# colordown下跌时的颜色，colorup上涨时的颜色，alpha透明度，.values读取全部数据
candlestick_ohlc(ax1, df_ohlc.values, width = 1, colordown = 'green', colorup = 'red', alpha = 0.75)
# ax1表示画在哪个副图里，即画到ax1中
ax2.bar(df_read_from_csv_reverse_order.index,
		df_read_from_csv_reverse_order['volume'])
plt.show()

# 矩形实体的两端分别表示收盘价和开盘价
# 如果当天的收盘价大于开盘价，则矩形为红色实体，即红色矩形的上端表示收盘价，下端表示开盘价
# 如果当天的收盘价低于开盘价，则矩形为绿色实体，即绿色矩形的上端表示开盘价，下端表示收盘价
# 矩形实体的高度表示收盘价与开盘价大小的差值

# 影线分为上影线和下影线
# 上影线的上端点表示最高价，上影线的长度代表最高价与红色收盘价或者绿色开盘价的差值
# 下影线的下端点表示最低价，下影线的长度代表最低价与绿色收盘价或者红色开盘价的差值

# 十字星：矩形实体较扁（开盘价与收盘价差别较小），与影线结合后像“十”。另外，一般来说，十字星的上下影线长度相似。
# 当天开市以后，买方市场和卖方市场试图均衡力量，尽管价格在一天中上下波动，最终由于买卖双方市场的较量，闭市后收盘价和开盘价很接近

# 锤子线/上吊线：下影线很长，上影线没有或很短，开盘价和收盘价价位很接近，看上去就象锤子形状
# 在锤子线之前，必定先有一段下降趋势（哪怕是较小规模的下降趋势），这样锤子线才能够逆转这个趋势
# 上吊线属于顶部反转形态，必须出现在一段上升趋势之后
# 锤子线和上吊线的下影线的长度至少达到实体高度的2倍

# 倒锤子线：上影线很长（实体2倍），下影线没有或很短，开盘价和收盘价价位很接近，看上去就象锤子形状
# 出现在下跌途中，见底信号，后市看涨。实体与上影线比例越悬殊，信号越有参考价值
# 如倒锤子与早晨之星同时出现，见底信号就更加可靠
# 值得注意的是，如果倒锤子出现在上涨后相对高的位置，则属于看空信号，称之为“射击之星”


