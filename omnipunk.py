import discord
import os
import datetime
import aiofiles
from datetime import datetime as dt
from asyncio import sleep as s
import aiohttp
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"),
                   intents=intents)
bot.remove_command('help')
bot.warnings = {}  # guild_id : {member_id: [count, [(admin_id, reason)]]}
bot.deleted_messages = {}
day = dt.now()
def load_channel_ids():
    with open('channels.json', 'r') as f:
        data = json.load(f)
        return data.get('channels', [])
@bot.event
async def on_message_delete(message):
    if message.guild is None or message.channel is None:
        return
    
    if message.guild.id not in bot.deleted_messages:
        bot.deleted_messages[message.guild.id] = {}

    bot.deleted_messages[message.guild.id][message.channel.id] = (message.content, message.author, message.created_at)

@bot.event
async def on_ready():
    for guild in bot.guilds:
        bot.warnings[guild.id] = {}

        async with aiofiles.open(f"{guild.id}.txt", mode="a") as temp:
            pass

        async with aiofiles.open(f"{guild.id}.txt", mode="r") as file:
            lines = await file.readlines()

            for line in lines:
                data = line.split(" ")
                member_id = int(data[0])
                admin_id = int(data[1])
                reason = " ".join(data[2:]).strip("\n")

                try:
                    bot.warnings[guild.id][member_id][0] += 1
                    bot.warnings[guild.id][member_id][1].append((admin_id, reason))

                except KeyError:
                    bot.warnings[guild.id][member_id] = [1, [(admin_id, reason)]]
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f'{len(bot.guilds)} servers | {len(bot.users)} users | Type .help or tag me for commands'))

@bot.event
async def on_guild_join(guild):
    bot.warnings[guild.id] = {}

@bot.command()
async def gotcha(ctx):
    """Destinys Qoute"""
    await ctx.send('Anything Else?')

@bot.command()
async def test1(ctx):
    """My Jokes"""
    await ctx.send('I cant wait to see what cosmic horrors I will face in NeoPunkFMs Discord')

"""New Help Command"""
@bot.command(aliases=['h'])
async def help(ctx):
    hlpembed = discord.Embed(title="Help Menu", colour=discord.Colour.blue())
    hlpembed.add_field(name="mute / m", value="Mutes users for a specified amount of time (a Reason is Required)", inline=False)
    hlpembed.add_field(name="ex:", value=" .mute @you 10 lame-ass user", inline=False)
    hlpembed.add_field(name="unmute / um", value="Unmutes users", inline=False)
    hlpembed.add_field(name="ex:", value=" .unmute @you", inline=False)
    hlpembed.add_field(name="clr / clear", value="This clears the chat the command is run in. Limit is 10,000", inline=False)
    hlpembed.add_field(name="ex:", value=" .clr 100", inline=False)
    hlpembed.add_field(name="warn / w", value="This gives the user a warning", inline=False)
    hlpembed.add_field(name="ex:", value=" .warn 100", inline=False)
    hlpembed.add_field(name="warns / ws", value="This gives the number, reasons, and mod who issued a specific warn", inline=False)
    hlpembed.add_field(name="ex:", value=" .ws @jupiter", inline=False)
    hlpembed.add_field(name="snipe / s", value="This snipes the user's last message", inline=False)
    hlpembed.add_field(name="ex:", value=" .snipe", inline=False)
    
    await ctx.send(embed=hlpembed)
    """await ctx.send(f"Successfully sent help to {member}.")"""


"""Command to 'Age restrict' certain channels"""
@bot.event
async def on_member_join(member):
    # Send DM asking for age
    try:
        await member.send("Welcome to the server! Please enter your age to get access to the appropriate channels.")
        
        def check(m):
            return m.author == member and isinstance(m.channel, discord.DMChannel)
        
        response = await bot.wait_for('message', timeout=60.0, check=check)
        age = int(response.content)
        
        # Get guild
        guild = member.guild
        channel_ids = load_channel_ids()  # Load the list of channel IDs
        
        for channel_id in channel_ids:
            channel = guild.get_channel(int(channel_id))
            
            if channel:
                # Clear all current permissions for the user
                await channel.set_permissions(member, overwrite=None)
                
                if age < 18:
                    # Allow users under 18 to view and send messages
                    await channel.set_permissions(member, read_messages=False, send_messages=False)
                else:
                    # Allow users 18 and older to view and send messages
                    await channel.set_permissions(member, read_messages=True, send_messages=True)
        
        # Notify the user
        await member.send(f"Your age has been verified. You now have access to the appropriate channels.")
    except ValueError:
        await member.send("Please enter a valid age (number).")
    except asyncio.TimeoutError:
        await member.send("You took too long to respond. Please try again later.")
    except Exception as e:
        await member.send(f"An error occurred: {str(e)}")

"""Snipe a users message."""
@bot.command(name='lastdeleted', aliases=['ld'])
async def last_deleted(ctx):
    guild_id = ctx.guild.id
    channel_id = ctx.channel.id

    if guild_id in bot.deleted_messages and channel_id in bot.deleted_messages[guild_id]:
        content, author, time = bot.deleted_messages[guild_id][channel_id]

        embed = discord.Embed(description=content, color=discord.Color.purple(), timestamp=time)
        embed.set_author(name=f"{author.name}#{author.discriminator}", icon_url=author.display_avatar.url)
        embed.set_footer(text=f"Deleted in: #{ctx.channel.name}")

        await ctx.send(embed=embed)
    else:
        await ctx.send("No deleted messages found in this channel.")


bot.run
