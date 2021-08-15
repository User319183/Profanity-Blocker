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
    bot.db = await asyncpg.create_pool(database = "problock", user = "postgres", password= "12345678" )
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
async def setprefix(ctx, prefix):
    await bot.db.execute('UPDATE guilds SET prefix = $1 WHERE guild_id = $2', prefix, ctx.guild.id)
    await ctx.send(f"The prefix has been updated! New prefix: `{prefix}`")

    try:
        the_channel = discord.utils.get(ctx.guild.text_channels, name="mod-logs")
        embed = discord.Embed(title="Prefix Updated", color=0xD708CC)
        embed.add_field(name="Moderator:", value=f"{ctx.author.mention}", inline=True)
        embed.add_field(name="New Prefix:", value=f"{prefix}", inline=True)
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


@bot.command(description = "The help panel for moderation commands.")
async def helpmoderation(ctx):
    embed = discord.Embed(title="Help Moderation Commands", color=0xD708CC, description= f"1. ban \n 2. unban \n 3. mute \n 4. unmute \n 5. warn \n 6. lock \n 7. unlock \n 8. slowmode \n 9. kick \n 10. clear \n 11. bypass \n 12. unbypass \n 13. add")
    await ctx.send(embed=embed)


#shutdown bot
@bot.command(description = "Shutsdown the bot.")
@commands.is_owner()
async def shutdown(ctx):
    embed = discord.Embed(title="Shutting down.", color=0xD708CC, description="Shutting down. This will take up to two minute.")
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


@bot.command(description = "Vote for the bot on Top.GG")
async def vote(ctx):
    embed = discord.Embed(title="Top.GG Vote", description="You can vote for the bot on Top.GG! Here's the link https://top.gg/bot/834812191277973564", color=0xD708CC)
    await ctx.send(embed=embed)


#ban command
@bot.command(description = "Ban the user.")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member, *, reason='None'):
    if reason is None:
        reason = "Not specificed."
    try:
        await ctx.guild.ban(discord.Object(id=member), reason=reason)
    except Exception as e:
        return
    embed = discord.Embed(title="Member Banned", description=f"**{member}**, has been banned..", color=0xD708CC)
    embed.timestamp = datetime.utcnow()
    await ctx.send(embed=embed)

    try:
        the_channel = discord.utils.get(ctx.guild.text_channels, name="mod-logs")
        embed = discord.Embed(title="Member Banned", color=0xD708CC)
        embed.add_field(name="Member's ID:", value=f"{member}", inline=True)
        embed.add_field(name="Moderator:", value=f"{ctx.author.mention}", inline=True)
        embed.add_field(name="Reason:", value=f"{reason}", inline=False)
        embed.timestamp = datetime.utcnow()
        await the_channel.send(embed=embed)

    except:
        pass



#unban command
@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user: discord.User, *, reason='Reason has not been specified.'):
    guild = ctx.guild
    try:
        await guild.unban(user, reason=reason)
    except exception as e:
        return await ctx.send(e)
    embed = discord.Embed(title="Member Unbanned", description=f"**{user}**, has been unbanned.", color=0xD708CC)
    embed.timestamp = datetime.utcnow()
    await ctx.send(embed=embed)

    try:
        logchannel = discord.utils.get(ctx.guild.text_channels, name="mod-logs")
        embed = discord.Embed(title="Member Unbanned", color=0xD708CC)
        embed.add_field(name="Member's ID:", value=f"{user}", inline=True)
        embed.add_field(name="Moderator:", value=f"{ctx.author.mention}", inline=True)
        embed.add_field(name="Reason:", value=f"{reason}", inline=False)
        embed.timestamp = datetime.utcnow()
        await logchannel.send(embed=embed)

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
        logchannel = discord.utils.get(ctx.guild.text_channels, name="mod-logs")
        embed = discord.Embed(title="Messages Cleared", color=0xD708CC)
        embed.add_field(name="Moderator:", value=f"{ctx.author.mention}", inline=True)
        embed.add_field(name="Amount Of Cleared Messages:", value=f"{len(deleted)}/{num} messages", inline=False)
        embed.timestamp = datetime.utcnow()
        await logchannel.send(embed=embed)
    except:
        pass


