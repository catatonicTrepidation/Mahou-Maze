# -- encoding: utf-8 --
import os
import random
import asyncio
import requests

from datetime import datetime
import json

import discord
from discord.ext import commands

import os, random

import cv2

import maze_maker
import maze_displayer
import imgtools.filters

from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


print("moe_pipic起動")

config_data = json.load(open('data/config.json','r',encoding="utf-8_sig"))
TOKEN = config_data['token']

locale_strings = json.load(open('data/config.json','r',encoding="utf-8_sig"))

description = "moe"


bot = commands.Bot(command_prefix=('nya~','...','…','---','!'), description=description)

@bot.command(aliases=['cmd1'], pass_context=True)
async def command1(ctx: commands.Context, param1 : str = None, param2 : int = None, *, args = 'nyan'):
    print('command1てすと:')
    print('param1 =',param1)
    print('param2 =',param2)
    print('args =',args)
    print()
    await bot.say("にゃ！！！（おこ）")


@bot.command(aliases=['maze','m'], pass_context=True)
async def startmaze(ctx: commands.Context, group_flag : str = None):
    print(ctx.message.type == "private")
    print(ctx.message.channel.type == discord.ChannelType.private)

    is_private = (ctx.message.channel.type == discord.ChannelType.private)

    is_group = True if group_flag in [".g", ".group"] else False
    print('group_flag =',group_flag)

    text_msg = None
    if not is_group:
        # create maze, connect to player ID
        maze_viewable, maze_savable, start_pos, goal_pos = maze_maker.create_maze(width=13, height=13)

        if is_private:
            await bot.say('mazeすたーと！')
        else:
            await bot.say(maze_maker.get_localized_message(ctx.message.server.id, 'maze_start'))

        maze_viewable[goal_pos[1]][goal_pos[0]] = '☆'
        maze_viewable[start_pos[1]][start_pos[0]] = '私'
        maze_msg = '\n'.join([''.join(x) for x in maze_viewable])
        await bot.say(maze_msg)
    else:
        if is_private:
            await bot.say('DMではグループ迷宮作れない...')
            return 0
        await bot.say(maze_maker.get_localized_message(ctx.message.server.id, 'group_maze_start'))

        # create maze, connect to player ID
        maze_viewable, maze_savable, start_pos, goal_pos = maze_maker.create_maze(width=22, height=20, complexity=0.60)

        maze_viewable[goal_pos[1]][goal_pos[0]] = '☆'
        maze_viewable[start_pos[1]][start_pos[0]] = '私'
        maze_msg = '\n'.join([''.join(x) for x in maze_viewable])
        text_msg = await bot.say(maze_msg)

    chosen_server_id = None
    if is_private:
        await bot.say('どのサーバーと結び付ける？')
        s = ""
        ctr = 1
        l = []
        for server in bot.servers:
            if ctx.message.author in server.members:
                s += str(ctr) + ": " + server.name + "\n"
                ctr += 1
                l.append(server.id)
        s += "**0: やっぱりやめよう**"
        print(s)
        await bot.say(s)

        choice = await bot.wait_for_message(timeout=10)
        if choice:
            if choice.content and choice.content.isdigit and 0 <= int(choice.content) <= ctr:
                if int(choice.content) == 0:
                    await bot.say('しないの？ふーん')
                else:
                    await bot.say(l[int(choice.content)-1])
                    chosen_server_id = l[int(choice.content)-1]
        else:
            await bot.say('もー遅いから！！')
            return 0
    else:
        chosen_server_id = ctx.message.server.id


    maze_save = '\n'.join([''.join([str(c) for c in x]) for x in maze_savable])
    map_key = maze_maker.save_maze(maze_save, start_pos, goal_pos, server_id=chosen_server_id, player_id=ctx.message.author.id, is_group=is_group)

    if not map_key:
        # do some sorta error handling? delete maze and stuff?
        return 0
    # start time limit

    if not is_group:
        # post first image
        await maze_displayer.save_position_image(chosen_server_id, ctx.message.author.id, map_key)
        msg = await bot.send_file(ctx.message.channel, './data/servers/{}/images/maze.png'.format(chosen_server_id), content=chosen_server_id if is_private else "")

        maze_maker.set_map_piece(chosen_server_id, msg.id, ctx.message.author.id, map_key)

        # add reactions
        await bot.add_reaction(msg, '⬅')
        await bot.add_reaction(msg, '➡')
        await bot.add_reaction(msg, '⬇')
        await bot.add_reaction(msg, '⬆')
    else:
        maze_maker.set_map_piece(chosen_server_id, text_msg.id, ctx.message.author.id, map_key)
        await bot.add_reaction(text_msg, '🌟')
        await bot.add_reaction(text_msg, '🈁')
        await bot.say(maze_maker.get_localized_message(chosen_server_id, "press_to_join"))



