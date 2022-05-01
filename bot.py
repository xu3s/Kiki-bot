import os
import time
import discord
from discord.ext import commands
# from discord.ext.commands.core import command
from cogs.misc_ext import presence_change
from config import conf

TOKEN = conf().DISCORD_TOKEN
prefix = conf().PREFIX
print(f'prefix: {prefix}')
description = '''
Kiki Ripper.
it's a discord bot that has utility for scanlation.
'''
bot = commands.Bot(command_prefix=prefix, description=description)

@bot.event
async def on_ready():
    print('Logged in as:')
    print(bot.user.name)
    print(bot.user.id)
    print('-----------')
    await presence_change(bot)

@bot.command()
async def ping(ctx:commands.Context):
    '''Ping the bot if it online or not.'''
    t1 = time.perf_counter()
    await ctx.trigger_typing()
    t2 = time.perf_counter()
    await ctx.send(f'Pong! {round((t2-t1)*1000)} ms')

if __name__=='__main__':
    cogs_to_load = ['cogs.cripper', 'cogs.merger']
    for cog in cogs_to_load:
        bot.load_extension(cog)
    bot.run(TOKEN)
