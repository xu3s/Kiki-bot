import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from cogs.misc_ext import presence_change

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
prefix = os.getenv('DISCORD_PREFIX')
print(f'prefix: {prefix}')
bot = commands.Bot(command_prefix=prefix, description='hello world')

@bot.event
async def on_ready():
    print('Logged in as:')
    print(bot.user.name)
    print(bot.user.id)
    print('-----------')
    await presence_change(bot)

if __name__=='__main__':
    cogs_to_load = ['cogs.cripper', 'cogs.merger']
    for cog in cogs_to_load:
        bot.load_extension(cog)
    bot.run(TOKEN)