def download_image(url, filename):
    """
    Download image from url
    :param url: URL of image to download
    :param filename: Filename to call saved image
    """
    r = requests.get(url)
    open(filename, 'wb').write(r.content)


# downloads avatar and returns image object!
async def get_user_avatar(server_id, discord_user):
    print('AVI URL =',discord_user.avatar_url)
    download_image(discord_user.avatar_url, "./data/servers/{}/saved/avatar.png".format(server_id))
    image = cv2.imread("./data/servers/{}/saved/avatar.png".format(server_id))
    return image


async def get_image_from_url(server_id, url):
    try:
        download_image(url, "./data/servers/{}/saved/url.png".format(server_id))
    except Exception as e:
        return None
    image = cv2.imread("./data/servers/{}/saved/url.png".format(server_id))
    return image

async def save_output_image(server_id, image):
    cv2.imwrite("./data/servers/{}/saved/output.png".format(server_id), image)

@bot.command(aliases=['jimetu','自滅', 'killme'], pass_context=True)
async def die(ctx: commands.Context):
    avatar_image = await get_user_avatar(ctx.message.server.id, ctx.message.author)
    gray_image = imgtools.filters.grayscale(avatar_image)
    await save_output_image(ctx.message.server.id, gray_image)
    await bot.send_file(ctx.message.channel, "./data/servers/{}/saved/output.png".format(ctx.message.server.id))

@bot.command(aliases=['tohsv'], pass_context=True)
async def hsv(ctx: commands.Context):
    avatar_image = await get_user_avatar(ctx.message.server.id, ctx.message.author)
    hsv_image = imgtools.filters.rgb_to_hsv(avatar_image)
    await save_output_image(ctx.message.server.id, hsv_image)
    await bot.send_file(ctx.message.channel, "./data/servers/{}/saved/output.png".format(ctx.message.server.id))

@bot.command(aliases=['changehsv'], pass_context=True)
async def change_hsv(ctx: commands.Context):
    avatar_image = await get_user_avatar(ctx.message.server.id, ctx.message.author)
    hsv_image = imgtools.filters.change_hsv(avatar_image)
    await save_output_image(ctx.message.server.id, hsv_image)
    await bot.send_file(ctx.message.channel, "./data/servers/{}/saved/output.png".format(ctx.message.server.id))

@bot.command(aliases=['kms', 'gta'], pass_context=True)
async def wasted(ctx: commands.Context, url : str = None):
    input_image = None
    if ctx.message.attachments:
        attach = ctx.message.attachments[0]
        print(attach['filename'][-4:])
        if (len(attach['filename']) > 3 and attach['filename'][-4:] in ('.png', '.jpg', '.gif', '.webp')) or (len(attach['filename']) > 4 and attach['filename'][-5:] == '.jpeg'):
            input_image = await get_image_from_url(ctx.message.server.id, attach['url'])
        else:
            await bot.say("えぇ？それ画像？画像っぽい拡張子じゃないとわかんないよアタシ！")
            return 0
    elif url:
        input_image = await get_image_from_url(ctx.message.server.id, url)
        if input_image is None:
            await bot.say("画像をダウンロードできなかった！")
            return 0
    else:
        input_image = await get_user_avatar(ctx.message.server.id, ctx.message.author)
    wasted_image = imgtools.filters.wasted(input_image)
    await save_output_image(ctx.message.server.id, wasted_image)
    await bot.send_file(ctx.message.channel, "./data/servers/{}/saved/output.png".format(ctx.message.server.id))

@bot.command(aliases=['groupmaze','groupm', 'gm'], pass_context=True)
async def startgroupmaze(ctx: commands.Context):
    bot.say(maze_maker.get_localized_message(ctx.message.server.id, 'group_maze_start'))

    # create maze, connect to player ID
    maze_viewable, maze_savable, start_pos, goal_pos = maze_maker.create_maze(width=22, height=20, complexity=0.60)

    maze_viewable[goal_pos[1]][goal_pos[0]] = '☆'
    maze_viewable[start_pos[1]][start_pos[0]] = '私'
    maze_msg = '\n'.join([''.join(x) for x in maze_viewable])
    text_msg = await bot.say(maze_msg)

    maze_save = '\n'.join([''.join([str(c) for c in x]) for x in maze_savable])
    maze_maker.save_maze(maze_save, goal_pos, server_id=ctx.message.server.id, player_id=ctx.message.author.id)

    await bot.add_reaction(text_msg, '🌟')
    await bot.say(maze_maker.get_localized_message(ctx.message.server.id, "press_to_join"))



