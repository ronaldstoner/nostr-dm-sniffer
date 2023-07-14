#!/usr/bin/env python

"""map-relationships.py: A python script to visualize data sniffed and put into data.csv"""

__author__      = "Ron Stoner"
__copyright__   = "None"
__pubkey__      = "npub1qjtnsj6hks7pq7nh3pcyv2gpha5wp6zc8vew9qt9vd2rcpvhsjjqydz44v"
__website__     = "www.stoner.com"

#!/usr/bin/env python

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import random

# Function to assign colors for each node
def get_colors(nodes):
    num_nodes = len(nodes)
    # Specify a custom color palette (add more colors if needed)
    color_palette = ['skyblue', 'lightgreen', 'yellow', 'lightpink', 'lightcoral', 'wheat', 'mediumseagreen', 
                     'palevioletred', 'lightsalmon', 'plum', 'lightsteelblue', 'peachpuff']
    
    node_color_dict = {}

    for i, node in enumerate(nodes):
        node_color_dict[node] = color_palette[i % len(color_palette)]

    return node_color_dict

# Load the CSV data
df = pd.read_csv('data.csv', names=['sender_nip05', 'sender', 'receiver_nip05', 'receiver', 'timestamp'], skiprows=1)

# Count the sender-receiver pairs
contacts = df.groupby(['sender', 'receiver'])['sender_nip05'].count().reset_index(name='count')

# Create a dictionary of dictionaries to store sender: receiver, count 
relationship_dict = {}
for index, row in contacts.iterrows():
    receiver_count = {row['receiver']: row['count']}
    if row['sender'] in relationship_dict:
        relationship_dict[row['sender']].update(receiver_count)
    else:
        relationship_dict[row['sender']] = receiver_count

# Print out the relationships to the console
print("\nRelationships:")
for sender, receiver_counts in relationship_dict.items():
    rec_counts = ", ".join([f'{receiver} ({count})' for receiver, count in receiver_counts.items()])
    print(f'{sender} talks to {rec_counts}')

# Create directed graph
G = nx.from_pandas_edgelist(contacts, 'sender', 'receiver', 'count', create_using=nx.DiGraph())

# Generate random color for each node
color_map = get_colors(G.nodes)

# Create a layout for our nodes
#pos = nx.spring_layout(G, seed=123)
pos = nx.spring_layout(G, scale=1.5, k=0.3, seed=123)

# Plot the graph
labels = nx.get_edge_attributes(G, 'count')

plt.figure(figsize=(12,12))  # increase figure size

nx.draw_networkx_nodes(G, pos, node_size=500, node_color=list(color_map.values()), alpha=0.7)
edges = G.edges(data=True)
edge_width = [(d['count']/np.max(contacts['count']))*5 for (u, v, d) in edges]  # Width of edge is 'count' attribute (scaled)
nx.draw_networkx_edges(G, pos, width=edge_width, arrowstyle='->', arrowsize=10, alpha=0.5, edge_cmap=plt.cm.Blues)
    
# Draw the labels
nx.draw_networkx_labels(G, pos)
nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)

plt.show()
