import os

import discord

async def presence_change(bot, op=None):
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, name=f'Processing {_process(op)} tasks'))

def _process(operation=None):
    p = os.getenv('N_REQUEST', '0')
    if operation == 'append':
        change = str(int(p)+1)
    elif operation == 'substract':
        change = str(int(p)-1)
    else:
        change = p
    os.environ['N_REQUEST'] = change
    return change
