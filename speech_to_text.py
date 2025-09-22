import logging
import speech_recognition as sr
from pydub import AudioSegment
from pydub.utils import which
from io import BytesIO

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ✅ Tell pydub where ffmpeg is
AudioSegment.converter = which("ffmpeg") or r"C:\Users\LENOVO\Downloads\ffmpeg-2025-09-08-git-45db6945e9-full_build\ffmpeg-2025-09-08-git-45db6945e9-full_build\bin\ffmpeg.exe"

def record_audio(file_path, timeout=20, phrase_time_limit=None):
    """
    Record audio from the microphone and save it as an MP3 file.

    Args:
        file_path (str): Path to save the recorded audio file.
        timeout (int): Maximum time to wait for a phrase to start (in seconds).
        phrase_time_limit (int): Maximum time for the phrase to be recorded (in seconds).
    """
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            logging.info("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            logging.info("Start speaking now...")

            # Record the audio
            audio_data = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            logging.info("Recording complete.")

            # Convert the recorded audio to an MP3 file
            wav_data = audio_data.get_wav_data()
            audio_segment = AudioSegment.from_wav(BytesIO(wav_data))
            audio_segment.export(file_path, format="mp3", bitrate="128k")

            logging.info(f"✅ Audio saved to {file_path}")

    except Exception as e:
        logging.error(f"❌ An error occurred: {e}")


if __name__ == "__main__":
    file_path = "test_txt_to_S.mp3"
    record_audio(file_path)


import os
from groq import Groq


def transcribe_with_groq(audio_filepath):
    GROQ_API_KEY="REMOVED_SECRETuHxFC"
    client=Groq(api_key=GROQ_API_KEY)
    stt_model="whisper-large-v3"
    audio_file=open(audio_filepath, "rb")
    transcription=client.audio.transcriptions.create(
        model=stt_model,
        file=audio_file,
        language="en"
    )

    return transcription.text

audio_filepath = "test_txt_to_S.mp3"
print(transcribe_with_groq(audio_filepath))