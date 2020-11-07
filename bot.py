import os
import discord
from discord.ext.commands import Cog,command
from datetime import datetime
import random
from discord.ext import commands, tasks
import youtube_dl
from random import choice

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' 
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title ')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


bot = commands.Bot(command_prefix='db ')
bot.remove_command('help')


status = ['music','listening to music','working on something','bot things','yeeting']



# on ready bot
@bot.event
async def on_ready():
    change_status.start()
    print(f'{bot.user} has logged in.')
    


#on member joined
@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.channels,name='general')
    await channel.send(f'**Welcome {member.mention}!! use +help to see what you can do with me ')


#on member left 
@bot.event
async def on_member_remove(member):
    channel = discord.utils.get(member.guild.channels,name = 'general')
    await channel.send(f'**Goodbye {member.mention}!!')

#change status
@tasks.loop(seconds = 20)
async def change_status():
    await bot.change_presence(activity=discord.Game(choice(status)))


#join
@bot.command(name='join',help = 'this command will make the bot join into the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send('join voice channel to play that')
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()


#dm
@bot.command(name='dm',help = 'this command will dm you!!')
async def dm(ctx,message=None):
    if message == None:
        await ctx.author.send('please give the message')
    else:
        await ctx.author.send(message)


#hello
@bot.command(name ='hello',help = 'this command will just greet you')
async def hello(ctx):
    await ctx.send('whatsup {}'.format(ctx.message.author.mention))



#ping
@bot.command(name = 'ping',help = 'this command will show the latency')
async def ping(ctx):
    await ctx.send(f'**pong!** Latency:{round(bot.latency *1000)}ms')
 


#answer
@bot.command(aliases=['amazing'],name = 'answer',help = 'this command will respond to your questions')
async def answer(ctx,*,question):
    responses=['how is you','am great','no','yes','probably not','amazing','wow','i dont know exactly','die','nothing much','am sorry']
    await ctx.send(random.choice(responses))



#roast
@bot.command(aliases=['die me'],name='roast',help='this command will roast people')
async def roast(ctx):
    roasting = ['look at the shit on your mirror',
                'you need plastic surgery',
                'I have no time to roast you,get lost',
                'just leave cunt']
    await ctx.send(random.choice(roasting))



#time
@bot.command(name = 'time',help ='this command will show the current time')
async def time(ctx):
    now = datetime.now()
    current_time = now.strftime('%H:%M:%S')
    await ctx.send('current time: {}'.format(current_time))



#clear
@bot.command(name ='clear',help ='this command will clear chats.the default clear value is 10')
async def clear(ctx ,amount=10):
    if amount =='all':
        await ctx.channel.purge(limit=amount *1000)
    else:
        await ctx.channel.purge(limit=amount)

queue = []
#queue
@bot.command(name='queue',help = 'this command will queue the tracks')
async def queue_(ctx,url):
    global queue
    queue.append(url)
    await ctx.send(f'`{url}` added to queue!')


#play_q
@bot.command(name='play_q',help = 'this command will play the song from the queue')
async def play_q(ctx):
    global queue
    server = ctx.message.guild
    voice_channel = server.voice_client

    async with ctx.typing():
        player = await YTDLSource.from_url(queue[0],loop=bot.loop)
        voice_channel.play(player,after=lambda e: print('Player error %s' % e)if e else None)
        del(queue[0])
    await ctx.send('**Now playing** {}'.format(player))


#play
@bot.command(name ='play',help = 'this plays the song')
async def play(ctx,url):
    global queue
    server = ctx.message.guild
    voice_channel = server.voice_client

    async with ctx.typing():
        player = await YTDLSource.from_url(url,loop=bot.loop)
        voice_channel.play(player,after=lambda e: print('Player error %s' %e)if e else None)
        await ctx.send('**Now Playing** {}'.format(player))

#pause
@bot.command(name='pause',help='this command will pause the music')
async def pause(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client
    voice_channel.pause()

#resume
@bot.command(description="Resumes the current playing track. Can only be used if current track has been paused.",brief="Resumes current track.",aliases=['RESUME','continue','CONTINUE'])
async def resume(ctx):
    try:
        server = ctx.message.guild
        server.voice_client.resume()
    except:
        await ctx.send('sorry i got some errors') 



#remove
@bot.command(name='remove',help = 'this command will remove the song from queue')
async def remove(ctx,number=0):
    global queue
    try:
        del(queue[int(number)])
        await ctx.send(f'your queue is now `{queue}`')
    except:
        await ctx.send('your queue is either **empty** or there is **no content** your looking at')




#view
@bot.command(name='view',help='this command will show the queue')
async def view(ctx):
    await ctx.send('your queue is now `{}`!'.format(str(queue)))

#stop
@bot.command(name='stop',help = 'this command will stop the player')
async def stop(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client
    voice_channel.stop()


#leave
@bot.command(name='leave',help = 'this command will leave the voice channel ')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    await voice_client.disconnect()


#help
@bot.command(pass_context=True)
async def help(ctx):
    author = ctx.message.author
    embed = discord.Embed(colour = discord.Colour.green())
    embed1 = discord.Embed(colour = discord.Color.red())
    embed2 = discord.Embed(colour = discord.Color.blue())


    title_help = ['music','moderating','miscellaneous']
    name_fields = [['remove','ban','dm'],['ping','hello','time','roast','answer']]
    values = [['for musics'],['for moderations'],['for fun']]
    music_field = ['play','pause','remove','view','queue','leave','stop']
    musics_value = ['play in vc','pause the play','remove songs in queue','view the queue','bot will leave the vc','stop the player']
    
    embed.set_author(name='voice channel',icon_url='https://3qlt52zt1rb4d0jxn31bq8fi-wpengine.netdna-ssl.com/wp-content/uploads/db-music-logo.png')
    embed.add_field(name ='play' ,value='play the music')
    embed.add_field(name='play_d',value='plays the music only from queue')
    embed.add_field(name='stop',value='stop current playing music')
    embed.add_field(name='pause',value ='pause the player')
    embed.add_field(name = 'resume',value='resume the player')
    embed.add_field(name ='queue',value='to add songs to a queue')
    embed.add_field(name='view',value='to view the queue')
    embed.add_field(name='leave',value = 'to make the bot exit vc')
    embed.add_field(name='remove',value='to remove songs in the queue')
    embed.set_thumbnail(url='https://hdwallpaperim.com/wp-content/uploads/2017/08/25/461486-DEDSEC-Watch_Dogs-video_games-Watch_Dogs_2-748x468.jpg',)
    await author.send(embed=embed)

    embed1.set_author(name='miscellaneous',)
    embed1.add_field(name='ping',value='shows latency of the bot')
    embed1.add_field(name='hello',value='greets the user')
    embed1.add_field(name='time',value='shows the current time')
    embed1.add_field(name='roast',value='roasts the user')
    embed1.add_field(name='answer',value='replies to random questions')
    await author.send(embed=embed1)

    embed2.set_author(name='moderations')
    embed2.add_field(name='dm',value='dms for you')
    embed2.add_field(name='ban',value='bans people')
    embed2.add_field(name='kick',value='kicks people')
    await author.send(embed=embed2)







    
bot.run('NzMzNjU5MzcxNzUzNDM5MjQy.XxGXiA.Gk1TUUznYl3hk0XHtBemDuwP7dw')
