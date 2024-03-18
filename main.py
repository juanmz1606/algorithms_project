import streamlit as st
from archivo import ArchivoApp
from editar import EditarApp
from ventana import VentanaApp
from ayuda import AyudaApp
from ejecutar import EjecutarApp


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
            archivo_app = ArchivoApp()
            archivo_app.menu()
        elif seleccion == "Editar":
            editar_app = EditarApp()
            editar_app.menu()
        elif seleccion == "Ejecutar":
            ejecutar_app = EjecutarApp()
            ejecutar_app.menu()
        elif seleccion == "Herramientas":
            self.herramientas()
        elif seleccion == "Ventana":
            ventana_app = VentanaApp()
            ventana_app.menu()
        elif seleccion == "Ayuda":
            ayuda_app = AyudaApp()
            ayuda_app.menu() 

    def ejecutar(self):
        st.header("Página de ejecutar")
        submenu_opcion = st.sidebar.selectbox("Seleccione una opción", 
                                              ["Procesos"])
                
    def herramientas(self):
        st.header("Página de herramientas")
        submenu_opcion = st.sidebar.selectbox("Seleccione una opción", 
                                              ["....Coming soon"])
                
# Crear una instancia de la clase GraphApp
app = GraphApp()

# Llamar al método menu_principal
app.menu_principal()

