from discord.ext import commands
import discord
import whisper
import ffmpeg
import asyncio
import numpy as np
import subprocess

model = whisper.load_model("base")

# Die ID des Channels, in den die Transkription gesendet wird
TRANSCRIPTION_CHANNEL_ID = 1292199193380782120

class VoiceClient(discord.VoiceClient):
    async def on_voice_receive(self, data):
        # Hier kannst du die empfangenen Audio-Daten verarbeiten
        print("Audio-Daten empfangen!")

    async def on_connect(self):
        # Start der Audioaufnahme sobald der Bot connected ist
        print(f"Verbunden mit dem Sprachkanal {self.channel}, starte die Aufnahme.")
        await self.capture_audio()

    async def capture_audio(self):
        # Hol dir den Channel, in den die Transkription geschrieben wird
        transcription_channel = self.guild.get_channel(TRANSCRIPTION_CHANNEL_ID)
        if transcription_channel is None:
            print(f"Fehler: Channel mit ID {TRANSCRIPTION_CHANNEL_ID} nicht gefunden.")
            return

        process = (
            ffmpeg
            .input('pipe:0', format='s16le', ac=2, ar='48000')  # ffmpeg wird den Audiostream des VoiceClients bearbeiten
            .output('pipe:1', format='wav')
            .run_async(pipe_stdin=True, pipe_stdout=True, pipe_stderr=True)
        )

        while True:
            try:
                # Audioblock vom Sprachkanal abrufen
                audio_data = await self.recv_audio()

                # Debug-Ausgaben, um sicherzustellen, dass der Bot Audiostreams erhält
                print("Audio-Daten empfangen:")
                print(f"Länge des empfangenen Audio-Datenblocks: {len(audio_data)} Bytes")

                # Sende Audio-Daten zu ffmpeg, um sie in WAV zu konvertieren
                process.stdin.write(audio_data)

                # Erhalte die umgewandelten WAV-Daten von ffmpeg
                wav_data = process.stdout.read()

                # FFmpeg-Fehler ausgeben, falls vorhanden
                stderr_output = process.stderr.read()
                if stderr_output:
                    print(f"FFmpeg-Fehler: {stderr_output}")

                # Debugging: Speichern der Audiodaten in eine Datei, um sie zu prüfen
                with open("received_audio.raw", "wb") as f:
                    f.write(audio_data)
                print("Rohdaten in 'received_audio.raw' gespeichert")

                # Konvertiere WAV-Daten in das richtige Format für Whisper
                result = model.transcribe(wav_data, language="en")

                # Sende den transkribierten Text in den spezifischen Discord-Channel
                for text in result["segments"]:
                    transcribed_text = text['text']
                    await transcription_channel.send(f"Transkribierter Text: {transcribed_text}")
                    print(f"Transkribierter Text gesendet: {transcribed_text}")

            except Exception as e:
                print(f"Fehler bei der Transkription: {e}")
                break


class WhisperCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="join")
    async def join(self, ctx):
        """Befehl, damit der Bot dem Sprachkanal beitritt und sofort die Aufnahme startet."""
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            voice_client = await channel.connect(cls=VoiceClient)
            await ctx.send(f"Bot ist dem Sprachkanal {channel} beigetreten und die Aufnahme hat begonnen.")
            print(f"Bot ist dem Sprachkanal {channel} beigetreten.")
        else:
            await ctx.send("Du bist in keinem Sprachkanal!")

    @commands.command(name="leave")
    async def leave(self, ctx):
        """Befehl zum Verlassen des Sprachkanals."""
        if ctx.voice_client is not None:
            await ctx.voice_client.disconnect()
            await ctx.send("Bot hat den Sprachkanal verlassen.")
        else:
            await ctx.send("Der Bot ist in keinem Sprachkanal!")

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.bot.user} ist bereit und wartet auf Voice-Channel-Joins.")

async def setup(bot):
    await bot.add_cog(WhisperCog(bot))
 