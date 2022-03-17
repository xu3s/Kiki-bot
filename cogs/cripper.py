import asyncio
import discord
from discord.ext import commands
from ccrawlerv2 import Manga
from cogs import pager
from cogs.misc_ext import presence_change


class ComicCrawler(commands.Cog):#pylint: disable=too-few-public-methods
    '''Crawl comic'''

    def __init__(self, bot):
        self.bot = bot

    # @commands.command(pass_context=True)
    # @commands.has_role('role')
    @commands.command()
    async def get(self, ctx:commands.Context, slink=None, chapter=None):
        if not slink:
            await ctx.reply('series Url is not specified')
            return
        slink = check_link(slink)
        manga = Manga(ctx)
        await ctx.send('Processing... Please wait!')
        analyze = manga.manga(slink)
        if analyze:
            await ctx.reply(analyze)
            return
        title = f'title: {manga.mission.title} \nhas {len(manga.mission.episodes)} Chapter(s)'
        episodes = manga.mission.episodes
        if len(episodes) == 0:
            await ctx.reply(f'Title: {title}\n No chapter available for download')
            return
        contents = [f'{i}.] {ep.title}' for i,ep in enumerate(episodes)]
        retry = 0
        while not isinstance(chapter, list):
            if retry >= 3:
                await ctx.reply("invalid answer for 3 times, so aborting!")
                return
            retry += 1
            if not chapter:
                chapter = await pager.pager(self.bot, ctx, title, contents)
            elif chapter == 'cancel':
                await ctx.reply('Aborted!!!')
                return
            else:
                try:
                    chapter = chan_gen(chapter)
                except ValueError:
                    await ctx.reply('Invalid Chapter!\nsee chapter list below')
                    chapter = await pager.pager(self.bot, ctx, title, contents)

            # await ctx.reply('Chapter number is invalid!')
            #     return
        loop = asyncio.get_running_loop()

        await asyncio.gather(loop.create_task(self.process(ctx,manga,chapter)))


    async def process(self,ctx:commands.Context,manga,chapter):

        await ctx.reply(f'Processing to dowload ***{",".join([str(a) for a in chapter])}*** Please wait!')
        # await self.bot.change_presence(activity=discord.Activity(
        #     type=discord.ActivityType.watching, name='Currently Downloading'))
        await presence_change(self.bot, 'append')
        for epl in manga.mdownload(chapter):
            await ctx.reply(epl)
            print(f'epl: {epl}')
        await ctx.reply('Done!')
        print(f'{bcolors.OKBLUE}requester: {ctx.author}{bcolors.ENDC}')
        await presence_change(self.bot, 'substract')
        # await self.bot.change_presence(activity=discord.Activity(
        #     type=discord.ActivityType.watching, name='Its ok to use'))



def check_link(link):

    if 'm.ac.qq.com' in link:
        sid = link[link.rfind('/')+1:].strip()
        link = f'https://ac.qq.com/Comic/comicInfo/id/{sid}'
    return link

def chan_gen(strnum):
    """ Generate chapter number from format 1,3-4,6
    or something like that
    :return: list of number [1,3,4,6]
    """
    strnum = str(strnum).strip().replace(' ', '')
    if "," in strnum:
        a = strnum.split(',')
    else:
        a = [strnum]
    result = []
    for x in a:
        if '-' in x:
            xr = x.split('-')
            for b in range(int(xr[0]), int(xr[1])+1):
                if b not in result:
                    result.append(b)
            continue
        if int(x) not in result:
            result.append(int(x))
    return result

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def setup(bot):
    bot.add_cog(ComicCrawler(bot))
