import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
style.use('ggplot')

# 热力图与相关性有关
# 自行修改文件名和文件路径
# 若只查看相关性数据而不绘图，自行删除或注释掉后面的代码，并添加return data和corr = pd.DataFrame(calculate_save_and_plot_pearson_correlation_heatmap())
def calculate_save_and_plot_pearson_correlation_heatmap():
    df = pd.read_csv('CSI_300_Joined_closes.csv')
    # 用变动百分比分析，而不是直接计算相关性
    # 10元上涨1元和1000元上涨1元虽然都是上涨1元但是变动百分比有天壤之别
    df = df.sort_values('trade_date', ascending = True)
    df_corr = df.pct_change().corr()
    data = df_corr.values
   
    fig = plt.figure()
    # “111”表示长宽为1×1，位置在1的子图，“234”表表示长宽为2×3，位置在4的子图
    ax = fig.add_subplot(111)
    # pcolor用于生成二维图像，主要是热力图
    # cmap用于改变绘制风格；plt.cm是色彩映射函数，后跟色彩代码
    heatmap = ax.pcolor(data, cmap = plt.cm.RdYlGn)
    # colorbar是色彩条，相当于图例
    fig.colorbar(heatmap)
   
    # 设置标签刻度和间隔
    # shape[0]图像的垂直尺寸，shape[1]图像的水平尺寸
    ax.set_xticks(np.arange(0.5,data.shape[0] + 0.5, step = 1))
    ax.set_yticks(np.arange(0.5,data.shape[1] + 0.5, step = 1))
    
    # 调整下x和y坐标标签的位置，需要同时调整
    ax.invert_yaxis()
    ax.xaxis.tick_top()
    
    column_labels = df_corr.columns
    row_labels = df_corr.index
   
    ax.set_xticklabels(column_labels)
    ax.set_yticklabels(row_labels)
   
    # 竖向显示坐标轴标签
    plt.xticks(rotation = 90)
    # 因为相关性是-1到1，heatmap的值的范围应当设置为-1到1
    heatmap.set_clim(-1,1)
    plt.tight_layout()
    plt.show()
    
calculate_save_and_plot_pearson_correlation_heatmap()