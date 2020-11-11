#!/user/bin/env python3 -tt
"""
Creating a network graph of Anking cards & videos
"""

# Imports
import sys
import os
import pdb
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from copy import copy
import csv
import argparse


# Global variables

# Class declarations

class GraphConfig:
    def __init__(self, ars):
        self.firstaid = ars.firstaid
        self.source = ars.source
        self.split = 'INSERT INTO notes VALUES'
        self.omit = self.omits()
    
    def omits(self):
        omits = ['other']
        if self.firstaid:
            return omits
        else:
            omits.append('FirstAid')
            return omits


class VideoGraph:
    def __init__(self, cards, config):
        self.config = config
        self.id_counter = 0
        self.id_to_tag = dict()
        self.tag_to_id = dict()
        self.nodes = dict()
        self.edges = dict()
        self.cards = cards
        self.build_nodes()
        self.build_edges()
        self.colors = np.array([(0.25390625, 0.75, 0.99609375, 1),
            (0.66015625, 0, 0.765625, 1),
            (0.       , 0.765625 , 0.4765625, 1),
            (0.99609375, 0.47265625, 0.33203125, 1),
            (0.79296875, 0.79296875, 0.79296875, 1)
            ])
        return

    def add_node(self, tag, card):
        node = VideoNode(tag, copy(card))
        tag_id = str(self.id_counter)
        self.id_to_tag[tag_id] = tag
        self.tag_to_id[tag] = tag_id
        self.nodes[tag_id] = node
        self.id_counter += 1
        return

    def add_edge(self, edge):
        edge = tuple(sorted(edge))
        if edge in self.edges:
            self.edges[edge].weight += 1
        else:
            self.edges[edge] = VideoEdge(edge)
        return

    def build_nodes(self):
        for card in self.cards:
            for tag in card:
                if tag not in self.tag_to_id:
                    self.add_node(tag, card)

    def build_edges(self):
        for node1 in self.nodes:
            for node2 in self.nodes[node1].card:
                if node2 not in self.tag_to_id:
                    pdb.set_trace()
                self.add_edge([node1, self.tag_to_id[node2]]) 

    def visualize(self):
        G = nx.Graph()
        
        node_size = 100
        font_size = 8

        for edge in self.edges:
            if self.nodes[edge[0]].node_class in self.config.omit or self.nodes[edge[1]].node_class in self.config.omit:
                continue
            G.add_edge(edge[0], edge[1], weight=self.edges[edge].weight)

        colors_idx = self.node_colors(G.nodes())
        # pdb.set_trace()

        nx.draw_networkx(G,
                        pos = nx.spring_layout(G),
                        node_size = node_size,
                        font_size = font_size,
                        node_color = self.colors[colors_idx]
                        )
        
        plt.show()
        
        return

    def output_tag_csv(self):
        with open('tag_list.csv', 'w') as csvfile:
            fieldnames = ['tag', 'tag_id']
            writer = csv.writer(csvfile)
            writer.writerow(fieldnames)
            for tag in self.tag_to_id:
                writer.writerow([tag, self.tag_to_id[tag]])
        print('csv written')
        return

    def node_colors(self, iter_list):
        colors = []
        categories = []
        for node_id in iter_list:
            colors.append(self.nodes[node_id].color_idx)
        return colors

class VideoEdge:
    def __init__(self, edge):
        self.nodes = set(edge)
        self.weight = 1
        return

class VideoNode:
    def __init__(self, tag, card):
        self.tag = tag
        self.card = card
        self.card.remove(tag)
        self.classify_node()
        return

    def classify_node(self):
        if '#B&B' in self.tag:
            self.node_class = 'B&B'
            self.node_color = (0.25390625, 0.75, 0.99609375, 0.00390625)
            self.color_idx = 0

        elif '#Pathoma' in self.tag:
            self.node_class = 'Pathoma'
            self.node_color = (0.66015625, 0, 0.765625, 1)
            self.color_idx = 1

        elif '#Sketchy' in self.tag:
            self.node_class = 'Sketchy'
            self.node_color = (0.       , 0.765625 , 0.4765625, 1)
            self.color_idx = 2

        elif '#FirstAid' in self.tag:
            self.node_class = 'FirstAid'
            self.node_color = (0.99609375, 0.47265625, 0.33203125, 1)
            self.color_idx = 3
        else:
            self.node_class = 'other'
            self.node_color = (0.79296875, 0.79296875, 0.79296875, 1)
            self.color_idx = 4
        return

# Function declarations

def read_dump(config):
    with open(config.source) as f:
        content = f.read()
        raw_cards = content.split(config.split)
    cards = []
    for raw_card in raw_cards:
        card = raw_card.split("\'")
        if len(card) < 4:
            if len(card) > 1:
                print(card)
            else:
                continue
        tag_list = card[3].split()
        if tag_list:
            cards.append(tag_list)
    return cards

def main(ars):
    config = GraphConfig(ars)

    cards = read_dump(config)

    g = VideoGraph(cards, config)
    
    g.visualize()
    #g.output_tag_csv()
    pdb.set_trace()

# Main body
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a network graph of the AnKing deck based on user-created tags')
    parser.add_argument('--firstaid', default=False, type=bool, help='Include FirstAid tags in the network graph')
    parser.add_argument('--source', default="/Users/ericrobinson/Desktop/dump.txt", type=str, help='Source data for creating network graph. Must be txt output of collection.ank2 sql file.')
    ars = parser.parse_args()
    main(ars)
