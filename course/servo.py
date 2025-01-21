from servo import Servo, servo2040
import time

print(2+2)

s = Servo(servo2040.SERVO_1)
s.enable()
time.sleep(0.5)
s.to_min()
time.sleep(0.5)
s.to_mid()
time.sleep(0.5)
s.to_max()