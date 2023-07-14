#!/usr/bin/env python

"""nostr-dm-sniffer.py: A python script to sniff and report on metadata related to nostr DMs (kind 4)"""

__author__      = "Ron Stoner"
__copyright__   = "None"
__pubkey__      = "npub1qjtnsj6hks7pq7nh3pcyv2gpha5wp6zc8vew9qt9vd2rcpvhsjjqydz44v"
__website__     = "www.stoner.com"

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
        "kinds": [4], # subscribe to NIP-4 (DM) events
        "since": now,  # events must be newer than this timestamp
        "until": now+3600,  # subscription expiration time (1 hour)
    }
]

# Process function to handle incoming NIP-4 events
async def process_event(event_json):
    
    print("--- DM DETECTED ---")
    sender = event_json["pubkey"]
    receiver = None

    print(f"Sender: {sender}")

    # Extract the receiver pubkey from the tags
    for tag in event_json["tags"]:
        if tag[0] == "p":
            receiver = tag[1]
            break

    if receiver:
        print(f"Receiver: {receiver}")
    else:
        print("Receiver: Not Found")

    # Determine the length of the content - assumes content to be a string
    content_length = len(event_json["content"])
    print(f"Length of Encrypted Content: {content_length}")

    timestamp_utc = datetime.utcfromtimestamp(event_json["created_at"]).isoformat()
    print(f"Timestamp (UTC): {timestamp_utc}\n")

    # Reset all the things
    sender = "", 
    receiver = "", 
    content_length = 0, 
    timestamp_utc = ""

# WebSocket client to connect to the relay, subscribe to NIP-0, NIP-4 events, and process incoming events
async def websocket_client(uri):
    async with websockets.connect(uri) as websocket:
        print("Connected.\n")

        # Subscribe to NIP-0, NIP-4 events
        await websocket.send(json.dumps(subscription_request))

        # Handle incoming events indefinitely
        while True:
            response = await websocket.recv()
            response_json = json.loads(response)

            # Determine if response is an EVENT message related to our subscription
            if response_json[0] == "EVENT":
                await process_event(response_json[2])
            time.sleep(1)

print("Connecting to relay...")
asyncio.get_event_loop().run_until_complete(websocket_client(relay_uri))
