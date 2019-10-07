# -*- coding: utf-8 -*-
import numpy
from numpy.random import randint as rand
import json
import random
import os
import discord

locale_strings = json.load(open('data/resource-strings.json','r',encoding="utf-8_sig"))

def create_maze(width=10, height=10, complexity=.75, density=.75):
    # Only odd shapes
    shape = ((height // 2) * 2 + 1, (width // 2) * 2 + 1)
    # Adjust complexity and density relative to maze size
    complexity = int(complexity * (5 * (shape[0] + shape[1]))) # number of components
    density    = int(density * ((shape[0] // 2) * (shape[1] // 2))) # size of components
    # Build actual maze
    Z = numpy.zeros(shape, dtype=int)
    # Fill borders
    Z[0, :] = Z[-1, :] = 1
    Z[:, 0] = Z[:, -1] = 1
    # Make aisles
    start_pos = None
    for i in range(density):
        x, y = rand(0, shape[1] // 2) * 2, rand(0, shape[0] // 2) * 2 # pick a random position
        Z[y, x] = 1
        for j in range(complexity):
            neighbours = []
            if x > 1:             neighbours.append((y, x - 2))
            if x < shape[1] - 2:  neighbours.append((y, x + 2))
            if y > 1:             neighbours.append((y - 2, x))
            if y < shape[0] - 2:  neighbours.append((y + 2, x))
            if len(neighbours):
                y_,x_ = neighbours[rand(0, len(neighbours) - 1)]
                if Z[y_, x_] == 0:
                    Z[y_, x_] = 1
                    Z[y_ + (y - y_) // 2, x_ + (x - x_) // 2] = 1
                    x, y = x_, y_

    good_chars = {False: '０', True: '１'}
    Z = Z.tolist()
    goal_pos = None

    while True:
        x = random.randrange(len(Z[0]))
        y = random.randrange(len(Z))
        if Z[y][x] == False:
            start_pos = x, y
            break
    while True:
        x = random.randrange(len(Z[0]))
        y = random.randrange(len(Z))
        if Z[y][x] == False and (x, y) != start_pos:
            goal_pos = x, y
            break

    Y = [a[:] for a in Z]
    for x in range(len(Z)):
        for j in range(len(Z[x])):
            Y[x][j] = good_chars[Z[x][j]]
    return Y, Z, start_pos, goal_pos

def is_group_maze(server_id, map_key):
    with open('./data/servers/{}/data.json'.format(server_id), 'r+') as f:
        data = json.load(f)
        is_group = data["maps"][map_key]["isGroup"]
        print('is_group =',is_group)
        return is_group


def gen_start_pos(server_id, map_key):
    taken_positions = []
    with open('./data/servers/{}/data.json'.format(server_id), 'r+') as f:
        data = json.load(f)
        for player_id in data["maps"][map_key]["participants"]:
            taken_positions.append(data["players"][player_id]["maps"][map_key]["position"])
        map = data["maps"][map_key]["mapString"].split('\n')

        i = j = 0
        while map[i][j] == '1':
            i = random.randrange(len(map))
            j = random.randrange(len(map[i]))
        return [i, j]

def get_participants(server_id, map_key):
    with open('./data/servers/{}/data.json'.format(server_id), 'r+') as f:
        data = json.load(f)
        participants = data["maps"][map_key]["participants"]
        return participants


def get_participants_string(server_id, map_key):
    participants = get_participants(server_id, map_key)


    with open('./data/servers/{}/data.json'.format(server_id), 'r+') as f:
        data = json.load(f)

        result = get_localized_message(server_id, "participants")
        prev = result

        for player_id in participants:
            nick = data["players"][player_id]["nick"]
            result += nick + "\n"
            if len(result) > 2000:
                break
            prev = result

    result = prev
    return result


def add_player_to_group_maze(server_id, player_id, map_key):
    with open('./data/servers/{}/data.json'.format(server_id), 'r+') as f:
        data = json.load(f)
        data["maps"][map_key]["participants"].append(player_id)
        data["players"][player_id]["maps"][map_key] = dict()
        # data["players"][player_id]["maps"][map_key]["mapString"] = data["maps"][map_key]["mapString"]
        data["players"][player_id]["maps"][map_key]["position"] = gen_start_pos(server_id, map_key)
        print('generated position:',data["players"][player_id]["maps"][map_key]["position"])

        return 1

def save_group_maze_old(maze, goal_pos, server_id, player_id):
    print('./data/servers/{}/ongoingmazes.json'.format(server_id))
    with open('./data/servers/{}/ongoingmazes.json'.format(server_id), 'r+') as f:
        data = json.load(f)

        data["GroupMaze"] = dict()
        data["GroupGoal"] = goal_pos
        data["GroupMaze"] = maze
        data["GroupPlayerPositions"] = dict()
        data["GroupMazeOwner"] = player_id

        f.seek(0)
        json.dump(data, f)
        f.truncate()

def gen_random_map_key():
    alph = "abcdefABCDEFG1234567890"
    s = ''.join([alph[random.randrange(len(alph))] for _ in range(8)])
    return s

def save_maze(maze, start_pos, goal_pos, server_id, player_id, is_group=False):
    print('./data/servers/{}/data.json'.format(server_id))
    map_key = None
    with open('./data/servers/{}/data.json'.format(server_id), 'r+') as f:
        data = json.load(f)

        map_key = gen_random_map_key()
        while map_key in data["players"][player_id]["maps"]: # probably not needed (lol) but will put in place in case it becomes relevant
            map_key = gen_random_map_key()



        data["players"][player_id]["maps"][map_key] = dict()

        # data["players"][player_id]["maps"][map_key]["mapString"] = maze

        data["players"][player_id]["maps"][map_key]["position"] = start_pos

        data["maps"][map_key] = dict()

        data["maps"][map_key]["goalPosition"] = goal_pos

        data["maps"][map_key]["participants"] = [player_id]

        data["maps"][map_key]["mapString"] = maze

        data["maps"][map_key]["isGroup"] = is_group


        f.seek(0)
        json.dump(data, f)
        f.truncate()

    return map_key

def save_maze_old(maze, start_pos, goal_pos, server_id, player_id):
    print('./data/servers/{}/ongoingmazes.json'.format(server_id))
    with open('./data/servers/{}/ongoingmazes.json'.format(server_id), 'r+') as f:
        data = json.load(f)

        data["PlayersToMazes"][player_id] = maze

        data["PlayerPositions"][player_id] = start_pos

        data["PlayerGoals"][player_id] = goal_pos

        f.seek(0)
        json.dump(data, f)
        f.truncate()


def set_map_piece(server_id, msg_id, player_id, map_key):
    with open('./data/servers/{}/data.json'.format(server_id), 'r+') as f:
        data = json.load(f)

        data["players"][player_id]["maps"][map_key]["msgId"] = msg_id # map_key is the one-time key for a single map
        # msg_id is current reply-able message
        data["maps"][map_key]["msgId"] = msg_id

        f.seek(0)
        json.dump(data, f)
        f.truncate()

def set_map_piece_old(server_id, msg_id, player_id):
    with open('./data/servers/{}/ongoingmazes.json'.format(server_id), 'r+') as f:
        data = json.load(f)

        data["PlayersToPieces"][player_id] = msg_id

        f.seek(0)
        json.dump(data, f)
        f.truncate()

def is_map_piece(msg_id, server_id, player_id):
    with open('./data/servers/{}/data.json'.format(server_id), 'r+') as f:
        data = json.load(f)
        for key, value in data["players"][player_id]["maps"].items():
            print('key =',key,'| val =',value['msgId'])
            if value['msgId'] == msg_id:
                return key
        return False

def is_map_piece_old(msg_id, server_id, player_id):
    with open('./data/servers/{}/ongoingmazes.json'.format(server_id), 'r+') as f:
        data = json.load(f)
        print('player piece:',data["PlayerPositions"][player_id])
        print('msg_id =',msg_id)
        return data["PlayersToPieces"][player_id] == msg_id

def make_move(server_id, player_id, map_key, dir):
    with open('./data/servers/{}/data.json'.format(server_id), 'r+') as f:
        data = json.load(f)
        # map = data["players"][player_id]["maps"][map_key]["mapString"]
        map = data["maps"][map_key]["mapString"]
        map = map.split('\n')
        cur_x, cur_y = data["players"][player_id]["maps"][map_key]["position"]
        dx, dy = dir
        print(map)
        if map[cur_y-dy][cur_x+dx] == '1':
            return False

        new_pos = [cur_x+dx, cur_y-dy]
        data["players"][player_id]["maps"][map_key]["position"] = new_pos

        f.seek(0)
        json.dump(data, f)
        f.truncate()

        return True

def make_move_old(server_id, player_id, dir):
    with open('./data/servers/{}/ongoingmazes.json'.format(server_id), 'r+') as f:
        data = json.load(f)
        map = data["PlayersToMazes"][player_id]
        map = map.split('\n')
        cur_x, cur_y = data["PlayerPositions"][player_id]
        dx, dy = dir
        print(map)
        if map[cur_y-dy][cur_x+dx] == '1':
            return False

        new_pos = [cur_x+dx, cur_y-dy]
        data["PlayerPositions"][player_id] = new_pos

        f.seek(0)
        json.dump(data, f)
        f.truncate()

        return True

def update_scores(server_id, player_id):
    with open('./data/servers/{}/data.json'.format(server_id), 'r+') as f:
        data = json.load(f)

        data["players"][player_id]["points"] += 10

        f.seek(0)
        json.dump(data, f)
        f.truncate()

def update_scores_old(server_id, player_id):
    with open('./data/servers/{}/ongoingmazes.json'.format(server_id), 'r+') as f:
        data = json.load(f)

        data["PlayerPoints"][player_id] += 10

        f.seek(0)
        json.dump(data, f)
        f.truncate()


def points_message(server_id, player_id, player_name):
    with open('./data/servers/{}/data.json'.format(server_id), 'r+') as f:
        data = json.load(f)

        s = ""

        player_points = data["players"][player_id]["points"]

        s += get_localized_message(server_id, "status_formatter").format(player_name, player_points)
        x = player_points/10
        if x == 0:
            s += get_localized_message(server_id, "status_weak")
        elif 1 <= x <= 4:
            s += get_localized_message(server_id, "status_medium")
        elif 5 <= x <= 9:
            s += get_localized_message(server_id, "status_strong")
        else:
            s += get_localized_message(server_id, "status_very_strong")

        return s

def points_message_old(server_id, player_id, player_name):
    with open('./data/servers/{}/ongoingmazes.json'.format(server_id), 'r+') as f:
        data = json.load(f)

        s = ""

        player_points = data["PlayerPoints"][player_id]

        s += "**{}**のポイント：**{}**\n".format(player_name, player_points)
        x = player_points/10
        if x == 0:
            s += "よわーい！"
        elif 1 <= x <= 4:
            s += "まあまあね"
        elif 5 <= x <= 9:
            s += "中々やるじゃない！"
        else:
            s += "キミすごい！！"

        return s


def get_player_name(server_id, player_id):
    with open('./data/servers/{}/data.json'.format(server_id), 'r+') as f:
        data = json.load(f)
        return data["players"][player_id]["nick"]

def get_player_name_old(server_id, player_id):
    with open('./data/servers/{}/ongoingmazes.json'.format(server_id), 'r+') as f:
        data = json.load(f)
        return data["PlayerNames"][player_id]


def register_name(server_id, player_id, nick):
    with open('./data/servers/{}/data.json'.format(server_id), 'r+') as f:
        data = json.load(f)
        data["players"][player_id]["nick"] = nick

        f.seek(0)
        json.dump(data, f)
        f.truncate()

def register_name_old(server_id, player_id, name):
    with open('./data/servers/{}/ongoingmazes.json'.format(server_id), 'r+') as f:
        data = json.load(f)
        data["PlayerNames"][player_id] = name

        f.seek(0)
        json.dump(data, f)
        f.truncate()

def change_locale(server_id, locale):
    locale_list = ["ja", "en"] # "ja" is default
    if locale in locale_list:
        with open('./data/servers/{}/data.json'.format(server_id), 'r+') as f:
            data = json.load(f)

            if locale == "ja":
                data["locale"] = ""
            else:
                data["locale"] = locale

            f.seek(0)
            json.dump(data, f)
            f.truncate()
            return True
    else:
        return False

def get_localized_message(server_id, locale_string):
    with open('./data/servers/{}/data.json'.format(server_id), 'r+') as f:
        data = json.load(f)
        return locale_strings["values" + data["locale"]][locale_string]

def initialize_guild_data(server):
    if not os.path.exists('./data/servers/{}'.format(server.id)):
        os.makedirs('./data/servers/{}'.format(server.id))
        os.makedirs('./data/servers/{}/saved'.format(server.id))
        os.makedirs('./data/servers/{}/output'.format(server.id))
        os.makedirs('./data/servers/{}/images'.format(server.id))
        with open('./data/servers/{}/data.json'.format(server.id), 'w+') as f:
            data = {}

            data["locale"] = ""
            data["players"] = dict()
            data["maps"] = dict()                #map key    : map creator id


            data["singlePuzzle"] = dict()
            data["singlePuzzle"]["fastestRecord"] = 9999999


            f.seek(0)
            json.dump(data, f)
            f.truncate()

        with open('./data/servers/{}/data.json'.format(server.id), 'r+') as f:
            data = json.load(f)

            default_player = dict()
            default_player["nick"] = None
            default_player["points"] = 0
            default_player["maps"] = dict()
            default_player["fastestRecord"] = 999999

            for member in server.members:
                if not member.id in data["players"]:
                    data["players"][member.id] = dict()
                    data["players"][member.id]["points"] = 0
                    data["players"][member.id]["maps"] = dict()
                    data["players"][member.id]["fastestRecord"] = 999999

                    x = member.nick
                    player_name = x if x != None else member.name
                    data["players"][member.id]["nick"] = player_name

            f.seek(0)
            json.dump(data, f)
            f.truncate()


def initialize_guild_data_old(server):
    if not os.path.exists('./data/servers/{}'.format(server.id)):
        os.makedirs('./data/servers/{}'.format(server.id))
        os.makedirs('./data/servers/{}/images'.format(server.id))
        with open('./data/servers/{}/ongoingmazes.json'.format(server.id), 'w+') as f:
            data = {}
            data["PlayersToMazes"] = dict()
            data["PlayerPositions"] = dict()
            data["PlayersToPieces"] = dict()
            data["PlayerPoints"] = dict()
            data["PlayerRecords"] = dict()
            data["PlayerGoals"] = dict()
            data["PlayerNames"] = dict()
            data["FastestRecord"] = 999999
            data["GroupMaze"] = dict()
            data["GroupGoal"] = dict()
            data["GroupPlayerPositions"] = dict()
            data["GroupMazeOwner"] = "X"

            f.seek(0)
            json.dump(data, f)
            f.truncate()

    with open('./data/servers/{}/ongoingmazes.json'.format(server.id), 'r+') as f:
        data = json.load(f)

        koumoku = [("PlayersToMazes", "X"), ("PlayerPositions", [0,0]), ("PlayersToPieces", "X"), ("PlayerPoints", 0), ("PlayerRecords",0), ("PlayerGoals", [0,0]), ("PlayerNames",None), ("GroupMaze", "X"), ("GroupGoal", [0,0]), ('GroupPlayerPositions', [0,0]), ("GroupMazeOwner", "X")]

        for attr, initval in koumoku:
            if not attr in data:
                data[attr] = dict()
            for member in server.members:
                if not member.id in data[attr]:
                    data[attr][member.id] = initval


        f.seek(0)
        json.dump(data, f)
        f.truncate()



# maze = create_maze(10, 10)
# for i in range(len(maze)):
#     print(maze[i])