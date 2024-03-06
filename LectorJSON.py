from streamlit_agraph import agraph, Node, Edge, Config
import streamlit as st
import json

class LectorJSON:
       
       def __init__(self, json_data):
              nodes = []
              edges = []
              
              for node in json_data["graph"][0]["data"]:
                     print("----------------------------------------------------------------")
                     print("----------------------------------------------------------------")
                     idNode = node["id"]
                     nodes.append(Node(id = idNode, size=node["radius"], label=node["label"], 
                                       type=node["type"], data=node["data"], color="blue", shape="circularImage"))
              
              for node in json_data["graph"][0]["data"]:
                     idNode = node["id"]
                     for edge in node["linkedTo"]:
                            if edge["nodeId"] in nodes:
                                   edges.append(Edge(source=idNode, label=edge["weight"], 
                                              target=edge["nodeId"]))
                            else:
                                  nodes.append(Node(id = edge["nodeId"], size=1, label=edge["nodeId"], 
                                       type=" ", data={}, color="blue", shape="circularImage")) 

              config = Config(width=750, height=950, directed=True, physics=True, hierarchical=False)

              # Mostrar el grafo utilizando agraph
              return_value = agraph(nodes=nodes, edges=edges, config=config)
              return return_value