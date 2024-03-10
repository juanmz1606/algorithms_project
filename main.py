import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
import json
import os
import psutil
import time
import keyboard
import uuid


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
        elif submenu_opcion == "Salir":
            self.salir()
            
          
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
            st.title("No se ha creado ningún grafo 😞")
        else:
            st.header("Grafo")
            agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"],
                        st.session_state.grafo["config"])

        # Submenú para elegir entre grafo personalizado y aleatorio
        subopcion = st.sidebar.radio("Selecciona el tipo de grafo:", ["Personalizado", "Aleatorio"])

        if subopcion == "Personalizado":
            self.crear_grafo_personalizado()
        elif subopcion == "Aleatorio":
            # Implementación para el grafo aleatorio
            st.sidebar.warning("La opción de grafo aleatorio aún no está implementada.")
            
            
    def crear_grafo_personalizado(self):
        nodes = []
        edges = []
        
        # Configuración para el grafo personalizado
        cantidad_nodos = st.sidebar.number_input("Cantidad de nodos:", min_value=1, value=5)

        grafo_completo = st.sidebar.checkbox("Grafo completo")

        grafo_conexo = st.sidebar.checkbox("Grafo conexo")

        ponderado = st.sidebar.checkbox("Ponderado")

        # Peso para todas las aristas (si el grafo es ponderado)
        peso_aristas = None
        if ponderado:
            peso_aristas = st.sidebar.number_input("Peso de todas las aristas:", min_value=1, value=1)

        dirigido = st.sidebar.checkbox("Dirigido")

        # Color para todos los nodos
        color_nodos = st.sidebar.color_picker("Color de todos los nodos", value="#3498db")

        config = Config(width=750, height=400, directed=dirigido, physics=True, hierarchical=False)
        
        # Crear grafo personalizado al hacer clic en el botón
        if st.sidebar.button("Crear Grafo"):
            # Crear nodos
            for i in range(cantidad_nodos):
                nodes.append(Node(id=f"{i+1}", size=25, label=f"N{i+1}", color=color_nodos, shape="circle"))

            # Crear aristas
            if grafo_completo:
                # Si se selecciona grafo completo, agregar aristas entre todos los pares de nodos
                for i in range(cantidad_nodos - 1):
                    for j in range(i + 1, cantidad_nodos):
                        edges.append(Edge(source=f"Nodo_{i+1}", target=f"Nodo_{j+1}", label=peso_aristas))
                        if not dirigido:
                            edges.append(Edge(source=f"Nodo_{j+1}", target=f"Nodo_{i+1}", label=peso_aristas))
            elif grafo_conexo:
                # Si se selecciona grafo conexo, agregar aristas para formar un grafo conexo
                for i in range(cantidad_nodos - 1):
                    edges.append(Edge(source=f"Nodo_{i+1}", target=f"Nodo_{i+2}", label=peso_aristas))
                    if not dirigido:
                        edges.append(Edge(source=f"Nodo_{i+2}", target=f"Nodo_{i+1}", label=peso_aristas))
            
            # Generar una clave única para el widget agraph
            unique_key = f"agraph_{uuid.uuid4().hex}"
            st.session_state.grafo = {"nodes": nodes, "edges": edges, "config": config}
            st.header("Grafo")
            grafo_personalizado = agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"],
                            st.session_state.grafo["config"])

    def salir(self):
        exit_app = st.sidebar.button("Click para salir de la aplicación")
        if exit_app:
            time.sleep(3)
            keyboard.press_and_release('ctrl+w')
            pid = os.getpid()
            p = psutil.Process(pid)
            p.terminate()

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

