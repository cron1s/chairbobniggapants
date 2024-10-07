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
    'options': '-vn'  # only audio, no video
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True): # Sets stream to true
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False)) # No download

        if 'entries' in data:
            data = data['entries'][0] # if playlist, take first

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)
    

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="play")
    async def play(self, ctx, *, url):
        async with ctx.typing():
            try:
                player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
                ctx.voice_client.play(player, after=lambda e: print(f"Error {e}") if e else None)
                await ctx.send(f"Playing: **{player.title}")
            except Exception as e:
                await ctx.send(f"Error on playing: {e}")

    @commands.command(name="stop")
    async def stop(self, ctx):
        if ctx.voice_client is not None:
            ctx.voice_client.stop()

    @commands.command(name="loop")
    async def loop(self, ctx, *, url):
        pass

    @commands.command(name="resume")
    async def resume(self, ctx, *, url):
        pass

    @commands.command(name="repeat")
    async def repeat(self, ctx, *, url):
        pass

    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.author.voice is None:
            return
        
        voice_channel = ctx.author.voice.channel

        if ctx.voice_client is not None:
            await ctx.voice_client.move_to(voice_channel)
        else:
            await voice_channel.connect()

async def setup(bot):
    await bot.add_cog(Music(bot))