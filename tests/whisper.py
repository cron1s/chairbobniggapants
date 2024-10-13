from discord.ext import commands, tasks
import whisper
import queue
import numpy as np
import pyaudio
import asyncio
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

# Whisper-Modell laden
model = whisper.load_model("base")
audio_queue = queue.Queue()

# Audiokonfiguration für PyAudio
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024  # Größe des Audioblocks

# Channel ID (diesen durch die ID des gewünschten Channels ersetzen)
CHANNEL_ID = 1292199193380782120  # Füge hier die Channel-ID ein

# Audioaufnahme mit PyAudio (z.B. durch virtuelle Audiokabel)
audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

class TranscribeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.transcription_task = None
        self.voice_client = None

    async def send_tts_message(self, text):
        """Sende eine Nachricht mit TTS in den angegebenen Discord-Channel."""
        channel = self.bot.get_channel(CHANNEL_ID)
        if channel is not None:
            await channel.send(text, tts=True)
        else:
            print("Channel nicht gefunden")

    async def record_audio(self):
        """Nimmt Audio vom lokalen Gerät auf und legt es in die Queue."""
        while True:
            audio_data = stream.read(CHUNK, exception_on_overflow=False)
            audio_np = np.frombuffer(audio_data, dtype=np.int16)
            audio_queue.put(audio_np)
            await asyncio.sleep(0.1)  # Vermeide das Blockieren des Loops

    @tasks.loop(seconds=1.0)
    async def live_transcribe(self):
        """Live-Transkription und Senden der TTS-Nachrichten."""
        while True:
            try:
                # Nächsten Audioblock aus der Queue holen
                if not audio_queue.empty():
                    audio_block = audio_queue.get()

                    # Audio block transkribieren
                    result = model.transcribe(audio_block, language="en")

                    # Text aus den Transkriptionssegmenten extrahieren
                    for text in result["segments"]:
                        # Den transkribierten Text über TTS in Discord senden
                        await self.send_tts_message(text['text'])
                        print(f"Gesendet: {text['text']}")

            except KeyboardInterrupt:
                print("\nTranskription beendet.")
                break

    @commands.command(name="join")
    async def join(self, ctx):
        """Lässt den Bot dem Sprachkanal beitreten."""
        if ctx.author.voice:  # Überprüft, ob der Benutzer in einem Sprachkanal ist
            channel = ctx.author.voice.channel  # Sprachkanal des Benutzers abrufen
            if ctx.voice_client is None:  # Überprüft, ob der Bot bereits verbunden ist
                self.voice_client = await channel.connect()  # Bot tritt dem Sprachkanal bei
                await ctx.send(f"Bot ist dem Sprachkanal {channel} beigetreten.")
                await self.record_audio()
            else:
                await ctx.send("Bot ist bereits in einem Sprachkanal.")
        else:
            await ctx.send("Du bist in keinem Sprachkanal!")

    @commands.command(name="leave")
    async def leave(self, ctx):
        """Lässt den Bot den Sprachkanal verlassen."""
        if ctx.voice_client is not None:  # Überprüft, ob der Bot in einem Sprachkanal ist
            await ctx.voice_client.disconnect()  # Bot verlässt den Sprachkanal
            await ctx.send("Bot hat den Sprachkanal verlassen.")
        else:
            await ctx.send("Der Bot ist in keinem Sprachkanal!")

    @commands.command(name='start_transcription')
    async def start_transcription(self, ctx):
        """Starte die Live-Transkription."""
        if self.transcription_task is None or not self.transcription_task.is_running():
            self.transcription_task = self.live_transcribe.start()
            await ctx.send("Live-Transkription gestartet!")
        else:
            await ctx.send("Die Transkription läuft bereits.")

    @commands.command(name='stop_transcription')
    async def stop_transcription(self, ctx):
        """Beende die Live-Transkription."""
        if self.transcription_task is not None and self.transcription_task.is_running():
            self.transcription_task.cancel()
            await ctx.send("Live-Transkription gestoppt.")
        else:
            await ctx.send("Keine Transkription läuft aktuell.")

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.bot.user} ist bereit.")

# Setup-Funktion für die Cog-Registrierung
async def setup(bot):
    await bot.add_cog(TranscribeCog(bot))