#warn command
@bot.command(description = "Warn a Discord member")
@commands.has_permissions(manage_roles=True)
async def warn(ctx, member:discord.Member, *, reason='Reason has not been specified.'):
    if member.bot:
        await ctx.send("Bot's are not allowed to be warned!")
        return


    warnedRole = discord.utils.get(ctx.guild.roles, name="Warned")

    if not warnedRole:
        warnedRole = await guild.create_role(name="Warned")
    embed = discord.Embed(title=f"Member Warned", description=f"{member.mention} has successfully been warned.", colour=discord.Colour.blue())
    await member.add_roles(warnedRole, reason=reason)
    embed.timestamp = datetime.utcnow()
    await ctx.send(embed=embed)

    try:
        logchannel = discord.utils.get(ctx.guild.text_channels, name="mod-logs")
        embed = discord.Embed(title="Member Warned", color=0xD708CC)
        embed.add_field(name="Member", value=f"{member.mention}", inline=True)
        embed.add_field(name="Moderator", value=f"{ctx.author.mention}", inline=True)
        embed.add_field(name="Reason", value=f"{reason}", inline=False)
        embed.set_thumbnail(url=member.avatar_url)
        embed.timestamp = datetime.utcnow()
        await logchannel.send(embed=embed)

    except:
        pass





#Mute command
@bot.command(description="Mutes a specified user.")
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, *, reason='Reason has not been specified.'):
    if member.bot:
        await ctx.send("Bot's are not allowed to be muted!")
        return

    mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")

    if not mutedRole:
        mutedRole = await ctx.guild.create_role(name="Muted")

        for channel in guild.channels:
            await channel.set_permissions(mutedRole, speak=False, send_messages=False, read_message_history=True, read_messages=False)
    embed = discord.Embed(title="Muted", description=f"{member.mention} was muted.", colour=discord.Colour.blue())
    embed.timestamp = datetime.utcnow()
    await ctx.send(embed=embed)
    await member.add_roles(mutedRole, reason=reason)


    try:
        logchannel = discord.utils.get(ctx.guild.text_channels, name="mod-logs")
        embed = discord.Embed(title="Member Muted", color=0xD708CC)
        embed.add_field(name="Member:", value=f"{member.mention}", inline=True)
        embed.add_field(name="Moderator:", value=f"{ctx.author.mention}", inline=True)
        embed.add_field(name="Reason:", value=f"{reason}", inline=False)
        embed.set_thumbnail(url=member.avatar_url)
        embed.timestamp = datetime.utcnow()
        await logchannel.send(embed=embed)

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
        logchannel = discord.utils.get(ctx.guild.text_channels, name="mod-logs")
        embed = discord.Embed(title="Member Unmuted", color=0xD708CC)
        embed.add_field(name="Member", value=f"{ctx.author.mention}", inline=True)
        embed.add_field(name="Moderator", value=f"{author.mention}", inline=True)
        embed.add_field(name="Reason", value=f"{reason}", inline=False)
        embed.set_thumbnail(url=member.avatar_url)
        embed.timestamp = datetime.utcnow()
        await logchannel.send(embed=embed)

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
        logchannel = discord.utils.get(ctx.guild.text_channels, name="mod-logs")
        embed = discord.Embed(title="Member Kicked", color=0xD708CC)
        embed.add_field(name="Member", value=f"{member.mention}", inline=True)
        embed.add_field(name="Moderator", value=f"{author.mention}", inline=True)
        embed.add_field(name="Reason", value=f"{reason}", inline=False)
        embed.set_thumbnail(url=member.avatar_url)
        embed.timestamp = datetime.utcnow()
        await logchannel.send(embed=embed)

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
        logchannel = discord.utils.get(ctx.guild.text_channels, name="mod-logs")
        embed = discord.Embed(title="Slowmode:", color=0xD708CC)
        embed.add_field(name="Moderator:", value=f"{ctx.author.mention}", inline=True)
        embed.add_field(name="Slowmode set to:", value=f"{seconds} seconds", inline=False)
        embed.set_thumbnail(url=author.avatar_url)
        embed.timestamp = datetime.utcnow()
        await logchannel.send(embed=embed)

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
        logchannel = discord.utils.get(ctx.guild.text_channels, name="mod-logs")
        embed = discord.Embed(title="Channel Locked", color=0xD708CC)
        embed.add_field(name="Moderator", value=f"{ctx.author.mention}", inline=True)
        embed.add_field(name="Channel", value=f"{ctx.channel.mention}", inline=False)
        embed.set_thumbnail(url=author.avatar_url)
        embed.timestamp = datetime.utcnow()
        await logchannel.send(embed=embed)

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
        logchannel = discord.utils.get(ctx.guild.text_channels, name="mod-logs")
        embed = discord.Embed(title="Channel Unlocked", color=0xD708CC)
        embed.add_field(name="Moderator", value=f"{ctx.author.mention}", inline=True)
        embed.add_field(name="Channel", value=f"{ctx.channel.mention}", inline=False)
        embed.set_thumbnail(url=author.avatar_url)
        embed.timestamp = datetime.utcnow()
        await logchannel.send(embed=embed)

    except:
        pass



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



