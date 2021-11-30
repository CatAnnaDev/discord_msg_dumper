#!/usr/bin/python3
import websocket  # pip3 install websocket-client
import requests  # pip3 install requests
import mimetypes
import json
import threading
import time
import os

###### CONFIG ######
# authorization token in request header message (xhr type)
token = ""
guildID = "292822970290929664"
heartbeat_interval_num = 1000  # = 41.25s
status = "invisible"
activities_name = "chalut \\o/"
Custom_RPC = True
Show_Header = False
img_download = True


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
            "op": 1,
            "d": "null"
        }
        send_json_request(ws, heartbeatJSON)


def download(url, name):
    response = requests.get(url)
    file = open(name, "wb")
    file.write(response.content)
    file.close()


ws = websocket.WebSocket()
ws.connect('wss://gateway.discord.gg/?v=9&encording=json')
if Show_Header:
    print(f"Headers ? {json.dumps(ws.headers, indent=4)}")
    print("------------------------------------------------------------")
event = recieve_json_response(ws)

heartbeat_interval = event['d']['heartbeat_interval'] / heartbeat_interval_num
print(f"Connected ? = {ws.connected}")
print(heartbeat_interval)
threading._start_new_thread(heartbeat, (heartbeat_interval, ws))

payload = {
    'op': 2,
    "d": {
        "token": token,
        "properties": {
            "$os": "windows",
            "$browser": "chrome",
            "$device": 'pc'
        }
    }
}
send_json_request(ws, payload)

payload_RPC = {
    "op": 3,
    "d": {
        "since": 91879201,
        "activities": [{
            "name": activities_name,
            "type": 0
        }],
        "status": status,
        "afk": False
    }
}

if Custom_RPC:
    send_json_request(ws, payload_RPC)
    print(f"Custom RPC set: {status} //// {activities_name}")

payload_GMember = {
    "op": 8,
    "d": {
        "guild_id": guildID,
        "query": "",
        "limit": 0
    }
}

#send_json_request(ws, payload_GMember)

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
                        f"Timestamp: {ts}\nOpcode: {opcodes}: {opcodes_type}\nType: {Type}\n{url_msg}\n{usename}: {msg_content}\n")
                else:
                    attachments_link = f"Url: {event['d']['attachments'][0]['url']} \t\nType: {event['d']['attachments'][0]['content_type']}\n"
                    file_object.write(
                        f"Timestamp: {ts}\nOpcode: {opcodes}: {opcodes_type}\nType: {Type}\n{url_msg}\n{usename}: {msg_content}\t\nMedia: {attachments_link}")

                print("------------------------------------------------------------")
                if not "url" in obj:
                    print(
                        f"Timestamp: {ts}\nOpcode: {opcodes}: {opcodes_type}\nType: {Type}\n{url_msg}\n{usename}: {msg_content}\n")
                else:
                    attachments_link = f"Url: {event['d']['attachments'][0]['url']} \t\nType: {event['d']['attachments'][0]['content_type']}\n"
                    print(
                        f"Timestamp: {ts}\nOpcode: {opcodes}: {opcodes_type}\nType: {Type}\n{url_msg}\n{usename}: {msg_content}\t\nMedia: {attachments_link}")
                    if img_download:
                        print(
                            f"Downloading Media {event['d']['attachments'][0]['filename']}")
                        download(event['d']['attachments'][0]['url'],
                                 event['d']['attachments'][0]['filename'])

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
