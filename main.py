import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
import json
import LectorJSON as Ljson

def menu_principal():
    st.title("Menú Principal")
    opciones = ["Archivo", "Editar", "Ejecutar", "Herramientas", "Ventana","Ayuda"]
    seleccion = st.sidebar.selectbox("Selecciona una opción", opciones)

    if seleccion == "Archivo":
        archivo()
    elif seleccion == "Editar":
        editar()
    elif seleccion == "Ejecutar":
        ejecutar()
    elif seleccion == "Herramientas":
        herramientas()
    elif seleccion == "Ventana":
        ventana()
    elif seleccion == "Ayuda":
        ayuda()

def archivo():
    st.header("Página de Archivo")
    st.write("Bienvenido a la aplicación. Esta es la página de archivo.")
    submenu_opcion = st.sidebar.selectbox("Seleccione una opción", 
                                          ["Nuevo Grafo", "Abrir", "Cerrar", 
                                           "Guardar", "Guardar Como", "Exportar datos",
                                           "Importar datos", "Salir"])
    if submenu_opcion == "Abrir":
        archivo_Abrir()
    elif submenu_opcion == "Nuevo Grafo":
        archivo_NuevoGrafo()
    

def editar():
    st.header("Página de editar")
    st.write("Bienvenido a la aplicación. Esta es la página de editar.")
    submenu_opcion = st.sidebar.selectbox("Seleccione una opción", 
                                          ["Deshacer", "Nodo", "Arco" ])

def ejecutar():
    st.header("Página de ejecutar")
    st.write("Bienvenido a la aplicación. Esta es la página de ejecutar.")
    submenu_opcion = st.sidebar.selectbox("Seleccione una opción", 
                                          ["Procesos"])
    
def herramientas():
    st.header("Página de herramientas")
    st.write("Bienvenido a la aplicación. Esta es la página de herramientas.")
    submenu_opcion = st.sidebar.selectbox("Seleccione una opción", 
                                          ["....Coming soon"])
    
def ventana():
    st.header("Página de ventana")
    st.write("Bienvenido a la aplicación. Esta es la página de ventana.")
    submenu_opcion = st.sidebar.selectbox("Seleccione una opción", 
                                          ["Grafica", "Tabla"])
    
def ayuda():
    st.header("Página de ayuda")
    st.write("Bienvenido a la aplicación. Esta es la página de ayuda.")
    submenu_opcion = st.sidebar.selectbox("Seleccione una opción", 
                                          ["Ayuda", "Acerca de grafos"])
    
    
def archivo_NuevoGrafo():
    nodes = [
        Node(id="Spiderman", label="Peter Parker", size=25, shape="circularImage", image="http://marvel-force-chart.surge.sh/marvel_force_chart_img/top_spiderman.png"),
        Node(id="Captain_Marvel", size=25, shape="circularImage", image="http://marvel-force-chart.surge.sh/marvel_force_chart_img/top_captainmarvel.png")
    ]

    edges = [
        Edge(source="Captain_Marvel", label="friend_of", target="Spiderman")
    ]

    config = Config(width=750, height=950, directed=True, physics=True, hierarchical=False)

    # Mostrar el grafo utilizando agraph
    return_value = agraph(nodes=nodes, edges=edges, config=config)
    st.write(return_value)

def archivo_Abrir():

    # Widget for uploading the JSON file
    uploaded_file = st.file_uploader("Select a JSON file", type=["json"])

    if uploaded_file is not None:
        try:
            # Read the uploaded file
            json_data = json.load(uploaded_file)
            nodes = []
            edges = []
              
            for node in json_data["graph"][0]["data"]:
                     idNode = node["id"]
                     nodes.append(Node(id = idNode, size=node["radius"], label=node["label"], 
                                       type=node["type"], data=node["data"], color="yellow", shape="circle"))
              
            for node in json_data["graph"][0]["data"]:
                     idNode = node["id"]
                     for edge in node["linkedTo"]:
                            if edge["nodeId"] in (node.id for node in nodes):
                                edges.append(Edge(source=idNode, label=edge["weight"], 
                                            target=edge["nodeId"]))
                            else:
                                  nodes.append(Node(id = edge["nodeId"], size=1, label=str(edge["nodeId"]), 
                                       type=" ", data={}, color="yellow", shape="circle")) 
                                  edges.append(Edge(source=idNode, label=edge["weight"], 
                                            target=edge["nodeId"]))
            

            config = Config(width=750, height=950, directed=True, physics=True, hierarchical=False)

              # Mostrar el grafo utilizando agraph
            return_value = agraph(nodes=nodes, edges=edges, config=config)
            st.write(return_value)
            
        except json.JSONDecodeError:
            st.error("Error al decodificar el archivo JSON. Asegúrate de que el archivo tenga un formato JSON válido.")


# Llama a la función del menú principal
menu_principal()