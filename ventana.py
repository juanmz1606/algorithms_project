import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
import pandas as pd
import numpy as np
import networkx as nx
import plotly.graph_objects as go

class VentanaApp:
    def __init__(self):
        pass

    def menu(self):
        submenu_opcion = st.sidebar.selectbox("Seleccione una opción", 
                                              ["Grafica", "Tabla" ])
        if submenu_opcion == "Grafica":
            self.grafica()
        elif submenu_opcion == "Tabla":
            self.tabla()


    def grafica(self):
        if st.session_state.grafo["nodes"] is not None:
            agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"],
                        st.session_state.grafo["config"])
            
        if st.sidebar.button("Mostrar gráfica"):
            G = nx.Graph()

            # Agregar nodos al grafo
            for node in st.session_state.grafo["nodes"]:
                G.add_node(node.id)

            # Agregar aristas al grafo
            for edge in st.session_state.grafo["edges"]:
                G.add_edge(edge.source, edge.to)

            # Obtener posiciones de los nodos
            pos = nx.spring_layout(G)

            # Crear figura de Plotly
            fig = go.Figure()

            # Agregar nodos al gráfico
            for node in G.nodes():
                x, y = pos[node]
                fig.add_trace(go.Scatter(x=[x], y=[y], mode='markers+text', text=[node], marker=dict(size=20, color='skyblue'), textposition="bottom center"))

            # Agregar aristas al gráfico
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], mode='lines', line=dict(color='black'), hoverinfo='none'))

            # Configurar diseño del gráfico
            fig.update_layout(title="Visualización del Gráfico", showlegend=False, hovermode='closest', margin=dict(b=20, l=5, r=5, t=40))

            # Mostrar el gráfico
            st.plotly_chart(fig)

    
    def tabla(self):
        if st.session_state.grafo["nodes"] is not None:
            agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"],
                        st.session_state.grafo["config"])
            
        if st.sidebar.button("Mostrar tabla"):
            
            num_nodes = len(st.session_state.grafo["nodes"])
            matriz_adyacencia = np.zeros((num_nodes, num_nodes))

            # Llenar la matriz de adyacencia con 1s en las posiciones correspondientes
            for edge in st.session_state.grafo["edges"]:
                source_index = edge.source - 1
                target_index = edge.to - 1
                matriz_adyacencia[source_index][target_index] = 1
                #matriz_adyacencia[target_index][source_index] = 1

            # Mostrar la matriz de adyacencia en un DataFrame de Pandas
            st.subheader("Matriz de Representacion:")
            st.write(pd.DataFrame(matriz_adyacencia, index=range(1, len(st.session_state.grafo["nodes"]) + 1), columns=range(1, len(st.session_state.grafo["nodes"]) + 1)))
      