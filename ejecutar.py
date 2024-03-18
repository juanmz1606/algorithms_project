import streamlit as st
import networkx as nx
from streamlit_agraph import agraph, Node, Edge, Config

class EjecutarApp:
    def __init__(self):
        pass

    def menu(self):
        submenu_opcion = st.sidebar.selectbox("Seleccione una opción", 
                                              ["Bipartito", "Más Procesos"])
        if submenu_opcion == "Bipartito":
            self.bipartito()
        elif submenu_opcion == "Nodo":
            self.nodo()
        elif submenu_opcion == "Arco":
            self.arco()
            
    def bipartitonx(self):
        if st.session_state.grafo["nodes"] is None:
            st.sidebar.warning("No se tiene un grafo para verificar si es bipartito.")
            return
        agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"],
                    st.session_state.grafo["config"])
        
        G = nx.Graph()
        edges = st.session_state.grafo["edges"]
       
        if st.sidebar.button("Verificar bipartito"):
            for edge in edges:
                print("------------------------------------")
                print(edge.source)
                print(edge.to)
                G.add_edge(edge.source, edge.to)
            
            if nx.is_bipartite(G):
                st.write("El grafo es bipartito")
            else:
                st.write("El grafo no es bipartito")
                
    def bipartito(self):
        if st.session_state.grafo["nodes"] is None:
            st.sidebar.warning("No se tiene un grafo para verificar si es bipartito.")
            return False  # No se puede determinar si es bipartito sin nodos

        nodes = {node.id: [] for node in st.session_state.grafo["nodes"]}
        for edge in st.session_state.grafo["edges"]:
            nodes[edge['source']].append(edge['to'])
            nodes[edge['to']].append(edge['source'])

        color = {}
        for node_id in nodes:
            color[node_id] = None

        for node_id in nodes:
            if color[node_id] is None:
                color[node_id] = 0
                queue = [node_id]
                while queue:
                    u = queue.pop(0)
                    for v in nodes[u]:
                        if color[v] is None:
                            color[v] = 1 - color[u]
                            queue.append(v)
                        elif color[v] == color[u]:
                            return False
        return True
