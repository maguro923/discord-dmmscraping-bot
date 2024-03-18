import asyncio
import discord
import discord.app_commands
import DiscordData.token as TokenData
import DiscordData.channel as ChannelData
import DiscordData.command as Command
import DiscordData.command_list as CommandList
import random
import time
import subprocess
import os
import sys
import dill

TOKEN = TokenData.TOKEN
client = discord.Client(intents=discord.Intents.all())
CHANNEL_ID = ChannelData.CHANNEL_ID
PATH = "send/{}_send.txt"
URL = "https://bitcoin.dmm.com/trade_chart_rate_list/{}-jpy"
COMMAND = Command.COMMAND
command_list = CommandList.command_list
status_send = False
ask_goal = {}
bid_goal = {}
for i in range(len(COMMAND)):
    ask_goal[COMMAND[i]] = []
    bid_goal[COMMAND[i]] = []
if os.path.isfile("DiscordData/ask_goal"):
    with open("DiscordData/ask_goal","rb") as f:
        ask_goal = dill.load(f)
        print("load: ask_goal\n",ask_goal)

if os.path.isfile("DiscordData/bid_goal"):
    with open("DiscordData/bid_goal","rb") as f:
        bid_goal = dill.load(f)
        print("load: bid_goal\n",bid_goal)

async def bot_status():
    channel = client.get_channel(CHANNEL_ID)
    while True:
        for i in range(6):
            for j in range(len(COMMAND)):
                url = URL.format(COMMAND[j])
                command = ["python3","checkbtc.py",url,"{}_send.txt".format(COMMAND[j])]
                proc = subprocess.Popen(command)
                await asyncio.sleep(30)
                await amount_check(COMMAND[j])
            await asyncio.sleep(600-len(COMMAND)*30)
        print("status: OK")
        if status_send:
            await send_status(channel,"status","OK",0x00ff00)

async def amount_check(command):
    amount = res_get(PATH.format(command))
    amount[0] = float(amount[0].replace(",",""))
    amount[1] = float(amount[1].replace(",",""))
    bid_del = []
    ask_del = []

    for i in range(len(bid_goal[command])):
        if amount[0] >= bid_goal[command][i][0] and bid_goal[command][i][3] == "+":
            bid_goal_channel = client.get_channel(bid_goal[command][i][2])
            print("{} の売値が {} 円を上回りました\n現在の売値 {} 円".format(command,bid_goal[command][i][0],amount[0]))
            await bid_goal_channel.send("<@{}>\n{} の売値が {} 円を上回りました\n現在の売値 {} 円".format(bid_goal[command][i][1],command,bid_goal[command][i][0],amount[0]))
            bid_del.append(i)
        
        if amount[0] <= bid_goal[command][i][0] and bid_goal[command][i][3] == "-":
            bid_goal_channel = client.get_channel(bid_goal[command][i][2])
            print("{} の売値が {} 円を下回りました\n現在の売値 {} 円".format(command,bid_goal[command][i][0],amount[0]))
            await bid_goal_channel.send("<@{}>\n{} の売値が {} 円を下回りました\n現在の売値 {} 円".format(bid_goal[command][i][1],command,bid_goal[command][i][0],amount[0]))
            bid_del.append(i)

    for i in range(len(ask_goal[command])):
        if amount[1] >= ask_goal[command][i][0] and ask_goal[command][i][3] == "+":
            ask_goal_channel = client.get_channel(ask_goal[command][i][2])
            print("{} の買値が {} 円を上回りました\n現在の買値 {} 円".format(command,ask_goal[command][i][0],amount[1]))
            await ask_goal_channel.send("<@{}>\n{} の買値が {} 円を上回りました\n現在の買値 {} 円".format(ask_goal[command][i][1],command,ask_goal[command][i][0],amount[1]))
            ask_del.append(i)

        if amount[1] <= ask_goal[command][i][0] and ask_goal[command][i][3] == "-":
            ask_goal_channel = client.get_channel(ask_goal[command][i][2])
            print("{} の買値が {} 円を下回りました\n現在の買値 {} 円".format(command,ask_goal[command][i][0],amount[1]))
            await ask_goal_channel.send("<@{}>\n{} の買値が {} 円を下回りました\n現在の買値 {} 円".format(ask_goal[command][i][1],command,ask_goal[command][i][0],amount[1]))
            ask_del.append(i)

    bid_del.sort(reverse=True)
    ask_del.sort(reverse=True)

    if len(bid_del):
        for i in range(len(bid_del)):
            del bid_goal[command][bid_del[i]]
        with open("DiscordData/bid_goal","wb") as f:
                dill.dump(bid_goal,f)
        print("dump: OK")

    if len(ask_del):
        for i in range(len(ask_del)):
            del ask_goal[command][ask_del[i]]
        with open("DiscordData/ask_goal","wb") as f:
                dill.dump(ask_goal,f)
        print("dump: OK")

