import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
from itertools import combinations
import random

class EjecutarApp:
    def __init__(self):
        pass

    def menu(self):
        submenu_opcion = st.sidebar.selectbox("Seleccione una opción", 
                                              ["Bipartito", "Componentes conexas", "Parcial 1.1"])
        if submenu_opcion == "Bipartito":
            self.bipartito()
        if submenu_opcion == "Componentes conexas":
            self.mostrarComponentes()
        if submenu_opcion == "Parcial 1.1":
            self.generar_combinaciones_subgrafos()
                        
    def bipartito(self):
        if st.session_state.grafo["nodes"] is None:
            st.sidebar.warning("No se tiene un grafo para verificar si es bipartito.")
            return
        agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"],
                    st.session_state.grafo["config"])
        
        if st.sidebar.button("Verificar bipartito"):
            if self.isBipartito():
                # Si no se encuentra ningún conflicto de color, el grafo es bipartito
                st.sidebar.write("El grafo es bipartito.")
            else:
                st.sidebar.write("El grafo no es bipartito.")
        
    def mostrarComponentes(self):
        if st.session_state.grafo["nodes"] is None:
            st.sidebar.warning("No se tiene un grafo en la aplicación.")
            return
        if self.isBipartito():
            componentes = self.obtenerComponentesConexas()
            if len(componentes) > 1:
                    # Guardar las componentes en el estado de la sesión
                    st.session_state.componentes_conexas = []
                    # Obtener y guardar los nodos y aristas de cada componente conexa en el estado de la sesión
                    for componente in componentes:
                        selected_nodes = [node for node in st.session_state.grafo["nodes"] if node.id in componente]
                        selected_edges = [edge for edge in st.session_state.grafo["edges"] if
                                        edge.source in [node.id for node in selected_nodes] and 
                                        edge.to in [node.id for node in selected_nodes]]
                        config = st.session_state.grafo["config"]  # Usar la misma configuración que el grafo original
                        # Guardar el grafo de la componente en el estado de la sesión
                        st.session_state.componentes_conexas.append((selected_nodes, selected_edges, config))

                        
                    # Verificar si se ha seleccionado una componente y mostrarla
                    if hasattr(st.session_state, 'componentes_conexas'):
                        component_names = [f"Componente {i+1}" for i in range(len(st.session_state.componentes_conexas))]
                        selected_component = st.sidebar.selectbox("Seleccione un componente", component_names)
                        index = component_names.index(selected_component)

                        selected_nodes, selected_edges, config = st.session_state.componentes_conexas[index]
                        if st.sidebar.button("Mostrar componente"):
                            # Mostrar el grafo de la componente seleccionada
                            agraph(selected_nodes, selected_edges, config)
            else:
                    agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"],
                    st.session_state.grafo["config"])
                    st.sidebar.write("El grafo es conexo con una sola componente.")
        else:
                st.sidebar.write("El grafo no es bipartito. No se pueden evaluar componentes.")

    def obtenerComponentesConexas(self):
        nodes = {node.id: [] for node in st.session_state.grafo["nodes"]}
        for edge in st.session_state.grafo["edges"]:
            nodes[edge.source].append(edge.to)
            nodes[edge.to].append(edge.source)

        visited = set()
        components = []
        for node_id in nodes:
            if node_id not in visited:
                component = set()
                self.dfs(node_id, nodes, visited, component)
                components.append(component)
        return components


    def dfs(self, node, nodes, visited, component):
        visited.add(node)
        component.add(node)
        for neighbor in nodes[node]:
            if neighbor not in visited:
                self.dfs(neighbor, nodes, visited, component)

    def isBipartito(self):
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
                                return False
        return True