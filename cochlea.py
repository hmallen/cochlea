import argparse
import i2c_lcd_driver
import json
import logging
from morse_keyer import MorseKeyer
import multiprocessing as mp
import os
from pprint import pprint
import speech_recognition as sr
import sys
import time

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

parser = argparse.ArgumentParser()
parser.add_argument('-e', '--energy_thresh', type=float, default=300, help='Energy threshold')
parser.add_argument('-d', '--dynamic_thresh', action='store_false', default=True, help='Dynamic energy threshold')
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

bcm_pin_servo = 18

lcd_delay = 1

# Initialize modules
lcd = i2c_lcd_driver.lcd()
recognizer = sr.Recognizer()
microphone = sr.Microphone(device_index=2, sample_rate=44100)
morse = MorseKeyer(bcm_pin_servo)


def lcd_display(display_string, line_number):
    if len(display_string) <= 16:
        lcd.lcd_display_string(display_string, line_number)
        time.sleep(lcd_delay)

    else:
        display_string = display_string + (' ' * 16)

        lcd.lcd_display_string(display_string, line_number)
        time.sleep(2.5)
        for x in range(0, (len(display_string) - 15)):
            display_text = display_string[x:(x+16)]
            lcd.lcd_display_string(display_text, line_number)
            time.sleep(0.15)


def microphone_speech_input():
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

    response = {
        'success': True,
        'error': None,
        'transcription': None
    }

    audio = None
    # adjust the recognizer sensitivity to ambient noise and record audio
    # from the microphone
    logger.debug('[BEFORE] recognizer.energy_threshold: ' + str(recognizer.energy_threshold))
    with microphone as source:
        if parameters['dynamic_energy_threshold'] is True:
            logger.debug('Adjusting for ambient noise.')
            lcd.lcd_clear()
            lcd_display('Recalibrating...', 1)
            recognizer.adjust_for_ambient_noise(source)#, duration=1)
            # time.sleep(1)
        logger.info('Speak now.')
        lcd_display('Speak now.', 2)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=30)
        except sr.WaitTimeoutError:
            logger.debug('Timed-out while waiting for microphone input.')
    logger.debug('[AFTER] recognizer.energy_threshold: ' + str(recognizer.energy_threshold))

    if audio != None:
        logger.info('Transcribing input speech.')
        lcd.lcd_clear()
        lcd_display('Transcribing...', 1)

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
    lcd.backlight(1)

    lcd_display('Speech-to-Morse', 1)
    lcd_display('Wait for prompt to speak.', 2)

    recognizer.energy_threshold = parameters['energy_threshold']
    recognizer.dynamic_energy_threshold = parameters['dynamic_energy_threshold']
    recognizer.pause_threshold = parameters['pause_threshold']

    try:
        while True:
                while True:
                    speech_input = microphone_speech_input()
                    if speech_input['transcription']:# or not speech_input['success']:
                        break
                    logger.info('Please repeat your last statement.')

                if speech_input['error']:
                    logger.error('Error: {}'.format(speech_input['error']))
                else:
                    print('Transcription: ' + speech_input['transcription'])
                    if speech_input['transcription'] == 'exit' or speech_input['transcription'] == 'quit':
                        logger.info('Exiting command received.')
                        lcd.lcd_clear()
                        lcd_display('Exiting program.')
                        break
                    else:
                        lcd.lcd_clear()
                        lcd_display('Transcription:', 1)
                        keyword_arguments = {
                            'display_string': speech_input['transcription'],
                            'line_number': 2
                        }
                        lcd_proc = mp.Process(target=lcd_display, args=tuple(), kwargs=keyword_arguments)
                        lcd_proc.start()

                        morse_input = morse.string_to_morse(speech_input['transcription'])
                        logger.debug('morse_input: ' + morse_input)
                        output_result = morse.output_morse(morse_input)
                        logger.debug('output_result: ' + str(output_result))

                        lcd_proc.join()
                        lcd.lcd_clear()

    except Exception as e:
        logger.exception(e)

    except KeyboardInterrupt:
        logger.info('Exit signal received.')
        # break

    finally:
        logger.info('Exiting.')
        lcd.lcd_clear()
        lcd.backlight(0)
