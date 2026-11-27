import csv
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
log = Path(__file__).resolve().parents[2] / "a5_lqr_balance.csv"

with log.open("w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["t_s", "x_m", "theta_rad", "force_N"])
    for k in range(round(10.0 / dt) + 1):
        t = k * dt
        x, theta = cart.getValue(), pole.getValue()
        v, omega = (x - prev_x) / dt, (theta - prev_theta) / dt
        prev_x, prev_theta = x, theta

        state = (x, v, theta, omega)
        gains = (-4.6918, -5.3978, -41.7045, -7.2396)
        force = clip(-sum(k * s for k, s in zip(gains, state)), 10.0)
        writer.writerow([t, x, theta, force])
        peak_x = max(peak_x, abs(x))
        if t >= 8.0:
            tail_x = max(tail_x, abs(x))
            tail_theta = max(tail_theta, abs(theta))
        if k == 0:
            print(f"START theta={theta:+.4f} rad F={force:+.3f} N", flush=True)
        if t < 10.0:
            motor.setForce(force)
            if robot.step(step_ms) == -1:
                raise SystemExit

motor.setForce(0.0)
print(f"A5 peak_x={peak_x:.4f} m tail_x={tail_x:.4f} m "
      f"tail_theta={tail_theta:.4f} rad", flush=True)
while robot.step(step_ms) != -1:
    pass
