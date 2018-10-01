import argparse
import i2c_lcd_driver
import json
import logging
import os
from pprint import pprint
import speech_recognition as sr
import sys
import time

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

parser = argparse.ArgumentParser()
parser.add_argument('-e', '--energy_thresh', type=float, default=100, help='Energy threshold')
parser.add_argument('-d', '--dynamic_thresh', type=bool, default=True, help='Dynamic energy threshold')
parser.add_argument('-p', '--pause_thresh', type=float, default=0.5, help='Pause threshold')
args = parser.parse_args()

parameters = {
    'energy_threshold': args.energy_thresh,
    'dynamic_energy_threshold': args.dynamic_thresh,
    'pause_threshold': args.pause_thresh
}

logger.debug('parameters: ' + str(parameters))

morse_reference_file = 'morse_reference.json'

with open(morse_reference_file) as file:
    morse_reference = json.load(file)


def lcd_display(lcd, display_string, line_number):
    if len(display_string) <= 16:
        lcd.lcd_display_string(display_string, line_number)

    else:
        display_string = display_string + (' ' * 16)

        lcd.lcd_display_string(display_string, line_number)
        time.sleep(2.5)
        for x in range(0, (len(display_string) - 16)):
            display_text = display_string[x:(x+16)]
            lcd.lcd_display_string(display_text, line_number)
            time.sleep(0.15)


def microphone_speech_input(recognizer, microphone, lcd):
    """Transcribe speech from recorded from microphone.
    Returns a dictionary with three keys:
    'success': a boolean indicating whether or not the API request was
               successful.
    'error':   'None' if no error occured, otherwise a string containing
               an error message if the API could not be reached or
               speech was unrecognizable.
    'transcription': 'None' if speech could not be transcribed,
               otherwise a string containing the transcribed text.
    """

    # check that recognizer and microphone arguments are appropriate type
    # if not isinstance(recognizer, sr.Recognizer):
        # raise TypeError('The "recognizer" object must be a "Recognizer" instance.')

    # if not isinstance(microphone, sr.Microphone):
        # raise TypeError('The "microphone" object must be a "Microphone" instance.')

    audio = None
    # adjust the recognizer sensitivity to ambient noise and record audio
    # from the microphone
    logger.debug('[BEFORE] recognizer.energy_threshold: ' + str(recognizer.energy_threshold))
    with microphone as source:
        logger.debug('Adjusting for ambient noise.')
        recognizer.adjust_for_ambient_noise(source, duration=1)
        # time.sleep(1)
        print('Speak now.')
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=15)
        except Exception as e:
            logger.exception(e)
    logger.debug('[AFTER] recognizer.energy_threshold: ' + str(recognizer.energy_threshold))

    logger.info('Transcribing input speech.')

    # set up the response object
    response = {
        'success': True,
        'error': None,
        'transcription': None
    }

    if audio != None:
        # try recognizing the speech in the recording
        # if a RequestError or UnknownValueError exception is caught,
        #     update the response object accordingly
        try:
            response['transcription'] = recognizer.recognize_google(audio)
        except sr.RequestError:
            # API was unreachable or unresponsive
            response['success'] = False
            response['error'] = 'API unavailable.'
        except sr.UnknownValueError:
            # speech was unintelligible
            response['error'] = 'Unable to recognize speech.'

    else:
        response['success'] = False
        response['error'] = 'No audio recorded.'

    return response


if __name__ == '__main__':
    lcd = i2c_lcd_driver.lcd()
    lcd.backlight(1)

    lcd_display(lcd, 'Speech-to-Morse', 1)
    # lcd_display(lcd, 'When prompted, speak sentence for translation.', 2)

    recognizer = sr.Recognizer()
    recognizer.energy_threshold = parameters['energy_threshold']
    recognizer.dynamic_energy_threshold = parameters['dynamic_energy_threshold']
    recognizer.pause_threshold = parameters['pause_threshold']
    microphone = sr.Microphone(device_index=2)

    try:
        while True:
                while True:
                    speech_input = microphone_speech_input(recognizer, microphone, lcd)
                    if speech_input['transcription'] or not speech_input['success']:
                        break
                    print('Please repeat your last statement.')

                if speech_input['error']:
                    logger.error('Error: {}'.format(speech_input['error']))
                else:
                    print('Transcription: ' + speech_input['transcription'])
                    if speech_input['transcription'] == 'exit' or speech_input['transcription'] == 'quit':
                        logger.info('Exiting command received.')
                        break
                    else:
                        morse_output = ''
                        for char in speech_input['transcription']:
                            if char == ' ':
                                morse_output += ' '
                            else:
                                morse_output += '(' + morse_reference[char.lower()] + ')'
                        print('Morse: ' + morse_output)

    except Exception as e:
        logger.exception(e)

    except KeyboardInterrupt:
        logger.info('Exit signal received.')
        # break

    finally:
        logger.info('Exiting.')
        lcd.lcd_clear()
        lcd.backlight(0)
