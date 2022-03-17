import asyncio
import tempfile
import zipfile
import os
import re

# import requests as req
import discord
from discord.ext import commands
import uptobox as dbx
from cogs import ijoiner
from cogs.misc_ext import presence_change


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
        await presence_change(self.bot, 'append')
        await asyncio.gather(loop.create_task(
            self.proccess_stitch(ctx, zip_link, att, max_stitch)))
        await presence_change(self.bot, 'substract')

    async def proccess_stitch(self, ctx:commands.Context, zip_link, att, max_stitch):
        tr = '[ \n]'
        try:
            max_stitch = int(max_stitch)
        except (ValueError,TypeError):
            max_stitch = None
       #  if att:
       # zip_link.extend([z.url for z in att if z.filename.endswith('.zip')])
        # await presence_change(self.bot, 'append')
        if zip_link:
            zip_link = re.sub(tr, ' ', zip_link).split(' ')
            for zl in zip_link:
                with tempfile.TemporaryDirectory() as tempdir:
                    if 'dropbox.com' in zl:
                        status, info, fp = dbx.download(zl,tempdir)
                        if status == 'success':

                            try:
                                with zipfile.ZipFile(fp,'r',zipfile.ZIP_DEFLATED) as zf:
                                    # loop = asyncio.get_running_loop()
                                    # print(zf.filelist)
                                    if max_stitch:
                                        ijoiner.zip_stitch(fp, max_stitch=max_stitch)
                                    else:
                                        retry = 0
                                        while True:
                                            try:
                                                custom = await makelist(self.bot,ctx,fp, zf)
                                                break

                                            except Exception as e:
                                                retry += 1
                                                if retry >= 5:
                                                    print(f'error on mkl {e}')
                                                    await ctx.reply(f'failed loading file:\n {e}')
                                                    return e
                                        # print(custom)
                                        # return
                                        if custom['status'] == 'success':
                                            ijoiner.zip_stitch(fp, custom=custom['result'])
                                        else:
                                            await ctx.reply('operation canceled!')
                                            break
                                    # run in task maybe??
                                    up = dbx.upload(fp, '/stitched', False)
                                    await ctx.reply(up)

                            except Exception as e:
                                print(e)
                                await ctx.reply(f'error processing {zl}: \n {e}')
                        else:
                            await ctx.reply(f'failed to fetch file\nerr:{info}')
                    elif 'cdn.discordapp.com' in zl:
                        await ctx.reply(zl)
                    else:
                        print('not implemented yet')
                        await ctx.reply('feature not implemented yet')

                print(f'^^{bcolors.OKBLUE}requester: {ctx.author}{bcolors.ENDC}')

        # await presence_change(self.bot, 'substract')

        # await ctx.send(f'att: {att}, \n zip_link: {zip_link}')
        # await ctx.send([f'{a.filename} {a.id} {a.url}' for a in att])

async def makelist(bot:commands.Bot,ctx:commands.Context,temp_f,zf):
    result = {}
    sl = []
    stop = False
    status = 'success'
    print(temp_f)
    zfd = ijoiner.get_zfl(temp_f)
    for fol in zfd.keys():
        ranges = zfd[fol]
        print(f'fol:{fol},\nranges:{ranges}')
        result[fol] = []
        for d in ranges:
            skip = False
            print(d)
            while True:
                response = await reactor(bot=bot,ctx=ctx,fp=d,zf=zf,curfol=fol)
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
                break
            print(f'd:{d}, ml:{ml}, sl:{sl}')
        if stop:
            status = 'stopped'
            break
    if [x for x in result.values() if x]:
        await ctx.reply('All skipped or none was selected.')
        status, info='skipped', 'Skipped or none was selected.'

    return {'status':status, 'result':result, 'info':info}

async def reactor(bot,ctx:commands.Context,fp,zf,curfol):#pylint: disable=R0914

    d = os.path.basename(fp)
    print(fp)
    reactions = ['⏫','⏭️']
    state = f'current folder: {curfol}\nimage:{d}'
    embed = discord.Embed(title='image selector',description=state)
    embed.set_image(url=f'attachment://{d}')
    embed.set_footer(text='react with ⏫ = add, ⏭️= add to next list.\ntype stop or cancel to stop')

    message = await ctx.reply(embed=embed,file=discord.File(zf.open(fp,'r'),d))
    for react in reactions:
        await message.add_reaction(react)
    # await message.add_reaction('👍')
    # await message.add_reaction('⏭️')
    # await message.add_reaction('✖️')

    def check(reaction,user):
        return user == ctx.author and str(reaction) in reactions
    def check_msg(msg):
        return msg.author == ctx.author

    try:
        done, pending = await asyncio.wait([
            asyncio.create_task(bot.wait_for(
                'reaction_add', check=check, timeout=30)),
            # , timeout=15))
            asyncio.create_task(bot.wait_for('message', check=check_msg))
        ], return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()
        # event = done.pop().result()

        event = next(x.result() for x in done)

        if isinstance(event, discord.Message):
            await message.delete()
            return event.content.lower()

        reaction, user = event

        # reaction, user = await bot.wait_for('reaction_add', check=check, timeout=30)

        if str(reaction.emoji) =='⏫':
            # sl.append(d)
            await ctx.send(f'{d} added', delete_after=15)
            await message.delete()
            return 'append'
        if str(reaction.emoji) =='⏭️':
            await ctx.send(f'{d} added to a new list', delete_after=15)
            await message.delete()
            return 'next'
        # if str(reaction.emoji) =='✖️':
        #     await ctx.send(f'stop. result:{ml}', delete_after=35)
        #     await message.delete()
        #     stop = True
    except asyncio.TimeoutError:
        await ctx.send('time is up!. Canceling...', delete_after=35)
        await message.delete()
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
