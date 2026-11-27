# A6 验收记录：PID 与 LQR 同工况对比

## 基本信息

- 日期：2026-11-27
- Webots：R2025a
- 步长：`8 ms`
- 记录时长：`10 s`
- 初始角：`+0.08 rad`
- 力限幅：`±10 N`
- 基础世界：`worlds/cart_pole.wbt`（摆杆 `0.24 kg`）
- 质量摄动世界：`worlds/cart_pole_mass.wbt`（摆杆 `0.30 kg`，+25%）

## 测试矩阵

| 工况 | 世界设置 | 输入 |
|---|---|---|
| `step` | 摆杆 `0.24 kg` | `t = 2.000 s` 时位置目标从 `0` 跳到 `+0.20 m` |
| `pulse` | 摆杆 `0.24 kg` | 位置目标保持 `0`；`t = 4.000 s` 起叠加 `+3 N`，持续 `80 ms` |
| `mass` | 摆杆 `0.30 kg` | 重复 `step` 的 `+0.20 m` 位置阶跃 |

每种工况分别运行 PID 和 LQR，控制器参数保持不变。

## 控制与记录

- PID：A4 的级联 PD-PID，位置外环使用 `x_error = x - x_ref`。
- LQR：A5 的增益 `K = [-4.6918, -5.3978, -41.7045, -7.2396]`，状态使用 `(x_error, v, theta, omega)`。
- 两种控制器都在基础力上叠加扰动：`force = clip(force + disturbance, 10 N)`。
- CSV 列：`t_s, x_ref_m, x_m, theta_rad, disturbance_N, force_N`。
- `tail_x` / `tail_theta` 为 `t ≥ 8 s` 时间窗内 `|x - x_ref|` / `|θ|` 的最大值。

## 六组汇总

```text
A6 mode=pid case=step  peak_x=0.1943 m tail_x=0.0059 m tail_theta=0.0003 rad
A6 mode=lqr case=step  peak_x=0.2058 m tail_x=0.0028 m tail_theta=0.0003 rad
A6 mode=pid case=pulse peak_x=0.0934 m tail_x=0.0056 m tail_theta=0.0005 rad
A6 mode=lqr case=pulse peak_x=0.0985 m tail_x=0.0012 m tail_theta=0.0002 rad
A6 mode=pid case=mass  peak_x=0.1941 m tail_x=0.0062 m tail_theta=0.0003 rad
A6 mode=lqr case=mass  peak_x=0.2050 m tail_x=0.0024 m tail_theta=0.0003 rad
```

首拍输出：

| 工况 | PID `START F` | LQR `START F` |
|---|---:|---:|
| `step` | `+3.742 N` | `+3.344 N` |
| `pulse` | `+3.742 N` | `+3.344 N` |
| `mass` | `+3.742 N` | `+3.344 N` |

## 验收判定

统一通过线：

- 跑满 `10 s`，摆杆不倒、不碰关节限位；
- 最后 2 s：`|x - x_ref| ≤ 0.02 m`，`|θ| ≤ 0.02 rad`；
- `pulse` 组恰好有 10 个连续样本 `disturbance_N = 3.0`。

| 工况 | 控制器 | 时长 | 最大 `|θ|` (rad) | `tail_x` (m) | `tail_theta` (rad) | 结果 |
|---|---|---:|---:|---:|---:|---|
| `step` | PID | 10 s | `0.080175` | `0.005933` | `0.000280` | 通过 |
| `step` | LQR | 10 s | `0.080175` | `0.002826` | `0.000334` | 通过 |
| `pulse` | PID | 10 s | `0.080175` | `0.005566` | `0.000532` | 通过 |
| `pulse` | LQR | 10 s | `0.080175` | `0.001193` | `0.000173` | 通过 |
| `mass` | PID | 10 s | `0.080181` | `0.006208` | `0.000308` | 通过 |
| `mass` | LQR | 10 s | `0.080181` | `0.002435` | `0.000292` | 通过 |

- 六组 CSV 均为 1251 行，覆盖 `0.000 ～ 10.000 s`。
- 六组最大 `|θ| ≈ 0.08018 rad`，没有接近 `±1.4 rad` 限位。
- 六组最大 `|F|` 在 `3.34 ～ 3.75 N` 之间，没有持续饱和。
- `pulse` 两组的 `disturbance_N = 3.0` 均为恰好 10 个连续样本，符合 `80 ms / 8 ms`。

## 初步观察

- 三个工况下，LQR 的 `tail_x` 都小于 PID：`step` 为 `0.0028` 对 `0.0059`，`pulse` 为 `0.0012` 对 `0.0056`，`mass` 为 `0.0024` 对 `0.0062`。
- `step` / `mass` 的 `peak_x` 略高于 `0.20 m` 目标：LQR 约 `0.205`，PID 约 `0.194`；这里 `peak_x` 是绝对位置，不是误差，因此不直接代表超调量。
- LQR 的首拍力和最大力略小（`3.344 N` 对 `3.742 N`）。
- 完整的调节时间、超调量和曲线对比留到下一轮，用六份 CSV 统一生成。

## 结论

**PASS**

`A6：六组全部通过｜PID/LQR × step/pulse/mass｜tail_x ≤ 0.0062 m｜tail_theta ≤ 0.00053 rad`

## 证据

- `docs/a6_pid_step.txt`、`docs/a6_lqr_step.txt`
- `docs/a6_pid_pulse.txt`、`docs/a6_lqr_pulse.txt`
- `docs/a6_pid_mass.txt`、`docs/a6_lqr_mass.txt`
- `a6_pid_step.csv`、`a6_lqr_step.csv`
- `a6_pid_pulse.csv`、`a6_lqr_pulse.csv`
- `a6_pid_mass.csv`、`a6_lqr_mass.csv`

## 备注

- 质量摄动世界只改摆杆质量 `0.24 → 0.30 kg`，小车仍为 `1.00 kg`；控制器增益不重新整定。
- 六次运行均从磁盘重新加载世界，初始角保持 `+0.08 rad`。
- 世界文件默认：`cart_pole.wbt` 使用 LQR + `step`，`cart_pole_mass.wbt` 使用 LQR + `mass`。
