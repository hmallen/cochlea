import json
import logging
from gpiozero import AngularServo
import time

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

servo_pin = 18  # BCM pin number of servo

morse_reference_file = 'morse_reference.json'

with open(morse_reference_file) as file:
    morse_reference = json.load(file)


class MorseKeyer:

    def __init__(self, bcm_pin, interkey_delay=0.1, interword_delay=1, dash_delay=0.5, angle_rest=0, angle_keyed=15, travel_delay=0.1):
        self.interkey_delay = interkey_delay
        self.interword_delay = interword_delay
        self.dash_delay = dash_delay
        self.angle_rest = angle_rest
        self.angle_keyed = angle_keyed
        self.travel_delay = travel_delay

        self.servo = AngularServo(bcm_pin)
        self.servo.angle = self.angle_rest

    def output_morse(self, input_string):

        def key_press(key_type):
            if key_type == '.':
                self.servo.angle = self.angle_keyed
                time.sleep(self.travel_delay)
                # while self.servo.angle < self.angle_keyed:
                    # pass
                # print(self.servo.angle)
                self.servo.angle = self.angle_rest
                time.sleep(self.travel_delay)
                # while self.servo.angle > self.angle_rest:
                    # pass
                # print(self.servo.angle)

            elif key_type == '-':
                self.servo.angle = self.angle_keyed
                time.sleep(self.travel_delay)
                # while self.servo.angle < self.angle_keyed:
                    # pass
                # print(self.servo.angle)
                time.sleep(self.dash_delay)
                self.servo.angle = self.angle_rest
                time.sleep(self.travel_delay)
                # while self.servo.angle > self.angle_rest:
                    # pass
                # print(self.servo.angle)

            elif key_type == ' ':
                time.sleep(self.interword_delay)

            else:
                logger.error('Unrecognized key_type in output_morse.key_press().')

        morse_output = ''
        for char in input_string:
            if char == ' ':
                morse_output += ' '
            else:
                morse_output += morse_reference[char.lower()]
        logger.debug('morse_output: ' + morse_output)

        for char in morse_output:
            key_press(char)
            time.sleep(self.interkey_delay)


if __name__ == '__main__':
    morse = MorseKeyer(servo_pin)
    morse_test = 'hello world'
    morse.output_morse(morse_test)
