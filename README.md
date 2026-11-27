# Webots Cart-Pole

Webots R2025a 的一阶倒立摆（cart-pole）仿真项目。

已完成从被动模型到闭环站立的验证链：

- A1：被动 cart-pole，小车只沿 X 移动，摆杆自由倒下。
- A2：Python 读取 `x`、`θ`，并验证 `±2 N` 施力方向。
- A3：非线性动力学、A2 开环对照、直立点线性化。
- A4：级联 PD-PID 站立 10 s。
- A5：离散 LQR 站立 10 s。

当前 `worlds/cart_pole.wbt` 使用 A5 控制器：

```text
controller "cart_pole_lqr"
```

## 当前状态

- A0 环境验收：通过（Webots R2025a，Python 3.14.7 64-bit）
- A1 被动模型：通过
- A2 传感器与施力方向：通过
- A3 动力学模型与开环校验：完成
- A4 级联 PD-PID 站立：通过
- A5 离散 LQR 站立：通过
- A6 同工况对比（位置阶跃/扰动）：待开始

## 模型参数

| 符号 | 含义 | 值 |
|---|---|---:|
| `M` | 小车质量 | `1.00 kg` |
| `m` | 摆杆质量 | `0.24 kg` |
| `L` | 摆杆长度 | `0.50 m` |
| `l` | 铰点到摆杆质心距离 | `0.25 m` |
| `J_y` | 摆杆绕质心、平行于铰轴的转动惯量 | `0.00501 kg·m²` |
| `I_p` | 摆杆绕铰点转动惯量 | `0.0200125 kg·m²` |
| — | 小车行程 | `-1.50 ～ +1.50 m` |
| `θ₀` | 摆杆初始倾角 | `+0.08 rad` |
| — | 仿真步长 | `8 ms` |

## 坐标与符号约定

- 世界坐标系：`ENU`，`+X` 向右，`+Y` 为铰轴方向，`+Z` 向上。
- 直立为 `θ = 0 rad`；杆顶向 `+X` 倾斜为正。
- 控制输入定义为小车沿 `+X` 的力 `F`，单位 `N`。
- `cart_position` 单位为米；`pole_angle` 单位为弧度。

## 文件结构

```text
cart-pole-webots/
  worlds/cart_pole.wbt                  # 当前 A5 世界
  controllers/
    cart_pole_lqr/cart_pole_lqr.py      # A5 离散 LQR
    cart_pole_pid/cart_pole_pid.py      # A4 级联 PD-PID
    cart_pole_probe/cart_pole_probe.py  # A2 探针
  docs/
    A1-acceptance.md
    A2-acceptance.md
    A4-acceptance.md
    A5-acceptance.md
    a1-initial.png
    a1-fall.png
    a1-verification.txt
    a1-probe-run1.csv
    a1-probe-run2.csv
    a2-positive.txt
    a2-negative.txt
    a4-console.txt
    a5-console.txt
    model.md                            # A3 动力学模型与开环校验
  a4_pid_balance.csv                    # A4 10 s 数据
  a5_lqr_balance.csv                    # A5 10 s 数据
  README.md
```

## 运行 A5

1. Webots R2025a → `File → Open World` → `worlds/cart_pole.wbt`。
2. `Pause` → `Reset Simulation`，确认时间为 `0:00:00:000`。
3. 使用 `Real-time` 或 `Fast` 运行 10 s。
4. 控制器按 8 ms 周期采样 `x`、`θ`，差分得到 `\dot x`、`\dot\theta`，计算 `F = clip(-K s, ±10 N)`。
5. Console 出现 `A5` 行后 `Pause`；项目根目录生成 `a5_lqr_balance.csv`。

## A5 结果

```text
START theta=+0.0802 rad F=+3.344 N
A5 peak_x=0.0985 m tail_x=0.0022 m tail_theta=0.0003 rad
```

