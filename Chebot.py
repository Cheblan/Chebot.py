import os
import shutil
from os import system

import discord
import youtube_dl
from discord.ext import commands
from discord.utils import get

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.command(pass_context=True, aliases=['j'])
async def join(ctx):
    global voice
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()

    await voice.disconnect()

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        print(f"Бот зашёл в {channel}\n")

    await ctx.send(f"Бот зашёл в {channel}")


@bot.command(pass_context=True, aliases=['l'])
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
        print(f"Бот вышел из {channel}")
        await ctx.send(f"Бот вышел из {channel}.")
    else:
        print("Бот не в голосовом канале")
        await ctx.send("Бот не в голосовом канале.")


@bot.command(pass_context=True, aliases=['p'])
async def play(ctx, url: str):

    def check_queue():
        Queue_infile = os.path.isdir("./Queue")
        if Queue_infile is True:
            DIR = os.path.abspath(os.path.realpath("Queue"))
            length = len(os.listdir(DIR))
            still_q = length - 1
            try:
                first_file = os.listdir(DIR)[0]
            except:
                print("Очередь пуста")
                ctx.send("Очередь пуста.")
                queues.clear()
                return
            main_location = os.path.dirname(os.path.realpath(__file__))
            song_path = os.path.abspath(os.path.realpath("Queue") + "\\" + first_file)
            if length != 0:
                print("Песня закончена, идём дальше по очереди")
                print(f"Песен в очереди: {still_q}")
                song_there = os.path.isfile("song.mp3")
                if song_there:
                    os.remove("song.mp3")
                shutil.move(song_path, main_location)
                for file in os.listdir("./"):
                    if file.endswith(".mp3"):
                        os.rename(file, 'song.mp3')

                voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: check_queue())
                voice.source = discord.PCMVolumeTransformer(voice.source)
                voice.source.volume = 0.07

            else:
                queues.clear()
                return

        else:
            queues.clear()
            print("В очереди больше не было песен")

    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
            queues.clear()
            print("Снёс старый сонг")
    except PermissionError:
        print("Пытался снести сонг, но он играл")
        await ctx.send("Музыка уже играет. Дождитесь конца или добавьте песни в очередь командой '!queueadd'")
        return


    Queue_infile = os.path.isdir("./Queue")
    try:
        Queue_folder = "./Queue"
        if Queue_infile is True:
            print("Снёс старую папку с очередью песен")
            shutil.rmtree(Queue_folder)
    except:
        print("Старой папки с очередью нет")

    await ctx.send("Подготовка музыки для проигрывания.")

    voice = get(bot.voice_clients, guild=ctx.guild)

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Качаю музыку")
        ydl.download([url])

    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            name = file
            os.rename(file, "song.mp3")

    song_there = os.path.isfile("song.mp3")
    if song_there:
        voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: check_queue())
        voice.source = discord.PCMVolumeTransformer(voice.source)
        voice.source.volume = 0.07

    nname = name.rsplit("-", 2)
    await ctx.send(f"В данный момент играет: {nname[1]}.")
    print("Музыка играет")


@bot.command(pass_context=True)
async def pause(ctx):

    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print("Музыка поставлена на паузе")
        voice.pause()
        await ctx.send("Музыка поставлена на паузе.")
    else:
        print("Музыка уже не играла или уже на паузе")
        await ctx.send("Музыка уже не играла или уже на паузе.")


@bot.command(pass_context=True, aliases=['res'])
async def resume(ctx):

    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_paused():
        print("Продолжаем")
        voice.resume()
        await ctx.send("Продолжаем.")
    else:
        print("Музыка не стояла на паузе.")
        await ctx.send("Музыка не стояла на паузе.")


@bot.command(pass_context=True, aliases=['s'])
async def stop(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print("Музыка остановлена")
        voice.stop()
        await ctx.send("Музыка остановлена.")
    else:
        print("Музыка не играла")
        await ctx.send("Музыка не играла.")

queues = {}

@bot.command(pass_context=True, aliases=['qadd'])
async def queueadd(ctx, url: str):
    Queue_infile = os.path.isdir("./Queue")
    if Queue_infile is False:
        os.mkdir("Queue")
    DIR = os.path.abspath(os.path.realpath("Queue"))
    q_num = len(os.listdir(DIR))
    q_num += 1
    add_queue = True
    while add_queue:
        if q_num in queues:
            q_num += 1
        else:
            add_queue = False
            queues[q_num] = q_num

    queue_path = os.path.abspath(os.path.realpath("Queue") + f"\song{q_num}.%(ext)s")

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'outtmpl': queue_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Качаю музыку")
        ydl.download([url])

    await ctx.send("Уже " + str(q_num) + " песни в очереди.")

    print("Сонг добавлен в очередь")

@bot.command(pass_context=True, aliases=['n'])
async def next(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print("Играем дальше.")
        voice.stop()
        await ctx.send("Следующая песня начала играть.")
    else:
        print("Музыка не играла")
        await ctx.send("Музыка не играла.")

@bot.command(pass_context=True)
async def clean(ctx):
    global queues
    queues = {}
    await ctx.send("Очередь очищена.")

bot.run('NjM2MTk0MjM3MzE0MjM2NDI3.Xa8H0g.BKJxV7t_uLijRFCDPjQdDui2y-k')
