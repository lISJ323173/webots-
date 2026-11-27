# Webots Cart-Pole

Webots R2025a 的一阶倒立摆（cart-pole）仿真项目。

A1 完成了**被动开环模型**：小车只能沿世界 X 轴直线滑动，摆杆从 `+0.08 rad` 的初始倾角开始在重力作用下绕 Y 轴自由倒下。A2 在此基础上加入 `LinearMotor` 和只读探针控制器，验证 Python 能读取小车位置、摆杆角度，并按 `+X` / `-X` 方向施力。

当前 `worlds/cart_pole.wbt` 是 A2 配置：

```text
controller "cart_pole_probe"
controllerArgs [ "2.0" ]
```

## 当前状态

- A0 环境验收：通过（Webots R2025a，Python 3.14.7 64-bit）
- A1 被动模型：通过
- A2 传感器与施力方向：通过
- A3 动力学模型与开环校验：完成
- A4 级联 PID 闭环站立：待开始

## 模型参数

| 符号 | 含义 | 值 |
|---|---|---:|
| `M` | 小车质量 | `1.00 kg` |
| `m` | 摆杆质量 | `0.24 kg` |
| `L` | 摆杆长度 | `0.50 m` |
| `l` | 铰点到摆杆质心距离 | `0.25 m` |
| `J_y` | 摆杆绕质心、平行于铰轴的转动惯量 | `0.00501 kg·m²` |
| — | 小车行程 | `-1.50 ～ +1.50 m` |
| `θ₀` | 摆杆初始倾角 | `+0.08 rad` |
| — | 仿真步长 | `8 ms` |

`J_y` 由均匀刚性杆 `m(L² + w²)/12` 计算，其中截面宽度 `w = 0.025 m`，约为 `0.00501 kg·m²`。

## 坐标与符号约定

- 世界坐标系：`ENU`，`+X` 向右，`+Y` 为铰轴方向，`+Z` 向上。
- 直立为 `θ = 0 rad`；杆顶向 `+X` 倾斜为正。
- 控制输入定义为小车沿 `+X` 的力 `F`，单位 `N`。
- `cart_position` 位置传感器单位为米；`pole_angle` 位置传感器单位为弧度。

## 文件结构

```text
cart-pole-webots/
  worlds/cart_pole.wbt                  # 当前 A2 世界
  controllers/cart_pole_probe/
    cart_pole_probe.py                  # A2 传感器/施力探针
  docs/
    a1-initial.png                      # A1 初始姿态
    a1-fall.png                         # A1 摆杆倒下
    a1-verification.txt                 # A1 数值摘要
    a1-probe-run1.csv                   # A1 8 ms 采样，第 1 次
    a1-probe-run2.csv                   # A1 8 ms 采样，第 2 次
    A1-acceptance.md                    # A1 验收记录
    A2-acceptance.md                    # A2 验收记录
    a2-positive.txt                     # A2 +2 N Console 输出
    a2-negative.txt                     # A2 -2 N Console 输出
    model.md                            # A3 动力学模型与开环校验
  README.md
```

## 运行方法：A2 默认正向测试

1. 使用 Webots R2025a，`File → Open World` 打开 `worlds/cart_pole.wbt`。
2. 确认 `controllerArgs` 为 `[ "2.0" ]`。
3. 先 `Pause`，再 `Reset Simulation`，确认时间为 `0:00:00:000`。
4. 切换 `Real-time` 并运行。控制器会：
   - 先空走一步，采集 `x0`、`theta0`；
   - 施加 `+2.0 N` 共 20 步（160 ms）；
   - 打印 `START` 和 `END`，随后把力设回 0 并继续空走。
5. 在底部 `Console` 查看两行输出，然后 `Pause`。

预期：

```text
START F=+2.00 N x≈0 m theta≈+0.08 rad
END   dx > 0
```

## 反向测试

1. 在 VS Code 中把 `controllerArgs` 改为 `[ "-2.0" ]`。
2. 保存后，在 Webots 中 `Reload World`（或重新打开世界）。
3. 按上面的步骤运行，确认 `START` 打印 `F=-2.00 N`，并且 `END` 的 `dx < 0`。

