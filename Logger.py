#!/usr/bin/python3
import websocket  # pip3 install websocket-client
import requests  # pip3 install requests
import json
import threading
import random
import time
import math
import os
os.system('cls' if os.name == 'nt' else 'clear')

###### CONFIG ######
# authorization token in request header message (xhr type) OR see on footer page


class config:
    token = ""
    heartbeat_interval_num = 1000  # = 41.25s
    status = "invisible"
    activities_name = "chalut \\o/"
    Activity_type = 3
    Activity_link = "https://github.com/PsykoDev"
    Custom_RPC = True
    Show_Header = False
    img_download = False


# Activity_type
# 0	Game	Playing {name}
# 1	Streaming	Streaming {details}
# 2	Listening	Listening to {name}
# 3	Watching	Watching {name}
# 4	Custom	{emoji} {name}
# 5	Competing	Competing in {name}


class bcolors:
    HEADER = '\033[95m'
    OKPURPLE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class DiscordWebSocket:
    DISPATCH = 0
    HEARTBEAT = 1
    IDENTIFY = 2
    PRESENCE = 3
    VOICE_STATE = 4
    VOICE_PING = 5
    RESUME = 6
    RECONNECT = 7
    REQUEST_MEMBERS = 8
    INVALIDATE_SESSION = 9
    HELLO = 10
    HEARTBEAT_ACK = 11
    GUILD_SYNC = 12


def send_json_request(ws, request):
    ws.send(json.dumps(request))


def recieve_json_response(ws):
    response = ws.recv()
    if response:
        return json.loads(response)


def heartbeat(interval, ws):
    while True:
        time.sleep(interval)
        heartbeatJSON = {
            "op": DiscordWebSocket.HEARTBEAT,
            "d": "null"
        }
        send_json_request(ws, heartbeatJSON)


def download(url, name):
    response = requests.get(url)
    file = open(name, "wb")
    file.write(response.content)
    file.close()


def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


def get_guild_name(id):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.7.12) Gecko/20050915 Firefox/1.0.7',
        'Authorization': config.token
    }

    response = requests.get(
        f"https://discord.com/api/guilds/{id}",
        headers=headers,
        params={"with_counts": True}
    ).json()
    return response['name']


ws = websocket.WebSocket()
ws.connect('wss://gateway.discord.gg/?v=9&encording=json')
print(
    f"Config: \n\tCustom_RPC = {config.Custom_RPC}\n\tShow_Header = {config.Show_Header}\n\timg_download = {config.img_download}\n\tMSG Color = {bcolors.OKPURPLE}Purple{bcolors.ENDC}\n\tMedia Color = {bcolors.OKCYAN}Cyan{bcolors.ENDC}\n\tMedia Download = {bcolors.OKGREEN}Green{bcolors.ENDC}")
if config.Show_Header:
    print(f"Headers ? {json.dumps(ws.headers, indent=4)}")
    print("------------------------------------------------------------")
event = recieve_json_response(ws)

heartbeat_interval = event['d']['heartbeat_interval'] / \
    config.heartbeat_interval_num
print(f"Connected ? = {ws.connected}")
print(f"heartbeat_interval = {heartbeat_interval}")
threading._start_new_thread(heartbeat, (heartbeat_interval, ws))

payload = {
    'op': DiscordWebSocket.IDENTIFY,
    "d": {
        "token": config.token,
        "properties": {
            "$os": "windows",
            "$browser": "chrome",
            "$device": 'pc'
        }
    }
}
send_json_request(ws, payload)

payload_RPC = {
    "op": DiscordWebSocket.PRESENCE,
    "d": {
        "since": 91879201,
        "activities": [{
            "name": config.activities_name,
            "type": config.Activity_type,
            "url": config.Activity_link
        }],
        "status": config.status,
        "afk": False
    }
}

if config.Custom_RPC:
    send_json_request(ws, payload_RPC)
    print(
        f"Custom RPC set: {config.status} //// {config.activities_name}")


type_msg = ["DEFAULT", "RECIPIENT_ADD", "RECIPIENT_REMOVE", "CALL", "CHANNEL_NAME_CHANGE", "CHANNEL_ICON_CHANGE", "CHANNEL_PINNED_MESSAGE", "GUILD_MEMBER_JOIN", "USER_PREMIUM_GUILD_SUBSCRIPTION", "USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_1", "USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_2", "USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_3",
            "CHANNEL_FOLLOW_ADD", "", "GUILD_DISCOVERY_DISQUALIFIED", "GUILD_DISCOVERY_REQUALIFIED", "GUILD_DISCOVERY_GRACE_PERIOD_INITIAL_WARNING", "GUILD_DISCOVERY_GRACE_PERIOD_FINAL_WARNING", "THREAD_CREATED", "REPLY", "CHAT_INPUT_COMMAND", "THREAD_STARTER_MESSAGE", "GUILD_INVITE_REMINDER", "CONTEXT_MENU_COMMAND"]

