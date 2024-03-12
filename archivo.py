import subprocess
import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
import json
import os
import psutil
import time
import keyboard
import pyautogui
import time

class ArchivoApp:
    def __init__(self):
        pass

    def menu(self):
        submenu_opcion = st.sidebar.selectbox("Seleccione una opción", 
                                              ["Nuevo Grafo", "Abrir", "Cerrar", 
                                               "Guardar", "Guardar Como", "Exportar datos",
                                               "Importar datos", "Salir"])
        if submenu_opcion == "Nuevo Grafo":
            self.nuevo_grafo()
        elif submenu_opcion == "Abrir":
            self.abrir()
        elif submenu_opcion == "Cerrar":
            self.cerrar()
        elif submenu_opcion == "Exportar datos":
            self.exportar_datos()
        elif submenu_opcion == "Importar datos":
            self.importar_datos()
        elif submenu_opcion == "Salir":
            self.salir()
        
    def nuevo_grafo(self):
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

        tipo_grafo = st.sidebar.radio("Selecciona el tipo de grafo:", ["No conexo","Completo", "Conexo"])

        ponderado = st.sidebar.checkbox("Ponderado")

        # Peso para todas las aristas (si el grafo es ponderado)
        peso_aristas = None
        if ponderado:
            peso_aristas = st.sidebar.number_input("Peso de todas las aristas:", min_value=1, value=1)

        dirigido = st.sidebar.checkbox("Dirigido")

        # Color para todos los nodos
        color_nodos = st.sidebar.color_picker("Color de todos los nodos", value="#3498db")

        config = Config(width=600, height=300, directed=dirigido, physics=True, hierarchical=False)
        
        # Crear grafo personalizado al hacer clic en el botón
        if st.sidebar.button("Crear Grafo"):
            # Crear nodos
            for i in range(cantidad_nodos):
                nodes.append(Node(id=i+1, size=25, label=f"N{i+1}", color=color_nodos, shape="circle"))

            if tipo_grafo == "Completo":
                # Si se selecciona grafo completo, agregar aristas entre todos los pares de nodos
                for i in range(cantidad_nodos - 1):
                    for j in range(i + 1, cantidad_nodos):
                        edges.append(Edge(source=i + 1, target=j + 1, label=peso_aristas))
                        if not dirigido:
                            edges.append(Edge(source=j + 1, target=i + 1, label=peso_aristas))

            elif tipo_grafo == "Conexo":
                # Si se selecciona grafo conexo, agregar aristas para formar un grafo conexo
                for i in range(cantidad_nodos - 1):
                    edges.append(Edge(source=i + 1, target=i + 2, label=peso_aristas))
                    if not dirigido:
                        edges.append(Edge(source=i + 2, target=i + 1, label=peso_aristas))

            st.session_state.grafo = {"nodes": nodes, "edges": edges, "config": config}
            agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"],
                            st.session_state.grafo["config"])
            
    
    def importar_datos(self):
        # Widget para cargar el archivo JSON
        uploaded_file = st.sidebar.file_uploader("Selecciona un archivo TXT", type=["txt"])

        if uploaded_file is not None:
        
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

                config = Config(width=750, height=500, directed=True, physics=True, hierarchical=False)
                
                st.session_state.grafo = {"nodes": nodes, "edges": edges, "config": config}
                agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"],
                        st.session_state.grafo["config"])
                             
        
            
    def abrir(self):
        # Widget para cargar el archivo JSON
        uploaded_file = st.sidebar.file_uploader("Selecciona un archivo JSON", type=["json"])

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

                config = Config(width=750, height=500, directed=True, physics=True, hierarchical=False)
                
                st.session_state.grafo = {"nodes": nodes, "edges": edges, "config": config}
                agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"],
                        st.session_state.grafo["config"])
                    
                    
            except json.JSONDecodeError:
                st.error("Error al decodificar el archivo JSON. Asegúrate de que el archivo tenga un formato JSON válido.")
    
    def exportar_datos(self):
        #config = Config(width=750, height=500, directed=True, physics=True, hierarchical=False)
        if st.session_state.grafo["nodes"] is not None:
            agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"],
                        st.session_state.grafo["config"])
            
        # Submenú para elegir entre grafo personalizado y aleatorio
        subopcion = st.sidebar.radio("Selecciona el formato de exportacion:", ["Imagen", "Excel"])

        if subopcion == "Imagen":
            self.exportar_datos_imagen()
        elif subopcion == "Excel":
            st.sidebar.warning("La opción de excel aún no está implementada.")
        

    def exportar_datos_imagen(self):

        if st.sidebar.button("Exportar Imagen"):
            #  Agrega un retraso antes de tomar la captura de pantalla
            time.sleep(1)

            # Especifica las coordenadas (x, y) del punto de inicio de la región y su ancho y altura
            x_inicio, y_inicio = 465, 130  # Coordenadas del punto de inicio de la región
            ancho, altura = 890, 600  # Ancho y altura de la región

            x_fin = x_inicio + ancho
            y_fin = y_inicio + altura

            # Toma una captura de pantalla de la región especificada
            captura = pyautogui.screenshot(region=(x_inicio, y_inicio, x_fin - x_inicio, y_fin - y_inicio))

            # Guardar la captura de pantalla como archivo de imagen
            captura.save("captura_1.png")
            captura.save("captura_2.jpg")

        
    def salir(self):
        if st.session_state.grafo["nodes"] is not None:
            agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"],
                        st.session_state.grafo["config"])

        exit_app = st.sidebar.button("Oprima para salir")
        if exit_app:
            time.sleep(1)
            keyboard.press_and_release('ctrl+w')
            pid = os.getpid()
            p = psutil.Process(pid)
            p.terminate()

    def cerrar(self):
        if st.session_state.grafo["nodes"] is not None:
            agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"],
                        st.session_state.grafo["config"])

        exit_app = st.sidebar.button("Cerrar el espacio de trabajo actual")
        if exit_app:
            time.sleep(1)
            keyboard.press_and_release('ctrl+w')
            comando = "streamlit run main.py"  
            subprocess.run(comando, shell=True)
            

     
        