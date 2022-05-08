# import os
import asyncio
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
it's a discord bot to download raws or stitch image.
'''
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=prefix, description=description,
        intents=intents)

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
    await ctx.typing()
    t2 = time.perf_counter()
    await ctx.send(f'Pong! {round((t2-t1)*1000)} ms')

async def main():
    cogs_to_load = ['cogs.cripper', 'cogs.merger']
    async with bot:
        for cog in cogs_to_load:
            await bot.load_extension(cog)
        await bot.start(TOKEN)

if __name__=='__main__':
    asyncio.run(main())
