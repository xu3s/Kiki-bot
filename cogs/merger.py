import asyncio
import tempfile
import zipfile
import os
from urllib import parse
import re

# import requests as req
import discord
from discord.ext import commands
import uptobox as dbx
from cogs import ijoiner
from cogs.misc_ext import presence_change
from config import conf

server = conf().SERVER_URL
tempfile.tempdir = conf().TEMPDIR

class ImageStitcher(commands.Cog):
    '''Stitch Image. from a zip file.'''

    def __init__(self,bot):
        self.bot = bot

    @commands.command(description='stitch image from a zip file. currently only support dropbox url') #pylint: disable=C0301
    async def stitch(self, ctx:commands.Context, zip_link=None, max_stitch=None):

        att = ctx.message.attachments
        print(zip_link)
        if not zip_link and not att:
            await ctx.reply('No link to zip or attachment found/specified')
            return

        loop = asyncio.get_running_loop()
        await asyncio.gather(loop.create_task(
            self.proccess_stitch(ctx, zip_link, att, max_stitch)))

    async def proccess_stitch(self, ctx:commands.Context, zip_link, att, max_stitch):
        tr = '[ \n]'
        try:
            max_stitch = int(max_stitch)
        except (ValueError,TypeError):
            max_stitch = None
       #  if att:
       # zip_link.extend([z.url for z in att if z.filename.endswith('.zip')])
        await presence_change(self.bot,'append')
        if zip_link:
            zip_link = re.sub(tr, ' ', zip_link).split(' ')
            for zl in zip_link:
                with tempfile.TemporaryDirectory() as tempdir:
                    os.chmod(tempdir, os.stat(tempfile.tempdir).st_mode)
                    print(f'tempd: {tempdir}')
                    if 'dropbox.com' in zl:
                        status, info, fp = dbx.download(zl,tempdir)
                        if status == 'success':

                            try:
                                with zipfile.ZipFile(fp,'r',zipfile.ZIP_DEFLATED) as zf:
                                    if max_stitch:
                                        nfp = ijoiner.zip_stitch(fp, max_stitch=max_stitch)
                                        await ctx.send(f'stitching... max_stitch:{max_stitch}', delete_after=30)
                                    else:
                                        print('extracting..')
                                        zf.extractall(path=tempdir)
                                        retry = 0
                                        while True:
                                            try:
                                                custom = await makelist(self.bot,ctx,tempdir,fp)
                                                break

                                            except Exception as e:
                                                retry += 1
                                                if retry >= 5:
                                                    print(f'error on mkl {e}')
                                                    await ctx.reply(f'failed loading file:\n {e}')
                                                    await presence_change(self.bot, 'substract')
                                                    return e
                                        if custom['status'] == 'success':
                                            print('process stitching..')
                                            await ctx.send('stitching...', delete_after=30)
                                            nfp = ijoiner.zip_stitch(fp, custom=custom['result'])
                                        else:
                                            await ctx.reply('operation canceled!')
                                            break
                                    # run in task maybe??
                                    up = dbx.upload(nfp, '/stitched', False)
                                    await ctx.reply(up)

                            except Exception as e:
                                await ctx.reply(f'error processing {zl}: \n {e}')
                                await presence_change(self.bot,'substract')
                                raise e
                        else:
                            await ctx.reply(f'failed to fetch file\nerr:{info}')
                    elif 'cdn.discordapp.com' in zl:
                        await ctx.reply(zl)
                    else:
                        print('not implemented yet')
                        await ctx.reply('feature not implemented yet')

                print(f'^^{bcolors.OKBLUE}requester: {ctx.author}{bcolors.ENDC}')
        await presence_change(self.bot,'substract')


        # await presence_change(self.bot, 'substract')

        # await ctx.send(f'att: {att}, \n zip_link: {zip_link}')
        # await ctx.send([f'{a.filename} {a.id} {a.url}' for a in att])

