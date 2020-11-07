import discord
from discord.ext import commands
import random
from config import BOT_TOKEN
import asyncio
import youtube_dl
import os
import shutil
from youtube_search import YoutubeSearch
import requests
from discord.utils import get
import traceback

bot = commands.Bot(command_prefix='*')
players = {}

youtube_dl.utils.bug_reports_message = lambda: ''
##############################################################################################
#join
@bot.command(pass_context=True,aliases=['j'])
async def join(ctx):
    global voice
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients,guild = ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
    await voice.disconnect()
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
    await ctx.send('Joined {}'.format(channel))
#############################################################################################
#play
@bot.command(pass_context=True, aliases=['p', 'pla'])
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
                print("No more queued song(s)\n")
                queues.clear()
                return
            main_location = os.path.dirname(os.path.realpath(__file__))
            song_path = os.path.abspath(os.path.realpath("Queue") + "\\" + first_file)
            if length != 0:
                print("Song done, playing next queued\n")
                print(f"Songs still in queue: {still_q}")
                song_there = os.path.isfile("song.mp3")
                if song_there:
                    os.remove("song.mp3")
                shutil.move(song_path, main_location)
                for file in os.listdir("./"):
                    if file.endswith(".mp3"):
                        os.rename(file, 'song.mp3')

                voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: check_queue())
                voice.source = discord.PCMVolumeTransformer(voice.source)
                voice.source.volume = 0.7

            else:
                queues.clear()
                return

        else:
            queues.clear()
            print("No songs were queued before the ending of the last song\n")



    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
            queues.clear()
            print("Removed old song file")
    except PermissionError:
        print("Trying to delete song file, but it's being played")
        await ctx.send("ERROR: Music playing")
        return


    Queue_infile = os.path.isdir("./Queue")
    try:
        Queue_folder = "./Queue"
        if Queue_infile is True:
            print("Removed old Queue Folder")
            shutil.rmtree(Queue_folder)
    except:
        print("No old Queue folder")

    await ctx.send("Getting everything ready now")

    voice = get(bot.voice_clients, guild=ctx.guild)

    ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{'key':'FFmpegExtractAudio',
                        'preferredcodec':'mp3',
                        'preferredquality':'192'}],
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'}

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Downloading audio now\n")
        ydl.download([url])

    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            name = file
            print(f"Renamed File: {file}\n")
            os.rename(file, "song.mp3")

    voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: check_queue())
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.7

    nname = name.rsplit("-", 2)
    await ctx.send(f"Playing: {nname[0]}")
    print("playing\n")
#############################################################################################################
#leave
@bot.command(name='leave',pass_context=True,aliases=['l'])
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients,guild = ctx.guild)
    if voice and voice.is_connected():
        await voice.disconnect()
        await ctx.send(f'left {channel}')
    else:
        await ctx.send('I dont think am in a voice channel!')
##############################################################################################
#stop
@bot.command(name='stop')
async def stop(ctx):
    voice = get(bot.voice_clients,guild = ctx.guild)
    if voice and voice.is_playing():
        server = ctx.message.guild
        voice_client = server.voice_client
        voice_client.stop()
        await ctx.send('stopped {}'.format(ctx.message.author.mention))
    else:
        await ctx.send('No track is playing right now')
#############################################################################################################     

#pause
@bot.command(name='pause')
async def pause(ctx):
    voice = get(bot.voice_clients,guild = ctx.guild)
    if voice and voice.is_playing():
        server = ctx.message.guild
        voice_client = server.voice_client
        voice_client.pause()
        await ctx.send('paused {}'.format(ctx.message.author.mention))
    else:
        await ctx.send('No track is playing now!')
 #########################################################################################################   
        
#resume
@bot.command(name='resume')
async def resume(ctx):
    voice = get(bot.voice_clients,guild = ctx.guild)
    if voice and voice.is_paused():
        voice_client = ctx.message.guild.voice_client
        voice_client.resume()
        await ctx.send('resumed {}'.format(ctx.message.author.mention))
    else:
        await ctx.send('Music is not paused!')
###############################################################################################
#on ready
@bot.event
async def on_ready():
    print('{} has logged in'.format(str(bot.user)))
########################################################################################
#message
@bot.event
async def on_message(message):
    channel = message.channel
    if message.author == bot.user:
        return
    if message.content == '*test':
        await channel.send('this is a test!')
    await bot.process_commands(message)
########################################################################################
#ping
@bot.command(name='ping',aliases=['latency'])
async def ping(ctx):
    await ctx.send('Pong! My latency is {}ms'.format(round(bot.latency *1000)))
#############################################################################################
#queue
queues = {}

@bot.command(pass_context=True, aliases=['q', 'que'])
async def queue(ctx, url: str):
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
    'postprocessors': [{'key':'FFmpegExtractAudio',
                        'preferredcodec':'mp3',
                        'preferredquality':'192'}],
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'outtmpl' : queue_path,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'}

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Downloading audio now\n")
        ydl.download([url])
    await ctx.send("Adding song " + str(q_num) + " to the queue")

    print("Song added to queue\n")
###################################################################################
#skip
@bot.command(pass_context = True,aliases = ['ski','s'])
async def skip(ctx):
    voice = get(bot.voice_clients,guild = ctx.guild)
    if voice and voice.is_playing():
        voice.stop()
        await ctx.send('playing next song')

    else:
        print('no music playing')
        await ctx.send('No music playing!')
##########################################################################################
#volume
@bot.command(pass_context=True, aliases=['v', 'vol'])
async def volume(ctx, volume: int):

    if ctx.voice_client is None:
        return await ctx.send("Not connected to voice channel")

    print(volume/100)

    ctx.voice_client.source.volume = volume / 100
    await ctx.send(f"Changed volume to {volume}%")

bot.run(BOT_TOKEN)
