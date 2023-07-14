# nostr-dm-sniffer
A python script to sniff and report on metadata related to nostr DMs (kind 4).

## Install
1. git clone this repo
2. update the `relay_uri` in the code to the relay you wish to monitor
3. `pip install -r requirements.txt`

## Usage - sniffer 
1. `python nostr-dm-sniffer.py`

## Usage - visualizor 
1. `python map-relationships.py` - requires data.csv to be generated from sniffer

## Screenshots
<img src="https://github.com/ronaldstoner/nostr-dm-sniffer/blob/main/img/nostr-dm-sniffer.png?raw=true" alt="A text console showing DM metadata on the nostr protocol" width="600">

<img src="https://github.com/ronaldstoner/nostr-dm-sniffer/blob/main/img/map-relationships.png?raw=true" alt="A matplot graph showing relationships between sender and receiver" width="600">

## Note
This software has no guarantees and may cause quantum entanglement, solar flares, and in some extreme cases, arthritis. Side effects can vary depending on factors such as age, use of other drugs, vitamins, or dietary supplements, and underlying diseases or conditions. Please consult with your health professional and IT staff before running unknown code.