async def goal_setting(message,orders):
    orders[2] = float(orders[2])
    if orders[0] == "ask" and orders[3] == "+" and command_check("del",orders[1]):
        print("command: /ask")
        x = [orders[2],str(message.author.id),int(message.channel.id),orders[3]]
        ask_goal[orders[1]].append(x)
        print("{} の買値が {} 円を上回った場合に通知します".format(orders[1].upper(),orders[2]))
        await message.channel.send("{} の買値が {} 円を上回った場合に通知します".format(orders[1].upper(),orders[2]))
        with open("DiscordData/ask_goal","wb") as f:
            dill.dump(ask_goal,f)

    elif orders[0] == "ask" and orders[3] == "-" and command_check("del",orders[1]):
        print("command: /ask")
        x = [orders[2],str(message.author.id),int(message.channel.id),orders[3]]
        ask_goal[orders[1]].append(x)
        print("{} の買値が {} 円を下回った場合に通知します".format(orders[1].upper(),orders[2]))
        await message.channel.send("{} の買値が {} 円を下回った場合に通知します".format(orders[1].upper(),orders[2]))
        with open("DiscordData/ask_goal","wb") as f:
            dill.dump(ask_goal,f)
            
    elif orders[0] == "bid" and orders[3] == "+" and command_check("del",orders[1]):
        print("command: /bid")
        x = [orders[2],str(message.author.id),int(message.channel.id),orders[3]]
        bid_goal[orders[1]].append(x)
        print("{} の売値が {} 円を上回った場合に通知します".format(orders[1].upper(),orders[2]))
        await message.channel.send("{} の売値が {} 円を上回った場合に通知します".format(orders[1].upper(),orders[2]))
        with open("DiscordData/bid_goal","wb") as f:
            dill.dump(bid_goal,f)

    elif orders[0] == "bid" and orders[3] == "-" and command_check("del",orders[1]):
        print("command: /bid")
        x = [orders[2],str(message.author.id),int(message.channel.id),orders[3]]
        bid_goal[orders[1]].append(x)
        print("{} の売値が {} 円を下回った場合に通知します".format(orders[1].upper(),orders[2]))
        await message.channel.send("{} の売値が {} 円を下回った場合に通知します".format(orders[1].upper(),orders[2]))
        with open("DiscordData/bid_goal","wb") as f:
            dill.dump(bid_goal,f)

    else:
        print("{} は無効な引数です。正しい引数を入力して下さい".format(orders[1]))
        await message.channel.send("{} は無効な引数です。正しい引数を入力して下さい".format(orders[1]))

async def command_write(command):
    await asyncio.sleep(1)
    data = open("DiscordData/command.py")
    data_list = data.readlines()
    data.close()
    command_index = data_list[0].find("[")
    data_list[0] = data_list[0][:command_index]
    data_list[0] += "["
    for i in range(len(command)):
        data_list[0] += "'"+command[i]+"'"
        if not i+1 == len(command):
            data_list[0] += ","
    data_list[0] += "]\n"
    data = open("DiscordData/command.py",mode="w")
    data.writelines(data_list)
    os.fsync(data.fileno())
    data.close()
    print("command_write: OK")

