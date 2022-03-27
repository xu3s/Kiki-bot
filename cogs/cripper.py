import asyncio
from discord.ext import commands
from ccrawlerv3 import Manga
from cogs import pager
from cogs.misc_ext import presence_change
queue = asyncio.Queue()

class ComicCrawler(commands.Cog):
    '''Crawl comic'''

    def __init__(self, bot):
        self.manga:Manga
        self.bot = bot

    @commands.command()
    async def get(self, ctx:commands.Context, slink=None, chapter=None):
        if not slink:
            await ctx.reply('series Url is not specified')
            return
        slink = check_link(slink)
        manga = Manga(slink)
        self.manga = manga
        await ctx.send('Processing... Please wait!', delete_after=60)
        analyze = manga.manga()
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
                await ctx.reply("invalid answer for 3 times, so aborting!", delete_after=30)
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

        await presence_change(self.bot, 'append')
        try:
            await asyncio.gather(
                    self.process(ctx,chapter),
                    _queue_consumer(len(chapter))
                    )
            await ctx.reply('Done!')
        except Exception:
            await ctx.send('''
Unexepected error occured!.
did you delete your original message/commands''')
            await presence_change(self.bot,'substract')
            raise
        await presence_change(self.bot, 'substract')


    async def process(self,ctx:commands.Context,chapter):
        loop = asyncio.get_running_loop()
        await ctx.reply(f'''
Processing to dowload episode(s) ***{",".join([str(a) for a in chapter])}*** Please wait!
''')
        def _process_download():
            for epl in self.manga.mdownload(chapter):
                queue.put_nowait((ctx,epl))

        await loop.run_in_executor(None,_process_download)


async def _queue_consumer(ch_len):
    processed_item = 0
    while True:
        try:
            ctx, result = queue.get_nowait()
            match result['status']:
                case 'ok':
                    message = f'''
File Name: {result['name']}
Download Url: {result['url']}
'''
                case 'error':
                    message = f'''
Error occured!
Info: {result['info']}
'''
                case _:
                    message = f'''
Unexepected error!.
{result}
'''
            await ctx.reply(message)
            processed_item += 1
        except asyncio.QueueEmpty:
            await asyncio.sleep(1)
        if processed_item >= ch_len:
            break

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
    strnum = str(strnum).strip().replace('- ', '-').replace(' -',
            '-').replace(', ',',').replace(' ,',',').replace(' ',',')
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

<<<<<<< HEAD
def setup(bot):
    bot.add_cog(ComicCrawler(bot))
=======
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


async def setup(bot):
    await bot.add_cog(ComicCrawler(bot))
>>>>>>> 4546770 (testing discord.py v2.0)
