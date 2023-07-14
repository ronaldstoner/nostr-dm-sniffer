#!/usr/bin/env python

"""nostr-dm-sniffer.py: A python script to sniff and report on metadata related to nostr DMs (kind 4)"""

__author__      = "Ron Stoner"
__copyright__   = "None"
__pubkey__      = "npub1qjtnsj6hks7pq7nh3pcyv2gpha5wp6zc8vew9qt9vd2rcpvhsjjqydz44v"
__website__     = "www.stoner.com"

#!/usr/bin/env python

import asyncio
import aiohttp
import json
import websockets
import time
import traceback
import uuid
from datetime import datetime

# Construct the URI for relay
relay_uri = 'wss://relay.damus.io'  # replace with your actual relay URI

# Current epoch time
now = int(time.time())

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
async def process_event(event_json):
    #print(event_json)
    print("--- DM DETECTED ---")
    sender = event_json["pubkey"]
    receiver = None

    print(f"Sender: {sender} ({await get_nip05(sender)})")

    for tag in event_json["tags"]:
        if tag[0] == "p":
            receiver = tag[1]
            break

    if receiver:
        print(f"Receiver: {receiver} ({await get_nip05(receiver)})")
    else:
        print("Receiver: Not Found")

    content_str = event_json["content"]
    content_len = len(event_json["content"])
    _, iv_str = content_str.split("?iv=")
    iv_length_exact = len(iv_str)
    original_encrypted_length = content_len - len("?iv=") - iv_length_exact
    print(f"Length of Encrypted Content: {original_encrypted_length}")

    timestamp_utc = datetime.utcfromtimestamp(event_json["created_at"]).isoformat()
    print(f"Timestamp (UTC): {timestamp_utc}\n")

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

                    if response_json[0] == "EVENT":
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