@bot.event
async def on_reaction_add(reaction, user):
    if user == bot.user:
        return
    server_id = None
    is_private = (reaction.message.channel.type == discord.ChannelType.private)
    if is_private:
        server_id = reaction.message.content
    else:
        server_id = reaction.message.server.id

    if reaction.message.author.bot: # if it's on a msg posted by pot, check if it's a current map piece
        map_key = maze_maker.is_map_piece(reaction.message.id, server_id, user.id)
        if map_key:
            if maze_maker.is_group_maze(server_id, map_key):
                if reaction.emoji == '🌟': # 参加したいね！
                    maze_maker.add_player_to_group_maze(server_id, user.id, map_key)
                    await bot.send_message('はい〜！参加登録した！', user)
                if reaction.emoji == '🈁': # 参加したいね！
                    participants_msg = maze_maker.get_participants_string(server_id, map_key)
                    await bot.send_message(reaction.message.channel,participants_msg)
                    await bot.remove_reaction(reaction.message, reaction.emoji,
                                        reaction.message.server.get_member(user.id))  # remove reaction
            else:
                dir = decode_reaction(reaction)
                success = maze_maker.make_move(server_id, user.id, map_key, dir)
                if not success:
                    await bot.remove_reaction(reaction.message, reaction.emoji,
                                        reaction.message.server.get_member(user.id))  # remove reaction
                    warning_msg = await bot.send_message(reaction.message.channel,maze_maker.get_localized_message(server_id, "cant"))
                    await asyncio.sleep(1)
                    await bot.delete_message(warning_msg)
                    return 0

                # delete old message
                await bot.delete_message(reaction.message)

                is_goal = await maze_displayer.save_position_image(server_id, user.id, map_key)
                msg = None
                if is_goal:
                    msg = await bot.send_file(reaction.message.channel, './res/win.jpg')
                    maze_maker.update_scores(server_id, user.id)
                    await bot.add_reaction(msg, '🌟')
                    return
                else:
                    msg = await bot.send_file(reaction.message.channel, './data/servers/{}/images/maze.png'.format(server_id), content=server_id if is_private else "")

                maze_maker.set_map_piece(server_id, msg.id, user.id, map_key)

                # add reactions
                await bot.add_reaction(msg, '⬅')
                await bot.add_reaction(msg, '➡')
                await bot.add_reaction(msg, '⬇')
                await bot.add_reaction(msg, '⬆')


def decode_reaction(reaction):
    reacts_to_dirs = {'⬅':[-1,0],'➡':[1,0],'⬇':[0,-1],'⬆':[0,1]}
    return reacts_to_dirs[reaction.emoji]


@bot.command(aliases=['view_points'], pass_context=True)
async def points(ctx: commands.Context):
    player_name = maze_maker.get_player_name(ctx.message.server.id, ctx.message.author.id)
    if player_name == None:
        x = ctx.message.author.nick
        player_name = x if x != None else ctx.message.author.name
    reply_text = maze_maker.points_message(ctx.message.server.id, ctx.message.author.id, player_name)
    await bot.say(reply_text)

@bot.command(aliases=['registername', 'regname', 'changename', 'register', 'reg'], pass_context=True)
async def register_name(ctx: commands.Context, name : str = None):
    if name:
        maze_maker.register_name(ctx.message.server.id, ctx.message.author.id, name)
        await bot.say(maze_maker.get_localized_message(ctx.message.server.id, 'registered_success').format(name))
    else:
        await bot.say(maze_maker.get_localized_message(ctx.message.server.id, 'registered_failure'))

@bot.command(aliases=['changelocale', 'cl'], pass_context=True)
async def change_locale(ctx: commands.Context, locale : str = None):
    if locale:
        success = maze_maker.change_locale(ctx.message.server.id, locale)
        if success:
            await bot.say(maze_maker.get_localized_message(ctx.message.server.id, 'locale_success'))
        else:
            await bot.say(maze_maker.get_localized_message(ctx.message.server.id, 'locale_failure2'))
    else:
        await bot.say(maze_maker.get_localized_message(ctx.message.server.id, 'locale_failure1'))


@bot.event
async def on_ready():
    print("i'm ready~nya~")

@bot.event
async def on_server_join(server):
    print('JOINED SERVER!!!')
    maze_maker.initialize_guild_data(server)

@bot.command(aliases=['initplayers'], pass_context=True)
async def plsinit(ctx: commands.Context, param1 : str = None, param2 : int = None, *, args = 'nyan'):
    print('init!!!')
    maze_maker.initialize_guild_data(ctx.message.server)

# async def on_server_join()

import time
@bot.command(aliases=['cutie','cutiescore','cutescore','cscore'], pass_context=True)
async def cuteness(ctx: commands.Context, target: discord.Member):
    # await bot.say(target.id)
    if target.id == "232904019415269377":
        await bot.say(f"{target.mention} is a gosh darn cutie~!")
    else:
        t = time.time()
        await bot.say("{} gets {} cutie points!".format(target.mention, 1 + t%100))

bot.run(TOKEN)
