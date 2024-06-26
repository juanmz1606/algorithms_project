import streamlit as st
from archivo import ArchivoApp
from editar import EditarApp
from ventana import VentanaApp
from ayuda import AyudaApp
from ejecutar import EjecutarApp
from analisis import AnalisisApp


class GraphApp:
    def __init__(self):
        self.initialize_session_state()

    def initialize_session_state(self):
        if 'grafo' not in st.session_state:
            st.session_state.grafo = {"nodes": None, "edges": None, "config": None}
            
        if 'directed' not in st.session_state:
            st.session_state.directed = False
            
        if 'previous_grafo' not in st.session_state:
            st.session_state.previous_grafo = {"nodes": None, "edges": None, "config": None}
            
        if 'tablas_prob' not in st.session_state:
            st.session_state.tablas_prob = {}
            
        if 'grafo_temporal' not in st.session_state:
            st.session_state.grafo_temporal = {}
            
        if 'estrategia1' not in st.session_state:
            st.session_state.estrategia1 = {"estadoInicial": None, "valPresente": None, "valFuturo":None,
                                            "valPerdida":None,"tiempo": None}
        if 'estrategia2' not in st.session_state:
            st.session_state.estrategia2 = {"estadoInicial": None, "valPresente": None, "valFuturo":None,
                                            "valPerdida":None,"tiempo": None}
        if 'estrategiaFinal' not in st.session_state:
            st.session_state.estrategiaFinal = {"estadoInicial": None, "valPresente": None, "valFuturo":None,
                                            "valPerdida":None,"tiempo": None}

    def menu_principal(self):
        # Restaurar o inicializar el estado de la sesión
        self.initialize_session_state()

        # Definir la disposición de la página
        st.sidebar.title("Menú Principal")
        opciones = ["Archivo", "Editar", "Ejecutar", "Herramientas", "Ventana", "Ayuda", "Analisis"]
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
        elif seleccion == "Analisis":
            analisis_app = AnalisisApp()
            analisis_app.menu()
                
    def herramientas(self):
        st.header("Página de herramientas")
        submenu_opcion = st.sidebar.selectbox("Seleccione una opción", 
                                              ["....Coming soon"])
                
# Crear una instancia de la clase GraphApp
app = GraphApp()

# Llamar al método menu_principal
app.menu_principal()

