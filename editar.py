import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

class EditarApp:
    def __init__(self):
        pass

    def menu(self):
        submenu_opcion = st.sidebar.selectbox("Seleccione una opción", 
                                              ["Deshacer", "Nodo", "Arco" ])
        if submenu_opcion == "Deshacer":
            self.deshacer()
        elif submenu_opcion == "Nodo":
            self.nodo()
        elif submenu_opcion == "Arco":
            self.arco()
            
    def deshacer(self):
        st.warning("La opción de deshacer aún no está implementada.")
        
    def nodo(self):
        st.warning("La opción de nodo aún no está implementada.")
            
    def arco(self):
        submenu_opcion_arco = st.sidebar.selectbox("Modificar arco:", 
                                              ["Agregar", "Editar", "Eliminar" ])
        if submenu_opcion_arco == "Agregar":
            self.agregar_arco()
        elif submenu_opcion_arco == "Editar":
            self.editar_arco()
        elif submenu_opcion_arco == "Eliminar":
            self.eliminar_arco()
            
    def agregar_arco(self):
        if st.session_state.grafo["nodes"] is not None:
            agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"],
                        st.session_state.grafo["config"])
    
    def editar_arco(self):
        if st.session_state.grafo["nodes"] is not None:
            agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"],
                        st.session_state.grafo["config"])
    
    def eliminar_arco(self):
        if st.session_state.grafo["nodes"] is not None:
            agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"],
                        st.session_state.grafo["config"])