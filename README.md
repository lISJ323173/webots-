# Webots Cart-Pole

Webots R2025a 的一阶倒立摆（cart-pole）仿真项目。

已完成从被动模型到闭环对比的验证链：

- A1：被动 cart-pole，小车只沿 X 移动，摆杆自由倒下。
- A2：Python 读取 `x`、`θ`，验证 `±2 N` 施力方向。
- A3：非线性动力学、A2 开环对照、直立点线性化。
- A4：级联 PD-PID 站立 10 s。
- A5：离散 LQR 站立 10 s。
- A6：PID/LQR × `step`/`pulse`/`mass` 六组同工况对比。

当前基础世界 `worlds/cart_pole.wbt` 默认：

```text
controller "cart_pole_lqr"
controllerArgs [ "step" ]
```

质量摄动世界 `worlds/cart_pole_mass.wbt` 默认：

```text
controller "cart_pole_lqr"
controllerArgs [ "mass" ]
```

## 当前状态

- A0 环境验收：通过（Webots R2025a，Python 3.14.7 64-bit）
- A1 被动模型：通过
- A2 传感器与施力方向：通过
- A3 动力学模型与开环校验：完成
- A4 级联 PD-PID 站立：通过
- A5 离散 LQR 站立：通过
- A6 六组同工况对比：通过
- A7 曲线、调节时间和最终对比：待开始

## 模型参数

| 符号 | 含义 | 值 |
|---|---|---:|
| `M` | 小车质量 | `1.00 kg` |
| `m` | 摆杆质量 | `0.24 kg`（mass 组 `0.30 kg`） |
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
- 控制输入为小车沿 `+X` 的力 `F`，单位 `N`；限幅 `±10 N`。
- `cart_position` 单位为米；`pole_angle` 单位为弧度。

## 文件结构

```text
cart-pole-webots/
  worlds/
    cart_pole.wbt                  # 基础世界，摆杆 0.24 kg
    cart_pole_mass.wbt             # 质量摄动，摆杆 0.30 kg
  controllers/
    cart_pole_pid/cart_pole_pid.py # 级联 PD-PID + A6 工况
    cart_pole_lqr/cart_pole_lqr.py # 离散 LQR + A6 工况
    cart_pole_probe/cart_pole_probe.py # A2 探针
  docs/
    A1-acceptance.md
    A2-acceptance.md
    A4-acceptance.md
    A5-acceptance.md
    A6-acceptance.md
    a1-initial.png
    a1-fall.png
    a1-verification.txt
    a1-probe-run1.csv
    a1-probe-run2.csv
    a2-positive.txt
    a2-negative.txt
    a4-console.txt
    a5-console.txt
    a6_pid_step.txt
    a6_lqr_step.txt
    a6_pid_pulse.txt
    a6_lqr_pulse.txt
    a6_pid_mass.txt
    a6_lqr_mass.txt
    model.md
  a4_pid_balance.csv
  a5_lqr_balance.csv
  a6_pid_step.csv
  a6_lqr_step.csv
  a6_pid_pulse.csv
  a6_lqr_pulse.csv
  a6_pid_mass.csv
  a6_lqr_mass.csv
  README.md
```

## A6 测试矩阵

| 工况 | 世界设置 | 输入 |
|---|---|---|
| `step` | 摆杆 `0.24 kg` | `t=2.000 s` 位置目标 `0 → +0.20 m` |
| `pulse` | 摆杆 `0.24 kg` | 目标保持 `0`；`t=4.000 s` 起叠加 `+3 N`，持续 `80 ms` |
| `mass` | 摆杆 `0.30 kg` | 重复 `step` 的 `+0.20 m` 阶跃 |

两种控制器使用同一组增益、同一 `8 ms` 步长、同一 `±10 N` 限幅、同一 `+0.08 rad` 初始角，每次从磁盘重新加载世界。

## 运行 A6

1. 在 `worlds/cart_pole.wbt` 或 `worlds/cart_pole_mass.wbt` 中选择 `controller`。
2. 用 `controllerArgs [ "step" ]`、`[ "pulse" ]` 或 `[ "mass" ]` 选择工况。
3. 从磁盘打开世界，`Pause` → `Reset Simulation`，确认 `0:00:00:000`。
4. 用 `Real-time` 或 `Fast` 运行 10 s；Console 出现 `A6` 后暂停。
5. 项目根目录生成 `a6_{mode}_{case}.csv`。

## A6 结果

```text
A6 mode=pid case=step  peak_x=0.1943 m tail_x=0.0059 m tail_theta=0.0003 rad
A6 mode=lqr case=step  peak_x=0.2058 m tail_x=0.0028 m tail_theta=0.0003 rad
A6 mode=pid case=pulse peak_x=0.0934 m tail_x=0.0056 m tail_theta=0.0005 rad
A6 mode=lqr case=pulse peak_x=0.0985 m tail_x=0.0012 m tail_theta=0.0002 rad
A6 mode=pid case=mass  peak_x=0.1941 m tail_x=0.0062 m tail_theta=0.0003 rad
A6 mode=lqr case=mass  peak_x=0.2050 m tail_x=0.0024 m tail_theta=0.0003 rad
```

| 工况 | 控制器 | `tail_x` (m) | `tail_theta` (rad) | 结果 |
|---|---|---:|---:|---|
| `step` | PID | `0.005933` | `0.000280` | 通过 |
| `step` | LQR | `0.002826` | `0.000334` | 通过 |
| `pulse` | PID | `0.005566` | `0.000532` | 通过 |
| `pulse` | LQR | `0.001193` | `0.000173` | 通过 |
| `mass` | PID | `0.006208` | `0.000308` | 通过 |
| `mass` | LQR | `0.002435` | `0.000292` | 通过 |

六组都跑满 10 s，最大 `|θ| ≈ 0.08018 rad`，未接近 `±1.4 rad` 限位；最大力在 `3.34 ～ 3.75 N`，未饱和。`pulse` 两组各有恰好 10 个连续 `disturbance_N = 3.0` 样本。

初步观察：三个工况下 LQR 的 `tail_x` 都小于 PID；LQR 的首拍力和最大力也略小。`peak_x` 是绝对位置，`step`/`mass` 组因目标为 `0.20 m`，不能直接当作超调量。完整曲线、调节时间和超调量留到 A7。

## A5 结果（历史记录）

```text
START theta=+0.0802 rad F=+3.344 N
A5 peak_x=0.0985 m tail_x=0.0022 m tail_theta=0.0003 rad
```

## A4 结果（历史记录）

```text
START theta=+0.0802 rad F=+3.742 N
A4 peak_x=0.0934 m tail_x=0.0004 m tail_theta=0.0002 rad
```

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

## 备注

- A1/A2/A4/A5 的数据保留为历史验证；当前世界已加入 A6 工况选择。
- 该世界没有 `Background` 和地板，3D 背景为黑色是正常的。
- 质量摄动只改摆杆 `0.24 → 0.30 kg`，控制器增益不重新整定。

## 下一步：A7

用六份 `a6_*.csv` 生成对照曲线，计算从事件发生到位置和摆角同时进入误差带、并保持的时间，完成 LQR 与级联 PID 的最终对比。
