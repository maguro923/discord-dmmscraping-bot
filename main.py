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

TOKEN = TokenData.TOKEN
client = discord.Client(intents=discord.Intents.all())
CHANNEL_ID = ChannelData.CHANNEL_ID
PATH = "send/{}_send.txt"
URL = "https://bitcoin.dmm.com/trade_chart_rate_list/{}-jpy"
COMMAND = Command.COMMAND
command_list = CommandList.command_list
#tree = discord.app_commands.CommandTree(client)

async def bot_status():
    channel=client.get_channel(CHANNEL_ID)
    while True:
        for i in range(6):
            for j in range(len(COMMAND)):
                url = URL.format(COMMAND[j])
                command = ["python3","checkbtc.py",url,"{}_send.txt".format(COMMAND[j])]
                proc = subprocess.Popen(command)
                await asyncio.sleep(20)
            await asyncio.sleep(600-len(COMMAND)*30)
        print("status: OK")
        await send_status(channel,"status","OK",0x00ff00)

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
    os.fdatasync(data.fileno())
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
        await message.channel.send("{} は無効な引数です。正しい引数を入力して下さい".format(name))
        return
    if not command_check(action,name) and action == "add":
        await message.channel.send("{} は既に追加されています".format(name))
        return
    if not command_check(action,name) and action == "del":
        await message.channel.send("{} は既に削除されています".format(name))
        return
    if action == "add":
        new_command = COMMAND
        new_command.append(name)
        await command_write(new_command)
        await message.channel.send("{} を追加しました".format(name))
        print("再起動します...")
        await send_status(message.channel,"ログ","Botを切断しました\n再起動しています...",0xff0000)
        os.execv(sys.executable, ['python'] + sys.argv)
    else:
        new_command = COMMAND
        new_command.remove(name)
        await command_write(new_command)
        await message.channel.send("{} を削除しました".format(name))
        print("再起動します...")
        await send_status(message.channel,"ログ","Botを切断しました\n再起動しています...",0xff0000)
        os.execv(sys.executable, ['python'] + sys.argv)

#async def command_show(message):

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
    elif message.content == "/show-command":
#        await command_show(message)
        x = "\n".join(COMMAND)
        y = ",".join(command_list)
        await message.channel.send("現在有効化されたコマンドは\n"+x+"\nコマンド一覧は\n"+y)
    else:
        asyncio.ensure_future(dmm_selenium(message))

client.run(TOKEN)

