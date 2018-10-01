from gpiozero import AngularServo
import time


if __name__ == '__main__':
    servo = AngularServo(18)

    time.sleep(1)

    servo.angle = -90
    print('ang: ' + str(ang))

    time.sleep(3)

    start = time.time()
    servo.angle = 90
    while servo.angle < 90:
        pass
    end = time.time()

    duration = end - start
    print('duration: ' + str(duration))

    sec_per_deg = duration / 180
    print('sec_per_deg: ' + str(sec_per_deg))