## A2 验收结果

正向 `F = +2.00 N`：

```text
START F=+2.00 N x=-0.00001 m theta=+0.08018 rad
END pulse=160 ms dx=+0.02350 m theta=+0.04243 rad
```

反向 `F = -2.00 N`：

```text
START F=-2.00 N x=-0.00001 m theta=+0.08018 rad
END pulse=160 ms dx=-0.02767 m theta=+0.20537 rad
```

两次初始 `x` 都接近 0，`θ` 都接近 `+0.08 rad`；`+2 N` 产生 `dx > 0`，`-2 N` 产生 `dx < 0`，方向正确。详细记录见 [docs/A2-acceptance.md](docs/A2-acceptance.md)。

## A3 动力学模型与开环校验

非线性模型：

```text
(M+m)x¨ + ml cosθ θ¨ - ml sinθ θdot² = F
Ip θ¨ + ml cosθ x¨ = mgl sinθ
```

其中 `Ip = Jy + ml² = 0.0200125 kg·m²`。用这组方程复算 A2 的 160 ms 脉冲：

| 脉冲 | Webots dx | 模型 dx | Webots 末端 θ | 模型末端 θ |
|---|---:|---:|---:|---:|
| `+2.00 N` | `+0.02350 m` | `+0.02237 m` | `+0.04243 rad` | `+0.04443 rad` |
| `-2.00 N` | `-0.02767 m` | `-0.02635 m` | `+0.20537 rad` | `+0.19913 rad` |

最大绝对误差：位移 `0.00132 m`，末端摆角 `0.00624 rad`。方向和量级一致，可作为控制器初始设计模型。

直立点线性化：

```text
A = [0  1   0       0;
     0  0  -1.6646  0;
     0  0   0       1;
     0  0  34.4024  0]
B = [0; 0.9433; 0; -2.8281]
```

开环正特征值约 `5.87 s⁻¹`，直立点不稳定。完整推导、假设和误差讨论见 [docs/model.md](docs/model.md)。

## A1 验收结果（历史记录）

A1 使用 `controller "<none>"` 的被动世界，验证结果如下：

| 检查项 | 实测结果 |
|---|---|
| 初始摆杆角度 | `+0.080175 rad`（约 `+4.59°`） |
| 2 s 时摆杆角度 | `+1.400000 rad`，绕 `(0, 1, 0)` 轴 |
| 首次到达 `+1.4 rad` 限位 | `0.624 s` |
| 小车 X | `0 → -0.043815 m`（向 `-X` 退约 `4.4 cm`） |
| 小车 Y | 全程 `0.000000 m` |
| 小车 Z | `0.079991 ～ 0.079999 m` |
| Console | 空，无解析错误 |
| 重置可复现 | 两次独立运行 CSV 字节完全一致 |

![A1 初始状态](docs/a1-initial.png)

![A1 摆杆倒下](docs/a1-fall.png)

详细记录见 [docs/A1-acceptance.md](docs/A1-acceptance.md)。

## 备注

- `HingeJoint` 的硬限位为 `±1.4 rad`；A1 中摆杆约 `0.624 s` 就到达 `+1.4 rad`，所以 1 s 截图看起来已经停住，这是模型限位。
- 该世界没有 `Background` 和地板，3D 背景为黑色是正常的；验收看轨道、小车和摆杆是否可见。
- 原始 `Viewpoint` 的 `orientation 1 0 0 1.2` 绕 X 轴滚转，视线仍沿 X 轴，导致相机在 `y=-3` 时看不到 `y=0` 的模型。A1 已修正 Viewpoint；模型参数未改动。
- A2 的 160 ms 脉冲后摆杆继续倒下是正常现象，A2 只验证传感器和施力方向，不要求摆杆保持直立。

## 下一步：A4

A4 只做级联 PID 的第一条闭环站立曲线：先用内环/外环结构把摆杆稳定在直立附近，再与 LQR 的响应做对比。
