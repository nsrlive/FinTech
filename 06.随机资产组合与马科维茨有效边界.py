import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
style.use('seaborn')

# tickers是你想选的股票，股票数据文件调用的是之前批量获取的，也可以自己重新获取感兴趣的股票
# 建立投资组合之前，用之前的代码检查一下相关性，相关性太高，投资组合降低风险的效果就会有限
tickers = ['002739.SZ','002466.SZ']

def put_some_stock_price_into_one_df():
    some_stock_price_df = pd.DataFrame()
    for count, ticker in enumerate(tickers):
        df = pd.read_csv('stock_dfs/{}.csv'.format(ticker))
        df = df.sort_values('trade_date', ascending = True)
        df.set_index('trade_date', inplace = True)
        df.rename(columns = {'close':ticker}, inplace = True)
        # 1 or axis=1 跨列
        df.drop(['index', 'ts_code', 'open', 'high', 'low', 'pre_close', 'change', 'pct_chg', 'vol', 'amount'], 1, inplace = True)
        if some_stock_price_df.empty:
            some_stock_price_df = df
        else:
            some_stock_price_df = some_stock_price_df.join(df, how = 'outer')
        print(count)
    some_stock_price_df.to_csv('CSI_selected_closes.csv')

put_some_stock_price_into_one_df()

# 预处理
df = pd.read_csv('CSI_selected_closes.csv')
df = df.set_index('trade_date')
df = df.dropna()

# 基本金融指标计算
return_daily = df.pct_change()
return_annual = return_daily.mean() * 250

cov_daily = return_daily.cov()
cov_annual = cov_daily * 250

portfolio_return = []
portfolio_volatility = []
stock_weights = []

# Make Portfolio
num_assets = len(tickers)
# 两种股票比例随机，生成1000种不同比例的投资组合
num_portfolio = 1000

for single_portfolio in range(num_portfolio):
    weights = np.random.random(num_assets)
    # 让比例相加等于1
    # c /= a 等效于 c = c / a
    weights = weights / np.sum(weights)
    # 矩阵运算在投资组合回报中的应用
    # return_annual是两行一列的数据，weights是一行两列的数据
    returns = np.dot(weights, return_annual)
    # 投资组合标准差
    volatility = np.sqrt(np.dot(np.dot(weights, cov_annual), weights.T))
    portfolio_return.append(returns)
    portfolio_volatility.append(volatility)
    stock_weights.append(weights)

print(portfolio_return)
print(portfolio_volatility)
print(stock_weights)

# 将生成的投资组合合并到一张表种
portfolio = {'Rp':portfolio_return,
             'Vp':portfolio_volatility}

# 现在portfolio里只有不同比例投资组合的收益和风险，需要将每种组合中各股票的比例显示出来
# 设置每一列的列名为股票代码 + 'Weight'
for counter, ticker in enumerate(tickers):
    portfolio[ticker + 'Weight'] = [Weight[counter] for Weight in stock_weights]
    
df = pd.DataFrame(portfolio)
df.to_csv('big_portfolio_data.csv')

# 找出最小风险值和收益最大值分别对应的数据
df['Vp'].idxmin()
df['Rp'].idxmax()
df.iloc[117,:] # 手动替换117

# 画出有效边界
df.plot.scatter(x = 'Vp', y = 'Rp', figsize = (10,8), grid = True)
plt.xlabel('Volatility', fontsize = 20)
plt.ylabel('Expected Returns', fontsize = 20)
plt.title('Efficient Frontier', fontsize = 20)
