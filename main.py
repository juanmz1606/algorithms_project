import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
import json

class GraphApp:
    def __init__(self):
        self.initialize_session_state()

    def initialize_session_state(self):
        if 'grafo' not in st.session_state:
            st.session_state.grafo = {"nodes": None, "edges": None, "config": None}

    def menu_principal(self):
        # Restaurar o inicializar el estado de la sesión
        self.initialize_session_state()

        # Definir la disposición de la página
        st.sidebar.title("Menú Principal")
        opciones = ["Archivo", "Editar", "Ejecutar", "Herramientas", "Ventana", "Ayuda"]
        seleccion = st.sidebar.selectbox("Selecciona una opción", opciones)

        if seleccion == "Archivo":
            self.archivo()
        elif seleccion == "Editar":
            self.editar()
        elif seleccion == "Ejecutar":
            self.ejecutar()
        elif seleccion == "Herramientas":
            self.herramientas()
        elif seleccion == "Ventana":
            self.ventana()
        elif seleccion == "Ayuda":
            self.ayuda()

    def archivo(self):
        submenu_opcion = st.sidebar.selectbox("Seleccione una opción", 
                                              ["Nuevo Grafo", "Abrir", "Cerrar", 
                                               "Guardar", "Guardar Como", "Exportar datos",
                                               "Importar datos", "Salir"])
        if submenu_opcion == "Abrir":
            self.archivo_abrir()
        elif submenu_opcion == "Nuevo Grafo":
            self.archivo_nuevo_grafo()

    def editar(self):
        st.header("Página de editar")
        submenu_opcion = st.sidebar.selectbox("Seleccione una opción", 
                                              ["Deshacer", "Nodo", "Arco" ])

    def ejecutar(self):
        st.header("Página de ejecutar")
        submenu_opcion = st.sidebar.selectbox("Seleccione una opción", 
                                              ["Procesos"])
                
    def herramientas(self):
        st.header("Página de herramientas")
        submenu_opcion = st.sidebar.selectbox("Seleccione una opción", 
                                              ["....Coming soon"])
                
    def ventana(self):
        st.header("Página de ventana")
        submenu_opcion = st.sidebar.selectbox("Seleccione una opción", 
                                              ["Grafica", "Tabla"])
                
    def ayuda(self):
        st.header("Página de ayuda")
        submenu_opcion = st.sidebar.selectbox("Seleccione una opción", 
                                              ["Ayuda", "Acerca de grafos"])
                
                
    def archivo_nuevo_grafo(self):
        if st.session_state.grafo["nodes"] is None:
            st.header("No hay un grafo en la aplicación")
        else:
            st.header("Grafo")
            agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"],
                   st.session_state.grafo["config"])

    def archivo_abrir(self):
        # Widget para cargar el archivo JSON
        uploaded_file = st.file_uploader("Selecciona un archivo JSON", type=["json"])

        if uploaded_file is not None:
            try:
                # Leer el archivo cargado
                json_data = json.load(uploaded_file)
                nodes = []
                edges = []
                
                for node in json_data["graph"][0]["data"]:
                    idNode = node["id"]
                    nodes.append(Node(id=idNode, size=node["radius"], label=node["label"], 
                                      type=node["type"], data=node["data"], color="yellow", shape="circle"))
                
                for node in json_data["graph"][0]["data"]:
                    idNode = node["id"]
                    for edge in node["linkedTo"]:
                        if edge["nodeId"] in (n.id for n in nodes):
                            edges.append(Edge(source=idNode, label=edge["weight"], 
                                              target=edge["nodeId"]))
                        else:
                            nodes.append(Node(id=edge["nodeId"], size=1, label=str(edge["nodeId"]), 
                                              type=" ", data={}, color="yellow", shape="circle")) 
                            edges.append(Edge(source=idNode, label=edge["weight"], 
                                              target=edge["nodeId"]))

                config = Config(width=750, height=950, directed=True, physics=True, hierarchical=False)
                
                st.session_state.grafo = {"nodes": nodes, "edges": edges, "config": config}
                st.header("Grafo")
                agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"],
                        st.session_state.grafo["config"])
                
            except json.JSONDecodeError:
                st.error("Error al decodificar el archivo JSON. Asegúrate de que el archivo tenga un formato JSON válido.")

# Crear una instancia de la clase GraphApp
app = GraphApp()

# Llamar al método menu_principal
app.menu_principal()
