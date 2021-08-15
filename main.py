# coding=utf-8
import discord #Import Discord.py
import random #Import the abilty to make things random like 8ball
import json
from discord import activity
from discord.ext import commands, tasks #get tasks from discord.ext commands
import os
import sys
from itertools import cycle
from discord import Member
from random import choice, randint
import time
import asyncio
import asyncio as asyncio
import aiohttp
from discord.utils import find
import re
import string
from discord.ext import tasks
from discord import Embed
from discordpy_slash import slash as s
import subprocess
from discord.utils import get
#other
import logging
from discord.ext import *
from discord.ext.commands import *
from ctypes import *
from datetime import datetime
from discord import Webhook, AsyncWebhookAdapter
import aiohttp
import asyncpg

intents = discord.Intents.default()
intents.members = True
intents.messages

DEFAULT_PREFIX = '+'

async def get_prefix(bot, message):
    if not message.guild:
        return commands.when_mentioned_or(DEFAULT_PREFIX)(bot,message)

    prefix = await bot.db.fetch('SELECT prefix FROM guilds WHERE guild_id = $1', message.guild.id)
    if len(prefix) == 0:
        await bot.db.execute('INSERT INTO guilds(guild_id, prefix) VALUES ($1, $2)', message.guild.id, DEFAULT_PREFIX)
        prefix = DEFAULT_PREFIX
    else:
        prefix = prefix[0].get("prefix")
    return commands.when_mentioned_or(prefix)(bot,message)


bot = commands.Bot(command_prefix = get_prefix, intents=intents, case_insensitive=True)

bot.remove_command('help')

async def create_db_pool():
    bot.db = await asyncpg.create_pool(database = "tutorial", user = "postgres", password= "20266137" )
    print("Connected to the DataBase.")


@bot.event
async def on_ready():
    print('Bot is starting..')
    await bot.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.watching, name=f"https://profanityblocker.org"))
    print('Status Changed. Syncing slash commands..')
    await s.sync_all_commands(bot, send_hidden=False)
    print('Bot is fully online. Slash commands have been %100 synced.')



@bot.command()
@commands.has_permissions(administrator=True)
async def setprefix(ctx, new_prefix):
    await bot.db.execute('UPDATE guilds SET prefix = $1 WHERE guild_id = $2', new_prefix, ctx.guild.id)
    await ctx.send(f"The prefix has been updated! New prefix: `{new_prefix}`")

    try:
        the_guild = ctx.guild
        author = ctx.author
        the_channel = discord.utils.get(the_guild.text_channels, name="mod-logs")
        embed = discord.Embed(title="Prefix Updated", color=0xD708CC)
        embed.add_field(name="Moderator:", value=f"{author.mention}", inline=True)
        embed.add_field(name="New Prefix:", value=f"{new_prefix}", inline=True)
        embed.add_field(name="Old Prefix:", value=f"{ctx.prefix}", inline=True)
        embed.timestamp = datetime.utcnow()
        await the_channel.send(embed=embed)

    except:
        pass


@bot.command(description = "The help panel")
async def help(ctx):
    embed = discord.Embed(title="Help Panel", color=0xD708CC, description = "Default help panel.")
    embed.add_field(name = "Other Commands", value = f"Use `(prefix)helpother` for the list of general commands.")
    embed.add_field(name = "Moderation Commands", value = "Use `(prefix)helpmoderation` for the list of moderation commands.")
    embed.add_field(name = "Support Server", value = "https://discord.gg/ecz2z36gkB")
    embed.add_field(name = "Our Website", value = "https://profanityblocker.org")
    await ctx.send(embed=embed)

@bot.command(description = "The help panel for other commands.")
async def helpother(ctx):
    embed = discord.Embed(title="Help Other commands", color=0xD708CC, description= f"1. ping \n 2. servercount \n 3. info \n 4. invite \n 5. setrules \n 6. vote \n 7. helpme \n 8. debug \n 9. setprefix")
    await ctx.send(embed=embed)


@bot.command(description = "The help panel for other commands.")
async def helpmoderation(ctx):
    embed = discord.Embed(title="Help Moderation Commands", color=0xD708CC, description= f"1. ban \n 2. unban \n 3. mute \n 4. unmute \n 5. warn \n 6. lock \n 7. unlock \n 8. slowmode \n 9. kick \n 10. clear \n 11. bypass \n 12. unbypass \n 13. add")
    await ctx.send(embed=embed)