def command_check(action,name):
    if action == "add":
        for i in range(len(COMMAND)):
            if COMMAND[i] == name:
                return False
        return True
    elif action == "del":
        for i in range(len(COMMAND)):
            if COMMAND[i] == name:
                return True
        return False
    elif action == "check":
        for i in range(len(command_list)):
            if name == command_list[i]:
                return True
        return False

async def command_reload(message,action,name):
    if not command_check("check",name):
        print("{} は無効な引数です。正しい引数を入力して下さい".format(name))
        await message.channel.send("{} は無効な引数です。正しい引数を入力して下さい".format(name))
        return
    if not command_check(action,name) and action == "add":
        print("{} は既に追加されています".format(name))
        await message.channel.send("{} は既に追加されています".format(name))
        return
    if not command_check(action,name) and action == "del":
        print("{} は既に削除されています".format(name))
        await message.channel.send("{} は既に削除されています".format(name))
        return
    if action == "add" and len(COMMAND)>=20:
        print("登録できるコマンドの上限は20個です")
        await message.channel.send("登録できるコマンドの上限は20個です")
        return
    if action == "add":
        new_command = COMMAND
        new_command.append(name)
        await command_write(new_command)
        await message.channel.send("{} を追加しました".format(name))
        ask_goal[name] = []
        with open("DiscordData/ask_goal","wb") as f:
            dill.dump(ask_goal,f)
        bid_goal[name] = []
        with open("DiscordData/bid_goal","wb") as f:
            dill.dump(bid_goal,f)
        print("再起動します...")
        await send_status(message.channel,"ログ","Botを切断しました\n再起動しています...",0xff0000)
        os.execv(sys.executable, ['python'] + sys.argv)
    else:
        new_command = COMMAND
        new_command.remove(name)
        await command_write(new_command)
        await message.channel.send("{} を削除しました".format(name))
        del ask_goal[name]
        with open("DiscordData/ask_goal","wb") as f:
            dill.dump(ask_goal,f)
        del bid_goal[name]
        with open("DiscordData/bid_goal","wb") as f:
            dill.dump(bid_goal,f)
        print("再起動します...")
        await send_status(message.channel,"ログ","Botを切断しました\n再起動しています...",0xff0000)
        os.execv(sys.executable, ['python'] + sys.argv)

async def show(message,command):
    if command == "command":
        print("command: show command")
        x = "\n".join(COMMAND)
        y = ",".join(command_list)
        await message.channel.send("現在有効化されたコマンドは\n"+x+"\nコマンド一覧は\n"+y)
    elif command == "ask":
        print("command: show ask")
        z = []
        for i in range(len(COMMAND)):
            if len(ask_goal[COMMAND[i]]):
                x = [COMMAND[i]]
                for j in range(len(ask_goal[COMMAND[i]])):
                    x.append([ask_goal[COMMAND[i]][j][0],ask_goal[COMMAND[i]][j][3]])
                z.append(x)
        if len(z) == 0:
            await message.channel.send("通知する買値が設定されていません")
        for i in range(len(z)):
            for j in range(len(z[i])-1):
                if z[i][j+1][1] == "+":
                    await message.channel.send("{} の買値が {} 円を上回った場合に通知します".format(z[i][0].upper(),z[i][j+1][0]))
                elif z[i][j+1][1] == "-":
                    await message.channel.send("{} の買値が {} 円を下回った場合に通知します".format(z[i][0].upper(),z[i][j+1][0]))

    elif command == "bid":
        print("command: show bid")
        z = []
        for i in range(len(COMMAND)):
            if len(bid_goal[COMMAND[i]]):
                x = [COMMAND[i]]
                for j in range(len(bid_goal[COMMAND[i]])):
                    x.append([bid_goal[COMMAND[i]][j][0],bid_goal[COMMAND[i]][j][3]])
                z.append(x)
        if len(z) == 0:
            await message.channel.send("通知する売値が設定されていません")
        for i in range(len(z)):
            for j in range(len(z[i])-1):
                if z[i][j+1][1] == "+":
                    await message.channel.send("{} の売値が {} 円を上回った場合に通知します".format(z[i][0].upper(),z[i][j+1][0]))
                elif z[i][j+1][1] == "-":
                    await message.channel.send("{} の売値が {} 円を下回った場合に通知します".format(z[i][0].upper(),z[i][j+1][0]))


