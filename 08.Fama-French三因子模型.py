# 市场风险溢酬、市值、账面市值比 三因素模型
# 市场风险溢酬因子对应的是市场投资组合的收益率
# 账面市值比因子对应的做多市值较小的公司、做空市值较大公司的投资组合收益率
# 账面市值比因子对应的是做多高B/M比公司、做空低B/M比公司的投资组合收益率

# Rit - Rft = αi + bi*(Rmt - Rft) + si*SMBt + hi*HMLt + εit
# αi超额收益率，Rit投资组合收益率，市值因子SMBt，账面市值比因子HMLt
# 通过回归，检验αi和bi、si、hi（三个因子的系数）是否显著异于0，即是否能解释收益率
# 若研究对象为投资组合Rit需要加权平均计算（等比例加权平均、按市值比例加权平均）

# Fama-French因子计算复杂，暂时先从国泰安数据库获取
# P9705：创业板; P9706：综合A股市场; P9707：综合B股市场; P9709：综合A股和创业板; P9710：综合AB股和创业板； P9711：科创板； P9712：综合A股和科创板； P9713：综合AB股和科创板； P9714：综合A股和创业板和科创板； P9715：综合AB股和创业板和科创板


import tushare as ts
ts.set_token('你的token')
pro = ts.pro_api()

import pandas as pd
import matplotlib; matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
plt.rcParams['font.sans-serif'] = 'SimHei'  #让matplotlib支持微软雅黑中文
plt.rcParams['axes.unicode_minus'] = False  #解决负号无法正常使用的问题

xianbank = pro.daily(ts_code='600928.SH', start_date='20200101', end_date='20200331')
dailyreturn_xianbank = xianbank[['trade_date','pct_chg']]
dailyreturn_xianbank = dailyreturn_xianbank.sort_values('trade_date', ascending = True)
dailyreturn_xianbank = dailyreturn_xianbank.set_index('trade_date')
dailyreturn_xianbank.index = pd.to_datetime(dailyreturn_xianbank.index) # 必须

threefactors = pd.read_csv('FF_data.csv', index_col = 'TradingDate') # 国泰安编码使用GB2312，encoding无效，这里源文件已改为UTF-8
a_threefactors = threefactors[threefactors['MarkettypeID']== 'P9706']
a_threefactors.index = pd.to_datetime(a_threefactors.index) # 必须
a_threefactors = a_threefactors.drop(['MarkettypeID'], axis=1)

plt.subplot(221)
plt.scatter(dailyreturn_xianbank['pct_chg'], a_threefactors['RiskPremium1'])
plt.subplot(222)
plt.scatter(dailyreturn_xianbank['pct_chg'], a_threefactors['SMB1'])
plt.subplot(223)
plt.scatter(dailyreturn_xianbank['pct_chg'], a_threefactors['HML1'])

import statsmodels.api as sm
regression_threefactors = sm.OLS(dailyreturn_xianbank['pct_chg'], sm.add_constant(a_threefactors))
result = regression_threefactors.fit()
result.summary()

# 根据拟合结果，西安银行的股票收益率对三因子模型中的市场风险溢酬敏感，也就是说市场风险溢酬可以部分地解释西安银行股票收益率的变动
# 假设三因子模型是正确的，市场风险、市值风险、账面市值比这三类风险能很好地解释个股的超额收益，那么a的长期均值应该是 0
# 
# 今天的偏离在未来都会最终回到得到正确的定价
# 在建模时将数据分为两组，即历史数据和预测数据
# 假设1月到3月的数据为历史数据，通过拟合得到超额收益率αi和bi、si、hi（三个因子的系数）
