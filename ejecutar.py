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
            return
        agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"],
                    st.session_state.grafo["config"])
        
        if st.sidebar.button("Verificar bipartito"):

            nodes = {node.id: [] for node in st.session_state.grafo["nodes"]}
            for edge in st.session_state.grafo["edges"]:
                nodes[edge.source].append(edge.to)
                nodes[edge.to].append(edge.source)

        # Algoritmo de BFS para verificar si el grafo es bipartito
        
            color = {}  # Un diccionario para mantener los colores de los nodos
            for node_id in nodes:
                color[node_id] = None  

            for node_id in nodes:  
                if color[node_id] is None:  # Si el nodo no ha sido coloreado
                    color[node_id] = 0  # Asignar un color al nodo (0 o 1)
                    queue = [node_id]  # Inicializar una cola con el nodo actual
                    while queue:  # Mientras la cola no esté vacía
                        u = queue.pop(0)  # Extraer el primer nodo de la cola
                        for v in nodes[u]:  # Iterar sobre todos los nodos adyacentes al nodo u
                            if color[v] is None:  # Si el nodo adyacente no ha sido coloreado
                                color[v] = 1 - color[u]  # Asignar un color diferente al nodo adyacente
                                queue.append(v)  # Agregar el nodo adyacente a la cola
                            elif color[v] == color[u]:  # Si el nodo adyacente tiene el mismo color que u
                                # Si se encuentra un conflicto de color, el grafo no es bipartito
                                st.write("El grafo no es bipartito.")
                                return False
                                
            # Si no se encuentra ningún conflicto de color, el grafo es bipartito
            st.write("El grafo es bipartito.")
            return True
        
        
