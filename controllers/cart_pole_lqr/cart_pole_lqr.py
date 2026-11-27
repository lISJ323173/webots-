import csv
import sys
from pathlib import Path

from controller import Robot


def clip(value, limit):
    return max(-limit, min(limit, value))


robot = Robot()
step_ms = int(robot.getBasicTimeStep())
dt = step_ms / 1000.0
motor = robot.getDevice("cart_motor")
cart = robot.getDevice("cart_position")
pole = robot.getDevice("pole_angle")
cart.enable(step_ms)
pole.enable(step_ms)

motor.setForce(0.0)
if robot.step(step_ms) == -1:
    raise SystemExit

prev_x, prev_theta = cart.getValue(), pole.getValue()
peak_x = tail_x = tail_theta = 0.0

mode = "lqr"
case = sys.argv[1] if len(sys.argv) > 1 else "step"
if case not in ("step", "pulse", "mass"):
    raise ValueError(f"Unknown test case: {case}")

log = Path(__file__).resolve().parents[2] / f"a6_{mode}_{case}.csv"
step_at = round(2.000 / dt)
pulse_at = round(4.000 / dt)
pulse_steps = round(0.080 / dt)

with log.open("w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["t_s", "x_ref_m", "x_m", "theta_rad", "disturbance_N", "force_N"])
    for k in range(round(10.0 / dt) + 1):
        t = k * dt
        x, theta = cart.getValue(), pole.getValue()
        v, omega = (x - prev_x) / dt, (theta - prev_theta) / dt
        prev_x, prev_theta = x, theta

        x_ref = 0.20 if case in ("step", "mass") and k >= step_at else 0.0
        x_error = x - x_ref
        disturbance = 3.0 if case == "pulse" and pulse_at <= k < pulse_at + pulse_steps else 0.0

        state = (x_error, v, theta, omega)
        gains = (-4.6918, -5.3978, -41.7045, -7.2396)
        force = clip(-sum(gain * value for gain, value in zip(gains, state)), 10.0)
        force = clip(force + disturbance, 10.0)
        writer.writerow([t, x_ref, x, theta, disturbance, force])
        peak_x = max(peak_x, abs(x))
        if t >= 8.0:
            tail_x = max(tail_x, abs(x_error))
            tail_theta = max(tail_theta, abs(theta))
        if k == 0:
            print(f"START mode={mode} case={case} theta={theta:+.4f} rad F={force:+.3f} N", flush=True)
        if t < 10.0:
            motor.setForce(force)
            if robot.step(step_ms) == -1:
                raise SystemExit

motor.setForce(0.0)
print(f"A6 mode={mode} case={case} peak_x={peak_x:.4f} m "
      f"tail_x={tail_x:.4f} m tail_theta={tail_theta:.4f} rad", flush=True)
while robot.step(step_ms) != -1:
    pass