async def makelist(bot:commands.Bot,ctx:commands.Context,temp_d, temp_f):
    result = {}
    sl = []
    stop = False
    status = 'success'
    info = 'makelist done'
    print(temp_d)
    msg = None
    zfd = ijoiner.get_zfl(temp_f)
    print(f'zfd keys: {zfd.keys()}')
    for fol in zfd.keys():
        ranges = zfd[fol]
        result[fol] = []
        for d in ranges:
            skip = False
            print(d)
            im_url=os.path.join(server, os.path.basename(temp_d), d)
            print(im_url)
            misc={'folder':fol,'sl':sl,'url':im_url}
            while True:
                if not msg:
                    msg, response = await reactor(bot=bot,ctx=ctx,misc=misc)
                else:
                    response = await reactor(bot=bot,ctx=ctx,misc=misc,saved=msg)

                print(response)
                if response == 'append':
                    sl.append(d)
                if response == 'next':
                    result[fol].append(sl.copy())
                    sl.clear()
                    sl.append(d)
                if response in ['stop','cancel']:
                    stop = True
                if response == 'skip':
                    skip = True
                if d == ranges[-1]:
                    result[fol].append(sl.copy())
                    sl.clear()
                break
            if stop or skip:
                result[fol].append(sl.copy())
                sl.clear()
                break
        if stop:
            status = 'stopped'
            break
    await msg.delete()
    if not [x for x in result.values() if any(x)] and not stop:
        await ctx.reply('All skipped or none was selected.')
        status, info='skipped', 'Skipped or none was selected.'

    print(f'result: {result}')
    return {'status':status, 'result':result, 'info':info}

async def reactor(bot,ctx:commands.Context,misc,saved:commands.Context=None):#pylint: disable=R0914,R0913

    d = os.path.basename(misc['url'])
    misc['sl'] = [os.path.basename(p) for p in misc['sl']]
    reactions = ['⏫','⏭️']
    state = f'Current folder: {misc["folder"]}\nCurrent list:{misc["sl"]}\nimage: {d}'
    embed = discord.Embed(title='image selector',description=state)
    embed.set_image(url=parse.quote(misc['url'],safe=':/'))
    instructions = 'react with ⏫ = add to stitch, ⏭️= add to next list.\ntype "stop" to abort. type "skip" to skip folder.'
    embed.set_footer(text=instructions)

    if not saved:
        message = await ctx.reply(embed=embed)
        for react in reactions:
            await message.add_reaction(react)
    else:
        message = saved
        await message.edit(embed=embed)

    def check(reaction,user):
        return user == ctx.author and str(reaction) in reactions
    def check_msg(msg):
        return msg.author == ctx.author

    try:
        done, pending = await asyncio.wait([
            asyncio.create_task(bot.wait_for(
                'reaction_add', check=check, timeout=30)),
            asyncio.create_task(bot.wait_for('message', check=check_msg))
        ], return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()
        event = next(x.result() for x in done)

        if isinstance(event, discord.Message):
            await event.delete()
            if not saved:
                return message, event.content.lower()
            return event.content.lower()

        reaction, user = event

        if str(reaction.emoji) =='⏫':
            # await ctx.send(f'{d} added', delete_after=30)
            cmd = 'append'
        if str(reaction.emoji) =='⏭️':
            # await ctx.send(f'{d} added to a new list', delete_after=30)
            cmd = 'next'
        await message.remove_reaction(reaction, user)
        if not saved:
            return message, cmd
        return cmd
    except asyncio.TimeoutError:
        await ctx.send('time is up!. Canceling...', delete_after=35)
        if not saved:
            return None, 'stop'
        return 'stop'

async def stitch_up(ctx,zfp,custom):
    ijoiner.zip_stitch(zfp, custom=custom)
    retry = 0
    while True:
        try:
            up = dbx.upload(zfp, '/stitched', False)
            await ctx.reply(up)
            break
        except Exception as e:
            retry += 1
            if retry >= 5:
                print(f'failed to upload file. \n e: {e}')
                await ctx.reply(f'failed to upload the file Please try again. \n error:{e}')
                break

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
    bot.add_cog(ImageStitcher(bot))