#shutdown bot
@bot.command(description = "Shutsdown the bot.")
@commands.is_owner()
async def shutdown(ctx):
    embed = discord.Embed(title="Shutting down.", color=0xD708CC, description=f"Shutting down. This will take up to two minute.")
    await ctx.send(embed=embed)
    await bot.close()


#check ping
@bot.command()
async def ping(ctx):
    start = time.perf_counter()
    message = await ctx.send("Calculating the ping...")
    end = time.perf_counter()
    duration = (end - start) * 1000
    await message.edit(content='API latency is **{:.2f}**ms'.format(duration))
        

#servercount
@bot.command(description = "Check how many servers the bot is in.")
async def servercount(ctx):
    embed = discord.Embed(title="Servercount", color=0xD708CC, description=f"This bot is in **{len(bot.guilds)}** guilds.")
    await ctx.send(embed=embed)

#errors
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    embed = discord.Embed(title="An Error Occured", color=0xD708CC, description=f"```{str(error)}```")      
    embed.timestamp = datetime.utcnow() 
    await ctx.send(embed=embed)

#invite command
@bot.command(description = "Invite for this bot.")
async def invite(ctx):
    embed = discord.Embed(title="My invite", color=0xD708CC, description="https://discord.com/api/oauth2/authorize?client_id=834812191277973564&permissions=8&scope=bot%20applications.commands")
    await ctx.send(embed=embed)


#restart the bot
@bot.command(description = "Restart the bot.")
@commands.is_owner()
async def restart(ctx):
    embed = discord.Embed(title="Restarting the bot.", color=0xD708CC, description="Restarting the api. This will take up to 5 seconds.")
    await ctx.send(embed=embed)
    os.execl(sys.executable, sys.executable, *sys.argv)



#Info command for the bot
import platform # For stats
pythonVersion = platform.python_version()
dpyVersion = discord.__version__
host = platform


@bot.command(description = "Information about this bot.")
async def info(ctx):

    all_members_embed_list = []

    for x in bot.get_all_members():
        all_members_embed_list.append(x)

        bot_embed_guilds = []

        for t in bot.guilds:
            bot_embed_guilds.append(t)

    embed = discord.Embed(title="Bot Info", description="General information about Profanity Blocker", color=0xD708CC)
    embed.add_field(name="Bot developers:", value="User319183#3149, Thewizzzzzz1338#6367", inline=True)
    embed.add_field(name="Guild Count:", value=f"{len(bot_embed_guilds)}", inline=True)
    # embed.add_field(name="Python Version:", value=f"{pythonVersion}", inline=True)
    # embed.add_field(name="Discord.py Version:", value=f"{dpyVersion}", inline=True)
    embed.add_field(name="Website:", value=f"https://profanityblocker.org")
    await ctx.send(embed=embed)


@bot.command(description = "Vote for the bot on Top.GG")
async def vote(ctx):
    embed = discord.Embed(title="Top.GG Vote", description="You can vote for the bot on Top.GG! Here's the link https://top.gg/bot/834812191277973564", color=0xD708CC)
    await ctx.send(embed=embed)


#ban command
@bot.command(description = "Ban the user.")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member, *, reason='None'):
    if reason is None: # Step 2 - part 1
        reason = "Not specificed." # Step 2 - part 2
    try: # Step 4 - part 1
        await ctx.guild.ban(discord.Object(id=member), reason=reason)
    except Exception as e: # Step 4 - part 2
        return
    embed = discord.Embed(title="Member Banned", description=f"**{member}**, has been banned..", color=0xD708CC)
    embed.timestamp = datetime.utcnow()
    await ctx.send(embed=embed)

    try:

        the_guild = ctx.guild
        author = ctx.author
        the_channel = discord.utils.get(the_guild.text_channels, name="mod-logs")
        embed = discord.Embed(title="Member Banned", color=0xD708CC)
        embed.add_field(name="Member's ID:", value=f"{member}", inline=True)
        embed.add_field(name="Moderator:", value=f"{author.mention}", inline=True)
        embed.add_field(name="Reason:", value=f"{reason}", inline=False)
        embed.timestamp = datetime.utcnow()
        await the_channel.send(embed=embed)

    except:
        pass



