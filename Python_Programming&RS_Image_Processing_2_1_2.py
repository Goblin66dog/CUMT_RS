# 清理数据集：将所有空值、？替换为NaN
import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt
df = pd.read_csv(r"Python_Programming&RS_Image_Processing_2\Automobile_data.csv")
df.replace([" ",'?'], np.nan, inplace=True)
# 找到价格最低和最高的汽车公司名称、车身风格、轴距、发动机类型、价格、里程、马力等信息
df['price'] = pd.to_numeric(df['price']) # 将价格列转换为数值类型
min_price = df['price'].min() # 计算最低价格
max_price = df['price'].max() # 计算最高价格
min_price_car = df[df['price'] == min_price] # 筛选出价格最低的汽车
max_price_car = df[df['price'] == max_price] # 筛选出价格最高的汽车
print('价格最低的汽车信息如下：')
print(min_price_car[['company', 'body-style', 'wheel-base', 'engine-type', 'price', 'average-mileage', 'horsepower']])
print('价格最高的汽车信息如下：')
print(max_price_car[['company', 'body-style', 'wheel-base', 'engine-type', 'price', 'average-mileage', 'horsepower']])

# 打印所有沃尔沃汽车的详细信息
volvo_cars = df[df['company'] == 'volvo'] # 筛选出沃尔沃汽车
print('所有沃尔沃汽车的详细信息如下：')
print(volvo_cars)

# 计算每家公司的汽车数量
car_counts = df['company'].value_counts() # 统计每家公司的汽车数量
print('每家公司的汽车数量如下：')
print(car_counts)

# 按照汽车轴距对汽车进行排序
df['wheel-base'] = pd.to_numeric(df['wheel-base']) # 将轴距列转换为数值类型
sorted_cars = df.sort_values(by='wheel-base', ascending=False) # 按照轴距对汽车进行排序
print('按照汽车轴距排序后的汽车信息如下：')
print(sorted_cars)

