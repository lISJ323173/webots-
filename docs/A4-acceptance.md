# A4 验收记录：级联 PD-PID 站立

## 基本信息

- 日期：2026-11-27
- Webots：R2025a
- 世界文件：`worlds/cart_pole.wbt`
- 控制器：`controllers/cart_pole_pid/cart_pole_pid.py`
- 控制周期：`8 ms`
- 记录时长：`10 s`
- 数据文件：`a4_pid_balance.csv`（项目根目录）

## 控制结构

位置外环 PD：

$$
\theta_{\mathrm{ref}} = \operatorname{clip}(-0.0868x - 0.1403\dot x,\ \pm0.15)
$$

角度内环 PID：

$$
e = \theta - \theta_{\mathrm{ref}}
$$

$$
F = \operatorname{clip}(46.66e + 8.23\dot\theta + 1.0\int e\,dt,\ \pm10)
$$

- 微分项使用实测角速度 `\dot\theta`。
- 积分限幅：`±0.25 rad·s`。
- 力限幅：`±10 N`。
- 内环误差为实测角度减目标角度，`e = θ - θ_ref`。

## 世界修改

- `Robot.controller` 改为 `cart_pole_pid`。
- 删除 A2 的 `controllerArgs`。
- 保留 `LinearMotor { name "cart_motor" maxForce 10 }`。
- 保留 `cart_position`、`pole_angle` 两个 PositionSensor。
- 保留摆杆初始角 `+0.08 rad`，`HingeJoint` 仍为被动关节。

## 运行方法

1. 从磁盘重新打开 `worlds/cart_pole.wbt`。
2. `Pause` → `Reset Simulation`，确认时间为 `0:00:00:000`。
3. 使用 `Real-time` 或 `Fast` 运行，控制器会记录 10 s 数据。
4. Console 出现 `A4` 汇总行后 `Pause`。
5. 项目根目录生成 `a4_pid_balance.csv`。

## Console 结果

```text
INFO: cart_pole_pid: Starting controller: python.exe -u cart_pole_pid.py
START theta=+0.0802 rad F=+3.742 N
A4 peak_x=0.0934 m tail_x=0.0004 m tail_theta=0.0002 rad
```

## 指标核对

| 检查项 | 通过标准 | 实测 | 结果 |
|---|---|---|---|
| 初始角度 | 接近 `+0.08 rad` | `+0.08018 rad` | 通过 |
| 首拍力方向 | `F > 0 N` | `+3.742 N` | 通过 |
| 记录时长 | 撑满 `10 s` | `0.000 ～ 10.000 s`，1251 行 | 通过 |
| 摆杆不倒 | 不碰 `±1.4 rad` 限位 | 最大 `|θ| = 0.08018 rad` | 通过 |
| 小车峰值 | `peak_x ≤ 0.30 m` | `0.09343 m` | 通过 |
| 最后 2 s 小车 | `tail_x ≤ 0.05 m` | `0.00044 m` | 通过 |
| 最后 2 s 摆角 | `tail_theta ≤ 0.02 rad` | `0.00023 rad` | 通过 |
| 力饱和 | 不应持续饱和 | 最大 `|F| = 3.742 N < 10 N` | 通过 |

`tail_x` / `tail_theta` 是 `t ≥ 8 s` 时间窗内 `|x|` / `|θ|` 的最大值。

## 结论

**PASS**

`A4：级联 PD-PID 站立成功｜首拍 F=+3.742 N｜peak_x=0.0934 m｜tail_x=0.0004 m｜tail_theta=0.0002 rad`

## 证据

- `docs/a4-console.txt`：Console 原始输出
- `a4_pid_balance.csv`：10 s、8 ms 采样数据
- `controllers/cart_pole_pid/cart_pole_pid.py`：控制器源码

## 备注

- 本轮只验收站立；位置阶跃和扰动测试留到 LQR 与 PID 对比时进行。
- 首拍 `+3.742 N` 与 A3 非线性模型预估的 `+3.74 N` 一致。
- 最大力 `3.742 N` 未达到 `±10 N` 限幅，说明该工况下控制器没有靠饱和硬撑。
