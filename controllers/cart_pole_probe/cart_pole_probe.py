import sys
from controller import Robot

robot = Robot()
step_ms = int(robot.getBasicTimeStep())
force_n = float(sys.argv[1]) if len(sys.argv) > 1 else 2.0

motor = robot.getDevice("cart_motor")
cart = robot.getDevice("cart_position")
pole = robot.getDevice("pole_angle")
cart.enable(step_ms)
pole.enable(step_ms)

motor.setForce(0.0)
if robot.step(step_ms) == -1:
    raise SystemExit

x0 = cart.getValue()
theta0 = pole.getValue()
print(f"START F={force_n:+.2f} N x={x0:+.5f} m "
      f"theta={theta0:+.5f} rad", flush=True)

motor.setForce(force_n)
for _ in range(20):
    if robot.step(step_ms) == -1:
        raise SystemExit

motor.setForce(0.0)
print(f"END pulse={20 * step_ms} ms "
      f"dx={cart.getValue() - x0:+.5f} m "
      f"theta={pole.getValue():+.5f} rad", flush=True)

while robot.step(step_ms) != -1:
    pass
