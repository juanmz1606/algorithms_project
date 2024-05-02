import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
import copy

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
        if st.sidebar.button("Deshacer último cambio"):
            if st.session_state.get("previous_grafo", {"nodes": None, "edges": None, "config": None})["nodes"] is None:
                st.sidebar.warning("No se ha realizado ningún cambio al grafo actual")
                return
            st.session_state.grafo = st.session_state.previous_grafo
            agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"], st.session_state.grafo["config"])
            
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
        if st.session_state.grafo["nodes"] is None:
            st.header("No existe un grafo para agregar nodos. Debe crear un grafo primero.")
            return
        nodos_actuales = []
        cantidad_nodos = st.sidebar.number_input("Cantidad de nodos:", min_value=1, value=1)
        color_nodos = st.sidebar.color_picker("Color de los nodos", value="#3498db")
        max_id = 0
        if st.sidebar.button("Agregar Nodo"):
            # Guardar el estado actual del grafo en previous_grafo
            st.session_state.previous_grafo = copy.deepcopy(st.session_state.grafo)

            if st.session_state.grafo["nodes"] is not None:
                nodos_actuales = st.session_state.grafo["nodes"]
                max_id = max([node.id for node in nodos_actuales])
            for i in range(cantidad_nodos):
                new_id = max_id + i + 1
                nodos_actuales.append(Node(id=new_id, size=float(25), label=f"N{new_id}", type=" ", data={}, color=color_nodos, shape="circle"))
            st.session_state.grafo["nodes"] = nodos_actuales
            agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"], st.session_state.grafo["config"])
            st.rerun()
            
    def editar_nodo(self):
        if st.session_state.grafo["nodes"] is None:
            st.sidebar.warning("No existe actualmente ningún nodo en el grafo")
            return
        
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
            nuevo_tamaño = st.sidebar.number_input("Nuevo tamaño:", min_value=0.1, value=nodo_seleccionado.size)
            
            if st.sidebar.button("Guardar cambios"):
                # Guardar el estado actual del grafo en previous_grafo
                st.session_state.previous_grafo = copy.deepcopy(st.session_state.grafo)
                
                # Actualizar el nodo seleccionado con los nuevos valores
                nodo_seleccionado.color = nuevo_color
                nodo_seleccionado.label = nueva_etiqueta
                nodo_seleccionado.size = nuevo_tamaño
                
                st.session_state.grafo["nodes"] = nodos_actuales
                agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"],
                        st.session_state.grafo["config"])
                st.rerun()
            
            
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
            # Guardar el estado actual del grafo en previous_grafo
            st.session_state.previous_grafo = copy.deepcopy(st.session_state.grafo)
            # Filtrar los nodos actuales para eliminar el nodo seleccionado
            nodos_actuales = [node for node in nodos_actuales if node.id != nodo_a_eliminar]
            
            # Actualizar el grafo en la session_state
            st.session_state.grafo["nodes"] = nodos_actuales

            agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"],
                        st.session_state.grafo["config"])
            st.rerun()

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
        color_arista = st.sidebar.color_picker("Color de la nueva arista", value="#000000")
        punteada = st.sidebar.checkbox("Arista punteada", value=False)
    

        # Aquí deberías tener una lista de identificadores de nodos disponibles para seleccionar
        source_id = st.sidebar.selectbox("Seleccionar nodo de origen:", [node.id for node in nodos_actuales], key=100)
        target_id = st.sidebar.selectbox("Seleccionar nodo de destino:", [node.id for node in nodos_actuales if node.id != source_id], key=111)
        
        if st.sidebar.button("Agregar Arista"):
            # Guardar el estado actual del grafo en previous_grafo
            st.session_state.previous_grafo = copy.deepcopy(st.session_state.grafo)
            
            for edge in edges:
                if (edge.source == source_id and edge.to == target_id):
                    st.sidebar.warning("Ya existe una arista entre los nuevos nodos de origen y destino.")
                    return
                if not st.session_state.directed:
                    if (edge.to == source_id and edge.source == target_id):
                        st.sidebar.warning("Ya existe una arista entre los nuevos nodos de " +
                                           "origen y destino.")
                        return
            edges.append(Edge(source=int(source_id), target=int(target_id), 
                              label=peso_arista, color=color_arista, dashes=punteada))

            if not st.session_state.directed:  # Si el grafo no es dirigido, agregamos la arista en la dirección opuesta
                edges.append(Edge(source=int(target_id), target=int(source_id), 
                              label=peso_arista, color=color_arista, dashes=punteada))
            
            # Actualizar el grafo en el estado de la sesión
            st.session_state.grafo["edges"] = edges
            agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"], 
                   st.session_state.grafo["config"])
            st.rerun()
    
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
        edge_seleccionado_nodirected = None

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
        nuevo_peso = st.sidebar.number_input("Nuevo peso:", min_value=0, value=int(edge_seleccionado.label))
        color_arista = st.sidebar.color_picker("Color de la nueva arista", value="#000000")
        punteada = st.sidebar.checkbox("Arista punteada", value=False)

        if st.sidebar.button("Guardar cambios"):
            # Guardar el estado actual del grafo en previous_grafo
            st.session_state.previous_grafo = copy.deepcopy(st.session_state.grafo)

            # Verificar si ya existe una arista entre los nuevos nodos de origen y destino
            for edge in edges:
                if (edge.source == nuevo_source_id and edge.to == nuevo_target_id):
                    st.sidebar.warning("Ya existe una arista entre los nuevos nodos de origen y destino.")
                    return
                if not st.session_state.directed:
                    if (edge.to == nuevo_source_id and edge.source == nuevo_target_id):
                        st.sidebar.warning("Ya existe una arista entre los nuevos nodos de origen y destino.")
                        return

            index_edge_seleccionado_nodirected = None
            if not st.session_state.directed:
                for edge in edges:
                    if edge.source == edge_seleccionado.to and edge.to == edge_seleccionado.source:
                        edge_seleccionado_nodirected = edge
                        index_edge_seleccionado_nodirected = edges.index(edge_seleccionado_nodirected)
                        break

            st.sidebar.write("Cambio exitoso")
            edges.pop(index_edge_seleccionado)
            edges.append(Edge(source=nuevo_source_id, target=nuevo_target_id, label=nuevo_peso, color=color_arista, dashes=punteada))

            # Agregamos la nueva arista si no es un grafo dirigido
            if not st.session_state.directed and index_edge_seleccionado_nodirected is not None:
                edges.pop(index_edge_seleccionado_nodirected)
                edges.append(Edge(source=nuevo_target_id, target=nuevo_source_id, label=nuevo_peso, color=color_arista, dashes=punteada))

            # Actualizar el grafo en session_state
            st.session_state.grafo["edges"] = edges
            agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"], st.session_state.grafo["config"])
            st.rerun()
    
    def eliminar_arco(self):
        edges = st.session_state.grafo["edges"]
        
        if edges is None or len(edges) == 0:
            st.sidebar.warning("No hay arcos en el grafo para eliminar.")
            return
        
        # Obtener los IDs de los nodos del grafo
        nodos_actuales = st.session_state.grafo["nodes"]
        ids_nodos = [node.id for node in nodos_actuales]
        
        # Crear una lista de selección con los IDs de los nodos
        source_id = st.sidebar.selectbox("Seleccionar nodo de origen:", options=ids_nodos)
        target_id = st.sidebar.selectbox("Seleccionar nodo de destino:", options=ids_nodos)
        
        edge_seleccionado = None
        for edge in edges:
            if edge.source == source_id and edge.to == target_id:
                edge_seleccionado = edge
                break
        
        if edge_seleccionado is None:
            st.sidebar.warning("No se encontró el arco seleccionado en el grafo.")
            return
        
        if st.sidebar.button("Eliminar arco"):
            # Guardar el estado actual del grafo en previous_grafo
            st.session_state.previous_grafo = copy.deepcopy(st.session_state.grafo)
            edges.remove(edge_seleccionado)
            st.session_state.grafo["edges"] = edges
            agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"], st.session_state.grafo["config"])
            st.rerun()
