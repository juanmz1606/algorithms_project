import streamlit as st
import webbrowser
from streamlit_agraph import agraph

class AyudaApp:
    def __init__(self):
        pass
    
    def menu(self):
        submenu_opcion = st.sidebar.selectbox("Seleccione una opción", 
                                              ["Ayuda", "Acerca de Grafos" ])
        if submenu_opcion == "Ayuda":
            self.ayuda()
        elif submenu_opcion == "Acerca de Grafos":
            self.ayuda()
            
    def ayuda(self):
        if st.session_state.grafo["nodes"] is not None:
            agraph(st.session_state.grafo["nodes"], st.session_state.grafo["edges"],
                        st.session_state.grafo["config"])
        if st.sidebar.button("Manual de Usuario"):
            url = "https://docs.google.com/document/d/1LDUW-OBcIUwL3S5trRErjC7xy_caHRxHcVJozf5wcDg/edit"
            webbrowser.open(url)
        return
        
        
    def acerca_grafos(self):
        pass