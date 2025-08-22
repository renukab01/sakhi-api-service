import time
import io
from logger import logger
from pydub import AudioSegment

from env_manager import translate_class as translator
from utils import get_from_env_or_config

DEFAULT_LANGAUGE = get_from_env_or_config('default', 'language_default', None)

def process_incoming_voice(file_url, input_language):
    """
    Main Function for processing audio based queries
    """
    error_message = None
    try:
        regional_text = translator.speech_to_text(file_url, input_language)
        try:
            english_text = translator.translate_text(text=regional_text, source=input_language, destination=DEFAULT_LANGAUGE)
        except Exception as e:
            error_message = "Indic translation to English failed"
            logger.error(f"Exception occurred: {e}", exc_info=True)
            english_text = None
    except Exception as e:
        error_message = "Speech to text conversion API failed"
        logger.error(f"Exception occurred: {e}", exc_info=True)
        regional_text = None
        english_text = None
    return regional_text, english_text, error_message


def process_incoming_text(regional_text, input_language):
    """
    Main function for processing text queries
    """
    error_message = None
    try:
        english_text = translator.translate_text(text=regional_text, source=input_language, destination=DEFAULT_LANGAUGE)
    except Exception as e:
        error_message = "Indic translation to English failed"
        english_text = None
        logger.error(f"Exception occurred: {e}", exc_info=True)
    return english_text, error_message


def process_outgoing_text(english_text, input_language):
    """
    Main func for generating text response
    """
    error_message = None
    try:
        regional_text = translator.translate_text(text=english_text, source=DEFAULT_LANGAUGE, destination=input_language)
    except Exception as e:
        error_message = "English translation to indic language failed"
        logger.error(f"Exception occurred: {e}", exc_info=True)
        regional_text = None
    return regional_text, error_message


def process_outgoing_voice(message, input_language, prefix=""):
    """
    Main function for generating audio response completely in-memory.
    Converts text to speech (WAV), then converts WAV to MP3 in RAM.
    Returns an in-memory file buffer and a generated filename.
    """
    input_language="hi"
    error_message = None
    decoded_audio_content = translator.text_to_speech(language=input_language, text=message)

    if decoded_audio_content:
        logger.info("Received WAV audio content from Bhashini. Converting to MP3 in-memory.")
        try:
            wav_file_in_memory = io.BytesIO(decoded_audio_content)
            audio = AudioSegment.from_wav(wav_file_in_memory)

            mp3_file_in_memory = io.BytesIO()

            audio.export(mp3_file_in_memory, format="mp3")

            time_stamp = time.strftime("%Y%m%d-%H%M%S")
            if prefix != "":
                output_mp3_filename = f"{prefix}-{time_stamp}.mp3"
            else:
                output_mp3_filename = f"audio-output-{time_stamp}.mp3"
            
            logger.info("In-memory MP3 conversion successful.")
            return mp3_file_in_memory, output_mp3_filename, None

        except Exception as e:
            error_message = f"Failed during in-memory audio conversion: {e}"
            logger.error(error_message, exc_info=True)
            return None, None, error_message

    error_message = "Text to Audio conversion failed (did not receive content from Bhashini)"
    logger.error(error_message)
    return None, None, error_message