#unban command
@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user: discord.User, *, reason='Reason has not been specified.'): # Step 1
    guild = ctx.guild # Step 3
    try: # Step 4 - part 1
        await guild.unban(user, reason=reason) # Step 5
    except exception as e: # Step 4 - part 2
        return await ctx.send(e) # Step 4 - part 3
    embed = discord.Embed(title="Member Unbanned", description=f"**{user}**, has been unbanned.", color=0xD708CC)
    embed.timestamp = datetime.utcnow()
    await ctx.send(embed=embed)

    try:
        the_guild = ctx.guild
        author = ctx.author
        the_channel = discord.utils.get(the_guild.text_channels, name="mod-logs")
        embed = discord.Embed(title="Member Unbanned", color=0xD708CC)
        embed.add_field(name="Member's ID:", value=f"{user}", inline=True)
        embed.add_field(name="Moderator:", value=f"{author.mention}", inline=True)
        embed.add_field(name="Reason:", value=f"{reason}", inline=False)
        embed.timestamp = datetime.utcnow()
        await the_channel.send(embed=embed)

    except:
        pass


#Clear command
@bot.command(description="Clears X messages.")
@commands.has_permissions(manage_messages=True)
async def clear(ctx, num: int, target: discord.Member=None):
    if num > 500 or num < 0:
        return await ctx.send("Invalid amount. The maximum amount of messages you can delete is 500.")
    def msgcheck(amsg):
        if target:
           return amsg.author.id == target.id
        return True
    deleted = await ctx.channel.purge(limit=num, check=msgcheck)
    await ctx.send(f'**{len(deleted)}/{num}** messages have been deleted. This message will auto-delete after 10 seconds.', delete_after=10)

    try:
        the_guild = ctx.guild
        author = ctx.author
        the_channel = discord.utils.get(the_guild.text_channels, name="mod-logs")
        embed = discord.Embed(title="Messages Cleared", color=0xD708CC)
        embed.add_field(name="Moderator:", value=f"{author.mention}", inline=True)
        embed.add_field(name="Amount Of Cleared Messages:", value=f"{len(deleted)}/{num} messages", inline=False)
        embed.timestamp = datetime.utcnow()
        await the_channel.send(embed=embed)
    except:
        pass


#warn command
@bot.command(description = "Warn a Discord member")
@commands.has_permissions(manage_roles=True)
async def warn(ctx, member:discord.Member, *, reason='Reason has not been specified.'):
    if member.bot:
        await ctx.send("Bot's are not allowed to be warned!")
        return


    guild = ctx.guild
    warnedRole = discord.utils.get(guild.roles, name="Warned")

    if not warnedRole:
        warnedRole = await guild.create_role(name="Warned")
    embed = discord.Embed(title=f"Member Warned", description=f"{member.mention} has successfully been warned.", colour=discord.Colour.blue())
    await member.add_roles(warnedRole, reason=reason)
    embed.timestamp = datetime.utcnow()
    await ctx.send(embed=embed)

    try:
        the_guild = ctx.guild
        author = ctx.author
        the_channel = discord.utils.get(the_guild.text_channels, name="mod-logs")
        embed = discord.Embed(title="Member Warned", color=0xD708CC)
        embed.add_field(name="Member", value=f"{member.mention}", inline=True)
        embed.add_field(name="Moderator", value=f"{author.mention}", inline=True)
        embed.add_field(name="Reason", value=f"{reason}", inline=False)
        embed.set_thumbnail(url=member.avatar_url)
        embed.timestamp = datetime.utcnow()
        await the_channel.send(embed=embed)

    except:
        pass





#Mute command
@bot.command(description="Mutes a specified user.")
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, *, reason='Reason has not been specified.'):
    if member.bot:
        await ctx.send("Bot's are not allowed to be muted!")
        return

    guild = ctx.guild
    mutedRole = discord.utils.get(guild.roles, name="Muted")

    if not mutedRole:
        mutedRole = await guild.create_role(name="Muted")

        for channel in guild.channels:
            await channel.set_permissions(mutedRole, speak=False, send_messages=False, read_message_history=True, read_messages=False)
    embed = discord.Embed(title="Muted", description=f"{member.mention} was muted.", colour=discord.Colour.blue())
    embed.timestamp = datetime.utcnow()
    await ctx.send(embed=embed)
    await member.add_roles(mutedRole, reason=reason)


    try:
        the_guild = ctx.guild
        author = ctx.author
        the_channel = discord.utils.get(the_guild.text_channels, name="mod-logs")
        embed = discord.Embed(title="Member Muted", color=0xD708CC)
        embed.add_field(name="Member:", value=f"{member.mention}", inline=True)
        embed.add_field(name="Moderator:", value=f"{author.mention}", inline=True)
        embed.add_field(name="Reason:", value=f"{reason}", inline=False)
        embed.set_thumbnail(url=member.avatar_url)
        embed.timestamp = datetime.utcnow()
        await the_channel.send(embed=embed)

    except:
        pass



