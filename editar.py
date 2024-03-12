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
        if st.session_state.grafo["nodes"] is not None:
            agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"],
                        st.session_state.grafo["config"])
            
        # Submenú para elegir e
        subopcion = st.sidebar.radio("Seleccionar Opcion", ["Agregar", "Editar", "Eliminar"])

        if subopcion == "Agregar":
            self.agregar_nodo()


    def agregar_nodo(self):
        nodos_actuales = []
        
        cantidad_nodos = st.sidebar.number_input("Cantidad de nodos:", min_value=1, value=1)
        color_nodos = st.sidebar.color_picker("Color de los nodos", value="#3498db")

        if st.sidebar.button("Agregar Nodo"):
            nodos_actuales = st.session_state.grafo["nodes"]

            # Encontrar el máximo identificador actual
            max_id = max([node.id for node in nodos_actuales])
      
            for i in range(cantidad_nodos):
                new_id = max_id + i + 1  # Asignar un identificador único
                nodos_actuales.append(Node(id=new_id, size=25, label=f"N{new_id}", color=color_nodos, shape="circle"))
            
            st.session_state.grafo["nodes"] = nodos_actuales
            agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"],
                        st.session_state.grafo["config"])
              
             
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