@bot.command(description="Debug the bot to get it's permissions that are enabled and disabled.")
async def debug(ctx):
    embed = discord.Embed(title="Permissions", description=f"{dict(ctx.me.guild_permissions)}", color=0xD708CC)
    embed.timestamp = datetime.utcnow()
    await ctx.send(embed=embed)



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

    bypassedRole = discord.utils.get(guild.roles, name="Bypassed")
    if bypassedRole in member.roles:
        return await ctx.send(f"{member.mention} is already bypassed!")

    try:    
        bypassedRole = discord.utils.get(guild.roles, name="Bypassed")
        await member.add_roles(bypassedRole)
        await ctx.send(f"{member.mention} is now bypassed!")
    except:
        pass

    if not bypassedRole:
        bypassedRole = await guild.create_role(name="Bypassed")
        await member.add_roles(bypassedRole)
        await ctx.send(f"{member.mention} is now bypassed!")

    logchannel = discord.utils.get(ctx.guild.text_channels, name="mod-logs")

    embed = discord.Embed(title="Member Bypassed", description=f"{member.mention} is now bypassed.", color=3447003)
    embed.add_field(name="Moderator", value=f"{ctx.author.mention}", inline=False)
    embed.timestamp = datetime.utcnow()
    await logchannel.send(embed=embed)




@bot.command()
@commands.has_permissions(manage_roles=True)
async def unbypass(ctx, member: discord.Member):
    if member.bot:
        await ctx.send("Bot's are automatically bypassed by default!")
        return

    bypassedRole = discord.utils.get(ctx.guild.roles, name="Bypassed")
    if bypassedRole not in member.roles:
        return await ctx.send(f"{member.mention} has not been bypassed!")

    try:    
        bypassedRole = discord.utils.get(ctx.guild.roles, name="Bypassed")
        await member.remove_roles(bypassedRole)
        await ctx.send(f"{member.mention} has been unbypassed!")
    except:
        pass


    logchannel = discord.utils.get(ctx.guild.text_channels, name="mod-logs")

    embed = discord.Embed(title="Member Unbypassed", description=f"{member.mention} has been unbypassed.", color=15158332)
    embed.add_field(name="Moderator", value=f"{ctx.author.mention}", inline=False)
    embed.timestamp = datetime.utcnow()
    await logchannel.send(embed=embed)



bot.loop.run_until_complete(create_db_pool())
bot.run("") # your token here
