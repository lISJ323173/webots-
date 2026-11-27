# A2 验收记录：传感器读取与施力方向

## 基本信息

- 日期：2026-11-27
- Webots：R2025a
- 世界文件：`worlds/cart_pole.wbt`
- 控制器：`controllers/cart_pole_probe/cart_pole_probe.py`
- 仿真步长：`8 ms`
- 脉冲长度：`20 × 8 ms = 160 ms`

## 目标

验证 Python 控制器能够：

1. 读取小车位置 `x`（`cart_position`，单位 m）。
2. 读取摆杆角度 `θ`（`pole_angle`，单位 rad）。
3. 通过 `LinearMotor` 对小车施加正、负方向的力，并确认 `dx` 的符号正确。

## 世界修改

- 根 `Robot`：

```text
controller "cart_pole_probe"
controllerArgs [ "2.0" ]
```

- `SliderJoint` 的 `device` 增加线性电机：

```text
device [
  LinearMotor { name "cart_motor" maxForce 10 }
  PositionSensor { name "cart_position" }
]
```

- `HingeJoint` 保持被动，只保留 `PositionSensor { name "pole_angle" }`。

## 控制器行为

1. `setForce(0)`，先走一步采集 `x0`、`theta0`。
2. 打印 `START` 行。
3. `setForce(force_n)`，连续走 20 步（160 ms）。
4. `setForce(0)`，打印 `END` 行，之后继续空走。

两次测试都从磁盘重新打开世界，确保从初始姿态开始。

## 测试结果

### 正向：`F = +2.00 N`

```text
START F=+2.00 N x=-0.00001 m theta=+0.08018 rad
END pulse=160 ms dx=+0.02350 m theta=+0.04243 rad
```

- 初始 `x ≈ 0 m`，`θ ≈ +0.08 rad`。
- `dx = +0.02350 m > 0`，正向力使小车向 `+X` 移动。

### 反向：`F = -2.00 N`

```text
START F=-2.00 N x=-0.00001 m theta=+0.08018 rad
END pulse=160 ms dx=-0.02767 m theta=+0.20537 rad
```

- 初始 `x ≈ 0 m`，`θ ≈ +0.08 rad`。
- `dx = -0.02767 m < 0`，反向力使小车向 `-X` 移动。

## 判定

| 检查项 | 正向 | 反向 |
|---|---|---|
| 初始 x 接近 0 | 通过 | 通过 |
| 初始 θ 接近 +0.08 rad | 通过 | 通过 |
| dx 符号 | `+0.02350 m > 0` | `-0.02767 m < 0` |
| 控制器启动 | 通过 | 通过 |

结论：**PASS**。传感器读取正常，`+2 N` 和 `-2 N` 产生的位移方向相反且符合世界坐标约定。

## 证据

- `docs/a2-positive.txt`：正向 Console 输出
- `docs/a2-negative.txt`：反向 Console 输出

## 备注

- 160 ms 脉冲后摆杆继续倒下是正常现象；A2 只验证传感器和施力方向。
- 正向脉冲期间 `θ` 从 `+0.08018` 变为 `+0.04243`，反向脉冲后变为 `+0.20537`；这是小车加速度对摆杆的惯性影响，不作为 A2 的通过条件。
- 世界文件默认 `controllerArgs` 已恢复为 `[ "2.0" ]`，便于从正向测试开始。
