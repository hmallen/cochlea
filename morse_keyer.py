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

    #def __init__(self, bcm_pin, dot_delay=0.15, dash_delay=0.45, interkey_delay=0.15, interword_delay=1.05, angle_rest=0, angle_keyed=15, travel_delay=0.1):
    def __init__(self, bcm_pin, dot_delay=0.075, angle_rest=0, angle_keyed=15): #, travel_delay=0.1):
        self.dot_delay = dot_delay
        self.dash_delay = dot_delay * 3 #dash_delay

        self.interkey_delay = dot_delay #interkey_delay
        self.interword_delay = dot_delay * 7 #interword_delay

        self.angle_rest = angle_rest
        self.angle_keyed = angle_keyed

        self.travel_delay = dot_delay / 2

        self.servo = AngularServo(bcm_pin)
        self.servo.angle = self.angle_rest
        time.sleep(self.travel_delay)

    def string_to_morse(self, input_string):
        morse_output = ''
        for char in input_string:
            if char == ' ':
                morse_output += ' '
            else:
                morse_output += morse_reference[char.lower()]
        logger.debug('morse_output: ' + morse_output)

        return morse_output

    def output_morse(self, morse_string):
        output_return = {
            'success': True,
            'input': morse_string,
            'error': None
        }

        def key_press(key_type):
            if key_type == '.':
                self.servo.angle = self.angle_keyed
                time.sleep(self.travel_delay)

                time.sleep(self.dot_delay)

                self.servo.angle = self.angle_rest
                time.sleep(self.travel_delay)

            elif key_type == '-':
                self.servo.angle = self.angle_keyed
                time.sleep(self.travel_delay)

                time.sleep(self.dash_delay)

                self.servo.angle = self.angle_rest
                time.sleep(self.travel_delay)

            elif key_type == ' ':
                time.sleep(self.interword_delay)

            else:
                logger.error('Unrecognized key_type in output_morse.key_press().')

        try:
            for char in morse_string:
                key_press(char)
                time.sleep(self.interkey_delay)

        except Exception as e:
            logger.exception(e)
            output_return['success'] = False
            output_return['error'] = str(e)

        finally:
            return output_return


if __name__ == '__main__':
    morse = MorseKeyer(servo_pin)

    morse_input = morse.string_to_morse('Hello, world!')
    logger.debug('morse_input: ' + morse_input)

    output_result = morse.output_morse(morse_input)
    logger.debug('output_result: ' + str(output_result))

    if output_result['success'] is False:
        print('Error: ' + output_result['error'])
