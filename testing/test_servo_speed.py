from gpiozero import AngularServo
import time


if __name__ == '__main__':
    servo = AngularServo(18)

    time.sleep(1)

    servo.angle = -90

    time.sleep(1)

    start = time.time()
    servo.angle = 90
    while True:
        ang = servo.angle
        print(ang)
        if servo.angle == 90:
            break
    end = time.time()

    duration = end - start
    print('duration: ' + str(duration))

    sec_per_deg = duration / 180
    print('sec_per_deg: ' + str(sec_per_deg))

    time.sleep(3)

    servo.angle = -90
    servo.angle = 90
    servo.angle = -90
