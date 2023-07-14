import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

# Load the CSV data
df = pd.read_csv('data.csv', names=['sender_nip05', 'sender', 'receiver_nip05', 'receiver', 'timestamp'], skiprows=1)

# Count the sender-receiver pairs
contacts = df.groupby(['sender', 'receiver'])['sender_nip05'].count().reset_index(name='count')

# Create directed graph
G = nx.from_pandas_edgelist(contacts, 'sender', 'receiver', 'count', create_using=nx.DiGraph())

# Create a layout for our nodes 
pos = nx.spring_layout(G, seed=123)

# Plot the graph with labels
plt.figure(figsize=(12,12))  # increase figure size

labels = nx.get_edge_attributes(G, 'count')

nx.draw_networkx(G, pos, with_labels=True, node_color='skyblue', node_size=500)
nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_size=7)  # increase font size for readability
plt.show()
