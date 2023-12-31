#!/usr/bin/env python

"""nostr-dm-sniffer.py: A python script to sniff and report on metadata related to nostr DMs (kind 4)"""

__author__      = "Ron Stoner"
__copyright__   = "None"
__pubkey__      = "npub1qjtnsj6hks7pq7nh3pcyv2gpha5wp6zc8vew9qt9vd2rcpvhsjjqydz44v"
__website__     = "www.stoner.com"

import asyncio
import aiohttp
import csv
import json
import os
import time
import traceback
import uuid
import websockets
from datetime import datetime

# Construct the URI for relay
relay_uri = 'wss://relay.damus.io'  # replace with your actual relay URI

# Current epoch time
now = int(time.time())

# Check and write CSV header
if not os.path.isfile('data.csv'):
    with open('data.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['sender', 'sender_nip05', 'receiver', 'receiver_nip05', 'timestamp'])  # write header

# NIP-4 event subscription request
subscription_id = uuid.uuid1().hex
subscription_request = [
    "REQ",
    subscription_id,
    {
        "kinds": [4],  # subscribe to NIP-4 (DM) events
        "since": now,  # events must be newer than this timestamp
        "until": now + 3600,  # subscription expiration time (1 hour)
    }
]

async def get_nip05(pubkey):
    pubkey_metadata_reply = ""
    pubkey_metadata = ""
    json_acceptable_string = ""
    d = ""
    nip_05_identifier = ""
    name = ""
    display_name = ""
    search_filter_nip05 = {
        "kinds": [0],
        "authors": [pubkey]
    }

    request = json.dumps(["REQ", "nip05-" + pubkey[:8], search_filter_nip05])

    await websocket.send(request)
    pubkey_metadata_reply = await websocket.recv()

    if "EOSE" not in pubkey_metadata_reply and pubkey_metadata_reply:
        #print(pubkey_metadata_reply)
        pubkey_metadata_reply = pubkey_metadata_reply.strip()  # Remove whitespace characters
        pubkey_metadata = json.loads(pubkey_metadata_reply)

        json_acceptable_string = pubkey_metadata[2].get('content')

        if json_acceptable_string:  # checking if json_acceptable_string is not None and if it isn't an empty string
            try:
                d = json.loads(json_acceptable_string)
                name = d.get('name')
                display_name = d.get('display_name')
                nip_05_identifier = name if name else display_name
            
                if not nip_05_identifier:
                    nip_05_identifier = 'No NIP05 id found'
            
            except json.JSONDecodeError:
                nip_05_identifier = 'NIP05 Decode Error'

        else:
            nip_05_identifier = "No valid NIP05 found"

        await websocket.send(json.dumps(["CLOSE", "nip05-" + pubkey[:8]]))
        pubkey_metadata_close = await websocket.recv()

    else:
        nip_05_identifier = "No NIP05 found"

    return nip_05_identifier

def write_to_csv(writer, data):
    writer.writerow(data)

async def process_event(event_json):
    #print(event_json)
    sender = ""
    content_str = ""
    content_len = 0
    content_str_without_iv = ""
    iv_str = ""
    iv_length_exact = 0
    original_encrypted_length = 0
    sender_nip05 = ""
    receiver_nip05 = ""
    print("--- DM DETECTED ---")
    sender = event_json["pubkey"]
    receiver = None

    sender_nip05 = await get_nip05(sender)
    print(f"Sender: {sender} ({sender_nip05})")

    for tag in event_json["tags"]:
        if tag[0] == "p":
            receiver = tag[1]
            break

    if receiver:
        receiver_nip05 = await get_nip05(receiver)
        print(f"Receiver: {receiver} ({receiver_nip05})")
    else:
        print("Receiver: Not Found")

    content_str = event_json["content"]
    content_len = len(event_json["content"])
    content_str_without_iv, iv_str = content_str.split("?iv=")
    
    if "?iv=" in content_str:
        content_str_without_iv, iv_str = content_str.split("?iv=")
    else:
        iv_str = "No IV found"
    iv_length_exact = len(iv_str)
    
    original_encrypted_length = content_len - len("?iv=") - iv_length_exact
    print(f"Length of Encrypted Content: {original_encrypted_length}")
    print(f"Encrypted Content: {content_str_without_iv}")
    print(f"Encrypted IV: {iv_str}")

    timestamp_utc = datetime.utcfromtimestamp(event_json["created_at"]).isoformat()
    print(f"Timestamp (UTC): {timestamp_utc}\n")

    # Create a data dictionary and append it to csv
    data = [sender, sender_nip05, receiver, receiver_nip05, timestamp_utc]
    with open('data.csv', 'a', newline='') as file:  # changed to 'a' (append) mode
        writer = csv.writer(file)
        write_to_csv(writer, data)

async def websocket_client(uri):
    global websocket  # to make websocket accessible in other functions

    while True:
        try:
            async with websockets.connect(uri) as websocket:
                print("Connected.\n")
                
                await websocket.send(json.dumps(subscription_request))

                while True:
                    response = await websocket.recv()
                    response_json = json.loads(response)

                    #print(response_json)
                    if response_json[0] == "EVENT":
                        if 'kind' in response_json[2] and response_json[2]['kind'] == 4:
                            await process_event(response_json[2])
                    #time.sleep(1)

        except Exception as e:
            print("An error occurred. Details:\n", traceback.format_exc())
            print("Attempting to reconnect in 5 seconds...")
            await asyncio.sleep(5)
        else:
            print("Disconnecting...")
            break

print("Connecting to relay...")
asyncio.get_event_loop().run_until_complete(websocket_client(relay_uri))
