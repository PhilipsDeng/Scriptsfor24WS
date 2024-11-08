import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import numpy as np
import matplotlib.pyplot as plt

# 1. 定义UNet模块
class UNet(nn.Module):
    def __init__(self):
        super(UNet, self).__init__()
        self.encoder = nn.Sequential(
            nn.Conv2d(2, 64, 3, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 128, 3, padding=1),
            nn.ReLU()
        )
        self.middle = nn.Sequential(
            nn.Conv2d(128, 128, 3, padding=1),
            nn.ReLU()
        )
        self.decoder = nn.Sequential(
            nn.Conv2d(128, 64, 3, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 1, 3, padding=1)
        )

    def forward(self, x, t):
        # 将t步嵌入扩展到与x相同的尺寸
        t_embed = t[:, None, None, None].expand(-1, 1, x.shape[2], x.shape[3])
        x_in = torch.cat([x, t_embed], dim=1)
        x1 = self.encoder(x_in)
        x2 = self.middle(x1)
        x3 = self.decoder(x2)
        return x3

# 2. 定义正向和反向扩散过程
def q_sample(x_0, t, noise):
    beta_t_device = beta_t.to(x_0.device)
    t = t.view(-1, 1, 1, 1).expand(x_0.size(0), 1, x_0.size(2), x_0.size(3))
    return x_0 * torch.sqrt(1 - beta_t_device[t]) + noise * torch.sqrt(beta_t_device[t])

def p_sample(model, x_t, t):
    beta_t_device = beta_t.to(x_t.device)
    t_tensor = torch.full((x_t.size(0),), t, device=x_t.device, dtype=torch.long)
    t_tensor = t_tensor.view(-1, 1, 1, 1).expand(x_t.size(0), 1, x_t.size(2), x_t.size(3))
    pred_noise = model(x_t, t_tensor)
    return (x_t - pred_noise * torch.sqrt(beta_t_device[t])) / torch.sqrt(1 - beta_t_device[t])

# 3. 准备MNIST数据集，使用本地.pt文件
train_images = torch.load(r"C:\Users\Philips Deng\Downloads\i2dl\datasets\mnist\train_images.pt")
train_labels = torch.load(r"C:\Users\Philips Deng\Downloads\i2dl\datasets\mnist\train_labels.pt")
val_images = torch.load(r"C:\Users\Philips Deng\Downloads\i2dl\datasets\mnist\val_images.pt")
val_labels = torch.load(r"C:\Users\Philips Deng\Downloads\i2dl\datasets\mnist\val_labels.pt")

# 使用 DataLoader 进行打包
train_dataset = torch.utils.data.TensorDataset(train_images, train_labels)
val_dataset = torch.utils.data.TensorDataset(val_images, val_labels)

train_dataloader = DataLoader(train_dataset, batch_size=64, shuffle=True)
val_dataloader = DataLoader(val_dataset, batch_size=64, shuffle=False)

# 4. 定义模型、优化器和损失函数
model = UNet().to(torch.device("cuda" if torch.cuda.is_available() else "cpu"))
optimizer = optim.Adam(model.parameters(), lr=1e-4)
loss_fn = nn.MSELoss()

# 5. 设定扩散过程的超参数
T = 1000
beta_t = torch.linspace(1e-4, 0.02, T)

# 6. 训练过程
epochs = 5
for epoch in range(epochs):
    for batch_idx, (data, target) in enumerate(train_dataloader):
        data = data.to(torch.device("cuda" if torch.cuda.is_available() else "cpu"))
        t = torch.randint(0, T, (data.size(0),), device=data.device)
        noise = torch.randn_like(data)
        x_t = q_sample(data, t, noise)

        # 预测噪声
        pred_noise = model(x_t, t)
        loss = loss_fn(pred_noise, noise)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if batch_idx % 100 == 0:
            print(f"Epoch [{epoch+1}/{epochs}], Batch [{batch_idx}], Loss: {loss.item():.4f}")

# 7. 生成图像
model.eval()
with torch.no_grad():
    label = 3  # 生成数字 '3'
    generated_images = []
    x_t = torch.randn((1, 1, 28, 28), device=model.encoder[0].weight.device)
    for t in reversed(range(T)):
        x_t = p_sample(model, x_t, t)
        generated_images.append(x_t.squeeze().cpu().numpy())

    # 显示生成的图像
    plt.imshow(generated_images[-1], cmap="gray")
    plt.show()