while True:
    event = recieve_json_response(ws)
    try:
        if not "bot" in event['d']['author']:
            file_object = open("Log.txt", "a")
            if os.path.exists("Log.txt"):
                opcodes = event['t']
                opcodes_type = event['op']
                Type = f"{type_msg[event['d']['type']]}: {event['d']['type']}"
                usename = f"{event['d']['author']['username']}#{event['d']['author']['discriminator']}"
                msg_content = event['d']['content']
                ts = event['d']['timestamp']
                obj = json.dumps(event['d']['attachments'],
                                 sort_keys=True, indent=4)
                url_msg = f"https://discord.com/channels/{event['d']['guild_id']}/{event['d']['channel_id']}/{event['d']['nonce']}"

                file_object.write(
                    "------------------------------------------------------------\n")
                if not "url" in obj:
                    file_object.write(
                        f"Timestamp: {ts}\nOpcode: {opcodes}: {opcodes_type}\nType: {Type}\nMsg URL: {url_msg}\nServer name: {get_guild_name(event['d']['guild_id'])} \n{usename}: {msg_content}\n")
                else:
                    attachments_link = f"\n\tUrl: {event['d']['attachments'][0]['url']} \n\tType: {event['d']['attachments'][0]['content_type']}\n"
                    file_object.write(
                        f"Timestamp: {ts}\nOpcode: {opcodes}: {opcodes_type}\nType: {Type}\nMsg URL: {url_msg}\nServer name: {get_guild_name(event['d']['guild_id'])} \n{usename}: {msg_content}\n\n Media: {attachments_link} ")

                print("------------------------------------------------------------")
                if not "url" in obj:
                    print(
                        f"Timestamp: {ts}\nOpcode: {opcodes}: {opcodes_type}\nType: {Type}\nMsg URL: {url_msg}\nServer name: {get_guild_name(event['d']['guild_id'])} \n{bcolors.OKPURPLE}{usename}: {msg_content}{bcolors.ENDC}\n")
                else:
                    attachments_link = f"\n\tUrl: {event['d']['attachments'][0]['url']} \n\tType: {event['d']['attachments'][0]['content_type']}\n"
                    print(
                        f"Timestamp: {ts}\nOpcode: {opcodes}: {opcodes_type}\nType: {Type}\nMsg URL: {url_msg}\nServer name: {get_guild_name(event['d']['guild_id'])} \n{bcolors.OKPURPLE}{usename}: {msg_content}{bcolors.ENDC}\n\n{bcolors.OKCYAN} Media: {attachments_link} {bcolors.ENDC}")
                    if config.img_download:
                        print(
                            bcolors.OKGREEN + f"Number of files: {len(event['d']['attachments'])}" + bcolors.ENDC)
                        if len(event['d']['attachments']) == 1:
                            mini = event['d']['attachments'][0]
                            var_name = random.randint(0, 500000)
                            custom_name = str(var_name) + mini['filename']
                            print(
                                bcolors.OKGREEN + f"Downloading Media {custom_name} // Size: {convert_size(int(mini['size']))}" + bcolors.ENDC)
                            threading._start_new_thread(
                                download, (mini['url'], custom_name))
                        else:
                            for index in range(len(event['d']['attachments'])):
                                mini = event['d']['attachments'][index]
                                var_name = random.randint(0, 500000)
                                custom_name = str(var_name) + mini['filename']
                                print(
                                    bcolors.OKGREEN + f"Downloading Media {custom_name} // Size: {convert_size(int(mini['size']))}" + bcolors.ENDC)
                                threading._start_new_thread(
                                    download, (mini['url'], custom_name))
                #print(json.dumps(event, indent=4))
            else:
                print("No Log.txt file found")
        op_code = event['op']
    except:
        pass

# 't' = opcode event name https://discord.com/developers/docs/topics/opcodes-and-status-codes#gateway-gateway-opcodes
# 's' = integer sequence number, used for resuming sessions and heartbeats
# 'op' = opcode number
# 'd' = event data mixed json
# s and t are null when op is not 0 (Gateway Dispatch Opcode)
# https://discord.com/developers/docs/topics/gateway

# TYPE :

# 0 DEFAULT
# 1 RECIPIENT_ADD
# 2 RECIPIENT_REMOVE
# 3 CALL
# 4 CHANNEL_NAME_CHANGE
# 5 CHANNEL_ICON_CHANGE
# 6 CHANNEL_PINNED_MESSAGE
# 7 GUILD_MEMBER_JOIN
# 8 USER_PREMIUM_GUILD_SUBSCRIPTION
# 9 USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_1
# 10 USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_2
# 11 USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_3
# 12 CHANNEL_FOLLOW_ADD
# 14 GUILD_DISCOVERY_DISQUALIFIED
# 15 GUILD_DISCOVERY_REQUALIFIED
# 16 GUILD_DISCOVERY_GRACE_PERIOD_INITIAL_WARNING
# 17 GUILD_DISCOVERY_GRACE_PERIOD_FINAL_WARNING
# 18 THREAD_CREATED
# 19 REPLY
# 20 CHAT_INPUT_COMMAND
# 21 THREAD_STARTER_MESSAGE
# 22 GUILD_INVITE_REMINDER
# 23 CONTEXT_MENU_COMMAND

# Get discord token from console
# just copy paste this line below in discord console then copy paste your token
# var req=webpackJsonp.push([[],{extra_id:(e,r,t)=>e.exports=t},[["extra_id"]]]);for(let e in req.c)if(req.c.hasOwnProperty(e)){let r=req.c[e].exports;if(r&&r.__esModule&&r.default)for(let e in r.default)"getToken"===e&&console.log(r.default.getToken())}