#Unmute command
@bot.command(description="Unmutes a specified user.")
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member, *, reason='Reason has not been specified.'):

    mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")

    if mutedRole not in member.roles:
        return await ctx.send(f"{member} is not muted.")

    mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")
    await member.remove_roles(mutedRole)
    embed = discord.Embed(title="Unmuted", description=f"Unmuted {member.mention}",colour=discord.Colour.blue())
    embed.timestamp = datetime.utcnow()
    await ctx.send(embed=embed)

    try:
        the_guild = ctx.guild
        author = ctx.author
        the_channel = discord.utils.get(ctx.guild.text_channels, name="mod-logs")
        embed = discord.Embed(title="Member Unmuted", color=0xD708CC)
        embed.add_field(name="Member", value=f"{member.mention}", inline=True)
        embed.add_field(name="Moderator", value=f"{author.mention}", inline=True)
        embed.add_field(name="Reason", value=f"{reason}", inline=False)
        embed.set_thumbnail(url=member.avatar_url)
        embed.timestamp = datetime.utcnow()
        await the_channel.send(embed=embed)

    except:
        pass


#kick command
@bot.command(description = "Kicks a user from the server.")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason='Reason has not been specified.'):
    embed = discord.Embed(title="Kicked", description=f"{member.mention} has been kicked.",colour=discord.Colour.blue())
    embed.timestamp = datetime.utcnow()
    await member.kick(reason=reason)
    await ctx.send(embed=embed)


    try:
        the_guild = ctx.guild
        author = ctx.author
        the_channel = discord.utils.get(the_guild.text_channels, name="mod-logs")
        embed = discord.Embed(title="Member Kicked", color=0xD708CC)
        embed.add_field(name="Member", value=f"{member.mention}", inline=True)
        embed.add_field(name="Moderator", value=f"{author.mention}", inline=True)
        embed.add_field(name="Reason", value=f"{reason}", inline=False)
        embed.set_thumbnail(url=member.avatar_url)
        embed.timestamp = datetime.utcnow()
        await the_channel.send(embed=embed)

    except:
        pass

#slowmode
@bot.command(description = "Change the slowmode.")
@commands.has_permissions(manage_channels=True, manage_messages=True)
async def slowmode(ctx, seconds: int):
    if seconds > 21600:
        return await ctx.send("Invalid slowmode. Slowmode must be 21600 seconds or lower.")
    def msgcheck(amsg):
        if target:
           return amsg.author.id == target.id
        return True
    await ctx.channel.edit(slowmode_delay=seconds)
    embed = discord.Embed(title="Slowmode", description=f"Slowmode has been set to **{seconds}** seconds in this channel.", color=0xD708CC)
    embed.timestamp = datetime.utcnow()
    await ctx.send(embed=embed)

    try:

        the_guild = ctx.guild
        author = ctx.author
        the_channel = discord.utils.get(the_guild.text_channels, name="mod-logs")
        embed = discord.Embed(title="Slowmode:", color=0xD708CC)
        embed.add_field(name="Moderator:", value=f"{author.mention}", inline=True)
        embed.add_field(name="Slowmode set to:", value=f"{seconds} seconds", inline=False)
        embed.set_thumbnail(url=author.avatar_url)
        embed.timestamp = datetime.utcnow()
        await the_channel.send(embed=embed)

    except:
        pass
    



