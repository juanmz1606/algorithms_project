import streamlit as st

def menu_principal():
    st.title("Menú Principal")
    opciones = ["Inicio", "Configuración", "Ayuda"]
    seleccion = st.sidebar.selectbox("Selecciona una opción", opciones)

    if seleccion == "Inicio":
        mostrar_inicio()
    elif seleccion == "Configuración":
        mostrar_configuracion()
    elif seleccion == "Ayuda":
        mostrar_ayuda()

def mostrar_inicio():
    st.header("Página de Inicio")
    st.write("Bienvenido a la aplicación. Esta es la página de inicio.")

def mostrar_configuracion():
    st.header("Página de Configuración")
    st.write("Aquí puedes ajustar la configuración de la aplicación.")

def mostrar_ayuda():
    st.header("Página de Ayuda")
    st.write("Si necesitas ayuda, consulta la documentación o ponte en contacto con nosotros.")

# Llama a la función del menú principal
menu_principal()

