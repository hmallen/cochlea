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

morse_reference_file = 'morse_reference.json'


def recognize_speech_from_mic(recognizer, microphone):
    """Transcribe speech from recorded from 'microphone'.
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

    # adjust the recognizer sensitivity to ambient noise and record audio
    # from the microphone
    with microphone as source:
        logger.debug('Adjusting for ambient noise.')
        recognizer.adjust_for_ambient_noise(source)
        time.sleep(1)
        print('Speak now.')
        audio = recognizer.listen(source)

    logger.info('Transcribing input speech.')

    # set up the response object
    response = {
        'success': True,
        'error': None,
        'transcription': None
    }

    # try recognizing the speech in the recording
    # if a RequestError or UnknownValueError exception is caught,
    #     update the response object accordingly
    try:
        response['transcription'] = recognizer.recognize_google(audio)
    except sr.RequestError:
        # API was unreachable or unresponsive
        response['success'] = False
        response['error'] = 'API unavailable'
    except sr.UnknownValueError:
        # speech was unintelligible
        response['error'] = 'Unable to recognize speech'

    """
    try:
        response['transcription'] = recognizer.recognize_google_cloud(audio, credentials_json=gcs_credentials)
    except sr.UnknownValueError:
        logger.error('Google Cloud Speech could not understand audio.')
        response['success'] = False
        response['error'] = 'Unable to recognize speech.'
    except sr.RequestError as e:
        response['success'] = False
        response['error'] = 'API unavailable. Error: {0}'.format(e)
    """

    return response


if __name__ == '__main__':
    with open(morse_reference_file) as file:
        morse_reference = json.load(file)
    # pprint(morse_reference)

    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    while True:
        try:
            while True:
                speech_input = recognize_speech_from_mic(recognizer, microphone)
                if speech_input['transcription'] or not speech_input['success']:
                    break
                print('Please repeat your last statement.')

            if speech_input['error']:
                logger.error('Error: {}'.format(speech_input['error']))
            else:
                print('Transcription: ' + speech_input['transcription'])
                if speech_input['transcription'] == 'exit' or speech_input['transcription'] == 'quit':
                    print('Exiting program.')
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
            break

    logger.info('Exiting.')
