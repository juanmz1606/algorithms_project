import streamlit as st

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
        ejecutar()
    elif seleccion == "Ventana":
        ejecutar()
    elif seleccion == "Ayuda":
        ejecutar()

def archivo():
    st.header("Página de Archivo")
    st.write("Bienvenido a la aplicación. Esta es la página de archivo.")
    submenu_opcion = st.sidebar.selectbox("Seleccione una opción", 
                                          ["Nuevo Grafo", "Abrir", "Cerrar", 
                                           "Guardar", "Guardar Como", "Exportar datos",
                                           "Importar datos", "Salir"])
    

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

# Llama a la función del menú principal
menu_principal()