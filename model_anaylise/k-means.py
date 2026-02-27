import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 示例数据：日期和使用数量
data = {
    'date': ['2024-01-01', '2024-01-05', '2024-01-10', '2024-01-15', '2024-01-20'],
    'usage': [10, 15, 12, 18, 20]
}

# 转换为DataFrame
df = pd.DataFrame(data)
df['date'] = pd.to_datetime(df['date'])  # 将日期字符串转换为datetime对象

# 计算间隔天数
df['interval_days'] = df['date'].diff().dt.days  # 计算相邻日期的间隔天数
df.loc[0, 'interval_days'] = 0  # 第一次使用的间隔天数设置为0

# 绘图
fig, ax = plt.subplots(figsize=(10, 6))

# 绘制间隔天数
ax.bar(df['date'], df['interval_days'], color='skyblue', label='Interval Days')

# 绘制使用数量
ax2 = ax.twinx()  # 创建第二个y轴
ax2.plot(df['date'], df['usage'], color='red', marker='o', label='Usage')

# 设置x轴日期格式和间隔
ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))  # 设置日期间隔为5天[^19^]
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # 设置日期格式[^19^]

# 自动调整日期标签，避免重叠
fig.autofmt_xdate(rotation=45)  # 旋转日期标签[^24^]

# 添加图例
ax.legend(loc='upper left')
ax2.legend(loc='upper right')

# 设置标题和标签
plt.title('Usage and Interval Days Over Time')
ax.set_xlabel('Date')
ax.set_ylabel('Interval Days')
ax2.set_ylabel('Usage')

plt.show()