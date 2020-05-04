import tushare as ts
ts.set_token('你的token')
pro = ts.pro_api()

import pandas as pd
import matplotlib; matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt

xianbank = pro.daily(ts_code='600928.SH', start_date='20200101', end_date='20200331')
hs300 = pro.index_daily(ts_code='399300.SZ', start_date='20200101', end_date='20200331')

close_xianbank = xianbank[['trade_date', 'close']]
close_hs300 = hs300[['trade_date', 'close']]
#close_xianbank = close_xianbank.set_index(['trade_date'])
#close_hs300 = close_hs300.set_index(['trade_date'])
close_xianbank = close_xianbank.sort_values('trade_date', ascending = True)
close_hs300 = close_hs300.sort_values('trade_date', ascending = True)

dailyreturn_xianbank = close_xianbank['close'].pct_change().dropna()
dailyreturn_xianbank.name = 'dailyreturn_xianbank'
dailyreturn_hs300 = close_hs300['close'].pct_change().dropna()
dailyreturn_hs300.name = 'dailyreturn_hs300'

merge_return = pd.merge(pd.DataFrame(dailyreturn_xianbank), pd.DataFrame(dailyreturn_hs300), left_index = True, right_index = True, how = 'inner')

# 计算无风险收益率
# 假设当年一年期的国债利率的年化利率为1.125%，先转化为月利率
# 年复利率R转换成月复利率r的计算公式为： r=(1+R)^(1/12)-1
# 年复利率R转换成月复利率r的计算公式为： r=(1+R)^(1/360)-1
rf = 1.0125**(1/360) - 1

# 计算股票超额收益率和市场风险溢价
Eret = merge_return - rf

# 绘制两者之间的散点图
plt.scatter(Eret.values[:,0], Eret.values[:,1])

# 拟合资本资产定价模型
import statsmodels.api as sm
model = sm.OLS(Eret.dailyreturn_xianbank, sm.add_constant(Eret.dailyreturn_hs300))
result = model.fit()
result.summary()

# 根据拟合结果，判断西安银行的股票和沪深300指数的关系为：
# Ri - Rf = αi + βi(Rm - Rf) + εi
# Ri - Rf = 常数项系数 + mktret系数(Rm - Rf) + εi
# Ri - Rf = -0.0036 + 1.0477(Rm - Rf) + εi
# α大于0说明实际回报率大于期望回报率，回报率越高价格越低，实际价格比期望价格低，股价低估；α小于0,说明股价高估
# 西安银行的α为-0.0036<0，股价高估，但是α并没有显著异于0，从β看，西安银行的波动率大于大盘
# 在实际操作中，可以买入预期alpha>0的股票

########偷#######懒#######方#######法##############
# xianbank = pro.daily(ts_code='600928.SH', start_date='20200101', end_date='20200331')
# hs300 = pro.index_daily(ts_code='399300.SZ', start_date='20200101', end_date='20200331')
# merge_return = pd.merge(pd.DataFrame(hs300.pct_chg),pd.DataFrame(xianbank.pct_chg),left_index=True,right_index=True,how='inner')  