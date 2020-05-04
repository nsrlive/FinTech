import tushare as ts
ts.set_token('你的token')
pro = ts.pro_api()

import pandas as pd
import matplotlib; matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

xianbank = pro.daily(ts_code='600928.SH', start_date='20190301', end_date='20200229')
xibuzhengquan = pro.daily(ts_code='002673.SZ', start_date='20190301', end_date='20200229')

close_xianbank = xianbank[['trade_date', 'close']]
close_xibuzhengquan = xibuzhengquan[['trade_date', 'close']]
close_xianbank = close_xianbank.set_index(['trade_date'])
close_xibuzhengquan = close_xibuzhengquan.set_index(['trade_date'])
close_xianbank = close_xianbank.sort_values('trade_date', ascending = True)
close_xibuzhengquan = close_xibuzhengquan.sort_values('trade_date', ascending = True)

# 单期简单收益率
# 将收盘价格滞后一期
close_xianbank['lag_close']= close_xianbank['close'].shift(1)
dailyreturn_xianbank = (close_xianbank['close'] - close_xianbank['lag_close']) / close_xianbank['lag_close']
# 用pct_change()更简单
# dailyreturn_xianbank = close_xianbank['close'].pct_change()

# 多期简单收益率 以2期为例
dailyreturn_xianbank_2 = (close_xianbank['close'] - close_xianbank['close'].shift(2)) / close_xianbank['close'].shift(2)
# 同样用pct_change()更简单
# dailyreturn_xianbank_2 = close_xianbank['close'].pct_change(periods = 2)

# 利用ffn模块计算单期简单收益率
# pip install ffn
import ffn
ffn_dailyreturn_xianbank = ffn.to_returns(close_xianbank['close'])

# 计算对数收益 / 连续复利收益率
logreturn_xianbank = np.log(close_xianbank['close'] / close_xianbank['close'].shift(1))
logreturn_xianbank_2 = np.log(close_xianbank['close'] / close_xianbank['close'].shift(2))
# 或者
ffn_logreturn_xianbank = ffn.to_log_returns(close_xianbank['close'])

# 计算年化简单收益率，假设一年有245个交易日
annualize_dailyreturn_xianbank = (1 + dailyreturn_xianbank).cumprod()[-1]**(245/311) - 1

# 收益率曲线绘图
dailyreturn_xianbank.plot()
# 累积收益率曲线
# cumprod()， 0代表列的计算，1代表行的计算
((1 + dailyreturn_xianbank).cumprod(0) - 1).plot()

# 观察方差比较两只股票风险的大小
dailyreturn_xianbank_without_nan = close_xianbank['close'].pct_change().dropna()
dailyreturn_xibuzhengquan_without_nan = close_xibuzhengquan['close'].pct_change().dropna()

dailyreturn_xianbank_without_nan.std()
dailyreturn_xibuzhengquan_without_nan.std()

# 下行风险(低于目标收益率的变动，更贴合投资者实际担忧的风险)
def cal_half_dev(returns):
	mu = returns.mean()
	temp = returns[returns < mu]
	half_deviation = (sum((mu - temp)**2) / len(returns))**0.5
	return(half_deviation)

cal_half_dev(dailyreturn_xianbank_without_nan)
cal_half_dev(dailyreturn_xibuzhengquan_without_nan)

# 用风险价值Value at Rist, VaR度量风险
# 历史模拟，下跌超过5%的概率
dailyreturn_xianbank_without_nan.quantile(0.05)
dailyreturn_xibuzhengquan_without_nan.quantile(0.05)
# 协方差矩阵法，下跌超过5%的概率
from scipy.stats import norm
norm.ppf(0.05, dailyreturn_xianbank_without_nan.mean(), dailyreturn_xianbank_without_nan.std())
norm.ppf(0.05, dailyreturn_xibuzhengquan_without_nan.mean(), dailyreturn_xibuzhengquan_without_nan.std())

# 期望亏空，超过VaR水平的损失的期望值，也就是最坏的α%损失的平均值，越小越好
dailyreturn_xianbank_without_nan[dailyreturn_xianbank_without_nan <= dailyreturn_xianbank_without_nan.quantile(0.05)].mean()
dailyreturn_xibuzhengquan_without_nan[dailyreturn_xibuzhengquan_without_nan <= dailyreturn_xibuzhengquan_without_nan.quantile(0.05)].mean()

# 最大回撤：一段周期内从最高点下跌到最低点的最大值，越小越好
# 例:最高收益80％，最低收益50％，最大回撤30％
value = (1+ dailyreturn_xianbank_without_nan).cumprod()
D = value.cummax() - value # 回撤
d = D / (D + value) # 回撤率
MDD = D.max() # 最大回撤
mdd = d.max() # 最大回撤率

# 利用ffn模块计算最大回撤率
# (1 + return_daxiangsu).cumprod()为收益率序列
ffn.calc_max_drawdown((1+ dailyreturn_xianbank_without_nan).cumprod())
