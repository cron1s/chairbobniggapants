import discord
import pyaudio
import wave
import asyncio
from discord.ext import commands, tasks

# PyAudio-Konfiguration
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
CHUNK = (RATE // 1000) * 20

# PyAudio-Objekt erstellen
audio = pyaudio.PyAudio()

# Öffne einen Audio-Loopback-Stream
loopback_stream = audio.open(format=FORMAT,
                             channels=CHANNELS,
                             rate=RATE,
                             input=True,
                             output=True,
                             input_device_index=2,  # Audio Input (Loopback)
                             output_device_index=6,  # Audio Output (Loopback)
                             frames_per_buffer=CHUNK)

class AudioCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_client = None  # Wird benutzt, um den VoiceClient zu speichern
        self.audio_task = None  # Aufgabe für den Audio-Loopback-Task
        self.wf = None  # WAV-Datei-Handler

    @commands.command()
    async def join(self, ctx):
        """Lässt den Bot dem Sprachkanal beitreten und startet das Audio-Streaming."""
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            if ctx.voice_client is None:
                # Bot tritt dem Sprachkanal bei
                self.voice_client = await channel.connect()
                await ctx.send(f"Bot ist dem Sprachkanal {channel.name} beigetreten.")
                # Starte den Audio-Loopback-Task
                self.audio_task = self.stream_audio_loopback.start(self.voice_client)
            else:
                await ctx.send("Der Bot ist bereits in einem Sprachkanal.")
        else:
            await ctx.send("Du musst dich in einem Sprachkanal befinden.")

    @commands.command()
    async def leave(self, ctx):
        """Lässt den Bot den Sprachkanal verlassen und stoppt das Audio-Streaming."""
        if ctx.voice_client:
            # Stoppe die Audio-Streaming-Task und schließe die WAV-Datei
            if self.audio_task is not None:
                self.audio_task.cancel()
                self.cleanup()  # Ressourcen freigeben
            await ctx.voice_client.disconnect()
            await ctx.send("Bot hat den Sprachkanal verlassen.")
        else:
            await ctx.send("Der Bot ist in keinem Sprachkanal.")

    def cleanup(self):
        """Schließt die WAV-Datei und räumt Ressourcen auf."""
        if self.wf is not None:
            self.wf.close()  # Schließe die WAV-Datei
            self.wf = None
        print("Ressourcen wurden freigegeben.")

    def open_wav_file(self):
        """Öffnet die WAV-Datei für das Schreiben von Audiodaten."""
        wave_output_filename = "output.wav"
        self.wf = wave.open(wave_output_filename, 'wb')
        self.wf.setnchannels(CHANNELS)
        self.wf.setsampwidth(audio.get_sample_size(FORMAT))
        self.wf.setframerate(RATE)
        print("WAV-Datei geöffnet.")

    @tasks.loop(seconds=0.01)
    async def stream_audio_loopback(self, voice_client):
        """Kontinuierlich Audiodaten vom Loopback-Stream lesen und im Sprachkanal abspielen und speichern."""
        try:
            # Öffne die WAV-Datei, wenn der Task startet
            self.open_wav_file()

            while True:
                # Lese den Audioblock vom PyAudio-Stream
                audio_data = loopback_stream.read(CHUNK)

                # Speichere den Audioblock in die WAV-Datei
                if self.wf is not None:
                    self.wf.writeframes(audio_data)

                # Sende den Audioblock an Discord zum Abspielen
                if voice_client.is_playing():
                    voice_client.stop()

                # PCM-Daten abspielen
                audio_source = discord.PCMAudio(audio_data)
                voice_client.play(audio_source)

                await asyncio.sleep(0.01)
        except Exception as e:
            print(f"Fehler beim Audio-Streaming: {e}")
            self.cleanup()  # Schließe die Datei bei einem Fehler

    @commands.command(name='start_audio')
    async def start_audio(self, ctx):
        if ctx.voice_client and self.audio_task is None:
            # Starte den Audio-Loopback-Task
            self.audio_task = self.stream_audio_loopback.start(ctx.voice_client)
            await ctx.send("Audio-Streaming gestartet.")
        else:
            await ctx.send("Der Bot ist entweder nicht in einem Sprachkanal oder das Streaming läuft bereits.")

    @commands.command(name='stop_audio')
    async def stop_audio(self, ctx):
        if self.audio_task is not None:
            self.audio_task.cancel()
            self.audio_task = None
            self.cleanup()  # Ressourcen freigeben und die WAV-Datei schließen
            await ctx.send("Audio-Streaming gestoppt.")
        else:
            await ctx.send("Das Audio-Streaming läuft nicht.")

async def setup(bot):
    await bot.add_cog(AudioCog(bot))