| 检查项 | 通过标准 | 实测 |
|---|---|---|
| 初始角度 | 接近 `+0.08 rad` | `+0.08018 rad` |
| 首拍力 | `F > 0 N` | `+3.344 N` |
| 时长 | 10 s | 10.000 s，1251 行 |
| 摆杆 | 不碰 `±1.4 rad` 限位 | 最大 `|θ| = 0.08018 rad` |
| 小车峰值 | `peak_x ≤ 0.30 m` | `0.09852 m` |
| 最后 2 s 小车 | `tail_x ≤ 0.05 m` | `0.00224 m` |
| 最后 2 s 摆角 | `tail_theta ≤ 0.02 rad` | `0.00027 rad` |
| 力饱和 | 不持续饱和 | 最大 `3.344 N < 10 N` |

完整记录见 [docs/A5-acceptance.md](docs/A5-acceptance.md)。

## A4 与 A5 初步对照

| 指标 | A4 级联 PD-PID | A5 LQR |
|---|---:|---:|
| 首拍力 | `+3.742 N` | `+3.344 N` |
| `peak_x` | `0.0934 m` | `0.0985 m` |
| `tail_x` | `0.0004 m` | `0.0022 m` |
| `tail_theta` | `0.0002 rad` | `0.0003 rad` |
| 最大 `|F|` | `3.742 N` | `3.344 N` |

两种控制器都通过站立验收线。就这次同工况而言，PID 的峰值和尾段位置误差更小，LQR 的首拍力和最大力略小；位置阶跃和扰动对比留到 A6。

## A4 结果（历史记录）

```text
START theta=+0.0802 rad F=+3.742 N
A4 peak_x=0.0934 m tail_x=0.0004 m tail_theta=0.0002 rad
```

详细记录见 [docs/A4-acceptance.md](docs/A4-acceptance.md)，数据见 `a4_pid_balance.csv`。

## A3 动力学模型

非线性模型：

```text
(M+m)x¨ + ml cosθ θ¨ - ml sinθ θdot² = F
Ip θ¨ + ml cosθ x¨ = mgl sinθ
```

A2 开环对照：

| 脉冲 | Webots dx | 模型 dx | Webots 末端 θ | 模型末端 θ |
|---|---:|---:|---:|---:|
| `+2.00 N` | `+0.02350 m` | `+0.02237 m` | `+0.04243 rad` | `+0.04443 rad` |
| `-2.00 N` | `-0.02767 m` | `-0.02635 m` | `+0.20537 rad` | `+0.19913 rad` |

最大绝对误差：位移 `0.00132 m`，末端摆角 `0.00624 rad`。

直立点线性化：

```text
A = [0  1   0       0;
     0  0  -1.6646  0;
     0  0   0       1;
     0  0  34.4024  0]
B = [0; 0.9433; 0; -2.8281]
```

开环正特征值约 `5.87 s⁻¹`。完整推导见 [docs/model.md](docs/model.md)。

## A1/A2 历史记录

- A1：被动摆杆从 `+0.08 rad` 自由倒下，小车只沿 X 移动；两次重置运行 CSV 完全一致。
- A2：`+2 N` 产生 `dx=+0.02350 m`，`-2 N` 产生 `dx=-0.02767 m`，传感器和施力方向正确。

详见 [docs/A1-acceptance.md](docs/A1-acceptance.md) 和 [docs/A2-acceptance.md](docs/A2-acceptance.md)。

## 备注

- A1/A2/A4 的控制器和数据保留为历史验证；当前世界已切换为 A5 LQR。
- 该世界没有 `Background` 和地板，3D 背景为黑色是正常的；验收看轨道、小车和摆杆是否可见。
- A5 最大力 `3.344 N` 未达到 `±10 N` 限幅，不是靠饱和硬撑。

## 下一步：A6

用 `a4_pid_balance.csv` 和 `a5_lqr_balance.csv` 做同工况对比，再补位置阶跃和扰动测试，比较 LQR 与级联 PID 的恢复速度、峰值和稳态误差。
