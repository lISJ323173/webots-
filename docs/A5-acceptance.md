# A5 验收记录：离散 LQR 站立

## 基本信息

- 日期：2026-11-27
- Webots：R2025a
- 世界文件：`worlds/cart_pole.wbt`
- 控制器：`controllers/cart_pole_lqr/cart_pole_lqr.py`
- 控制周期：`8 ms`
- 记录时长：`10 s`
- 数据文件：`a5_lqr_balance.csv`（项目根目录）

## 控制律

状态顺序沿用 A3：

$$
\mathbf{s} = [x,\ \dot x,\ \theta,\ \dot\theta]^\mathsf{T}
$$

连续模型按 `8 ms` 零阶保持离散化，取：

$$
Q = \operatorname{diag}(25, 1, 120, 2), \qquad R = 1
$$

离散 LQR 增益：

$$
K = [-4.6918,\ -5.3978,\ -41.7045,\ -7.2396]
$$

控制力：

$$
F = \operatorname{clip}(-K\mathbf{s},\ \pm10\ \mathrm{N})
$$

速度 `\dot x` 和角速度 `\dot\theta` 由相邻采样差分得到，`dt = 0.008 s`。

## 世界修改

- `Robot.controller` 改为 `cart_pole_lqr`。
- 删除 A2 的 `controllerArgs`。
- 保留 `cart_motor`、`cart_position`、`pole_angle`。
- 摆杆初始角保持 `+0.08 rad`，其他参数不变。

## 运行方法

1. 从磁盘重新打开 `worlds/cart_pole.wbt`。
2. `Pause` → `Reset Simulation`，确认时间为 `0:00:00:000`。
3. 使用 `Real-time` 或 `Fast` 运行 10 s。
4. Console 出现 `A5` 汇总行后 `Pause`。
5. 项目根目录生成 `a5_lqr_balance.csv`。

## Console 结果

```text
INFO: cart_pole_lqr: Starting controller: python.exe -u cart_pole_lqr.py
START theta=+0.0802 rad F=+3.344 N
A5 peak_x=0.0985 m tail_x=0.0022 m tail_theta=0.0003 rad
```

## 指标核对

| 检查项 | 通过标准 | 实测 | 结果 |
|---|---|---|---|
| 初始角度 | 接近 `+0.08 rad` | `+0.08018 rad` | 通过 |
| 首拍力方向 | `F > 0 N` | `+3.344 N` | 通过 |
| 记录时长 | 撑满 `10 s` | `0.000 ～ 10.000 s`，1251 行 | 通过 |
| 摆杆不倒 | 不碰 `±1.4 rad` 限位 | 最大 `|θ| = 0.08018 rad` | 通过 |
| 小车峰值 | `peak_x ≤ 0.30 m` | `0.09852 m` | 通过 |
| 最后 2 s 小车 | `tail_x ≤ 0.05 m` | `0.00224 m` | 通过 |
| 最后 2 s 摆角 | `tail_theta ≤ 0.02 rad` | `0.00027 rad` | 通过 |
| 力饱和 | 不应持续饱和 | 最大 `|F| = 3.344 N < 10 N` | 通过 |

## 与 A4 的初步对照

| 指标 | A4 级联 PD-PID | A5 LQR |
|---|---:|---:|
| 首拍力 | `+3.742 N` | `+3.344 N` |
| `peak_x` | `0.0934 m` | `0.0985 m` |
| `tail_x` | `0.0004 m` | `0.0022 m` |
| `tail_theta` | `0.0002 rad` | `0.0003 rad` |
| 最大 `|F|` | `3.742 N` | `3.344 N` |

两种控制器都通过 A4/A5 的站立验收线。就这一次同工况而言，PID 的峰值和尾段位置误差更小，LQR 的首拍力和最大力略小；完整的位置阶跃和扰动对比留到下一轮。

## 结论

**PASS**

`A5：LQR 站立成功｜首拍 F=+3.344 N｜peak_x=0.0985 m｜tail_x=0.0022 m｜tail_theta=0.0003 rad`

## 证据

- `docs/a5-console.txt`：Console 原始输出
- `a5_lqr_balance.csv`：10 s、8 ms 采样数据
- `controllers/cart_pole_lqr/cart_pole_lqr.py`：LQR 控制器源码
- `a4_pid_balance.csv`：A4 对照数据

## 备注

- 首拍 `+3.344 N` 与 A3 非线性模型预估的 `+3.34 N` 一致。
- 最大力 `3.344 N` 未达到 `±10 N` 限幅。
- 本轮只做同一初始姿态的站立复跑；位置阶跃和扰动测试下一轮再做。
