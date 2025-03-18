import math

# 设置相机参数
elev = math.radians(30)   # 仰角
azim = math.radians(-140) # 方位角
dist = 3.3                # 距离

# 计算相机位置（球坐标转笛卡尔坐标）
x = dist * math.cos(elev) * math.cos(azim)
y = dist * math.cos(elev) * math.sin(azim)
z = dist * math.sin(elev)

print(f"相机位置：({x:.3f}, {y:.3f}, {z:.3f})")