#lock the channel
@bot.command(description = "Locks a channel.")
@commands.has_permissions(manage_channels = True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    embed = discord.Embed(title="Channel Locked", description=f"{ctx.channel.mention} is now in lockdown.", color=0xD708CC)
    embed.timestamp = datetime.utcnow()
    await ctx.send(embed=embed)

    try:

        the_guild = ctx.guild
        author = ctx.author
        the_channel = discord.utils.get(the_guild.text_channels, name="mod-logs")
        embed = discord.Embed(title="Channel Locked", color=0xD708CC)
        embed.add_field(name="Moderator", value=f"{author.mention}", inline=True)
        embed.add_field(name="Channel", value=f"{ctx.channel.mention}", inline=False)
        embed.set_thumbnail(url=author.avatar_url)
        embed.timestamp = datetime.utcnow()
        await the_channel.send(embed=embed)

    except:
        pass

#unlock the channel
@bot.command(description = "Unlock a channel.")
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    embed = discord.Embed(title="Channel Unlocked", description=f"{ctx.channel.mention} has been unlocked.", color=0xD708CC)
    embed.timestamp = datetime.utcnow()
    await ctx.send(embed=embed)


    try:


        the_guild = ctx.guild
        author = ctx.author
        the_channel = discord.utils.get(the_guild.text_channels, name="mod-logs")
        embed = discord.Embed(title="Channel Unlocked", color=0xD708CC)
        embed.add_field(name="Moderator", value=f"{author.mention}", inline=True)
        embed.add_field(name="Channel", value=f"{ctx.channel.mention}", inline=False)
        embed.set_thumbnail(url=author.avatar_url)
        embed.timestamp = datetime.utcnow()
        await the_channel.send(embed=embed)

    except:
        pass



#disable embeds
# @bot.command(description="Syntax: +disable embed")
# @commands.cooldown(1, 10, commands.BucketType.user)
# @commands.has_permissions(administrator = True)
# async def disable(ctx, setting):
#     if setting == 'embed':
#         with open('embed.json', 'r') as f:
#             embed = json.load(f)
        
#         embed[str(ctx.guild.id)] = 0

#         with open('embed.json', 'w') as f:
#             json.dump(embed, f, indent=4)
#     embed = discord.Embed(title="Embeds Disabled", description=f"The setting `{setting}` has been disabled.", color=3447003)
#     embed.timestamp = datetime.utcnow()
#     await ctx.send(embed=embed)
#     await bot.process_commands(message)

#     the_guild = ctx.guild
#     author = ctx.author
#     the_channel = discord.utils.get(the_guild.text_channels, name="mod-logs")
#     embed = discord.Embed(title="Embeds Disabled", color=3447003)
#     embed.add_field(name="Moderator:", value=f"{author.mention}", inline=True)
#     embed.set_thumbnail(url=author.avatar_url)
#     embed.timestamp = datetime.utcnow()
#     await the_channel.send(embed=embed)



#enable embeds
# @bot.command(description="Syntax: +enable embed")
# @commands.cooldown(1, 10, commands.BucketType.user)
# @commands.has_permissions(administrator = True)
# async def enable(ctx, setting):
#     if setting == 'embed':
#         with open('embed.json', 'r') as f:
#             embed = json.load(f)
        
#         embed[str(ctx.guild.id)] = 1

#         with open('embed.json', 'w') as f:
#             json.dump(embed, f, indent=4)
#     embed = discord.Embed(title="Embeds Disabled", description=f"The setting `{setting}` has been enabled.", color=3447003)
#     await bot.process_commands(message)
#     embed.timestamp = datetime.utcnow()
#     await ctx.send(embed=embed)

#     the_guild = ctx.guild
#     author = ctx.author
#     the_channel = discord.utils.get(the_guild.text_channels, name="mod-logs")
#     embed = discord.Embed(title="Embeds Enabled", color=3447003)
#     embed.add_field(name="Moderator:", value=f"{author.mention}", inline=True)
#     embed.set_thumbnail(url=author.avatar_url)
#     embed.timestamp = datetime.utcnow()
#     await the_channel.send(embed=embed)


#open embed.json to put the default embed (1)
# @bot.event
# async def on_guild_join(guild):

#     with open("embed.json", "r") as f:
#         embed = json.load(f)

#     embed[str(guild.id)] = 1

#     with open('embed.json', 'w') as f:
#         json.dump(embed, f, indent=4)



#find join guild
@bot.event
async def on_guild_join(guild):
    channel = bot.get_channel(875084449119891459)

    e = discord.Embed(title="I've joined a server.")
    e.add_field(name="Server Name:", value=guild.name, inline=False)
    e.set_thumbnail(url=guild.icon_url)
    e.timestamp = datetime.utcnow()
    await channel.send(embed=e)


#find remove guild
@bot.event
async def on_guild_remove(guild):
    channel = bot.get_channel(875084449119891459)

    e = discord.Embed(title="I've left a server.")
    e.add_field(name="Server Name:", value=guild.name, inline=False)
    e.set_thumbnail(url=guild.icon_url)
    e.timestamp = datetime.utcnow()
    await channel.send(embed=e)
    

#DM owner when get suggested to add a bad word
@bot.command(description="Suggest bad words for the developers to add.")
async def add(ctx, *, badword):
    msg_dump_channel = 861002914848047105

    channel = bot.get_channel(861002914848047105)
    embed = discord.Embed(title="Bad Word Suggested", description=f"{ctx.author.mention} has suggested **{badword}** to be added.", color=0xD708CC)
    embed.timestamp = datetime.utcnow()
    await channel.send(embed=embed)

    embed = discord.Embed(title="Bad Word Suggested", description="Your bad word suggestion has been sent to the developers.", color=0xD708CC)
    embed.timestamp = datetime.utcnow()
    await ctx.send(embed=embed)


#change bot's status to idle
@bot.command()
@commands.is_owner()
async def idle(ctx):
    await bot.change_presence(status=discord.Status.idle)
    await ctx.send("Status changed to `idle`.")

#change bot's status to online
@bot.command()
@commands.is_owner()
async def online(ctx):
    await bot.change_presence(status=discord.Status.online)
    await ctx.send("Status changed to `online`.")


#change bot's status to dnd
@bot.command()
@commands.is_owner()
async def dnd(ctx):
    await bot.change_presence(status=discord.Status.dnd)
    await ctx.send("Status changed to `dnd`.")

#change bot's status to invisible
@bot.command()
@commands.is_owner()
async def invisible(ctx):
    await bot.change_presence(status=discord.Status.invisible)
    await ctx.send("Status changed to `invisible`.")


@bot.command(description="Need help? Use this command and provide a reason.")
@has_permissions(administrator=True)
async def helpme(ctx, reason):
    await ctx.send("Please note that this command is only for help and not for advertising Discord servers or any products.")
    await ctx.send("Creating Invite so a staff member can join.")
    channel = ctx.message.channel
    invite = await channel.create_invite()

    channel = bot.get_channel(872858303804350464)

    await channel.send(f"{ctx.author.mention} used the `helpme` command in in **{ctx.guild.name}**. Reason: **{reason}**    Invite:  {invite}")


#send webhooks
# from discord import Webhook, AsyncWebhookAdapter
# import aiohttp

# @bot.command()
# async def webhook_send(ctx):
#     async with aiohttp.ClientSession() as session:
#         webhook = Webhook.from_url('Webhook_URL', adapter=AsyncWebhookAdapter(session))

#         e = discord.Embed(title="Title", description="Description")
#         e.add_field(name="Test1", value="Test2")
#         e.add_field(name="Test3", value="Test4")

#         await webhook.send(embed=e)



@bot.command(description="Debug the bot to get it's permissions that are enabled and disabled.")
async def debug(ctx):
    embed = discord.Embed(title="Permissions", description=f"{dict(ctx.me.guild_permissions)}", color=0xD708CC)
    embed.timestamp = datetime.utcnow()
    await ctx.send(embed=embed)

    


#make bot send msg when bot joins server
@bot.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            embed = discord.Embed(title="Thanks for inviting me!", description="Thanks for inviting me! Profanity Blocker is a bot that keeps your server safe by deleting messages that contain bad words. My default prefix is `+`. You can also use my mention as a secondary prefix. You can view our website for more details on this bot. Website: https://profanityblocker.org.", color=0xD708CC)
            embed.timestamp = datetime.utcnow()
            await channel.send(embed=embed)
        break

#logging system
@bot.listen()
async def on_message_edit(before, after):
    if before.content == after.content:
        return

    try: 
        the_guild = before.guild
        the_channel = discord.utils.get(the_guild.text_channels, name="mod-logs")
        the_author = before.author
        if the_author.bot == True:
            return

        embed = discord.Embed(title="Message Edited", description=f"Message edited by {after.author.mention} in {after.channel.mention}", color=3447003)
        embed.add_field(name="Before Edit", value=f"{before.content}", inline=False)
        embed.add_field(name="After Edit", value=f"{after.content}", inline=False)
        embed.add_field(name="Author's ID", value=f"{after.author.id}", inline=False)
        embed.add_field(name="Message link", value=f"{after.jump_url}", inline=False)
        embed.timestamp = datetime.utcnow()
        await the_channel.send(embed=embed)

    except:
        pass




@bot.listen()
async def on_raw_message_delete(payload):
    msg=payload.cached_message

    if msg.author == bot.user:
        return
    if msg.author.bot: 
        return
        
    try:
        the_guild = msg.guild
        the_channel = discord.utils.get(the_guild.text_channels, name="mod-logs")
        the_author = msg.author
        if msg.author == True:
            return
        embed = discord.Embed(title="Deleted Message", description=f"Message deleted by {msg.author.mention} in {msg.channel.mention}", color=15158332)
        embed.add_field(name="Deleted Message", value=f"{msg.content}", inline=False)
        embed.add_field(name="Author's ID", value=f"{msg.author.id}", inline=False)
        embed.timestamp = datetime.utcnow()
        await the_channel.send(embed=embed)

    except:
        pass



symbols = string.punctuation + string.digits
letters = string.ascii_letters

with open("test.txt") as file:
    test2 = file.read().split('\n')

@bot.listen("on_message")
async def on_message(message):
    if message.author == bot.user:
        return
    if message.author.bot: 
        return

    guild = message.guild
    bypassedRole = discord.utils.get(guild.roles, name="Bypassed")


    if bypassedRole in message.author.roles:
        return

    for word in test2:
        regex_match_true = re.compile(fr"[{symbols}]*".join(list(word)), re.IGNORECASE)
        regex_match_none = re.compile(fr"([{letters}]+{word})|({word}[{letters}]+)", re.IGNORECASE)
        if regex_match_true.search(message.content) and regex_match_none.search(message.content) is None:
            await message.delete()
            embed = discord.Embed(title="Message Deleted", color=0xD708CC, description= f"{message.author.mention}, You're not allowed to say that.")
            embed.timestamp = datetime.utcnow()
            await message.channel.send(embed=embed)


            the_guild = message.guild
            the_channel = discord.utils.get(the_guild.text_channels, name="badword-logs")
            the_author = message.author

            embed = discord.Embed(title="Bad Word Blocked", description=f"{message.author.mention} sent a bad word", color=15158332)
            embed.add_field(name="Blocked Message", value=f"{message.content}", inline=False)
            embed.add_field(name="Channel", value=f"{message.channel.mention}", inline=False)
            embed.timestamp = datetime.utcnow()
            await the_channel.send(embed=embed)

    


with open("badwords.txt", encoding="utf8") as file:
    blacklist = file.read().split('\n')

@bot.event
async def on_message(message):
    message.content = message.content.lower()
    message.content = discord.utils.remove_markdown(message.content)
    if message.author == bot.user:
        return
    if message.author.bot: 
        return

    guild = message.guild
    bypassedRole = discord.utils.get(guild.roles, name="Bypassed")


    if bypassedRole in message.author.roles:
        await bot.process_commands(message)
        return

    for word in blacklist:
        if message.content.count(word) > 0:
            await message.delete()
            embed = discord.Embed(title="Message Deleted", color=0xD708CC, description= f"{message.author.mention}, You're not allowed to say that.")
            embed.timestamp = datetime.utcnow()
            await message.channel.send(embed=embed)


            the_guild = message.guild
            the_channel = discord.utils.get(the_guild.text_channels, name="badword-logs")
            the_author = message.author

            embed = discord.Embed(title="Bad Word Blocked", description=f"{message.author.mention} sent a bad word", color=15158332)
            embed.add_field(name="Blocked Message", value=f"{message.content}", inline=False)
            embed.add_field(name="Channel", value=f"{message.channel.mention}", inline=False)
            embed.timestamp = datetime.utcnow()
            await the_channel.send(embed=embed)

    await bot.process_commands(message)



#can't bypass a edit with bad word
@bot.event
async def on_message_edit(before, after):
    if after.author == bot.user:
        return
    if after.author.bot: 
        return
    after.content = after.content.lower()
    after.content = discord.utils.remove_markdown(after.content)
    bypassedRole = discord.utils.get(after.guild.roles, name="Bypassed")

    if bypassedRole in after.author.roles:
        return

    for word in blacklist:
        if after.content.count(word) > 0:
            await after.delete()
            embed = discord.Embed(title="Message Deleted", color=0xD708CC, description= f"{after.author.mention}, You're not allowed to say that.")
            embed.timestamp = datetime.utcnow()
            await after.channel.send(embed=embed)


            the_guild = after.guild
            the_channel = discord.utils.get(the_guild.text_channels, name="badword-logs")
            the_author = after.author

            embed = discord.Embed(title="Bad Word Blocked", description=f"{after.author.mention} edited their message to a bad word", color=15158332)
            embed.add_field(name="Blocked Message", value=f"{after.content}", inline=False)
            embed.add_field(name="Channel", value=f"{after.channel.mention}", inline=False)
            embed.timestamp = datetime.utcnow()
            await the_channel.send(embed=embed)

        await bot.process_commands(after)





@bot.listen("on_message_edit")
async def on_message_edit(before, after):
    if after.author == bot.user:
        return
    if after.author.bot: 
        return
    after.content = after.content.lower()
    after.content = discord.utils.remove_markdown(after.content)
    bypassedRole = discord.utils.get(after.guild.roles, name="Bypassed")

    if bypassedRole in after.author.roles:
        return

    for word in test2:
        regex_match_true = re.compile(fr"[{symbols}]*".join(list(word)), re.IGNORECASE)
        regex_match_none = re.compile(fr"([{letters}]+{word})|({word}[{letters}]+)", re.IGNORECASE)
        if regex_match_true.search(after.content) and regex_match_none.search(after.content) is None:
            await after.delete()
            embed = discord.Embed(title="Message Deleted", color=0xD708CC, description= f"{after.author.mention}, You're not allowed to say that.")
            embed.timestamp = datetime.utcnow()
            await after.channel.send(embed=embed)


            the_guild = after.guild
            the_channel = discord.utils.get(the_guild.text_channels, name="badword-logs")
            the_author = after.author

            embed = discord.Embed(title="Bad Word Blocked", description=f"{after.author.mention} edited their message to a bad word", color=15158332)
            embed.add_field(name="Blocked Message", value=f"{after.content}", inline=False)
            embed.add_field(name="Channel", value=f"{after.channel.mention}", inline=False)
            embed.timestamp = datetime.utcnow()
            await the_channel.send(embed=embed)



@bot.command()
@commands.is_owner()
async def copy(ctx, *, arg):
    await ctx.send(f"{arg}")

@bot.command()
@commands.is_owner()
async def embedcopy(ctx, *, arg):
    embed = discord.Embed(title="", color=0xD708CC, description= f"{arg}")
    await ctx.send(embed=embed)


@bot.command()
@commands.has_permissions(manage_roles=True)
async def bypass(ctx, member: discord.Member):
    if member.bot:
        await ctx.send("Bot's are automatically bypassed!")
        return

    guild = ctx.guild
    bypassedRole = discord.utils.get(guild.roles, name="Bypassed")
    if bypassedRole in member.roles:
        return await ctx.send(f"{member.mention} is already bypassed!")

    try:    
        guild = ctx.guild
        bypassedRole = discord.utils.get(guild.roles, name="Bypassed")
        await member.add_roles(bypassedRole)
        await ctx.send(f"{member.mention} is now bypassed!")
    except:
        pass

    if not bypassedRole:
        bypassedRole = await guild.create_role(name="Bypassed")
        await member.add_roles(bypassedRole)
        await ctx.send(f"{member.mention} is now bypassed!")

    the_guild = ctx.guild
    the_channel = discord.utils.get(the_guild.text_channels, name="mod-logs")
    the_author = ctx.author

    embed = discord.Embed(title="Member Bypassed", description=f"{member.mention} is now bypassed.", color=3447003)
    embed.add_field(name="Moderator", value=f"{ctx.author.mention}", inline=False)
    embed.timestamp = datetime.utcnow()
    await the_channel.send(embed=embed)




@bot.command()
@commands.has_permissions(manage_roles=True)
async def unbypass(ctx, member: discord.Member):
    if member.bot:
        await ctx.send("Bot's are automatically bypassed by default!")
        return

    guild = ctx.guild
    bypassedRole = discord.utils.get(ctx.guild.roles, name="Bypassed")
    if bypassedRole not in member.roles:
        return await ctx.send(f"{member.mention} has not been bypassed!")

    try:    
        guild = ctx.guild
        bypassedRole = discord.utils.get(ctx.guild.roles, name="Bypassed")
        await member.remove_roles(bypassedRole)
        await ctx.send(f"{member.mention} has been unbypassed!")
    except:
        pass


    the_guild = ctx.guild
    the_channel = discord.utils.get(the_guild.text_channels, name="mod-logs")
    the_author = ctx.author

    embed = discord.Embed(title="Member Unbypassed", description=f"{member.mention} has been unbypassed.", color=15158332)
    embed.add_field(name="Moderator", value=f"{ctx.author.mention}", inline=False)
    embed.timestamp = datetime.utcnow()
    await the_channel.send(embed=embed)



bot.loop.run_until_complete(create_db_pool())
bot.run("ODM5ODc5MjA1MjczMjA2Nzg0.YJQEdg.M-IGYZDAvRFmbe7-ESaI3xGnDLU")