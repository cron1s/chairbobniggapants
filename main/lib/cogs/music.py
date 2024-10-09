import yt_dlp as youtube_dl
import asyncio
import discord
from discord.ext import commands

# Configuration of Youtube_dl
ytdl_format_options = {
    'format': 'bestaudio/best',
    'noplaylist': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'extract_flat': 'in_playlist',
    'source_address': '0.0.0.0',
    'force_generic_extractor': True  # to stream and not to download
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',  # only audio, no video
    'executable': 'C:/ffmpeg/bin/ffmpeg.exe'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

        if 'entries' in data:
            data = data['entries'][0]

        duration = data.get('duration', 0)
        end_time = max(data['duration'] - 5, 0)

        ffmpeg_options['options'] = f'-vn -af "afade=t=in:st=0:d=5,afade=t=out:st={end_time}:d=5"'

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []  # The queue for songs
        self.is_looping = False
        self.current_url = None

    async def play_next_in_queue(self, ctx):
        """Play the next song in the queue."""
        if self.queue:
            next_song = self.queue.pop(0)  # Get the next song from the queue
            self.current_url = next_song['url']
            player = next_song['player']
            await ctx.send(f"Now playing: **{player.title}**")
            ctx.voice_client.play(player, after=lambda e: self.bot.loop.create_task(self.play_next_in_queue(ctx)))
        else:
            await ctx.send("The queue is now empty.")

    @commands.command(name="play")
    async def play(self, ctx, *, url):
        async with ctx.typing():
            try:
                player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)

                if ctx.voice_client.is_playing():
                    self.queue.append({'player': player, 'url': url})
                    await ctx.send(f"Added to queue: **{player.title}**")
                else:
                    self.current_url = url
                    await ctx.send(f"Now playing: **{player.title}**")
                    ctx.voice_client.play(player, after=lambda e: self.bot.loop.create_task(self.play_next_in_queue(ctx)))

            except Exception as e:
                await ctx.send(f"Error while playing: {e}")

    @commands.command(name="queue")
    async def view_queue(self, ctx):
        """Displays the current queue."""
        if self.queue:
            queue_list = '\n'.join([f"{i+1}. {song['player'].title}" for i, song in enumerate(self.queue)])
            await ctx.send(f"Current Queue:\n{queue_list}")
        else:
            await ctx.send("The queue is empty.")

    @commands.command(name="stop")
    async def stop(self, ctx):
        if ctx.voice_client is not None:
            self.is_looping = False
            self.queue.clear()
            ctx.voice_client.stop()
            await ctx.send("Playback has been stopped and queue cleared.")

    @commands.command(name="skip")
    async def skip(self, ctx):
        """Skips the current song."""
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("Song skipped.")

    @commands.command(name="pause")
    async def pause(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("Playback has been paused.")

    @commands.command(name="resume")
    async def resume(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("Playback has resumed.")

    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("You are not connected to a voice channel.")
            return

        voice_channel = ctx.author.voice.channel

        if ctx.voice_client is not None:
            await ctx.voice_client.move_to(voice_channel)
        else:
            await voice_channel.connect()

async def setup(bot):
    await bot.add_cog(Music(bot))