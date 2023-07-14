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

    if "EOSE" not in pubkey_metadata_reply and pubkey_metadata_reply is not None:
        pubkey_metadata_reply = pubkey_metadata_reply.replace('\n', '')  # Remove newline characters from the metadata string
        pubkey_metadata = json.loads(pubkey_metadata_reply)
        json_acceptable_string = pubkey_metadata[2]['content']
        d = json.loads(json_acceptable_string)
        name = d['name']

        nip_05_identifier = name

        await websocket.send(json.dumps(["CLOSE", "nip05-" + pubkey[:8]]))
        pubkey_metadata_close = await websocket.recv()

    else:
        nip_05_identifier = "No NIP05 found"

    return nip_05_identifier

async def process_event(event_json):
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

    content_length = len(event_json["content"])
    print(f"Length of Encrypted Content: {content_length}")

    timestamp_utc = datetime.utcfromtimestamp(event_json["created_at"]).isoformat()
    print(f"Timestamp (UTC): {timestamp_utc}\n")

async def websocket_client(uri):
    global websocket  # to make websocket accessible in other functions

    async with websockets.connect(uri) as websocket:
        print("Connected.\n")

        await websocket.send(json.dumps(subscription_request))

        while True:
            response = await websocket.recv()
            response_json = json.loads(response)

            if response_json[0] == "EVENT":
                await process_event(response_json[2])
            time.sleep(1)


print("Connecting to relay...")
asyncio.get_event_loop().run_until_complete(websocket_client(relay_uri))
