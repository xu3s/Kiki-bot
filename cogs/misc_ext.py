import os
import sys
from datetime import datetime

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

class ForwardPrint:
    '''Forward print statement to file.'''
    def __init__(self,fname):
        self._original_stdout = sys.stdout
        self.fname = os.path.expanduser(f'~/.kiki-logs/{fname}')

    def __enter__(self):
        # if os.path.dirname(self.fname):
        os.makedirs(os.path.dirname(self.fname), exist_ok=True)
        sys.stdout = open(self.fname, 'a')
        print('--------------------------------')
        print(f'---START: {datetime.utcnow()}---')
        print('--------------------------------')


    def __exit__(self, exc_type, exc_val, exc_tb):
        print('--------------------------------')
        print(f'---END: {datetime.utcnow()}---')
        print('--------------------------------')
        sys.stdout.close()
        sys.stdout = self._original_stdout
