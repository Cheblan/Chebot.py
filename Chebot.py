import discord
import youtube_dl
import asyncio
import os
from discord.utils import get
from discord.ext import commands
from discord import FFmpegPCMAudio
from discord.ext.commands import Bot
from discord.voice_client import VoiceClient

bot = commands.Bot(command_prefix='!')

volume = 50

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command(pass_context=True)
async def join(ctx):
    global voice
    try:
        channel = ctx.message.author.voice.channel
        voice = get(bot.voice_clients, guild=ctx.guild)
        if voice and voice.is_connected():
            await voice.move_to(channel)
        else:
            voice = await channel.connect()
            print(voice)
    except:
        await ctx.send("Вы не в голосовом канале.")

@bot.command(pass_context=True)
async def leave(ctx):
    try:
        channel = ctx.message.author.voice.channel
        voice = get(bot.voice_clients, guild=ctx.guild)
        if voice and voice.is_connected():
            await voice.disconnect()
        else:
            pass
    except:
        await ctx.send("Вы не в голосовом канале.")

@bot.command(pass_context=True)
async def play(ctx, url: str):
    #try:
        channel = ctx.message.author.voice.channel
        voice = get(bot.voice_clients, guild=ctx.guild)

        if voice and voice.is_connected():
            if url == None:
                await ctx.send("Для проигрывания музыки нужна ссылка на Youtube.")

            else:
                song_there = os.path.isfile("song.mp3")
                try:
                    if song_there:
                        os.remove("song.mp3")
                        print("Снёс старый сонг.")
                except PermissionError:
                    print("Пытался снести сонг, но он пока что играл.")
                    await ctx.send("Музыка уже играет. Дождитесь пока она доиграет.")
                    return

                await ctx.send ("Подготавливаю музыку для проигрывания.")

                YTDL_OPTIONS = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                    }],
                }

                with youtube_dl.YoutubeDL(YTDL_OPTIONS) as ytdl:
                    print("Скачиваю музыку.")
                    ytdl.download([url])

                for file in os.listdir("./"):
                    if file.endswith(".mp3"):
                        name = file
                        os.rename(file, "song.mp3")

                nname = name.rsplit("-", 2)

                voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: print(f"Композиция {name} закончила играть."))
                voice.source = discord.PCMVolumeTransformer(voice.source)
                voice.source.volume = 0.07

                nname = name.rsplit("-", 2)
                await ctx.send(f"Играет: {nname[0]}")

                print("Музыка играет.")
        else:
            await ctx.send("Пригласите бота в голосовой канал командой '!join' для начала проигрывания музыки.")
    #except:
        #await ctx.send("Вы должны находиться в голосовом канале, чтобы бот начал проигрывать музыку.")

bot.run('Токен')
