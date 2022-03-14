import asyncio

# from discord.ext import commands
import discord


async def pager(bot, ctx, title, contents:list):
    contents = [contents[x:x+10] for x in range(0, len(contents), 10)]
    pages = len(contents)
    cur_p = 1
    message = await ctx.reply(embed=_page(cur_p, pages, contents, title))
    for x in ['⏮️', '⬅️', '➡️', '⏭️','❌']:
        await message.add_reaction(x)

    async def process(cur_p):

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['⬅️', '➡️', '⏮️', '⏭️','❌']

        def check_msg(msg):
            return msg.author == ctx.author

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
            return event.content

        # reaction
        reaction, user = event

        if str(reaction.emoji) == '➡️' and cur_p != pages:
            cur_p += 1
            await message.edit(embed=_page(cur_p, pages, contents, title))
        elif str(reaction.emoji) == '⬅️' and cur_p > 1:
            cur_p -= 1
            await message.edit(embed=_page(cur_p, pages, contents, title))
        elif str(reaction.emoji) == '⏭️' and cur_p + 10 <= pages:
            cur_p += 10
            await message.edit(embed=_page(cur_p, pages, contents, title))
        elif str(reaction.emoji) == '⏮️' and cur_p - 10 >= 1:
            cur_p -= 10
            await message.edit(embed=_page(cur_p, pages, contents, title))
        elif str(reaction.emoji) == '❌':
            return 'cancel'

        await message.remove_reaction(reaction, user)
        return await process(cur_p)

    try:
        user_response = await process(cur_p)
        print(user_response)
        return user_response
        # if user_response == 'cancel':
            # await ctx.send('Aborted!')
            # return user_response
            # return
        # return chan_gen(user_response)

    except asyncio.TimeoutError:
        await ctx.reply('Time is Up!!!')
        return 'cancel'
    except ValueError as e:
        print(e)
        await ctx.reply('Invalid response!!!\nAborted!.')
        return 'cancel'
    except asyncio.CancelledError:
        await ctx.reply('Aborted')
        return 'cancel'

def _page(cur_page, pages, content, title):
    nl = '\n'
    return discord.Embed(title=title,
                         description=f'Page {cur_page}/{pages}\n{nl.join(content[cur_page-1])}'
                         )

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
            (result.append(b) for b in range(int(xr[0]), int(xr[1])+1))# pylint: disable=W0106
            #     result.append(b)
            continue
        result.append(int(x))
    return result