def res_get(path):
    res = open(path)
    amount = res.readlines()
    res.close()
    return amount

async def dmm_selenium(message):
    for i in range(len(COMMAND)):
        if message.content == COMMAND[i]:
            print("command: {}".format(COMMAND[i]))
            amount = res_get(PATH.format(COMMAND[i]))
            await now_embed_send(amount,message,"{}/JPY レート".format(COMMAND[i].upper()))
        elif message.content == "{}now".format(COMMAND[i]):
            print("command: {}".format(message.content))
            await message.channel.send("データ取得中です。30秒お待ちください")
            url = URL.format(COMMAND[i])
            command = ["python3","checkbtc.py",url,"{}_send.txt".format(COMMAND[i])]
            proc = subprocess.Popen(command)
            await asyncio.sleep(30)
            amount = res_get(PATH.format(COMMAND[i]))
            await now_embed_send(amount,message,"{}/JPY リアルタイムレート".format(COMMAND[i].upper()))
            print("command: {} OK".format(message.content))

async def dmm_order(message,orders):
    if orders[0] == "ask" and not len(orders) == 4:
        #引数の数が正しくない
        print("”/ask” の引数は add 対象 目標買値 '+'or'-' です")
        await message.channel.send("”/ask” の引数は ask 対象 目標買値 '+'or'-' です")

    elif orders[0] == "bid" and not len(orders) == 4:
        #引数の数が正しくない
        print("”/bid” の引数は bid 対象 目標売値 '+'or'-' です")
        await message.channel.send("”/bid” の引数は bid 対象 目標売値 '+'or'-' です")

    elif ((orders[0]=="ask" or orders[0]=="bid") and not isfloat(orders[2])) or (not orders[3] == "+" and not orders[3] == "-"):
        print("引数の型が間違っています")
        await message.channel.send("引数の型が間違っています")

    elif orders[0] == "ask" and len(orders) == 4:
        #目標買値設定
        await goal_setting(message,orders)

    elif orders[0] == "bid" and len(orders) == 4:
        #目標売値設定
        await goal_setting(message,orders)

def isfloat(s):
    try:
        float(s)
    except ValueError:
        return False
    else:
        return True


async def now_embed_send(amount,message,titlename):
    connected = discord.Embed(
        title = titlename,
        color = 0x00ff00,
        description = "Bid(売値): "+amount[0].rstrip("\n")+" 円\n"+"Ask(買値): "+amount[1].rstrip("\n")+" 円\n"+amount[2],
    )
    await message.channel.send(embed=connected)

async def send_status(channel,title_data,text,color_data):
    connected = discord.Embed(
        title = title_data,
        color = color_data,
        description = text,
    )
    await channel.send(embed=connected)

@client.event
async def on_ready():
#    await tree.sync()
    print('ログインしました')
    channel = client.get_channel(CHANNEL_ID)
    await send_status(channel,"ログ","接続を確立しました",0x00ff00)
    asyncio.ensure_future(bot_status())

# メッセージ受信時に動作する処理
@client.event
async def on_message(message):
    if message.author.bot:
        return
    print("input:",message.content)
    if message.content == "/reply":
        await message.reply("やあ、"+message.author.name+"君。調子はどうだい？")
    elif message.content == "/kill-process":
        await send_status(message.channel,"ログ","Botを切断しました",0xff0000)
        exit()
    elif str(message.content).startswith("/add ") or str(message.content).startswith("/del "):
        x = str(message.content).split(" ")
        await command_reload(message,x[0].lstrip("/"),x[1])
    elif str(message.content).startswith("/show "):
        x = str(message.content).split(" ")
        await show(message,x[1])
    elif str(message.content).startswith("/"):
        sended_text = str(message.content).removeprefix("/").split()
        await dmm_order(message,sended_text)
    else:
        asyncio.ensure_future(dmm_selenium(message))
client.run(TOKEN)

