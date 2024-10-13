import sounddevice as sd
import numpy as np
import whisper
import queue
import sys
import torch
import warnings


warnings.filterwarnings("ignore", category=UserWarning)

model = whisper.load_model("base")
audio_queue = queue.Queue()


fs = 16000 
block_size = 2 

def audio_callback(indata, frames, time, status):
    """Callback-Funktion, die Audioblocks erfasst."""
    if status:
        print(status, file=sys.stderr)
    audio_queue.put(indata.copy())  # Audioblock queue

def live_transcribe():
    with sd.InputStream(samplerate=fs, channels=1, callback=audio_callback, blocksize=int(fs * block_size)):
        while True:
            try:
                # Queue new Audiofeed
                audio_block = audio_queue.get()

                # Audio
                audio_block = np.squeeze(audio_block)

                # Transkription des Audioblocks
                result = model.transcribe(audio_block, language="en")

                # Fortschrittlich angezeigter Te
                for text in result["segments"]:
                    sys.stdout.write(f"\r{text['text']}")
                    sys.stdout.flush()

            except KeyboardInterrupt:
                print("\nTranskription beendet.")
                break

if __name__ == "__main__":
    live_transcribe()
