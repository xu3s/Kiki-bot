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
# intents = discord.Intents.default()
#intents.message_content = True
# intents.guild_messages = True
# intents.presences = True
# intents.guild_reactions = True
# intents.members = True
# intents.messages = True
#TODO: Use only required intents
intents = discord.Intents.all()
# bot = commands.Bot(command_prefix=prefix, description=description,
#         intents=intents)

class MyBot(commands.Bot):
    '''Setup Bot '''

    def __init__(self):
        super().__init__(
                command_prefix=commands.when_mentioned_or(prefix),
                intents=intents)

    async def on_ready(self):
        print('Logged in as:')
        print(self.user.name)
        print(self.user.id)
        print('-----------')
        await presence_change(self)


    # async def setup_hook(self) -> None:
    #     pass

bot = MyBot()

# @bot.event
# async def on_ready():
#     print('Logged in as:')
#     print(bot.user.name)
#     print(bot.user.id)
#     print('-----------')
#     await presence_change(bot)

@bot.command()
async def ping(ctx:commands.Context):
    '''Ping the bot if it online or not.'''
    t1 = time.perf_counter()
    await ctx.typing()
    t2 = time.perf_counter()
    await ctx.send(f'Pong! {round((t2-t1)*1000)} ms')

async def main():
    cogs_to_load = ['cogs.cripper', 'cogs.merger']
    # async with bot:
    for cog in cogs_to_load:
        await bot.load_extension(cog)
    await bot.start(TOKEN)

if __name__=='__main__':
    asyncio.run(main())
