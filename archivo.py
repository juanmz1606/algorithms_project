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
import pandas as pd
import random

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
        elif submenu_opcion == "Guardar":
            self.guardar_grafo()
        elif submenu_opcion == "Guardar Como":
            self.guardar_grafo_como()
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
            self.crear_grafo_aleatorio()
    

    def guardar_grafo(self):
        if st.session_state.grafo["nodes"] is not None:
            agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"],
                        st.session_state.grafo["config"])
            
        if st.sidebar.button("Oprima para Guardar"):
            # Inicializar la estructura del grafo en formato JSON
            grafo = {
                "graph": [],
                "generalData1": 100,
                "generalData2": "Alg",
                "generalData3": 300
            }

            # Obtener los nodos y aristas del grafo
            nodos = st.session_state.grafo["nodes"]
            aristas = st.session_state.grafo["edges"]

            # Procesar nodos
            nodos_json = []
            for nodo in nodos:
                nodo_json = {
                    "id": nodo.id,
                    "label": nodo.label,
                    "data": {},
                    "type": " ",
                    "linkedTo": [],
                    "radius": nodo.size,  # Modificar según necesites
                    "coordenates": {"x": 0, "y": 0}  # Modificar según necesites
                }
                nodos_json.append(nodo_json)

            # Procesar aristas
            for arista in aristas:
                nodo_origen = next((nodo for nodo in nodos_json if nodo["id"] == arista.source), None)
                nodo_destino = next((nodo for nodo in nodos_json if nodo["id"] == arista.to), None)
                if nodo_origen and nodo_destino:
                    nodo_origen["linkedTo"].append({
                        "nodeId": arista.to,
                        "weight": arista.label
                    })

            # Agregar los nodos procesados al grafo
            grafo["graph"].append({
                "name": "G",
                "data": nodos_json
            })

            # Guardar el grafo en formato JSON
            with open("grafo.json", "w") as file:
                json.dump(grafo, file, indent=2)

            st.sidebar.success("Grafo guardado exitosamente como grafo.json")
        

    def guardar_grafo_como(self):
        if st.session_state.grafo["nodes"] is not None:
            agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"],
                        st.session_state.grafo["config"])
            nombre_archivo = st.sidebar.text_input("Nombre del archivo sin extension: ")
            st.sidebar.write("Click en el boton 'Guardar como' al ingresar el nombre del archivo.")
            
        if st.sidebar.button("Guardar Como"):
                if nombre_archivo != "":
                    # Inicializar la estructura del grafo en formato JSON
                    grafo = {
                        "graph": [],
                        "generalData1": 100,
                        "generalData2": "Alg",
                        "generalData3": 300
                    }

                    # Obtener los nodos y aristas del grafo
                    nodos = st.session_state.grafo["nodes"]
                    aristas = st.session_state.grafo["edges"]

                    # Procesar nodos
                    nodos_json = []
                    for nodo in nodos:
                        nodo_json = {
                            "id": nodo.id,
                            "label": nodo.label,
                            "data": {},
                            "type": " ",
                            "linkedTo": [],
                            "radius": nodo.size,  # Modificar según necesites
                            "coordenates": {"x": 0, "y": 0}  # Modificar según necesites
                        }
                        nodos_json.append(nodo_json)

                    # Procesar aristas
                    for arista in aristas:
                        nodo_origen = next((nodo for nodo in nodos_json if nodo["id"] == arista.source), None)
                        nodo_destino = next((nodo for nodo in nodos_json if nodo["id"] == arista.to), None)
                        if nodo_origen and nodo_destino:
                            nodo_origen["linkedTo"].append({
                                "nodeId": arista.to,
                                "weight": arista.label
                            })

                    # Agregar los nodos procesados al grafo
                    grafo["graph"].append({
                        "name": "G",
                        "data": nodos_json
                    })
                    # Guardar el grafo en formato JSON    
                    with open(nombre_archivo + ".json", "w") as f:
                        json.dump(grafo, f, indent=2)

                    
                    st.success(f"Grafo guardado como {nombre_archivo}.json")
                elif nombre_archivo == "":
                    st.error("Por favor, ingresa un nombre de archivo.")
        
          
    def crear_grafo_personalizado(self):
        if st.session_state.grafo["nodes"] is not None:
            agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"],
                        st.session_state.grafo["config"])
        
        nodes = []
        edges = []
        
        # Configuración para el grafo personalizado
        cantidad_nodos = st.sidebar.number_input("Cantidad de nodos:", min_value=1, value=5)

        tipo_grafo = st.sidebar.radio("Selecciona el tipo de grafo:", ["No conexo","Completo", "Conexo"])

        ponderado = st.sidebar.checkbox("Ponderado")

        # Peso para todas las aristas (si el grafo es ponderado)
        peso_aristas = 0
        if ponderado:
            peso_aristas = st.sidebar.number_input("Peso de todas las aristas:", min_value=1, value=1)

        dirigido = st.sidebar.checkbox("Dirigido")

        # Color para todos los nodos
        color_nodos = st.sidebar.color_picker("Color de todos los nodos", value="#3498db")
        config = Config(width=600, height=450, directed=dirigido, physics=True, hierarchical=False)
        
        # Crear grafo personalizado al hacer clic en el botón
        if st.sidebar.button("Crear Grafo"):
            # Crear nodos
            for i in range(cantidad_nodos):
                nodes.append(Node(id=i+1, size=float(25), label=f"N{i+1}", 
                                  color=color_nodos, shape="circle"))

            if tipo_grafo == "Completo":
                # Si se selecciona grafo completo, agregar aristas entre todos los pares de nodos
                for i in range(cantidad_nodos - 1):
                    for j in range(i + 1, cantidad_nodos):
                        edges.append(Edge(source=i + 1, target=j + 1, label=peso_aristas, 
                                          color="#000000"))
                        if not dirigido:
                            edges.append(Edge(source=j + 1, target=i + 1, label=peso_aristas, 
                                              color="#000000"))

            elif tipo_grafo == "Conexo":
                # Si se selecciona grafo conexo, agregar aristas para formar un grafo conexo
                for i in range(cantidad_nodos - 1):
                    edges.append(Edge(source=i + 1, target=i + 2, label=peso_aristas, color="#000000"))
                    if not dirigido:
                        edges.append(Edge(source=i + 2, target=i + 1, label=peso_aristas, color="#000000"))

            st.session_state.grafo = {"nodes": nodes, "edges": edges, "config": config}
            
            agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"],
                            st.session_state.grafo["config"])
            st.rerun()
            
    def crear_grafo_aleatorio(self):
        if st.session_state.grafo["nodes"] is not None:
            agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"],
                        st.session_state.grafo["config"])
        nodes = []
        edges = []
        
        # Configuración para el grafo aleatorio
        cantidad_nodos = st.sidebar.number_input("Cantidad de nodos:", min_value=1, value=5)
        
        # Selección aleatoria del tipo de grafo
        tipo_grafo = random.choice(["Completo", "Conexo"])

        ponderado = st.sidebar.checkbox("Ponderado")

        # Peso para todas las aristas (si el grafo es ponderado)
        peso_aristas = 0
        if ponderado:
            peso_aristas = st.sidebar.number_input("Peso de todas las aristas:", min_value=1, value=1)

        dirigido = st.sidebar.checkbox("Dirigido")

        # Color para todos los nodos
        color_nodos = st.sidebar.color_picker("Color de todos los nodos", value="#3498db")

        config = Config(width=600, height=450, directed=dirigido, physics=True, hierarchical=False)
        
        # Crear grafo aleatorio al hacer clic en el botón
        if st.sidebar.button("Crear Grafo"):
            # Crear nodos
            for i in range(cantidad_nodos):
                nodes.append(Node(id=i+1, size=float(25), label=f"N{i+1}", color=color_nodos, shape="circle"))

            if tipo_grafo == "Completo":
                # Si se selecciona grafo completo, agregar aristas entre todos los pares de nodos
                for i in range(cantidad_nodos - 1):
                    for j in range(i + 1, cantidad_nodos):
                        edges.append(Edge(source=i + 1, target=j + 1, label=peso_aristas, color="#000000"))
                        if not dirigido:
                            edges.append(Edge(source=j + 1, target=i + 1, label=peso_aristas, color="#000000"))

            elif tipo_grafo == "Conexo":
                # Si se selecciona grafo conexo, agregar aristas para formar un grafo conexo
                for i in range(cantidad_nodos - 1):
                    edges.append(Edge(source=i + 1, target=i + 2, label=peso_aristas, color="#000000"))
                    if not dirigido:
                        edges.append(Edge(source=i + 2, target=i + 1, label=peso_aristas, color="#000000"))

            st.session_state.grafo = {"nodes": nodes, "edges": edges, "config": config}
            
            agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"], st.session_state.grafo["config"])
            st.rerun()
        
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
                                      type=node["type"], data=node["data"], color="#ffff00", shape="circle"))
                
                for node in json_data["graph"][0]["data"]:
                    idNode = node["id"]
                    for edge in node["linkedTo"]:
                        if edge["nodeId"] in (n.id for n in nodes):
                            edges.append(Edge(source=idNode, label=edge["weight"], 
                                              target=edge["nodeId"], color="#000000"))
                        else:
                            nodes.append(Node(id=edge["nodeId"], size=float(25), label=str(edge["nodeId"]), 
                                              type=" ", data={}, color="#ffff00", shape="circle")) 
                            edges.append(Edge(source=idNode, label=edge["weight"], 
                                              target=edge["nodeId"], color="#000000"))

                config = Config(width=600, height=450, directed=False, physics=True, hierarchical=False)
                
                st.session_state.grafo = {"nodes": nodes, "edges": edges, "config": config}
                agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"],
                        st.session_state.grafo["config"])
                st.rerun()
                             
        
            
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
                                      type=node["type"], data=node["data"], color="#ffff00", shape="circle"))
                
                for node in json_data["graph"][0]["data"]:
                    idNode = node["id"]
                    for edge in node["linkedTo"]:
                        if edge["nodeId"] in (n.id for n in nodes):
                            edges.append(Edge(source=idNode, label=edge["weight"], 
                                              target=edge["nodeId"], color="#000000"))
                        else:
                            nodes.append(Node(id=edge["nodeId"], size=float(25), label=str(edge["nodeId"]), 
                                              type=" ", data={}, color="#ffff00", shape="circle")) 
                            edges.append(Edge(source=idNode, label=edge["weight"], 
                                              target=edge["nodeId"], color="#000000"))

                config = Config(width=600, height=450, directed=False, physics=True, hierarchical=False)
                
                st.session_state.grafo = {"nodes": nodes, "edges": edges, "config": config}
                agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"],
                        st.session_state.grafo["config"])
                st.rerun()
                
            except json.JSONDecodeError:
                st.error("Error al decodificar el archivo JSON. Asegúrate de que el archivo tenga un formato JSON válido.")
            
    def exportar_datos(self):
        if st.session_state.grafo["nodes"] is not None:
            agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"],
                        st.session_state.grafo["config"])
            
        # Submenú para elegir entre grafo personalizado y aleatorio
        subopcion = st.sidebar.radio("Selecciona el formato de exportacion:", ["Imagen", "Excel"])

        if subopcion == "Imagen":
            self.exportar_datos_imagen()
        elif subopcion == "Excel":
            self.exportar_datos_excel()
        
    def exportar_datos_excel(self):

        if st.sidebar.button("Exportar XLSX"):
            # Obtener nodos y aristas del grafo en session_state
            nodos = st.session_state.grafo["nodes"]
            aristas = st.session_state.grafo["edges"]

            # Crear una lista de diccionarios con los atributos de cada nodo
            datos_nodos = [{"id": nodo.id, "label": nodo.label, "color": nodo.color, "shape": nodo.shape} for nodo in nodos]
            datos_aristas = [{"source": arista.source,"target":arista.to, "label": arista.label} for arista in aristas]
            
            # Crear DataFrame
            df_nodos = pd.DataFrame(datos_nodos)
            df_aristas = pd.DataFrame(datos_aristas)
            
            # Guardar los DataFrames en un archivo XLSX
            with pd.ExcelWriter('grafo.xlsx') as writer:
                df_nodos.to_excel(writer, sheet_name='nodos', index=False)
                df_aristas.to_excel(writer, sheet_name='aristas', index=False)
        
            st.sidebar.success("Archivo XLSX exportado con éxito.")


    def exportar_datos_imagen(self):

        if st.sidebar.button("Exportar Imagen"):
            #  Agrega un retraso antes de tomar la captura de pantalla
            time.sleep(1)

            # Especifica las coordenadas (x, y) del punto de inicio de la región y su ancho y altura
            x_inicio, y_inicio = 465, 155  # Coordenadas del punto de inicio de la región
            ancho, altura = 890, 575  # Ancho y altura de la región

            x_fin = x_inicio + ancho
            y_fin = y_inicio + altura

            # Toma una captura de pantalla de la región especificada
            captura = pyautogui.screenshot(region=(x_inicio, y_inicio, x_fin - x_inicio, y_fin - y_inicio))

            # Guardar la captura de pantalla como archivo de imagen
            captura.save("captura_1.png")
            captura.save("captura_2.jpg")

            st.success("Grafo guardado con éxito como imagen.")

        
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
            

     
        