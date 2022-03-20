import os
from dotenv import load_dotenv

load_dotenv()
class conf:
    '''Config load helper.'''
    def __init__(self):
        self.DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
        self.PREFIX = os.getenv('DISCORD_PREFIX')
        self.DROPBOX_TOKEN = os.getenv('DROPBOX_TOKEN')
        self.SERVER_URL = os.getenv('SERVER_URL')
        self.TEMPDIR = os.getenv('TEMPDIR')
