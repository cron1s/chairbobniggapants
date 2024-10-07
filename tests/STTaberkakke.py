import sounddevice as sd
import numpy as np
import whisper
import queue
import sys

model = whisper.load_model("base")
SAMPLE_RATE = 16000
BLOCK_SIZE = 16000  
CHANNELS = 1


audio_queue = queue.Queue()


DB_THRESHOLD = -40  
def rms(data):
    """Calculate the Root Mean Square of the audio data."""
    return np.sqrt(np.mean(np.square(data)))

def db_from_rms(rms_value):
    """Convert RMS value to decibels."""
    return 20 * np.log10(rms_value) if rms_value > 0 else -np.inf
def callback(indata, frames, time, status):
    if status:
        print(f"Audio callback status: {status}", file=sys.stderr)
    
    audio_rms = rms(indata)
    audio_db = db_from_rms(audio_rms)


    if audio_db > DB_THRESHOLD:
        audio_queue.put(indata.copy())

with sd.InputStream(callback=callback, channels=CHANNELS, samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE):
    print("Listening and transcribing... Press Ctrl+C to stop.")

    try:
        while True:
            audio_block = audio_queue.get()
            audio_data = np.squeeze(audio_block)
            result = model.transcribe(audio_data, fp16=False, language="de")
            print(result['text'])

    except KeyboardInterrupt:
        print("Transcription stopped.")
