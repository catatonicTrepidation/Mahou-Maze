# -*- coding: utf-8 -*-
import numpy
from numpy.random import randint as rand
import json
from PIL import Image



async def save_position_image(server_id, player_id, map_key):
    maze = pos = None
    print('./data/servers/{}/data.json'.format(server_id))
    with open('./data/servers/{}/data.json'.format(server_id), 'r') as f:
        data = json.load(f)
        maze = data["maps"][map_key]["mapString"]
        pos = data["players"][player_id]["maps"][map_key]["position"]
        goal = data["maps"][map_key]["goalPosition"]
        print(pos)
        maze = maze.split('\n')
        print(maze)
        if pos == goal:
            img = await draw_祝()
            # img.save('./data/servers/{}/images/win.png'.format(server_id))
            return True
        img = await draw_position(maze, pos, visibility=1)
        img.save('./data/servers/{}/images/maze.png'.format(server_id))
        return False



async def save_position_image_old(server_id, player_id):
    maze = pos = None
    print('./data/servers/{}/ongoingmazes.json'.format(server_id))
    with open('./data/servers/{}/ongoingmazes.json'.format(server_id), 'r') as f:
        data = json.load(f)
        maze = data["PlayersToMazes"][player_id]
        pos = data["PlayerPositions"][player_id]
        goal = data["PlayerGoals"][player_id]
        print(pos)
        maze = maze.split('\n')
        print(maze)
        if pos == goal:
            img = await draw_祝()
            # img.save('./data/servers/{}/images/win.png'.format(server_id))
            return True
        img = await draw_position(maze, pos, visibility=1)
        img.save('./data/servers/{}/images/maze.png'.format(server_id))
        return False


async def draw_position(maze, pos, visibility=1):
    block_size = 200
    background = Image.new('RGBA', (block_size*(1+2*visibility), block_size*(1+2*visibility)), 'white')
    char = Image.open('./res/char.png')

    char_w, char_h = char.size
    bg_w, bg_h = background.size

    offset = ((bg_w - char_w) // 2, (bg_h - char_h) // 2)

    background.paste(char, offset, char)

    岩 = Image.open('./res/stone.png')

    print('maze =',maze)
    x, y = pos
    # x, y = 5, 5
    for dx in range(-1,2):
        for dy in range(-1,2):
            if maze[y+dy][x+dx] == '1':
                offset = block_size*(dx+1), block_size*(dy+1)
                background.paste(岩, offset, 岩)


    return background


async def draw_祝():
    return 0