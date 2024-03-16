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
            
        subopcion = st.sidebar.radio("Seleccionar Opcion", ["Agregar", "Editar", "Eliminar"])

        if subopcion == "Agregar":
            self.agregar_nodo()
        elif subopcion == "Editar":
            self.editar_nodo()
        elif subopcion == "Eliminar":
            self.eliminar_nodo()


    def agregar_nodo(self):
        nodos_actuales = []
        cantidad_nodos = st.sidebar.number_input("Cantidad de nodos:", min_value=1, value=1)
        color_nodos = st.sidebar.color_picker("Color de los nodos", value="#3498db")
        max_id = 0

        if st.sidebar.button("Agregar Nodo"):
            if st.session_state.grafo["nodes"] is not None:
                nodos_actuales = st.session_state.grafo["nodes"]
                # Encontrar el máximo identificador actual
                max_id = max([node.id for node in nodos_actuales])
      
            for i in range(cantidad_nodos):
                new_id = max_id + i + 1  # Asignar un identificador único
                nodos_actuales.append(Node(id=new_id, size=1, label=f"N{new_id}", 
                                           type=" ", data={},color=color_nodos, shape="circle"))
                
            config = Config(width=600, height=300, directed=False, physics=True, hierarchical=False)
                
            st.session_state.grafo["nodes"] = nodos_actuales
            
            agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"],
                        st.session_state.grafo["config"])
            
    def editar_nodo(self):
        if st.session_state.grafo["nodes"] is None:
            st.sidebar.warning("No existe actualmente ningún nodo en el grafo")
            return
        nodos_actuales = []
        nodos_actuales = st.session_state.grafo["nodes"]
            
        # Obtener los IDs de los nodos del grafo
        ids_nodos = [node.id for node in nodos_actuales]
            
        # Crear una lista de selección con los IDs de los nodos
        nodo_a_editar = st.sidebar.selectbox("Seleccionar ID del nodo:", options=ids_nodos)

        # Obtener el nodo seleccionado por su ID
        nodo_seleccionado = next((node for node in nodos_actuales if node.id == nodo_a_editar), None)
        
        if nodo_seleccionado:
            # Campos de entrada para editar el nodo seleccionado
            nuevo_color = st.sidebar.color_picker("Nuevo color:", value=nodo_seleccionado.color)
            nueva_etiqueta = st.sidebar.text_input("Nueva etiqueta:", value=nodo_seleccionado.label)
            nuevo_tamaño = st.sidebar.number_input("Nuevo tamaño:", min_value=1, value=nodo_seleccionado.size)
            
            if st.sidebar.button("Guardar cambios"):
                # Actualizar el nodo seleccionado con los nuevos valores
                nodo_seleccionado.color = nuevo_color
                nodo_seleccionado.label = nueva_etiqueta
                nodo_seleccionado.size = nuevo_tamaño
                
                # Actualizar el grafo en session_state
                st.session_state.grafo["nodes"] = nodos_actuales
                agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"],
                        st.session_state.grafo["config"])
            
            
    def eliminar_nodo(self):
        if st.session_state.grafo["nodes"] is None:
            st.sidebar.warning("No existe actualmente ningún nodo en el grafo")
            return
        nodos_actuales = []
        nodos_actuales = st.session_state.grafo["nodes"]
            
        # Obtener los IDs de los nodos del grafo
        ids_nodos = [node.id for node in nodos_actuales]
            
        # Crear una lista de selección con los IDs de los nodos
        nodo_a_eliminar= st.sidebar.selectbox("Seleccionar ID del nodo:", options=ids_nodos)

        if st.sidebar.button("Eliminar Nodo"):
            # Filtrar los nodos actuales para eliminar el nodo seleccionado
            nodos_actuales = [node for node in nodos_actuales if node.id != nodo_a_eliminar]
            
            # Actualizar el grafo en la session_state
            st.session_state.grafo["nodes"] = nodos_actuales

            agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"],
                        st.session_state.grafo["config"])

    def arco(self):
        if st.session_state.grafo["nodes"] is not None:
            agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"],
                        st.session_state.grafo["config"])
            
        submenu_opcion_arco = st.sidebar.radio("Modificar arco:", 
                                              ["Agregar", "Editar", "Eliminar" ])
        if submenu_opcion_arco == "Agregar":
            self.agregar_arco()
        elif submenu_opcion_arco == "Editar":
            self.editar_arco()
        elif submenu_opcion_arco == "Eliminar":
            self.eliminar_arco()
            
    def agregar_arco(self):
        if st.session_state.grafo["nodes"] is None or len(st.session_state.grafo["nodes"]) <= 1:
            st.sidebar.warning("Debe existir mas de un nodo para agregar un arco")
            return
        
        nodos_actuales = st.session_state.grafo["nodes"]
        edges = st.session_state.grafo["edges"]
        peso_arista = st.sidebar.number_input("Peso de la arista:", min_value=1, value=1)

        # Aquí deberías tener una lista de identificadores de nodos disponibles para seleccionar
        source_id = st.sidebar.selectbox("Seleccionar nodo de origen:", [node.id for node in nodos_actuales], key=100)
        target_id = st.sidebar.selectbox("Seleccionar nodo de destino:", [node.id for node in nodos_actuales if node.id != source_id], key=111)
        
        if st.sidebar.button("Agregar Arista"):
            edges.append(Edge(source=int(source_id), target=int(target_id), label=str(peso_arista)))
            # Actualizar el grafo en el estado de la sesión
            st.session_state.grafo["edges"] = edges
            agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"], st.session_state.grafo["config"])
    
    def editar_arco(self):
        edges = st.session_state.grafo["edges"]
        # Verificar si edges es None
        if edges is None:
            st.sidebar.warning("No hay arcos en el grafo para editar.")
            return

        nodos_actuales = st.session_state.grafo["nodes"]

        # Obtener los IDs de los nodos del grafo
        ids_nodos = [node.id for node in nodos_actuales]

        # Crear una lista de selección con los IDs de los nodos
        source_id = st.sidebar.selectbox("Seleccionar nodo de origen:", options=ids_nodos)
        target_id = st.sidebar.selectbox("Seleccionar nodo de destino:", options=ids_nodos)

        edge_seleccionado = None
        for edge in edges:
            if edge.source == source_id and edge.to == target_id:
                edge_seleccionado = edge
                index_edge_seleccionado = edges.index(edge_seleccionado)
                break

        if edge_seleccionado is None:
            st.sidebar.warning("No se encontró el arco seleccionado en el grafo.")
            return

        # Campos de entrada para editar el arco seleccionado
        nuevo_source_id = st.sidebar.selectbox("Nuevo nodo de origen:", options=ids_nodos)
        nuevo_target_id = st.sidebar.selectbox("Nuevo nodo de destino:", options=ids_nodos)
        nuevo_peso = st.sidebar.number_input("Nuevo peso:", min_value=1, value=int(edge_seleccionado.label))

        # Verificar si ya existe una arista entre los nuevos nodos de origen y destino
        for edge in edges:
            if (edge.source == nuevo_source_id and edge.to == nuevo_target_id):
                st.sidebar.warning("Ya existe una arista entre los nuevos nodos de origen y destino.")
                return

        if st.sidebar.button("Guardar cambios"):
            edges.pop(index_edge_seleccionado)
            
            edges.append(Edge(source=nuevo_source_id, 
                              target=nuevo_target_id, label=str(nuevo_peso)))  # Agregamos la nueva arista

            # Actualizar el grafo en session_state
            st.session_state.grafo["edges"] = edges
            agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"], st.session_state.grafo["config"])
            st.rerun()
    
    def eliminar_arco(self):
        pass