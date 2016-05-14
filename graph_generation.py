#!/usr/bin/env python
# coding=utf-8

import networkx as nx
import json
import matplotlib.pyplot as plt

def course_data_load():
    course_list = json.loads(open("./course_list.json","r").read())
    return course_list

if __name__ == "__main__":
    course_list = course_data_load()
    course_id = [course["id"] for course in course_list]
    G = nx.DiGraph()
    G.add_nodes_from(range(0,len(course_list)))
    for num,course in enumerate(course_list):
        G.node[num]["name"] = course["name"]
        G.node[num]["id"] = course["id"]
    for m,course in enumerate(course_list):
        if course["prerequisite"] is not None or len(course["sim"])>0: 
            if course["prerequisite"] is not None:
                for prereq in course["prerequisite"]:
                    if prereq in course_id:
                        n = course_id.index(prereq)
                        G.add_edge(m,n,prerequisite=True)
                    else:
                        G.add_edge(m,prereq,prerequisite=True)
            if len(course["sim"]) >0:
                for sim in course["sim"]:
                    G.add_edge(m,int(sim[0]),similarity=sim[1])
        else:
            continue

    nx.draw_networkx(G,node_list=G.nodes_with_selfloops())
    plt.show()
    plt.savefig("course_graph.png")

